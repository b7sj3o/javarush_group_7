import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'
import { formatPrice, AUDIENCE_LABELS } from '../../utils/format.js'
import ProductTile from './ProductTile.jsx'
import FavouriteButton from './FavouriteButton.jsx'
import RatingStars from '../ui/RatingStars.jsx'

export default function ProductCard({ product, onFavouriteChange }) {
  const { user } = useAuth()

  return (
    <article className="card group relative overflow-hidden transition-all hover:-translate-y-0.5 hover:border-accent/50 hover:shadow-md">
      <Link to={`/products/${product.slug}`} className="block" aria-label={product.name}>
        <ProductTile name={product.name} className="aspect-[4/3]" />

        <div className="p-4">
          <div className="flex items-baseline justify-between gap-2">
            <h3 className="font-semibold group-hover:text-accent">{product.name}</h3>
          </div>
          <p className="mt-0.5 text-xs text-muted">
            {product.category?.name}
            {product.brand?.name && ` · ${product.brand.name}`}
          </p>

          <div className="mt-2">
            <RatingStars value={product.avg_rating} count={product.reviews_count} />
          </div>

          {product.sizes?.length > 0 && (
            <p className="mt-2 flex flex-wrap gap-1">
              {product.sizes.map((size) => (
                <span key={size} className="badge border border-line text-muted">
                  {size}
                </span>
              ))}
            </p>
          )}

          <div className="mt-3 flex items-center justify-between">
            <span className="text-base font-bold">{formatPrice(product.price)}</span>
            <span className="badge bg-accent-soft text-accent-deep">
              {AUDIENCE_LABELS[product.audience] ?? product.audience}
            </span>
          </div>
        </div>
      </Link>

      {user && onFavouriteChange && (
        <FavouriteButton
          product={product}
          onChange={onFavouriteChange}
          className="absolute top-3 right-3"
        />
      )}
    </article>
  )
}
