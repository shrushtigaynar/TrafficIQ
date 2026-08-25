// Smart City AI - app.js
const API='http://127.0.0.1:8000';
let blueprintData=null,_mapScale=1,currentView='top';

/**
 * Trigger autonomous agent analysis
 * Called when user clicks the agent button or via auto-trigger
 */
function triggerAgentAnalysis(){
  const city=(document.getElementById('navInput').value||document.getElementById('heroInput').value).trim();
  if(!city){
    showToast('Please analyze a city first');
    return;
  }
  if(typeof runAgentAnalysis === 'function'){
    runAgentAnalysis(city);
  }else{
    showToast('Agent system not loaded');
  }
}

/* ── TABS ── */
function switchTab(tab){
  ['dashboard','blueprint','analytics','reports'].forEach(t=>{
    document.getElementById('tab-'+t).classList.toggle('active',t===tab);
  });
  const show=(id,cond)=>{ const el=document.getElementById(id); if(el) el.style.display=cond?'flex':'none'; };
  show('heroSection',       tab==='dashboard'&&!blueprintData);
  show('blueprintSection',  tab==='blueprint'&&!!blueprintData);
  show('analyticsSection',  tab==='analytics'&&!!blueprintData);
  show('reportsSection',    tab==='reports'&&!!blueprintData);
  if(tab!=='dashboard'&&!blueprintData) showToast('Analyse a city first.');
}

/* ── LOADING STEPS ── */
const LS=['ls1','ls2','ls3','ls4','ls5','ls6'];
let lsTimer=null,lsCur=0;
function startLoadSteps(){
  lsCur=0;
  LS.forEach((id,i)=>{ const el=document.getElementById(id); el.className='load-step'; el.querySelector('.load-step-icon').textContent=i+1; });
  advLS();
}
function advLS(){
  if(lsCur>0) doneLS(LS[lsCur-1]);
  if(lsCur<LS.length){ document.getElementById(LS[lsCur]).classList.add('active'); lsCur++; lsTimer=setTimeout(advLS,7000); }
}
function doneLS(id){ const el=document.getElementById(id); el.className='load-step done'; el.querySelector('.load-step-icon').textContent='checkmark'; }
function finishLS(){ clearTimeout(lsTimer); LS.forEach(id=>doneLS(id)); }

/* ── ANALYSIS ── */
async function startAnalysis(){
  const city=(document.getElementById('navInput').value||document.getElementById('heroInput').value).trim();
  if(!city){ showToast('Please enter a city name.'); return; }
  document.getElementById('loadingOverlay').style.display='flex';
  ['analyseBtn','heroBtn'].forEach(id=>{ const el=document.getElementById(id); if(el) el.disabled=true; });
  startLoadSteps();
  try{
    const res=await fetch(API+'/analyse-city',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({city_name:city})});
    const data=await res.json();
    if(!res.ok){ const d=data.detail||{}; throw new Error('['+(d.failed_step||'error')+'] '+(d.error||res.statusText)); }
    finishLS();
    setTimeout(()=>{ document.getElementById('loadingOverlay').style.display='none'; blueprintData=data.blueprint; renderAll(blueprintData); },600);
  }catch(e){
    document.getElementById('loadingOverlay').style.display='none';
    showToast('Analysis failed: '+e.message);
  }finally{
    ['analyseBtn','heroBtn'].forEach(id=>{ const el=document.getElementById(id); if(el) el.disabled=false; });
  }
}
document.getElementById('heroInput').addEventListener('keydown',e=>{ if(e.key==='Enter') startAnalysis(); });
document.getElementById('navInput').addEventListener('keydown',e=>{ if(e.key==='Enter') startAnalysis(); });

/* ── RENDER ALL ── */
function renderAll(bp){
  renderSidebar(bp); renderRightPanel(bp); renderBlueprintMap(bp); renderAnalytics(bp); renderReports(bp);
  document.getElementById('heroSection').style.display='none';
  document.getElementById('blueprintSection').style.display='flex';
  document.getElementById('sidebarEmpty').style.display='none';
  document.getElementById('sidebarContent').style.display='flex';
  document.getElementById('rightEmpty').style.display='none';
  document.getElementById('rightContent').style.display='block';
  ['dashboard','blueprint','analytics','reports'].forEach(t=>document.getElementById('tab-'+t).classList.remove('active'));
  document.getElementById('tab-blueprint').classList.add('active');
}

