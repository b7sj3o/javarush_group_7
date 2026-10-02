export default function Footer() {
  return (
    <footer className="mt-16 border-t border-line py-8">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 text-sm text-muted">
        <span>
          <span className="font-display text-xs font-bold text-ink">ПОТУЖНО</span> · навчальний
          проєкт JavaRush
        </span>
        <span>© {new Date().getFullYear()}</span>
      </div>
    </footer>
  )
}
