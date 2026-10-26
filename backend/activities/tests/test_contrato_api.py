from datetime import datetime
from uuid import UUID, uuid4

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Activity, Enrollment, Participant


User = get_user_model()
LOCMEM_EMAIL = "django.core.mail.backends.locmem.EmailBackend"


class FailingEmailBackend(BaseEmailBackend):
    """Simula un servidor SMTP caído."""

    def send_messages(self, email_messages):
        raise ConnectionRefusedError("SMTP no disponible")


def bearer_headers(user):
    return {
        "HTTP_AUTHORIZATION": f"Bearer {RefreshToken.for_user(user).access_token}",
    }


class ApiContractTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ada", password="secret")
        self.other_user = User.objects.create_user(username="grace", password="secret")
        self.participant = Participant.objects.create(name="Ada", user=self.user)
        self.other_participant = Participant.objects.create(
            name="Grace",
            user=self.other_user,
        )
        self.activity = Activity.objects.create(
            id=UUID("1b470ddf-3e84-4b77-9aae-091d21e52bd6"),
            title="Diseño de una API",
            starts_at=timezone.make_aware(datetime(2026, 3, 23, 18, 0)),
            capacity=2,
        )
        self.headers = bearer_headers(self.user)
        self.activity_url = f"/api/v1/activities/{self.activity.id}"
        self.enrollments_url = "/api/v1/me/enrollments"
        self.enrollment_url = (
            f"/api/v1/me/enrollments/{self.activity.id}"
        )

    def test_lists_activities_with_availability(self):
        Enrollment.objects.create(
            participant=self.other_participant,
            activity=self.activity,
        )

        response = self.client.get("/api/v1/activities")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "id": str(self.activity.id),
                    "title": "Diseño de una API",
                    "starts_at": "2026-03-23T18:00:00-03:00",
                    "capacity": 2,
                    "available_slots": 1,
                }
            ],
        )

    def test_gets_an_activity_and_reports_a_missing_one(self):
        response = self.client.get(self.activity_url)
        missing_response = self.client.get(
            f"/api/v1/activities/{uuid4()}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], str(self.activity.id))
        self.assertEqual(response.json()["available_slots"], 2)
        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(
            missing_response.json()["code"],
            "activity_not_found",
        )

    def test_personal_routes_reject_missing_or_invalid_credentials(self):
        invalid_headers = {"HTTP_AUTHORIZATION": "Bearer not-a-token"}
        responses = [
            self.client.get(self.enrollments_url),
            self.client.put(self.enrollment_url),
            self.client.delete(self.enrollment_url, **invalid_headers),
        ]

        for response in responses:
            with self.subTest(method=response.request["REQUEST_METHOD"]):
                self.assertEqual(response.status_code, 401)

    def test_obtains_a_token_pair(self):
        response = self.client.post(
            "/api/v1/token/",
            {"username": "ada", "password": "secret"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("access", payload)
        self.assertIn("refresh", payload)

        authorized = self.client.get(
            self.enrollments_url,
            HTTP_AUTHORIZATION=f"Bearer {payload['access']}",
        )
        self.assertEqual(authorized.status_code, 200)

    def test_lists_only_the_current_participant_enrollments(self):
        own = Enrollment.objects.create(
            participant=self.participant,
            activity=self.activity,
        )
        other_activity = Activity.objects.create(
            title="Otra actividad",
            starts_at=timezone.now(),
            capacity=1,
        )
        Enrollment.objects.create(
            participant=self.other_participant,
            activity=other_activity,
        )

        response = self.client.get(
            self.enrollments_url,
            **self.headers,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["activity_id"], str(self.activity.id))
        self.assertEqual(
            payload[0]["participant_id"],
            str(self.participant.id),
        )
        self.assertAlmostEqual(
            datetime.fromisoformat(payload[0]["enrolled_at"]).timestamp(),
            timezone.localtime(own.enrolled_at).timestamp(),
            delta=0.001,
        )

    def test_put_creates_an_idempotent_enrollment(self):
        created_response = self.client.put(
            self.enrollment_url,
            **self.headers,
        )
        repeated_response = self.client.put(
            self.enrollment_url,
            **self.headers,
        )

        self.assertEqual(created_response.status_code, 201)
        self.assertEqual(repeated_response.status_code, 200)
        self.assertEqual(repeated_response.json(), created_response.json())
        self.assertEqual(
            Enrollment.objects.filter(
                participant=self.participant,
                activity=self.activity,
            ).count(),
            1,
        )

    @override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
    def test_put_sends_email_only_when_enrollment_is_created(self):
        self.user.email = "ada@example.com"
        self.user.save(update_fields=["email"])

        created_response = self.client.put(self.enrollment_url, **self.headers)
        repeated_response = self.client.put(self.enrollment_url, **self.headers)

        self.assertEqual(created_response.status_code, 201)
        self.assertEqual(repeated_response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ada@example.com"])
        self.assertIn(self.activity.title, mail.outbox[0].subject)

    @override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
    def test_put_without_user_email_enrolls_without_sending(self):
        response = self.client.put(self.enrollment_url, **self.headers)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(
        EMAIL_BACKEND="activities.tests.test_contrato_api.FailingEmailBackend",
    )
    def test_put_keeps_the_enrollment_when_email_fails(self):
        self.user.email = "ada@example.com"
        self.user.save(update_fields=["email"])

        with self.assertLogs("activities", level="ERROR"):
            response = self.client.put(self.enrollment_url, **self.headers)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Enrollment.objects.filter(
                participant=self.participant,
                activity=self.activity,
            ).exists()
        )

    def test_put_rejects_a_body_and_an_activity_without_capacity(self):
        body_response = self.client.put(
            self.enrollment_url,
            data="{}",
            content_type="application/json",
            **self.headers,
        )
        self.activity.capacity = 1
        self.activity.save(update_fields=["capacity"])
        Enrollment.objects.create(
            participant=self.other_participant,
            activity=self.activity,
        )
        full_response = self.client.put(
            self.enrollment_url,
            **self.headers,
        )

        self.assertEqual(body_response.status_code, 400)
        self.assertEqual(body_response.json()["code"], "invalid_request")
        self.assertEqual(full_response.status_code, 409)
        self.assertEqual(full_response.json()["code"], "capacity_exhausted")

    def test_put_and_delete_report_a_missing_activity(self):
        url = f"/api/v1/me/enrollments/{uuid4()}"

        responses = [
            self.client.put(url, **self.headers),
            self.client.delete(url, **self.headers),
        ]

        for response in responses:
            with self.subTest(method=response.request["REQUEST_METHOD"]):
                self.assertEqual(response.status_code, 404)
                self.assertEqual(
                    response.json()["code"],
                    "activity_not_found",
                )

    def test_delete_is_idempotent_and_releases_the_slot(self):
        self.client.put(self.enrollment_url, **self.headers)

        first_response = self.client.delete(
            self.enrollment_url,
            **self.headers,
        )
        repeated_response = self.client.delete(
            self.enrollment_url,
            **self.headers,
        )
        activity_response = self.client.get(self.activity_url)

        self.assertEqual(first_response.status_code, 204)
        self.assertEqual(first_response.content, b"")
        self.assertEqual(repeated_response.status_code, 204)
        self.assertEqual(repeated_response.content, b"")
        self.assertEqual(activity_response.json()["available_slots"], 2)
        self.assertFalse(
            Enrollment.objects.filter(
                participant=self.participant,
                activity=self.activity,
            ).exists()
        )

    def test_routes_reject_methods_that_are_not_documented(self):
        responses = [
            self.client.post("/api/v1/activities"),
            self.client.put(self.activity_url),
            self.client.post(self.enrollments_url, **self.headers),
            self.client.post(self.enrollment_url, **self.headers),
        ]

        for response in responses:
            with self.subTest(path=response.request["PATH_INFO"]):
                self.assertEqual(response.status_code, 405)
                self.assertIn("Allow", response.headers)

    def test_openapi_exposes_the_complete_contract(self):
        docs_response = self.client.get("/api/v1/docs")
        schema_response = self.client.get("/api/v1/openapi.json")
        schema = schema_response.json()

        self.assertEqual(docs_response.status_code, 200)
        self.assertEqual(schema_response.status_code, 200)
        self.assertEqual(
            set(schema["paths"]),
            {
                "/api/v1/activities",
                "/api/v1/activities/{activity_id}",
                "/api/v1/me/enrollments",
                "/api/v1/me/enrollments/{activity_id}",
                "/api/v1/token/",
                "/api/v1/token/refresh/",
            },
        )
        enrollment_path = schema["paths"][
            "/api/v1/me/enrollments/{activity_id}"
        ]
        self.assertEqual(set(enrollment_path), {"put", "delete"})
        self.assertIn("409", enrollment_path["put"]["responses"])
        self.assertIn("204", enrollment_path["delete"]["responses"])
        self.assertIn("401", enrollment_path["put"]["responses"])
        me_get = schema["paths"]["/api/v1/me/enrollments"]["get"]
        header_parameters = me_get.get("parameters") or []
        self.assertFalse(
            any(
                parameter["in"] == "header"
                and parameter["name"] == "X-Participant-ID"
                for parameter in header_parameters
            )
        )
        self.assertTrue(me_get.get("security") or schema.get("security"))
        self.assertIn("401", me_get["responses"])
        self.assertIn(
            "available_slots",
            schema["components"]["schemas"]["ActivityOut"]["properties"],
        )
