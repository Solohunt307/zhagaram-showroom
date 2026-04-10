console.log("Sale Details Loaded");

/* GLOBAL */
const API = window.API;
const token = window.token;

if (!token) location.href = "login.html";

/* GET SALE ID */
const params = new URLSearchParams(location.search);
const saleId = params.get("sale_id");

const saleSummary = document.getElementById("saleSummary");
const paymentTable = document.getElementById("paymentTable");
const paymentForm = document.getElementById("paymentForm");

const payAmount = document.getElementById("payAmount");
const payType = document.getElementById("payType");
const receivedBy = document.getElementById("receivedBy");

/* ================= LOAD DETAILS ================= */

async function loadSaleDetails() {

  const res = await fetch(
    `${API}/sales/${saleId}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  const data = await res.json();

  renderSummary(data);
  loadPayments();
}

/* ================= SUMMARY ================= */

function renderSummary(s) {

  saleSummary.innerHTML = `
    <b>Invoice:</b> ${s.invoice_number}<br>
    <b>Customer:</b> ${s.customer_name}<br>
    <b>Product:</b> ${s.product_name}<br>
    <b>Qty:</b> ${s.quantity}<br>
    <b>Total:</b> ₹${s.order_amount}<br>
    <b>Paid:</b> ₹${s.paid_amount}<br>
    <b>Balance:</b> ₹${s.balance_amount}
  `;
}

/* ================= PAYMENTS ================= */

async function loadPayments() {

  const res = await fetch(
    `${API}/sales/${saleId}/payments`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  const data = await res.json();

  renderPayments(data);
}

function renderPayments(items) {

  paymentTable.innerHTML = "";

  items.forEach(p => {

    paymentTable.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${p.paid_at}</td>
        <td>${p.payment_type}</td>
        <td>${p.amount}</td>
        <td>${p.received_by}</td>
      </tr>
    `);
  });
}

/* ================= ADD PAYMENT ================= */

paymentForm.onsubmit = async e => {

  e.preventDefault();

  const amount = Number(payAmount.value);

  if (amount <= 0) {
    alert("Invalid amount");
    return;
  }

  const res = await fetch(
    `${API}/sales/${saleId}/payments`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        amount,
        payment_type: payType.value,
        received_by: receivedBy.value
      })
    }
  );

  if (!res.ok) {
    alert("Payment failed");
    return;
  }

  paymentForm.reset();

  loadSaleDetails();
};

loadSaleDetails();
