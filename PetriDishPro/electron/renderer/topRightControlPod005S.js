(() => {
  "use strict";

  const SEAL = "PETRI_005S_CONTROL_POD";

  function norm(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function upper(value) {
    return norm(value).toUpperCase();
  }

  function rank(label) {
    if (label === "CAPTURE") return 1;
    if (label === "DRUG LAB") return 2;
    if (label === "RUN" || label === "PAUSE") return 3;
    if (label === "RESET") return 4;
    if (label === "STATE") return 5;
    return 99;
  }

  function normalizeLabel(button) {
    const t = upper(button.textContent);
    if (t.includes("DRUG")) button.textContent = "Drug Lab";
    if (t === "CAPTURE") button.textContent = "Capture";
    if (t === "RUN") button.textContent = "Run";
    if (t === "PAUSE") button.textContent = "Pause";
    if (t === "RESET") button.textContent = "Reset";
    if (t === "STATE") button.textContent = "State";
  }

  function isTopControl(button) {
    const t = upper(button.textContent);
    return (
      t === "CAPTURE" ||
      t === "RUN" ||
      t === "PAUSE" ||
      t === "RESET" ||
      t === "STATE" ||
      t === "DRUG LAB" ||
      t.includes("DRUG LAB")
    );
  }

  function findButtons() {
    return Array.from(document.querySelectorAll("button")).filter(isTopControl);
  }

  function findPod(buttons) {
    const ordered = buttons.slice().sort((a, b) => rank(upper(a.textContent)) - rank(upper(b.textContent)));
    if (!ordered.length) return null;
    return ordered[0].parentElement || null;
  }

  function repairPod() {
    const buttons = findButtons();
    if (buttons.length < 4) return;

    const pod = findPod(buttons);
    if (!pod) return;

    pod.id = "petri-005s-top-control-pod";
    pod.classList.add("petri-005s-top-control-pod");
    pod.dataset.seal005s = SEAL;

    const parent = pod.parentElement;
    if (parent) {
      parent.classList.add("petri-005s-top-control-shell");
      parent.dataset.seal005s = SEAL;
    }

    buttons.forEach(button => {
      normalizeLabel(button);
      button.classList.add("petri-005s-control-button");
      button.classList.remove("petri-005s-control-button-drug");
      if (upper(button.textContent) === "DRUG LAB") {
        button.classList.add("petri-005s-control-button-drug");
      }
      button.style.removeProperty("width");
      button.style.removeProperty("min-width");
      button.style.removeProperty("max-width");
      button.style.removeProperty("height");
      button.style.removeProperty("margin");
      button.style.removeProperty("padding");
      button.style.removeProperty("position");
      button.style.removeProperty("top");
      button.style.removeProperty("left");
      button.style.removeProperty("right");
      button.dataset.seal005s = SEAL;
    });

    buttons
      .slice()
      .sort((a, b) => rank(upper(a.textContent)) - rank(upper(b.textContent)))
      .forEach(button => {
        if (button.parentElement === pod) pod.appendChild(button);
      });

    window.PETRI_005S_TOP_RIGHT = {
      seal: SEAL,
      buttons: buttons.map(b => norm(b.textContent)),
      count: buttons.length,
      claim_boundary: "Top-right UI alignment only."
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", repairPod, { once: true });
  } else {
    repairPod();
  }

  let tick = 0;
  const timer = setInterval(() => {
    tick += 1;
    repairPod();
    if (tick > 20) clearInterval(timer);
  }, 300);

  window.addEventListener("resize", () => setTimeout(repairPod, 80));
})();
