(() => {
  "use strict";

  const SEAL = "PETRI_005T_CONTROL_SPACING_CARD_MENUS";

  function norm(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function upper(value) {
    return norm(value).toUpperCase();
  }

  function slug(value) {
    return norm(value)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_+|_+$/g, "");
  }

  function byText(root, tagList, needle) {
    const tags = Array.isArray(tagList) ? tagList : [tagList];
    const pool = tags.flatMap(tag => Array.from(root.querySelectorAll(tag)));
    return pool.find(el => upper(el.textContent).includes(needle));
  }

  function flash(el) {
    if (!el) return;
    el.classList.add("petri-005t-flash");
    setTimeout(() => el.classList.remove("petri-005t-flash"), 1200);
  }

  function clickCheckboxIn(card) {
    const box = card.querySelector('input[type="checkbox"]');
    if (box && !box.checked) box.click();
  }

  function normalizeButtonLabels(buttons) {
    buttons.forEach(button => {
      const t = upper(button.textContent);
      if (t.includes("DRUG")) button.textContent = "Drug Lab";
      if (t === "CAPTURE") button.textContent = "Capture";
      if (t === "RUN") button.textContent = "Run";
      if (t === "PAUSE") button.textContent = "Pause";
      if (t === "RESET") button.textContent = "Reset";
      if (t === "STATE") button.textContent = "State";
    });
  }

  function controlRank(label) {
    if (label === "CAPTURE") return 1;
    if (label === "DRUG LAB") return 2;
    if (label === "RUN" || label === "PAUSE") return 3;
    if (label === "RESET") return 4;
    if (label === "STATE") return 5;
    return 99;
  }

  function topButtons() {
    return Array.from(document.querySelectorAll("button")).filter(btn => {
      const t = upper(btn.textContent);
      return t === "CAPTURE" || t === "RUN" || t === "PAUSE" || t === "RESET" || t === "STATE" || t === "DRUG LAB" || t.includes("DRUG LAB");
    });
  }

  function repairTopControls() {
    const buttons = topButtons();
    if (buttons.length < 4) return;
    normalizeButtonLabels(buttons);
    const sorted = buttons.slice().sort((a, b) => controlRank(upper(a.textContent)) - controlRank(upper(b.textContent)));
    const pod = sorted[0].parentElement;
    if (!pod) return;

    pod.id = "petri-005t-top-control-pod";
    pod.classList.add("petri-005t-top-control-pod");
    if (pod.parentElement) {
      pod.parentElement.classList.add("petri-005t-top-control-shell");
    }

    sorted.forEach(button => {
      button.classList.add("petri-005t-control-button");
      button.classList.remove("petri-005t-control-button-drug");
      if (upper(button.textContent) === "DRUG LAB") {
        button.classList.add("petri-005t-control-button-drug");
      }
      button.style.removeProperty("width");
      button.style.removeProperty("min-width");
      button.style.removeProperty("max-width");
      button.style.removeProperty("transform");
      button.style.removeProperty("margin");
      button.style.removeProperty("padding");
      if (button.parentElement === pod) pod.appendChild(button);
    });
  }

  function likelyOrganismCards(panel) {
    const nodes = Array.from(panel.querySelectorAll("input[type='checkbox']"));
    const cards = nodes.map(box => box.closest("div, article, section, li"));
    return cards.filter(Boolean).filter((el, i, arr) => arr.indexOf(el) === i).filter(card => /[A-Za-z]/.test(card.textContent || ""));
  }

  function likelyDrugCards(panel) {
    const nodes = Array.from(panel.querySelectorAll("button, div, article, section"));
    const withDrugLook = nodes.filter(el => {
      const t = upper(el.textContent);
      return el.getBoundingClientRect().height > 28 && (t.includes("AMPICILLIN") || t.includes("CIPRO") || t.includes("FLOX") || t.includes("MYCIN") || t.includes("AZOLE") || t.includes("DRUG") || t.includes("VANCOMYCIN") || t.includes("TETRACYCLINE") || t.includes("RIFAMPICIN"));
    });
    const clean = [];
    withDrugLook.forEach(el => {
      const card = el.closest("button, article, section, div");
      if (card && clean.indexOf(card) === -1) clean.push(card);
    });
    return clean;
  }

  function cardLabel(card, fallbackPrefix, index) {
    const named = card.querySelector("h1,h2,h3,h4,strong,b,.title,.name,.card-title,.panel-title") || card;
    const text = norm(named.textContent || "").split(" ").slice(0, 6).join(" ");
    return text || `${fallbackPrefix} ${index + 1}`;
  }

  function buildSelectorRow(config) {
    const existing = config.host.querySelector(`.petri-005t-selector-row[data-role="${config.role}"]`);
    if (existing) existing.remove();

    const row = document.createElement("div");
    row.className = "petri-005t-selector-row";
    row.dataset.role = config.role;

    const label = document.createElement("label");
    label.className = "petri-005t-selector-label";
    label.textContent = config.label;

    const select = document.createElement("select");
    select.className = "petri-005t-selector-select";

    const lead = document.createElement("option");
    lead.value = "";
    lead.textContent = config.placeholder;
    select.appendChild(lead);

    config.items.forEach(item => {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.label;
      select.appendChild(option);
    });

    select.addEventListener("change", () => {
      const hit = config.items.find(x => x.id === select.value);
      if (!hit || !hit.element) return;
      hit.element.scrollIntoView({ behavior: "smooth", block: "nearest" });
      flash(hit.element);
      if (config.role === "organism-menu") {
        clickCheckboxIn(hit.element);
      } else {
        const clickable = hit.element.querySelector("button") || hit.element;
        if (clickable) clickable.click();
      }
    });

    row.appendChild(label);
    row.appendChild(select);
    config.host.prepend(row);
    return row;
  }

  function installOrganismMenu() {
    const cardsHeader = byText(document, ["h1","h2","h3","h4","div","span"], "ORGANISM CARDS");
    if (!cardsHeader) return 0;
    const panel = cardsHeader.closest("section, article, div") || cardsHeader.parentElement;
    if (!panel) return 0;

    const cards = likelyOrganismCards(panel);
    const items = cards.map((card, index) => ({
      id: card.dataset.cardId || slug(cardLabel(card, "Organism", index)),
      label: cardLabel(card, "Organism", index),
      element: card
    })).filter(x => x.label);

    if (!items.length) return 0;

    buildSelectorRow({
      host: panel,
      role: "organism-menu",
      label: "Organisms",
      placeholder: "Select organism card",
      items
    });

    return items.length;
  }

  function installDrugMenu() {
    const huds = Array.from(document.querySelectorAll(".petri-005s-drug-red-hud, [id*='drug'], [class*='drug'], [id*='Drug'], [class*='Drug']"));
    const hud = huds.find(el => upper(el.textContent).includes("DRUG") && (upper(el.textContent).includes("LAB") || upper(el.textContent).includes("LIBRARY")) && el.getBoundingClientRect().width > 260);
    if (!hud) return 0;

    const cards = likelyDrugCards(hud);
    const items = cards.map((card, index) => ({
      id: card.dataset.drugId || slug(cardLabel(card, "Drug", index)),
      label: cardLabel(card, "Drug", index),
      element: card
    })).filter(x => x.label);

    if (!items.length) return 0;

    const host = hud.querySelector(".petri-005s-drug-hud-title")?.parentElement || hud;
    buildSelectorRow({
      host,
      role: "drug-menu",
      label: "Drug cards",
      placeholder: "Select drug card",
      items
    });

    return items.length;
  }

  function applyAll() {
    repairTopControls();
    const organismCount = installOrganismMenu();
    const drugCount = installDrugMenu();
    window.PETRI_005T_UI = {
      seal: SEAL,
      organism_menu_count: organismCount,
      drug_menu_count: drugCount,
      claim_boundary: "UI alignment and selector-shell only."
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyAll, { once: true });
  } else {
    applyAll();
  }

  let tick = 0;
  const timer = setInterval(() => {
    tick += 1;
    applyAll();
    if (tick > 24) clearInterval(timer);
  }, 350);
})();
