import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { fetchProduct, fetchProductReviews, deleteProduct } from '../api/products.js'
import { deleteReview } from '../api/reviews.js'
import { useAuth } from '../context/AuthContext.jsx'
import { useToast } from '../context/ToastContext.jsx'
import { formatPrice, AUDIENCE_LABELS } from '../utils/format.js'
import ProductTile from '../components/product/ProductTile.jsx'
import FavouriteButton from '../components/product/FavouriteButton.jsx'
import RatingStars from '../components/ui/RatingStars.jsx'
import ReviewCard from '../components/reviews/ReviewCard.jsx'
import ReviewForm from '../components/reviews/ReviewForm.jsx'
import Pagination from '../components/ui/Pagination.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import EmptyState from '../components/ui/EmptyState.jsx'

function ReviewsSection({ slug, productId, onRatingChange }) {
  const { user, isModerator } = useAuth()
  const toast = useToast()
  const [reviews, setReviews] = useState(null) // { pagination, results }
  const [page, setPage] = useState(1)
  const [version, setVersion] = useState(0) // bump to refetch after add/delete

  useEffect(() => {
    fetchProductReviews(slug, page).then(setReviews).catch(() => {})
  }, [slug, page, version])

  // A created/deleted review also changes the product's avg_rating
  function refresh() {
    setVersion((v) => v + 1)
    onRatingChange()
  }

  async function handleDelete(review) {
    if (!window.confirm('Видалити цей відгук?')) return
    try {
      await deleteReview(review.id)
      toast('Відгук видалено.')
      refresh()
    } catch {
      toast('Не вдалося видалити відгук.', 'error')
    }
  }

  return (
    <section className="mt-12 max-w-3xl">
      <h2 className="font-display text-xl font-bold">
        Відгуки{reviews && ` (${reviews.pagination?.count ?? reviews.results.length})`}
      </h2>

      <div className="mt-5 space-y-3">
        {reviews === null ? (
          <Spinner />
        ) : reviews.results.length === 0 ? (
          <p className="text-sm text-muted">Ще ніхто не залишив відгук — будьте першим.</p>
        ) : (
          reviews.results.map((review) => (
            <ReviewCard
              key={review.id}
              review={review}
              canDelete={Boolean(user) && (review.user === user.username || isModerator)}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>

      {reviews && <Pagination pagination={reviews.pagination} onPage={setPage} />}

      <div className="mt-8">
        {user ? (
          <ReviewForm productId={productId} onCreated={refresh} />
        ) : (
          <p className="card p-5 text-sm text-muted">
            <Link to="/login" className="font-semibold text-accent hover:underline">
              Увійдіть
            </Link>
            , щоб залишити відгук.
          </p>
        )}
      </div>
    </section>
  )
}

export default function ProductDetailPage() {
  const { slug } = useParams()
  const { user, isManager } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()

  const [product, setProduct] = useState(null)
  const [notFoundSlug, setNotFoundSlug] = useState(null)
  const [version, setVersion] = useState(0) // bump to refetch (rating changed)

  // product/notFound keep the slug they belong to, so navigating between
  // products needs no state reset inside the effect
  const notFound = notFoundSlug === slug
  const loaded = product?.slug === slug

  useEffect(() => {
    fetchProduct(slug)
      .then(setProduct)
      .catch((err) => {
        if (err.status === 404) setNotFoundSlug(slug)
      })
  }, [slug, user, version])

  async function handleDeleteProduct() {
    const confirmed = window.confirm(
      `Видалити товар «${product.name}»? Разом з ним зникнуть усі відгуки.`,
    )
    if (!confirmed) return
    try {
      await deleteProduct(slug)
      toast('Товар видалено.')
      navigate('/products')
    } catch {
      toast('Не вдалося видалити товар.', 'error')
    }
  }

  if (notFound) {
    return <EmptyState title="Товар не знайдено" hint="Можливо, його вже зняли з продажу." />
  }

  if (!loaded) return <Spinner />

  const isStaffView = product.stock !== undefined

  return (
    <>
      <nav className="text-sm text-muted" aria-label="Хлібні крихти">
        <Link to="/products" className="hover:text-accent">
          Каталог
        </Link>
        <span className="mx-2">/</span>
        <span className="text-ink">{product.name}</span>
      </nav>

      <div className="mt-6 grid gap-8 md:grid-cols-2">
        <ProductTile name={product.name} large className="aspect-square rounded-xl" />

        <div>
          <p className="flex flex-wrap gap-2">
            <span className="badge bg-accent-soft text-accent-deep">
              {product.category?.name}
            </span>
            {product.brand?.name && (
              <span className="badge border border-line text-muted">{product.brand.name}</span>
            )}
            <span className="badge border border-line text-muted">
              {AUDIENCE_LABELS[product.audience] ?? product.audience}
            </span>
          </p>

          <h1 className="mt-3 font-display text-2xl font-bold sm:text-3xl">{product.name}</h1>

          <div className="mt-2">
            <RatingStars value={product.avg_rating} count={product.reviews_count} />
          </div>

          <p className="mt-4 text-3xl font-bold">{formatPrice(product.price)}</p>

          <p className="mt-3">
            {product.in_stock ? (
              <span className="badge bg-accent-soft text-accent-deep">В наявності</span>
            ) : (
              <span className="badge bg-danger-soft text-danger">Немає в наявності</span>
            )}
            {isStaffView && (
              <span className="ml-2 text-xs text-muted">
                Залишок: {product.stock} шт.{product.sku && ` · Артикул: ${product.sku}`}
              </span>
            )}
          </p>

          {product.sizes?.length > 0 && (
            <div className="mt-5">
              <span className="field-label">Розміри</span>
              <p className="flex flex-wrap gap-2">
                {product.sizes.map((size) => (
                  <span
                    key={size}
                    className="rounded-lg border border-line px-3 py-1.5 text-sm font-medium"
                  >
                    {size}
                  </span>
                ))}
              </p>
            </div>
          )}

          <div className="mt-6 flex flex-wrap items-center gap-3">
            {/* Cart is not built yet (neither models nor API) — honest placeholder,
                same as the disabled button in the template version */}
            <button type="button" disabled className="btn-primary" title="Кошик у розробці">
              🛒 Додати в кошик — скоро
            </button>
            {user && (
              <FavouriteButton
                product={product}
                onChange={(_, isFavourite) =>
                  setProduct({ ...product, is_favourite: isFavourite })
                }
              />
            )}
          </div>

          {isManager && (
            <div className="mt-6 flex gap-3 border-t border-line pt-4">
              <Link to={`/manage/products/${product.slug}/edit`} className="btn-outline">
                Редагувати
              </Link>
              <button type="button" onClick={handleDeleteProduct} className="btn-danger">
                Видалити
              </button>
            </div>
          )}

          {product.description && (
            <div className="mt-6">
              <h2 className="field-label">Опис</h2>
              <p className="text-sm leading-relaxed whitespace-pre-line">{product.description}</p>
            </div>
          )}
        </div>
      </div>

      {/* key={slug} remounts the section (and resets its page) per product */}
      <ReviewsSection
        key={slug}
        slug={slug}
        productId={product.id}
        onRatingChange={() => setVersion((v) => v + 1)}
      />
    </>
  )
}
