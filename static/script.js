function legendFor(code) {
  return LEGEND.find(e => e.code === code);
}

function applyColor(input) {
  const entry = legendFor(input.value.trim());
  if (entry) {
    input.style.background = entry.bg;
    input.style.color = entry.fg;
  } else {
    input.style.background = "transparent";
    input.style.color = "inherit";
  }
}

document.querySelectorAll("td.cell input").forEach(input => {
  input.addEventListener("change", () => {
    const value = input.value.trim();
    applyColor(input);
    fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        year: YEAR,
        week: WEEK,
        row: input.dataset.row,
        day: input.dataset.day,
        half: input.dataset.half,
        agent: input.dataset.agent,
        value: value,
      }),
    }).catch(() => alert("Échec de la sauvegarde, vérifie ta connexion."));
  });

  // navigation rapide au clavier entre les cases (flèches)
  input.addEventListener("keydown", (e) => {
    const inputs = Array.from(document.querySelectorAll("td.cell input"));
    const idx = inputs.indexOf(input);
    if (e.key === "ArrowRight" && idx < inputs.length - 1) inputs[idx + 1].focus();
    if (e.key === "ArrowLeft" && idx > 0) inputs[idx - 1].focus();
  });
});
