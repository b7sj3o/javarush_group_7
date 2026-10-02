import { useState } from 'react'
import { createReview } from '../../api/reviews.js'
import { parseApiError } from '../../utils/errors.js'
import { useToast } from '../../context/ToastContext.jsx'
import ErrorNote from '../ui/ErrorNote.jsx'

export default function ReviewForm({ productId, onCreated }) {
  const [rating, setRating] = useState(5)
  const [text, setText] = useState('')
  const [errors, setErrors] = useState({ general: '', fields: {} })
  const [busy, setBusy] = useState(false)
  const toast = useToast()

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setErrors({ general: '', fields: {} })

    try {
      await createReview(productId, rating, text.trim())
      setText('')
      setRating(5)
      toast('Відгук додано. Дякуємо!')
      onCreated()
    } catch (err) {
      setErrors(parseApiError(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-4 p-5">
      <h3 className="font-display text-sm font-bold">Залишити відгук</h3>

      <div>
        <span className="field-label">Оцінка</span>
        <div className="flex gap-1" role="radiogroup" aria-label="Оцінка від 1 до 5">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              role="radio"
              aria-checked={rating === star}
              aria-label={`${star} з 5`}
              onClick={() => setRating(star)}
              className={`text-2xl transition-colors ${
                star <= rating ? 'text-volt' : 'text-line hover:text-volt/60'
              }`}
            >
              ★
            </button>
          ))}
        </div>
        {errors.fields.rating && <p className="field-error">{errors.fields.rating}</p>}
      </div>

      <div>
        <label className="field-label" htmlFor="review-text">
          Ваш відгук
        </label>
        <textarea
          id="review-text"
          rows={3}
          className="input"
          placeholder="Ваші враження про товар"
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        {errors.fields.text && <p className="field-error">{errors.fields.text}</p>}
      </div>

      <ErrorNote>{errors.general}</ErrorNote>

      <button type="submit" disabled={busy} className="btn-primary">
        {busy ? 'Надсилаємо…' : 'Опублікувати'}
      </button>
    </form>
  )
}
