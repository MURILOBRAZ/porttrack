document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".toast").forEach((el) => bootstrap.Toast.getOrCreateInstance(el).show());

  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    const root = document.documentElement;
    const syncIcon = () => {
      toggle.innerHTML = root.getAttribute("data-bs-theme") === "dark"
        ? '<i class="bi bi-sun"></i>'
        : '<i class="bi bi-moon-stars"></i>';
    };
    syncIcon();
    toggle.addEventListener("click", () => {
      const next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-bs-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      syncIcon();
      document.dispatchEvent(new CustomEvent("themechange"));
    });
  }
});
