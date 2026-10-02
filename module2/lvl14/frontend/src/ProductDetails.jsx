import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getProduct } from "./api.js";

export default function ProductDetails() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    getProduct(id)
      .then((data) => {
        setProduct(data);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, [id]);

  if (status === "loading") {
    return <p className="state">Loading product...</p>;
  }

  if (status === "error") {
    return (
      <main className="details-page">
        <Link className="back-link" to="/">
          Back to catalog
        </Link>
        <p className="state state--error">Product was not found.</p>
      </main>
    );
  }

  return (
    <main className="details-page">
      <Link className="back-link" to="/">
        Back to catalog
      </Link>

      <article className="details-card">
        <img src={product.image_url} alt={product.title} />
        <div className="details-card__content">
          <span className="badge">{product.category.name}</span>
          <h1>{product.title}</h1>
          <p>{product.description}</p>

          <div className="details-meta">
            <div>
              <span>Price</span>
              <strong>${Number(product.price).toFixed(2)}</strong>
            </div>
            <div>
              <span>In stock</span>
              <strong>{product.stock} pcs</strong>
            </div>
          </div>

          <button type="button">Add to cart</button>
        </div>
      </article>
    </main>
  );
}
