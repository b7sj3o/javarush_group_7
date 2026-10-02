import { useState } from 'react'
import { AUDIENCE_LABELS } from '../../utils/format.js'

// Collapsible filter group (native <details> — accessible out of the box)
function FilterGroup({ title, children }) {
  return (
    <details open className="group px-4 py-3">
      <summary className="flex cursor-pointer list-none items-center justify-between text-sm font-semibold select-none [&::-webkit-details-marker]:hidden">
        {title}
        <span aria-hidden="true" className="text-muted transition-transform group-open:rotate-180">
          ▾
        </span>
      </summary>
      <div className="mt-3">{children}</div>
    </details>
  )
}

function CheckOption({ checked, onChange, children }) {
  return (
    <label className="flex cursor-pointer items-center gap-2.5 py-1 text-sm hover:text-accent">
      <input type="checkbox" className="size-4 shrink-0 accent-accent" checked={checked} onChange={onChange} />
      {children}
    </label>
  )
}

const RATING_OPTIONS = [
  { value: '', label: 'Будь-який' },
  { value: '4', label: '4★ і вище' },
  { value: '3', label: '3★ і вище' },
]

/**
 * Rozetka-style filter sidebar: checkbox groups with multi-select.
 * The parent owns the state (URL query string); every change goes
 * through onChange with a partial filters object.
 */
export default function FilterSidebar({
  filters,
  categories,
  brands,
  sizes,
  activeCount,
  onChange,
  onReset,
  className = '',
}) {
  const [minPrice, setMinPrice] = useState(filters.minPrice)
  const [maxPrice, setMaxPrice] = useState(filters.maxPrice)

  // Re-seed the price drafts when filters change from outside (chips, reset)
  const [prevFilters, setPrevFilters] = useState(filters)
  if (prevFilters.minPrice !== filters.minPrice || prevFilters.maxPrice !== filters.maxPrice) {
    setPrevFilters(filters)
    setMinPrice(filters.minPrice)
    setMaxPrice(filters.maxPrice)
  }

  // OR within a group: toggling adds/removes one value from the array
  function toggle(key, value) {
    const list = filters[key]
    onChange({
      [key]: list.includes(value) ? list.filter((item) => item !== value) : [...list, value],
    })
  }

  return (
    <aside className={className} aria-label="Фільтри">
      <div className="card divide-y divide-line">
        <div className="flex items-center justify-between px-4 py-3">
          <h2 className="font-display text-sm font-bold">Фільтри</h2>
          {activeCount > 0 && (
            <button type="button" onClick={onReset} className="text-xs text-muted hover:text-accent">
              Скинути все ({activeCount})
            </button>
          )}
        </div>

        <FilterGroup title="Категорія">
          {categories.map((category) => (
            <CheckOption
              key={category.id}
              checked={filters.categories.includes(category.slug)}
              onChange={() => toggle('categories', category.slug)}
            >
              {category.name}
            </CheckOption>
          ))}
        </FilterGroup>

        <FilterGroup title="Бренд">
          {brands.map((brand) => (
            <CheckOption
              key={brand.id}
              checked={filters.brands.includes(brand.slug)}
              onChange={() => toggle('brands', brand.slug)}
            >
              {brand.name}
            </CheckOption>
          ))}
        </FilterGroup>

        <FilterGroup title="Розмір">
          <div className="flex flex-wrap gap-2">
            {sizes.map((size) => (
              <label
                key={size.id}
                className={`cursor-pointer rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors ${
                  filters.sizes.includes(size.name)
                    ? 'border-accent bg-accent-soft text-accent-deep'
                    : 'border-line hover:border-accent'
                }`}
              >
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={filters.sizes.includes(size.name)}
                  onChange={() => toggle('sizes', size.name)}
                />
                {size.name}
              </label>
            ))}
          </div>
        </FilterGroup>

        <FilterGroup title="Для кого">
          {Object.entries(AUDIENCE_LABELS).map(([value, label]) => (
            <CheckOption
              key={value}
              checked={filters.audiences.includes(value)}
              onChange={() => toggle('audiences', value)}
            >
              {label}
            </CheckOption>
          ))}
        </FilterGroup>

        <FilterGroup title="Ціна, грн">
          <form
            className="flex items-center gap-2"
            onSubmit={(event) => {
              event.preventDefault()
              onChange({ minPrice, maxPrice })
            }}
          >
            <input
              type="number"
              min="0"
              className="input min-w-0 flex-1 px-2"
              placeholder="від"
              aria-label="Ціна від"
              value={minPrice}
              onChange={(event) => setMinPrice(event.target.value)}
            />
            <span className="text-muted">–</span>
            <input
              type="number"
              min="0"
              className="input min-w-0 flex-1 px-2"
              placeholder="до"
              aria-label="Ціна до"
              value={maxPrice}
              onChange={(event) => setMaxPrice(event.target.value)}
            />
            <button type="submit" className="btn-outline px-3 py-2">
              OK
            </button>
          </form>
        </FilterGroup>

        <FilterGroup title="Рейтинг">
          {RATING_OPTIONS.map(({ value, label }) => (
            <label
              key={value}
              className="flex cursor-pointer items-center gap-2.5 py-1 text-sm hover:text-accent"
            >
              <input
                type="radio"
                name="min_rating"
                className="size-4 shrink-0 accent-accent"
                checked={filters.minRating === value}
                onChange={() => onChange({ minRating: value })}
              />
              {label}
            </label>
          ))}
        </FilterGroup>

        <FilterGroup title="Наявність">
          <CheckOption
            checked={filters.inStock}
            onChange={() => onChange({ inStock: !filters.inStock })}
          >
            Тільки в наявності
          </CheckOption>
        </FilterGroup>
      </div>
    </aside>
  )
}
