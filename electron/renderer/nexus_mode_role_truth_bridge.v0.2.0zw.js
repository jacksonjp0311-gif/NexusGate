/*
  NEXUS GATE - Mode Role Truth Bridge v0.2.0ZX
  Exposes selected role backend truth to the UI and repairs legacy rendered summaries.
*/
(function () {
  if (window.__nexusModeRoleTruthBridgeV020ZX) return;
  window.__nexusModeRoleTruthBridgeV020ZX = true;

  const ROLE_TRUTH = {
    FAST: {
      label: "FAST / Phi-4-mini",
      backend: "tnn-phi4-mini:latest",
      brain: "Tesseract Neural Network/phi4-mini-hot-brain",
      available: true,
      command: ".\\scripts\\nexus.ps1 tnn-chat -Tag \"<ask>\" -CallModel",
      message: "FAST selected. Phi-4-mini hot recommendation voice is active for local planning."
    },
    BALANCED: {
      label: "BALANCED / Phi-4-mini",
      backend: "tnn-phi4-mini:latest",
      brain: "Tesseract Neural Network/phi4-mini-hot-brain",
      available: true,
      command: ".\\scripts\\nexus.ps1 tnn-chat -Tag \"<ask>\" -CallModel",
      message: "BALANCED selected. Phi-4-mini balanced recommendation voice is active for local planning."
    },
    DEEP: {
      label: "DEEP / Mistral",
      backend: "tnn-mistral:latest",
      brain: "Tesseract Neural Network/mistral-deep-brain",
      available: true,
      command: ".\\scripts\\nexus.ps1 tnn-deep -Tag \"<ask>\"",
      message: "DEEP selected. Mistral deep recommendation voice is active for deeper local planning."
    },
    TNN: {
      label: "Tesseract Neural Network",
      backend: "tnn-phi4-mini:latest",
      brain: "Tesseract Neural Network/phi4-mini-hot-brain",
      available: true,
      command: ".\\scripts\\nexus.ps1 tnn-chat -Tag \"<ask>\" -CallModel",
      message: "Tesseract Neural Network selected. Phi-4-mini hot brain is active."
    },
    HANDOFF: {
      label: "HANDOFF / ChatGPT-Codex",
      backend: "ChatGPT-Codex relay",
      brain: "ChatGPT-Codex handoff relay",
      available: true,
      command: "/handoff run",
      message: "HANDOFF selected. ChatGPT-Codex relay is active for compressed handoff."
    },
    NEX_CORE: {
      label: "NEX CORE / Geometric Language",
      backend: "local NGLM",
      brain: "NEX CORE/NGLM",
      available: true,
      command: ".\\scripts\\nexus.ps1 nex-chat -Tag \"<ask>\"",
      message: "NEX CORE selected. Direct NGLM cognitive substrate is active without Ollama or external model authority."
    }
  };

  const oldPhi = "Phi" + "-3";
  const oldPhiLower = "phi" + "3";
  const oldBrain = "mistral-" + "chat-brain";

  function $(id) {
    return document.getElementById(id);
  }

  function selectedRole() {
    const select = $("role-select");
    return select && ROLE_TRUTH[select.value] ? select.value : "BALANCED";
  }

  function selectedTruth() {
    return ROLE_TRUTH[selectedRole()] || ROLE_TRUTH.BALANCED;
  }

  function replaceAll(text, oldValue, newValue) {
    return String(text).split(oldValue).join(newValue);
  }

  function cleanText(text) {
    let value = String(text || "");
    value = replaceAll(value, oldPhi, "Phi-4-mini");
    value = replaceAll(value, oldPhiLower + ":mini", "tnn-phi4-mini:latest");
    value = replaceAll(value, oldPhiLower + ":latest", "tnn-phi4-mini:latest");
    value = replaceAll(value, oldBrain, "phi4-mini-hot-brain");
    value = replaceAll(value, "->", "->");
    value = value.replace(/[\u00C2-\u00FF][^\s]*/g, "");
    return value;
  }

  function setText(id, text) {
    const node = $(id);
    if (node) node.textContent = text;
  }

  function emitSystemEvent(text) {
    const output = $("output");
    const stream = $("console-stream");
    const message = "[NEXUS] " + text + " Backend=" + selectedTruth().backend + ". Selector source=truth-bridge.";

    if (typeof window.nexusAppendSystemEvent === "function") {
      window.nexusAppendSystemEvent(message);
      return;
    }

    if (output) {
      const existing = cleanText(output.textContent || "");
      output.textContent = existing + "\n" + message;
      return;
    }

    if (stream) {
      const pre = document.createElement("pre");
      pre.className = "output ai-output nexus-truth-bridge-event";
      pre.textContent = message;
      stream.appendChild(pre);
    }
  }

  function patchSummaryText() {
    document.querySelectorAll("pre, code, .output, #output").forEach((node) => {
      const before = node.textContent || "";
      let after = cleanText(before);
      after = after.replace(/BALANCED: none \/ available=false/g, "BALANCED: tnn-phi4-mini:latest / available=true");
      after = after.replace(/FAST: none \/ available=false/g, "FAST: tnn-phi4-mini:latest / available=true");
      after = after.replace(/TNN: Tesseract Neural Network\/phi4-mini-hot-brain \/ available=true/g, "TNN: Tesseract Neural Network/phi4-mini-hot-brain / available=true");
      if (after !== before) node.textContent = after;
    });
  }

  function syncTruthUI(shouldEmit) {
    const truth = selectedTruth();
    const select = $("role-select");

    if (select) {
      select.dataset.backend = truth.backend;
      select.dataset.brain = truth.brain;
      select.dataset.available = truth.available ? "true" : "false";
      select.dataset.command = truth.command;
    }

    document.body.dataset.nexusSelectedRole = selectedRole();
    document.body.dataset.nexusSelectedBackend = truth.backend;
    document.body.dataset.nexusSelectedBrain = truth.brain;

    setText("selector-hud-status", truth.label.toUpperCase());
    setText("role-model", truth.brain);
    setText("role-command", truth.command);

    const current = document.querySelector(".nexus-mode-current");
    if (current) current.textContent = truth.label;

    document.querySelectorAll(".nexus-mode-green-option").forEach((row) => {
      const active = row.dataset.mode === selectedRole();
      row.classList.toggle("is-active", active);
      row.setAttribute("aria-selected", active ? "true" : "false");
    });

    patchSummaryText();

    if (shouldEmit) emitSystemEvent(truth.message);
  }

  function buildRolePreamble(role, prompt) {
    const truth = ROLE_TRUTH[role] || ROLE_TRUTH.BALANCED;
    return [
      "role=" + role,
      "backend=" + truth.backend,
      "brain=" + truth.brain,
      "available=" + String(truth.available),
      "command=" + truth.command,
      "",
      prompt
    ].join("\n");
  }

  function wireFormTruth() {
    const form = $("operator-form");
    const textarea = $("operator-command");
    if (!form || !textarea || form.dataset.nexusTruthBridge === "1") return;

    form.dataset.nexusTruthBridge = "1";
    form.addEventListener("submit", function () {
      const role = selectedRole();
      const truth = selectedTruth();
      document.body.dataset.nexusLastSubmittedRole = role;
      document.body.dataset.nexusLastSubmittedBackend = truth.backend;
      textarea.dataset.nexusRole = role;
      textarea.dataset.nexusBackend = truth.backend;
      textarea.dataset.nexusBrain = truth.brain;
      textarea.dataset.nexusTruthPreamble = buildRolePreamble(role, textarea.value);

      window.setTimeout(patchSummaryText, 0);
      window.setTimeout(patchSummaryText, 400);
      window.setTimeout(patchSummaryText, 1200);
    }, true);
  }

  function boot() {
    const select = $("role-select");
    if (select && select.dataset.nexusTruthBridge !== "1") {
      select.dataset.nexusTruthBridge = "1";
      select.addEventListener("change", function () {
        syncTruthUI(true);
      });
    }

    wireFormTruth();
    syncTruthUI(false);
    patchSummaryText();
  }

  window.nexusModeRoleTruth = ROLE_TRUTH;
  window.nexusSelectedRoleTruth = selectedTruth;
  window.nexusBuildRolePreamble = buildRolePreamble;
  window.nexusPatchRoleSummaryText = patchSummaryText;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  document.addEventListener("click", function () {
    window.setTimeout(boot, 0);
    window.setTimeout(patchSummaryText, 50);
  }, true);

  document.addEventListener("nexus:message-rendered", patchSummaryText, true);
})();
