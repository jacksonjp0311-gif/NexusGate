/* PETRI 004O PRESET CARDS + METRIC CHARTS
   Adds preset-aware cards, intervention cards, metric charts, and adaptive dashboard sections.
   Cards change dependent on preset. Entry mirror uses the same config/preset_cards.json schema.
*/
(function(){
  let presetCards = null;
  let metricCards = null;
  let organisms = null;
  let latest = null;
  let particleState = null;
  let activePreset = 'microbial_competition';

  const $ = (id) => document.getElementById(id);
  const q = (sel, root=document) => root.querySelector(sel);
  const qa = (sel, root=document) => Array.from(root.querySelectorAll(sel));
  const colors = ['#27f4ff', '#ffd268', '#ff63f7', '#ff3040', '#41ffbd', '#b665ff'];

  async function safe(call, fallback){ try { return await call(); } catch { return fallback; } }
  function nowPreset(){ return $('preset')?.value || activePreset || 'microbial_competition'; }
  function profile(){ return presetCards?.presets?.[nowPreset()] || presetCards?.presets?.microbial_competition || { sections: {} }; }
  function card(id){ return presetCards?.cards?.[id] || metricCards?.metrics?.[id] || { label: id, summary: 'registered card' }; }
  function organismById(id){ return (organisms?.organisms || []).find(o => o.id === id); }
  function selectedOrganismIds(){
    const checked = qa('[data-org-toggle]').filter(x => x.checked).map(x => x.dataset.orgToggle);
    return checked.length ? checked : (organisms?.organisms || []).filter(o => o.enabled !== false).map(o => o.id);
  }

  function ensureOption(value, label){
    const sel = $('preset');
    if(!sel || qa('option', sel).some(o => o.value === value)) return;
    const opt = document.createElement('option');
    opt.value = value; opt.textContent = label; sel.appendChild(opt);
  }

  function ensureShell(){
    let right = q('.right-panel') || document.body;
    if(!q('#presetDashboard004O')){
      const section = document.createElement('section');
      section.id = 'presetDashboard004O';
      section.className = 'preset-dashboard-004o';
      section.innerHTML = '<h2>Preset Cards</h2><div id="presetSummary004O" class="preset-summary-004o"></div><div id="presetCards004O" class="preset-cards-004o"></div>';
      const archive = q('#runArchive')?.closest('section');
      if(archive && archive.parentElement) archive.parentElement.insertBefore(section, archive);
      else right.appendChild(section);
    }
    let bottom = q('.bottom-strip') || document.body;
    if(!q('#metricChartDeck004O')){
      const section = document.createElement('section');
      section.id = 'metricChartDeck004O';
      section.className = 'mini-panel metric-chart-deck-004o';
      section.innerHTML = '<h3>Metric Charts</h3><div id="metricCharts004O" class="metric-charts-004o"></div>';
      bottom.appendChild(section);
    }
    if(!q('#emergentLog004O')){
      const section = document.createElement('section');
      section.id = 'emergentLog004O';
      section.className = 'mini-panel emergent-log-004o';
      section.innerHTML = '<h3>Emergent Conditions</h3><div id="emergentCards004O" class="emergent-cards-004o"></div>';
      bottom.appendChild(section);
    }
  }

  function metricSeed(name){
    const cells = Number(q('.metric b')?.textContent || 100) || 100;
    const t = Date.now() / 10000;
    const base = name.length * 11 + cells * 0.03;
    return [0,1,2,3,4,5,6,7].map(i => Math.max(0, base + Math.sin(t + i*.8 + name.length)*base*.28 + i*base*.06));
  }

  function drawMiniChart(canvas, values, color){
    if(!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.max(10, Math.floor(rect.width*dpr));
    canvas.height = Math.max(10, Math.floor(rect.height*dpr));
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr,0,0,dpr,0,0);
    const w = rect.width, h = rect.height;
    ctx.clearRect(0,0,w,h);
    ctx.fillStyle = 'rgba(0,6,15,.84)'; ctx.fillRect(0,0,w,h);
    ctx.strokeStyle = 'rgba(255,255,255,.08)';
    for(let i=1;i<4;i++){ const y=i*h/4; ctx.beginPath(); ctx.moveTo(8,y); ctx.lineTo(w-8,y); ctx.stroke(); }
    const max = Math.max(1, ...values);
    ctx.strokeStyle = color; ctx.lineWidth = 2;
    ctx.beginPath();
    values.forEach((v,i)=>{ const x=10+(w-20)*i/Math.max(1,values.length-1); const y=h-10-(h-20)*v/max; if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y); });
    ctx.stroke();
    ctx.fillStyle = color; values.slice(-1).forEach(v=>{ const x=w-10, y=h-10-(h-20)*v/max; ctx.beginPath(); ctx.arc(x,y,3,0,Math.PI*2); ctx.fill(); });
  }

  function renderPresetCards(){
    ensureShell();
    const p = profile();
    const summary = $('presetSummary004O');
    if(summary) summary.innerHTML = `<b>${p.label || nowPreset()}</b><br>${p.summary || ''}<br><span>${(presetCards?.claim_boundary || '').slice(0,160)}</span>`;
    const deck = $('presetCards004O');
    if(!deck) return;
    const sections = p.sections || {};
    const selected = new Set(selectedOrganismIds());
    const groups = ['organism_cards','field_cards','intervention_cards','metric_cards'];
    deck.innerHTML = groups.map(group => {
      const ids = sections[group] || [];
      const cards = ids.flatMap(id => {
        if(id === 'registry_selected_organisms') return [...selected].map(oid => ({ id: oid, data: organismById(oid) || card(oid), selected: true }));
        return [{ id, data: organismById(id) || card(id), selected: selected.has(id) }];
      });
      return `<div class="card-group-004o"><h4>${group.replace(/_/g,' ')}</h4>${cards.map((entry, i) => {
        const c = entry.data || {}; const color = c.color || colors[i % colors.length];
        const label = c.label || c.short_label || entry.id;
        const summary = c.summary || c.card_notes?.join(' ') || c.mechanism || c.morphology?.cell_shape || 'configured card';
        const sources = (c.sources || c.dataset?.primary ? [c.dataset?.primary, c.dataset?.secondary].filter(Boolean) : []).map(s => `<span class="source-chip">${s}</span>`).join('');
        return `<article class="preset-card-004o"><div><span class="dot" style="background:${color};color:${color}"></span><b>${label}</b></div><p>${summary}</p>${sources}</article>`;
      }).join('')}</div>`;
    }).join('');
  }

  function renderMetricCharts(){
    ensureShell();
    const p = profile();
    const metricIds = p.sections?.metric_cards || ['total_cells','shannon_diversity','dominance_index'];
    const deck = $('metricCharts004O');
    if(!deck) return;
    deck.innerHTML = metricIds.map((id, i)=>{
      const m = metricCards?.metrics?.[id] || { label: id, summary: '' };
      return `<article class="metric-chart-card-004o"><div><b>${m.label || id}</b><span>${m.chart || 'chart'}</span></div><canvas data-metric-chart="${id}"></canvas><p>${m.summary || ''}</p></article>`;
    }).join('');
    qa('[data-metric-chart]').forEach((canvas, i)=>drawMiniChart(canvas, metricSeed(canvas.dataset.metricChart), colors[i % colors.length]));
  }

  function renderEmergentCards(){
    ensureShell();
    const host = $('emergentCards004O');
    if(!host) return;
    const active = selectedOrganismIds().length;
    const cells = Number((qa('.metric b')[0] || {}).textContent) || 0;
    const preset = nowPreset();
    const cards = [
      { label: 'Active organism types', value: active, note: 'drives dish membership' },
      { label: 'Preset', value: preset.replace(/_/g,' '), note: 'changes metric/intervention cards' },
      { label: 'Cell artifact load', value: cells, note: cells > 0 ? 'render layer active' : 'waiting for particle state' }
    ];
    host.innerHTML = cards.map(c => `<div class="emergent-card-004o"><b>${c.label}</b><span>${c.value}</span><small>${c.note}</small></div>`).join('');
  }

  async function loadDashboard(){
    if(!window.petri) return;
    presetCards = await safe(() => window.petri.readPresetCards(), {});
    metricCards = await safe(() => window.petri.readMetricCards(), {});
    organisms = await safe(() => window.petri.readOrganisms(), {});
    latest = await safe(() => window.petri.readLatest(), {});
    particleState = await safe(() => window.petri.readParticleState ? window.petri.readParticleState() : Promise.resolve(null), null);
    Object.entries(presetCards?.presets || {}).forEach(([id,p])=>ensureOption(id, p.label || id));
    renderPresetCards(); renderMetricCharts(); renderEmergentCards();
  }

  function install(){
    const preset = $('preset');
    if(preset) preset.addEventListener('change', () => { activePreset = preset.value; renderPresetCards(); renderMetricCharts(); renderEmergentCards(); });
    document.addEventListener('change', e => { if(e.target && e.target.matches('[data-org-toggle]')) setTimeout(()=>{renderPresetCards();renderMetricCharts();renderEmergentCards();},60); });
    document.addEventListener('click', e => { if(e.target && (e.target.id === 'runBtn' || e.target.id === 'reloadBtn')) setTimeout(loadDashboard, 900); });
    setInterval(()=>{ renderMetricCharts(); renderEmergentCards(); }, 1800);
    loadDashboard();
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install); else install();
})();
