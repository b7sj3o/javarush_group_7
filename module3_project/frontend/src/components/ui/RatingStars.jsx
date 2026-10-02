/**
 * Read-only star rating. `value` may be null (no reviews yet) — the API
 * returns avg_rating as null/0 for products without reviews.
 */
export default function RatingStars({ value, count }) {
  const rating = Number(value) || 0

  if (!rating) {
    return <span className="text-xs text-muted">Ще без відгуків</span>
  }

  const rounded = Math.round(rating)

  return (
    <span className="inline-flex items-center gap-1.5">
      <span aria-hidden="true" className="text-sm leading-none tracking-tight">
        {[1, 2, 3, 4, 5].map((star) => (
          <span key={star} className={star <= rounded ? 'text-volt' : 'text-line'}>
            ★
          </span>
        ))}
      </span>
      <span className="text-xs text-muted">
        {rating.toFixed(1)}
        {count != null && ` · ${count}`}
      </span>
    </span>
  )
}
