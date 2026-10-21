/* ---------- look: accent colour and background, on top of light/dark ---------- */
const ACCENTS={indigo:'#4349C9',blue:'#1D6FD8',teal:'#0F8B8D',green:'#1F8A57',lime:'#5B8A12',yellow:'#B8860B',gold:'#B8860B',orange:'#D9631A',red:'#C23B35',pink:'#C93C7C',magenta:'#B5389E',purple:'#7A3FC4',violet:'#6A45D1',brown:'#8A5A3C',grey:'#58677A',gray:'#58677A',slate:'#4A5B6A',cyan:'#0E87A8',navy:'#26407A',maroon:'#8E2B3A'};
// Each background has a light and a dark version. tone 'dark' means it only makes sense in dark mode.
const BGS={
  default:{label:'Default',l:{bg:'#F3F0E6'},d:{bg:'#0E1B15'}},
  paper:{label:'Paper',l:{bg:'#F7F1E5'},d:{bg:'#2A261F'}},
  mint:{label:'Mint',l:{bg:'#E9F4EE'},d:{bg:'#1C2823'}},
  sky:{label:'Sky',l:{bg:'#E8F1FB'},d:{bg:'#1B2733'}},
  blush:{label:'Blush',l:{bg:'#FBEDEE'},d:{bg:'#2C2124'}},
  lavender:{label:'Lavender',l:{bg:'#EFEBFA'},d:{bg:'#262037'}},
  slate:{label:'Slate',l:{bg:'#E4E8EC'},d:{bg:'#14181E'}},
  sunrise:{label:'Sunrise',l:{bg:'#FBEFE4',img:'linear-gradient(170deg,#FFE9D6 0%,#FBEFE4 38%,#F3EEF8 100%)'},d:{bg:'#2A1F1B',img:'linear-gradient(170deg,#3A281D 0%,#2A1F1B 45%,#231E2E 100%)'}},
  aurora:{label:'Aurora',l:{bg:'#E8F3F1',img:'linear-gradient(165deg,#D8F1EA 0%,#E8F3F1 40%,#E6E8FA 100%)'},d:{bg:'#1A2628',img:'linear-gradient(165deg,#1A3A34 0%,#1A2628 45%,#241F42 100%)'}},
  midnight:{label:'Midnight',tone:'dark',d:{bg:'#141C32',img:'linear-gradient(180deg,#1C2850 0%,#141C32 60%)'}},
  black:{label:'Black',tone:'dark',d:{bg:'#121519'}}
};

