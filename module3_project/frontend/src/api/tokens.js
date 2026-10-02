// JWT storage. localStorage is a deliberate simplicity trade-off (see L20b):
// an httpOnly-cookie setup would be safer against XSS but much more involved.
const ACCESS = 'potuzhno_access'
const REFRESH = 'potuzhno_refresh'

export const getAccess = () => localStorage.getItem(ACCESS)
export const getRefresh = () => localStorage.getItem(REFRESH)

export function saveTokens({ access, refresh }) {
  localStorage.setItem(ACCESS, access)
  if (refresh) localStorage.setItem(REFRESH, refresh)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS)
  localStorage.removeItem(REFRESH)
}

export const hasTokens = () => Boolean(getAccess() || getRefresh())
