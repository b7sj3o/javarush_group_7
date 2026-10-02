import { request } from './client.js'

/**
 * Catalog list. The products endpoint uses the custom StandardPagination:
 * response is { pagination: { count, pages, current, ... }, results: [...] }
 * and the page parameter is called page_number (not page).
 *
 * Checkbox filters (categories/brands/sizes/audiences) are arrays and become
 * repeated query params (?category=hudi&category=kurtky): the API ORs values
 * within a group and ANDs the groups together.
 */
export function fetchProducts(
  {
    search,
    categories = [],
    brands = [],
    sizes = [],
    audiences = [],
    minPrice,
    maxPrice,
    minRating,
    inStock,
    ordering,
    page,
    pageSize,
  } = {},
  { signal } = {},
) {
  const params = new URLSearchParams()
  params.set('is_active', 'true') // the catalog shows active products only, like the templates
  if (search) params.set('search', search)
  for (const slug of categories) params.append('category', slug)
  for (const slug of brands) params.append('brand', slug)
  for (const name of sizes) params.append('size', name)
  for (const value of audiences) params.append('audience', value)
  if (minPrice) params.set('min_price', minPrice)
  if (maxPrice) params.set('max_price', maxPrice)
  if (minRating) params.set('min_rating', minRating)
  if (inStock) params.set('in_stock', 'true')
  if (ordering) params.set('ordering', ordering)
  if (page && page > 1) params.set('page_number', page)
  if (pageSize) params.set('page_size', pageSize)

  return request(`/products/?${params}`, { signal })
}

export const fetchFeatured = ({ signal } = {}) =>
  request('/products/featured/?is_active=true&page_size=3', { signal })

export const fetchProduct = (slug, { signal } = {}) =>
  request(`/products/${slug}/`, { signal })

export const fetchProductReviews = (slug, page = 1, { signal } = {}) =>
  request(`/products/${slug}/reviews/?page_number=${page}`, { signal })

export const fetchFavourites = (page = 1, { signal } = {}) =>
  request(`/products/favourites/?page_number=${page}`, { signal })

export const addFavourite = (slug) =>
  request(`/products/${slug}/favourite/`, { method: 'POST' })

export const removeFavourite = (slug) =>
  request(`/products/${slug}/favourite/`, { method: 'DELETE' })

// Catalog management (superuser or "Менеджер каталогу" group)

export const createProduct = (data) =>
  request('/products/', { method: 'POST', body: data })

export const updateProduct = (slug, data) =>
  request(`/products/${slug}/`, { method: 'PATCH', body: data })

export const deleteProduct = (slug) =>
  request(`/products/${slug}/`, { method: 'DELETE' })
