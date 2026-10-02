import { createContext, useContext, useCallback, useRef, useState } from 'react'

// Client-side replacement for the Django messages framework:
// toast('Товар додано') shows a short-lived notification.
const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const nextId = useRef(1)

  const toast = useCallback((text, type = 'success') => {
    const id = nextId.current++
    setToasts((current) => [...current, { id, text, type }])
    setTimeout(() => {
      setToasts((current) => current.filter((item) => item.id !== id))
    }, 4000)
  }, [])

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="pointer-events-none fixed inset-x-0 top-4 z-50 flex flex-col items-center gap-2 px-4">
        {toasts.map(({ id, text, type }) => (
          <div
            key={id}
            role="status"
            className={`card pointer-events-auto px-4 py-2 text-sm font-medium shadow-lg ${
              type === 'error' ? 'border-danger/40 text-danger' : 'border-accent/40'
            }`}
          >
            {text}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components -- the hook belongs next to its provider
export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>')
  return ctx
}
