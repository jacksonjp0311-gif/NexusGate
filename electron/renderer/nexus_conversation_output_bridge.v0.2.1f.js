/*
  NEXUS GATE - Conversation Output Bridge v0.2.1F
  Keeps casual chat conversational while preserving operator/gate outputs.
*/
(function () {
  if (window.__nexusConversationOutputBridgeV021F) return;
  window.__nexusConversationOutputBridgeV021F = true;

  const CHAT_BRIDGE_VERSION = "0.2.1F";
  const ROLES = ["FAST", "BALANCED", "DEEP", "TNN", "HANDOFF"];

  function $(id) {
    return document.getElementById(id);
  }

  function transcriptText() {
    const nodes = Array.from(document.querySelectorAll("#console-stream .chat-message, #output"));
    return nodes.map((node) => String(node.textContent || "")).join("\n").slice(-12000);
  }

  function selectedRole() {
    const explicit = document.body?.dataset?.nexusLastSubmittedRole || "";
    const select = $("role-select");
    const selected = select && ROLES.includes(select.value) ? select.value : "";
    return explicit || selected || "BALANCED";
  }

  function roleLabel(role = selectedRole()) {
    if (role === "FAST") return "FAST / Phi-4-mini";
    if (role === "BALANCED") return "BALANCED / Phi-4-mini";
    if (role === "DEEP") return "DEEP / Mistral";
    if (role === "TNN") return "Tesseract Neural Network";
    if (role === "HANDOFF") return "HANDOFF / ChatGPT-Codex";
    return "NEX";
  }

  function inferPromptFromTranscript() {
    const messages = Array.from(document.querySelectorAll("#console-stream .human-message pre"));
    const last = messages[messages.length - 1];
    return String(last?.textContent || "").trim();
  }

  function currentHumanPrompt() {
    const box = $("operator-command");
    const live = String(box?.value || "").trim();
    const stored = String(document.body?.dataset?.nexusLastHumanPrompt || "").trim();
    return live || stored || inferPromptFromTranscript();
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
    if (!value || isOperatorCommand(value)) return false;
    if (/^(hey|hi|hello|yo|sup|you there|are you there|u there|ping|testing|test|what's up|whats up)\??!?$/i.test(value)) return true;
    if (/^(what do you think|thoughts|help me|can you|tell me|explain|walk me through|talk to me)/i.test(value)) return true;
    return value.length <= 260;
  }

  function looksLikeAuditCard(text) {
    const value = String(text || "");
    const sections = ["Observation", "Recommendation", "Risk", "Human Authorization"]
      .filter((name) => new RegExp("(^|\\n)\\s*" + name + "\\s*:", "i").test(value));
    return sections.length >= 2;
  }

  function looksLikeStaleEngineeringMove(text) {
    const value = String(text || "");
    return /next safe engineering move/i.test(value)
      || (/NexusGate product development/i.test(value) && /code review/i.test(value))
      || (/Conduct a code review/i.test(value) && /automated test suite/i.test(value));
  }

  function naturalGreeting(prompt, role = selectedRole()) {
    const p = String(prompt || "").trim().toLowerCase();
    if (/^(you there|are you there|u there|ping|testing|test)\??!?$/.test(p)) {
      return "Yeah, I'm here. " + roleLabel(role) + " is active. Send me what you want to work on.";
    }
    if (/^(hey|hi|hello|yo|sup|what's up|whats up)\??!?$/.test(p)) {
      return "Hey, I'm here. " + roleLabel(role) + " is active. What are we working on?";
    }
    return "I'm here. " + roleLabel(role) + " is active. Talk to me normally, or use /run when you want a governed lane.";
  }

  function conversationalizeAudit(text, prompt, role = selectedRole()) {
    if (looksLikeStaleEngineeringMove(text)) return naturalGreeting(prompt, role);
    const firstRecommendation = String(text || "")
      .split(/\r?\n/)
      .map((line) => line.replace(/^\s*[-*\d.]+\s*/, "").trim())
      .find((line) => line && !/^(Observation|Recommendation|Risk|Human Authorization)\s*:?$/i.test(line));
    if (!firstRecommendation) return naturalGreeting(prompt, role);
    return [
      "I'm here. " + roleLabel(role) + " is active.",
      firstRecommendation,
      "Boundary: recommendation-only unless you explicitly run a governed lane."
    ].join("\n");
  }

  function patchNode(node) {
    if (!node) return;
    const before = String(node.textContent || "");
    if (!before.trim()) return;
    const prompt = currentHumanPrompt();
    if (!isSimpleHumanChat(prompt)) return;

    let after = before;
    if (looksLikeAuditCard(before)) after = conversationalizeAudit(before, prompt);
    if (looksLikeStaleEngineeringMove(after)) after = naturalGreeting(prompt);

    if (after.trim() !== before.trim()) {
      node.textContent = after;
      node.dataset.nexusConversationBridge = CHAT_BRIDGE_VERSION;
    }
  }

  function patchOutput() {
    document.querySelectorAll("#console-stream .ai-message .message-body pre, #output").forEach(patchNode);
  }

  function annotatePromptIntent() {
    const form = $("operator-form");
    const input = $("operator-command");
    if (!form || !input || form.dataset.nexusConversationBridgeV021F === "1") return;
    form.dataset.nexusConversationBridgeV021F = "1";
    form.addEventListener("submit", function () {
      const prompt = String(input.value || "").trim();
      document.body.dataset.nexusLastHumanPrompt = prompt;
      document.body.dataset.nexusChatIntent = isSimpleHumanChat(prompt) ? "conversation" : "operator";
      document.body.dataset.nexusLastSubmittedRole = $("role-select")?.value || selectedRole();
      [0, 60, 160, 420, 900, 1800].forEach((ms) => window.setTimeout(patchOutput, ms));
    }, true);
  }

  function boot() {
    annotatePromptIntent();
    patchOutput();
  }

  window.nexusConversationOutputBridge = {
    version: CHAT_BRIDGE_VERSION,
    isSimpleHumanChat,
    isOperatorCommand,
    looksLikeAuditCard,
    looksLikeStaleEngineeringMove,
    conversationalizeAudit,
    patchOutput
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  document.addEventListener("nexus:message-rendered", function () {
    window.setTimeout(patchOutput, 0);
    window.setTimeout(patchOutput, 120);
  }, true);

  const observer = new MutationObserver(() => patchOutput());
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
