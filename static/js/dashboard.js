/* ---------------- GLOBALS ---------------- */

window.API = "http://127.0.0.1:8000";

window.token = localStorage.getItem("access_token");

if (!token) {
  alert("No token found — redirecting to login");
  window.location.href = "login.html";
}

/* ---------------- LOAD SHOWROOMS ---------------- */

async function loadShowrooms() {

  console.log("Loading showrooms...");

  try {

    const res = await fetch(`${window.API}/auth/showrooms`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    console.log("Showroom status:", res.status);

    if (!res.ok) {
      const err = await res.text();
      console.error("Showroom API error:", err);
      return;
    }

    const data = await res.json();

    console.log("Showrooms received:", data);

    const div = document.getElementById("showrooms");

    if (!div) {
      console.error("showrooms div missing in HTML");
      return;
    }

    div.innerHTML = "";

    data.forEach(s => {

      const btn = document.createElement("button");

      btn.className = "showroom-card";
      btn.innerText = s.name;

      btn.onclick = () => selectShowroom(s.id);

      div.appendChild(btn);
    });

  } catch (err) {
    console.error("Network error loading showrooms:", err);
  }
}

/* ---------------- SELECT SHOWROOM ---------------- */

async function selectShowroom(id) {

  console.log("Selecting showroom:", id);

  const res = await fetch(`${window.API}/auth/select-showroom/${id}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (!res.ok) {
    console.error("Showroom select failed:", await res.text());
    return;
  }

  const data = await res.json();

  console.log("New token:", data.access_token);

  localStorage.setItem("access_token", data.access_token);

  window.location.href = "dashboard.html";
}

/* ---------------- AUTO RUN ---------------- */

document.addEventListener("DOMContentLoaded", () => {

  console.log("DOM loaded at:", window.location.pathname);

  if (window.location.pathname.includes("showroom-select")) {
    loadShowrooms();
  }

});

/* ---------------- EXPORT GLOBALS ---------------- */

window.loadShowrooms = loadShowrooms;
window.selectShowroom = selectShowroom;