/* ── SIDEBAR ── */
function renderSidebar(bp){
  const score=(bp.overall_score||0)*10;
  const color=score>=70?'var(--green)':score>=50?'var(--orange)':'var(--red)';
  const rating=score>=70?'Good':score>=50?'Moderate':'Critical';
  const circ=276,offset=circ-(score/100)*circ;
  const fg=document.getElementById('sideRingFg');
  fg.style.stroke=color; fg.style.strokeDashoffset=circ;
  document.getElementById('sideRingScore').textContent=score.toFixed(0);
  document.getElementById('sideRingRating').textContent=rating;
  document.getElementById('sideRingRating').style.color=color;
  setTimeout(()=>{ fg.style.strokeDashoffset=offset; },300);
  const areas=bp.areas||[];
  const stats=[['person','Total Areas',areas.length.toString()],['building','City',bp.city_name||'Unknown'],['rupee','Traffic Level',bp.overall_level||'N/A'],['clock','Timestamp',(bp.timestamp||'').substring(11,16)],['chart','Best Areas',(bp.best_areas||[]).length.toString()]];
  const icons={'person':'👤','building':'🏢','rupee':'₹','clock':'⏱','chart':'📈'};
  document.getElementById('quickStats').innerHTML=stats.map(([k,label,val])=>`<div class="stat-card"><div class="stat-icon">${icons[k]}</div><div class="stat-info"><div class="stat-label">${label}</div><div class="stat-value">${val}</div></div></div>`).join('');
  const worstAreas=bp.worst_areas||[];
  document.getElementById('sideProblems').innerHTML=worstAreas.length?worstAreas.map((a,i)=>{
    const cls=a.congestion_level==='CRITICAL'?'sev-c':a.congestion_level==='HIGH'?'sev-h':'sev-l';
    return `<div class="prob-mini"><div class="prob-mini-header"><div class="prob-mini-name">${a.area_name||''}</div><span class="sev ${cls}">${a.congestion_level||'N/A'}</span></div><div class="prob-mini-desc">Score: ${a.congestion_score||0}/10</div></div>`;
  }).join(''):'<div style="font-size:.75rem;color:var(--green)">All areas clear</div>';
  document.getElementById('phaseStepper').innerHTML='<div style="font-size:.75rem;color:var(--muted)">Real-time Traffic Intelligence System Ready</div>';
}

