console.log("Purchases JS Loaded");

/* ================= GLOBAL ================= */

const API = window.API;
const token = window.token;

if (!token) location.href = "login.html";

const PAGE_SIZE = 10;

/* ================= STATE ================= */

let editingVendorId = null;
let editingPurchaseId = null;

let vendorPage = 1;
let purchasePage = 1;

let currentPurchases = [];

/* =====================================================
                    DOM READY
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

  window.vendorTable = document.getElementById("vendorTable");
  window.vendorPagination = document.getElementById("vendorPagination");

  window.vendorName = document.getElementById("vendorName");
  window.vendorMobile = document.getElementById("vendorMobile");
  window.vendorEmail = document.getElementById("vendorEmail");
  window.vendorGST = document.getElementById("vendorGST");
  window.vendorLocation = document.getElementById("vendorLocation");
  window.vendorBtn = document.getElementById("vendorBtn");

  window.productSelect = document.getElementById("productSelect");
  window.vendorSelect = document.getElementById("vendorSelect");

  window.purchaseForm = document.getElementById("purchaseForm");
  window.purchaseTable = document.getElementById("purchaseTable");
  window.purchasePagination = document.getElementById("purchasePagination");

  window.purchaseSearch = document.getElementById("purchaseSearch");
  window.fromDate = document.getElementById("fromDate");
  window.toDate = document.getElementById("toDate");

  document.getElementById("applyFilterBtn")?.addEventListener("click", () => {
    loadPurchases(1);
  });

  document.getElementById("exportCSVBtn")?.addEventListener("click", exportPurchasesCSV);

  vendorBtn.addEventListener("click", saveVendor);

  purchaseForm.addEventListener("submit", submitPurchase);

  loadVendors();
  loadProducts();
  loadPurchases();
});

/* =====================================================
                    VENDORS
===================================================== */

async function loadVendors(page = 1) {

  vendorPage = page;

  const res = await fetch(
    `${API}/purchases/vendors?page=${page}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const data = await res.json();

  renderVendorTable(data.items || []);
  renderVendorPagination(data.total || 0);
  populateVendorDropdown(data.items || []);
}

/* ---------- Vendor Table ---------- */

function renderVendorTable(vendors) {

  vendorTable.innerHTML = "";

  vendors.forEach(v => {

    vendorTable.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${v.name}</td>
        <td>${v.mobile}</td>
        <td>${v.email || ""}</td>
        <td>${v.gst_no || ""}</td>
        <td>${v.location}</td>
        <td>
          <button onclick="editVendor(${v.id})">Edit</button>
          <button onclick="deleteVendor(${v.id})">Delete</button>
        </td>
      </tr>
    `);
  });
}

/* ---------- Vendor Pagination ---------- */

function renderVendorPagination(total) {

  vendorPagination.innerHTML = "";

  const pages = Math.ceil(total / PAGE_SIZE);

  for (let i = 1; i <= pages; i++) {

    const btn = document.createElement("button");
    btn.innerText = i;

    if (i === vendorPage) btn.disabled = true;

    btn.onclick = () => loadVendors(i);

    vendorPagination.appendChild(btn);
  }
}

/* ---------- Save Vendor ---------- */

async function saveVendor() {

  const payload = {
    name: vendorName.value.trim(),
    mobile: vendorMobile.value.trim(),
    email: vendorEmail.value.trim(),
    gst_no: vendorGST.value.trim(),
    location: vendorLocation.value.trim()
  };

  if (!payload.name || !payload.mobile || !payload.location) {
    alert("Fill mandatory vendor fields");
    return;
  }

  const url = editingVendorId
    ? `${API}/purchases/vendors/${editingVendorId}`
    : `${API}/purchases/vendors`;

  const method = editingVendorId ? "PUT" : "POST";

  await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  clearVendorForm();
  loadVendors(vendorPage);
}

window.editVendor = id => {

  const row = [...vendorTable.children]
    .find(tr => tr.innerHTML.includes(`editVendor(${id})`));

  vendorName.value = row.children[0].innerText;
  vendorMobile.value = row.children[1].innerText;
  vendorEmail.value = row.children[2].innerText;
  vendorGST.value = row.children[3].innerText;
  vendorLocation.value = row.children[4].innerText;

  editingVendorId = id;
  vendorBtn.innerText = "Update Vendor";
};

