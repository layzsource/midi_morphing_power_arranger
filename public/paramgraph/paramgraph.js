
/*! ParamGraph — parameter & modulation matrix (tailored) */
(function(global){
  const P = new Map();
  const M = [];
  const owners = new Map();
  let ticking = false, rafId = null, autoFn = null, onChange = null;

  function now(){ return (performance && performance.now)? performance.now(): Date.now(); }
  function clamp(x,a,b){ return Math.max(a, Math.min(b, x)); }
  function lerp(a,b,t){ return a + (b-a)*t; }

  function addParam(id, opts){
    const o = Object.assign({value:0,min:0,max:1,smoothing:0.12,scope:"global",tags:[]}, opts||{});
    P.set(id, {value:o.value, target:o.value, min:o.min, max:o.max, smoothing:o.smoothing, scope:o.scope, tags:o.tags, last: now()});
    if(onChange) onChange(id, o.value);
  }
  function ensure(id, opts){ if(!P.has(id)) addParam(id, opts); }
  function addMod(mod){ const m = Object.assign({gain:1,bias:0,priority:0,enabled:true}, mod||{}); M.push(m); return m; }
  function setEnabled(mod, en){ mod.enabled = !!en; }
  function clearMods(filterFn){ if(!filterFn){ M.length=0; return; } for(let i=M.length-1;i>=0;--i){ if(filterFn(M[i])) M.splice(i,1);} }

  function setInput(source, path, raw01){
    const p = P.get(path); if(!p) return;
    let v = p.min + raw01*(p.max - p.min);
    let top=null;
    for(const m of M){ if(m.enabled && m.source===source && m.path===path){ if(!top || m.priority>top.priority) top=m; } }
    if(top){ v = v*top.gain + top.bias; owners.set(path, {source, priority: top.priority, ts: now()}); }
    else { owners.set(path, {source, priority: 0, ts: now()}); }
    p.target = clamp(v, p.min, p.max);
  }
  function nudge(path, d){ const p=P.get(path); if(!p) return; p.target = clamp(p.target + d, p.min, p.max); }
  function get(path){ const p=P.get(path); return p? p.value : undefined; }
  function getOwner(path){ return owners.get(path) || null; }

  function tickOnce(dtMaxMs=50){
    const t=now();
    for(const [id,p] of P){
      const dt = Math.min(dtMaxMs/1000, (t - p.last)/1000); p.last = t;
      const alpha = 1 - Math.pow(1 - p.smoothing, dt * 60);
      p.value = lerp(p.value, p.target, alpha);
      if(onChange) onChange(id, p.value);
    }
    if(typeof autoFn==="function"){
      try{ autoFn(1/60); }catch(e){}
    }
  }
  function start(){ if(ticking) return; ticking=true; (function loop(){ tickOnce(); rafId=(global.requestAnimationFrame||setTimeout)(loop,16); })(); }
  function stop(){ ticking=false; if(rafId){ (global.cancelAnimationFrame||clearTimeout)(rafId); rafId=null; } }
  function setAuto(fn){ autoFn=fn; }
  function setOnChange(fn){ onChange=fn; }

  function snapshot(){ const params={}; for(const [id,p] of P){ params[id]={value:p.value,min:p.min,max:p.max,smoothing:p.smoothing,scope:p.scope,tags:p.tags}; } return {version:1, params}; }
  function loadSnapshot(snap){ if(!snap||!snap.params) return; for(const k in snap.params){ const s=snap.params[k]; ensure(k,s); const p=P.get(k); p.value=s.value; p.target=s.value; p.min=s.min; p.max=s.max; p.smoothing=s.smoothing; p.scope=s.scope; p.tags=s.tags||[]; if(onChange) onChange(k,p.value);} }
  function resetTargetsToValues(){ for(const [,p] of P){ p.target=p.value; } }

  let activeViewport = "viewport/main";
  function setActiveWindow(id){ activeViewport = id; }
  function getActiveWindow(){ return activeViewport; }

  global.ParamGraph = {
    addParam, ensure, addMod, setEnabled, clearMods,
    setInput, nudge, get, getOwner,
    tickOnce, start, stop, setAuto, setOnChange,
    snapshot, loadSnapshot, resetTargetsToValues,
    setActiveWindow, getActiveWindow
  };
})(window);
