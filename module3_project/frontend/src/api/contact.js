import { request } from './client.js'

export const sendContactMessage = (data) =>
  request('/contact/', { method: 'POST', body: data })
