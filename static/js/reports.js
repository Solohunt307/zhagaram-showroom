const API = "https://zhagaram-api.onrender.com";

// ==========================
// TOKEN HANDLING
// ==========================

function getToken() {

    // 🔥 try both keys (fix for mismatch)
    let token = localStorage.getItem("token");

    if (!token) {
        token = localStorage.getItem("access_token");
    }

    return token;
}

// ==========================
// HEADERS
// ==========================

function getHeaders() {

    const token = getToken();

    if (!token) {
        console.warn("No token found");
        alert("Please login again");
        window.location.href = "/static/login.html";
        return null;
    }

    return {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    };
}

// ==========================
// PARAMS (SAFE DEFAULT)
// ==========================

function getParams() {

    let from = document.getElementById("fromDate")?.value;
    let to = document.getElementById("toDate")?.value;

    // 🔥 default last 7 days
    if (!to) {
        let today = new Date();
        to = today.toISOString().split("T")[0];
    }

    if (!from) {
        let past = new Date();
        past.setDate(past.getDate() - 7);
        from = past.toISOString().split("T")[0];
    }

    return `?from_date=${from}&to_date=${to}`;
}

// ==========================
// SAFE API CALL
// ==========================

async function apiCall(url) {

    const headers = getHeaders();
    if (!headers) return null;

    try {

        const res = await fetch(API + url, {
            headers: headers
        });

        // 🔥 only logout on 401
        if (res.status === 401) {
            alert("Session expired. Please login again");
            localStorage.removeItem("token");
            localStorage.removeItem("access_token");
            window.location.href = "/static/login.html";
            return null;
        }

        // 🔥 handle other errors without logout
        if (!res.ok) {
            const text = await res.text();
            console.error("API ERROR:", text);
            return null;
        }

        return await res.json();

    } catch (err) {
        console.error("Network error:", err);
        return null;
    }
}

// ==========================
// LOAD ALL
// ==========================

function loadAll() {

    console.log("TOKEN:", getToken()); // 🔥 debug

    loadSummary();
    loadTopProducts();
    loadEmployees();
    loadCustomers();
    loadTrend();
}

// ==========================
// 1. SALES SUMMARY
// ==========================

async function loadSummary() {

    const data = await apiCall("/reports/sales-summary" + getParams());

    if (!data) return;

    document.getElementById("summary").innerText =
        `Revenue: ₹${data.total_revenue} | Invoices: ${data.total_invoices} | Avg: ₹${data.avg_order_value}`;
}

// ==========================
// 2. TOP PRODUCTS
// ==========================

async function loadTopProducts() {

    const data = await apiCall("/reports/top-products");

    if (!data || !Array.isArray(data)) return;

    let html = "";

    data.forEach(p => {
        html += `
            <tr>
                <td>${p.product}</td>
                <td>${p.qty}</td>
                <td>₹${p.revenue}</td>
            </tr>
        `;
    });

    document.getElementById("productTable").innerHTML = html;
}

// ==========================
// 3. EMPLOYEE PERFORMANCE
// ==========================

async function loadEmployees() {

    const data = await apiCall("/reports/sales-by-employee");

    if (!data || !Array.isArray(data)) return;

    let html = "";

    data.forEach(e => {
        html += `
            <tr>
                <td>${e.employee}</td>
                <td>${e.invoice_count}</td>
                <td>₹${e.revenue}</td>
            </tr>
        `;
    });

    document.getElementById("employeeTable").innerHTML = html;
}

// ==========================
// 4. CUSTOMER PATTERNS
// ==========================

async function loadCustomers() {

    const data = await apiCall("/reports/customers");

    if (!data || !Array.isArray(data)) return;

    let html = "";

    data.forEach(c => {
        html += `
            <tr>
                <td>${c.customer}</td>
                <td>${c.orders}</td>
            </tr>
        `;
    });

    document.getElementById("customerTable").innerHTML = html;
}

// ==========================
// 5. SALES TREND
// ==========================

let chart;

async function loadTrend() {

    const data = await apiCall("/reports/sales-trend?days=7");

    if (!data || !Array.isArray(data)) return;

    let labels = [];
    let values = [];

    data.forEach(d => {
        labels.push(d.date);
        values.push(d.revenue);
    });

    const ctx = document.getElementById("trendChart");

    if (!ctx) return;

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Revenue",
                data: values
            }]
        },
        options: {
            responsive: true
        }
    });
}

// ==========================
// 6. EXPORT CSV
// ==========================

function exportCSV(type) {

    const token = getToken();

    if (!token) {
        alert("Please login again");
        window.location.href = "/static/login.html";
        return;
    }

    window.open(
        API + `/reports/export/csv?type=${type}&token=${token}`,
        "_blank"
    );
}

// ==========================
// AUTO LOAD
// ==========================

document.addEventListener("DOMContentLoaded", () => {
    loadAll();
});
