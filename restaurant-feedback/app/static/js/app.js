document.addEventListener("DOMContentLoaded", () => {
  // --- Live search ---
  const input = document.getElementById("search-input");
  const dropdown = document.getElementById("search-results");

  if (input && dropdown) {
    let debounce = null;

    input.addEventListener("input", () => {
      clearTimeout(debounce);
      const q = input.value.trim();
      if (q.length < 2) {
        dropdown.hidden = true;
        return;
      }
      debounce = setTimeout(() => {
        fetch(`/api/restaurants/search?q=${encodeURIComponent(q)}`)
          .then((r) => r.json())
          .then((data) => {
            if (!data.length) {
              dropdown.hidden = true;
              return;
            }
            dropdown.innerHTML = data
              .map(
                (r) => `
              <a href="/restaurant/${r.id}" class="dropdown-item">
                <strong>${escapeHtml(r.name)}</strong>
                <span>${escapeHtml(r.address)}</span>
                ${r.avg_rating ? `<span class="rating-badge">${r.avg_rating} &#9733;</span>` : ""}
              </a>`
              )
              .join("");
            dropdown.hidden = false;
          });
      }, 250);
    });

    document.addEventListener("click", (e) => {
      if (!dropdown.contains(e.target) && e.target !== input) {
        dropdown.hidden = true;
      }
    });
  }

  // --- Star rating inputs ---
  document.querySelectorAll(".star-input").forEach((container) => {
    const radios = container.querySelectorAll('input[type="radio"]');
    const stars = container.querySelectorAll(".star");

    function highlight(upTo) {
      stars.forEach((s, i) => {
        s.classList.toggle("active", i < upTo);
      });
    }

    radios.forEach((radio, idx) => {
      radio.addEventListener("change", () => highlight(idx + 1));
    });

    // Init from existing value
    const preset = parseInt(container.dataset.rating, 10);
    if (preset > 0) highlight(preset);
  });

  // --- Auto-dismiss flash messages ---
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 300);
    }, 4000);
  });
});

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
