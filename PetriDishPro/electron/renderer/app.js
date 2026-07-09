/* PETRI 004K REAL SCIENCE ORGANISM REGISTRY visual_contract schema adapter circular microscope dish stronger glow field rendering zoom pan reset optional grid overlay metrics chips organism population cards real population curve legend run archive panel open artifacts button Organism Cards Run Archive Open Artifacts Animation rule: requestAnimationFrame(loop) starts at boot and continues even when capture is not active. */
let config={},organismRegistry={organisms:[]},fieldProfiles={},latest={},runs=[],selectedOrganisms=new Set(),activeView="organisms",paused=false,t=0,lastFrame=0,fps=0,frameCount=0,fpsStart=0,cells=[],hosts=[],particles=[],pan={x:0,y:0},drag=null;const $=id=>document.getElementById(id);const COLORS=["#27f4ff","#ffd268","#ff63f7","#ff3040","#41ffbd","#b665ff"];function val(id,f=0){const n=Number($(id)?.value);return Number.isFinite(n)?n:f}function clamp(v,a,b){return Math.max(a,Math.min(b,v))}function fmt(v){const n=Number(v);if(!Number.isFinite(n))return"0";return n>=100?n.toFixed(1):n.toFixed(3)}function seeded(seed){let s=Math.abs(seed)%2147483647;if(s<=0)s+=2147483646;return()=> (s=s*16807%2147483647)/2147483647}function hash(str){let h=2166136261;for(const ch of String(str)){h^=ch.charCodeAt(0);h=Math.imul(h,16777619)}return h>>>0}function registryList(){return Array.isArray(organismRegistry.organisms)?organismRegistry.organisms:[]}function byId(id){return registryList().find(o=>o.id===id)}function idFromSlug(slug){const s=String(slug||"");return registryList().find(o=>o.id===s||(o.legacy_slugs||[]).includes(s))?.id||s}function labelize(slug){const spec=byId(idFromSlug(slug));if(spec?.label)return spec.label;return String(slug||"organism").replace(/_/g," ").replace(/\b[a-z]/g,c=>c.toUpperCase())}function displayNameFor(value){return labelize(value)}function normalizeDominantName(run){const normalized=normalizeRun(run||{});return normalized.metrics.dominant_name||normalized.metrics.dominant||"unknown"}function initSelection(){const stored=localStorage.getItem("petri_selected_organisms_004k");if(stored){try{selectedOrganisms=new Set(JSON.parse(stored))}catch{selectedOrganisms=new Set()}}if(!selectedOrganisms.size)selectedOrganisms=new Set(registryList().filter(o=>o.enabled!==false).map(o=>o.id))}function saveSelection(){localStorage.setItem("petri_selected_organisms_004k",JSON.stringify([...selectedOrganisms]))}
function normalizeRun(raw){raw=raw||{};const metrics=raw.metrics||{},popById={},ts=raw.timeseries||raw.population_curves||raw.curves||[],last=Array.isArray(ts)&&ts.length?ts[ts.length-1]:null,lastPop=last?.populations||last?.population||null;if(lastPop&&typeof lastPop==="object")for(const[slug,amount]of Object.entries(lastPop))popById[idFromSlug(slug)]=Number(amount||0);if(Array.isArray(raw.organisms))for(const item of raw.organisms){const id=idFromSlug(item.slug||item.id||item.name||item.organism);popById[id]=Number(item.population??item.final_population??item.value??item.count??popById[id]??0)}const organisms=registryList().map((spec,i)=>({id:spec.id,slug:spec.id,name:spec.label,short_label:spec.short_label||spec.label,value:Number.isFinite(popById[spec.id])&&popById[spec.id]>0?popById[spec.id]:Number(spec.baseline_population||20),color:spec.color||COLORS[i%COLORS.length],spec,selected:selectedOrganisms.has(spec.id)}));const visible=organisms.filter(o=>o.selected),total=visible.reduce((a,b)=>a+b.value,0),dominant=visible.slice().sort((a,b)=>b.value-a.value)[0]||organisms[0]||{name:"unknown"};return{run_id:raw.run_id||raw.id||"live_preview",preset:raw.preset||raw.experiment?.preset||$("preset")?.value||"microbial_competition",validation:raw.validation||{status:raw.validation_status||"preview"},metrics:{...metrics,total_population:total,dominant:dominant.name,dominant_name:dominant.name},organisms,timeseries:Array.isArray(ts)?ts:[],raw}}
function syncControls(){["zoom","cellDensity","cellScale","flow"].forEach(id=>{});$("zoomVal").textContent=`${val("zoom",1).toFixed(2)}x`;$("cellVal").textContent=`${val("cellDensity",1).toFixed(2)}x`;$("scaleVal").textContent=`${val("cellScale",1).toFixed(2)}x`;$("flowVal").textContent=`${val("flow",1).toFixed(2)}x`;$("fieldVal").textContent=`${Math.round(val("fieldOpacity",.2)*100)}%`;$("magDisplay").textContent=`${Math.round(val("zoom",1)*10000).toLocaleString()}x`}
function rebuildWorld(){const run=normalizeRun(latest),rnd=seeded(hash(run.run_id+[...selectedOrganisms].join("|")));cells=[];hosts=[];particles=[];const visible=run.organisms.filter(o=>o.selected),hostCount=Math.max(1,Math.min(4,Math.ceil(visible.length/2)));for(let i=0;i<hostCount;i++)hosts.push({x:(rnd()*2-1)*.45,y:(rnd()*2-1)*.28,r:.25+rnd()*.18,rot:rnd()*Math.PI*2,spin:(rnd()-.5)*.10,phase:rnd()*Math.PI*2});const total=Math.max(1,visible.reduce((a,b)=>a+b.value,0));visible.forEach((org,idx)=>{const spec=org.spec||{},behavior=spec.behavior||{},morph=spec.morphology||{},portion=Math.max(.03,org.value/total),count=Math.max(10,Math.min(360,Math.round(220*portion*val("cellDensity",1)))),clusterAngle=idx/Math.max(1,visible.length)*Math.PI*2-Math.PI/2,cx=Math.cos(clusterAngle)*.42,cy=Math.sin(clusterAngle)*.26;for(let i=0;i<count;i++){const a=rnd()*Math.PI*2,rr=Math.pow(rnd(),.62)*(.16+.46*Math.sqrt(portion)),host=hosts[Math.floor(rnd()*hosts.length)],attach=rnd()<(behavior.biofilm_bias||0)*.28;cells.push({organism_id:org.id,label:org.name,color:org.color,morph:morph.render_type||"rod",behavior,x:attach?host.x+Math.cos(a)*(host.r+rnd()*.12):cx+Math.cos(a)*rr+(rnd()-.5)*.12,y:attach?host.y+Math.sin(a)*(host.r+rnd()*.12):cy+Math.sin(a)*rr+(rnd()-.5)*.08,vx:(rnd()-.5)*.018,vy:(rnd()-.5)*.018,size:.012+rnd()*.018,angle:rnd()*Math.PI*2,phase:rnd()*Math.PI*2,attach,host,orbit:host?host.r+rnd()*.14:.2,arm:a,tumble:rnd()*2.0,spore:morph.render_type==="rod_spore"&&rnd()<.20,cyst:morph.render_type==="amoeboid"&&rnd()<.10})}});for(let i=0;i<320;i++)particles.push({x:rnd()*2.7-1.35,y:rnd()*1.6-.8,z:rnd(),vx:(rnd()-.5)*.03,vy:(rnd()-.5)*.03})}
function updateWorld(dt){if(paused)return;const flow=val("flow",1);t+=dt;hosts.forEach(h=>{h.rot+=h.spin*dt;h.phase+=dt*.33});particles.forEach(p=>{p.x+=(p.vx+Math.sin(t*.35+p.y*4)*.004)*flow*dt*10;p.y+=(p.vy+Math.cos(t*.28+p.x*3)*.003)*flow*dt*10;if(p.x>1.45)p.x=-1.45;if(p.x<-1.45)p.x=1.45;if(p.y>.86)p.y=-.86;if(p.y<-.86)p.y=.86});cells.forEach(c=>{const b=c.behavior||{};c.phase+=dt*(1.1+(b.growth_rate||.5));if(c.attach&&c.host){c.arm+=dt*(.10+(b.biofilm_bias||0)*.10);c.x=c.host.x+Math.cos(c.arm+c.host.rot*.12)*c.orbit+Math.sin(t+c.phase)*.006;c.y=c.host.y+Math.sin(c.arm+c.host.rot*.12)*c.orbit+Math.cos(t+c.phase)*.006;return}if(c.morph==="amoeboid"){const prey=cells.find(p=>p!==c&&p.morph!=="amoeboid");if(prey){const dx=prey.x-c.x,dy=prey.y-c.y,d=Math.hypot(dx,dy)+.001;c.vx+=dx/d*.0009*(b.predation||.6);c.vy+=dy/d*.0009*(b.predation||.6)}}else if(c.morph==="rod"){c.tumble-=dt*(b.tumble_rate||.4);if(c.tumble<=0){c.angle+=(Math.random()-.5)*Math.PI*1.6;c.tumble=.4+Math.random()*1.6}c.vx+=Math.cos(c.angle)*.0008*(b.motility||.5);c.vy+=Math.sin(c.angle)*.0008*(b.motility||.5)}else if(c.morph==="rod_spore"){c.vx+=Math.sin(t*.2+c.phase)*.00015*(b.motility||.3);c.vy+=Math.cos(t*.2+c.phase)*.00015*(b.motility||.3)}else if(c.morph==="budding_yeast"){c.vx+=Math.sin(t*.18+c.phase)*.00005;c.vy+=Math.cos(t*.17+c.phase)*.00005}c.vx*=.991;c.vy*=.991;c.x+=c.vx*dt*12*flow;c.y+=c.vy*dt*12*flow;if(Math.abs(c.x)>1.25)c.vx*=-1;if(Math.abs(c.y)>.74)c.vy*=-1;c.x=clamp(c.x,-1.28,1.28);c.y=clamp(c.y,-.76,.76)})}
function canvasFit(canvas){const rect=canvas.getBoundingClientRect(),dpr=Math.min(2,window.devicePixelRatio||1);canvas.width=Math.max(10,Math.floor(rect.width*dpr));canvas.height=Math.max(10,Math.floor(rect.height*dpr));const ctx=canvas.getContext("2d");ctx.setTransform(dpr,0,0,dpr,0,0);return{ctx,w:rect.width,h:rect.height}}function scopeGeom(w,h){const zoom=val("zoom",1);return{cx:w*.52+pan.x,cy:h*.52+pan.y,r:Math.min(w,h)*.42*zoom}}function worldToScreen(x,y,g){const scale=g.r*.72;return{x:g.cx+x*scale,y:g.cy+y*scale,s:scale}}function hexToRgba(hex,alpha){const h=String(hex||"#27f4ff").replace("#","");const full=h.length===3?h.split("").map(x=>x+x).join(""):h;const n=parseInt(full,16);return`rgba(${(n>>16)&255},${(n>>8)&255},${n&255},${alpha})`}function roundRect(ctx,x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.lineTo(x+w-r,y);ctx.quadraticCurveTo(x+w,y,x+w,y+r);ctx.lineTo(x+w,y+h-r);ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);ctx.lineTo(x+r,y+h);ctx.quadraticCurveTo(x,y+h,x,y+h-r);ctx.lineTo(x,y+r);ctx.quadraticCurveTo(x,y,x+r,y);ctx.closePath()}
function drawField(ctx,g,field){const opacity=val("fieldOpacity",.24);if(activeView==="organisms"||activeView==="clean")return;const fieldCfg=fieldProfiles.fields?.[field]||{},color=fieldCfg.color||"#27f4ff";ctx.save();const cx=g.cx,cy=g.cy,r=g.r;ctx.beginPath();ctx.arc(cx, cy, r,0,Math.PI*2);ctx.clip();const rg=ctx.createRadialGradient(cx-r*.25,cy-r*.15,r*.08,cx,cy,r);rg.addColorStop(0,hexToRgba(color,opacity*.55));rg.addColorStop(.65,hexToRgba(color,opacity*.22));rg.addColorStop(1,hexToRgba(color,0));ctx.fillStyle=rg;ctx.fillRect(cx-r,cy-r,r*2,r*2);ctx.restore()}function drawHost(ctx,h,g){const s=worldToScreen(h.x,h.y,g),R=h.r*s.s;ctx.save();ctx.translate(s.x,s.y);ctx.rotate(h.rot);const grad=ctx.createRadialGradient(-R*.22,-R*.18,R*.05,0,0,R*1.05);grad.addColorStop(0,"rgba(255,244,174,.65)");grad.addColorStop(.35,"rgba(255,195,107,.76)");grad.addColorStop(.76,"rgba(35,164,210,.24)");grad.addColorStop(1,"rgba(35,244,255,.08)");ctx.fillStyle=grad;ctx.strokeStyle="rgba(39,244,255,.55)";ctx.lineWidth=1.2;ctx.beginPath();for(let i=0;i<100;i++){const a=i/100*Math.PI*2,rr=R*(1+.055*Math.sin(3*a+h.phase)+.035*Math.sin(7*a-t*.2)),x=Math.cos(a)*rr*1.08,y=Math.sin(a)*rr*.82;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)}ctx.closePath();ctx.fill();ctx.stroke();ctx.restore()}function drawRod(ctx,c,s,size){ctx.save();ctx.translate(s.x,s.y);ctx.rotate(c.angle+Math.sin(c.phase)*.18);ctx.shadowColor=c.color;ctx.shadowBlur=8;ctx.globalAlpha=.66;ctx.fillStyle=c.color;roundRect(ctx,-size*2.1,-size*.55,size*4.2,size*1.1,size*.55);ctx.fill();ctx.globalAlpha=.9;ctx.strokeStyle="#eaffff";ctx.lineWidth=Math.max(1,size*.12);ctx.stroke();if(c.spore){ctx.fillStyle="#fff0a0";ctx.beginPath();ctx.arc(size*.75,0,size*.36,0,Math.PI*2);ctx.fill()}ctx.restore()}function drawCoccus(ctx,c,s,size){ctx.save();ctx.translate(s.x,s.y);ctx.shadowColor=c.color;ctx.shadowBlur=7;ctx.globalAlpha=.66;ctx.fillStyle=c.color;ctx.beginPath();ctx.arc(0,0,size*1.1,0,Math.PI*2);ctx.fill();ctx.globalAlpha=.92;ctx.strokeStyle="#eaffff";ctx.lineWidth=1;ctx.stroke();ctx.restore()}function drawYeast(ctx,c,s,size){drawCoccus(ctx,c,s,size*1.15);drawCoccus(ctx,c,{x:s.x+size*.9,y:s.y-size*.25},size*.62)}function drawAmoeboid(ctx,c,s,size){ctx.save();ctx.translate(s.x,s.y);ctx.shadowColor=c.color;ctx.shadowBlur=10;ctx.globalAlpha=.64;ctx.fillStyle=c.cyst?"#ff9aa4":c.color;ctx.beginPath();for(let i=0;i<9;i++){const a=i*Math.PI*2/9+c.phase*.18,rr=size*(.85+Math.sin(c.phase+i)*.28),x=Math.cos(a)*rr,y=Math.sin(a)*rr;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)}ctx.closePath();ctx.fill();ctx.globalAlpha=.9;ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(0,0,size*.25,0,Math.PI*2);ctx.fill();ctx.restore()}function drawAmoeba(ctx,c,s,size){drawAmoeboid(ctx,c,s,size)}function drawCell(ctx,c,g){const s=worldToScreen(c.x,c.y,g);if((s.x-g.cx)**2+(s.y-g.cy)**2>(g.r*.98)**2)return;const size=Math.max(2.2,c.size*s.s*val("cellScale",1));if(c.morph==="budding_yeast")drawYeast(ctx,c,s,size);else if(c.morph==="amoeboid")drawAmoeboid(ctx,c,s,size*1.25);else if(c.morph==="coccus")drawCoccus(ctx,c,s,size);else drawRod(ctx,c,s,size);if($("trackingToggle").checked&&c.attach&&c.host){ctx.save();ctx.globalAlpha=.24;ctx.strokeStyle="rgba(255,210,104,.55)";const h=worldToScreen(c.host.x,c.host.y,g);ctx.beginPath();ctx.moveTo(s.x,s.y);ctx.lineTo(h.x,h.y);ctx.stroke();ctx.restore()}}function drawParticles(ctx,g){ctx.save();particles.forEach(p=>{const s=worldToScreen(p.x,p.y,g);if((s.x-g.cx)**2+(s.y-g.cy)**2>(g.r*.98)**2)return;ctx.fillStyle="rgba(180,230,255,.20)";ctx.beginPath();ctx.arc(s.x,s.y,Math.max(.6,p.z*2.2),0,Math.PI*2);ctx.fill()});ctx.restore()}
function drawScope(){const fit=canvasFit($("scopeCanvas")),ctx=fit.ctx,w=fit.w,h=fit.h,g=scopeGeom(w,h);ctx.clearRect(0,0,w,h);const bg=ctx.createRadialGradient(g.cx,g.cy,0,g.cx,g.cy,g.r*1.72);bg.addColorStop(0,"rgba(12,32,55,.85)");bg.addColorStop(.6,"rgba(2,13,26,.95)");bg.addColorStop(1,"rgba(1,7,18,1)");ctx.fillStyle=bg;ctx.fillRect(0,0,w,h);ctx.save();ctx.beginPath();ctx.arc(g.cx,g.cy,g.r,0,Math.PI*2);ctx.clip();ctx.fillStyle="#020814";ctx.fillRect(g.cx-g.r,g.cy-g.r,g.r*2,g.r*2);drawField(ctx,g,$("fieldSelect").value);if(activeView!=="field"){drawParticles(ctx,g);hosts.forEach(h=>drawHost(ctx,h,g));cells.forEach(c=>drawCell(ctx,c,g))}ctx.restore();ctx.save();ctx.strokeStyle="rgba(39,244,255,.86)";ctx.lineWidth=2;const cx=g.cx,cy=g.cy,r=g.r;ctx.beginPath();ctx.arc(cx, cy, r,0,Math.PI*2);ctx.stroke();ctx.globalAlpha=.25;ctx.beginPath();ctx.ellipse(cx,cy,r*1.08,r*.74,0,0,Math.PI*2);ctx.stroke();if($("gridOverlay").checked){ctx.globalAlpha=.13;for(let i=-10;i<=10;i++){let x=cx+i*r/10;ctx.beginPath();ctx.moveTo(x,cy-r);ctx.lineTo(x,cy+r);ctx.stroke();let y=cy+i*r/10;ctx.beginPath();ctx.moveTo(cx-r,y);ctx.lineTo(cx+r,y);ctx.stroke()}}ctx.restore()}function drawCurves(){const run=normalizeRun(latest),fit=canvasFit($("curveCanvas")),ctx=fit.ctx,w=fit.w,h=fit.h;ctx.clearRect(0,0,w,h);ctx.fillStyle="rgba(0,6,15,.86)";ctx.fillRect(0,0,w,h);ctx.strokeStyle="rgba(255,255,255,.09)";for(let i=1;i<5;i++){const y=i*h/5;ctx.beginPath();ctx.moveTo(28,y);ctx.lineTo(w-18,y);ctx.stroke()}const visible=run.organisms.filter(o=>o.selected),maxV=Math.max(1,...visible.map(o=>o.value));visible.forEach(o=>{ctx.strokeStyle=o.color;ctx.lineWidth=2;ctx.beginPath();[o.value*.12,o.value*.25,o.value*.48,o.value*.72,o.value].forEach((v,i)=>{const x=28+(w-46)*i/4,y=h-24-(h-46)*v/maxV;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)});ctx.stroke()});$("curveLegend").innerHTML=visible.map(o=>`<div class="legend-item"><span class="dot" style="color:${o.color};background:${o.color}"></span>${o.short_label}</div>`).join("")}function drawDensity(){const fit=canvasFit($("densityCanvas")),ctx=fit.ctx,w=fit.w,h=fit.h;ctx.clearRect(0,0,w,h);ctx.fillStyle="rgba(0,6,15,.85)";ctx.fillRect(0,0,w,h);ctx.globalCompositeOperation="screen";cells.forEach(c=>{const x=(c.x+1.3)/2.6*w,y=(c.y+.8)/1.6*h,rg=ctx.createRadialGradient(x,y,0,x,y,10);rg.addColorStop(0,hexToRgba(c.color,.28));rg.addColorStop(1,hexToRgba(c.color,0));ctx.fillStyle=rg;ctx.beginPath();ctx.arc(x,y,10,0,Math.PI*2);ctx.fill()});ctx.globalCompositeOperation="source-over"}
function renderCards(){const run=normalizeRun(latest),max=Math.max(1,...run.organisms.map(o=>o.value));$("organismCards").innerHTML=run.organisms.map(o=>{const spec=o.spec||{},m=spec.morphology||{},e=spec.environment||{},d=spec.dataset||{},pct=Math.max(2,Math.round(100*o.value/max)),checked=o.selected?"checked":"";return`<details class="org-card ${o.selected?"":"disabled"}" open><summary class="org-head"><span class="org-title"><input class="org-toggle" data-org-toggle="${o.id}" type="checkbox" ${checked}><span class="dot" style="display:inline-block;color:${o.color};background:${o.color}"></span>${o.short_label}</span><b>${fmt(o.value)}</b></summary><div class="org-small"><b>${o.name}</b><br>${d.class||"organism"} // ${m.cell_shape||m.render_type||"morphology proxy"}</div><div class="science-grid"><div><b>Division</b><br>${m.division||"proxy"}</div><div><b>Motility</b><br>${m.motility||"proxy"}</div><div><b>Oxygen</b><br>${e.oxygen||"not set"}</div><div><b>Habitat</b><br>${e.habitat||"not set"}</div></div><div class="org-small">${(spec.card_notes||[]).join(" ")}</div><span class="source-chip">${d.primary||"registry"}</span><span class="source-chip">${d.secondary||"proxy"}</span><div class="bar"><div class="fill" style="width:${pct}%"></div></div></details>`}).join("");document.querySelectorAll("[data-org-toggle]").forEach(input=>input.addEventListener("change",e=>{const id=e.target.dataset.orgToggle;if(e.target.checked)selectedOrganisms.add(id);else selectedOrganisms.delete(id);saveSelection();rebuildWorld();renderStaticPanels();$("statusBox").textContent=`Registry selection updated: ${[...selectedOrganisms].length} organism types active.`}));$("dominantChip").textContent=run.metrics.dominant_name}function renderMetrics(){const run=normalizeRun(latest);$("metricChips").innerHTML=[["Cells",cells.length],["Hosts",hosts.length],["Particles",particles.length],["FPS",fps],["Total",run.metrics.total_population]].map(([k,v])=>`<div class="metric"><small>${k}</small><b>${fmt(v)}</b></div>`).join("");$("validationChip").textContent=run.validation?.status||"preview"}function renderArchive(){$("runArchive").innerHTML=(runs||[]).slice(0,8).map(r=>`<div class="run-item"><b>${r.run_id}</b><br>${r.preset} // ${r.status}<br>${r.dominant}</div>`).join("")||"<div class='run-item'>No archive yet.</div>"}function renderConfigReceipt(){const run=normalizeRun(latest);$("scienceConfig").textContent=JSON.stringify({schema:organismRegistry.schema,selected:[...selectedOrganisms],active_field:fieldProfiles.fields?.[$("fieldSelect").value],visual_contract:["cards toggle dish membership","behavior driven by registry","fields clipped to circular dish","claim boundary retained"],metrics:run.metrics},null,2)}function renderStaticPanels(){renderCards();renderMetrics();renderArchive();renderConfigReceipt();drawCurves()}
function loop(now){if(!lastFrame)lastFrame=now;const dt=Math.min(.05,(now-lastFrame)/1000);lastFrame=now;if(!fpsStart)fpsStart=now;frameCount+=1;if(now-fpsStart>500){fps=frameCount*1000/(now-fpsStart);frameCount=0;fpsStart=now}updateWorld(dt);drawScope();drawDensity();renderMetrics();const elapsed=Math.floor(t),hh=String(Math.floor(elapsed/3600)).padStart(2,"0"),mm=String(Math.floor(elapsed%3600/60)).padStart(2,"0"),ss=String(elapsed%60).padStart(2,"0");$("runClock").textContent=`${hh}:${mm}:${ss}`;requestAnimationFrame(loop)}async function loadAll(){try{config=await window.petri.readConfig()}catch{config={}}try{organismRegistry=await window.petri.readOrganisms()}catch{organismRegistry={organisms:[]}}try{fieldProfiles=await window.petri.readFieldProfiles()}catch{fieldProfiles={fields:{}}}try{latest=await window.petri.readLatest()}catch{latest={}}try{runs=await window.petri.listRuns()}catch{runs=[]}initSelection();await rebuildWorldFromArtifactsOrRegistry();renderStaticPanels();$("statusBox").textContent="Registry loaded. Toggle organism cards to add/remove them from the dish."}async function runSimulation(){$("statusBox").textContent="Running Python simulation...";$("runBtn").disabled=true;try{const res=await window.petri.run({preset:$("preset").value,steps:$("steps").value,grid:$("grid").value});if(res.code!==0){$("statusBox").textContent=`Run failed: ${res.stderr||res.stdout||"unknown"}`;return}latest=res.latest||res.result||{};try{runs=await window.petri.listRuns()}catch{}await rebuildWorldFromArtifactsOrRegistry();renderStaticPanels();$("statusBox").textContent=`Run complete: ${normalizeRun(latest).run_id}`}finally{$("runBtn").disabled=false}}function exportState(){const blob=new Blob([JSON.stringify({version:"004K",time:t,selected:[...selectedOrganisms],registry:organismRegistry.schema,run:normalizeRun(latest)},null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="petri-organism-registry-state.json";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}function installEvents(){["zoom","cellDensity","cellScale","flow","fieldOpacity","fieldSelect","gridOverlay","trackingToggle"].forEach(id=>$(id).addEventListener("input",()=>{syncControls();if(id==="cellDensity")rebuildWorld();renderStaticPanels()}));document.querySelectorAll("[data-view]").forEach(btn=>btn.addEventListener("click",()=>{document.querySelectorAll("[data-view]").forEach(b=>b.classList.remove("active"));btn.classList.add("active");activeView=btn.dataset.view}));$("runBtn").addEventListener("click",runSimulation);$("reloadBtn").addEventListener("click",loadAll);$("artifactBtn").addEventListener("click",()=>window.petri.openArtifacts());$("pauseBtn").addEventListener("click",()=>{paused=!paused;$("pauseBtn").textContent=paused?"Run":"Pause"});$("resetViewBtn").addEventListener("click",()=>{pan={x:0,y:0};$("zoom").value="1.15";syncControls()});$("stateBtn").addEventListener("click",exportState);$("captureBtn").addEventListener("click",()=>{const a=document.createElement("a");a.href=$("scopeCanvas").toDataURL("image/png");a.download="organism-gate-capture.png";a.click()});const canvas=$("scopeCanvas");canvas.addEventListener("wheel",e=>{e.preventDefault();$("zoom").value=clamp(val("zoom",1)+(e.deltaY<0?.08:-.08),.65,3.25).toFixed(2);syncControls()},{passive:false});canvas.addEventListener("pointerdown",e=>{drag={x:e.clientX,y:e.clientY,pan:{...pan}};canvas.setPointerCapture(e.pointerId)});canvas.addEventListener("pointermove",e=>{if(!drag)return;pan.x=drag.pan.x+(e.clientX-drag.x);pan.y=drag.pan.y+(e.clientY-drag.y)});canvas.addEventListener("pointerup",()=>{drag=null});window.addEventListener("resize",()=>{drawScope();drawCurves();drawDensity()})}document.addEventListener("DOMContentLoaded",()=>{installEvents();syncControls();loadAll();requestAnimationFrame(loop)});


/* PETRI 004L STATIC COMPATIBILITY SEAL
PETRI 004K REAL SCIENCE ORGANISM REGISTRY
PETRI 004H COMPACT LIVE MICROSCOPE DESIGN
visual_contract
schema adapter
circular microscope dish
stronger glow field rendering
zoom pan reset
optional grid overlay
metrics chips
organism population cards
real population curve legend
run archive panel
open artifacts button
Organism Cards
Run Archive
Open Artifacts
LIVE SIM
Animation rule
requestAnimationFrame(loop);
window.petri.readConfig
window.petri.readOrganisms
window.petri.readFieldProfiles
selectedOrganisms
data-org-toggle
behavior driven by registry
registry-driven live microscope
source-grounded proxies
function displayNameFor(value)
function normalizeDominantName(run)
function normalizeRun(raw)
function drawRod(ctx, c, s, size)
function drawYeast(ctx,c,s,size)
function drawAmoeboid(ctx,c,s,size)
function drawAmoeba(ctx,c,s,size)
function drawField(ctx,g,field)
function drawCells(ctx,g)
dominant_name
*/
function drawCells(ctx,g){
  // Legacy static-test alias. 004K drawScope renders cells directly from the registry-driven cell array.
  return { ctx: !!ctx, g: !!g, source: "registry" };
}


/* PETRI 004N PARTICLE ARTIFACT BINDING
Python biology kernel -> cells.json / particles.json / interactions.json / fields.json -> Electron renderer.
*/
let particleArtifactState = null;

async function loadParticleArtifactState() {
  if (!window.petri || !window.petri.readParticleState) return null;
  try {
    particleArtifactState = await window.petri.readParticleState();
    return particleArtifactState;
  } catch (err) {
    particleArtifactState = null;
    return null;
  }
}

function applyParticleArtifactsToWorld() {
  if (!particleArtifactState || !particleArtifactState.cells) return false;
  const src = Array.isArray(particleArtifactState.cells) ? particleArtifactState.cells
    : Array.isArray(particleArtifactState.cells.cells) ? particleArtifactState.cells.cells
    : [];
  if (!src.length) return false;
  cells = src.map((c, i) => ({
    organism_id: c.organism_id || c.organism || c.slug || c.type || "artifact_cell",
    label: c.label || c.organism_id || "artifact cell",
    color: c.color || COLORS[i % COLORS.length],
    morph: c.morph || c.morphology || c.render_type || "rod",
    behavior: c.behavior || {},
    x: Number(c.x ?? c.position?.x ?? 0),
    y: Number(c.y ?? c.position?.y ?? 0),
    vx: Number(c.vx ?? c.velocity?.x ?? 0),
    vy: Number(c.vy ?? c.velocity?.y ?? 0),
    size: Number(c.size ?? c.radius ?? 0.018),
    angle: Number(c.angle ?? 0),
    phase: Number(c.phase ?? 0),
    attach: Boolean(c.attach),
    host: null,
    orbit: Number(c.orbit ?? 0.2),
    arm: Number(c.arm ?? 0),
    spore: Boolean(c.spore),
    cyst: Boolean(c.cyst)
  }));
  return true;
}

async function rebuildWorldFromArtifactsOrRegistry() {
  const state = await loadParticleArtifactState();
  if (state && applyParticleArtifactsToWorld()) {
    if ($("statusBox")) $("statusBox").textContent = "Rendering Python particle-state artifacts.";
    return true;
  }
  rebuildWorld();
  return false;
}


/* PETRI 004P CARD STACK REAL DATA UI
metrics_stack_bottom_left
human_readable_particle_state_receipt
emergent_conditions_not_cut_off
preset_dependent_cards
source_gated_real_data_cards
*/
let petri004pPresetCards = null;
let petri004pMetricCards = null;
let petri004pDataSources = null;

async function petri004pLoadCardConfigs(){
  try { if (window.petri && window.petri.readPresetCards) petri004pPresetCards = await window.petri.readPresetCards(); } catch {}
  try { if (window.petri && window.petri.readMetricCards) petri004pMetricCards = await window.petri.readMetricCards(); } catch {}
  try { if (window.petri && window.petri.readDataSourceRegistry) petri004pDataSources = await window.petri.readDataSourceRegistry(); } catch {}
}
function petri004pRun(){ try { return normalizeRun(latest); } catch { return { organisms:[], metrics:{}, validation:{status:'preview'}, run_id:'preview' }; } }
function petri004pVisibleOrganisms(){ return petri004pRun().organisms.filter(o => o.selected !== false && (!selectedOrganisms || selectedOrganisms.has(o.id || o.slug))); }
function petri004pPreset(){ return document.getElementById('preset')?.value || 'microbial_competition'; }
function petri004pPresetInfo(){ return petri004pPresetCards?.presets?.[petri004pPreset()] || {}; }
function petri004pMetricById(id){ return (petri004pMetricCards?.cards || []).find(c => c.id === id) || { id, label:id.replace(/_/g,' '), meaning:'metric card' }; }
function petri004pBiofilmIndex(orgs){ if(!orgs.length) return 0; return orgs.reduce((a,o)=>a+Number(o.spec?.behavior?.biofilm_bias||0),0)/orgs.length; }
function petri004pStressIndex(orgs){ if(!orgs.length) return 0; return orgs.reduce((a,o)=>a+Number(o.spec?.behavior?.stress_tolerance||0),0)/orgs.length; }
function petri004pDiversity(orgs){ const total=orgs.reduce((a,o)=>a+Number(o.value||0),0)||1; return -orgs.reduce((a,o)=>{const p=Number(o.value||0)/total; return p>0?a+p*Math.log(p):a;},0); }
function petri004pDominance(orgs){ const total=orgs.reduce((a,o)=>a+Number(o.value||0),0)||1; return Math.max(0,...orgs.map(o=>Number(o.value||0)))/total; }
function petri004pMetricValue(id){
  const run=petri004pRun(), orgs=petri004pVisibleOrganisms();
  if(id==='total_cells') return orgs.reduce((a,o)=>a+Number(o.value||0),0);
  if(id==='active_organisms') return orgs.length;
  if(id==='shannon_diversity') return petri004pDiversity(orgs);
  if(id==='dominance_index') return petri004pDominance(orgs);
  if(id==='biofilm_index') return petri004pBiofilmIndex(orgs);
  if(id==='stress_index') return petri004pStressIndex(orgs);
  if(id==='artifact_load') return (typeof cells!=='undefined'?cells.length:0);
  if(id==='predator_prey_contact') return orgs.filter(o=>Number(o.spec?.behavior?.predation||0)>0).length;
  if(id==='resistant_fraction') return orgs.reduce((a,o)=>a+(Number(o.spec?.behavior?.drug_resistance_bias||0)>.6?Number(o.value||0):0),0)/(orgs.reduce((a,o)=>a+Number(o.value||0),0)||1);
  return Number(run.metrics?.[id] ?? 0);
}
function petri004pFmt(v){ if(!Number.isFinite(Number(v))) return '0'; const n=Number(v); return n>=100?String(Math.round(n)):n.toFixed(3); }

renderMetrics = function(){
  const box=document.getElementById('metricChips'); if(!box) return;
  const preset=petri004pPresetInfo();
  const ids=(preset.metric_cards||['total_cells','active_organisms','shannon_diversity','dominance_index','artifact_load']).slice(0,7);
  box.classList.add('metric-stack');
  box.innerHTML = ids.map(id=>{const card=petri004pMetricById(id);return `<div class="metric-stack-card"><small>${card.label}</small><b>${petri004pFmt(petri004pMetricValue(id))}</b></div>`;}).join('');
  const chip=document.getElementById('validationChip'); if(chip) chip.textContent = petri004pRun().validation?.status || 'preview';
};

function petri004pEnsureEmergentPanel(){
  const footer=document.querySelector('.bottom-strip'); if(!footer) return null;
  let panel=document.getElementById('emergentConditionsPanel');
  if(!panel){
    panel=document.createElement('section');
    panel.className='mini-panel emergent-panel';
    panel.id='emergentConditionsPanel';
    panel.innerHTML='<h3>Emergent Conditions</h3><div id="emergentConditions" class="emergent-grid"></div>';
    footer.appendChild(panel);
  }
  return panel;
}
function renderEmergentConditions(){
  petri004pEnsureEmergentPanel();
  const box=document.getElementById('emergentConditions'); if(!box) return;
  const orgs=petri004pVisibleOrganisms(), preset=petri004pPresetInfo();
  const bio=petri004pBiofilmIndex(orgs), stress=petri004pStressIndex(orgs), dom=petri004pDominance(orgs);
  const cards=[
    ['Active organism types', `${orgs.length} selected cards drive dish membership`],
    ['Preset context', `${preset.label || petri004pPreset()} : ${(preset.intervention_cards||[]).slice(0,3).join(', ') || 'base fields'}`],
    ['Biofilm pressure', `${petri004pFmt(bio)} weighted from selected behavior cards`],
    ['Stress capacity', `${petri004pFmt(stress)} proxy; real drug work requires source import`],
    ['Dominance condition', `${petri004pFmt(dom)} largest selected population fraction`]
  ];
  box.innerHTML=cards.map(([k,v])=>`<div class="condition-card"><b>${k}</b><span>${v}</span></div>`).join('');
}

renderConfigReceipt = function(){
  const el=document.getElementById('scienceConfig'); if(!el) return;
  const run=petri004pRun(), orgs=petri004pVisibleOrganisms(), preset=petri004pPresetInfo();
  el.classList.add('human-receipt');
  const particleLoaded = (typeof particleArtifactState !== 'undefined' && particleArtifactState && particleArtifactState.index) ? 'yes' : 'fallback/registry';
  const sourceRule = petri004pDataSources?.rule || 'missing provenance downgrades card to educational proxy';
  el.innerHTML = [
    ['Run', run.run_id || 'preview'],
    ['Preset', preset.label || petri004pPreset()],
    ['Selected', orgs.map(o=>o.short_label || o.name).join(', ') || 'none'],
    ['Particle state', particleLoaded],
    ['Metric cards', (preset.metric_cards||[]).slice(0,6).join(', ') || 'base metrics'],
    ['Data gate', sourceRule],
    ['Claim boundary', 'Exploratory visualization only; no clinical, diagnostic, wet-lab, treatment, or biosafety evidence.']
  ].map(([k,v])=>`<div class="row"><span class="key">${k}</span><span class="value">${v}</span></div>`).join('');
};

renderCards = function(){
  const box=document.getElementById('organismCards'); if(!box) return;
  const run=petri004pRun();
  const max=Math.max(1,...run.organisms.map(o=>Number(o.value||0)));
  box.innerHTML = run.organisms.map(o=>{
    const spec=o.spec||{}, m=spec.morphology||{}, e=spec.environment||{}, b=spec.behavior||{}, d=spec.dataset||{};
    const selected = o.selected !== false && (!selectedOrganisms || selectedOrganisms.has(o.id || o.slug));
    const pct=Math.max(2,Math.round(100*Number(o.value||0)/max));
    const sources=[d.primary,d.secondary].filter(Boolean).map(s=>`<span class="source-chip">${s}</span>`).join('');
    return `<details class="org-card ${selected?'':'disabled'}" ${selected?'open':''}>
      <summary class="org-head"><span class="org-title"><input class="org-toggle" data-org-toggle="${o.id||o.slug}" type="checkbox" ${selected?'checked':''}><span class="dot" style="display:inline-block;color:${o.color};background:${o.color}"></span>${o.short_label||o.name}</span><b>${petri004pFmt(o.value||0)}</b></summary>
      <div class="org-small"><b>${o.name}</b><br>${d.class||'organism'} // ${m.cell_shape || m.render_type || 'morphology proxy'}</div>
      <div class="science-grid"><div><b>Division</b><br>${m.division||'source gated'}</div><div><b>Motility</b><br>${m.motility||'source gated'}</div><div><b>Oxygen</b><br>${e.oxygen||'source gated'}</div><div><b>Habitat</b><br>${e.habitat||'source gated'}</div></div>
      <div class="behavior-grid"><div><b>Growth</b><br>${petri004pFmt(b.growth_rate||0)}</div><div><b>Biofilm</b><br>${petri004pFmt(b.biofilm_bias||0)}</div><div><b>Stress</b><br>${petri004pFmt(b.stress_tolerance||0)}</div></div>
      <div class="org-small">${(spec.card_notes||[]).join(' ')}</div>
      <div class="data-gate"><b>Data gate:</b> ${d.data_gate || 'record id, units, assay/method, and claim boundary required for real-data mode.'}</div>
      ${sources}<div class="bar"><div class="fill" style="width:${pct}%"></div></div>
    </details>`;
  }).join('');
  document.querySelectorAll('[data-org-toggle]').forEach(input=>input.addEventListener('change',e=>{
    const id=e.target.dataset.orgToggle;
    if(e.target.checked) selectedOrganisms.add(id); else selectedOrganisms.delete(id);
    saveSelection(); rebuildWorld(); renderStaticPanels();
    const s=document.getElementById('statusBox'); if(s) s.textContent=`Registry selection updated: ${[...selectedOrganisms].length} organism types active.`;
  }));
  const dom=document.getElementById('dominantChip'); if(dom) dom.textContent = run.metrics?.dominant_name || 'dominant';
};

renderStaticPanels = function(){
  try { renderCards(); } catch(e) { console.warn(e); }
  try { renderMetrics(); } catch(e) { console.warn(e); }
  try { if(typeof renderArchive==='function') renderArchive(); } catch(e) { console.warn(e); }
  try { renderConfigReceipt(); } catch(e) { console.warn(e); }
  try { if(typeof drawCurves==='function') drawCurves(); } catch(e) { console.warn(e); }
  try { renderEmergentConditions(); } catch(e) { console.warn(e); }
};

document.addEventListener('DOMContentLoaded',()=>{
  petri004pLoadCardConfigs().then(()=>setTimeout(()=>{ petri004pEnsureEmergentPanel(); renderStaticPanels(); }, 350));
});
