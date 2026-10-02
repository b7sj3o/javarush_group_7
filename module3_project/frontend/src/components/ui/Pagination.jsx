/**
 * Renders pager controls from the API's pagination block:
 * { count, pages, current, next, previous }.
 */
export default function Pagination({ pagination, onPage }) {
  if (!pagination || pagination.pages <= 1) return null

  const { current, pages } = pagination

  return (
    <nav className="mt-8 flex items-center justify-center gap-4" aria-label="Пагінація">
      <button
        type="button"
        className="btn-outline px-3 py-1.5"
        disabled={current <= 1}
        onClick={() => onPage(current - 1)}
      >
        ← Назад
      </button>
      <span className="text-sm text-muted">
        Сторінка {current} із {pages}
      </span>
      <button
        type="button"
        className="btn-outline px-3 py-1.5"
        disabled={current >= pages}
        onClick={() => onPage(current + 1)}
      >
        Далі →
      </button>
    </nav>
  )
}
