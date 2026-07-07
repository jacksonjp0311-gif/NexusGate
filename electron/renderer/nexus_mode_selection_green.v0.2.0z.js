/*
  NEXUS GATE â€” Mode Selection Green HUD v0.2.0Z
  Clean option labels and green mode/system-monitor sync.
*/
(function () {
  if (window.__nexusModeSelectionGreenV020Z) return;
  window.__nexusModeSelectionGreenV020Z = true;

  const MODES = {
    FAST: {
      label: "FAST / Phi-4-mini",
      model: "FAST â†’ Phi-4-mini",
      command: ".\\scripts\\nexus.ps1 tnn-chat -Tag \"<ask>\" -CallModel",
      icon: "âš¡",
      badge: "hot"
    },
    BALANCED: {
      label: "BALANCED / Phi-4-mini",
      model: "BALANCED â†’ Phi-4-mini",
      command: ".\\scripts\\nexus.ps1 tnn-chat -Tag \"<ask>\" -CallModel",
      icon: "âš–",
      badge: "steady"
    },
    DEEP: {
      label: "DEEP / Mistral",
      model: "DEEP â†’ Mistral",
      command: ".\\scripts\\nexus.ps1 tnn-deep -Tag \"<ask>\"",
      icon: "âœ£",
      badge: "deep"
    },
    TNN: {
      label: "Tesseract Neural Network",
      model: "TNN â†’ Phi-4-mini hot lane",
      command: ".\\scripts\\nexus.ps1 tnn-chat -Tag \"<ask>\" -CallModel",
      icon: "â—‡",
      badge: "local"
    },
    HANDOFF: {
      label: "HANDOFF / ChatGPT-Codex",
      model: "HANDOFF â†’ ChatGPT-Codex",
      command: "/handoff run",
      icon: "â˜š",
      badge: "relay"
    }
  };

  function $(id) {
    return document.getElementById(id);
  }

  function ensureOptions(select) {
    if (!select) return;
    const current = select.value || "DEEP";
    select.innerHTML = "";

    Object.keys(MODES).forEach((key) => {
      const option = document.createElement("option");
      option.value = key;
      option.textContent = MODES[key].label;
      select.appendChild(option);
    });

    select.value = MODES[current] ? current : "DEEP";
  }

  function ensureGreenList(select) {
    if (!select) return;

    let list = document.querySelector(".nexus-mode-green-list");
    if (list) return;

    list = document.createElement("div");
    list.className = "nexus-mode-green-list";
    list.setAttribute("role", "listbox");
    list.setAttribute("aria-label", "Clean local voice relay options");

    Object.keys(MODES).forEach((key) => {
      const mode = MODES[key];
      const row = document.createElement("button");
      row.type = "button";
      row.className = "nexus-mode-green-option";
      row.dataset.mode = key;
      row.innerHTML = [
        '<span class="nexus-mode-green-icon" aria-hidden="true">' + mode.icon + "</span>",
        "<span>" + mode.label + "</span>",
        '<span class="nexus-mode-green-badge">' + mode.badge + "</span>"
      ].join("");

      row.addEventListener("click", function () {
        select.value = key;
        select.dispatchEvent(new Event("change", { bubbles: true }));
      });

      list.appendChild(row);
    });

    select.insertAdjacentElement("afterend", list);
  }

  function syncModeUI() {
    const select = $("role-select");
    if (!select) return;

    const key = MODES[select.value] ? select.value : "DEEP";
    const mode = MODES[key];

    const status = $("selector-hud-status");
    const model = $("role-model");
    const command = $("role-command");

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
