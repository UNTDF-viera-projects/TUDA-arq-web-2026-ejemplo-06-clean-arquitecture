from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/v1/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("api/v1/", include("activities.api_urls")),
    path("", include("activities.urls")),
    path(
        "api/v1/openapi.json",
        SpectacularJSONAPIView.as_view(),
        name="api-schema",
    ),
    path(
        "api/v1/docs",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]
