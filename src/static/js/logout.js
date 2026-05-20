const logoutButtons = document.querySelectorAll(".logout-button");

logoutButtons.forEach(button => {
  button.addEventListener("click", async () => {

    await fetch("/api/logout", {
      method: "POST",
    });

    window.location.href = "/login";
  });
});