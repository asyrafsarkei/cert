const API_BASE = "https://yourapp.onrender.com"; // your Flask backend URL

// Login form
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(formData)),
      headers: { "Content-Type": "application/json" }
    });
    const data = await res.json();
    document.getElementById("message").innerText = data.message;
    if (data.success) window.location.href = "index.html";
  });
}

// Registration form
const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(registerForm);
    const res = await fetch(`${API_BASE}/register`, {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(formData)),
      headers: { "Content-Type": "application/json" }
    });
    const data = await res.json();
    document.getElementById("message").innerText = data.message;
  });
}
