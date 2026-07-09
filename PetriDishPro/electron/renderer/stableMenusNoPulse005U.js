(() => {
  "use strict";

  const SEAL = "PETRI_005U_STABLE_MENUS_NO_PULSE";
  let lastOrganismSignature = "";
  let lastDrugSignature = "";
  let lastTopSignature = "";

  function norm(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function upper(value) {
    return norm(value).toUpperCase();
  }

  function slug(value) {
    return norm(value).toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
  }

  function isTopButton(button) {
    const t = upper(button.textContent);
    return (
      t === "CAPTURE" ||
      t === "DRUG LAB" ||
      t === "RUN" ||
      t === "PAUSE" ||
      t === "RESET" ||
      t === "STATE" ||
      t.includes("DRUG LAB")
    );
  }

  function topRank(button) {
    const t = upper(button.textContent);
    if (t === "CAPTURE") return 1;
    if (t.includes("DRUG")) return 2;
    if (t === "RUN" || t === "PAUSE") return 3;
    if (t === "RESET") return 4;
    if (t === "STATE") return 5;
    return 99;
  }

  function normalizeTopLabel(button) {
    const t = upper(button.textContent);
    if (t.includes("DRUG")) button.textContent = "Drug Lab";
    if (t === "CAPTURE") button.textContent = "Capture";
    if (t === "RUN") button.textContent = "Run";
    if (t === "PAUSE") button.textContent = "Pause";
    if (t === "RESET") button.textContent = "Reset";
    if (t === "STATE") button.textContent = "State";
  }

  function repairTopControlsStable() {
    const buttons = Array.from(document.querySelectorAll("button")).filter(isTopButton);
    if (buttons.length < 4) return;

    buttons.forEach(normalizeTopLabel);
    const sorted = buttons.slice().sort((a, b) => topRank(a) - topRank(b));
    const pod = sorted[0].parentElement;
    if (!pod) return;

    const signature = sorted.map(b => norm(b.textContent)).join("|");
    pod.id = "petri-005u-top-control-pod";
    pod.classList.add("petri-005u-top-control-pod");
    pod.dataset.seal005u = SEAL;

    if (pod.parentElement) {
      pod.parentElement.classList.add("petri-005u-top-control-shell");
    }

    sorted.forEach(button => {
      button.classList.add("petri-005u-control-button");
      button.classList.remove("petri-005u-control-button-drug");
      if (upper(button.textContent) === "DRUG LAB") {
        button.classList.add("petri-005u-control-button-drug");
      }
      button.dataset.seal005u = SEAL;
    });

    if (signature !== lastTopSignature) {
      sorted.forEach(button => {
        if (button.parentElement === pod) pod.appendChild(button);
      });
      lastTopSignature = signature;
    }
  }

  function textHeader(needle) {
    const target = upper(needle);
    return Array.from(document.querySelectorAll("h1,h2,h3,h4,div,span,section,article"))
      .find(el => upper(el.textContent) === target || upper(el.textContent).startsWith(target));
  }

  function organismHost() {
    const header = textHeader("ORGANISM CARDS");
    if (!header) return null;
    return header.closest("section,article,div") || header.parentElement;
  }

  function organismCards(host) {
    if (!host) return [];
    const boxes = Array.from(host.querySelectorAll('input[type="checkbox"]'));
    const cards = boxes.map(box => box.closest("div,article,section,li"));
    return cards
      .filter(Boolean)
      .filter((el, i, arr) => arr.indexOf(el) === i)
      .filter(card => /[A-Za-z]/.test(card.textContent || ""));
  }

  function drugHudHost() {
    const nodes = Array.from(document.querySelectorAll(".petri-005s-drug-red-hud, #petri-005q-drug-hud, [id*='drug'], [class*='drug'], [id*='Drug'], [class*='Drug']"));
    return nodes.find(el => {
      const text = upper(el.textContent);
      const r = el.getBoundingClientRect();
      return r.width > 260 && r.height > 120 && text.includes("DRUG") && (text.includes("LAB") || text.includes("LIBRARY") || text.includes("TARGET"));
    }) || null;
  }

  function drugCards(host) {
    if (!host) return [];
    const nodes = Array.from(host.querySelectorAll("button,article,section,div"));
    const out = [];
    nodes.forEach(el => {
      const text = upper(el.textContent);
      const r = el.getBoundingClientRect();
      const looksDrug = text.includes("AMPICILLIN") || text.includes("CIPRO") || text.includes("GENTAMICIN") ||
        text.includes("TOBRAMYCIN") || text.includes("VANCOMYCIN") || text.includes("TETRACYCLINE") ||
        text.includes("ERYTHROMYCIN") || text.includes("RIFAMPICIN") || text.includes("FLUCONAZOLE") ||
        text.includes("AMPHOTERICIN") || text.includes("LPS") || text.includes("GLUCAN");
      if (looksDrug && r.height > 22 && r.width > 80 && out.indexOf(el) < 0) out.push(el);
    });
    return out;
  }

  function labelFor(card, fallback, index) {
    const named = card.querySelector("h1,h2,h3,h4,strong,b,.title,.name,.card-title,.panel-title") || card;
    const bits = norm(named.textContent).split(" ").slice(0, 6);
    const text = bits.join(" ");
    return text || `${fallback} ${index + 1}`;
  }

  function ensureSelector(host, role, label, placeholder, items, previousSignature) {
    if (!host || !items.length) return previousSignature;

    const signature = items.map(item => item.id + ":" + item.label).join("|");
    let row = host.querySelector(`.petri-005u-selector-row[data-role="${role}"]`);

    if (row && row.dataset.signature === signature) {
      return signature;
    }

    if (!row) {
      row = document.createElement("div");
      row.className = "petri-005u-selector-row";
      row.dataset.role = role;

      const lab = document.createElement("label");
      lab.className = "petri-005u-selector-label";
      lab.textContent = label;

      const select = document.createElement("select");
      select.className = "petri-005u-selector-select";

      row.appendChild(lab);
      row.appendChild(select);
      host.prepend(row);
    }

    row.dataset.signature = signature;

    const select = row.querySelector("select");
    const activeValue = select.value;
    select.innerHTML = "";

    const lead = document.createElement("option");
    lead.value = "";
    lead.textContent = placeholder;
    select.appendChild(lead);

    items.forEach(item => {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.label;
      select.appendChild(option);
    });

    if (items.some(item => item.id === activeValue)) select.value = activeValue;

    if (!select.dataset.bound005u) {
      select.dataset.bound005u = "true";
      select.addEventListener("change", () => {
        const hit = items.find(item => item.id === select.value);
        if (!hit || !hit.element) return;
        hit.element.scrollIntoView({ behavior: "smooth", block: "nearest" });
        hit.element.classList.add("petri-005u-selected-card");
        setTimeout(() => hit.element.classList.remove("petri-005u-selected-card"), 850);

        if (role === "organism-menu") {
          const box = hit.element.querySelector('input[type="checkbox"]');
          if (box && !box.checked) box.click();
        }

        if (role === "drug-menu") {
          const clickable = hit.element.matches("button") ? hit.element : hit.element.querySelector("button");
          if (clickable) clickable.click();
        }
      });
    }

    return signature;
  }

  function installOrganismMenuStable() {
    const host = organismHost();
    const cards = organismCards(host);
    const items = cards.map((card, index) => ({
      id: card.dataset.cardId || slug(labelFor(card, "Organism", index)),
      label: labelFor(card, "Organism", index),
      element: card
    })).filter(item => item.label);

    lastOrganismSignature = ensureSelector(
      host,
      "organism-menu",
      "Organisms",
      "Select organism card",
      items,
      lastOrganismSignature
    ) || lastOrganismSignature;

    return items.length;
  }

  function installDrugMenuStable() {
    const host = drugHudHost();
    const cards = drugCards(host);
    const items = cards.map((card, index) => ({
      id: card.dataset.drugId || slug(labelFor(card, "Drug", index)),
      label: labelFor(card, "Drug", index),
      element: card
    })).filter(item => item.label);

    lastDrugSignature = ensureSelector(
      host,
      "drug-menu",
      "Drug cards",
      "Select drug card",
      items,
      lastDrugSignature
    ) || lastDrugSignature;

    return items.length;
  }

  function killPulseClasses() {
    document.querySelectorAll(".petri-005t-flash").forEach(el => el.classList.remove("petri-005t-flash"));
  }

  function applyStableUi() {
    killPulseClasses();
    repairTopControlsStable();
    const organismCount = installOrganismMenuStable();
    const drugCount = installDrugMenuStable();

    window.PETRI_005U_STABLE_UI = {
      seal: SEAL,
      organism_menu_count: organismCount,
      drug_menu_count: drugCount,
      claim_boundary: "UI stability and selector-shell only."
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyStableUi, { once: true });
  } else {
    applyStableUi();
  }

  // Short bootstrap only. 005T pulsed because it rebuilt every cycle forever.
  let ticks = 0;
  const timer = setInterval(() => {
    ticks += 1;
    applyStableUi();
    if (ticks >= 6) clearInterval(timer);
  }, 500);

  const observer = new MutationObserver(() => {
    window.clearTimeout(window.__petri005uDebounce);
    window.__petri005uDebounce = window.setTimeout(applyStableUi, 180);
  });
  observer.observe(document.body, { childList: true, subtree: true });
})();
