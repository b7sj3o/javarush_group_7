import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { createProduct, getCategories, getProducts } from "./api.js";

const initialProductForm = {
  title: "",
  short_description: "",
  description: "",
  price: "",
  image_url: "",
  stock: "",
  category_id: "",
};

function ProductCard({ product }) {
  return (
    <article className="product-card">
      <img src={product.image_url} alt={product.title} />
      <div className="product-card__body">
        <span className="badge">{product.category.name}</span>
        <h3>{product.title}</h3>
        <p>{product.short_description}</p>
        <div className="product-card__footer">
          <strong>${Number(product.price).toFixed(2)}</strong>
          <Link to={`/products/${product.id}`}>Details</Link>
        </div>
      </div>
    </article>
  );
}

function ProductForm({
  categories,
  form,
  formStatus,
  onChange,
  onSubmit,
}) {
  return (
    <form className="product-form" onSubmit={onSubmit}>
      <div className="section-title">
        <div>
          <p className="eyebrow">New product</p>
          <h2>Create product</h2>
        </div>
      </div>

      <div className="form-grid">
        <label>
          Title
          <input
            name="title"
            value={form.title}
            onChange={onChange}
            placeholder="Product title"
            required
          />
        </label>

        <label>
          Category
          <select
            name="category_id"
            value={form.category_id}
            onChange={onChange}
            required
          >
            <option value="">Select category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Price
          <input
            name="price"
            type="number"
            min="0.01"
            step="0.01"
            value={form.price}
            onChange={onChange}
            placeholder="49.99"
            required
          />
        </label>

        <label>
          Stock
          <input
            name="stock"
            type="number"
            min="0"
            value={form.stock}
            onChange={onChange}
            placeholder="12"
            required
          />
        </label>
      </div>

      <label>
        Short description
        <input
          name="short_description"
          value={form.short_description}
          onChange={onChange}
          placeholder="Short card text"
          required
        />
      </label>

      <label>
        Full description
        <textarea
          name="description"
          value={form.description}
          onChange={onChange}
          placeholder="Detailed product description"
          required
        />
      </label>

      <label>
        Image URL
        <input
          name="image_url"
          type="url"
          value={form.image_url}
          onChange={onChange}
          placeholder="https://example.com/image.jpg"
          required
        />
      </label>

      <div className="form-actions">
        <button type="submit" disabled={formStatus === "submitting"}>
          {formStatus === "submitting" ? "Creating..." : "Create product"}
        </button>
        {formStatus === "success" && (
          <span className="form-message">Product created.</span>
        )}
        {formStatus === "error" && (
          <span className="form-message form-message--error">
            Could not create product.
          </span>
        )}
      </div>
    </form>
  );
}

export default function App() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(initialProductForm);
  const [formStatus, setFormStatus] = useState("idle");
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    Promise.all([getProducts(), getCategories()])
      .then(([productsData, categoriesData]) => {
        setProducts(productsData);
        setCategories(categoriesData);
        setForm((currentForm) => ({
          ...currentForm,
          category_id: categoriesData[0]?.id ?? "",
        }));
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  function handleFormChange(event) {
    const { name, value } = event.target;

    setForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }));
  }

  async function handleFormSubmit(event) {
    event.preventDefault();
    setFormStatus("submitting");

    try {
      const product = await createProduct({
        ...form,
        price: Number(form.price),
        stock: Number(form.stock),
        category_id: Number(form.category_id),
      });

      setProducts((currentProducts) => [product, ...currentProducts]);
      setForm({
        ...initialProductForm,
        category_id: categories[0]?.id ?? "",
      });
      setFormStatus("success");
    } catch {
      setFormStatus("error");
    }
  }

  return (
    <main>
      <section className="hero">
        <div>
          <p className="eyebrow">Mini online store</p>
          <h1>Simple products for a better everyday setup</h1>
          <p>
            Browse a small catalog powered by FastAPI, React, and PostgreSQL.
            Open any product card to see more details.
          </p>
        </div>
      </section>

      <section className="create-product">
        <ProductForm
          categories={categories}
          form={form}
          formStatus={formStatus}
          onChange={handleFormChange}
          onSubmit={handleFormSubmit}
        />
      </section>

      <section className="catalog">
        <div className="section-title">
          <p className="eyebrow">Catalog</p>
          <h2>Popular products</h2>
        </div>

        {status === "loading" && <p className="state">Loading products...</p>}
        {status === "error" && (
          <p className="state state--error">
            Could not load products. Check that the backend is running.
          </p>
        )}

        {status === "ready" && (
          <div className="product-grid">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
