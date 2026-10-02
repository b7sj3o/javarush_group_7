export default function EmptyState({ title, hint }) {
  return (
    <div className="py-16 text-center">
      <p className="font-display text-base font-bold">{title}</p>
      {hint && <p className="mt-2 text-sm text-muted">{hint}</p>}
    </div>
  )
}
