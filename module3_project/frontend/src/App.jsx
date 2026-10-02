import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout.jsx'
import RequireAuth from './components/RequireAuth.jsx'
import HomePage from './pages/HomePage.jsx'
import CatalogPage from './pages/CatalogPage.jsx'
import ProductDetailPage from './pages/ProductDetailPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'
import ContactPage from './pages/ContactPage.jsx'
import ProductFormPage from './pages/manage/ProductFormPage.jsx'
import TaxonomyPage from './pages/manage/TaxonomyPage.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/products" element={<CatalogPage />} />
        <Route path="/products/:slug" element={<ProductDetailPage />} />
        <Route path="/contact" element={<ContactPage />} />

        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          path="/profile"
          element={
            <RequireAuth>
              <ProfilePage />
            </RequireAuth>
          }
        />

        {/* Catalog management: superuser or "Менеджер каталогу" group */}
        <Route
          path="/manage/products/new"
          element={
            <RequireAuth manager>
              <ProductFormPage />
            </RequireAuth>
          }
        />
        <Route
          path="/manage/products/:slug/edit"
          element={
            <RequireAuth manager>
              <ProductFormPage />
            </RequireAuth>
          }
        />
        <Route
          path="/manage/taxonomy"
          element={
            <RequireAuth manager>
              <TaxonomyPage />
            </RequireAuth>
          }
        />

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
