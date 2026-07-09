/*
  NEXUS GATE - Conversation Output Bridge v0.2.1F
  Consolidated transcript-aware normal chat repair.
*/
(function () {
  if (window.__nexusConversationOutputBridgeV021F) return;
  window.__nexusConversationOutputBridgeV021F = true;

  const CHAT_BRIDGE_VERSION = "0.2.1F";

  function $(id) {
    return document.getElementById(id);
  }

  function transcriptText() {
    const nodes = Array.from(document.querySelectorAll("#output, #console-stream, .output, pre.ai-output, pre, body"));
    return nodes.map(function (n) { return String(n.textContent || ""); }).join("\n").slice(-12000);
  }

  function inferRoleFromTranscript() {
    const text = transcriptText();
    const matches = Array.from(text.matchAll(/role\s*=\s*(FAST|BALANCED|DEEP|TNN|HANDOFF)/gi));
    if (matches.length) return matches[matches.length - 1][1].toUpperCase();
    return "";
  }

  function selectedRole() {
    const explicit = document.body && document.body.dataset ? document.body.dataset.nexusLastSubmittedRole : "";
    const inferred = inferRoleFromTranscript();
    const select = $("role-select");
    return explicit || inferred || (select && select.value) || "BALANCED";
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

  function inferPromptFromTranscript() {
    const text = transcriptText();
    const roleBlock = /HUMAN\s*\n\s*role\s*=\s*(?:FAST|BALANCED|DEEP|TNN|HANDOFF)\s*\n([\s\S]*?)(?=\n\s*NEX\b|\n\s*YOU\b|\n\s*HUMAN\b|$)/gi;
    let match;
    let last = "";
    while ((match = roleBlock.exec(text)) !== null) {
      const candidate = String(match[1] || "")
        .split(/\n/)
        .map(function (line) { return line.trim(); })
        .filter(Boolean)
        .filter(function (line) { return !/^role\s*=/.test(line); })
        .join(" ")
        .trim();
      if (candidate) last = candidate;
    }

    if (last) return last;

    const humanLines = Array.from(text.matchAll(/(?:YOU|HUMAN)\s*\n([\s\S]{0,220}?)(?=\n\s*NEX\b|$)/gi));
    if (humanLines.length) {
      const raw = humanLines[humanLines.length - 1][1] || "";
      return raw.split(/\n/).map(function (line) { return line.trim(); }).filter(Boolean).pop() || "";
    }

    return "";
  }

  function currentHumanPrompt() {
    const box = $("operator-command");
    const live = box ? String(box.value || box.textContent || "").trim() : "";
    const stored = document.body && document.body.dataset ? String(document.body.dataset.nexusLastHumanPrompt || "").trim() : "";
    const inferred = inferPromptFromTranscript();
    return live || stored || inferred || "";
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
    return (hasObservation && hasRecommendation) || (hasRecommendation && hasRisk) || (hasObservation && hasRisk) || hasHumanAuth;
  }

  function looksLikeStaleEngineeringMove(text) {
    const value = String(text || "");
    if (/next safe engineering move/i.test(value)) return true;
    if (/NexusGate product development/i.test(value) && /code review/i.test(value)) return true;
    if (/Update the documentation/i.test(value) && /automated tests/i.test(value)) return true;
    if (/Conduct a code review/i.test(value) && /critical functionalities/i.test(value)) return true;
    return false;
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

  function patchNode(node) {
    if (!node) return;
    const before = String(node.textContent || "");
    if (!before) return;

    const prompt = currentHumanPrompt();
    const simple = isSimpleHumanChat(prompt);
    const audit = looksLikeAuditCard(before);

    // If the user is chatting normally, don't let audit-card formatting leak through.
    if (simple && audit) {
      const after = conversationalizeAudit(before, prompt);
      if (after && after.trim() && after.trim() !== before.trim()) {
        node.textContent = after;
        node.dataset.nexusConversationBridge = CHAT_BRIDGE_VERSION;
      }
      return;
    }

    // For truly stale canned engineering moves in response to simple chat, replace with a greeting.
    if (simple && looksLikeStaleEngineeringMove(before)) {
      const after = naturalGreeting(prompt || "you there");
      if (after && after !== before) {
        node.textContent = after;
        node.dataset.nexusConversationBridge = CHAT_BRIDGE_VERSION;
      }
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
    if (!form || !input || form.dataset.nexusConversationBridgeV021F === "1") return;

    form.dataset.nexusConversationBridgeV021F = "1";
    form.addEventListener("submit", function () {
      const prompt = String(input.value || "").trim();
      document.body.dataset.nexusLastHumanPrompt = prompt;
      document.body.dataset.nexusChatIntent = isSimpleHumanChat(prompt) ? "conversation" : "operator";
      document.body.dataset.nexusLastSubmittedRole = (document.getElementById("role-select") || {}).value || selectedRole();

      [0, 75, 150, 350, 900, 1800, 3000, 5000].forEach(function (ms) {
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
    inferPromptFromTranscript: inferPromptFromTranscript,
    inferRoleFromTranscript: inferRoleFromTranscript,
    isSimpleHumanChat: isSimpleHumanChat,
    isOperatorCommand: isOperatorCommand,
    looksLikeAuditCard: looksLikeAuditCard,
    looksLikeStaleEngineeringMove: looksLikeStaleEngineeringMove,
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
,
    looksLikeStaleEngineeringMove: looksLikeStaleEngineeringMove,
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
