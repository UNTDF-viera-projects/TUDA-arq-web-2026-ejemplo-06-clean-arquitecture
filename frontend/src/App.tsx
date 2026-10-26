import { type FormEvent, useEffect, useState } from 'react'
import './App.css'

const TOKEN_KEY = 'accessToken'

interface Activity {
  id: string
  title: string
  starts_at: string
  capacity: number
  available_slots: number
}

interface Enrollment {
  activity_id: string
  participant_id: string
  enrolled_at: string
}

function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

function App() {
  const [token, setToken] = useState<string | null>(() => getStoredToken())
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [authError, setAuthError] = useState<string | null>(null)
  const [isLoggingIn, setIsLoggingIn] = useState(false)

  const [activities, setActivities] = useState<Activity[]>([])
  const [enrolledIds, setEnrolledIds] = useState<Set<string>>(new Set())
  const [isFetching, setIsFetching] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [enrollingId, setEnrollingId] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  function persistToken(next: string | null) {
    setToken(next)
    if (next) {
      localStorage.setItem(TOKEN_KEY, next)
    } else {
      localStorage.removeItem(TOKEN_KEY)
      setEnrolledIds(new Set())
    }
  }

  useEffect(() => {
    let cancelled = false

    async function load() {
      setIsFetching(true)
      setLoadError(null)
      try {
        const activitiesResponse = await fetch('/api/v1/activities')
        if (!activitiesResponse.ok) {
          throw new Error('Error al obtener las actividades')
        }
        const nextActivities = (await activitiesResponse.json()) as Activity[]

        let nextEnrolled = new Set<string>()
        if (token) {
          const enrollmentsResponse = await fetch('/api/v1/me/enrollments', {
            headers: { Authorization: `Bearer ${token}` },
          })
          if (enrollmentsResponse.status === 401) {
            persistToken(null)
          } else if (!enrollmentsResponse.ok) {
            throw new Error('Error al obtener las inscripciones')
          } else {
            const enrollments = (await enrollmentsResponse.json()) as Enrollment[]
            nextEnrolled = new Set(enrollments.map((item) => item.activity_id))
          }
        }

        if (!cancelled) {
          setActivities(nextActivities)
          setEnrolledIds(nextEnrolled)
        }
      } catch (error) {
        if (!cancelled) {
          setLoadError(error instanceof Error ? error.message : 'Error desconocido')
        }
      } finally {
        if (!cancelled) {
          setIsFetching(false)
        }
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [token])

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsLoggingIn(true)
    setAuthError(null)
    setNotice(null)
    try {
      const response = await fetch('/api/v1/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      if (!response.ok) {
        throw new Error('Usuario o contraseña inválidos')
      }
      const payload = (await response.json()) as { access: string }
      persistToken(payload.access)
      setPassword('')
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'No se pudo iniciar sesión')
    } finally {
      setIsLoggingIn(false)
    }
  }

  async function handleEnroll(activity: Activity) {
    if (!token) {
      setNotice('Iniciá sesión para inscribirte.')
      return
    }

    setEnrollingId(activity.id)
    setNotice(null)
    try {
      const response = await fetch(`/api/v1/me/enrollments/${activity.id}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.status === 401) {
        persistToken(null)
        setNotice('La sesión expiró. Volvé a iniciar sesión.')
        return
      }
      if (response.status === 409) {
        setNotice('No hay cupos disponibles.')
        return
      }
      if (!response.ok) {
        throw new Error('No se pudo completar la inscripción')
      }

      const created = response.status === 201
      setEnrolledIds((current) => {
        const next = new Set(current)
        next.add(activity.id)
        return next
      })
      if (created) {
        setActivities((current) =>
          current.map((item) =>
            item.id === activity.id
              ? { ...item, available_slots: Math.max(item.available_slots - 1, 0) }
              : item,
          ),
        )
        setNotice(`Inscripción confirmada en «${activity.title}». Revisá el email en Mailpit.`)
      } else {
        setNotice(`Ya estabas inscrito en «${activity.title}».`)
      }
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'No se pudo completar la inscripción')
    } finally {
      setEnrollingId(null)
    }
  }

  return (
    <main>
      <h1>Actividades</h1>
      <p>Inscribite en una actividad. Al confirmarse se envía un email de aviso.</p>

      {token ? (
        <div className="session-bar">
          <p>Sesión iniciada.</p>
          <button type="button" onClick={() => persistToken(null)}>
            Cerrar sesión
          </button>
        </div>
      ) : (
        <form className="login-form" onSubmit={handleLogin}>
          <h2>Iniciar sesión</h2>
          <p className="hint">Usuario de demostración: demo / demo</p>
          <label>
            Usuario
            <input
              name="username"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>
          <label>
            Contraseña
            <input
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {authError ? <p className="error">{authError}</p> : null}
          <button type="submit" disabled={isLoggingIn}>
            {isLoggingIn ? 'Ingresando…' : 'Ingresar'}
          </button>
        </form>
      )}

      {notice ? <p className="notice">{notice}</p> : null}

      {isFetching ? <p>Cargando actividades...</p> : null}
      {loadError ? <p className="error">Error al cargar actividades: {loadError}</p> : null}
      {!isFetching && !loadError && activities.length === 0 ? (
        <p>No hay actividades cargadas.</p>
      ) : null}

      {!isFetching && !loadError && activities.length > 0 ? (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th scope="col">Título</th>
                <th scope="col">Comienza</th>
                <th scope="col">Capacidad</th>
                <th scope="col">Cupos disponibles</th>
                <th scope="col">Inscripción</th>
              </tr>
            </thead>
            <tbody>
              {activities.map((activity) => {
                const enrolled = enrolledIds.has(activity.id)
                const full = activity.available_slots <= 0
                const busy = enrollingId === activity.id
                let actionLabel = 'Inscribirse'
                if (enrolled) {
                  actionLabel = 'Inscrito'
                } else if (full) {
                  actionLabel = 'Sin cupo'
                } else if (busy) {
                  actionLabel = 'Inscribiendo…'
                }

                return (
                  <tr key={activity.id}>
                    <td>{activity.title}</td>
                    <td>
                      <time dateTime={activity.starts_at}>
                        {new Date(activity.starts_at).toLocaleString('es-AR')}
                      </time>
                    </td>
                    <td>{activity.capacity}</td>
                    <td>{activity.available_slots}</td>
                    <td>
                      <button
                        type="button"
                        onClick={() => void handleEnroll(activity)}
                        disabled={!token || enrolled || full || busy}
                      >
                        {actionLabel}
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      ) : null}
    </main>
  )
}

export default App
