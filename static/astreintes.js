const CYCLE = ["", "bleu", "orange"];
const COLORS = { "bleu": "#2E75B6", "orange": "#C0530A", "": "transparent" };

document.querySelectorAll(".astreinte-box").forEach(box => {
  box.addEventListener("click", () => {
    const current = box.dataset.state || "";
    const nextIndex = (CYCLE.indexOf(current) + 1) % CYCLE.length;
    const next = CYCLE[nextIndex];
    box.dataset.state = next;
    box.style.background = COLORS[next];

    fetch("/astreintes/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        year: YEAR,
        month: MONTH,
        agent_id: parseInt(box.dataset.agent, 10),
        day: parseInt(box.dataset.day, 10),
        state: next,
      }),
    }).catch(() => alert("Échec de la sauvegarde, vérifie ta connexion."));
  });
});
