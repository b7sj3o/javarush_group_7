import { request } from './client.js'
import { saveTokens, clearTokens } from './tokens.js'

export async function login(username, password) {
  const tokens = await request('/token/', {
    method: 'POST',
    body: { username, password },
  })
  saveTokens(tokens)
  return tokens
}

// Mirrors the template flow: register() logs the new user in right away,
// so the endpoint returns a JWT pair along with the user.
export async function register(username, password, password2) {
  const data = await request('/auth/register/', {
    method: 'POST',
    body: { username, password, password2 },
  })
  saveTokens(data)
  return data
}

export function logout() {
  clearTokens()
}

export const fetchMe = () => request('/users/me/')

export const updateMe = (patch) =>
  request('/users/me/', { method: 'PATCH', body: patch })
