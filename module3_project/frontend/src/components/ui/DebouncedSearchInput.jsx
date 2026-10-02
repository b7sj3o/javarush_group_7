import { useEffect, useState } from 'react'
import { useDebounce } from '../../hooks/useDebounce.js'

/**
 * Controlled-from-outside search input with an internal debounced draft:
 * onChange fires only after the user stops typing.
 */
export default function DebouncedSearchInput({ value, onChange, placeholder, className = '' }) {
  const [draft, setDraft] = useState(value)
  const debounced = useDebounce(draft)

  // Re-seed the draft when the value changes from outside (e.g. filters reset) —
  // the "adjusting state during render" pattern from the React docs
  const [prevValue, setPrevValue] = useState(value)
  if (prevValue !== value) {
    setPrevValue(value)
    setDraft(value)
  }

  useEffect(() => {
    if (debounced !== value) onChange(debounced)
  }, [debounced]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <input
      type="search"
      className={`input ${className}`}
      placeholder={placeholder}
      aria-label={placeholder}
      value={draft}
      onChange={(event) => setDraft(event.target.value)}
    />
  )
}