/* ── RIGHT PANEL ── */
function renderRightPanel(bp){
  const areas=bp.areas||[];
  const bestAreas=bp.best_areas||[];
  const worstAreas=bp.worst_areas||[];
  const predictions=bp.predictions||{};
  const llmInsights=bp.llm_insights||{};
  
  // Area Quality Comparison
  const areaCount=Math.min(4,areas.length);
  const topAreas=areas.sort((a,b)=>(b.congestion_score||0)-(a.congestion_score||0)).slice(0,areaCount);
  const areaMax=Math.max(...topAreas.map(a=>a.congestion_score||0),1);
  document.getElementById('aqChart').innerHTML=topAreas.map(a=>{
    const v=a.congestion_score||0,pct=(v/areaMax)*100,color=v>7?'var(--red)':v>4?'var(--orange)':'var(--green)';
    return `<div class="aq-bar-row"><div class="aq-label">${a.area_name||'Area'}</div><div class="aq-bar-bg"><div class="aq-bar-fill" style="width:${pct}%;background:${color}"></div></div><div class="aq-val">${v.toFixed(1)}</div></div>`;
  }).join('')+'<div style="font-size:.6rem;color:var(--muted);margin-top:.3rem">Congestion Score (0-10)</div>';
  
  // Traffic Distribution Donuts
  const congLevels=['CRITICAL','HIGH','MODERATE','LOW'];
  const levelCounts=congLevels.map(level=>areas.filter(a=>a.congestion_level===level).length);
  const donutItems=[['Critical',levelCounts[0],'var(--red)'],['High',levelCounts[1],'var(--orange)'],['Moderate',levelCounts[2],'#fbbf24'],['Low',levelCounts[3],'var(--green)']];
  const c70=2*Math.PI*28;
  document.getElementById('infraDonuts').innerHTML=donutItems.map(([label,count,color])=>{
    const pct=Math.round((count/(areas.length||1))*100);
    const offset=(c70-(pct/100)*c70).toFixed(1);
    return `<div class="donut-wrap"><svg viewBox="0 0 70 70"><circle class="donut-bg" cx="35" cy="35" r="28"/><circle class="donut-fg" cx="35" cy="35" r="28" stroke="${color}" stroke-dasharray="${c70.toFixed(1)}" stroke-dashoffset="${c70.toFixed(1)}" data-offset="${offset}" style="transition:stroke-dashoffset .9s ease;transform:rotate(-90deg);transform-origin:35px 35px;fill:none;stroke-width:8;stroke-linecap:round;"/><text x="35" y="38" text-anchor="middle" font-size="10" font-weight="800" fill="#e0e8ff">${pct}%</text></svg><div class="donut-label">${label}</div></div>`;
  }).join('');
  setTimeout(()=>{ document.querySelectorAll('.donut-fg').forEach(el=>{ el.style.strokeDashoffset=el.dataset.offset; }); },400);
  
  // LLM Insights
  const insights=llmInsights.immediate_solutions||[];
  const iMax=Math.max(...insights.map(s=>s.impact==='HIGH'?3:s.impact==='MEDIUM'?2:1),1);
  document.getElementById('trafficChart').innerHTML=insights.slice(0,3).map((sol,idx)=>{
    const impactVal=sol.impact==='HIGH'?3:sol.impact==='MEDIUM'?2:1;
    const color=impactVal===3?'var(--green)':impactVal===2?'var(--orange)':'#fbbf24';
    return `<div class="traffic-bar-row"><div class="traffic-bar-label"><span>${sol.solution||'Solution'}</span><span>${sol.impact||'N/A'}</span></div><div class="traffic-bar-bg"><div class="traffic-bar-fill" style="width:${(impactVal/iMax*100).toFixed(1)}%;background:${color}"></div></div></div>`;
  }).join('')+`<div style="font-size:.68rem;color:var(--muted);margin-top:.4rem">Immediate Solutions by Impact</div>`;
  
  // Best Travel Times (from predictions)
  const mostCongested=predictions.most_congested_tomorrow||[];
  const leastCongested=predictions.least_congested_tomorrow||[];
  const pbudgets=[mostCongested.length,leastCongested.length,worstAreas.length,bestAreas.length];
  const totalBudget=pbudgets.reduce((a,b)=>a+b,1);
  document.getElementById('investChart').innerHTML=`<div class="inv-bar-wrap">${[['Most Congested',pbudgets[0],'var(--red)'],['Least Congested',pbudgets[1],'var(--green)'],['Worst Now',pbudgets[2],'var(--orange)'],['Best Now',pbudgets[3],'#8b5cf6']].map(([label,val,col])=>{const pct=(val/totalBudget*100).toFixed(1);return `<div class="inv-seg" style="width:${pct}%;background:${col}" title="${label}: ${val}">${pct>8?label.substring(0,5):''}</div>`;}).join('')}</div><div class="inv-legend">${[['var(--red)','Most Congested Tomorrow: '+mostCongested.length],['var(--green)','Least Congested Tomorrow: '+leastCongested.length],['var(--orange)','Worst Areas Now: '+worstAreas.length],['#8b5cf6','Best Areas Now: '+bestAreas.length]].map(([col,txt])=>`<div class="inv-leg-item"><div class="inv-leg-dot" style="background:${col}"></div>${txt}</div>`).join('')}</div><div style="font-size:.68rem;color:var(--muted);margin-top:.3rem">Traffic Summary</div>`;
  
  // Travel Advice
  const advice=llmInsights.travel_advice||'Plan your route according to current traffic conditions.';
  const svg=document.getElementById('roiSvg');
  const W=svg.clientWidth||300,H=120;
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  svg.innerHTML=`<rect width="${W}" height="${H}" fill="rgba(0,212,255,.05)" rx="4"/><text x="10" y="20" font-size="11" font-weight="600" fill="#00d4ff">AI Travel Advice</text><text x="10" y="40" font-size="9" fill="#e0e8ff">${advice}</text>`;
  
  // Solutions
  const solutions=llmInsights.long_term_solutions||[];
  document.getElementById('solCards').innerHTML=solutions.slice(0,3).map((s,i)=>{
    const impact=s.impact==='VERY HIGH'?5:s.impact==='HIGH'?4:s.impact==='MEDIUM'?3:2;
    const stars=Array.from({length:5},(_,j)=>`<span class="mini-star" style="color:${j<impact?'var(--orange)':'var(--border)'}">&#9733;</span>`).join('');
    return `<div class="sol-card"><div class="sol-card-name">${s.solution||'Solution'}</div><div class="sol-card-meta"><span class="pill pill-cyan">${s.cost||'N/A'}</span><span class="pill pill-green">${s.impact||'N/A'}</span><div class="mini-stars">${stars}</div></div></div>`;
  }).join('')||'<div style="font-size:.75rem;color:var(--muted)">No solutions yet.</div>';
}

/* ── BLUEPRINT MAP ── */
const ZONE_COLORS={residential:'#1a3a5c',commercial:'#3a2a0a',industrial:'#1a1a2a',park:'#0a2a1a'};
const ZONE_STROKE={residential:'#2a5a8c',commercial:'#8c6a2a',industrial:'#3a3a5a',park:'#1a6a3a'};
function cityBlocks(W,H){
  const blocks=[],cols=9,rows=7,bw=(W-80)/cols,bh=(H-80)/rows;
  const types=['residential','commercial','industrial','park','residential','commercial','residential','park','residential'];
  for(let r=0;r<rows;r++) for(let c=0;c<cols;c++) blocks.push({x:40+c*bw+3,y:40+r*bh+3,w:bw-6,h:bh-6,type:types[(r*cols+c)%types.length],idx:r*cols+c});
  return blocks;
}
function getMapSize(){ const el=document.getElementById('bpCanvas'); return {W:el.clientWidth||800,H:el.clientHeight||500}; }

