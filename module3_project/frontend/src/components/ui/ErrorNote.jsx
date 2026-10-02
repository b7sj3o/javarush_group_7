export default function ErrorNote({ children }) {
  if (!children) return null
  return (
    <div className="rounded-lg border border-danger/30 bg-danger-soft px-4 py-3 text-sm text-danger">
      {children}
    </div>
  )
}
