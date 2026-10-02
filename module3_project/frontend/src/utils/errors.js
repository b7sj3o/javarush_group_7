import { ApiError } from '../api/client.js'

/**
 * Turns any error from the API layer into { general, fields } for forms:
 * general — a message for the whole form ("Ви вже залишали відгук…"),
 * fields  — per-field messages keyed by field name ({ price: "Ціна має…" }).
 */
export function parseApiError(err) {
  if (!(err instanceof ApiError)) {
    return { general: 'Немає звʼязку з сервером. Перевірте, чи запущений бекенд.', fields: {} }
  }

  if (!err.data || typeof err.data !== 'object') {
    return { general: `Помилка сервера (${err.status}).`, fields: {} }
  }

  const fields = {}
  let general = ''

  for (const [key, value] of Object.entries(err.data)) {
    const text = Array.isArray(value) ? value.join(' ') : String(value)
    if (key === 'detail' || key === 'non_field_errors') general = text
    else fields[key] = text
  }

  if (!general && Object.keys(fields).length === 0) {
    general = `Помилка сервера (${err.status}).`
  }

  return { general, fields }
}
