(() => {
  "use strict";

  const SEAL = "PETRI_005O_DRUG_INJECTION_HUD_PRESET_SELECTOR";
  const CLAIM = "Educational simulation proxy only - not medical, wet-lab, dosing, susceptibility, diagnostic, treatment, or biosafety guidance.";

  const ORGANISMS = [
    {id:"ecoli_k12_proxy",label:"E. coli K-12",sci:"Escherichia coli K-12",count:"180",shape:"short rod",division:"binary fission",motility:"run-tumble flagellar swimming",oxygen:"facultative anaerobe",habitat:"intestine, lab media, water/soil contexts",growth:.92,biofilm:.35,stress:.41,color:"#31f5ff",gram:"negative"},
    {id:"bacillus_subtilis_168_proxy",label:"Bacillus subtilis 168",sci:"Bacillus subtilis",count:"115",shape:"rod / endospore former",division:"binary fission",motility:"swimming / swarming proxy",oxygen:"aerobe / facultative context",habitat:"soil, plant-associated, lab media",growth:.78,biofilm:.48,stress:.63,color:"#ffd75a",gram:"positive"},
    {id:"saccharomyces_cerevisiae_s288c_proxy",label:"Saccharomyces cerevisiae S288C",sci:"Saccharomyces cerevisiae",count:"72.0K",shape:"budding yeast",division:"budding",motility:"non-motile",oxygen:"facultative anaerobe",habitat:"fermentation, fruit, lab media",growth:.58,biofilm:.22,stress:.55,color:"#ff62f2",gram:"fungal"},
    {id:"acanthamoeba_castellanii_proxy",label:"Acanthamoeba castellanii",sci:"Acanthamoeba castellanii",count:"16.0K",shape:"amoeboid trophozoite",division:"mitosis",motility:"amoeboid crawling",oxygen:"aerobic",habitat:"freshwater, soil, culture contexts",growth:.28,biofilm:.10,stress:.70,color:"#a897ff",gram:"protist"},
    {id:"pseudomonas_aeruginosa_pa01_proxy",label:"Pseudomonas aeruginosa PAO1",sci:"Pseudomonas aeruginosa",count:"95.0K",shape:"rod",division:"binary fission",motility:"polar flagellar swimming",oxygen:"aerobe",habitat:"water, surfaces, environmental/lab contexts",growth:.82,biofilm:.88,stress:.76,color:"#00d9ff",gram:"negative"},
    {id:"staphylococcus_aureus_proxy",label:"Staphylococcus aureus",sci:"Staphylococcus aureus",count:"90.0K",shape:"coccus clusters",division:"binary fission in multiple planes",motility:"non-motile",oxygen:"facultative anaerobe",habitat:"skin, mucosal, surface contexts",growth:.70,biofilm:.74,stress:.80,color:"#ff4f66",gram:"positive"},
    {id:"salmonella_enterica_proxy",label:"Salmonella enterica",sci:"Salmonella enterica",count:"82.0K",shape:"motile rod",division:"binary fission",motility:"flagellar swimming",oxygen:"facultative anaerobe",habitat:"intestinal / environmental contexts",growth:.74,biofilm:.42,stress:.58,color:"#ffac33",gram:"negative"},
    {id:"vibrio_proxy",label:"Vibrio cholerae O1 proxy",sci:"Vibrio sp.",count:"68.0K",shape:"curved rod",division:"binary fission",motility:"rapid aquatic swimming",oxygen:"facultative aquatic context",habitat:"aquatic / estuarine contexts",growth:.80,biofilm:.28,stress:.44,color:"#2cf6d0",gram:"negative"},
    {id:"lactobacillus_plantarum_proxy",label:"Lactobacillus plantarum",sci:"Lactobacillus plantarum",count:"54.0K",shape:"rod",division:"binary fission",motility:"non-motile",oxygen:"aerotolerant anaerobe",habitat:"fermented food, plant, gut-associated contexts",growth:.62,biofilm:.28,stress:.52,color:"#8dff81",gram:"positive"},
    {id:"candida_albicans_proxy",label:"Candida albicans SC5314",sci:"Candida albicans",count:"46.0K",shape:"yeast / pseudohypha proxy",division:"budding",motility:"non-motile",oxygen:"facultative anaerobe",habitat:"host-associated / culture contexts",growth:.60,biofilm:.65,stress:.78,color:"#d183ff",gram:"fungal"},
    {id:"tetrahymena_proxy",label:"Tetrahymena thermophila",sci:"Tetrahymena thermophila",count:"34.0K",shape:"large ciliate",division:"mitosis",motility:"ciliary swimming",oxygen:"aerobic aquatic",habitat:"freshwater and culture contexts",growth:.12,biofilm:.05,stress:.50,color:"#a7b8ff",gram:"protist"},
    {id:"synechocystis_pcc6803_proxy",label:"Synechocystis sp. PCC 6803",sci:"Synechocystis sp. PCC 6803",count:"28.0K",shape:"small coccoid",division:"binary fission",motility:"gliding / low-motility proxy",oxygen:"oxygenic phototroph",habitat:"light-exposed aquatic/culture contexts",growth:.26,biofilm:.56,stress:.64,color:"#2cc3ff",gram:"cyanobacteria"},
    {id:"listeria_monocytogenes_proxy",label:"Listeria monocytogenes",sci:"Listeria monocytogenes",count:"31.0K",shape:"short rod",division:"binary fission",motility:"tumbling motility proxy",oxygen:"facultative anaerobe",habitat:"food, soil, environmental contexts",growth:.58,biofilm:.38,stress:.66,color:"#b9ff66",gram:"positive"},
    {id:"mycobacterium_smegmatis_proxy",label:"Mycobacterium smegmatis",sci:"Mycobacterium smegmatis",count:"24.0K",shape:"slender rod",division:"binary fission",motility:"non-motile",oxygen:"aerobe",habitat:"soil / lab contexts",growth:.35,biofilm:.18,stress:.84,color:"#6f8bff",gram:"acidfast"},
    {id:"enterococcus_faecalis_proxy",label:"Enterococcus faecalis",sci:"Enterococcus faecalis",count:"39.0K",shape:"coccus chain",division:"binary fission",motility:"non-motile",oxygen:"facultative anaerobe",habitat:"gut / environmental / device-surface contexts",growth:.46,biofilm:.68,stress:.82,color:"#c9f270",gram:"positive"},
    {id:"streptococcus_mutans_proxy",label:"Streptococcus mutans",sci:"Streptococcus mutans",count:"26.0K",shape:"coccus chain",division:"binary fission",motility:"non-motile",oxygen:"facultative anaerobe",habitat:"oral biofilm contexts",growth:.52,biofilm:.80,stress:.62,color:"#f0a1ff",gram:"positive"},
    {id:"klebsiella_pneumoniae_proxy",label:"Klebsiella pneumoniae",sci:"Klebsiella pneumoniae",count:"41.0K",shape:"encapsulated rod",division:"binary fission",motility:"non-motile",oxygen:"facultative anaerobe",habitat:"gut / environmental / surface contexts",growth:.66,biofilm:.72,stress:.70,color:"#7ef7c4",gram:"negative"}
  ];

  const PRESETS = {
    "Microbial Competition":["ecoli_k12_proxy","bacillus_subtilis_168_proxy","saccharomyces_cerevisiae_s288c_proxy","acanthamoeba_castellanii_proxy","pseudomonas_aeruginosa_pa01_proxy","staphylococcus_aureus_proxy","salmonella_enterica_proxy","vibrio_proxy","lactobacillus_plantarum_proxy","tetrahymena_proxy","synechocystis_pcc6803_proxy","listeria_monocytogenes_proxy"],
    "Antibiotic Selection":["ecoli_k12_proxy","pseudomonas_aeruginosa_pa01_proxy","salmonella_enterica_proxy","staphylococcus_aureus_proxy","bacillus_subtilis_168_proxy","enterococcus_faecalis_proxy","klebsiella_pneumoniae_proxy","listeria_monocytogenes_proxy","mycobacterium_smegmatis_proxy"],
    "Cellular Tissue Interaction":["acanthamoeba_castellanii_proxy","candida_albicans_proxy","staphylococcus_aureus_proxy","pseudomonas_aeruginosa_pa01_proxy","ecoli_k12_proxy","enterococcus_faecalis_proxy"],
    "Drug Response Screen":["ecoli_k12_proxy","pseudomonas_aeruginosa_pa01_proxy","staphylococcus_aureus_proxy","salmonella_enterica_proxy","candida_albicans_proxy","klebsiella_pneumoniae_proxy"],
    "Antibody Binding Screen":["ecoli_k12_proxy","salmonella_enterica_proxy","klebsiella_pneumoniae_proxy","candida_albicans_proxy","saccharomyces_cerevisiae_s288c_proxy","staphylococcus_aureus_proxy"],
    "Antifungal Pressure":["candida_albicans_proxy","saccharomyces_cerevisiae_s288c_proxy","lactobacillus_plantarum_proxy","staphylococcus_aureus_proxy"],
    "Biofilm Stress":["pseudomonas_aeruginosa_pa01_proxy","staphylococcus_aureus_proxy","klebsiella_pneumoniae_proxy","streptococcus_mutans_proxy","enterococcus_faecalis_proxy","listeria_monocytogenes_proxy"],
    "Protist Predation":["ecoli_k12_proxy","bacillus_subtilis_168_proxy","saccharomyces_cerevisiae_s288c_proxy","acanthamoeba_castellanii_proxy","tetrahymena_proxy","synechocystis_pcc6803_proxy"],
    "Photosynthetic Mat":["synechocystis_pcc6803_proxy","lactobacillus_plantarum_proxy","saccharomyces_cerevisiae_s288c_proxy","ecoli_k12_proxy"],
    "Antibody Binding Panel":["ecoli_k12_proxy","salmonella_enterica_proxy","klebsiella_pneumoniae_proxy","candida_albicans_proxy","saccharomyces_cerevisiae_s288c_proxy","staphylococcus_aureus_proxy"],
    "Metric Cards":["ecoli_k12_proxy","bacillus_subtilis_168_proxy","pseudomonas_aeruginosa_pa01_proxy","staphylococcus_aureus_proxy"]
  };

  const DRUGS = [
    {id:"ampicillin",label:"Ampicillin",class:"beta-lactam",target:"PBP / cell wall synthesis",mechanism:"cell-wall synthesis pressure proxy",spectrum:"Gram+ / Gram- proxy",color:"#32f6ff",targets:["ecoli_k12_proxy","salmonella_enterica_proxy","bacillus_subtilis_168_proxy","enterococcus_faecalis_proxy"],resistance:["blaTEM","PBP shift","permeability"]},
    {id:"ciprofloxacin",label:"Ciprofloxacin",class:"fluoroquinolone",target:"DNA gyrase / topoisomerase",mechanism:"DNA replication stress proxy",spectrum:"broad bacterial proxy",color:"#8aff48",targets:["ecoli_k12_proxy","pseudomonas_aeruginosa_pa01_proxy","salmonella_enterica_proxy","klebsiella_pneumoniae_proxy"],resistance:["gyrA/parC","efflux","porin loss"]},
    {id:"gentamicin",label:"Gentamicin",class:"aminoglycoside",target:"30S ribosome",mechanism:"translation error/stall proxy",spectrum:"aerobic Gram- proxy",color:"#43a7ff",targets:["ecoli_k12_proxy","pseudomonas_aeruginosa_pa01_proxy","klebsiella_pneumoniae_proxy"],resistance:["AME enzymes","uptake loss","efflux"]},
    {id:"tobramycin",label:"Tobramycin",class:"aminoglycoside",target:"30S ribosome",mechanism:"translation error/stall proxy",spectrum:"Pseudomonas-biased proxy",color:"#15d6ff",targets:["pseudomonas_aeruginosa_pa01_proxy","ecoli_k12_proxy"],resistance:["AME enzymes","biofilm tolerance","efflux"]},
    {id:"vancomycin",label:"Vancomycin",class:"glycopeptide",target:"Gram+ cell wall",mechanism:"wall precursor binding proxy",spectrum:"Gram+ proxy",color:"#ad6bff",targets:["staphylococcus_aureus_proxy","enterococcus_faecalis_proxy","bacillus_subtilis_168_proxy","streptococcus_mutans_proxy"],resistance:["van cluster proxy","wall thickening"]},
    {id:"tetracycline",label:"Tetracycline",class:"tetracycline",target:"30S ribosome",mechanism:"translation access block proxy",spectrum:"broad bacterial proxy",color:"#ff5edb",targets:["ecoli_k12_proxy","staphylococcus_aureus_proxy","bacillus_subtilis_168_proxy","streptococcus_mutans_proxy"],resistance:["tet efflux","ribosomal protection"]},
    {id:"erythromycin",label:"Erythromycin",class:"macrolide",target:"50S ribosome",mechanism:"translation elongation block proxy",spectrum:"Gram+ proxy",color:"#ff9d4a",targets:["staphylococcus_aureus_proxy","streptococcus_mutans_proxy","bacillus_subtilis_168_proxy"],resistance:["erm methylation","efflux"]},
    {id:"rifampicin",label:"Rifampicin",class:"rifamycin",target:"RNA polymerase",mechanism:"transcription stress proxy",spectrum:"bacterial transcription proxy",color:"#ffca3a",targets:["mycobacterium_smegmatis_proxy","staphylococcus_aureus_proxy","ecoli_k12_proxy"],resistance:["rpoB proxy"]},
    {id:"fluconazole",label:"Fluconazole",class:"azole antifungal",target:"ergosterol pathway",mechanism:"fungal membrane synthesis stress proxy",spectrum:"fungal proxy",color:"#bd62ff",targets:["candida_albicans_proxy","saccharomyces_cerevisiae_s288c_proxy"],resistance:["ERG11 shift","efflux"]},
    {id:"amphotericin_b",label:"Amphotericin B",class:"polyene antifungal",target:"ergosterol-rich membrane",mechanism:"fungal membrane disruption proxy",spectrum:"fungal proxy",color:"#ff2f71",targets:["candida_albicans_proxy","saccharomyces_cerevisiae_s288c_proxy"],resistance:["sterol remodeling"]},
    {id:"anti_lps_igg",label:"anti-LPS IgG proxy",class:"antibody panel",target:"outer membrane LPS cue",mechanism:"surface occupancy / binding proxy",spectrum:"Gram- binding proxy",color:"#00ffd0",targets:["ecoli_k12_proxy","salmonella_enterica_proxy","klebsiella_pneumoniae_proxy"],resistance:["antigen masking","capsule proxy"]},
    {id:"anti_beta_glucan",label:"anti-beta-glucan mAb proxy",class:"antibody panel",target:"fungal wall beta-glucan cue",mechanism:"fungal wall occupancy proxy",spectrum:"fungal binding proxy",color:"#e07cff",targets:["candida_albicans_proxy","saccharomyces_cerevisiae_s288c_proxy"],resistance:["wall masking proxy"]}
  ];

  const byId = Object.fromEntries(ORGANISMS.map(o => [o.id, o]));
  const drugById = Object.fromEntries(DRUGS.map(d => [d.id, d]));
  const state = { preset:"Microbial Competition", selectedByPreset:{}, expanded:new Set(), selectedDrug:"ampicillin", activeDrugs:[], dose:10 };

  function norm(s){ return String(s || "").replace(/\s+/g," ").trim(); }
  function up(s){ return norm(s).toUpperCase(); }
  function esc(s){ return String(s ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
  function elem(tag, attrs={}, html=""){ const n=document.createElement(tag); Object.entries(attrs).forEach(([k,v])=>{ if(k==="class") n.className=v; else n.setAttribute(k,v); }); if(html) n.innerHTML=html; return n; }

  function findPresetSelect(){
    return Array.from(document.querySelectorAll("select")).find(sel => Array.from(sel.options || []).some(o => PRESETS[norm(o.textContent || o.value)]));
  }
  function currentPreset(){
    const sel = findPresetSelect();
    if(!sel) return state.preset;
    const opt = sel.options[sel.selectedIndex];
    return norm(opt?.textContent || sel.value || state.preset);
  }
  function selectedSet(){
    if(!state.selectedByPreset[state.preset]) state.selectedByPreset[state.preset] = new Set(PRESETS[state.preset] || PRESETS["Microbial Competition"]);
    if(Array.isArray(state.selectedByPreset[state.preset])) state.selectedByPreset[state.preset] = new Set(state.selectedByPreset[state.preset]);
    return state.selectedByPreset[state.preset];
  }
  function presetOrganisms(){ return (PRESETS[state.preset] || PRESETS["Microbial Competition"]).map(id => byId[id]).filter(Boolean); }

  function ensureDrugButton(){
    if(document.getElementById("petri-005o-drug-button")) return;
    const capture = Array.from(document.querySelectorAll("button")).find(b => up(b.textContent).includes("CAPTURE"));
    const btn = elem("button", {id:"petri-005o-drug-button", class:"petri-005o-top-drug-btn", type:"button"}, "âš- Drug Lab");
    btn.addEventListener("click", openHud);
    if(capture?.parentElement) capture.parentElement.insertBefore(btn, capture.nextSibling);
    else document.body.appendChild(btn);
  }

  function ensureHud(){
    let hud = document.getElementById("petri-005o-drug-hud");
    if(hud) return hud;
    hud = elem("div", {id:"petri-005o-drug-hud", class:"petri-005o-hud", "aria-hidden":"true"});
    hud.innerHTML = `
      <div class="petri-005o-hud-shell">
        <div class="petri-005o-hud-head"><div><div class="petri-005o-kicker">DRUG INJECTION LAB</div><div class="petri-005o-sub">cyber-blue proxy simulator / selectable drug cards</div></div><button id="petri-005o-hud-close" type="button">Ã-</button></div>
        <div class="petri-005o-hud-filters"><input id="petri-005o-drug-search" placeholder="Search drugs, classes, targets..."><select id="petri-005o-class-filter"><option>All Classes</option></select><select id="petri-005o-target-filter"><option>All Targets</option></select></div>
        <div class="petri-005o-hud-grid"><div><div class="petri-005o-section-title">DRUG LIBRARY</div><div id="petri-005o-drug-list" class="petri-005o-drug-list"></div></div><div id="petri-005o-drug-detail"></div></div>
        <div class="petri-005o-claim">${CLAIM}</div>
      </div>`;
    document.body.appendChild(hud);
    hud.querySelector("#petri-005o-hud-close").addEventListener("click", closeHud);
    hud.querySelector("#petri-005o-drug-search").addEventListener("input", renderDrugList);
    hud.querySelector("#petri-005o-class-filter").addEventListener("change", renderDrugList);
    hud.querySelector("#petri-005o-target-filter").addEventListener("change", renderDrugList);
    populateHudFilters();
    renderDrugList();
    renderDrugDetail();
    return hud;
  }
  function populateHudFilters(){
    const c=document.getElementById("petri-005o-class-filter"), t=document.getElementById("petri-005o-target-filter");
    if(!c || !t) return;
    c.innerHTML = "<option>All Classes</option>" + [...new Set(DRUGS.map(d=>d.class))].sort().map(x=>`<option>${esc(x)}</option>`).join("");
    t.innerHTML = "<option>All Targets</option>" + [...new Set(DRUGS.map(d=>d.target))].sort().map(x=>`<option>${esc(x)}</option>`).join("");
  }
  function openHud(){ const h=ensureHud(); h.classList.add("open"); h.setAttribute("aria-hidden","false"); renderDrugList(); renderDrugDetail(); }
  function closeHud(){ const h=document.getElementById("petri-005o-drug-hud"); h?.classList.remove("open"); h?.setAttribute("aria-hidden","true"); }

  function renderDrugList(){
    const root=document.getElementById("petri-005o-drug-list"); if(!root) return;
    const q=up(document.getElementById("petri-005o-drug-search")?.value || "");
    const cls=norm(document.getElementById("petri-005o-class-filter")?.value || "All Classes");
    const tgt=norm(document.getElementById("petri-005o-target-filter")?.value || "All Targets");
    const list=DRUGS.filter(d => (!q || up([d.label,d.class,d.target,d.mechanism,d.spectrum].join(" ")).includes(q)) && (cls==="All Classes" || d.class===cls) && (tgt==="All Targets" || d.target===tgt));
    root.innerHTML = list.map(d => `<button class="petri-005o-drug-card ${d.id===state.selectedDrug?"active":""}" data-drug="${esc(d.id)}" type="button"><span class="petri-005o-dot" style="--dot:${esc(d.color)}"></span><span><b>${esc(d.label)}</b><small>${esc(d.class)}</small></span><em>${state.activeDrugs.includes(d.id)?"ACTIVE":""}</em></button>`).join("");
    root.querySelectorAll("[data-drug]").forEach(btn => btn.addEventListener("click", () => { state.selectedDrug=btn.dataset.drug; renderDrugList(); renderDrugDetail(); }));
  }

  function susceptibility(org, drug){
    let base = drug.targets.includes(org.id) ? .78 : .22;
    if(drug.class.includes("antifungal") || drug.class.includes("polyene")) base = org.gram==="fungal" ? .82 : .06;
    if(drug.class.includes("antibody")) base = drug.targets.includes(org.id) ? .70 : .12;
    if(drug.class.includes("glycopeptide")) base = org.gram==="positive" ? .72 : .08;
    if(drug.class.includes("aminoglycoside")) base = org.gram==="negative" ? .68 : .24;
    if(org.biofilm > .70) base *= .72;
    if(org.stress > .75) base *= .82;
    return Math.max(.02, Math.min(.98, base));
  }
  function svgCurve(drug){
    const target = Array.from(selectedSet()).map(id=>byId[id]).filter(Boolean);
    const avg = target.reduce((s,o)=>s+susceptibility(o,drug),0) / Math.max(1,target.length);
    const pts=[]; for(let i=0;i<=16;i++){ const t=i/16; const y=96-(76*avg*(1-Math.exp(-3.5*t)))+(Math.sin(i*1.7)*2); pts.push([8+t*260,Math.max(12,Math.min(96,y))]);}
    const path=pts.map((p,i)=>`${i?"L":"M"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
    return `<svg viewBox="0 0 280 110" class="petri-005o-response-svg"><line x1="8" y1="96" x2="270" y2="96"></line><line x1="8" y1="12" x2="8" y2="96"></line><path d="${path}"></path><text x="12" y="18">survival proxy</text><text x="210" y="106">time</text></svg>`;
  }
  function renderDrugDetail(){
    const root=document.getElementById("petri-005o-drug-detail"); if(!root) return;
    const drug=drugById[state.selectedDrug] || DRUGS[0];
    const targets=Array.from(selectedSet()).map(id=>byId[id]).filter(Boolean);
    const rows=targets.slice(0,8).map(o=>{ const s=susceptibility(o,drug); return `<div class="petri-005o-response-row"><span><i style="background:${esc(o.color)}"></i>${esc(o.label)}</span><b>${Math.round(s*100)}%</b><meter min="0" max="1" value="${s.toFixed(2)}"></meter></div>`; }).join("");
    root.innerHTML = `<div class="petri-005o-detail-card"><div class="petri-005o-detail-head"><div><h3>${esc(drug.label)}</h3><p>${esc(drug.class)}</p></div><span>${state.activeDrugs.includes(drug.id)?"ACTIVE":"READY"}</span></div><div class="petri-005o-detail-grid"><label>Class <b>${esc(drug.class)}</b></label><label>Mechanism <b>${esc(drug.mechanism)}</b></label><label>Target <b>${esc(drug.target)}</b></label><label>Spectrum <b>${esc(drug.spectrum)}</b></label></div><div class="petri-005o-chips">${drug.resistance.map(r=>`<span>${esc(r)}</span>`).join("")}</div><div class="petri-005o-dose-grid"><label>Dose proxy <input id="petri-005o-dose" type="range" min="1" max="100" value="${state.dose}"><b>${state.dose} Âug/mL</b></label><label>Exposure <select><option>10 min</option><option selected>30 min</option><option>60 min</option></select></label><label>Application <select><option selected>Bolus</option><option>Gradient</option><option>Pulse</option></select></label></div><div class="petri-005o-section-title">PREDICTED RESPONSE</div>${svgCurve(drug)}<div class="petri-005o-response-list">${rows}</div><button id="petri-005o-inject" class="petri-005o-inject-btn" type="button">Inject Drug</button></div>`;
    root.querySelector("#petri-005o-dose")?.addEventListener("input", e => { state.dose=Number(e.target.value||10); renderDrugDetail(); });
    root.querySelector("#petri-005o-inject")?.addEventListener("click", () => { if(!state.activeDrugs.includes(drug.id)) state.activeDrugs.push(drug.id); document.body.classList.add("petri-005o-drug-active"); renderDrugList(); renderDrugDetail(); updateDashboard(); });
  }

  function findRegistryPanel(){
    const nodes=Array.from(document.querySelectorAll("aside,section,div"));
    return nodes.filter(n => up(n.textContent).includes("ORGANISM REGISTRY")).sort((a,b)=>(a.getBoundingClientRect().width*a.getBoundingClientRect().height)-(b.getBoundingClientRect().width*b.getBoundingClientRect().height))[0] || null;
  }
  function ensureRegistryHost(){
    let host=document.getElementById("petri-005o-registry-host"); if(host) return host;
    host=document.createElement("div"); host.id="petri-005o-registry-host"; host.className="petri-005o-registry-host";
    const panel=findRegistryPanel();
    if(panel){ Array.from(panel.children).forEach(c=>{ if(!c.id?.startsWith("petri-005o")) c.classList.add("petri-005o-soft-hidden"); }); panel.appendChild(host); }
    else { host.classList.add("floating"); document.body.appendChild(host); }
    return host;
  }
  function renderRegistry(){
    state.preset=currentPreset();
    if(!PRESETS[state.preset]) state.preset=Object.keys(PRESETS).find(k => up(k)===up(state.preset)) || "Microbial Competition";
    const host=ensureRegistryHost();
    const organisms=presetOrganisms();
    const selected=selectedSet();
    const active=organisms.filter(o=>selected.has(o.id)).length;
    host.innerHTML=`<div class="petri-005o-reg-head"><span>ORGANISM REGISTRY</span><b>${active} / ${organisms.length} selected</b></div><div class="petri-005o-reg-sub">Preset: <strong>${esc(state.preset)}</strong></div><div class="petri-005o-card-list">${organisms.map(o=>renderOrg(o, selected.has(o.id))).join("")}</div>`;
    host.querySelectorAll(".petri-005o-org-head").forEach(row=>row.addEventListener("click", e=>{ if(e.target?.matches?.("input")) return; const id=row.dataset.org; state.expanded.has(id)?state.expanded.delete(id):state.expanded.add(id); renderRegistry(); }));
    host.querySelectorAll("input[data-select-org]").forEach(input=>input.addEventListener("change", e=>{ const set=selectedSet(); e.target.checked?set.add(e.target.dataset.selectOrg):set.delete(e.target.dataset.selectOrg); renderRegistry(); updateDashboard(); }));
    updateDashboard();
  }
  function renderOrg(o, checked){
    const open=state.expanded.has(o.id);
    return `<div class="petri-005o-org-card ${open?"open":""} ${checked?"selected":""}"><div class="petri-005o-org-head" data-org="${esc(o.id)}"><label class="petri-005o-check"><input type="checkbox" data-select-org="${esc(o.id)}" ${checked?"checked":""}><span></span></label><i style="--dot:${esc(o.color)}"></i><div><b>${esc(o.label)}</b><small>${esc(o.sci)}</small></div><em>${esc(o.count)}</em><button type="button">${open?"âŒƒ":"âŒ„"}</button></div><div class="petri-005o-org-detail"><div><span>Shape</span><b>${esc(o.shape)}</b></div><div><span>Division</span><b>${esc(o.division)}</b></div><div><span>Motility</span><b>${esc(o.motility)}</b></div><div><span>Oxygen</span><b>${esc(o.oxygen)}</b></div><div><span>Habitat</span><b>${esc(o.habitat)}</b></div><div class="petri-005o-bars"><label>Growth <meter min="0" max="1" value="${o.growth}"></meter><b>${o.growth.toFixed(2)}</b></label><label>Biofilm <meter min="0" max="1" value="${o.biofilm}"></meter><b>${o.biofilm.toFixed(2)}</b></label><label>Stress <meter min="0" max="1" value="${o.stress}"></meter><b>${o.stress.toFixed(2)}</b></label></div></div></div>`;
  }

  function updateDashboard(){
    const organisms=presetOrganisms();
    const selected=organisms.filter(o=>selectedSet().has(o.id));
    const toast=document.getElementById("petri-005o-toast") || elem("div",{id:"petri-005o-toast",class:"petri-005o-toast"});
    toast.innerHTML=`<b>${esc(state.preset)}</b> Â· ${selected.length} organism${selected.length===1?"":"s"} selected Â· ${state.activeDrugs.length} drug card${state.activeDrugs.length===1?"":"s"} active`;
    if(!toast.parentElement) document.body.appendChild(toast);
    window.PETRI_005O_STATE={preset:state.preset,selected_organisms:selected.map(o=>o.id),active_drugs:[...state.activeDrugs],claim_boundary:CLAIM};
  }
  function wirePreset(){
    const sel=findPresetSelect(); if(!sel || sel.dataset.petri005oWired) return;
    sel.dataset.petri005oWired="true";
    sel.addEventListener("change",()=>{ state.preset=currentPreset(); if(!state.selectedByPreset[state.preset]) state.selectedByPreset[state.preset]=new Set(PRESETS[state.preset] || []); state.expanded.clear(); setTimeout(renderRegistry,20); });
  }
  function boot(){ ensureDrugButton(); ensureHud(); wirePreset(); renderRegistry(); }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", boot, {once:true}); else boot();
  let tries=0; const timer=setInterval(()=>{ tries++; ensureDrugButton(); wirePreset(); if(!document.getElementById("petri-005o-registry-host")) renderRegistry(); if(tries>20) clearInterval(timer); },500);
  window.PETRI_005O_DRUG_LAB={openHud,closeHud,renderRegistry,state,organisms:ORGANISMS,drugs:DRUGS,claim_boundary:CLAIM};
})();
