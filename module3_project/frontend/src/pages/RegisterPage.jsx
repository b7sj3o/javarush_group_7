import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useToast } from '../context/ToastContext.jsx'
import { parseApiError } from '../utils/errors.js'
import ErrorNote from '../components/ui/ErrorNote.jsx'

export default function RegisterPage() {
  const { register } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [errors, setErrors] = useState({ general: '', fields: {} })
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setErrors({ general: '', fields: {} })

    try {
      // Registers and logs in at once — like the template version did
      await register(username, password, password2)
      toast(`Акаунт створено. Вітаємо, ${username}!`)
      navigate('/')
    } catch (err) {
      setErrors(parseApiError(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-sm py-10">
      <h1 className="font-display text-2xl font-bold">Реєстрація</h1>

      <form onSubmit={handleSubmit} className="card mt-6 space-y-4 p-6">
        <div>
          <label className="field-label" htmlFor="reg-username">
            Логін
          </label>
          <input
            id="reg-username"
            className="input"
            autoComplete="username"
            required
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
          {errors.fields.username && <p className="field-error">{errors.fields.username}</p>}
        </div>

        <div>
          <label className="field-label" htmlFor="reg-password">
            Пароль
          </label>
          <input
            id="reg-password"
            type="password"
            className="input"
            autoComplete="new-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          {errors.fields.password && <p className="field-error">{errors.fields.password}</p>}
        </div>

        <div>
          <label className="field-label" htmlFor="reg-password2">
            Пароль ще раз
          </label>
          <input
            id="reg-password2"
            type="password"
            className="input"
            autoComplete="new-password"
            required
            value={password2}
            onChange={(event) => setPassword2(event.target.value)}
          />
          {errors.fields.password2 && <p className="field-error">{errors.fields.password2}</p>}
        </div>

        <ErrorNote>{errors.general}</ErrorNote>

        <button type="submit" disabled={busy} className="btn-primary w-full">
          {busy ? 'Створюємо…' : 'Створити акаунт'}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-muted">
        Вже маєте акаунт?{' '}
        <Link to="/login" className="font-semibold text-accent hover:underline">
          Увійдіть
        </Link>
      </p>
    </div>
  )
}
