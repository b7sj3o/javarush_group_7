import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import Spinner from './ui/Spinner.jsx'

/**
 * Route guard, the SPA analogue of @login_required.
 * With `manager` it additionally requires catalog-management rights
 * (superuser or the "Менеджер каталогу" group).
 */
export default function RequireAuth({ manager = false, children }) {
  const { user, booting, isManager } = useAuth()
  const location = useLocation()

  // Still checking the stored token — render nothing meaningful yet,
  // otherwise we would redirect a logged-in user to /login on refresh.
  if (booting) return <Spinner />

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }

  if (manager && !isManager) {
    return (
      <div className="card mx-auto max-w-md p-8 text-center">
        <h1 className="font-display text-lg font-bold">Недостатньо прав</h1>
        <p className="mt-2 text-sm text-muted">
          Ця сторінка доступна лише менеджерам каталогу.
        </p>
      </div>
    )
  }

  return children
}
