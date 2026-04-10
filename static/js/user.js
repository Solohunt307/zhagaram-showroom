const API = "http://127.0.0.1:8000";

/* =========================
   NAVIGATION
========================= */
function goToDashboard() {
  window.location.href = "dashboard.html";
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("role");
  window.location.href = "login.html";
}

/* =========================
   TOGGLE USER LIST
========================= */
function toggleUserList() {
  const panel = document.getElementById("userList");
  panel.classList.toggle("hidden");

  if (!panel.classList.contains("hidden")) {
    loadUsers();
  }
}

/* =========================
   ROLE CHANGE
========================= */
function handleRoleChange() {
  const role = document.getElementById("role").value;
  const showroomField = document.getElementById("showroomField");

  showroomField.style.display =
    role === "MANAGER" ? "block" : "none";
}

/* =========================
   LOAD SHOWROOMS
========================= */
async function loadShowrooms() {
  const token = localStorage.getItem("access_token");

  const res = await fetch(`${API}/auth/showrooms`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  const data = await res.json();

  const dropdown = document.getElementById("showroom");
  dropdown.innerHTML = "";

  data.forEach(s => {
    dropdown.innerHTML += `
      <option value="${s.id}">${s.name}</option>
    `;
  });
}

/* =========================
   CREATE USER (FIXED)
========================= */
async function createUser() {
  const token = localStorage.getItem("access_token");

  const payload = {
    name: document.getElementById("name").value,
    username: document.getElementById("username").value,
    email: document.getElementById("email").value,   // ✅ ADDED
    password: document.getElementById("password").value,
    role: document.getElementById("role").value,
    showroom_id:
      document.getElementById("role").value === "MANAGER"
        ? document.getElementById("showroom").value
        : null
  };

  // ✅ BASIC VALIDATION
  if (!payload.name || !payload.username || !payload.email || !payload.password) {
    alert("All fields are required");
    return;
  }

  const res = await fetch(`${API}/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  let data;
  try {
    data = await res.json();
  } catch {
    alert("Server error");
    return;
  }

  if (!res.ok) {
    alert(data.detail || "Failed to create user");
    return;
  }

  alert("User created successfully ✅");

  // clear form
  document.getElementById("name").value = "";
  document.getElementById("username").value = "";
  document.getElementById("email").value = "";
  document.getElementById("password").value = "";

  loadUsers();
}

/* =========================
   LOAD USERS
========================= */
async function loadUsers() {
  const token = localStorage.getItem("access_token");

  const res = await fetch(`${API}/users`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  const users = await res.json();

  const table = document.getElementById("userTable");
  table.innerHTML = "";

  users.forEach(u => {
    table.innerHTML += `
      <tr>
        <td>${u.name}</td>
        <td>${u.username}</td>
        <td>${u.email}</td> <!-- ✅ ADDED -->
        <td class="${u.role === 'ADMIN' ? 'role-admin' : 'role-manager'}">${u.role}</td>
        <td>${u.showroom_name || '-'}</td>
        <td class="actions">
          <button class="btn-danger" onclick="deleteUser(${u.id})">Delete</button>
          <button onclick="changePassword(${u.id})">Password</button>
        </td>
      </tr>
    `;
  });
}

/* =========================
   DELETE USER
========================= */
async function deleteUser(id) {
  if (!confirm("Delete this user?")) return;

  const token = localStorage.getItem("access_token");

  await fetch(`${API}/users/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  loadUsers();
}

/* =========================
   CHANGE PASSWORD
========================= */
async function changePassword(id) {
  const newPass = prompt("Enter new password:");

  if (!newPass) return;

  const token = localStorage.getItem("access_token");

  await fetch(`${API}/users/${id}/password`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ password: newPass })
  });

  alert("Password updated ✅");
}

/* =========================
   INIT
========================= */
window.onload = function () {
  loadShowrooms();
};