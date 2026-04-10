const API = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");

if (!token) location.href = "login.html";

let empPage = 1;

async function loadEmployees(page = 1) {

  empPage = page;

  const search = searchBox.value || "";

  const res = await fetch(
    `${API}/employees?page=${page}&search=${search}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  const data = await res.json();

  const tbody = document.getElementById("empTable");

  tbody.innerHTML = "";

  data.items.forEach(e => {

    tbody.insertAdjacentHTML("beforeend", `
      <tr>
        <td>${e.emp_code}</td>
        <td>${e.name}</td>
        <td>${e.address || ""}</td>
        <td>
          ${e.file_path
            ? `<a href="${API}/${e.file_path}" target="_blank">Download</a>`
            : ""}
        </td>
        <td>
          <button onclick="editEmployee(${e.id})">Edit</button>
          <button onclick="deleteEmployee(${e.id})">Delete</button>
        </td>
      </tr>
    `);
  });

  renderPagination(data.total);
}

function renderPagination(total) {

  const pages = Math.ceil(total / 10);

  pagination.innerHTML = "";

  for (let i = 1; i <= pages; i++) {

    const btn = document.createElement("button");

    btn.innerText = i;

    if (i === empPage) btn.disabled = true;

    btn.onclick = () => loadEmployees(i);

    pagination.appendChild(btn);
  }
}

async function deleteEmployee(id) {

  if (!confirm("Delete employee?")) return;

  await fetch(`${API}/employees/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` }
  });

  loadEmployees(empPage);
}

async function exportEmployees() {

  const res = await fetch(${API}/employees/export/csv, {
    headers: {
      Authorization: Bearer ${token}
    }
  });

  if (!res.ok) {
    alert("Export failed");
    return;
  }

  const blob = await res.blob();

  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "employees.csv";
  a.click();
}

loadEmployees();
