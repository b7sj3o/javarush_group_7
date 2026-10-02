import { getAccess, getRefresh, saveTokens, clearTokens } from './tokens.js'

const BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api/v1'

// Non-2xx responses become ApiError; err.data keeps the DRF payload
// (e.g. { price: ["Ціна має бути більшою за 0."] }) for form rendering.
export class ApiError extends Error {
  constructor(status, data) {
    super(`API request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

// Uses raw fetch, not request(): a failed refresh must not trigger another refresh.
async function tryRefresh() {
  const refresh = getRefresh()
  if (!refresh) return false

  const response = await fetch(`${BASE}/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })

  if (!response.ok) {
    clearTokens() // refresh token expired → the user has to log in again
    return false
  }

  saveTokens(await response.json())
  return true
}

/**
 * The single entry point for every API call.
 * - attaches the Bearer token when we have one;
 * - on 401 tries to refresh the access token once and retries the request;
 * - returns parsed JSON (null for 204), throws ApiError otherwise.
 */
export async function request(path, { method = 'GET', body, signal, retry = true } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  const access = getAccess()
  if (access) headers.Authorization = `Bearer ${access}`

  const response = await fetch(`${BASE}${path}`, {
    method,
    headers,
    signal,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (response.status === 401 && retry && getRefresh()) {
    if (await tryRefresh()) {
      return request(path, { method, body, signal, retry: false })
    }
  }

  if (response.status === 204) return null

  const data = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(response.status, data)
  return data
}
