document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".toast").forEach((el) => bootstrap.Toast.getOrCreateInstance(el).show());

  // Evita envio duplicado (clique duplo): o segundo POST chegaria com um token CSRF já trocado.
  document.querySelectorAll('form[method="post"]').forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (form.dataset.submitting) {
        event.preventDefault();
        return;
      }
      form.dataset.submitting = "true";
      setTimeout(() => {
        form.querySelectorAll('button[type="submit"], button:not([type])').forEach((btn) => {
          btn.disabled = true;
          btn.insertAdjacentHTML("afterbegin", '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>');
        });

// Ao voltar pelo histórico (bfcache), reabilita os formulários.
window.addEventListener("pageshow", (event) => {
  if (!event.persisted) return;
  document.querySelectorAll("form[data-submitting]").forEach((form) => {
    delete form.dataset.submitting;
    form.querySelectorAll("button[disabled]").forEach((btn) => {
      btn.disabled = false;
      btn.querySelector(".spinner-border")?.remove();
    });
  });
});
      }, 0);
    });

// Ao voltar pelo histórico (bfcache), reabilita os formulários.
window.addEventListener("pageshow", (event) => {
  if (!event.persisted) return;
  document.querySelectorAll("form[data-submitting]").forEach((form) => {
    delete form.dataset.submitting;
    form.querySelectorAll("button[disabled]").forEach((btn) => {
      btn.disabled = false;
      btn.querySelector(".spinner-border")?.remove();
    });
  });
});
  });

// Ao voltar pelo histórico (bfcache), reabilita os formulários.
window.addEventListener("pageshow", (event) => {
  if (!event.persisted) return;
  document.querySelectorAll("form[data-submitting]").forEach((form) => {
    delete form.dataset.submitting;
    form.querySelectorAll("button[disabled]").forEach((btn) => {
      btn.disabled = false;
      btn.querySelector(".spinner-border")?.remove();
    });
  });
});

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

// Ao voltar pelo histórico (bfcache), reabilita os formulários.
window.addEventListener("pageshow", (event) => {
  if (!event.persisted) return;
  document.querySelectorAll("form[data-submitting]").forEach((form) => {
    delete form.dataset.submitting;
    form.querySelectorAll("button[disabled]").forEach((btn) => {
      btn.disabled = false;
      btn.querySelector(".spinner-border")?.remove();
    });
  });
});
  }
});

// Ao voltar pelo histórico (bfcache), reabilita os formulários.
window.addEventListener("pageshow", (event) => {
  if (!event.persisted) return;
  document.querySelectorAll("form[data-submitting]").forEach((form) => {
    delete form.dataset.submitting;
    form.querySelectorAll("button[disabled]").forEach((btn) => {
      btn.disabled = false;
      btn.querySelector(".spinner-border")?.remove();
    });
  });
});
