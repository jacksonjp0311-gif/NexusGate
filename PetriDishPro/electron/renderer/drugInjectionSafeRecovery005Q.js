(() => {
  "use strict";

  const SEAL = "PETRI_005Q_EMERGENCY_VISUAL_RECOVERY_SAFE_DRUG_LAB";
  const CLAIM = "Educational simulation proxy only. Not medical, dosing, diagnostic, wet-lab, susceptibility, treatment, or biosafety guidance.";

  const organisms = [
    {id:"ecoli_k12_proxy", label:"E. coli K-12", type:"Gram-negative rod", behavior:"run-tumble motility", color:"#31f5ff"},
    {id:"bacillus_subtilis_168_proxy", label:"B. subtilis 168", type:"Gram-positive rod", behavior:"swimming / sporulation proxy", color:"#ffd75a"},
    {id:"pseudomonas_aeruginosa_pa01_proxy", label:"P. aeruginosa PAO1", type:"Gram-negative rod", behavior:"biofilm / polar motility", color:"#00d9ff"},
    {id:"staphylococcus_aureus_proxy", label:"S. aureus", type:"Gram-positive coccus", behavior:"cluster growth / biofilm proxy", color:"#ff4f66"},
    {id:"salmonella_enterica_proxy", label:"S. enterica", type:"Gram-negative rod", behavior:"flagellar motility", color:"#ffac33"},
    {id:"candida_albicans_proxy", label:"C. albicans", type:"fungal yeast", behavior:"budding / hypha proxy", color:"#d183ff"},
    {id:"saccharomyces_cerevisiae_s288c_proxy", label:"S. cerevisiae S288C", type:"budding yeast", behavior:"fermentation growth proxy", color:"#ff62f2"},
    {id:"tetrahymena_proxy", label:"Tetrahymena", type:"ciliate protist", behavior:"ciliary grazing proxy", color:"#a7b8ff"},
    {id:"synechocystis_pcc6803_proxy", label:"Synechocystis PCC 6803", type:"cyanobacterium", behavior:"phototroph / gliding proxy", color:"#2cc3ff"}
  ];

  const presets = {
    "Microbial Competition": ["ecoli_k12_proxy","bacillus_subtilis_168_proxy","pseudomonas_aeruginosa_pa01_proxy","staphylococcus_aureus_proxy","salmonella_enterica_proxy"],
    "Antibiotic Selection": ["ecoli_k12_proxy","pseudomonas_aeruginosa_pa01_proxy","salmonella_enterica_proxy","staphylococcus_aureus_proxy","bacillus_subtilis_168_proxy"],
    "Biofilm Stress": ["pseudomonas_aeruginosa_pa01_proxy","staphylococcus_aureus_proxy","bacillus_subtilis_168_proxy"],
    "Antifungal Pressure": ["candida_albicans_proxy","saccharomyces_cerevisiae_s288c_proxy"],
    "Protist Predation": ["ecoli_k12_proxy","bacillus_subtilis_168_proxy","tetrahymena_proxy","synechocystis_pcc6803_proxy"]
  };

  const drugs = [
    {id:"ampicillin", label:"Ampicillin", cls:"beta-lactam", target:"cell wall synthesis", color:"#32f6ff"},
    {id:"ciprofloxacin", label:"Ciprofloxacin", cls:"fluoroquinolone", target:"DNA gyrase / topoisomerase", color:"#8aff48"},
    {id:"gentamicin", label:"Gentamicin", cls:"aminoglycoside", target:"30S ribosome", color:"#43a7ff"},
    {id:"vancomycin", label:"Vancomycin", cls:"glycopeptide", target:"Gram-positive wall", color:"#ad6bff"},
    {id:"tetracycline", label:"Tetracycline", cls:"tetracycline", target:"30S ribosome", color:"#ff5edb"},
    {id:"fluconazole", label:"Fluconazole", cls:"azole antifungal", target:"ergosterol pathway", color:"#bd62ff"},
    {id:"anti_lps_igg", label:"anti-LPS IgG proxy", cls:"antibody panel", target:"outer membrane LPS cue", color:"#00ffd0"}
  ];

  const byId = Object.fromEntries(organisms.map(o => [o.id, o]));
  const state = {
    selectedDrug: "ampicillin",
    activeDrugs: [],
    selectedOrganisms: new Set(presets["Microbial Competition"])
  };

  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
  }

  function norm(s) {
    return String(s || "").replace(/\s+/g, " ").trim();
  }

  function up(s) {
    return norm(s).toUpperCase();
  }

  function q(id) {
    return document.getElementById(id);
  }

  function important(el, prop, value) {
    if (el) el.style.setProperty(prop, value, "important");
  }

  function releaseCoreSurfaces() {
    // Remove runtime hiding left behind by 005O/005P2.
    document.querySelectorAll(".petri-005o-soft-hidden").forEach(el => {
      el.classList.remove("petri-005o-soft-hidden");
      important(el, "display", "");
      important(el, "visibility", "");
      important(el, "opacity", "");
      important(el, "filter", "");
      important(el, "pointer-events", "");
    });

    // Remove invasive 005O HUD/registry clones. 005Q is standalone and does not touch the core registry.
    ["petri-005o-drug-hud", "petri-005o-registry-host", "petri-005o-toast"].forEach(id => {
      const node = q(id);
      if (node) node.remove();
    });

    document.body.classList.remove("petri-005o-drug-active", "petri-005p2-dragging", "petri-005p-dragging");
  }

  function findTopBar() {
    const capture = Array.from(document.querySelectorAll("button")).find(b => up(b.textContent).includes("CAPTURE"));
    return capture && capture.parentElement ? capture.parentElement : null;
  }

  function ensureButton() {
    let btn = q("petri-005q-drug-button");
    if (btn) return btn;

    btn = document.createElement("button");
    btn.id = "petri-005q-drug-button";
    btn.type = "button";
    btn.textContent = "Drug Lab";
    btn.title = "Open safe Drug Lab";
    btn.addEventListener("click", openHud);

    const bar = findTopBar();
    const capture = Array.from(document.querySelectorAll("button")).find(b => up(b.textContent).includes("CAPTURE"));
    if (bar && capture) bar.insertBefore(btn, capture.nextSibling);
    else document.body.appendChild(btn);

    return btn;
  }

  function ensureHud() {
    let hud = q("petri-005q-drug-hud");
    if (hud) return hud;

    hud = document.createElement("div");
    hud.id = "petri-005q-drug-hud";
    hud.innerHTML = `
      <div class="petri-005q-shell">
        <div class="petri-005q-head">
          <div>
            <div class="petri-005q-title">DRUG LAB SAFE MODE</div>
            <div class="petri-005q-sub">standalone overlay / does not modify microscope renderer</div>
          </div>
          <div class="petri-005q-tools">
            <button type="button" data-action="center">Center</button>
            <button type="button" data-action="wide">Wide</button>
            <button type="button" data-action="close">X</button>
          </div>
        </div>
        <div class="petri-005q-grid">
          <section>
            <div class="petri-005q-section">DRUG CARDS</div>
            <div id="petri-005q-drugs"></div>
          </section>
          <section>
            <div class="petri-005q-section">ORGANISM SELECTION</div>
            <select id="petri-005q-preset">
              ${Object.keys(presets).map(p => `<option>${esc(p)}</option>`).join("")}
            </select>
            <div id="petri-005q-organisms"></div>
          </section>
          <section>
            <div class="petri-005q-section">INTERACTION HUD</div>
            <div id="petri-005q-detail"></div>
          </section>
        </div>
        <div class="petri-005q-claim">${CLAIM}</div>
      </div>
    `;

    document.body.appendChild(hud);

    hud.querySelector('[data-action="close"]').addEventListener("click", closeHud);
    hud.querySelector('[data-action="center"]').addEventListener("click", centerHud);
    hud.querySelector('[data-action="wide"]').addEventListener("click", wideHud);
    hud.querySelector("#petri-005q-preset").addEventListener("change", ev => {
      state.selectedOrganisms = new Set(presets[ev.target.value] || []);
      renderHud();
    });

    enableDrag(hud);
    renderHud();
    centerHud();
    return hud;
  }

  function centerHud() {
    const hud = q("petri-005q-drug-hud");
    if (!hud) return;
    const w = Math.min(980, Math.max(760, Math.round(window.innerWidth * 0.62)));
    const h = Math.min(760, Math.max(540, Math.round(window.innerHeight * 0.76)));
    important(hud, "width", `${w}px`);
    important(hud, "height", `${h}px`);
    important(hud, "left", `${Math.max(20, Math.round((window.innerWidth - w) / 2))}px`);
    important(hud, "top", "76px");
    hud.dataset.moved = "true";
  }

  function wideHud() {
    const hud = q("petri-005q-drug-hud");
    if (!hud) return;
    important(hud, "left", "24px");
    important(hud, "top", "72px");
    important(hud, "width", "calc(100vw - 48px)");
    important(hud, "height", "calc(100vh - 104px)");
    hud.dataset.moved = "true";
  }

  function openHud() {
    const hud = ensureHud();
    hud.classList.add("open");
    releaseCoreSurfaces();
    renderHud();
  }

  function closeHud() {
    const hud = q("petri-005q-drug-hud");
    if (hud) hud.classList.remove("open");
  }

  function enableDrag(hud) {
    if (hud.dataset.drag005q) return;
    hud.dataset.drag005q = "true";

    let drag = false;
    let dx = 0;
    let dy = 0;

    document.addEventListener("mousedown", ev => {
      if (!hud.classList.contains("open")) return;
      const head = ev.target.closest && ev.target.closest(".petri-005q-head");
      if (!head) return;
      if (ev.target.closest("button,select,input")) return;
      const r = hud.getBoundingClientRect();
      drag = true;
      dx = ev.clientX - r.left;
      dy = ev.clientY - r.top;
      document.body.classList.add("petri-005q-dragging");
      ev.preventDefault();
    }, true);

    document.addEventListener("mousemove", ev => {
      if (!drag) return;
      const r = hud.getBoundingClientRect();
      const left = Math.max(8, Math.min(window.innerWidth - r.width - 8, ev.clientX - dx));
      const top = Math.max(8, Math.min(window.innerHeight - 80, ev.clientY - dy));
      important(hud, "left", `${Math.round(left)}px`);
      important(hud, "top", `${Math.round(top)}px`);
    }, true);

    document.addEventListener("mouseup", () => {
      drag = false;
      document.body.classList.remove("petri-005q-dragging");
    }, true);
  }

  function renderHud() {
    renderDrugs();
    renderOrganisms();
    renderDetail();
    window.PETRI_005Q_SAFE_STATE = {
      selected_drug: state.selectedDrug,
      active_drugs: state.activeDrugs.slice(),
      selected_organisms: Array.from(state.selectedOrganisms),
      claim_boundary: CLAIM
    };
  }

  function renderDrugs() {
    const root = q("petri-005q-drugs");
    if (!root) return;
    root.innerHTML = drugs.map(d => `
      <button type="button" class="petri-005q-drug ${d.id === state.selectedDrug ? "active" : ""}" data-drug="${esc(d.id)}">
        <i style="--dot:${esc(d.color)}"></i>
        <span><b>${esc(d.label)}</b><small>${esc(d.cls)}</small></span>
      </button>
    `).join("");

    root.querySelectorAll("[data-drug]").forEach(btn => {
      btn.addEventListener("click", () => {
        state.selectedDrug = btn.getAttribute("data-drug");
        renderHud();
      });
    });
  }

  function renderOrganisms() {
    const root = q("petri-005q-organisms");
    if (!root) return;
    root.innerHTML = organisms.map(o => {
      const checked = state.selectedOrganisms.has(o.id);
      return `
        <div class="petri-005q-org">
          <label>
            <input type="checkbox" data-org="${esc(o.id)}" ${checked ? "checked" : ""}>
            <i style="--dot:${esc(o.color)}"></i>
            <span><b>${esc(o.label)}</b><small>${esc(o.type)}</small></span>
          </label>
          <details>
            <summary>behavior</summary>
            <p>${esc(o.behavior)}</p>
          </details>
        </div>
      `;
    }).join("");

    root.querySelectorAll("[data-org]").forEach(input => {
      input.addEventListener("change", () => {
        const id = input.getAttribute("data-org");
        if (input.checked) state.selectedOrganisms.add(id);
        else state.selectedOrganisms.delete(id);
        renderDetail();
      });
    });
  }

  function drugResponseScore(org, drug) {
    let score = 0.24;
    if (drug.cls.includes("antifungal")) score = org.type.includes("yeast") || org.type.includes("fungal") ? 0.82 : 0.04;
    else if (drug.cls.includes("antibody")) score = org.type.includes("Gram-negative") ? 0.68 : 0.16;
    else if (drug.cls.includes("glycopeptide")) score = org.type.includes("Gram-positive") ? 0.72 : 0.07;
    else if (drug.cls.includes("aminoglycoside")) score = org.type.includes("Gram-negative") ? 0.70 : 0.22;
    else if (drug.cls.includes("beta-lactam")) score = org.type.includes("rod") || org.type.includes("Gram") ? 0.62 : 0.12;
    return Math.max(0.02, Math.min(0.98, score));
  }

  function renderDetail() {
    const root = q("petri-005q-detail");
    if (!root) return;
    const drug = drugs.find(d => d.id === state.selectedDrug) || drugs[0];
    const selected = Array.from(state.selectedOrganisms).map(id => byId[id]).filter(Boolean);
    const rows = selected.map(o => {
      const score = drugResponseScore(o, drug);
      return `
        <div class="petri-005q-row">
          <span><i style="--dot:${esc(o.color)}"></i>${esc(o.label)}</span>
          <meter min="0" max="1" value="${score.toFixed(2)}"></meter>
          <b>${Math.round(score * 100)}%</b>
        </div>
      `;
    }).join("");

    root.innerHTML = `
      <div class="petri-005q-detail">
        <h3>${esc(drug.label)}</h3>
        <p><b>Class:</b> ${esc(drug.cls)}</p>
        <p><b>Target:</b> ${esc(drug.target)}</p>
        <div class="petri-005q-dose">
          <label>Dose proxy <input type="range" min="1" max="100" value="10"></label>
          <label>Exposure <select><option>10 min</option><option selected>30 min</option><option>60 min</option></select></label>
          <label>Mode <select><option selected>Bolus</option><option>Gradient</option><option>Pulse</option></select></label>
        </div>
        <div class="petri-005q-section">RESPONSE PROXY</div>
        ${rows || "<p>No organisms selected.</p>"}
        <button type="button" id="petri-005q-inject">Inject Proxy</button>
      </div>
    `;

    const inject = q("petri-005q-inject");
    if (inject) {
      inject.addEventListener("click", () => {
        if (!state.activeDrugs.includes(drug.id)) state.activeDrugs.push(drug.id);
        inject.textContent = "Injected";
        document.body.classList.add("petri-005q-drug-active");
      });
    }
  }

  function boot() {
    releaseCoreSurfaces();
    ensureButton();
    ensureHud();
    closeHud();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, {once:true});
  else boot();

  let ticks = 0;
  const timer = setInterval(() => {
    ticks += 1;
    releaseCoreSurfaces();
    ensureButton();
    if (ticks > 20) clearInterval(timer);
  }, 400);

  window.PETRI_005Q_SAFE_RECOVERY = {
    seal: SEAL,
    openHud,
    closeHud,
    releaseCoreSurfaces,
    claim_boundary: CLAIM
  };
})();