async function deleteVendor(id) {

  if (!confirm("Delete vendor?")) return;

  await fetch(`${API}/purchases/vendors/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  loadVendors(vendorPage);
}

function clearVendorForm() {

  vendorName.value = "";
  vendorMobile.value = "";
  vendorEmail.value = "";
  vendorGST.value = "";
  vendorLocation.value = "";

  editingVendorId = null;
  vendorBtn.innerText = "Add Vendor";
}

/* =====================================================
                    PRODUCTS
===================================================== */

async function loadProducts() {

  const res = await fetch(`${API}/products?page=1`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();

  productSelect.innerHTML = `<option value="">-- Select Product --</option>`;

  data.items.forEach(p => {

    const opt = document.createElement("option");
    opt.value = p.id;
    opt.innerText = p.product_name;

    productSelect.appendChild(opt);
  });
}

/* =====================================================
                    PURCHASES
===================================================== */

async function submitPurchase(e) {

  e.preventDefault();

  const fd = new FormData(purchaseForm);

  const url = editingPurchaseId
    ? `${API}/purchases/${editingPurchaseId}`
    : `${API}/purchases`;

  const method = editingPurchaseId ? "PUT" : "POST";

  await fetch(url, {
    method,
    headers: { Authorization: `Bearer ${token}` },
    body: fd
  });

  editingPurchaseId = null;
  purchaseForm.reset();

  loadPurchases(purchasePage);
}

/* ---------- Load Purchases ---------- */

async function loadPurchases(page = 1) {

  purchasePage = page;

  let url = `${API}/purchases?page=${page}`;

  if (purchaseSearch?.value)
    url += `&search=${purchaseSearch.value}`;

  if (fromDate?.value)
    url += `&from_date=${fromDate.value}`;

  if (toDate?.value)
    url += `&to_date=${toDate.value}`;

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();

  currentPurchases = data.items || [];

  renderPurchaseTable(currentPurchases);
  renderPurchasePagination(data.total || 0);
}

/* ---------- Purchase Table ---------- */

function renderPurchaseTable(items) {

  purchaseTable.innerHTML = "";

  items.forEach(p => {

    purchaseTable.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${p.product_name}</td>
        <td>${p.vendor_name}</td>
        <td>${p.quantity}</td>
        <td>${p.amount}</td>
        <td>${p.purchase_date}</td>
        <td>
          <button onclick="editPurchase(${p.id})">Edit</button>
          <button onclick="deletePurchase(${p.id})">Delete</button>
        </td>
      </tr>
    `);
  });
}

/* ---------- Purchase Pagination ---------- */

function renderPurchasePagination(total) {

  purchasePagination.innerHTML = "";

  const pages = Math.ceil(total / PAGE_SIZE);

  for (let i = 1; i <= pages; i++) {

    const btn = document.createElement("button");
    btn.innerText = i;

    if (i === purchasePage) btn.disabled = true;

    btn.onclick = () => loadPurchases(i);

    purchasePagination.appendChild(btn);
  }
}

/* ---------- Edit Purchase ---------- */

window.editPurchase = id => {

  const p = currentPurchases.find(x => x.id === id);
  if (!p) return;

  productSelect.value = p.product_id;
  vendorSelect.value = p.vendor_id;
  qty.value = p.quantity;
  amount.value = p.amount;
  paymentMode.value = p.payment_mode;
  pdate.value = p.purchase_date;

  editingPurchaseId = id;

  window.scrollTo({ top: 0, behavior: "smooth" });
};

/* ---------- Delete Purchase ---------- */

async function deletePurchase(id) {

  if (!confirm("Delete purchase?")) return;

  await fetch(`${API}/purchases/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  loadPurchases(purchasePage);
}

/* ---------- CSV EXPORT ---------- */

function exportPurchasesCSV() {

  let csv = ["Product,Vendor,Qty,Amount,Date"];

  currentPurchases.forEach(p => {
    csv.push(
      `"${p.product_name}","${p.vendor_name}",${p.quantity},${p.amount},"${p.purchase_date}"`
    );
  });

  const blob = new Blob([csv.join("\n")], { type: "text/csv" });

  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "purchases.csv";
  a.click();
}

function populateVendorDropdown(vendors) {

  vendorSelect.innerHTML =
    `<option value="">-- Select Vendor --</option>`;

  vendors.forEach(v => {

    const opt = document.createElement("option");
    opt.value = v.id;
    opt.innerText = v.name;

    vendorSelect.appendChild(opt);
  });
}

