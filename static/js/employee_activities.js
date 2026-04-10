const API = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");

if (!token) location.href = "login.html";

let actPage = 1;
let editingId = null;

/* ================= LOAD ================= */

async function loadActivities(page = 1) {

  actPage = page;

  const search = searchBox.value || "";
  const from = fromDate.value || "";
  const to = toDate.value || "";

  const res = await fetch(
    `${API}/employees/activities?page=${page}&search=${search}&from_date=${from}&to_date=${to}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  const data = await res.json();

  const tbody = document.getElementById("activityTable");

  tbody.innerHTML = "";

  data.items.forEach(a => {

    tbody.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${a.employee_name}</td>
        <td>${a.total_hours}</td>
        <td>${a.salary_per_month}</td>
        <td>${a.salary_paid}</td>
        <td>${a.activity_date}</td>
        <td>${a.payment_type}</td>
        <td>
          <button onclick="openEditModal(${a.id})">Edit</button>
          <button onclick="deleteActivity(${a.id})">Delete</button>
        </td>
      </tr>
    `);
  });

  renderPagination(data.total);
}

/* ================= PAGINATION ================= */

function renderPagination(total) {

  const pages = Math.ceil(total / 10);

  pagination.innerHTML = "";

  for (let i = 1; i <= pages; i++) {

    const btn = document.createElement("button");

    btn.innerText = i;

    if (i === actPage) btn.disabled = true;

    btn.onclick = () => loadActivities(i);

    pagination.appendChild(btn);
  }
}

/* ================= DELETE ================= */

async function deleteActivity(id) {

  if (!confirm("Delete this activity?")) return;

  await fetch(`${API}/employees/activity/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  loadActivities(actPage);
}

/* ================= EXPORT ================= */

function exportCSV() {

  window.open(
    `${API}/employees/activities/export/csv`,
    "_blank"
  );
}

/* ================= EDIT FLOW ================= */

async function openEditModal(id) {

  editingId = id;

  // fetch single activity from list cache
  const res = await fetch(
    `${API}/employees/activities?page=${actPage}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  const data = await res.json();

  const act = data.items.find(x => x.id === id);

  if (!act) {
    alert("Activity not found");
    return;
  }

  editId.value = id;
  editName.value = act.employee_name;
  editHours.value = act.total_hours;
  editSalary.value = act.salary_per_month;
  editPaid.value = act.salary_paid;
  editDate.value = act.activity_date;
  editPayType.value = act.payment_type;

  document.getElementById("editModal").style.display = "flex";
}

function closeModal() {

  document.getElementById("editModal").style.display = "none";
  editingId = null;
}

/* ================= UPDATE ================= */

async function updateActivity() {

  const payload = {
    employee_id: 0, // backend ignores for update
    total_hours: Number(editHours.value),
    salary_per_month: Number(editSalary.value),
    salary_paid: Number(editPaid.value),
    activity_date: editDate.value,
    payment_type: editPayType.value
  };

  const res = await fetch(
    `${API}/employees/activity/${editingId}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    }
  );

  if (!res.ok) {
    alert("Update failed");
    return;
  }

  closeModal();
  loadActivities(actPage);
}

/* ================= INIT ================= */

loadActivities();
