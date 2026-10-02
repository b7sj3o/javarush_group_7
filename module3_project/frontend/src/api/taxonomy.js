import { request } from './client.js'

// Categories, brands and sizes are small reference lists ("довідники").
// page_size=100 (the API maximum) fetches them in one request for selects.

export const fetchCategories = ({ signal } = {}) =>
  request('/categories/?page_size=100', { signal })

export const fetchBrands = ({ signal } = {}) =>
  request('/brands/?page_size=100', { signal })

export const fetchSizes = ({ signal } = {}) => request('/sizes/', { signal })

// CRUD for the taxonomy management page (superuser or "Менеджер каталогу")

export const createCategory = (data) =>
  request('/categories/', { method: 'POST', body: data })

export const updateCategory = (id, data) =>
  request(`/categories/${id}/`, { method: 'PATCH', body: data })

export const deleteCategory = (id) =>
  request(`/categories/${id}/`, { method: 'DELETE' })

export const createBrand = (data) =>
  request('/brands/', { method: 'POST', body: data })

export const updateBrand = (id, data) =>
  request(`/brands/${id}/`, { method: 'PATCH', body: data })

export const deleteBrand = (id) =>
  request(`/brands/${id}/`, { method: 'DELETE' })
