/*
  NEXUS GATE â€” Mode Selection Green HUD v0.2.0ZV
  Custom green selector surface. Native select remains as state holder only.
*/
(function () {
  if (window.__nexusModeSelectionGreenV020ZV) return;
  window.__nexusModeSelectionGreenV020ZV = true;

  const MODES = {
    FAST: {
      label: "FAST / Phi-4-mini",
      model: "FAST -> Phi-4-mini",
      command: ".\\scripts\\nexus.ps1 tnn-chat -Tag \"<ask>\" -CallModel",
      icon: "F",
      badge: "HOT"
    },
    BALANCED: {
      label: "BALANCED / Phi-4-mini",
      model: "BALANCED -> Phi-4-mini",
      command: ".\\scripts\\nexus.ps1 tnn-chat -Tag \"<ask>\" -CallModel",
      icon: "B",
      badge: "STEADY"
    },
    DEEP: {
      label: "DEEP / Mistral",
      model: "DEEP -> Mistral",
      command: ".\\scripts\\nexus.ps1 tnn-deep -Tag \"<ask>\"",
      icon: "D",
      badge: "DEEP"
    },
    TNN: {
      label: "Tesseract Neural Network",
      model: "TNN -> Phi-4-mini hot lane",
      command: ".\\scripts\\nexus.ps1 tnn-chat -Tag \"<ask>\" -CallModel",
      icon: "T",
      badge: "LOCAL"
    },
    HANDOFF: {
      label: "HANDOFF / ChatGPT-Codex",
      model: "HANDOFF -> ChatGPT-Codex",
      command: "/handoff run",
      icon: "H",
      badge: "RELAY"
    }
  };

  function $(id) {
    return document.getElementById(id);
  }

  function ensureOptions(select) {
    if (!select) return;
    const current = MODES[select.value] ? select.value : "BALANCED";
    select.innerHTML = "";

    Object.keys(MODES).forEach((key) => {
      const option = document.createElement("option");
      option.value = key;
      option.textContent = MODES[key].label;
      select.appendChild(option);
    });

    select.value = current;
  }

  function ensureCurrent(select) {
    if (!select) return null;
    let current = document.querySelector(".nexus-mode-current");
    if (current) return current;

    current = document.createElement("div");
    current.className = "nexus-mode-current";
    current.setAttribute("role", "status");
    current.setAttribute("aria-live", "polite");
    select.insertAdjacentElement("afterend", current);
    return current;
  }

  function ensureGreenList(select) {
    if (!select) return;

    let list = document.querySelector(".nexus-mode-green-list");
    if (list) {
      list.innerHTML = "";
    } else {
      list = document.createElement("div");
      list.className = "nexus-mode-green-list";
      list.setAttribute("role", "listbox");
      list.setAttribute("aria-label", "Clean local voice relay options");
      const current = ensureCurrent(select);
      if (current) current.insertAdjacentElement("afterend", list);
      if (!current) select.insertAdjacentElement("afterend", list);
    }

    Object.keys(MODES).forEach((key) => {
      const mode = MODES[key];
      const row = document.createElement("button");
      row.type = "button";
      row.className = "nexus-mode-green-option";
      row.dataset.mode = key;
      row.innerHTML =
        '<span class="nexus-mode-green-icon" aria-hidden="true">' + mode.icon + "</span>" +
        "<span>" + mode.label + "</span>" +
        '<span class="nexus-mode-green-badge">' + mode.badge + "</span>";

      row.addEventListener("click", function () {
        select.value = key;
        select.dispatchEvent(new Event("change", { bubbles: true }));
      });

      list.appendChild(row);
    });
  }

  function syncModeUI() {
    const select = $("role-select");
    if (!select) return;

    const key = MODES[select.value] ? select.value : "BALANCED";
    const mode = MODES[key];

    const current = ensureCurrent(select);
    const status = $("selector-hud-status");
    const model = $("role-model");
    const command = $("role-command");

    if (current) current.textContent = mode.label;
    if (status) status.textContent = mode.model.toUpperCase();
    if (model) model.textContent = mode.model;
    if (command) command.textContent = mode.command;

    document.querySelectorAll(".nexus-mode-green-option").forEach((row) => {
      const active = row.dataset.mode === key;
      row.classList.toggle("is-active", active);
      row.setAttribute("aria-selected", active ? "true" : "false");
    });

    document.body.classList.add("nexus-mode-green-active");
    document.body.setAttribute("data-nexus-mode-selection", key);
  }

  function wireCopy() {
    const button = $("copy-role-command");
    const command = $("role-command");
    if (!button || !command || button.dataset.nexusGreenCopy === "1") return;

    button.dataset.nexusGreenCopy = "1";
    button.addEventListener("click", async function () {
      const text = command.textContent || "";
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text);
        }
        button.textContent = "Copied";
        window.setTimeout(() => { button.textContent = "Copy command"; }, 900);
      } catch (_) {
        button.textContent = "Copy manually";
        window.setTimeout(() => { button.textContent = "Copy command"; }, 1200);
      }
    });
  }

  function boot() {
    const select = $("role-select");
    ensureOptions(select);
    ensureCurrent(select);
    ensureGreenList(select);

    if (select && select.dataset.nexusGreenWired !== "1") {
      select.dataset.nexusGreenWired = "1";
      select.addEventListener("change", syncModeUI);
    }

    wireCopy();
    syncModeUI();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  document.addEventListener("click", function () {
    window.setTimeout(boot, 0);
  }, true);
})();
