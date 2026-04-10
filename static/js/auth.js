const API = "https://zhagaram-api.onrender.com";

async function login() {

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ username, password })
  });

  const data = await res.json();

  if (!res.ok) {
    document.getElementById("error").innerText =
      data.detail || "Login failed";
    return;
  }

  // save JWT
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("role", data.role);

  // redirect logic
  if (data.showroom_required) {
    window.location.href = "showroom-select.html";
  } else {
    window.location.href = "dashboard.html";
  }
}
