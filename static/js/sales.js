console.log("Sales JS Loaded");

/* ================= GLOBAL ================= */

const API = window.API;
const token = localStorage.getItem("access_token");

if (!token) location.href = "login.html";

const PAGE_SIZE = 10;

/* ================= DOM ================= */

const salesTable = document.getElementById("salesTable");
const salesPagination = document.getElementById("salesPagination");

const saleSearch = document.getElementById("saleSearch");
const fromDate = document.getElementById("fromDate");
const toDate = document.getElementById("toDate");

document.getElementById("applyFilterBtn").onclick = () => loadSales(1);
document.getElementById("exportCSVBtn").onclick = exportCSV;

/* ---- FORM ---- */

const saleForm = document.getElementById("saleForm");

const customerName = document.getElementById("customerName");
const phone = document.getElementById("phone");
const address = document.getElementById("address");

const productSelect = document.getElementById("productSelect");
const priceInput = document.getElementById("price");

const qtyInput = document.getElementById("qty");
const orderAmount = document.getElementById("orderAmount");
const paidAmount = document.getElementById("paidAmount");
const balanceAmount = document.getElementById("balanceAmount");

const paymentType = document.getElementById("paymentType");
const saleDate = document.getElementById("saleDate");
const receivedBy = document.getElementById("receivedBy");
const notes = document.getElementById("notes");

const modal = document.getElementById("saleModal");

/* ================= STATE ================= */

let salePage = 1;
let editingSaleId = null;

/* =====================================================
                    LOAD PRODUCTS
===================================================== */

async function loadProducts() {

  productSelect.innerHTML = `<option value="">-- Select Product --</option>`;

  const res = await fetch(`${API}/products?page=1`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();

  (data.items || []).forEach(p => {

    const opt = document.createElement("option");
    opt.value = p.id;
    opt.innerText = p.product_name;

    productSelect.appendChild(opt);
  });
}

/* =====================================================
                    SALES LIST
===================================================== */

async function loadSales(page = 1) {

  salePage = page;

  let url = `${API}/sales/?page=${page}`;

  if (saleSearch.value)
    url += `&search=${saleSearch.value}`;

  if (fromDate.value)
    url += `&from_date=${fromDate.value}`;

  if (toDate.value)
    url += `&to_date=${toDate.value}`;

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();

  renderSalesTable(data.items || []);
  renderSalesPagination(data.total || 0);
}

function renderSalesTable(items) {

  salesTable.innerHTML = "";

  items.forEach(s => {

    const cancelledClass =
      s.status === "CANCELLED" ? "cancelled-row" : "";

    salesTable.insertAdjacentHTML("beforeend", `
      <tr class="${cancelledClass}">
        <td>${s.invoice_number}</td>
        <td>${s.customer_name}</td>
        <td>${s.product_name}</td>
        <td>${s.quantity}</td>
        <td>${s.order_amount}</td>
        <td>${s.paid_amount}</td>
        <td>${s.balance_amount}</td>
        <td>${s.sale_date}</td>
        <td>
          <button onclick="editSale(${s.id})">Edit</button>
          <button onclick="cancelSale(${s.id})">Cancel</button>
          <button onclick="viewInvoice(${s.id})">Invoice</button>
        </td>
      </tr>
    `);
  });
}

function renderSalesPagination(total) {

  const pages = Math.ceil(total / PAGE_SIZE);

  salesPagination.innerHTML = "";

  for (let i = 1; i <= pages; i++) {

    const btn = document.createElement("button");

    btn.innerText = i;

    if (i === salePage) btn.disabled = true;

    btn.onclick = () => loadSales(i);

    salesPagination.appendChild(btn);
  }
}

/* =====================================================
                    CREATE / EDIT
===================================================== */

saleForm.onsubmit = async e => {

  e.preventDefault();

  const fd = new FormData();

  fd.append("customer_name", customerName.value);
  fd.append("phone", phone.value);
  fd.append("address", address.value);

  fd.append("product_id", productSelect.value);
  fd.append("quantity", qtyInput.value);

  fd.append("order_amount", orderAmount.value);
  fd.append("paid_amount", paidAmount.value);

  fd.append("payment_type", paymentType.value);
  fd.append("sale_date", saleDate.value);

  fd.append("received_by", receivedBy.value);
  fd.append("notes", notes.value);

  const url = editingSaleId
    ? `${API}/sales/${editingSaleId}`
    : `${API}/sales/`;

  const method = editingSaleId ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: { Authorization: `Bearer ${token}` },
    body: fd
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.detail || "Save failed");
    return;
  }

  alert("Saved successfully");

  hideSaleForm();
  loadSales(salePage);
};

/* =====================================================
                    CSV EXPORT
===================================================== */

function exportCSV() {

  const token = localStorage.getItem("access_token");

  if (!token) {
    alert("Login expired");
    location.href = "login.html";
    return;
  }

  window.open(`${API}/sales/export/csv?token=${token}`, "_blank");
}

/* =====================================================
                    CANCEL
===================================================== */

async function cancelSale(id) {

  if (!confirm("Cancel this sale?")) return;

  const res = await fetch(`${API}/sales/${id}/cancel`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    alert("Cancel failed");
    return;
  }

  alert("Cancelled successfully");

  loadSales(salePage);
}

/* =====================================================
                    INVOICE
===================================================== */

async function viewInvoice(id) {

  const res = await fetch(`${API}/sales/${id}/invoice`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);

  window.open(url, "_blank");
}

/* =====================================================
                    EDIT
===================================================== */

window.editSale = async id => {

  editingSaleId = id;

  const res = await fetch(`${API}/sales/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const sale = await res.json();

  showSaleForm();

  customerName.value = sale.customer.name || "";
  phone.value = sale.customer.phone || "";
  address.value = sale.customer.address || "";

  productSelect.value = sale.product_id;

  qtyInput.value = sale.quantity;
  orderAmount.value = sale.order_amount;
  paidAmount.value = sale.paid_amount;
  balanceAmount.value = sale.balance_amount;

  saleDate.value = sale.sale_date;
  paymentType.value = sale.payment_type;

  receivedBy.value = sale.received_by || "";
  notes.value = sale.notes || "";

  document.getElementById("saleFormTitle").innerText = "Edit Sale";
};

/* =====================================================
                    MODAL CONTROL
===================================================== */

window.showSaleForm = () => {
  modal.style.display = "block";
  saleForm.reset();
  editingSaleId = null;
};

window.hideSaleForm = () => {
  modal.style.display = "none";
};

/* =====================================================
                    INIT
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

  loadProducts();
  loadSales();

});