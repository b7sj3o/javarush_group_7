import { useState } from 'react'
import { addFavourite, removeFavourite } from '../../api/products.js'
import { useToast } from '../../context/ToastContext.jsx'

/**
 * Optimistic favourite toggle: the parent flips its state via onChange
 * immediately, and we roll back if the API call fails.
 */
export default function FavouriteButton({ product, onChange, className = '' }) {
  const [busy, setBusy] = useState(false)
  const toast = useToast()

  async function toggle() {
    const wasFavourite = product.is_favourite
    setBusy(true)
    onChange(product.slug, !wasFavourite)

    try {
      if (wasFavourite) await removeFavourite(product.slug)
      else await addFavourite(product.slug)
    } catch {
      onChange(product.slug, wasFavourite) // rollback
      toast('Не вдалося оновити обране.', 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      disabled={busy}
      aria-pressed={product.is_favourite}
      aria-label={product.is_favourite ? 'Прибрати з обраного' : 'Додати в обране'}
      className={`flex size-9 items-center justify-center rounded-full border border-line bg-card
        text-lg transition-colors hover:border-accent disabled:opacity-50 ${
          product.is_favourite ? 'text-accent' : 'text-muted/50'
        } ${className}`}
    >
      {product.is_favourite ? '♥' : '♡'}
    </button>
  )
}