// Colour themes: each sets the ink, the main colour, the hero card and the second ink. "forest" is the default in the stylesheet.
const PALS={
  forest:{label:'Forest',sw:['#1B5E3F','#B4440A'],
    l:{'--bg':'#F3F0E6','--ink':'#132A20','--ink2':'#2E4A3C','--ink3':'#3B5848','--ink-y':'#132A20','--blue':'#1B5E3F','--hero':'#17523A','--hero-ink':'#F4F8F4','--accent':'#B4440A','--accent-soft':'#FBE3D2','--accent-ink':'#FFFFFF','--scrim':'rgba(19,42,32,.5)'},
    d:{'--bg':'#0E1B15','--ink':'#EEF4EF','--ink2':'#C9D8CE','--ink3':'#B3C7B9','--ink-y':'#132A20','--blue':'#7FD6A0','--hero':'#1E6A47','--hero-ink':'#FFFFFF','--accent':'#FF9B5A','--accent-soft':'#402312','--accent-ink':'#0E1B15','--scrim':'rgba(2,10,6,.65)'}},
  maroon:{label:'Maroon',sw:['#7A1F2B','#0E6B6B'],
    l:{'--bg':'#F6F0E8','--ink':'#2A1418','--ink2':'#4D2B31','--ink3':'#5C3A40','--ink-y':'#2A1418','--blue':'#7A1F2B','--hero':'#6B1A26','--hero-ink':'#FBF3EF','--accent':'#0E6B6B','--accent-soft':'#D5EEEC','--accent-ink':'#FFFFFF','--scrim':'rgba(42,20,24,.5)'},
    d:{'--bg':'#1E0F12','--ink':'#F6ECE6','--ink2':'#E0CCC6','--ink3':'#CDB4AD','--ink-y':'#2A1418','--blue':'#F0A0A8','--hero':'#8A2432','--hero-ink':'#FFFFFF','--accent':'#4CC3C3','--accent-soft':'#0F3030','--accent-ink':'#1E0F12','--scrim':'rgba(12,4,6,.65)'}},
  graphite:{label:'Graphite',sw:['#2B2B25','#C2381A'],
    l:{'--bg':'#F2F1EC','--ink':'#1A1A17','--ink2':'#3B3B35','--ink3':'#4A4A43','--ink-y':'#1A1A17','--blue':'#2B2B25','--hero':'#23231F','--hero-ink':'#F7F6F0','--accent':'#C2381A','--accent-soft':'#F8DDD5','--accent-ink':'#FFFFFF','--scrim':'rgba(26,26,23,.5)'},
    d:{'--bg':'#121210','--ink':'#F1F0EA','--ink2':'#D3D2C9','--ink3':'#BDBCB2','--ink-y':'#1A1A17','--blue':'#E9E6D8','--hero':'#2C2C27','--hero-ink':'#FFFFFF','--accent':'#FF7A4F','--accent-soft':'#40211A','--accent-ink':'#121210','--scrim':'rgba(0,0,0,.65)'}}
};
let LOOK=Object.assign({accent:null,bg:null,pal:null},lsGet('pl.look',{}));
const isDarkNow=()=>theme==='dark'||(theme==='auto'&&!!(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches));
const hexOk=h=>typeof h==='string'&&/^#[0-9a-f]{6}$/i.test(h);
function h2rgb(h){return [1,3,5].map(i=>parseInt(h.slice(i,i+2),16))}
function rgb2hsl([r,g,b]){r/=255;g/=255;b/=255;const mx=Math.max(r,g,b),mn=Math.min(r,g,b),l=(mx+mn)/2;let h=0,s=0;
  if(mx!==mn){const d=mx-mn;s=l>.5?d/(2-mx-mn):d/(mx+mn);h=mx===r?(g-b)/d+(g<b?6:0):mx===g?(b-r)/d+2:(r-g)/d+4;h*=60}
  return [h,s*100,l*100]}
