const API = "https://zhagaram-api.onrender.com";
const token = localStorage.getItem("access_token");

if (!token) location.href = "login.html";

let currentPage = 1;
const PAGE_SIZE = 10;

/* ================= INVOICES ================= */

async function loadInvoices(page = 1) {

  currentPage = page;

  const from = document.getElementById("fromDate").value;
  const to = document.getElementById("toDate").value;
  const invFrom = document.getElementById("invFrom").value;
  const invTo = document.getElementById("invTo").value;

  let url = `${API}/accounting/invoices?page=${page}`;

  if (from) url += `&from_date=${from}`;
  if (to) url += `&to_date=${to}`;
  if (invFrom) url += `&invoice_from=${invFrom}`;
  if (invTo) url += `&invoice_to=${invTo}`;

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    alert("Failed to load invoices");
    console.error(await res.text());
    return;
  }

  const data = await res.json();

  renderInvoices(data.items || []);
  renderPagination(data.total || 0);
}

function renderInvoices(items) {

  const tbody = document.getElementById("invoiceTable");
  tbody.innerHTML = "";

  items.forEach(i => {

    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${i.invoice_no}</td>
      <td>${i.sale_date}</td>
      <td>₹ ${i.order_amount}</td>
    `;

    tbody.appendChild(tr);
  });
}

/* ================= SUMMARY ================= */

async function loadSummary() {

  const from = document.getElementById("fromDate").value;
  const to = document.getElementById("toDate").value;

  let url = `${API}/accounting/summary`;

  const params = [];

  if (from) params.push(`from_date=${from}`);
  if (to) params.push(`to_date=${to}`);

  if (params.length) url += "?" + params.join("&");

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    alert("Summary failed");
    console.error(await res.text());
    return;
  }

  const d = await res.json();

  document.getElementById("summaryBox").innerHTML = `
    <p>Sales Count: ${d.sales_count}</p>
    <p>Purchase Count: ${d.purchase_count}</p>
    <p>Total Sales: ₹ ${d.total_sales}</p>
    <p>Total Purchase: ₹ ${d.total_purchase}</p>
    <p>Total Expense: ₹ ${d.total_expense}</p>
    <h3>Net Profit: ₹ ${d.net_profit}</h3>
  `;
}

/* ================= EXPORT PDF ================= */

async function exportPDF() {

  const token = localStorage.getItem("access_token");

  const from = document.getElementById("fromDate").value;
  const to = document.getElementById("toDate").value;

  let url = `${API}/accounting/export/pdf`;

  const params = [];

  if (from) params.push(`from_date=${from}`);
  if (to) params.push(`to_date=${to}`);

  if (params.length) url += "?" + params.join("&");

  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (!res.ok) {
    alert("Export failed");
    console.error(await res.text());
    return;
  }

  const blob = await res.blob();

  const link = document.createElement("a");
  link.href = window.URL.createObjectURL(blob);
  link.download = "invoices.pdf";

  document.body.appendChild(link);
  link.click();
  link.remove();
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

    btn.onclick = () => loadInvoices(i);

    div.appendChild(btn);
  }
}

/* ================= INIT ================= */

document.addEventListener("DOMContentLoaded", () => {

  loadInvoices();

});
