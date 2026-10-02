import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { fetchProducts } from '../api/products.js'
import { fetchCategories, fetchBrands, fetchSizes } from '../api/taxonomy.js'
import { useAuth } from '../context/AuthContext.jsx'
import { AUDIENCE_LABELS } from '../utils/format.js'
import FilterSidebar from '../components/product/FilterSidebar.jsx'
import ProductCard from '../components/product/ProductCard.jsx'
import DebouncedSearchInput from '../components/ui/DebouncedSearchInput.jsx'
import Pagination from '../components/ui/Pagination.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import EmptyState from '../components/ui/EmptyState.jsx'
import ErrorNote from '../components/ui/ErrorNote.jsx'

const ORDERING_OPTIONS = [
  { value: '', label: 'Новинки' },
  { value: 'price', label: 'Дешевші спершу' },
  { value: '-price', label: 'Дорожчі спершу' },
  { value: 'name', label: 'За назвою (А–Я)' },
  { value: '-avg_rating', label: 'За рейтингом' },
]

/**
 * The URL query string is the single source of truth for the filters
 * (like the GET form in the template version): the page survives refresh
 * and filtered links can be shared. Checkbox groups are repeated params
 * (?category=hudi&category=kurtky), read back via searchParams.getAll().
 */
export default function CatalogPage() {
  const { user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  // result.key remembers which query the data belongs to: while it differs
  // from the current queryKey we are loading (no sync setState in effects)
  const [result, setResult] = useState({ key: '', data: null, error: false })
  const [categories, setCategories] = useState([])
  const [brands, setBrands] = useState([])
  const [sizes, setSizes] = useState([])
  const [showFilters, setShowFilters] = useState(false) // mobile only

  // is_favourite in the response depends on who is logged in
  const queryKey = `${searchParams.toString()}|${user?.username ?? ''}`
  const loading = result.key !== queryKey
  const { data, error } = result

  const filters = {
    search: searchParams.get('q') ?? '',
    categories: searchParams.getAll('category'),
    brands: searchParams.getAll('brand'),
    sizes: searchParams.getAll('size'),
    audiences: searchParams.getAll('audience'),
    minPrice: searchParams.get('min_price') ?? '',
    maxPrice: searchParams.get('max_price') ?? '',
    minRating: searchParams.get('min_rating') ?? '',
    inStock: searchParams.get('in_stock') === '1',
    ordering: searchParams.get('ordering') ?? '',
    page: Number(searchParams.get('page')) || 1,
  }

  function changeFilters(partial) {
    const next = { ...filters, ...partial }
    // Any filter change sends the user back to page 1
    if (!('page' in partial)) next.page = 1

    const params = new URLSearchParams()
    if (next.search) params.set('q', next.search)
    for (const value of next.categories) params.append('category', value)
    for (const value of next.brands) params.append('brand', value)
    for (const value of next.sizes) params.append('size', value)
    for (const value of next.audiences) params.append('audience', value)
    if (next.minPrice) params.set('min_price', next.minPrice)
    if (next.maxPrice) params.set('max_price', next.maxPrice)
    if (next.minRating) params.set('min_rating', next.minRating)
    if (next.inStock) params.set('in_stock', '1')
    if (next.ordering) params.set('ordering', next.ordering)
    if (next.page > 1) params.set('page', String(next.page))
    setSearchParams(params)
  }

  useEffect(() => {
    fetchCategories().then((data) => setCategories(data.results)).catch(() => {})
    fetchBrands().then((data) => setBrands(data.results)).catch(() => {})
    fetchSizes().then(setSizes).catch(() => {})
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    fetchProducts(filters, { signal: controller.signal })
      .then((data) => setResult({ key: queryKey, data, error: false }))
      .catch((err) => {
        if (err.name !== 'AbortError') setResult({ key: queryKey, data: null, error: true })
      })

    return () => controller.abort()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queryKey])

  function handleFavouriteChange(slug, isFavourite) {
    setResult((current) => ({
      ...current,
      data: {
        ...current.data,
        results: current.data.results.map((product) =>
          product.slug === slug ? { ...product, is_favourite: isFavourite } : product,
        ),
      },
    }))
  }

  // Chips of the applied filters (shown above the grid, Rozetka-style)
  const chips = []
  const removeFrom = (key, value) => () =>
    changeFilters({ [key]: filters[key].filter((item) => item !== value) })

  for (const slug of filters.categories) {
    const name = categories.find((category) => category.slug === slug)?.name ?? slug
    chips.push({ id: `category-${slug}`, label: name, onRemove: removeFrom('categories', slug) })
  }
  for (const slug of filters.brands) {
    const name = brands.find((brand) => brand.slug === slug)?.name ?? slug
    chips.push({ id: `brand-${slug}`, label: name, onRemove: removeFrom('brands', slug) })
  }
  for (const name of filters.sizes) {
    chips.push({ id: `size-${name}`, label: `Розмір ${name}`, onRemove: removeFrom('sizes', name) })
  }
  for (const value of filters.audiences) {
    chips.push({
      id: `audience-${value}`,
      label: AUDIENCE_LABELS[value] ?? value,
      onRemove: removeFrom('audiences', value),
    })
  }
  if (filters.minPrice || filters.maxPrice) {
    const from = filters.minPrice ? `від ${filters.minPrice}` : ''
    const to = filters.maxPrice ? `до ${filters.maxPrice}` : ''
    chips.push({
      id: 'price',
      label: `Ціна ${[from, to].filter(Boolean).join(' ')} грн`,
      onRemove: () => changeFilters({ minPrice: '', maxPrice: '' }),
    })
  }
  if (filters.minRating) {
    chips.push({
      id: 'rating',
      label: `${filters.minRating}★ і вище`,
      onRemove: () => changeFilters({ minRating: '' }),
    })
  }
  if (filters.inStock) {
    chips.push({ id: 'stock', label: 'В наявності', onRemove: () => changeFilters({ inStock: false }) })
  }

  return (
    <>
      <h1 className="font-display text-2xl font-bold">Каталог</h1>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <DebouncedSearchInput
          className="max-w-64"
          placeholder="Пошук: напр. худі"
          value={filters.search}
          onChange={(search) => changeFilters({ search })}
        />

        <button
          type="button"
          onClick={() => setShowFilters((open) => !open)}
          className="btn-outline lg:hidden"
          aria-expanded={showFilters}
        >
          Фільтри{chips.length > 0 && ` (${chips.length})`}
        </button>

        <label className="ml-auto flex items-center gap-2 text-sm text-muted">
          Сортування
          <select
            className="input w-auto"
            value={filters.ordering}
            onChange={(event) => changeFilters({ ordering: event.target.value })}
          >
            {ORDERING_OPTIONS.map(({ value, label }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-6 items-start gap-8 lg:flex">
        <FilterSidebar
          className={`${showFilters ? 'block' : 'hidden'} mb-6 lg:mb-0 lg:block lg:w-64 lg:shrink-0 lg:sticky lg:top-20 lg:max-h-[calc(100vh-6rem)] lg:overflow-y-auto`}
          filters={filters}
          categories={categories}
          brands={brands}
          sizes={sizes}
          activeCount={chips.length}
          onChange={changeFilters}
          onReset={() => setSearchParams({})}
        />

        <div className="min-w-0 flex-1">
          {chips.length > 0 && (
            <div className="mb-4 flex flex-wrap items-center gap-2">
              {chips.map(({ id, label, onRemove }) => (
                <button
                  key={id}
                  type="button"
                  onClick={onRemove}
                  className="badge cursor-pointer gap-1.5 border border-accent/30 bg-accent-soft text-accent-deep hover:border-accent"
                  aria-label={`Прибрати фільтр: ${label}`}
                >
                  {label}
                  <span aria-hidden="true">✕</span>
                </button>
              ))}
              <button
                type="button"
                onClick={() => setSearchParams({})}
                className="text-xs text-muted hover:text-accent"
              >
                Скинути все
              </button>
            </div>
          )}

          {loading ? (
            <Spinner />
          ) : error ? (
            <ErrorNote>Не вдалося завантажити каталог. Спробуйте оновити сторінку.</ErrorNote>
          ) : data.results.length === 0 ? (
            <EmptyState
              title="Нічого не знайдено"
              hint="Спробуйте змінити фільтри або скинути їх."
            />
          ) : (
            <>
              <p className="text-sm text-muted">Знайдено товарів: {data.pagination.count}</p>
              <div className="mt-4 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                {data.results.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onFavouriteChange={handleFavouriteChange}
                  />
                ))}
              </div>
              <Pagination
                pagination={data.pagination}
                onPage={(page) => changeFilters({ page })}
              />
            </>
          )}
        </div>
      </div>
    </>
  )
}
