import { useState } from 'react'
import { sendContactMessage } from '../api/contact.js'
import { parseApiError } from '../utils/errors.js'
import { useToast } from '../context/ToastContext.jsx'
import ErrorNote from '../components/ui/ErrorNote.jsx'

const SUBJECTS = [
  { value: 'product', label: 'Питання про товар' },
  { value: 'order', label: 'Питання про замовлення' },
  { value: 'delivery', label: 'Доставка й оплата' },
  { value: 'return', label: 'Повернення / обмін' },
  { value: 'other', label: 'Інше' },
]

const EMPTY_FORM = {
  name: '',
  email: '',
  subject: 'product',
  order_number: '',
  message: '',
  consent: false,
}

export default function ContactPage() {
  const toast = useToast()
  const [form, setForm] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({ general: '', fields: {} })
  const [busy, setBusy] = useState(false)

  const needsOrderNumber = form.subject === 'order' || form.subject === 'return'

  function setField(key, value) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setErrors({ general: '', fields: {} })

    try {
      const { detail } = await sendContactMessage(form)
      toast(detail)
      setForm(EMPTY_FORM)
    } catch (err) {
      setErrors(parseApiError(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <h1 className="font-display text-2xl font-bold">Контакти</h1>

      <div className="mt-6 grid gap-8 md:grid-cols-[2fr_1fr]">
        <form onSubmit={handleSubmit} className="card space-y-4 p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="field-label" htmlFor="contact-name">
                Ваше імʼя
              </label>
              <input
                id="contact-name"
                className="input"
                placeholder="Як до вас звертатися"
                required
                value={form.name}
                onChange={(event) => setField('name', event.target.value)}
              />
              {errors.fields.name && <p className="field-error">{errors.fields.name}</p>}
            </div>

            <div>
              <label className="field-label" htmlFor="contact-email">
                Email
              </label>
              <input
                id="contact-email"
                type="email"
                className="input"
                placeholder="you@example.com"
                required
                value={form.email}
                onChange={(event) => setField('email', event.target.value)}
              />
              {errors.fields.email && <p className="field-error">{errors.fields.email}</p>}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="field-label" htmlFor="contact-subject">
                Тема звернення
              </label>
              <select
                id="contact-subject"
                className="input"
                value={form.subject}
                onChange={(event) => setField('subject', event.target.value)}
              >
                {SUBJECTS.map(({ value, label }) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="field-label" htmlFor="contact-order">
                Номер замовлення{needsOrderNumber ? '' : ' (необовʼязково)'}
              </label>
              <input
                id="contact-order"
                className="input"
                placeholder="напр. 100237"
                value={form.order_number}
                onChange={(event) => setField('order_number', event.target.value)}
              />
              {errors.fields.order_number && (
                <p className="field-error">{errors.fields.order_number}</p>
              )}
            </div>
          </div>

          <div>
            <label className="field-label" htmlFor="contact-message">
              Повідомлення
            </label>
            <textarea
              id="contact-message"
              rows={5}
              className="input"
              placeholder="Опишіть питання якомога детальніше"
              required
              value={form.message}
              onChange={(event) => setField('message', event.target.value)}
            />
            {errors.fields.message && <p className="field-error">{errors.fields.message}</p>}
          </div>

          <div>
            <label className="flex cursor-pointer items-start gap-2 text-sm">
              <input
                type="checkbox"
                className="mt-0.5 size-4 accent-accent"
                checked={form.consent}
                onChange={(event) => setField('consent', event.target.checked)}
                required
              />
              Погоджуюсь на обробку персональних даних
            </label>
            {errors.fields.consent && <p className="field-error">{errors.fields.consent}</p>}
          </div>

          <ErrorNote>{errors.general}</ErrorNote>

          <button type="submit" disabled={busy} className="btn-primary">
            {busy ? 'Надсилаємо…' : 'Надіслати'}
          </button>
        </form>

        <aside className="card h-fit p-6 text-sm">
          <h2 className="font-display text-sm font-bold">Ми на звʼязку</h2>
          <dl className="mt-4 space-y-3">
            <div>
              <dt className="field-label">Email</dt>
              <dd>hello@potuzhno.shop</dd>
            </div>
            <div>
              <dt className="field-label">Телефон</dt>
              <dd>0 800 210 210</dd>
            </div>
            <div>
              <dt className="field-label">Графік</dt>
              <dd>щодня 9:00–20:00</dd>
            </div>
          </dl>
        </aside>
      </div>
    </>
  )
}
