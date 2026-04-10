const API = window.API;
const token = window.token;

const dashDate = document.getElementById("dashDate");

dashDate.valueAsDate = new Date();

async function loadDaily() {

  const date = dashDate.value;

  const res = await fetch(
    `${API}/sales/dashboard/daily?date=${date}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  const data = await res.json();

  document.getElementById("totalSales").innerText = data.total_sales;
  document.getElementById("totalPaid").innerText = data.total_paid;
  document.getElementById("totalBalance").innerText = data.total_balance;
  document.getElementById("totalInvoices").innerText = data.invoices;

  loadTopProducts();
}


async function loadTopProducts() {

  const from = dashDate.value;
  const to = dashDate.value;

  const res = await fetch(
    `${API}/sales/dashboard/range?from_date=${from}&to_date=${to}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  const rows = await res.json();

  const tbody = document.getElementById("topProducts");

  tbody.innerHTML = "";

  rows.forEach(r => {

    tbody.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${r.product}</td>
        <td>${r.qty}</td>
        <td>${r.amount}</td>
      </tr>
    `);

  });

}

document.addEventListener("DOMContentLoaded", loadDaily);
