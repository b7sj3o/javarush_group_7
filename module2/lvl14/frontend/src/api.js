const API_URL = import.meta.env.VITE_API_URL;

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, options);

  if (!response.ok) {
    throw new Error("Unable to load shop data");
  }

  return response.json();
}

export function getProducts() {
  return request("/api/products");
}

export function getProduct(id) {
  return request(`/api/products/${id}`);
}

export function getCategories() {
  return request("/api/categories");
}

export function createProduct(product) {
  return request("/api/products", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(product),
  });
}