const lumOf=hex=>{const [r,g,b]=h2rgb(hex).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*r+.7152*g+.0722*b};
function parseColour(s){
  s=String(s||'').trim().toLowerCase();
  if(ACCENTS[s])return ACCENTS[s];
  let m=s.match(/^#?([0-9a-f]{6})$/);if(m)return '#'+m[1];
  m=s.match(/^#?([0-9a-f]{3})$/);if(m)return '#'+m[1].split('').map(c=>c+c).join('');
  return null;
}
function applyLook(){
  const st=document.documentElement.style,dark=isDarkNow();
  const vars=['--accent','--accent-soft','--accent-ink','--bg','--bgimg','--ink','--ink2','--ink3','--ink-y','--blue','--hero','--hero-ink','--scrim'];
  vars.forEach(v=>st.removeProperty(v));
  const pal=LOOK.pal&&PALS[LOOK.pal];
  if(pal)Object.entries(dark?pal.d:pal.l).forEach(([k,v])=>st.setProperty(k,v));
  if(LOOK.accent&&hexOk(LOOK.accent)){
    const [h,s0,l0]=rgb2hsl(h2rgb(LOOK.accent)),s=Math.min(s0,88);
    // keep the colour readable: darker on light screens, lighter on dark ones
    const l=dark?Math.max(l0,66):Math.min(l0,42);
    st.setProperty('--accent',`hsl(${h.toFixed(0)} ${s.toFixed(0)}% ${l.toFixed(0)}%)`);
    st.setProperty('--accent-soft',dark?`hsl(${h.toFixed(0)} 38% 20%)`:`hsl(${h.toFixed(0)} 70% 94%)`);
    st.setProperty('--accent-ink',dark?'#0E1217':'#FFFFFF');
  }
  const bg=resolveBg(LOOK.bg,dark);
  if(bg){st.setProperty('--bg',bg.bg);if(bg.img)st.setProperty('--bgimg',bg.img)}
  const meta=document.querySelector('meta[name=theme-color]');
  if(meta)meta.setAttribute('content',bg?bg.bg:(getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()||'#F3F0E6'));
}
function resolveBg(key,dark){
  if(!key)return null;
  if(BGS[key]){const b=BGS[key];return dark?(b.d||null):(b.l||b.d||null)}
  if(hexOk(key))return {bg:key};
  return null;
}
// Returns a note when the theme had to change so the text stays readable.
function setLook(p){
  let note='';
  if('accent' in p){const c=p.accent?parseColour(p.accent):null;if(p.accent&&!c)return {err:H('I do not know the colour "'+p.accent+'". Try a name like green or orange, or a hex code like #1D6FD8.','मैं "'+p.accent+'" रंग नहीं {पहचानता|पहचानती}। हरा या नारंगी जैसा नाम, या #1D6FD8 जैसा हेक्स कोड बताएँ।')};LOOK.accent=c}
  if('pal' in p){LOOK.pal=p.pal&&PALS[p.pal]?p.pal:null}
  if('bg' in p){
    let k=p.bg;
    if(k&&!BGS[k]){const c=parseColour(k);if(!c)return {err:H('I do not know the background "'+k+'". Pick one of: '+Object.keys(BGS).join(', ')+', or give a hex code.','मैं "'+k+'" पृष्ठभूमि नहीं {पहचानता|पहचानती}। इनमें से चुनें: '+Object.keys(BGS).map(x=>L(BGS[x].label)).join(', ')+', या हेक्स कोड दें।')};k=c}
    LOOK.bg=k||null;
    let wantDark=null;
    if(k&&BGS[k]&&BGS[k].tone==='dark')wantDark=true;
    else if(k&&hexOk(k)){wantDark=lumOf(k)<.3}
    if(wantDark!==null&&wantDark!==isDarkNow()){
      theme=wantDark?'dark':'light';lsSet('pl.theme',theme);
      note=wantDark?H(' I switched to dark mode so the text stays readable on it.',' लिखावट साफ़ पढ़ी जा सके, इसलिए मैंने गहरा मोड चालू कर दिया।'):H(' I switched to light mode so the text stays readable on it.',' लिखावट साफ़ पढ़ी जा सके, इसलिए मैंने हल्का मोड चालू कर दिया।');
    }
  }
  lsSet('pl.look',LOOK);applyTheme();
  return {note};
}
function resetLook(){LOOK={accent:null,bg:null,pal:null};lsSet('pl.look',LOOK);applyLook()}
if(window.matchMedia)try{matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>applyLook())}catch(e){}

/* swatches in Settings */
const PICK_ACC=['indigo','blue','teal','green','orange','red','pink','purple'];
function lookPickers(){
  const acc=PICK_ACC.map(k=>`<button type="button" class="sw" style="background:${ACCENTS[k]}" data-act="lookacc" data-v="${k}" aria-label="${k} accent" aria-pressed="${LOOK.accent===ACCENTS[k]}"></button>`).join('')+`<button type="button" class="btn sm ghost" data-act="lookacc" data-v="">Default</button>`;
  const dk=isDarkNow();
  const bgs=Object.keys(BGS).filter(k=>k!=='default').map(k=>{const r=resolveBg(k,dk)||resolveBg(k,!dk);return `<button type="button" class="sw bgsw" style="background:${r.img||r.bg}" data-act="lookbg" data-v="${k}" aria-label="${BGS[k].label} background" aria-pressed="${LOOK.bg===k}"></button>`}).join('')+`<button type="button" class="btn sm ghost" data-act="lookbg" data-v="">Default</button>`;
  const pals=Object.keys(PALS).map(k=>`<button type="button" class="sw palsw" style="background:linear-gradient(135deg,${PALS[k].sw[0]} 50%,${PALS[k].sw[1]} 50%)" data-act="lookpal" data-v="${k}" aria-label="${PALS[k].label} colour theme" aria-pressed="${(LOOK.pal||'forest')===k}"></button>`).join('');
  return `<div class="stack" id="lookpick" style="gap:8px"><span class="kick">Colour theme</span><div class="sw-row">${pals}</div><span class="kick" style="margin-top:6px">Accent colour</span><div class="sw-row">${acc}</div><span class="kick" style="margin-top:6px">Background</span><div class="sw-row">${bgs}</div></div>`;
}
function paintLookPickers(){const e=document.getElementById('lookpick');if(e)e.outerHTML=lookPickers()}
