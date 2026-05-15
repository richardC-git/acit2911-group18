const loginForm = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginButton = document.getElementById("login-button");
const loginMessage = document.getElementById("login-message");

loginForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  loginMessage.textContent = "";

  if (!email || !password) {
    loginMessage.textContent = "Email and password are required.";
    return;
  }

  loginButton.disabled = true;
  loginButton.textContent = "Logging in...";

  try {
    const response = await fetch("/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      loginMessage.textContent = data.error || "Login failed.";
      return;
    }

    window.location.href = "/";
  } catch (error) {
    loginMessage.textContent = "Unable to connect to the server.";
  } finally {
    loginButton.disabled = false;
    loginButton.textContent = "Login";
  }
});