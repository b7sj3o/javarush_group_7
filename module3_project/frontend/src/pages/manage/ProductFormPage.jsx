import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchProduct, createProduct, updateProduct, deleteProduct } from '../../api/products.js'
import { fetchCategories, fetchBrands, fetchSizes } from '../../api/taxonomy.js'
import { useToast } from '../../context/ToastContext.jsx'
import { parseApiError } from '../../utils/errors.js'
import { AUDIENCE_LABELS } from '../../utils/format.js'
import Spinner from '../../components/ui/Spinner.jsx'
import ErrorNote from '../../components/ui/ErrorNote.jsx'

const EMPTY_FORM = {
  name: '',
  category: '',
  brand: '',
  description: '',
  price: '',
  audience: 'unisex',
  sizes: [], // size ids
  stock: '0',
  sku: '',
  is_active: true,
  is_featured: false,
}

/**
 * Create & edit in one page — the SPA analogue of the staff-only
 * product_create / product_update views (ProductForm).
 */
export default function ProductFormPage() {
  const { slug } = useParams() // undefined → create mode
  const isEdit = Boolean(slug)
  const toast = useToast()
  const navigate = useNavigate()

  const [form, setForm] = useState(EMPTY_FORM)
  const [categories, setCategories] = useState([])
  const [brands, setBrands] = useState([])
  const [sizes, setSizes] = useState([])
  // stock/sku are hidden from non-staff API responses; remember whether we
  // actually received them so a PATCH doesn't overwrite unseen values
  const [hasInternalFields, setHasInternalFields] = useState(true)
  const [loading, setLoading] = useState(isEdit)
  const [errors, setErrors] = useState({ general: '', fields: {} })
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    Promise.all([fetchCategories(), fetchBrands(), fetchSizes()])
      .then(([categoriesData, brandsData, sizesData]) => {
        setCategories(categoriesData.results)
        setBrands(brandsData.results)
        setSizes(sizesData)

        if (!isEdit) return null
        return fetchProduct(slug).then((product) => {
          const hasInternal = product.stock !== undefined
          setHasInternalFields(hasInternal)
          setForm({
            name: product.name,
            category: String(product.category.id),
            brand: String(product.brand.id),
            description: product.description ?? '',
            price: product.price,
            audience: product.audience,
            // the read serializer returns size names → map them back to ids
            sizes: sizesData
              .filter((size) => product.sizes.includes(size.name))
              .map((size) => size.id),
            stock: hasInternal ? String(product.stock) : '',
            sku: product.sku ?? '',
            is_active: product.is_active,
            is_featured: product.is_featured,
          })
        })
      })
      .catch(() => setErrors({ general: 'Не вдалося завантажити дані форми.', fields: {} }))
      .finally(() => setLoading(false))
  }, [slug, isEdit])

  function setField(key, value) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  function toggleSize(id) {
    setForm((current) => ({
      ...current,
      sizes: current.sizes.includes(id)
        ? current.sizes.filter((sizeId) => sizeId !== id)
        : [...current.sizes, id],
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setErrors({ general: '', fields: {} })

    const payload = {
      name: form.name,
      category: Number(form.category),
      brand: Number(form.brand),
      description: form.description || null,
      price: form.price,
      audience: form.audience,
      sizes: form.sizes,
      is_active: form.is_active,
      is_featured: form.is_featured,
    }
    if (hasInternalFields) {
      payload.stock = Number(form.stock || 0)
      payload.sku = form.sku.trim() || null
    }

    try {
      const product = isEdit
        ? await updateProduct(slug, payload)
        : await createProduct(payload)
      toast(isEdit ? 'Товар оновлено.' : 'Товар створено.')
      navigate(`/products/${product.slug}`)
    } catch (err) {
      setErrors(parseApiError(err))
    } finally {
      setBusy(false)
    }
  }

  async function handleDelete() {
    if (!window.confirm(`Видалити товар «${form.name}»? Разом з ним зникнуть усі відгуки.`)) return
    try {
      await deleteProduct(slug)
      toast('Товар видалено.')
      navigate('/products')
    } catch {
      toast('Не вдалося видалити товар.', 'error')
    }
  }

  if (loading) return <Spinner />

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="font-display text-2xl font-bold">
        {isEdit ? `Редагування: ${form.name}` : 'Новий товар'}
      </h1>

      <form onSubmit={handleSubmit} className="card mt-6 space-y-4 p-6">
        <div>
          <label className="field-label" htmlFor="product-name">
            Назва
          </label>
          <input
            id="product-name"
            className="input"
            required
            value={form.name}
            onChange={(event) => setField('name', event.target.value)}
          />
          {errors.fields.name && <p className="field-error">{errors.fields.name}</p>}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="field-label" htmlFor="product-category">
              Категорія
            </label>
            <select
              id="product-category"
              className="input"
              required
              value={form.category}
              onChange={(event) => setField('category', event.target.value)}
            >
              <option value="">— оберіть —</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            {errors.fields.category && <p className="field-error">{errors.fields.category}</p>}
          </div>

          <div>
            <label className="field-label" htmlFor="product-brand">
              Бренд
            </label>
            <select
              id="product-brand"
              className="input"
              required
              value={form.brand}
              onChange={(event) => setField('brand', event.target.value)}
            >
              <option value="">— оберіть —</option>
              {brands.map((brand) => (
                <option key={brand.id} value={brand.id}>
                  {brand.name}
                </option>
              ))}
            </select>
            {errors.fields.brand && <p className="field-error">{errors.fields.brand}</p>}
          </div>
        </div>

        <div>
          <label className="field-label" htmlFor="product-description">
            Опис
          </label>
          <textarea
            id="product-description"
            rows={4}
            className="input"
            value={form.description}
            onChange={(event) => setField('description', event.target.value)}
          />
          {errors.fields.description && <p className="field-error">{errors.fields.description}</p>}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="field-label" htmlFor="product-price">
              Ціна, грн
            </label>
            <input
              id="product-price"
              type="number"
              min="0"
              step="0.01"
              className="input"
              required
              value={form.price}
              onChange={(event) => setField('price', event.target.value)}
            />
            {errors.fields.price && <p className="field-error">{errors.fields.price}</p>}
          </div>

          <div>
            <label className="field-label" htmlFor="product-audience">
              Аудиторія
            </label>
            <select
              id="product-audience"
              className="input"
              value={form.audience}
              onChange={(event) => setField('audience', event.target.value)}
            >
              {Object.entries(AUDIENCE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <span className="field-label">Доступні розміри</span>
          <div className="flex flex-wrap gap-2">
            {sizes.map((size) => (
              <label
                key={size.id}
                className={`cursor-pointer rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors ${
                  form.sizes.includes(size.id)
                    ? 'border-accent bg-accent-soft text-accent-deep'
                    : 'border-line hover:border-accent'
                }`}
              >
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={form.sizes.includes(size.id)}
                  onChange={() => toggleSize(size.id)}
                />
                {size.name}
              </label>
            ))}
          </div>
          {errors.fields.sizes && <p className="field-error">{errors.fields.sizes}</p>}
        </div>

        {hasInternalFields && (
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="field-label" htmlFor="product-stock">
                Залишок
              </label>
              <input
                id="product-stock"
                type="number"
                min="0"
                className="input"
                value={form.stock}
                onChange={(event) => setField('stock', event.target.value)}
              />
              {errors.fields.stock && <p className="field-error">{errors.fields.stock}</p>}
            </div>

            <div>
              <label className="field-label" htmlFor="product-sku">
                Артикул
              </label>
              <input
                id="product-sku"
                className="input"
                placeholder="напр. HD-OVR-001, можна лишити порожнім"
                value={form.sku}
                onChange={(event) => setField('sku', event.target.value)}
              />
              {errors.fields.sku && <p className="field-error">{errors.fields.sku}</p>}
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-6">
          <label className="flex cursor-pointer items-center gap-2 text-sm">
            <input
              type="checkbox"
              className="size-4 accent-accent"
              checked={form.is_active}
              onChange={(event) => setField('is_active', event.target.checked)}
            />
            Активний (показувати в каталозі)
          </label>
          <label className="flex cursor-pointer items-center gap-2 text-sm">
            <input
              type="checkbox"
              className="size-4 accent-accent"
              checked={form.is_featured}
              onChange={(event) => setField('is_featured', event.target.checked)}
            />
            Рекомендований
          </label>
        </div>
        {errors.fields.is_featured && <p className="field-error">{errors.fields.is_featured}</p>}

        <ErrorNote>{errors.general}</ErrorNote>

        <div className="flex flex-wrap gap-3 border-t border-line pt-4">
          <button type="submit" disabled={busy} className="btn-primary">
            {busy ? 'Зберігаємо…' : isEdit ? 'Зберегти зміни' : 'Створити товар'}
          </button>
          <button type="button" onClick={() => navigate(-1)} className="btn-outline">
            Скасувати
          </button>
          {isEdit && (
            <button type="button" onClick={handleDelete} className="btn-danger ml-auto">
              Видалити товар
            </button>
          )}
        </div>
      </form>
    </div>
  )
}