function renderBlueprintMap(bp){
  document.getElementById('bpTitle').textContent=(bp.city_name||'City')+' - Live Traffic Map';
  drawTopView(bp); draw3DView(bp); drawZoneView(bp); drawNetworkView(bp);
  switchView('top');
}

function drawTopView(bp){
  const {W,H}=getMapSize(),blocks=cityBlocks(W,H);
  const areas=bp.areas||[];
  const worstAreas=bp.best_areas||[];
  const hasCrit=areas.some(a=>a.congestion_level==='CRITICAL');
  const cols=9,rows=7,bw=(W-80)/cols,bh=(H-80)/rows;
  let h=`<defs><radialGradient id="hotspot"><stop offset="0%" stop-color="#ff3366" stop-opacity=".5"/><stop offset="100%" stop-color="#ff3366" stop-opacity="0"/></radialGradient><radialGradient id="solspot"><stop offset="0%" stop-color="#00d4ff" stop-opacity=".4"/><stop offset="100%" stop-color="#00d4ff" stop-opacity="0"/></radialGradient><filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><rect width="${W}" height="${H}" fill="#080e1c"/>`;
  for(let c=0;c<=cols;c++){ const x=40+c*bw; h+=`<line x1="${x}" y1="30" x2="${x}" y2="${H-30}" stroke="#1a2a3a" stroke-width="${c%3===0?2:1}"/>`; }
  for(let r=0;r<=rows;r++){ const y=40+r*bh; h+=`<line x1="30" y1="${y}" x2="${W-30}" y2="${y}" stroke="#1a2a3a" stroke-width="${r%3===0?2:1}"/>`; }
  const ry=H*0.62;
  h+=`<path d="M0,${ry} Q${W*.25},${ry-20} ${W*.5},${ry+15} Q${W*.75},${ry+35} ${W},${ry+10}" fill="none" stroke="#0a3a5a" stroke-width="18" opacity=".7"/>`;
  h+=`<path d="M0,${ry} Q${W*.25},${ry-20} ${W*.5},${ry+15} Q${W*.75},${ry+35} ${W},${ry+10}" fill="none" stroke="#0d4a70" stroke-width="10" opacity=".5"/>`;
  blocks.forEach((b,i)=>{
    const isProblem=hasCrit&&worstAreas.length>0&&i<3;
    const isBest=(bp.best_areas||[]).length>0&&i>=blocks.length-3;
    h+=`<rect x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" fill="${ZONE_COLORS[b.type]}" stroke="${ZONE_STROKE[b.type]}" stroke-width=".8" rx="2" style="cursor:pointer" onmouseenter="showBlockTip(event,'${b.type}',${i})" onmouseleave="hideTip()"/>`;
    if(isProblem) h+=`<circle cx="${b.x+b.w/2}" cy="${b.y+b.h/2}" r="${Math.min(b.w,b.h)*.4}" fill="url(#hotspot)"><animate attributeName="r" values="${Math.min(b.w,b.h)*.3};${Math.min(b.w,b.h)*.5};${Math.min(b.w,b.h)*.3}" dur="2s" repeatCount="indefinite"/></circle>`;
    if(isBest) h+=`<circle cx="${b.x+b.w/2}" cy="${b.y+b.h/2}" r="6" fill="var(--cyan)" filter="url(#glow)"><animate attributeName="opacity" values="1;.4;1" dur="1.5s" repeatCount="indefinite"/></circle><text x="${b.x+b.w/2}" y="${b.y+b.h/2+4}" text-anchor="middle" font-size="7" fill="#000" font-weight="bold">✓</text>`;
  });
  h+=`<line x1="40" y1="${40+2*bh+bh/2}" x2="${W-40}" y2="${40+2*bh+bh/2}" stroke="#2a4a6a" stroke-width="4" opacity=".6"/>`;
  h+=`<line x1="${40+4*bw+bw/2}" y1="40" x2="${40+4*bw+bw/2}" y2="${H-40}" stroke="#2a4a6a" stroke-width="4" opacity=".6"/>`;
  const svg=document.getElementById('cityMapSvg');
  svg.innerHTML=h; svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
}

