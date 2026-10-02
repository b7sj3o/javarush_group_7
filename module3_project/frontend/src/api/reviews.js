import { request } from './client.js'

export const createReview = (productId, rating, text) =>
  request('/reviews/', {
    method: 'POST',
    body: { product: productId, rating, text },
  })

export const deleteReview = (id) =>
  request(`/reviews/${id}/`, { method: 'DELETE' })

export const fetchMyReviews = (page = 1, { signal } = {}) =>
  request(`/reviews/mine/?page_number=${page}`, { signal })
