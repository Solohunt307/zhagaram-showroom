/* ================= PRODUCTS MODULE ================= */

console.log("Products.js loaded");

/* GLOBALS FROM dashboard.js */
const API = window.API;
const token = window.token;

if (!token) {
  alert("Session expired. Login again.");
  location.href = "login.html";
}

/* ================= DOM ================= */

const addProductBtn = document.getElementById("addProductBtn");
const searchBox = document.getElementById("searchBox");
const productTable = document.getElementById("productTable");
const pagination = document.getElementById("pagination");
const lowStockList = document.getElementById("lowStockList");

const fromDateInput = document.getElementById("fromDate");
const toDateInput = document.getElementById("toDate");

/* ================= FORM INPUTS ================= */

const product_name = document.getElementById("product_name");
const hsn = document.getElementById("hsn");
const model = document.getElementById("model");
const variant = document.getElementById("variant");
const color = document.getElementById("color");
const sale_price = document.getElementById("sale_price");
const stock_qty = document.getElementById("stock_qty");
const threshold = document.getElementById("threshold");
const description = document.getElementById("description");

/* ================= STATE ================= */

let editingId = null;
let currentPage = 1;
let currentProducts = [];

/* ================= ADD / UPDATE ================= */

async function addProduct() {

  const payload = {
    product_name: product_name.value.trim(),
    hsn: hsn.value.trim(),
    model: model.value.trim(),
    variant: variant.value.trim(),
    color: color.value.trim(),
    sale_price: Number(sale_price.value),
    stock_qty: Number(stock_qty.value),
    low_stock_threshold: Number(threshold.value),
    description: description.value.trim()
  };

  if (
    !payload.product_name ||
    !payload.hsn ||
    !payload.model ||
    !payload.variant ||
    !payload.color ||
    !payload.sale_price
  ) {
    alert("Fill mandatory fields");
    return;
  }

  const url = editingId
    ? `${API}/products/${editingId}`
    : `${API}/products`;

  const method = editingId ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    console.error(await res.text());
    alert("Failed to save product");
    return;
  }

  editingId = null;
  addProductBtn.innerText = "Add Product";

  clearForm();
  loadProducts(currentPage);
}

/* ================= LOAD ================= */

async function loadProducts(page = 1) {

  currentPage = page;

  const search = searchBox.value || "";

  let url = `${API}/products?page=${page}&search=${search}`;

  if (fromDateInput?.value)
    url += `&from_date=${fromDateInput.value}`;

  if (toDateInput?.value)
    url += `&to_date=${toDateInput.value}`;

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    console.error(await res.text());
    return;
  }

  const data = await res.json();

  currentProducts = data.items;

  renderTable(data.items);
  renderPagination(data.total);
  renderLowStock(data.items);
}

/* ================= RENDER TABLE ================= */

function renderTable(items) {

  productTable.innerHTML = "";

  items.forEach(p => {

    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${p.product_name}</td>
      <td>${p.hsn}</td>
      <td>${p.model}</td>
      <td>${p.variant}</td>
      <td>${p.color}</td>
      <td>${p.purchase_price ?? ""}</td>
      <td>${p.sale_price}</td>
      <td>${p.tax_rate ?? ""}</td>
      <td>${p.stock_qty}</td>
      <td>${p.low_stock_threshold}</td>
      <td>${p.description || ""}</td>
      <td>
        <button class="edit-btn" data-id="${p.id}">Edit</button>
        <button class="delete-btn" data-id="${p.id}">Delete</button>
      </td>
    `;

    productTable.appendChild(row);
  });

  document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.onclick = () => editProduct(Number(btn.dataset.id));
  });

  document.querySelectorAll(".delete-btn").forEach(btn => {
    btn.onclick = () => deleteProduct(Number(btn.dataset.id));
  });
}

/* ================= PAGINATION ================= */

function renderPagination(total) {

  const pages = Math.ceil(total / 10);

  pagination.innerHTML = "";

  for (let i = 1; i <= pages; i++) {

    const btn = document.createElement("button");

    btn.innerText = i;

    if (i === currentPage) btn.disabled = true;

    btn.onclick = () => loadProducts(i);

    pagination.appendChild(btn);
  }
}

/* ================= EDIT ================= */

function editProduct(id) {

  const p = currentProducts.find(x => x.id === id);

  if (!p) {
    alert("Product not found in current page");
    return;
  }

  product_name.value = p.product_name;
  hsn.value = p.hsn;
  model.value = p.model;
  variant.value = p.variant;
  color.value = p.color;
  sale_price.value = p.sale_price;
  stock_qty.value = p.stock_qty;
  threshold.value = p.low_stock_threshold;
  description.value = p.description || "";

  editingId = id;

  addProductBtn.innerText = "Update Product";
}

/* ================= DELETE ================= */

async function deleteProduct(id) {

  if (!confirm("Delete?")) return;

  const res = await fetch(`${API}/products/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    alert("Delete failed");
    return;
  }

  loadProducts(currentPage);
}

/* ================= EXPORT CSV ================= */

function exportCSV() {

  let csv = [
    [
      "Product Name",
      "HSN","Model","Variant","Color",
      "Purchase Price","Sale Price","Tax Rate",
      "Stock","Low Threshold","Description"
    ].join(",")
  ];

  document.querySelectorAll("#productTable tr").forEach(row => {

    const cols = [...row.children]
      .slice(0, 11)
      .map(td => `"${td.innerText}"`);

    csv.push(cols.join(","));
  });

  const blob = new Blob([csv.join("\n")], { type: "text/csv" });

  const a = document.createElement("a");

  a.href = URL.createObjectURL(blob);
  a.download = "products.csv";

  a.click();
}

/* ================= LOW STOCK ================= */

function renderLowStock(items) {

  lowStockList.innerHTML = "";

  items
    .filter(p => p.stock_qty <= p.low_stock_threshold)
    .forEach(p => {

      const li = document.createElement("li");

      li.innerText = `${p.product_name} - ${p.stock_qty}`;

      lowStockList.appendChild(li);
    });
}

/* ================= UTILS ================= */

function clearForm() {

  product_name.value = "";
  hsn.value = "";
  model.value = "";
  variant.value = "";
  color.value = "";
  sale_price.value = "";
  stock_qty.value = "";
  threshold.value = "";
  description.value = "";
}

/* ================= INIT ================= */

document.addEventListener("DOMContentLoaded", () => {

  addProductBtn.onclick = addProduct;

  searchBox.addEventListener("keyup", () => loadProducts(1));

  fromDateInput?.addEventListener("change", () => loadProducts(1));
  toDateInput?.addEventListener("change", () => loadProducts(1));

  loadProducts();
});

/* ================= EXPORTS ================= */

window.exportCSV = exportCSV;
