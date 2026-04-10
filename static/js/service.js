console.log("Service JS Loaded");

/* ================= GLOBAL ================= */

const API = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");

if (!token) location.href = "login.html";

let currentPage = 1;
const PAGE_SIZE = 10;

const params = new URLSearchParams(window.location.search);
const editId = params.get("id");

/* ================= LIST ================= */

async function loadTickets(page = 1) {

  currentPage = page;

  let url = `${API}/service/?page=${page}`;

  const search = document.getElementById("searchBox")?.value;
  const from = document.getElementById("fromDate")?.value;
  const to = document.getElementById("toDate")?.value;

  if (search) url += `&search=${encodeURIComponent(search)}`;
  if (from) url += `&from_date=${from}`;
  if (to) url += `&to_date=${to}`;

  try {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!res.ok) throw new Error("Load failed");

    const data = await res.json();

    renderTable(data.items || []);
    renderPagination(data.total || 0);

  } catch (err) {
    alert(err.message);
  }
}

/* ================= TABLE ================= */

function safe(val) {
  return val ?? "";
}

function renderTable(items) {

  const table = document.getElementById("ticketTable");
  table.innerHTML = "";

  items.forEach(t => {

    table.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${safe(t.ticket_code)}</td>
        <td>${safe(t.customer_name)}</td>
        <td>${safe(t.product_name)}</td>
        <td>${safe(t.product_description)}</td>
        <td>${safe(t.complaint)}</td>
        <td>${safe(t.mobile)}</td>
        <td>${safe(t.technician)}</td>
        <td>${safe(t.resolved_complaint)}</td>
        <td>${safe(t.unresolved_complaint)}</td>
        <td>${safe(t.bill_no)}</td>
        <td>${safe(t.received_by)}</td>
        <td>${safe(t.service_completed_date)}</td>
        <td>${safe(t.service_cost)}</td>
        <td>${safe(t.amount_paid)}</td>
        <td>${safe(t.balance)}</td>
        <td>${safe(t.payment_mode)}</td>
        <td class="${safe(t.status)}">${safe(t.status)}</td>
        <td>${t.created_at ? t.created_at.split("T")[0] : ""}</td>
        <td>${safe(t.closed_at)}</td>
        <td>
          <button onclick="viewTicket(${t.id})">View</button>
          <button onclick="editTicket(${t.id})">Edit</button>
          <button onclick="deleteTicket(${t.id})">Delete</button>
        </td>
      </tr>
    `);
  });
}

/* ================= PAGINATION ================= */

function renderPagination(total) {

  const pages = Math.ceil(total / PAGE_SIZE);
  const div = document.getElementById("pagination");

  div.innerHTML = "";

  for (let i = 1; i <= pages; i++) {

    const btn = document.createElement("button");

    btn.innerText = i;

    if (i === currentPage) btn.disabled = true;

    btn.onclick = () => loadTickets(i);

    div.appendChild(btn);
  }
}

/* ================= VIEW ================= */

function viewTicket(id) {
  location.href = `service_view.html?id=${id}`;   // ✅ FIXED
}

async function loadView() {

  const id = new URLSearchParams(window.location.search).get("id");

  if (!id) return;

  try {
    const res = await fetch(`${API}/service/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!res.ok) throw new Error("Failed to load ticket");

    const t = await res.json();

    const box = document.getElementById("viewBox");
    if (!box) return;

    box.innerHTML = `
      <p><b>Ticket:</b> ${safe(t.ticket_code)}</p>
      <p><b>Customer:</b> ${safe(t.customer_name)}</p>
      <p><b>Product:</b> ${safe(t.product_name)}</p>
      <p><b>Description:</b> ${safe(t.product_description)}</p>
      <p><b>Complaint:</b> ${safe(t.complaint)}</p>
      <p><b>Technician:</b> ${safe(t.technician)}</p>
      <p><b>Status:</b> ${safe(t.status)}</p>
      <p><b>Cost:</b> ${safe(t.service_cost)}</p>
      <p><b>Paid:</b> ${safe(t.amount_paid)}</p>
      <p><b>Balance:</b> ${safe(t.balance)}</p>
    `;

  } catch (err) {
    alert(err.message);
  }
}

/* ================= DELETE ================= */

async function deleteTicket(id) {

  if (!confirm("Delete ticket?")) return;

  try {
    const res = await fetch(`${API}/service/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!res.ok) throw new Error("Delete failed");

    loadTickets(currentPage);

  } catch (err) {
    alert(err.message);
  }
}

/* ================= CREATE / EDIT ================= */

const form = document.getElementById("ticketForm");

if (form) {

  if (editId) loadForEdit(editId);

  form.addEventListener("submit", async e => {

    e.preventDefault();

    const fd = new FormData(form);

    ["service_cost", "amount_paid", "balance"].forEach(k => {
      if (!fd.get(k)) fd.delete(k);
    });

    const url = editId
      ? `${API}/service/${editId}`
      : `${API}/service/`;

    const method = editId ? "PUT" : "POST";

    try {
      const res = await fetch(url, {
        method,
        headers: { Authorization: `Bearer ${token}` },
        body: fd
      });

      if (!res.ok) throw new Error(await res.text());

      alert("Saved successfully");
      location.href = "service.html";

    } catch (err) {
      alert(err.message);
    }
  });
}

/* ================= PREFILL ================= */

async function loadForEdit(id) {

  const res = await fetch(`${API}/service/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const t = await res.json();

  for (let k in t) {
    const el = document.querySelector(`[name="${k}"]`);
    if (el) el.value = t[k] || "";
  }
}

/* ================= AUTO BALANCE ================= */

const serviceCost = document.getElementById("serviceCost");
const amountPaid = document.getElementById("amountPaid");
const balance = document.getElementById("balance");

function calcBalance() {

  const cost = Number(serviceCost?.value || 0);
  const paid = Number(amountPaid?.value || 0);

  if (balance) balance.value = cost - paid;
}

serviceCost?.addEventListener("input", calcBalance);
amountPaid?.addEventListener("input", calcBalance);

/* ================= REDIRECT ================= */

function editTicket(id) {
  location.href = `service_new.html?id=${id}`;
}

/* ================= INIT ================= */

document.addEventListener("DOMContentLoaded", () => {

  if (document.getElementById("ticketTable")) {
    loadTickets();
  }

  if (document.getElementById("viewBox")) {
    loadView();   // ✅ FIXED (was missing)
  }

});