import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchFeatured } from '../api/products.js'
import { useAuth } from '../context/AuthContext.jsx'
import ProductCard from '../components/product/ProductCard.jsx'
import Spinner from '../components/ui/Spinner.jsx'

export default function HomePage() {
  const { user } = useAuth()
  const [products, setProducts] = useState(null)

  useEffect(() => {
    const controller = new AbortController()

    fetchFeatured({ signal: controller.signal })
      .then((data) => setProducts(data.results))
      .catch((err) => {
        if (err.name !== 'AbortError') setProducts([])
      })

    return () => controller.abort()
  }, [user]) // refetch after login/logout — is_favourite depends on the user

  function handleFavouriteChange(slug, isFavourite) {
    setProducts((current) =>
      current.map((product) =>
        product.slug === slug ? { ...product, is_favourite: isFavourite } : product,
      ),
    )
  }

  return (
    <>
      <section className="py-14 sm:py-20">
        <p className="text-xs font-semibold tracking-[0.25em] text-muted uppercase">
          Одяг і взуття
        </p>
        <h1 className="mt-3 font-display text-5xl font-black tracking-tight sm:text-7xl">
          ПОТУЖНО<span className="text-accent">.</span>
        </h1>
        <p className="mt-5 max-w-xl text-base leading-relaxed text-muted">
          Каталог речей, у яких зручно жити: від худі до кросівок. Обирайте розмір,
          читайте відгуки, зберігайте улюблене.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/products" className="btn-primary px-6 py-3">
            Перейти в каталог
          </Link>
          {!user && (
            <Link to="/register" className="btn-outline px-6 py-3">
              Створити акаунт
            </Link>
          )}
        </div>
      </section>

      <section>
        <div>
          <h2 className="font-display text-xl font-bold">Рекомендовані</h2>
          <span className="mt-2 block h-1.5 w-10 rounded-full bg-volt" aria-hidden="true" />
        </div>

        {products === null ? (
          <Spinner />
        ) : products.length === 0 ? (
          <p className="mt-4 text-sm text-muted">Поки що нічого не рекомендуємо — зазирніть у каталог.</p>
        ) : (
          <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onFavouriteChange={handleFavouriteChange}
              />
            ))}
          </div>
        )}
      </section>
    </>
  )
}
