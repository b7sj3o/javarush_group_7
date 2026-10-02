import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'
import { useToast } from '../../context/ToastContext.jsx'

const navLinkClass = ({ isActive }) =>
  `text-sm font-medium transition-colors hover:text-accent ${
    isActive ? 'text-accent' : 'text-ink'
  }`

export default function Header() {
  const { user, isManager, logout } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    toast('Ви вийшли з акаунта.')
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-card/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
        <Link to="/" className="flex items-center gap-2" aria-label="ПОТУЖНО Shop — на головну">
          <span className="flex size-7 items-center justify-center rounded-md bg-accent font-display text-sm font-bold text-white">
            П
          </span>
          <span className="font-display text-sm font-bold tracking-tight">
            ПОТУЖНО<span className="text-accent">.</span>shop
          </span>
        </Link>

        <nav className="flex items-center gap-4">
          <NavLink to="/products" className={navLinkClass}>
            Каталог
          </NavLink>
          <NavLink to="/contact" className={navLinkClass}>
            Контакти
          </NavLink>
          {isManager && (
            <NavLink to="/manage/taxonomy" className={navLinkClass}>
              Довідники
            </NavLink>
          )}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          {isManager && (
            <Link to="/manage/products/new" className="btn-outline px-3 py-1.5">
              + Товар
            </Link>
          )}
          {user ? (
            <>
              <Link
                to="/profile"
                className="text-sm font-semibold text-ink transition-colors hover:text-accent"
              >
                {user.username}
              </Link>
              <button type="button" onClick={handleLogout} className="btn-outline px-3 py-1.5">
                Вийти
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm font-medium hover:text-accent">
                Увійти
              </Link>
              <Link to="/register" className="btn-primary px-3 py-1.5">
                Реєстрація
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
