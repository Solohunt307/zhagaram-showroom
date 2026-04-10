const API = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");

if (!token) location.href = "login.html";

let currentPage = 1;
let editingCustomerId = null;

/* ================= DOM ================= */

const custName = document.getElementById("custName");
const custPhone = document.getElementById("custPhone");
const custEmail = document.getElementById("custEmail");
const custAddr = document.getElementById("custAddr");

const searchBox = document.getElementById("searchBox");
const fromDate = document.getElementById("fromDate");
const toDate = document.getElementById("toDate");

const table = document.getElementById("customerTable");
const paginationDiv = document.getElementById("pagination");

const formTitle = document.getElementById("formTitle");
const submitBtn = document.getElementById("submitCustomerBtn");
const cancelBtn = document.getElementById("cancelEditBtn");

/* ================= LOAD ================= */

async function loadCustomers(page = 1) {

  currentPage = page;

  let url =
    `${API}/customers?page=${page}`;

  if (searchBox.value)
    url += `&search=${searchBox.value}`;

  if (fromDate.value)
    url += `&from_date=${fromDate.value}`;

  if (toDate.value)
    url += `&to_date=${toDate.value}`;

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();

  renderCustomers(data.items || []);
  renderPagination(data.total || 0);
}

/* ================= TABLE ================= */

function renderCustomers(items) {

  table.innerHTML = "";

  items.forEach(c => {

    table.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${c.name}</td>
        <td>${c.phone}</td>
        <td>${c.email || ""}</td>
        <td>${c.address}</td>
        <td>
          <button onclick="editCustomer(${c.id})">Edit</button>
          <button onclick="deleteCustomer(${c.id})">Delete</button>
        </td>
      </tr>
    `);

  });
}

/* ================= PAGINATION ================= */

function renderPagination(total) {

  const pages = Math.ceil(total / 10);

  paginationDiv.innerHTML = "";

  for (let i = 1; i <= pages; i++) {

    const btn = document.createElement("button");

    btn.innerText = i;

    if (i === currentPage) btn.disabled = true;

    btn.onclick = () => loadCustomers(i);

    paginationDiv.appendChild(btn);
  }
}

/* ================= ADD / UPDATE ================= */

async function saveCustomer() {

  if (!custName.value || !custPhone.value || !custAddr.value) {
    alert("Name, Phone & Address required");
    return;
  }

  const payload = {
    name: custName.value,
    phone: custPhone.value,
    email: custEmail.value,
    address: custAddr.value,
  };

  const url = editingCustomerId
    ? `${API}/customers/${editingCustomerId}`
    : `${API}/customers`;

  const method = editingCustomerId ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    alert("Save failed");
    return;
  }

  resetForm();
  loadCustomers(currentPage);
}

/* ================= EDIT ================= */

window.editCustomer = async id => {

  const res = await fetch(`${API}/customers?page=1&search=`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();

  const cust = data.items.find(x => x.id === id);

  if (!cust) return;

  editingCustomerId = id;

  custName.value = cust.name;
  custPhone.value = cust.phone;
  custEmail.value = cust.email || "";
  custAddr.value = cust.address;

  formTitle.innerText = "Edit Customer";
  submitBtn.innerText = "Update Customer";
  cancelBtn.style.display = "inline-block";
};

/* ================= DELETE ================= */

async function deleteCustomer(id) {

  if (!confirm("Are you sure you want to delete this customer?")) return;

  await fetch(`${API}/customers/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  loadCustomers(currentPage);
}

/* ================= CSV ================= */

async function exportCustomersCSV() {

  const res = await fetch(`${API}/customers/export/csv`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (!res.ok) {
    const err = await res.text();
    alert("Export failed: " + err);
    return;
  }

  const blob = await res.blob();

  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "customers.csv";
  document.body.appendChild(a);
  a.click();

  a.remove();
  window.URL.revokeObjectURL(url);
}


/* ================= RESET ================= */

function resetForm() {

  editingCustomerId = null;

  custName.value = "";
  custPhone.value = "";
  custEmail.value = "";
  custAddr.value = "";

  formTitle.innerText = "Add New Customer";
  submitBtn.innerText = "Add Customer";
  cancelBtn.style.display = "none";
}

/* ================= INIT ================= */

document.addEventListener("DOMContentLoaded", () => {

  loadCustomers();

});
