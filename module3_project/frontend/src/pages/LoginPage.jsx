import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useToast } from '../context/ToastContext.jsx'
import ErrorNote from '../components/ui/ErrorNote.jsx'

export default function LoginPage() {
  const { login } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const location = useLocation()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')

    try {
      await login(username, password)
      toast(`Вітаємо, ${username}!`)
      // RequireAuth remembers where the user came from
      navigate(location.state?.from ?? '/', { replace: true })
    } catch (err) {
      setError(
        err.status === 401
          ? 'Невірний логін або пароль.'
          : 'Не вдалося увійти. Спробуйте ще раз.',
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-sm py-10">
      <h1 className="font-display text-2xl font-bold">Вхід</h1>

      <form onSubmit={handleSubmit} className="card mt-6 space-y-4 p-6">
        <div>
          <label className="field-label" htmlFor="login-username">
            Логін
          </label>
          <input
            id="login-username"
            className="input"
            autoComplete="username"
            required
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </div>

        <div>
          <label className="field-label" htmlFor="login-password">
            Пароль
          </label>
          <input
            id="login-password"
            type="password"
            className="input"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>

        <ErrorNote>{error}</ErrorNote>

        <button type="submit" disabled={busy} className="btn-primary w-full">
          {busy ? 'Входимо…' : 'Увійти'}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-muted">
        Немає акаунта?{' '}
        <Link to="/register" className="font-semibold text-accent hover:underline">
          Зареєструйтесь
        </Link>
      </p>
    </div>
  )
}
