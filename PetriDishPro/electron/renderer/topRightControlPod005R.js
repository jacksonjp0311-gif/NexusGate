(() => {
  "use strict";

  const SEAL = "PETRI_005R_TOP_RIGHT_CONTROL_POD_ALIGNMENT";

  function norm(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function upper(value) {
    return norm(value).toUpperCase();
  }

  function isControlButton(button) {
    const t = upper(button.textContent);
    return (
      t === "CAPTURE" ||
      t === "PAUSE" ||
      t === "RESET" ||
      t === "STATE" ||
      t === "DRUG LAB" ||
      t.includes("DRUG LAB")
    );
  }

  function findButtons() {
    return Array.from(document.querySelectorAll("button")).filter(isControlButton);
  }

  function findPod(buttons) {
    const capture = buttons.find(b => upper(b.textContent) === "CAPTURE");
    if (capture && capture.parentElement) return capture.parentElement;
    return buttons.length ? buttons[0].parentElement : null;
  }

  function normalizeButtonText(button) {
    const t = upper(button.textContent);
    if (t.includes("DRUG")) button.textContent = "Drug Lab";
    if (t === "CAPTURE") button.textContent = "Capture";
    if (t === "PAUSE") button.textContent = "Pause";
    if (t === "RESET") button.textContent = "Reset";
    if (t === "STATE") button.textContent = "State";
  }

  function buttonRank(button) {
    const t = upper(button.textContent);
    if (t === "CAPTURE") return 1;
    if (t.includes("DRUG")) return 2;
    if (t === "PAUSE") return 3;
    if (t === "RESET") return 4;
    if (t === "STATE") return 5;
    return 99;
  }

  function repairTopRightPod() {
    const buttons = findButtons();
    if (buttons.length < 4) return;

    const pod = findPod(buttons);
    if (!pod) return;

    pod.id = "petri-005r-top-control-pod";
    pod.dataset.seal005r = SEAL;
    pod.classList.add("petri-005r-top-control-pod");

    buttons.forEach(button => {
      normalizeButtonText(button);
      button.classList.add("petri-005r-control-button");
      button.dataset.seal005r = SEAL;
      button.style.removeProperty("min-width");
      button.style.removeProperty("max-width");
      button.style.removeProperty("width");
      button.style.removeProperty("height");
      button.style.removeProperty("padding");
      button.style.removeProperty("margin");
    });

    buttons
      .slice()
      .sort((a, b) => buttonRank(a) - buttonRank(b))
      .forEach(button => {
        if (button.parentElement === pod) pod.appendChild(button);
      });

    if (pod.parentElement) {
      pod.parentElement.classList.add("petri-005r-top-control-shell");
      pod.parentElement.dataset.seal005r = SEAL;
    }

    window.PETRI_005R_TOP_RIGHT = {
      seal: SEAL,
      buttons: buttons.map(b => norm(b.textContent)),
      claim_boundary: "UI alignment only."
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", repairTopRightPod, { once: true });
  } else {
    repairTopRightPod();
  }

  let ticks = 0;
  const timer = window.setInterval(() => {
    ticks += 1;
    repairTopRightPod();
    if (ticks > 20) window.clearInterval(timer);
  }, 300);

  window.addEventListener("resize", () => window.setTimeout(repairTopRightPod, 80));
})();
