/*
  NEXUS GATE - Conversation Output Bridge v0.2.1B
  Stronger normal-chat bridge for partial audit cards and stale engineering-context replies.
*/
(function () {
  if (window.__nexusConversationOutputBridgeV021B) return;
  window.__nexusConversationOutputBridgeV021B = true;

  const CHAT_BRIDGE_VERSION = "0.2.1B";

  function $(id) {
    return document.getElementById(id);
  }

  function selectedRole() {
    const explicit = document.body && document.body.dataset ? document.body.dataset.nexusLastSubmittedRole : "";
    const select = $("role-select");
    return explicit || (select && select.value) || "BALANCED";
  }

  function roleLabel() {
    const role = selectedRole();
    if (role === "FAST") return "FAST / Phi-4-mini";
    if (role === "BALANCED") return "BALANCED / Phi-4-mini";
    if (role === "DEEP") return "DEEP / Mistral";
    if (role === "TNN") return "Tesseract Neural Network";
    if (role === "HANDOFF") return "HANDOFF / ChatGPT-Codex";
    return role || "NEX";
  }

  function currentHumanPrompt() {
    const box = $("operator-command");
    if (!box) return document.body.dataset.nexusLastHumanPrompt || "";
    return String(box.value || box.textContent || document.body.dataset.nexusLastHumanPrompt || "").trim();
  }

  function isOperatorCommand(text) {
    const value = String(text || "").trim();
    if (!value) return false;
    if (value.startsWith("/")) return true;
    if (/^(run|status|evolve|reflect|feedback|interconnect|handoff|git|commit|push|pull|shell|powershell|python|npm|node)\b/i.test(value)) return true;
    if (/\b(commit|push|delete|mutate|execute|run script|apply patch|write file|stage files|repo mutation)\b/i.test(value)) return true;
    return false;
  }

  function isSimpleHumanChat(text) {
    const value = String(text || "").trim();
    if (!value) return false;
    if (isOperatorCommand(value)) return false;
    if (/^(hey|hi|hello|yo|sup|you there|are you there|u there|ping|testing|test|what's up|whats up)\??!?$/i.test(value)) return true;
    if (/^(what do you think|thoughts|help me|can you|tell me|explain|walk me through|talk to me)/i.test(value)) return true;
    if (value.length <= 260) return true;
    return false;
  }

  function looksLikeAuditCard(text) {
    const value = String(text || "");
    const hasObservation = /(^|\n)\s*Observation\s*:/i.test(value);
    const hasRecommendation = /(^|\n)\s*Recommendation\s*:/i.test(value);
    const hasRisk = /(^|\n)\s*Risk\s*:/i.test(value);
    const hasHumanAuth = /(^|\n)\s*Human Authorization\s*:/i.test(value);
    return (hasObservation && hasRecommendation) || (hasRecommendation && hasRisk) || (hasObservation && hasRisk && hasHumanAuth);
  }

  function looksLikeStaleEngineeringMove(text, prompt) {
    const value = String(text || "");
    const p = String(prompt || "").trim().toLowerCase();
    if (!isSimpleHumanChat(p)) return false;
    if (/next safe engineering move/i.test(value)) return true;
    if (/NexusGate product development/i.test(value) && /code review/i.test(value)) return true;
    if (/Update the automated test suite/i.test(value) && /Enhance UX documentation/i.test(value)) return true;
    return false;
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

  function naturalGreeting(prompt) {
    const p = String(prompt || "").trim().toLowerCase();
    if (/^(you there|are you there|u there|ping|testing|test)\??!?$/.test(p)) {
      return "Yeah - I'm here. " + roleLabel() + " is active. Send me what you want to work on.";
    }
    if (/^(hey|hi|hello|yo|sup|what's up|whats up)\??!?$/.test(p)) {
      return "Hey - I'm here. " + roleLabel() + " is active. What are we working on?";
    }
    return "I'm here. " + roleLabel() + " is active. Talk to me normally unless you want me to run a system action.";
  }

  function conversationalizeAudit(text, prompt) {
    const fields = parseAuditCard(text);
    const p = String(prompt || "").trim();

    if (looksLikeStaleEngineeringMove(text, p)) {
      return naturalGreeting(p);
    }

    if (/^(hey|hi|hello|yo|sup|you there|are you there|u there|ping|testing|test|what's up|whats up)\??!?$/i.test(p)) {
      return naturalGreeting(p);
    }

    if (fields.Recommendation) {
      let reply = fields.Recommendation;
      reply = reply.replace(/^Respond with\s+/i, "");
      reply = reply.replace(/^a friendly greeting\.?$/i, naturalGreeting(p));
      reply = reply.replace(/^1\.\s*/m, "");
      if (reply.length < 12 || /code review|automated test suite|UX documentation/i.test(reply)) {
        reply = naturalGreeting(p);
      }
      return reply;
    }

    return naturalGreeting(p);
  }

  function patchNode(node) {
    if (!node) return;
    const before = String(node.textContent || "");
    if (!before) return;

    const prompt = currentHumanPrompt();
    if (!isSimpleHumanChat(prompt)) return;

    const shouldPatch = looksLikeAuditCard(before) || looksLikeStaleEngineeringMove(before, prompt);
    if (!shouldPatch) return;

    const after = conversationalizeAudit(before, prompt);
    if (after && after !== before) {
      node.textContent = after;
      node.dataset.nexusConversationBridge = CHAT_BRIDGE_VERSION;
    }
  }

  function patchOutput() {
    document.querySelectorAll("#output, .output, pre.ai-output, pre").forEach(patchNode);
  }

  function suppressMismatchedSelectorEvents() {
    document.querySelectorAll("#output, .output, pre.ai-output, pre").forEach(function (node) {
      const text = String(node.textContent || "");
      if (!text) return;
      const role = selectedRole();
      if (!role) return;

      const lines = text.split(/\n/).filter(function (line) {
        if (!line.includes("[NEXUS]") || !line.includes("selected.") || !line.includes("Selector source=select")) return true;
        if (role === "FAST" && line.includes("FAST selected.")) return true;
        if (role === "BALANCED" && line.includes("BALANCED selected.")) return true;
        if (role === "DEEP" && line.includes("DEEP selected.")) return true;
        if (role === "TNN" && line.includes("Tesseract Neural Network selected.")) return true;
        if (role === "HANDOFF" && line.includes("HANDOFF selected.")) return true;
        return false;
      });

      const next = lines.join("\n").trim();
      if (next !== text.trim()) node.textContent = next;
    });
  }

  function annotatePromptIntent() {
    const form = $("operator-form");
    const input = $("operator-command");
    if (!form || !input || form.dataset.nexusConversationBridgeV021B === "1") return;

    form.dataset.nexusConversationBridgeV021B = "1";
    form.addEventListener("submit", function () {
      const prompt = String(input.value || "").trim();
      document.body.dataset.nexusLastHumanPrompt = prompt;
      document.body.dataset.nexusChatIntent = isSimpleHumanChat(prompt) ? "conversation" : "operator";
      document.body.dataset.nexusLastSubmittedRole = (document.getElementById("role-select") || {}).value || selectedRole();

      [0, 150, 350, 900, 1800, 3000].forEach(function (ms) {
        window.setTimeout(function () {
          suppressMismatchedSelectorEvents();
          patchOutput();
        }, ms);
      });
    }, true);
  }

  function boot() {
    annotatePromptIntent();
    suppressMismatchedSelectorEvents();
    patchOutput();
  }

  window.nexusConversationOutputBridge = {
    version: CHAT_BRIDGE_VERSION,
    isSimpleHumanChat: isSimpleHumanChat,
    isOperatorCommand: isOperatorCommand,
    looksLikeAuditCard: looksLikeAuditCard,
    looksLikeStaleEngineeringMove: looksLikeStaleEngineeringMove,
    conversationalizeAudit: conversationalizeAudit,
    patchOutput: patchOutput,
    suppressMismatchedSelectorEvents: suppressMismatchedSelectorEvents
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  document.addEventListener("nexus:message-rendered", function () {
    window.setTimeout(function () {
      suppressMismatchedSelectorEvents();
      patchOutput();
    }, 0);
  }, true);

  document.addEventListener("click", function () {
    window.setTimeout(boot, 0);
  }, true);

  const observer = new MutationObserver(function () {
    suppressMismatchedSelectorEvents();
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