function draw3DView(bp){
  const {W,H}=getMapSize(),cols=8,rows=6,tw=60,th=30,tz=40,ox=W/2,oy=H*.25;
  let h=`<rect width="${W}" height="${H}" fill="#060c18"/>`;
  for(let r=0;r<rows;r++) for(let c=0;c<cols;c++){
    const types=['residential','commercial','industrial','park'];
    const type=types[(r*cols+c)%types.length];
    const bh={residential:tz,commercial:tz*2.5,industrial:tz*1.5,park:tz*.3}[type];
    const col={residential:{top:'#1e4a7a',left:'#0d2a4a',right:'#152a5a'},commercial:{top:'#7a5a1e',left:'#4a3a0d',right:'#5a4a15'},industrial:{top:'#3a3a5a',left:'#1a1a3a',right:'#2a2a4a'},park:{top:'#1a5a2a',left:'#0d3a1a',right:'#152a1e'}}[type];
    const x=ox+(c-cols/2)*tw+(r-rows/2)*tw,y=oy+(c-cols/2)*th-(r-rows/2)*th;
    h+=`<polygon points="${x},${y-bh} ${x+tw},${y+th-bh} ${x+tw},${y+th} ${x},${y}" fill="${col.top}" stroke="#0a1a2a" stroke-width=".5"/>`;
    h+=`<polygon points="${x+tw},${y+th-bh} ${x+2*tw},${y-bh} ${x+2*tw},${y} ${x+tw},${y+th}" fill="${col.right}" stroke="#0a1a2a" stroke-width=".5"/>`;
    h+=`<polygon points="${x},${y-bh} ${x},${y} ${x+tw},${y+th} ${x+tw},${y+th-bh}" fill="${col.left}" stroke="#0a1a2a" stroke-width=".5"/>`;
  }
  const svg=document.getElementById('city3dSvg'); svg.innerHTML=h; svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
}

function drawZoneView(bp){
  const {W,H}=getMapSize(),blocks=cityBlocks(W,H);
  const infra=bp.data_summary?.infrastructure||{};
  const zc={residential:'rgba(30,74,122,.8)',commercial:'rgba(122,90,30,.8)',industrial:'rgba(58,58,90,.8)',park:'rgba(26,90,42,.8)'};
  const zl={residential:'Res',commercial:'Com',industrial:'Ind',park:'Park'};
  let h=`<rect width="${W}" height="${H}" fill="#060c18"/>`;
  blocks.forEach(b=>{ h+=`<rect x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" fill="${zc[b.type]}" stroke="${ZONE_STROKE[b.type]}" stroke-width="1" rx="2"/><text x="${b.x+b.w/2}" y="${b.y+b.h/2+3}" text-anchor="middle" font-size="7" fill="rgba(255,255,255,.35)">${zl[b.type]}</text>`; });
  const wp=infra.water_coverage_pct||50,ep=infra.electricity_coverage_pct||60;
  for(let i=0;i<8;i++){
    if(i/8*100<wp) h+=`<line x1="${40+i*(W-80)/8}" y1="40" x2="${40+i*(W-80)/8}" y2="${H-40}" stroke="rgba(0,100,255,.2)" stroke-width="1.5" stroke-dasharray="4,4"/>`;
    if(i/8*100<ep) h+=`<line x1="40" y1="${40+i*(H-80)/8}" x2="${W-40}" y2="${40+i*(H-80)/8}" stroke="rgba(255,220,0,.12)" stroke-width="1" stroke-dasharray="6,6"/>`;
  }
  const svg=document.getElementById('zoneMapSvg'); svg.innerHTML=h; svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
}

function drawNetworkView(bp){
  const {W,H}=getMapSize();
  const traffic=bp.data_summary?.traffic||{};
  const junctions=Math.min(traffic.major_junctions||20,40);
  const density=traffic.road_density||'medium';
  const nodes=[];
  for(let i=0;i<junctions;i++) nodes.push({x:60+Math.random()*(W-120),y:60+Math.random()*(H-120),size:3+Math.random()*5,cong:Math.random()});
  let h=`<rect width="${W}" height="${H}" fill="#060c18"/>`;
  nodes.forEach((n,i)=>{ nodes.forEach((m,j)=>{ if(j<=i) return; const d=Math.hypot(n.x-m.x,n.y-m.y); if(d>W*.22) return; const c=(n.cong+m.cong)/2; h+=`<line x1="${n.x.toFixed(1)}" y1="${n.y.toFixed(1)}" x2="${m.x.toFixed(1)}" y2="${m.y.toFixed(1)}" stroke="rgb(${Math.round(c*255)},${Math.round((1-c)*200)},30)" stroke-width="${density==='high'?1.5:.8}" opacity=".5"/>`; }); });
  nodes.forEach(n=>{ h+=`<circle cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="${n.size}" fill="rgb(${Math.round(n.cong*255)},${Math.round((1-n.cong)*200)},30)" stroke="rgba(0,212,255,.4)" stroke-width=".8">${n.cong>.7?`<animate attributeName="r" values="${n.size};${n.size*1.6};${n.size}" dur="1.5s" repeatCount="indefinite"/>`:''}  </circle>`; });
  h+=`<text x="10" y="18" font-size="9" fill="var(--muted)">Node size = junction importance | Color = congestion level</text>`;
  const svg=document.getElementById('networkSvg'); svg.innerHTML=h; svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
}

