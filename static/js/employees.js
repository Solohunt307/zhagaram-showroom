console.log("Employees JS loaded");

/* ================= GLOBAL ================= */

const API = "https://zhagaram-api.onrender.com";
const token = localStorage.getItem("access_token");

if (!token) location.href = "login.html";

const PAGE_SIZE = 10;

let empPage = 1;
let actPage = 1;

let editingEmpId = null;
let editingActId = null;

/* ================= DOM ================= */

const empForm = document.getElementById("empForm");

const empTable = document.getElementById("empTable");
const empPagination = document.getElementById("empPagination");

const activityTable = document.getElementById("activityTable");
const activityPagination = document.getElementById("activityPagination");

/* ================= SECTION TOGGLER ================= */

function hideAll() {
  document.getElementById("employeeFormBox").style.display = "none";
  document.getElementById("activityFormBox").style.display = "none";
  document.getElementById("employeeListBox").style.display = "none";
  document.getElementById("activityListBox").style.display = "none";
}

window.showEmployeeForm = function () {
  hideAll();
  empForm.reset();
  editingEmpId = null;
  document.getElementById("employeeFormBox").style.display = "block";
};

window.showActivityForm = function () {
  hideAll();
  editingActId = null;
  document.getElementById("activityFormBox").style.display = "block";
  loadEmployeeDropdown();
};

window.showEmployeeList = function () {
  hideAll();
  document.getElementById("employeeListBox").style.display = "block";
  loadEmployees();
};

window.showActivityList = function () {
  hideAll();
  document.getElementById("activityListBox").style.display = "block";
  loadActivities();
};

/* ================= CREATE / UPDATE EMPLOYEE ================= */

empForm.addEventListener("submit", async e => {
  e.preventDefault();

  const fd = new FormData(empForm);

  const url = editingEmpId
    ? `${API}/employees/${editingEmpId}`
    : `${API}/employees`;

  const method = editingEmpId ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: fd
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.detail || "Employee save failed");
    return;
  }

  alert("Employee saved!");
  showEmployeeList();
});

/* ================= LOAD EMPLOYEES ================= */

async function loadEmployees(page = 1) {

  empPage = page;

  const search = document.getElementById("empSearch").value || "";

  const res = await fetch(
    `${API}/employees?page=${page}&search=${search}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const data = await res.json();

  renderEmployees(data.items || []);
  renderEmpPagination(data.total || 0);
}

function renderEmployees(items) {

  empTable.innerHTML = "";

  items.forEach(e => {
    empTable.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${e.emp_code}</td>
        <td>${e.name}</td>
        <td>${e.address || ""}</td>
        <td>${e.mobile || ""}</td>
        <td>${e.role}</td>
        <td>
          ${e.file_path ? `<a href="${API}/${e.file_path}" target="_blank">Download</a>` : ""}
        </td>
        <td>
          <button onclick="editEmployee(${e.id})">Edit</button>
          <button onclick="deleteEmployee(${e.id})">Delete</button>
        </td>
      </tr>
    `);
  });
}

function renderEmpPagination(total) {

  empPagination.innerHTML = "";

  const pages = Math.ceil(total / PAGE_SIZE);

  for (let i = 1; i <= pages; i++) {
    const btn = document.createElement("button");
    btn.innerText = i;

    if (i === empPage) btn.disabled = true;

    btn.onclick = () => loadEmployees(i);
    empPagination.appendChild(btn);
  }
}

/* ================= EDIT EMPLOYEE ================= */

window.editEmployee = async id => {

  const res = await fetch(`${API}/employees/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const emp = await res.json();

  editingEmpId = id;

  showEmployeeForm();

  empForm.emp_code.value = emp.emp_code;
  empForm.name.value = emp.name;
  empForm.address.value = emp.address || "";
  empForm.mobile.value = emp.mobile || "";
  empForm.email.value = emp.email || "";
  empForm.role.value = emp.role;
};

/* ================= DELETE EMPLOYEE ================= */

window.deleteEmployee = async id => {

  if (!confirm("Delete employee?")) return;

  const res = await fetch(`${API}/employees/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    alert("Delete failed");
    return;
  }

  alert("Employee deleted");
  loadEmployees(empPage);
};

/* ================= ACTIVITY ================= */

async function submitActivity() {

  const payload = {
    employee_id: parseInt(document.getElementById("empId").value),
    total_hours: Number(hours.value),
    salary_per_month: Number(salary.value),
    salary_paid: Number(paid.value),
    activity_date: actDate.value,
    payment_type: payType.value
  };

  const url = editingActId
    ? `${API}/employees/activity/${editingActId}`
    : `${API}/employees/activity`;

  const method = editingActId ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.detail || "Save failed");
    return;
  }

  alert("Activity saved!");
  showActivityList();
}

/* ================= LOAD ACTIVITIES ================= */

async function loadActivities(page = 1) {

  actPage = page;

  const search = document.getElementById("actSearch").value || "";

  const res = await fetch(
    `${API}/employees/activities?page=${page}&search=${search}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const data = await res.json();

  renderActivities(data.items || []);
  renderActivityPagination(data.total || 0);
}

function renderActivities(items) {

  activityTable.innerHTML = "";

  items.forEach(a => {
    activityTable.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${a.employee_name}</td>
        <td>${a.total_hours}</td>
        <td>${a.salary_per_month}</td>
        <td>${a.salary_paid}</td>
        <td>${a.activity_date}</td>
        <td>${a.payment_type}</td>
        <td>
          <button onclick="editActivity(${a.id})">Edit</button>
          <button onclick="deleteActivity(${a.id})">Delete</button>
        </td>
      </tr>
    `);
  });
}

function renderActivityPagination(total) {

  activityPagination.innerHTML = "";

  const pages = Math.ceil(total / PAGE_SIZE);

  for (let i = 1; i <= pages; i++) {
    const btn = document.createElement("button");
    btn.innerText = i;

    if (i === actPage) btn.disabled = true;

    btn.onclick = () => loadActivities(i);
    activityPagination.appendChild(btn);
  }
}

/* ================= DELETE ACTIVITY ================= */

window.deleteActivity = async id => {

  if (!confirm("Delete activity?")) return;

  const res = await fetch(`${API}/employees/activity/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) {
    alert("Delete failed");
    return;
  }

  alert("Deleted");
  loadActivities(actPage);
};

/* ================= DROPDOWN ================= */

async function loadEmployeeDropdown() {

  const res = await fetch(`${API}/employees/dropdown`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await res.json();

  const dropdown = document.getElementById("empId");

  dropdown.innerHTML = `<option value="">Select Employee</option>`;

  data.forEach(e => {
    dropdown.innerHTML += `<option value="${e.id}">${e.name}</option>`;
  });
}

/* ================= CSV EXPORT ================= */

async function exportEmployeesCSV() {

  const res = await fetch(`${API}/employees/export/csv`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const blob = await res.blob();

  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "employees.csv";
  a.click();
}

async function exportActivitiesCSV() {

  const res = await fetch(`${API}/employees/activities/export/csv`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const blob = await res.blob();

  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "activities.csv";
  a.click();
}

/* ================= INIT ================= */

hideAll();
showEmployeeList();
