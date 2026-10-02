import { createContext, useContext, useCallback, useEffect, useState } from 'react'
import * as authApi from '../api/auth.js'
import { hasTokens } from '../api/tokens.js'

const CATALOG_MANAGER_GROUP = 'Менеджер каталогу'
const REVIEW_MODERATOR_GROUP = 'Модератор відгуків'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  // true while we check the stored token on first load,
  // so guarded routes don't redirect before we know who the user is
  const [booting, setBooting] = useState(hasTokens())

  useEffect(() => {
    if (!hasTokens()) return

    authApi
      .fetchMe()
      .then(setUser)
      .catch(() => authApi.logout()) // stored tokens are stale → drop them
      .finally(() => setBooting(false))
  }, [])

  const login = useCallback(async (username, password) => {
    await authApi.login(username, password)
    setUser(await authApi.fetchMe())
  }, [])

  const register = useCallback(async (username, password, password2) => {
    await authApi.register(username, password, password2)
    setUser(await authApi.fetchMe())
  }, [])

  const logout = useCallback(() => {
    authApi.logout()
    setUser(null)
  }, [])

  const updateProfile = useCallback(async (patch) => {
    setUser(await authApi.updateMe(patch))
  }, [])

  const groups = user?.groups ?? []
  const value = {
    user,
    booting,
    login,
    register,
    logout,
    updateProfile,
    isManager: Boolean(user?.is_superuser || groups.includes(CATALOG_MANAGER_GROUP)),
    isModerator: Boolean(user?.is_superuser || groups.includes(REVIEW_MODERATOR_GROUP)),
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components -- the hook belongs next to its provider
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
