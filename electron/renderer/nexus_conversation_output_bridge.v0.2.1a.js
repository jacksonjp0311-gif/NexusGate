/*
  NEXUS GATE - Conversation Output Bridge v0.2.1A
  Normal chat should feel like chat. Operator/system tasks keep governance.
*/
(function () {
  if (window.__nexusConversationOutputBridgeV021A) return;
  window.__nexusConversationOutputBridgeV021A = true;

  const CHAT_BRIDGE_VERSION = "0.2.1A";

  function $(id) {
    return document.getElementById(id);
  }

  function selectedRole() {
    const explicit = document.body && document.body.dataset ? document.body.dataset.nexusLastSubmittedRole : "";
    const select = $("role-select");
    return explicit || (select && select.value) || "BALANCED";
  }

  function isOperatorCommand(text) {
    const value = String(text || "").trim();
    if (!value) return false;
    if (value.startsWith("/")) return true;
    if (/^(run|status|evolve|reflect|feedback|interconnect|handoff|git|commit|push|pull|shell|powershell|python|npm|node)\b/i.test(value)) return true;
    if (/\b(commit|push|delete|mutate|execute|run script|apply patch|write file|stage files)\b/i.test(value)) return true;
    return false;
  }

  function isSimpleHumanChat(text) {
    const value = String(text || "").trim();
    if (!value) return false;
    if (isOperatorCommand(value)) return false;
    if (value.length <= 220) return true;
    if (/^(hey|hi|hello|yo|sup|what do you think|thoughts|help me|can you|tell me|explain)/i.test(value)) return true;
    return false;
  }

  function currentHumanPrompt() {
    const box = $("operator-command");
    if (!box) return "";
    return String(box.value || box.textContent || "").trim();
  }

  function roleLabel() {
    const role = selectedRole();
    if (role === "FAST") return "FAST / Phi-4-mini";
    if (role === "BALANCED") return "BALANCED / Phi-4-mini";
    if (role === "DEEP") return "DEEP / Mistral";
    if (role === "TNN") return "Tesseract Neural Network";
    if (role === "HANDOFF") return "HANDOFF / ChatGPT-Codex";
    return role;
  }

  function looksLikeAuditCard(text) {
    const value = String(text || "");
    return /Observation:\s*/.test(value) &&
           /Recommendation:\s*/.test(value) &&
           /Risk:\s*/.test(value) &&
           /Human Authorization:\s*/.test(value);
  }

  function parseAuditCard(text) {
    const value = String(text || "");
    const fields = {};
    ["Observation", "Recommendation", "Risk", "Human Authorization"].forEach(function (label) {
      const pattern = new RegExp(label + ":\\s*([\\s\\S]*?)(?=\\n(?:Observation|Recommendation|Risk|Human Authorization):|$)", "i");
      const match = value.match(pattern);
      fields[label] = match ? match[1].trim() : "";
    });
    return fields;
  }

  function conversationalizeAudit(text, prompt) {
    const fields = parseAuditCard(text);
    const p = String(prompt || "").trim().toLowerCase();

    if (/^(hey|hi|hello|yo|sup)\b/.test(p)) {
      return "Hey - I'm here. " + roleLabel() + " is active. What are we working on?";
    }

    if (fields.Recommendation) {
      let reply = fields.Recommendation;
      reply = reply.replace(/^Respond with\s+/i, "");
      reply = reply.replace(/^a friendly greeting\.?$/i, "Hey - I'm here. What do you want to dig into?");
      if (reply.length < 12) reply = "I'm with you. Tell me what you want to work through.";
      return reply;
    }

    return "I'm here. " + roleLabel() + " is active, and we can talk normally unless you ask me to run or change something.";
  }

  function patchNode(node) {
    if (!node) return;
    const before = String(node.textContent || "");
    if (!before) return;

    const prompt = currentHumanPrompt();
    if (!isSimpleHumanChat(prompt)) return;
    if (!looksLikeAuditCard(before)) return;

    const after = conversationalizeAudit(before, prompt);
    if (after && after !== before) {
      node.textContent = after;
      node.dataset.nexusConversationBridge = CHAT_BRIDGE_VERSION;
    }
  }

  function patchOutput() {
    document.querySelectorAll("#output, .output, pre.ai-output, pre").forEach(patchNode);
  }

  function suppressStaleSelectorEvents() {
    document.querySelectorAll("#output, .output, pre.ai-output, pre").forEach(function (node) {
      const text = String(node.textContent || "");
      if (!text) return;
      const role = selectedRole();
      if (role && role !== "FAST" && text.includes("[NEXUS] FAST selected.") && text.includes("Selector source=select")) {
        node.textContent = text
          .split(/\n/)
          .filter(function (line) {
            return !(line.includes("[NEXUS] FAST selected.") && line.includes("Selector source=select"));
          })
          .join("\n")
          .trim();
      }
    });
  }

  function annotatePromptIntent() {
    const form = $("operator-form");
    const input = $("operator-command");
    if (!form || !input || form.dataset.nexusConversationBridge === "1") return;

    form.dataset.nexusConversationBridge = "1";
    form.addEventListener("submit", function () {
      const prompt = String(input.value || "").trim();
      document.body.dataset.nexusChatIntent = isSimpleHumanChat(prompt) ? "conversation" : "operator";
      document.body.dataset.nexusLastSubmittedRole = (document.getElementById("role-select") || {}).value || selectedRole();
      [0, 250, 900, 1800].forEach(function (ms) {
        window.setTimeout(function () {
          suppressStaleSelectorEvents();
          patchOutput();
        }, ms);
      });
    }, true);
  }

  function boot() {
    annotatePromptIntent();
    suppressStaleSelectorEvents();
    patchOutput();
  }

  window.nexusConversationOutputBridge = {
    version: CHAT_BRIDGE_VERSION,
    isSimpleHumanChat: isSimpleHumanChat,
    isOperatorCommand: isOperatorCommand,
    conversationalizeAudit: conversationalizeAudit,
    patchOutput: patchOutput,
    suppressStaleSelectorEvents: suppressStaleSelectorEvents
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  document.addEventListener("nexus:message-rendered", function () {
    window.setTimeout(function () {
      suppressStaleSelectorEvents();
      patchOutput();
    }, 0);
  }, true);

  document.addEventListener("click", function () {
    window.setTimeout(boot, 0);
  }, true);

  const observer = new MutationObserver(function () {
    suppressStaleSelectorEvents();
    patchOutput();
  });

  function observeWhenReady() {
    const target = $("console-stream") || document.body;
    if (target) observer.observe(target, { childList: true, subtree: true, characterData: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", observeWhenReady);
  } else {
    observeWhenReady();
  }
})();