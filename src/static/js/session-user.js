const userNameElement = document.getElementById("user-name");

async function loadUserName() {
  const response = await fetch("/api/session");

  if (!response.ok) {
    return;
  }

  const data = await response.json();

  if (data.logged_in && data.user_name) {
    userNameElement.textContent = data.user_name;
  }
}

loadUserName();