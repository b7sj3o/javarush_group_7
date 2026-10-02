import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="py-20 text-center">
      <p className="font-display text-6xl font-black text-accent">404</p>
      <h1 className="mt-4 font-display text-xl font-bold">Такої сторінки немає</h1>
      <p className="mt-2 text-sm text-muted">Але каталог нікуди не дівся.</p>
      <Link to="/products" className="btn-primary mt-6">
        До каталогу
      </Link>
    </div>
  )
}
