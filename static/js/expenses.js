const API = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");

if (!token) location.href = "login.html";

let currentPage = 1;


/* =============================
        MONTHLY
============================= */

async function saveMonthly() {

  const fields = [
    { id: "rent", label: "RENT" },
    { id: "salary", label: "SALARY" },
    { id: "eb", label: "EB" },
    { id: "office", label: "OFFICE" },
    { id: "misc", label: "MISC" },
  ];

  for (let f of fields) {

    const val = document.getElementById(f.id).value;

    if (!val) continue;

    await fetch(`${API}/expenses`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        category: f.label,
        description: "Monthly Expense",
        amount: Number(val),
        expense_date: new Date().toISOString().slice(0, 10)
      })
    });

  }

  alert("Monthly expenses saved!");

  loadExpenses();
}


/* =============================
        DAILY
============================= */

function addDailyRow() {

  const tr = document.createElement("tr");

  tr.innerHTML = `
    <td><input class="desc"></td>
    <td><input type="date" class="date"></td>
    <td><input class="doneby"></td>
    <td><input type="number" class="amt"></td>
    <td><button onclick="this.closest('tr').remove()">❌</button></td>
  `;

  document.getElementById("dailyBody").appendChild(tr);
}

addDailyRow();


async function submitDaily() {

  const rows = document.querySelectorAll("#dailyBody tr");

  const items = [];

  rows.forEach(r => {

    const desc = r.querySelector(".desc").value;
    const date = r.querySelector(".date").value;
    const amt = r.querySelector(".amt").value;

    if (!desc || !date || !amt) return;

    items.push({
      category: "DAILY",
      description: desc,
      expense_date: date,
      amount: Number(amt),
    });
  });

  if (!items.length) {
    alert("No valid rows!");
    return;
  }

  await fetch(`${API}/expenses/bulk`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ items })
  });

  alert("Daily expenses saved!");

  document.getElementById("dailyBody").innerHTML = "";
  addDailyRow();

  loadExpenses();
}


/* =============================
        LIST
============================= */

async function loadExpenses(page = 1) {

  currentPage = page;

  const search = document.getElementById("searchBox").value;
  const from = document.getElementById("fromDate").value;
  const to = document.getElementById("toDate").value;

  let url = `${API}/expenses?page=${page}`;

  if (search) url += `&search=${search}`;
  if (from) url += `&from_date=${from}`;
  if (to) url += `&to_date=${to}`;

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();

  renderTable(data.items || []);
  renderPagination(data.total || 0);
}


/* =============================
        TABLE
============================= */

function renderTable(items) {

  const tbody = document.getElementById("expenseTable");

  tbody.innerHTML = "";

  items.forEach(e => {

    tbody.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${e.category}</td>
        <td>${e.description || ""}</td>
        <td>₹ ${e.amount}</td>
        <td>${e.expense_date}</td>
        <td>
          <button onclick="editExpense(${e.id}, '${e.category}')">Edit</button>
          <button onclick="deleteExpense(${e.id})">Delete</button>
        </td>
      </tr>
    `);
  });
}


/* =============================
        PAGINATION
============================= */

function renderPagination(total) {

  const pages = Math.ceil(total / 10);

  const box = document.getElementById("pagination");

  box.innerHTML = "";

  for (let i = 1; i <= pages; i++) {

    const btn = document.createElement("button");

    btn.innerText = i;

    if (i === currentPage) btn.disabled = true;

    btn.onclick = () => loadExpenses(i);

    box.appendChild(btn);
  }
}


/* =============================
        DELETE
============================= */


async function deleteExpense(id) {

  if (!confirm("Delete this expense?")) return;

  await fetch(`${API}/expenses/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  loadExpenses(currentPage);
}


/* =============================
        EDIT
============================= */

async function editExpense(id, category) {

  const newDesc = prompt("New description:");
  const newAmt = prompt("New amount:");

  if (!newDesc || !newAmt) return;

  await fetch(`${API}/expenses/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      category: category,
      description: newDesc,
      amount: Number(newAmt),
      expense_date: new Date().toISOString().slice(0, 10)
    })
  });

  loadExpenses(currentPage);
}


/* =============================
        EXPORT (AUTH SAFE)
============================= */

async function exportCSV() {

  const res = await fetch(`${API}/expenses/export/csv`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  const blob = await res.blob();

  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");

  a.href = url;
  a.download = "expenses.csv";

  document.body.appendChild(a);
  a.click();

  a.remove();
}


/* =============================
        INIT
============================= */

loadExpenses();
