/* ================= GLOBAL ================= */

const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");
const role = localStorage.getItem("role");

if (!token) {
  window.location.href = "login.html";
}

/* ================= NAV HELPERS ================= */

function goHome() {
  window.location.href = "dashboard.html";
}

function logout() {
  if (confirm("Are you sure you want to logout?")) {
    localStorage.clear();
    window.location.href = "login.html";
  }
}

function goModule(page) {
  window.location.href = page;
}

/* ================= DASHBOARD INIT ================= */

window.onload = () => {

  console.log("Dashboard loaded");

  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("role");

  if (!token) {
    window.location.href = "login.html";
    return;
  }

  // Decode token
  const payload = JSON.parse(atob(token.split(".")[1]));

  console.log("Token payload:", payload);

  // 🚨 ADMIN MUST SELECT SHOWROOM
  if (role === "ADMIN" && !payload.showroom_id) {
    window.location.href = "showroom-select.html";
    return;
  }

  // Hide user management button
  if (role !== "ADMIN") {
    const btn = document.querySelector(".user-mgmt-btn");
    if (btn) btn.style.display = "none";
  }

  applyRoleRestrictions();

  loadDashboardKPIs();
  loadDailySalesChart();
};

/* ================= ROLE BASED UI ================= */

function goToUserManagement() {
  window.location.href = "user-management.html";
}

function applyRoleRestrictions() {

  if (!role) return;

  // TECHNICIAN = only service module
  if (role === "TECHNICIAN") {

    document.querySelectorAll(".module-card").forEach(card => {

      if (!card.innerText.includes("Service")) {
        card.style.display = "none";
      }

    });
  }

  // MANAGER limited modules
  if (role === "MANAGER") {

    document.querySelectorAll(".module-card").forEach(card => {

      const allowed = [
        "Products",
        "Purchases",
        "Sales",
        "Customers",
        "Service"
      ];

      if (!allowed.some(t => card.innerText.includes(t))) {
        card.style.display = "none";
      }

    });
  }

}

/* ================= KPI LOADER ================= */

async function loadDashboardKPIs() {

  try {

    const res = await fetch(`${API}/dashboard/kpis`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!res.ok) {
      console.error(await res.text());
      return;
    }

    const data = await res.json();

    console.log("Dashboard KPIs:", data);

    document.getElementById("totalSales").innerText =
      "₹ " + data.total_sales;

    document.getElementById("grossProfit").innerText =
      "₹ " + data.gross_profit;

    document.getElementById("totalExpenses").innerText =
      "₹ " + data.total_expenses;

    document.getElementById("netProfit").innerText =
      "₹ " + data.net_profit;

    document.getElementById("activeTickets").innerText =
      data.active_tickets;

    document.getElementById("closedTickets").innerText =
      data.closed_tickets;

  } catch (err) {
    console.error("Dashboard KPI error:", err);
  }
}




let dailySalesChart;

function renderDailySalesChart(labels, values) {

  const ctx = document
    .getElementById("dailySalesChart")
    .getContext("2d");

  if (dailySalesChart) {
    dailySalesChart.destroy();
  }

  dailySalesChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Daily Sales ₹",
        data: values,
        borderWidth: 2,
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}


async function loadDailySalesChart() {

  try {

    const res = await fetch(`${API}/dashboard/daily-sales?days=7`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!res.ok) {
      console.error("Daily sales API failed");
      return;
    }

    const data = await res.json();

    console.log("Daily sales chart:", data);

    renderDailySalesChart(data.labels, data.values);

  } catch (err) {
    console.error("Daily chart error:", err);
  }
}