function switchView(view){
  currentView=view;
  ['top','3d','zone','network'].forEach(v=>{ document.getElementById('vt-'+v).classList.toggle('active',v===view); });
  const ids={top:'cityMapSvg','3d':'city3dSvg',zone:'zoneMapSvg',network:'networkSvg'};
  Object.entries(ids).forEach(([v,id])=>{ const el=document.getElementById(id); el.style.opacity=v===view?'1':'0'; el.style.pointerEvents=v===view?'auto':'none'; });
  const legends={top:[['#1a3a5c','Residential'],['#3a2a0a','Commercial'],['#1a1a2a','Industrial'],['#0a2a1a','Park'],['#ff3366','Problem Zone'],['#00d4ff','Solution Marker']],
    '3d':[['#1e4a7a','Residential'],['#7a5a1e','Commercial'],['#3a3a5a','Industrial'],['#1a5a2a','Park']],
    zone:[['rgba(30,74,122,.8)','Residential'],['rgba(122,90,30,.8)','Commercial'],['rgba(58,58,90,.8)','Industrial'],['rgba(26,90,42,.8)','Green Zone']],
    network:[['#00c800','Low Congestion'],['#ff6b35','Medium'],['#ff3366','High Congestion']]};
  document.getElementById('mapLegend').innerHTML=(legends[view]||[]).map(([color,label])=>`<div class="legend-item"><div class="legend-dot" style="background:${color}"></div>${label}</div>`).join('');
}

function showBlockTip(e,type,idx){
  const tt=document.getElementById('mapTooltip');
  const labels={residential:'Residential Zone',commercial:'Commercial Zone',industrial:'Industrial Zone',park:'Green Zone / Park'};
  tt.innerHTML=`<h4>${labels[type]||type}</h4><p>Block #${idx+1}</p>`;
  tt.style.display='block'; tt.style.left=(e.offsetX+12)+'px'; tt.style.top=(e.offsetY+12)+'px';
}
function hideTip(){ document.getElementById('mapTooltip').style.display='none'; }
function mapZoom(f){ _mapScale=Math.max(.5,Math.min(3,_mapScale*f)); ['cityMapSvg','city3dSvg','zoneMapSvg','networkSvg'].forEach(id=>{ const el=document.getElementById(id); el.style.transform=`scale(${_mapScale})`; el.style.transformOrigin='center center'; }); }
function mapReset(){ _mapScale=1; mapZoom(1); }
function highlightProblem(i){ switchTab('blueprint'); }

