import { useEffect, useState } from 'react'

// Returns `value` after it has stopped changing for `delay` ms.
// Used by the catalog search so we don't hit the API on every keystroke.
export function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debounced
}
