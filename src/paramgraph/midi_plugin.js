
/*! ParamGraph MIDI plugin (tailored) */
(function(global){
  const PG = global.ParamGraph;
  let access=null;
  const ccMap = new Map();
  const MODWHEEL = 1;

  function to01(v){ return Math.max(0, Math.min(1, v/127)); }

  function onMIDIMessage(e){
    const [status,d1,d2] = e.data;
    if((status & 0xF0) === 0xB0){ // CC
      const cc=d1, val=d2;
      if(cc===MODWHEEL){
        const path = `${PG.getActiveWindow()}/vessel/rotY`;
        PG.setInput("midi", path, to01(val));
      }
      for(const [path,wanted] of ccMap){
        if(cc===wanted){ PG.setInput("midi", path, to01(val)); }
      }
    }
  }

  function init(){
    if(!navigator.requestMIDIAccess){ console.warn("MIDI not supported"); return; }
    navigator.requestMIDIAccess().then(a=>{
      access=a;
      for(const input of access.inputs.values()){ input.onmidimessage = onMIDIMessage; }
      access.onstatechange = ()=>{ for(const input of access.inputs.values()){ input.onmidimessage = onMIDIMessage; } };
    }).catch(e=>console.warn("MIDI access error:", e));
  }

  function mapCC(path, cc){ ccMap.set(path, cc); }
  function unmapCC(path){ ccMap.delete(path); }

  global.ParamGraphMIDI = { init, mapCC, unmapCC };
})(window);