/* ── ANALYTICS TAB ── */
function renderAnalytics(bp){
  const ds=bp.data_summary||{},air=ds.air_quality||{},infra=ds.infrastructure||{},traffic=ds.traffic||{};
  const fin=bp.financial_summary||{},roi=fin.roi||{};
  document.getElementById('analyticsContent').innerHTML=`
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
      <div class="chart-card"><div class="chart-title">Air Quality Detail</div>
        <div style="font-size:.8rem;color:var(--muted);line-height:2">
          PM2.5: <b style="color:${(air.pm2_5||0)>12?'var(--red)':'var(--green)'}">${air.pm2_5||'N/A'} ug/m3</b><br>
          PM10: <b style="color:${(air.pm10||0)>45?'var(--red)':'var(--green)'}">${air.pm10||'N/A'} ug/m3</b><br>
          NO2: <b style="color:${(air.nitrogen_dioxide||0)>40?'var(--red)':'var(--green)'}">${air.nitrogen_dioxide||'N/A'} ug/m3</b><br>
          Ozone: <b style="color:${(air.ozone||0)>100?'var(--red)':'var(--green)'}">${air.ozone||'N/A'} ug/m3</b>
        </div>
      </div>
      <div class="chart-card"><div class="chart-title">Weather Conditions</div>
        <div style="font-size:.8rem;color:var(--muted);line-height:2">
          Temperature: <b style="color:var(--text)">${ds.weather?.temperature_c||'N/A'} C</b><br>
          Humidity: <b style="color:var(--text)">${ds.weather?.humidity_percent||'N/A'}%</b><br>
          Wind Speed: <b style="color:var(--text)">${ds.weather?.wind_speed_kmh||'N/A'} km/h</b><br>
          Precipitation: <b style="color:var(--text)">${ds.weather?.precipitation_mm||0} mm</b>
        </div>
      </div>
      <div class="chart-card"><div class="chart-title">Infrastructure Coverage</div>
        <div style="font-size:.8rem;color:var(--muted);line-height:2">
          Water: <b style="color:${(infra.water_coverage_pct||0)>=60?'var(--green)':'var(--red)'}">${infra.water_coverage_pct||0}%</b><br>
          Electricity: <b style="color:${(infra.electricity_coverage_pct||0)>=70?'var(--green)':'var(--red)'}">${infra.electricity_coverage_pct||0}%</b><br>
          Waste Mgmt: <b style="color:${(infra.waste_coverage_pct||0)>=50?'var(--green)':'var(--red)'}">${infra.waste_coverage_pct||0}%</b><br>
          Roads Paved: <b style="color:${(infra.roads_paved_pct||0)>=60?'var(--green)':'var(--red)'}">${infra.roads_paved_pct||0}%</b>
        </div>
      </div>
      <div class="chart-card"><div class="chart-title">Traffic Statistics</div>
        <div style="font-size:.8rem;color:var(--muted);line-height:2">
          Major Junctions: <b style="color:var(--text)">${traffic.major_junctions||0}</b><br>
          Traffic Signals: <b style="color:var(--text)">${traffic.traffic_signals||0}</b><br>
          Pedestrian Crossings: <b style="color:var(--text)">${traffic.pedestrian_crossings||0}</b><br>
          Road Density: <b style="color:var(--text)">${traffic.road_density||'N/A'}</b>
        </div>
      </div>
      <div class="chart-card" style="grid-column:1/-1"><div class="chart-title">Financial Overview</div>
        <div style="display:flex;gap:2rem;flex-wrap:wrap;font-size:.82rem;color:var(--muted)">
          <div>Total Investment<br><b style="font-size:1.3rem;color:var(--cyan)">Rs.${fin.grand_total_crore||0} Cr</b></div>
          <div>Budget Status<br><b style="color:${fin.budget_status==='FEASIBLE'?'var(--green)':fin.budget_status==='STRETCH'?'var(--orange)':'var(--red)'}">${fin.budget_status||'N/A'}</b></div>
          <div>Annual ROI Savings<br><b style="font-size:1.1rem;color:var(--green)">Rs.${roi.total_annual_savings_crore||0} Cr</b></div>
          <div>10-Year Net Benefit<br><b style="font-size:1.1rem;color:var(--cyan)">Rs.${roi.total_net_benefit_10yr_crore||0} Cr</b></div>
          <div>Payback Period<br><b style="color:var(--text)">${roi.overall_payback_years||'N/A'} years</b></div>
        </div>
      </div>
    </div>`;
}

