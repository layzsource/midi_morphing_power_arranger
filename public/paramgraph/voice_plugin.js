
/*! ParamGraph Voice plugin (tailored) */
(function(global){
  const PG = global.ParamGraph;
  let rec=null, enabled=false;

  function parse(cmd){
    const m = /(rotate|spin)\s+(x|y|z)\s+(left|right|up|down)?(?:\s+(slow|fast))?(?:\s+in\s+(\w+))?/i.exec(cmd);
    if(!m) return null;
    const axis = m[2].toUpperCase();
    const dir = (m[3]||"right").toLowerCase();
    const speedWord = (m[4]||"").toLowerCase();
    const slot = m[5] ? ("viewport/"+ (m[5].toLowerCase()==="main"?"main":"aux")) : PG.getActiveWindow();
    const sign = /left|down/.test(dir)? -1 : 1;
    const gain = speedWord==="fast" ? 0.08 : 0.03;
    return { axis, sign, gain, slot };
  }

  function handle(text){
    const p = parse(text); if(!p) return;
    const path = `${p.slot}/vessel/rot${p.axis}`;
    PG.addMod({source:"voice", path, gain:p.gain, bias:0, priority:5, enabled:true});
    PG.nudge(path, 10 * p.sign);
  }

  function start(){
    const SR = global.SpeechRecognition || global.webkitSpeechRecognition;
    if(!SR){ console.warn("Voice: Web Speech not available."); return; }
    rec = new SR(); rec.lang="en-US"; rec.continuous=true; rec.interimResults=false;
    rec.onresult = (ev)=>{ for(let i=ev.resultIndex;i<ev.results.length;i++){ if(ev.results[i].isFinal){ handle(ev.results[i][0].transcript.trim()); } } };
    rec.onerror = (e)=>console.warn("Voice error:", e.error);
    rec.onend = ()=>{ if(enabled) try{ rec.start(); }catch(e){} };
    enabled=true; try{ rec.start(); }catch(e){}
  }
  function stop(){ enabled=false; if(rec) try{ rec.stop(); }catch(e){} }

  global.ParamGraphVoice = { start, stop };
})(window);
