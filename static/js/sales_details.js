console.log("Sales Details JS Loaded");

/* ================= GLOBAL ================= */

const API = window.API;
const token = window.token;

if (!token) location.href = "login.html";

/* ================= GET ID ================= */

const params = new URLSearchParams(window.location.search);

const saleId = params.get("id");

if (!saleId) {
  alert("Sale id missing");
  location.href = "sales.html";
}

/* ================= DOM ================= */

const invoiceEl = document.getElementById("invoice");
const customerEl = document.getElementById("customer");
const phoneEl = document.getElementById("phone");
const addressEl = document.getElementById("address");

const productEl = document.getElementById("product");
const qtyEl = document.getElementById("qty");

const orderEl = document.getElementById("order");
const paidEl = document.getElementById("paid");
const balanceEl = document.getElementById("balance");

const dateEl = document.getElementById("date");

const paymentTable = document.getElementById("paymentTable");

/* =====================================================
                    LOAD DETAILS
===================================================== */

async function loadSaleDetails() {

  const res = await fetch(
    `${API}/sales/${saleId}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  const sale = await res.json();

  invoiceEl.innerText = sale.invoice_number;

  customerEl.innerText = sale.customer.name;
  phoneEl.innerText = sale.customer.phone || "";
  addressEl.innerText = sale.customer.address || "";

  productEl.innerText = sale.product.product_name;
  qtyEl.innerText = sale.quantity;

  orderEl.innerText = sale.order_amount;
  paidEl.innerText = sale.paid_amount;
  balanceEl.innerText = sale.balance_amount;

  dateEl.innerText = sale.sale_date;

  renderPayments(sale.payments || []);
}

/* =====================================================
                    PAYMENTS
===================================================== */

function renderPayments(payments) {

  paymentTable.innerHTML = "";

  payments.forEach(p => {

    paymentTable.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${new Date(p.paid_at).toLocaleString()}</td>
        <td>${p.payment_type}</td>
        <td>${p.amount}</td>
        <td>${p.received_by}</td>
      </tr>
    `);
  });
}

/* =====================================================
                    ADD PAYMENT
===================================================== */

async function addPayment() {

  const amount =
    Number(document.getElementById("payAmount").value);

  const payment_type =
    document.getElementById("payMode").value;

  const received_by =
    document.getElementById("payReceivedBy").value;

  if (!amount || amount <= 0) {
    alert("Enter valid amount");
    return;
  }

  const fd = new FormData();

  fd.append("amount", amount);
  fd.append("payment_type", payment_type);
  fd.append("received_by", received_by);

  const res = await fetch(
    `${API}/sales/${saleId}/payments`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: fd
    }
  );

  const data = await res.json();

  if (!res.ok) {
    alert(data.detail || "Payment failed");
    return;
  }

  alert("Payment added");

  document.getElementById("payAmount").value = "";
  document.getElementById("payReceivedBy").value = "";

  loadSaleDetails();
}

/* =====================================================
                    INVOICE
===================================================== */

function viewInvoice() {

  window.open(
    `${API}/sales/${saleId}/invoice`,
    "_blank"
  );
}

/* =====================================================
                    INIT
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

  loadSaleDetails();

});
