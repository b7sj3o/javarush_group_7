import { useEffect, useState } from 'react'
import {
  fetchCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  fetchBrands,
  createBrand,
  updateBrand,
  deleteBrand,
} from '../../api/taxonomy.js'
import { useToast } from '../../context/ToastContext.jsx'
import { parseApiError } from '../../utils/errors.js'
import Spinner from '../../components/ui/Spinner.jsx'
import ErrorNote from '../../components/ui/ErrorNote.jsx'

/**
 * One reusable panel handles both reference lists — only the API
 * functions differ. In the template version this lived in Django admin.
 */
function TaxonomyPanel({ title, api }) {
  const toast = useToast()
  const [items, setItems] = useState(null)
  const [draft, setDraft] = useState({ name: '', slug: '' })
  const [editingId, setEditingId] = useState(null)
  const [editDraft, setEditDraft] = useState({ name: '', slug: '' })
  const [errors, setErrors] = useState({ general: '', fields: {} })

  function load() {
    api.fetchAll().then((data) => setItems(data.results)).catch(() => setItems([]))
  }

  useEffect(load, []) // eslint-disable-line react-hooks/exhaustive-deps

  async function handleCreate(event) {
    event.preventDefault()
    setErrors({ general: '', fields: {} })
    try {
      await api.create(draft)
      setDraft({ name: '', slug: '' })
      toast(`Запис «${draft.name}» додано.`)
      load()
    } catch (err) {
      setErrors(parseApiError(err))
    }
  }

  async function handleUpdate(id) {
    setErrors({ general: '', fields: {} })
    try {
      await api.update(id, editDraft)
      setEditingId(null)
      toast('Запис оновлено.')
      load()
    } catch (err) {
      setErrors(parseApiError(err))
    }
  }

  async function handleDelete(item) {
    if (!window.confirm(`Видалити «${item.name}»?`)) return
    try {
      await api.remove(item.id)
      toast(`Запис «${item.name}» видалено.`)
      load()
    } catch (err) {
      // 409 from the API: the record is protected by products referencing it
      toast(parseApiError(err).general || 'Не вдалося видалити.', 'error')
    }
  }

  return (
    <section className="card p-6">
      <h2 className="font-display text-lg font-bold">{title}</h2>

      {items === null ? (
        <Spinner />
      ) : (
        <ul className="mt-4 divide-y divide-line">
          {items.map((item) => (
            <li key={item.id} className="flex flex-wrap items-center gap-2 py-2.5">
              {editingId === item.id ? (
                <>
                  <input
                    className="input w-36 flex-1"
                    aria-label="Назва"
                    value={editDraft.name}
                    onChange={(event) => setEditDraft({ ...editDraft, name: event.target.value })}
                  />
                  <input
                    className="input w-36 flex-1"
                    aria-label="Slug"
                    value={editDraft.slug}
                    onChange={(event) => setEditDraft({ ...editDraft, slug: event.target.value })}
                  />
                  <button type="button" className="btn-primary px-3 py-1.5" onClick={() => handleUpdate(item.id)}>
                    Зберегти
                  </button>
                  <button type="button" className="btn-outline px-3 py-1.5" onClick={() => setEditingId(null)}>
                    Скасувати
                  </button>
                </>
              ) : (
                <>
                  <span className="font-medium">{item.name}</span>
                  <span className="text-xs text-muted">/{item.slug}</span>
                  <span className="ml-auto flex gap-3">
                    <button
                      type="button"
                      className="text-xs text-accent hover:underline"
                      onClick={() => {
                        setEditingId(item.id)
                        setEditDraft({ name: item.name, slug: item.slug })
                      }}
                    >
                      Змінити
                    </button>
                    <button
                      type="button"
                      className="text-xs text-danger hover:underline"
                      onClick={() => handleDelete(item)}
                    >
                      Видалити
                    </button>
                  </span>
                </>
              )}
            </li>
          ))}
          {items.length === 0 && (
            <li className="py-3 text-sm text-muted">Поки що порожньо.</li>
          )}
        </ul>
      )}

      <form onSubmit={handleCreate} className="mt-4 border-t border-line pt-4">
        <div className="flex flex-wrap gap-2">
          <input
            className="input w-36 flex-1"
            placeholder="Назва"
            aria-label="Назва"
            required
            value={draft.name}
            onChange={(event) => setDraft({ ...draft, name: event.target.value })}
          />
          <input
            className="input w-36 flex-1"
            placeholder="slug (латиницею)"
            aria-label="Slug"
            required
            value={draft.slug}
            onChange={(event) => setDraft({ ...draft, slug: event.target.value })}
          />
          <button type="submit" className="btn-primary">
            Додати
          </button>
        </div>
        {errors.fields.name && <p className="field-error">{errors.fields.name}</p>}
        {errors.fields.slug && <p className="field-error">{errors.fields.slug}</p>}
        <div className="mt-2">
          <ErrorNote>{errors.general}</ErrorNote>
        </div>
      </form>
    </section>
  )
}

export default function TaxonomyPage() {
  return (
    <>
      <h1 className="font-display text-2xl font-bold">Довідники</h1>
      <p className="mt-1 text-sm text-muted">
        Категорії та бренди каталогу. Розміри керуються через Django admin.
      </p>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <TaxonomyPanel
          title="Категорії"
          api={{
            fetchAll: fetchCategories,
            create: createCategory,
            update: updateCategory,
            remove: deleteCategory,
          }}
        />
        <TaxonomyPanel
          title="Бренди"
          api={{
            fetchAll: fetchBrands,
            create: createBrand,
            update: updateBrand,
            remove: deleteBrand,
          }}
        />
      </div>
    </>
  )
}
