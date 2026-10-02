import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchFavourites } from '../api/products.js'
import { fetchMyReviews, deleteReview } from '../api/reviews.js'
import { useAuth } from '../context/AuthContext.jsx'
import { useToast } from '../context/ToastContext.jsx'
import { formatDate } from '../utils/format.js'
import { parseApiError } from '../utils/errors.js'
import ProductCard from '../components/product/ProductCard.jsx'
import Pagination from '../components/ui/Pagination.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import ErrorNote from '../components/ui/ErrorNote.jsx'

function ProfileDetails() {
  const { user, updateProfile } = useAuth()
  const toast = useToast()

  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ email: '', phone: '', address: '' })
  const [errors, setErrors] = useState({ general: '', fields: {} })
  const [busy, setBusy] = useState(false)

  function startEditing() {
    setForm({ email: user.email, phone: user.phone, address: user.address })
    setErrors({ general: '', fields: {} })
    setEditing(true)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setErrors({ general: '', fields: {} })

    try {
      await updateProfile(form)
      toast('Профіль оновлено.')
      setEditing(false)
    } catch (err) {
      setErrors(parseApiError(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="card p-6">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="font-display text-xl font-bold">{user.username}</h1>
        {user.is_staff && <span className="badge bg-volt-soft text-ink">staff</span>}
        {user.groups.map((group) => (
          <span key={group} className="badge bg-accent-soft text-accent-deep">
            {group}
          </span>
        ))}
        <span className="ml-auto text-xs text-muted">
          З нами з {formatDate(user.date_joined)}
        </span>
      </div>

      {editing ? (
        <form onSubmit={handleSubmit} className="mt-5 grid gap-4 sm:grid-cols-3">
          {[
            { key: 'email', label: 'Email', type: 'email' },
            { key: 'phone', label: 'Телефон', type: 'tel' },
            { key: 'address', label: 'Адреса', type: 'text' },
          ].map(({ key, label, type }) => (
            <div key={key}>
              <label className="field-label" htmlFor={`profile-${key}`}>
                {label}
              </label>
              <input
                id={`profile-${key}`}
                type={type}
                className="input"
                value={form[key]}
                onChange={(event) => setForm({ ...form, [key]: event.target.value })}
              />
              {errors.fields[key] && <p className="field-error">{errors.fields[key]}</p>}
            </div>
          ))}

          <div className="sm:col-span-3">
            <ErrorNote>{errors.general}</ErrorNote>
          </div>

          <div className="flex gap-3 sm:col-span-3">
            <button type="submit" disabled={busy} className="btn-primary">
              {busy ? 'Зберігаємо…' : 'Зберегти'}
            </button>
            <button type="button" onClick={() => setEditing(false)} className="btn-outline">
              Скасувати
            </button>
          </div>
        </form>
      ) : (
        <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-3">
          <div>
            <dt className="field-label">Email</dt>
            <dd>{user.email || <span className="text-muted">не вказано</span>}</dd>
          </div>
          <div>
            <dt className="field-label">Телефон</dt>
            <dd>{user.phone || <span className="text-muted">не вказано</span>}</dd>
          </div>
          <div>
            <dt className="field-label">Адреса</dt>
            <dd>{user.address || <span className="text-muted">не вказано</span>}</dd>
          </div>
        </dl>
      )}

      {!editing && (
        <button type="button" onClick={startEditing} className="btn-outline mt-5">
          Редагувати профіль
        </button>
      )}
    </section>
  )
}

export default function ProfilePage() {
  const toast = useToast()

  const [favourites, setFavourites] = useState(null)
  const [favouritesPage, setFavouritesPage] = useState(1)
  const [reviews, setReviews] = useState(null)
  const [reviewsPage, setReviewsPage] = useState(1)

  useEffect(() => {
    fetchFavourites(favouritesPage).then(setFavourites).catch(() => {})
  }, [favouritesPage])

  useEffect(() => {
    fetchMyReviews(reviewsPage).then(setReviews).catch(() => {})
  }, [reviewsPage])

  // Un-hearting a product on the profile page removes it from the list
  function handleFavouriteChange(slug, isFavourite) {
    if (!isFavourite) {
      setFavourites((current) => ({
        ...current,
        results: current.results.filter((product) => product.slug !== slug),
      }))
    }
  }

  async function handleDeleteReview(review) {
    if (!window.confirm('Видалити цей відгук?')) return
    try {
      await deleteReview(review.id)
      toast('Відгук видалено.')
      setReviews((current) => ({
        ...current,
        results: current.results.filter((item) => item.id !== review.id),
      }))
    } catch {
      toast('Не вдалося видалити відгук.', 'error')
    }
  }

  return (
    <div className="space-y-10">
      <ProfileDetails />

      <section>
        <h2 className="font-display text-lg font-bold">Обране</h2>
        {favourites === null ? (
          <Spinner />
        ) : favourites.results.length === 0 ? (
          <p className="mt-3 text-sm text-muted">
            Поки що порожньо — тисніть ♡ на товарах у{' '}
            <Link to="/products" className="font-semibold text-accent hover:underline">
              каталозі
            </Link>
            .
          </p>
        ) : (
          <>
            <div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {favourites.results.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onFavouriteChange={handleFavouriteChange}
                />
              ))}
            </div>
            <Pagination pagination={favourites.pagination} onPage={setFavouritesPage} />
          </>
        )}
      </section>

      <section>
        <h2 className="font-display text-lg font-bold">Мої відгуки</h2>
        {reviews === null ? (
          <Spinner />
        ) : reviews.results.length === 0 ? (
          <p className="mt-3 text-sm text-muted">Ви ще не залишали відгуків.</p>
        ) : (
          <>
            <div className="mt-4 space-y-3">
              {reviews.results.map((review) => (
                <article key={review.id} className="card p-4">
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                    <Link
                      to={`/products/${review.product.slug}`}
                      className="font-semibold hover:text-accent"
                    >
                      {review.product.name}
                    </Link>
                    <span className="text-sm" aria-label={`Оцінка ${review.rating} з 5`}>
                      {[1, 2, 3, 4, 5].map((star) => (
                        <span
                          key={star}
                          className={star <= review.rating ? 'text-volt' : 'text-line'}
                        >
                          ★
                        </span>
                      ))}
                    </span>
                    <time className="text-xs text-muted">{formatDate(review.created_at)}</time>
                    <button
                      type="button"
                      onClick={() => handleDeleteReview(review)}
                      className="ml-auto text-xs text-danger hover:underline"
                    >
                      Видалити
                    </button>
                  </div>
                  {review.text && <p className="mt-2 text-sm">{review.text}</p>}
                </article>
              ))}
            </div>
            <Pagination pagination={reviews.pagination} onPage={setReviewsPage} />
          </>
        )}
      </section>
    </div>
  )
}
