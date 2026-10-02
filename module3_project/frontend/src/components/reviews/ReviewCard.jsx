import { formatDate } from '../../utils/format.js'

export default function ReviewCard({ review, canDelete, onDelete }) {
  return (
    <article className="card p-4">
      <header className="flex flex-wrap items-center gap-x-3 gap-y-1">
        <span className="font-semibold">{review.user}</span>
        <span aria-label={`Оцінка ${review.rating} з 5`} className="text-sm">
          {[1, 2, 3, 4, 5].map((star) => (
            <span key={star} className={star <= review.rating ? 'text-volt' : 'text-line'}>
              ★
            </span>
          ))}
        </span>
        <time className="text-xs text-muted">{formatDate(review.created_at)}</time>
        {canDelete && (
          <button
            type="button"
            onClick={() => onDelete(review)}
            className="ml-auto text-xs text-danger hover:underline"
          >
            Видалити
          </button>
        )}
      </header>
      {review.text && <p className="mt-2 text-sm leading-relaxed">{review.text}</p>}
    </article>
  )
}