/* ── REPORTS TAB ── */
function renderReports(bp){
  const ov=bp.city_overview||{},ex=bp.executive_summary||{},problems=bp.problem_report||[];
  const solutions=bp.solutions_section||[],phases=bp.phase_plan||{},fin=bp.financial_summary||{};
  const pkeys=['phase_1','phase_2','phase_3','phase_4'];
  document.getElementById('reportsContent').innerHTML=`
    <div class="report-section">
      <div class="report-h2">City Overview</div>
      <div class="report-text"><b>${ov.city_name||'—'}</b> | Population: ${(ov.population||0).toLocaleString('en-IN')} | Tier: ${(ov.city_tier||'').toUpperCase()} | Health Score: <b style="color:${(ov.health_score||0)>=70?'var(--green)':'var(--red)'}">${ov.health_score||0}/100 (${ov.health_rating||''})</b></div>
    </div>
    <div class="report-section">
      <div class="report-h2">Executive Summary</div>
      <div class="report-text">${ex.current_situation||'N/A'}</div>
      <div class="report-text" style="margin-top:.5rem"><b>Recommended Approach:</b> ${ex.recommended_approach||'N/A'}</div>
      <div class="report-text" style="margin-top:.5rem"><b>Expected Outcomes:</b> ${ex.expected_outcomes||'N/A'}</div>
    </div>
    <div class="report-section">
      <div class="report-h2">Problem Report</div>
      ${problems.length?`<table class="report-table"><thead><tr><th>#</th><th>Problem</th><th>Category</th><th>Severity</th><th>Score</th></tr></thead><tbody>${problems.map((p,i)=>`<tr><td>${i+1}</td><td>${p.name||''}</td><td>${p.category||''}</td><td style="color:${p.severity==='CRITICAL'?'var(--red)':p.severity==='HIGH'?'var(--orange)':'var(--muted)'}">${p.severity}</td><td>${p.score}/10</td></tr>`).join('')}</tbody></table>`:'<div class="report-text" style="color:var(--green)">No critical problems detected.</div>'}
    </div>
    <div class="report-section">
      <div class="report-h2">Solutions</div>
      ${solutions.length?`<table class="report-table"><thead><tr><th>#</th><th>Solution</th><th>Timeline</th><th>Cost (Cr)</th><th>Impact</th></tr></thead><tbody>${solutions.map((s,i)=>`<tr><td>${i+1}</td><td>${s.solution_name||''}</td><td>${s.timeline||''}</td><td>Rs.${s.cost?.avg||0}</td><td>${s.impact_score||0}/10</td></tr>`).join('')}</tbody></table>`:'<div class="report-text">No solutions generated.</div>'}
    </div>
    <div class="report-section">
      <div class="report-h2">Phase-wise Implementation</div>
      <table class="report-table"><thead><tr><th>Phase</th><th>Timeline</th><th>Budget (Cr)</th><th>Key Outcomes</th></tr></thead><tbody>${pkeys.map(key=>{ const ph=phases[key]||{}; return `<tr><td style="color:var(--cyan)">${ph.label||key}</td><td>${key.replace('phase_','Ph')}</td><td>Rs.${ph.total_budget_crore||0}</td><td>${ph.expected_outcomes||'N/A'}</td></tr>`; }).join('')}</tbody></table>
    </div>
    <div class="report-section">
      <div class="report-h2">Financial Summary</div>
      <div class="report-text" style="line-height:2">
        Total Investment: <b style="color:var(--cyan)">Rs.${fin.grand_total_crore||0} Crore</b><br>
        Budget Status: <b style="color:${fin.budget_status==='FEASIBLE'?'var(--green)':fin.budget_status==='STRETCH'?'var(--orange)':'var(--red)'}">${fin.budget_status||'N/A'}</b><br>
        Annual ROI Savings: <b style="color:var(--green)">Rs.${fin.roi?.total_annual_savings_crore||0} Crore</b><br>
        10-Year Net Benefit: <b style="color:var(--cyan)">Rs.${fin.roi?.total_net_benefit_10yr_crore||0} Crore</b><br>
        Payback Period: <b>${fin.roi?.overall_payback_years||'N/A'} years</b><br>
        Funding Sources: ${(fin.funding_sources||[]).join(' | ')}
      </div>
    </div>`;
}

/* ── MODAL ── */
function openSolutionModal(i){
  const solutions=(blueprintData?.solutions_section)||[];
  const s=solutions[i]; if(!s) return;
  document.getElementById('modalTitle').textContent=s.solution_name||'Solution';
  document.getElementById('modalBody').innerHTML=`
    <div class="modal-row"><div class="modal-key">Problem</div><div class="modal-val">${s.problem_addressed||'—'}</div></div>
    <div class="modal-row"><div class="modal-key">Technology</div><div class="modal-val">${s.technology||'—'}</div></div>
    <div class="modal-row"><div class="modal-key">Location</div><div class="modal-val">${s.location_type||'—'}</div></div>
    <div class="modal-row"><div class="modal-key">Timeline</div><div class="modal-val">${s.timeline||'—'}</div></div>
    <div class="modal-row"><div class="modal-key">Cost Range</div><div class="modal-val">Rs.${s.cost?.min||0} - Rs.${s.cost?.max||0} Cr (avg Rs.${s.cost?.avg||0} Cr)</div></div>
    <div class="modal-row"><div class="modal-key">Impact Score</div><div class="modal-val">${s.impact_score||0}/10</div></div>
    <div class="modal-row"><div class="modal-key">Cost/Citizen</div><div class="modal-val">Rs.${s.cost_per_citizen_inr||0}</div></div>
    <div class="modal-row"><div class="modal-key">Annual Savings</div><div class="modal-val">Rs.${s.roi?.estimated_annual_savings_crore||0} Cr</div></div>
    <div class="modal-row"><div class="modal-key">Payback</div><div class="modal-val">${s.roi?.payback_years||'N/A'} years</div></div>`;
  document.getElementById('modal').style.display='flex';
}
function closeModal(e){ if(e.target===document.getElementById('modal')) document.getElementById('modal').style.display='none'; }

/* ── UTILS ── */
function showToast(msg){ const t=document.getElementById('toast'); t.textContent=msg; t.style.display='block'; setTimeout(()=>{ t.style.display='none'; },4000); }
function downloadBlueprint(){ if(!blueprintData) return; const city=(blueprintData.city_overview?.city_name||'city').toLowerCase(); const blob=new Blob([JSON.stringify(blueprintData,null,2)],{type:'application/json'}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=city+'_blueprint.json'; a.click(); }
