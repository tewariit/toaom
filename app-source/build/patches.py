# Source patches applied on top of the original โตฟิต / โตออม code when building โตไลฟ์.

def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:80])
    return s.replace(a, b)


FIT_HELPERS = r'''
/* ===== โตไลฟ์: meal price -> ออม (the ออม transaction is the single record; ฟิต only reads it back) ===== */
let priceEditing=null,priceErr="";
const linkOf=(k,slot)=>"fit:"+k+":"+slot;
const hasBridge=()=>typeof TL!=="undefined"&&!!TL.aom;
function priceOf(k,slot){try{return hasBridge()?TL.aom.linked(linkOf(k,slot)):null}catch(e){return null}}
const shortName=n=>{n=String(n||"").trim();if(n.length<=40)return n;const c=n.slice(0,40),i=Math.max(c.lastIndexOf(" "),c.lastIndexOf("/"));return (i>20?c.slice(0,i):c)+"…"};
const bahtTxt=v=>"฿"+(+v).toLocaleString("th-TH",{maximumFractionDigits:2});
function priceChip(k,slot){
  if(!hasBridge()||priceEditing===k+":"+slot)return "";
  const v=priceOf(k,slot);
  return `<button class="chipbtn price${v!=null?" paid":""}" data-price="${slot}">${v!=null?bahtTxt(v)+" · แก้ราคา":"ใส่ราคา ฿"}</button>`;
}
function priceEd(k,slot,name){
  if(priceEditing!==k+":"+slot)return "";
  const v=priceOf(k,slot);
  return `<div class="editf prf"><label>ราคา (บาท)<input id="prIn" type="number" inputmode="decimal" min="0" max="100000" step="any" value="${v!=null?v:""}" placeholder="เช่น 70"></label>
    <button class="btn" data-prsave="${slot}" data-prname="${esc(shortName(name))}">บันทึกราคา</button>
    ${v!=null?`<button class="chipbtn danger" data-prdel="${slot}">ลบราคา</button>`:""}<button class="chipbtn" data-prcancel="1">ยกเลิก</button>
    <span class="note" style="flex-basis:100%">${priceErr?`<b style="color:var(--warn)">${esc(priceErr)}</b><br>`:""}ไปขึ้นในออม หมวดอาหาร ทันที · มื้อที่ทำกินเองจากของที่ซื้อตุนไว้ เว้นว่างได้ จะได้ไม่นับเงินซ้ำ</span></div>`;
}
function setPrice(k,slot,amt,name){
  if(!hasBridge())return false;
  return TL.aom.setLinked(linkOf(k,slot),amt>0?{amt,date:k,note:(name||"มื้ออาหาร")+" · จากฟิต"}:null);
}
let aomT=null;
if(typeof TL!=="undefined")TL.onAomData=()=>{clearTimeout(aomT);aomT=setTimeout(()=>{
  if(tabNow!=="day"||editing||priceEditing)return;
  try{renderMeals(iso(cur),plan(cur))}catch(e){}},250)};
'''

FIT_BIND = r'''
  q("[data-price]").forEach(b=>b.onclick=()=>{priceEditing=k+":"+b.dataset.price;priceErr="";renderMeals(k,p);const f=$("prIn");if(f)f.focus()});
  q("[data-prcancel]").forEach(b=>b.onclick=()=>{priceEditing=null;priceErr="";renderMeals(k,p)});
  q("[data-prsave]").forEach(b=>b.onclick=()=>{
    const v=num($("prIn").value),slot=b.dataset.prsave;if(v==null||v<0||v>100000){$("prIn").focus();return}
    if(!setPrice(k,slot,v,b.dataset.prname)){priceErr="ออมยังโหลดข้อมูลไม่เสร็จ หรืออยู่ในโหมดตัวอย่าง ลองใหม่อีกครั้ง";renderMeals(k,p);return}
    if(v>0&&slot[0]!=="x"){toggleIdx(k,slot==="s"?snackIdx(p):mealIdx(p,+slot),true);saveDay(k)}
    priceEditing=null;priceErr="";render()});
  q("[data-prdel]").forEach(b=>b.onclick=()=>{setPrice(k,b.dataset.prdel,0);priceEditing=null;priceErr="";renderMeals(k,p)});
'''


def patch_fit_js(js):
    js = rep(js, 'function renderMeals(k,p){', FIT_HELPERS + 'function renderMeals(k,p){')
    js = rep(js, '${canPhoto()?`<button class="chipbtn photo" data-photo="${i}"',
             '${priceChip(k,String(i))}${canPhoto()?`<button class="chipbtn photo" data-photo="${i}"')
    js = rep(js, '${canPhoto()?`<button class="chipbtn photo" data-photo="s"',
             '${priceChip(k,"s")}${canPhoto()?`<button class="chipbtn photo" data-photo="s"')
    js = rep(js, '${editing===k+":m"+i?editForm(k+":m"+i,e,!!act):""}',
             '${editing===k+":m"+i?editForm(k+":m"+i,e,!!act):""}${priceEd(k,String(i),nm?act.d:r.text)}')
    js = rep(js, '${editing===k+":ms"?editForm(k+":ms",se,!!sAct):""}',
             '${editing===k+":ms"?editForm(k+":ms",se,!!sAct):""}${priceEd(k,"s",sNm?sAct.d:sTxt)}')
    js = rep(js, '${x.w?`<span class="warnline">⚠ ${esc(x.w)}</span>`:""}',
             '${x.w?`<span class="warnline">⚠ ${esc(x.w)}</span>`:""}${priceEd(k,"x"+x.id,x.d)}')
    js = rep(js, '<div class="acts"><button class="chipbtn" data-edit="${key}">แก้ตัวเลข</button>',
             '<div class="acts"><button class="chipbtn" data-edit="${key}">แก้ตัวเลข</button>${priceChip(k,"x"+x.id)}')
    js = rep(js, 'dd.x=(dd.x||[]).filter(y=>y!==x);saveDay(k);render();',
             'dd.x=(dd.x||[]).filter(y=>y!==x);if(x)setPrice(k,"x"+x.id,0);saveDay(k);render();')
    js = rep(js, '$("xText").value="";$("xK").value="";saveDay(k);',
             'const pr0=num($("xPrice").value);$("xText").value="";$("xK").value="";$("xPrice").value="";saveDay(k);if(pr0>0)setPrice(k,"x"+item.id,pr0,shortName(item.d));')
    # one date for the whole app: the shell's date bar drives ฟิต's `cur`
    js = rep(js, '$("gotoday").onclick=()=>{cur=new Date(today);editing=null;render()};',
             '$("gotoday").onclick=()=>{cur=new Date(today);editing=null;render()};\nif(typeof TL!=="undefined")TL.fitDate=d=>{const n=new Date(d);n.setHours(0,0,0,0);if(+n===+cur)return;cur=n;editing=null;priceEditing=null;render()};')
    js = rep(js, '\nfunction render(){', '\nfunction render(){if(typeof TL!=="undefined"&&TL.fromFit)TL.fromFit(cur);')
    # append bind handlers at the end of bindMeals (just before renderMuscle)
    js = rep(js, '\n}\nfunction renderMuscle(k){', FIT_BIND + '}\nfunction renderMuscle(k){')
    return js


def patch_fit_body(body, css):
    body = rep(body, 'aria-label="แคลอรี (ไม่บังคับ)">',
               'aria-label="แคลอรี (ไม่บังคับ)"><input id="xPrice" class="narrow" type="number" inputmode="decimal" min="0" max="100000" step="any" placeholder="฿ ราคา" aria-label="ราคา (ไม่บังคับ)">')
    css += "\n#datebar{display:none!important}"
    css += "\n.chipbtn.paid{border-color:var(--good);color:var(--good);font-weight:600}\n.prf .btn{min-height:40px}\n"
    return body, css


AOM_BRIDGE = r'''
/* ===== โตไลฟ์ bridge: meals priced in ฟิต live here as food transactions tagged with `link` ===== */
TL.aomRefresh=()=>{try{scheduleRender()}catch(e){}};
TL.aom={
  linked(link){for(const [,b] of D()){if(b&&b.kind==='tx'&&Array.isArray(b.items)){const it=b.items.find(i=>i&&i.link===link);if(it)return num(it.amt)}}return null},
  setLinked(link,t){
    if(Demo.on||!Store.loaded)return false;
    let found=null;
    for(const [id,b] of Store.docs){if(b&&b.kind==='tx'&&Array.isArray(b.items)&&b.items.some(i=>i&&i.link===link)){found={id,b};break}}
    if(t){
      const key=String(t.date).slice(0,7),tid='tx-'+key;
      if(found&&found.id===tid)return Store.put(tid,Object.assign({},found.b,{items:found.b.items.map(i=>i&&i.link===link?Object.assign({},i,{amt:num(t.amt),note:i.note||t.note,edited:Date.now()}):i)}),true);
      if(found&&!Store.put(found.id,Object.assign({},found.b,{items:found.b.items.filter(i=>!(i&&i.link===link))}),true))return false;
      const items=txMonth(key).slice();
      items.push({id:uid(),ts:Date.now(),type:'out',cat:'food',amt:num(t.amt),date:t.date,note:t.note,link});
      return Store.put(tid,{kind:'tx',month:key,items},true);
    }
    if(found)return Store.put(found.id,Object.assign({},found.b,{items:found.b.items.filter(i=>!(i&&i.link===link))}),true);
    return true;
  }
};
'''


def patch_aom_js(js):
    js = rep(js, """    txt+=' · งบวันนี้ <b>'+B(Math.max(0,perDay))+'</b>'+(spent>perDay&&perDay>0?' <span class="tag bad">เกินงบ</span>':'')}""",
             """    txt+=' · งบวันนี้ <b>'+B(Math.max(0,perDay))+'</b>';
    if(perDay>0){const left=perDay-spent,used=Math.min(100,spent/perDay*100);
      txt+='<span class="q-left'+(left<0?' bad':'')+'"><span class="q-lab">'+(left>=0?'เหลือใช้ได้วันนี้':'เกินงบวันนี้')+'</span><b class="num">'+B(Math.abs(left))+'</b></span>'
        +'<span class="q-meter'+(left<0?' bad':used>=80?' warn':'')+'" role="img" aria-label="ใช้ไป '+Math.round(used)+'% ของงบวันนี้"><i style="width:'+used.toFixed(1)+'%"></i></span>'}}""")
    js = rep(js, 'function onData(){scheduleRender()}',
             'function onData(){scheduleRender();try{if(typeof TL!=="undefined"&&TL.onAomData)TL.onAomData()}catch(e){}}')
    js = rep(js, 'window.__toaom={', AOM_BRIDGE + 'window.__toaom={')
    js = rep(js, "const today=()=>{const d=new Date();",
             "const today=()=>{const d=(typeof TL!=='undefined'&&TL.date)?new Date(TL.date):new Date();")
    js = rep(js, "let txt='วันนี้ใช้ไป <b>'", "const DW=(typeof TL!=='undefined'&&TL.dayWord)?TL.dayWord():'วันนี้';let txt=DW+'ใช้ไป <b>'")
    js = rep(js, "txt+=' · งบวันนี้ <b>'", "txt+=' · งบ'+DW+' <b>'")
    js = rep(js, "+'วันนี้ '+fullDate(now);", "+((typeof TL!=='undefined'&&TL.isToday&&!TL.isToday())?'กำลังดูวันที่ ':'วันนี้ ')+fullDate(now);")
    js = rep(js, "let txt=DW+'ใช้ไป <b>'", "{const h=$('#quickSum')&&$('#quickSum').closest('section,.card');const h2=h&&h.querySelector('h2');if(h2&&h2.lastChild&&h2.lastChild.nodeType===3)h2.lastChild.textContent='จดรายจ่าย'+DW.trim()}let txt=DW+'ใช้ไป <b>'")
    js = rep(js, "(left>=0?'เหลือใช้ได้วันนี้':'เกินงบวันนี้')", "(left>=0?'เหลือใช้ได้'+DW:'เกินงบ'+DW)")
    return js


def patch_aom_css(css):
    return css + """
.q-left{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-top:10px;padding:10px 12px;border-radius:12px;background:var(--good-soft);color:var(--good)}
.q-left .q-lab{font-size:14.5px;font-weight:600}
.q-left b{font:600 24px/1.2 var(--f-mono);font-variant-numeric:tabular-nums}
.q-left.bad{background:var(--bad-soft);color:var(--bad)}
.q-meter{display:block;height:6px;margin-top:6px;border-radius:999px;background:var(--sunk);overflow:hidden}
.q-meter i{display:block;height:100%;border-radius:999px;background:var(--good)}
.q-meter.warn i{background:var(--warn)}
.q-meter.bad i{background:var(--bad)}
"""


# ---------- compact layout: one header (the shell's), real bottom tab bar in ออม ----------
SETTINGS_BTN = ('<button class="icon-btn" id="openSettings" type="button" aria-label="ข้อมูลของฉัน" title="ข้อมูลของฉัน">'
                '<svg viewBox="0 0 24 24"><path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2.2"/><circle cx="9" cy="17" r="2.2"/></svg></button>')


def patch_aom_body(body):
    body = rep(body, '</svg>ภาพรวม</a>', '</svg>สรุป</a>')
    body = rep(body, SETTINGS_BTN, '')
    # settings becomes the 7th tab, so it is reachable on phones
    i = body.index('<a href="#learn" data-v="learn">')
    j = body.index('</a>', i) + 4
    btn = (SETTINGS_BTN.replace('<button class="icon-btn" id="openSettings"', '<button class="icon-btn tl-set" id="openSettings"')
           .replace('</svg></button>', '</svg><span class="tl-lab">ข้อมูล</span></button>'))
    body = body[:j] + btn + body[j:]
    return body


def patch_aom_layout_css(css):
    css = rep(css, 'backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);', '')
    css = rep(css, 'grid-template-columns:repeat(6,1fr)', 'grid-template-columns:repeat(7,1fr)')
    return css + """
.top .brand{display:none}
.greet{display:none}
.tabs .tl-set .tl-lab{display:none}
@media (max-width:760px){
  .top{position:static;border:0;background:transparent}
  .top-in{min-height:0}
  .tabs a{font-size:11.5px}
  .tabs .tl-set{width:auto;height:auto;border:0;border-radius:0;background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;padding:8px 0 7px;color:var(--ink-2);font:600 11.5px/1.2 var(--f-body)}
  .tabs .tl-set .tl-lab{display:block}
  .toasts{bottom:calc(84px + env(safe-area-inset-bottom,0px))}
}
"""


def patch_fit_layout_css(css):
    return css + """
.logo,header h1{display:none}
header{align-items:center}
.progress{font-size:.85rem}
.progress br{display:none}
#askFab{display:none!important}
#t-shop,#goEat{display:none!important}
.tabs{grid-template-columns:repeat(3,1fr)!important}
"""


def patch_fit_layout_js(js):
    return rep(js, '$("prog").innerHTML=dayNo<1?"เริ่มแผน<br>อีก "+(1-dayNo)+" วัน":"วันที่ "+dayNo+"<br>ของแผน";',
               '$("prog").innerHTML=dayNo<1?"เริ่มแผนอีก "+(1-dayNo)+" วัน":"วันที่ "+dayNo+" ของแผน";')


# ---------- save meal photos to the device ----------
PHOTO_SAVE_JS = r'''
async function savePhoto(id,name,btn){
  if(!id)return;const old=btn.textContent;btn.disabled=true;btn.textContent="กำลังเตรียมรูป…";
  try{
    const dl=await window.claude?.use?.("downloads");
    const blob=await (await fetch("/_blob/"+id)).blob();
    if(!dl)throw {code:"unavailable"};
    await dl.save({filename:name+".jpg",data:blob});btn.textContent="บันทึกแล้ว ✓";
  }catch(e){btn.textContent=e&&e.code==="declined"?old:"บันทึกไม่สำเร็จ ลองใหม่"}
  finally{btn.disabled=false;setTimeout(()=>{btn.textContent=old},2500)}
}
'''


def patch_fit_photo_js(js):
    js = rep(js, 'function renderMeals(k,p){', PHOTO_SAVE_JS + 'function renderMeals(k,p){', 1)
    js = rep(js, '${assets&&ph[i]?`<button class="chipbtn" data-rmphoto="${i}">ลบรูป</button>`:""}',
             '${ph[i]?`<button class="chipbtn" data-savephoto="${esc(ph[i])}" data-pname="อาหาร-${k}-มื้อ${i+1}">บันทึกรูป</button>`:""}${assets&&ph[i]?`<button class="chipbtn" data-rmphoto="${i}">ลบรูป</button>`:""}')
    js = rep(js, '${assets&&ph.s?`<button class="chipbtn" data-rmphoto="s">ลบรูป</button>`:""}',
             '${ph.s?`<button class="chipbtn" data-savephoto="${esc(ph.s)}" data-pname="อาหาร-${k}-รองท้อง">บันทึกรูป</button>`:""}${assets&&ph.s?`<button class="chipbtn" data-rmphoto="s">ลบรูป</button>`:""}')
    js = rep(js, '${priceChip(k,"x"+x.id)}',
             '${priceChip(k,"x"+x.id)}${x.ph?`<button class="chipbtn" data-savephoto="${esc(x.ph)}" data-pname="อาหาร-${k}-${esc(String(x.t||"").replace(":",""))}">บันทึกรูป</button>`:""}')
    js = rep(js, '  q("[data-price]").forEach(',
             '  q("[data-savephoto]").forEach(b=>b.onclick=()=>savePhoto(b.dataset.savephoto,b.dataset.pname,b));\n  q("[data-price]").forEach(')
    return js


# ---------- calories burned from logged exercise ----------
BURN_JS = r'''
/* โตไลฟ์: run/walk energy — distance known: ~1 kcal per kg per km; else ~6.5 MET for run/walk intervals */
function wtOn(k){const w=(S.weights||[]).filter(r=>r[0]<=k);const r=w.length?w[w.length-1]:(S.weights||[])[0];return r?+r[1]:85}
function burnOf(k,l){if(!l||!(l.done==="1"||l.done==="2"))return 0;const kg=wtOn(k),km=parseFloat(l.km),mn=parseFloat(l.min);
  let v=0;if(km>0)v=kg*km;else if(mn>0)v=6.5*kg*mn/60;return Math.round(v/10)*10}
'''


def patch_fit_burn(js, body, css):
    js = rep(js, 'function renderRun(){', BURN_JS + 'function renderRun(){')
    js = rep(js, '''${ok?'<span class="ok">✓</span>'+(l.km?" "+esc(l.km)+" กม.":""):l.done==="3"?"ข้าม":""}''',
             '''${ok?'<span class="ok">✓</span>'+(l.km?" "+esc(l.km)+" กม.":"")+(burnOf(kk,l)?" · "+burnOf(kk,l)+" kcal":""):l.done==="3"?"ข้าม":""}''')
    js = rep(js, 'let dn=0,mn=0,km=0;for(let i=0;i<7;i++){const l=S.runs[iso(addD(mon,i))];if(l&&(l.done==="1"||l.done==="2")){dn++;mn+=+l.min||0;km+=+l.km||0}}',
             'let dn=0,mn=0,km=0,bk=0;for(let i=0;i<7;i++){const kk=iso(addD(mon,i)),l=S.runs[kk];if(l&&(l.done==="1"||l.done==="2")){dn++;mn+=+l.min||0;km+=+l.km||0;bk+=burnOf(kk,l)}}')
    js = rep(js, '$("rKm").textContent=km.toFixed(1);', '$("rKm").textContent=km.toFixed(1);$("rKcal").textContent=bk.toLocaleString();')
    js = rep(js, '$("runStatus").textContent=db?"บันทึกแล้ว":"บันทึกในเครื่องนี้แล้ว";',
             '{const b=burnOf(k,rec);$("runStatus").textContent=(db?"บันทึกแล้ว":"บันทึกในเครื่องนี้แล้ว")+(b?" · เผาผลาญ ≈ "+b+" kcal":"")}')
    js = rep(js, '''$("kLeg").innerHTML='<span>กินจริง '+EK.toLocaleString()+'</span><span class="pl">แผน '+K.toLocaleString()+'</span>';''',
             '''{const b=burnOf(k,S.runs[k]);$("kLeg").innerHTML='<span>กินจริง '+EK.toLocaleString()+'</span><span class="pl">แผน '+K.toLocaleString()+'</span>'+(b?'<span class="burn">ออกกำลังเผาผลาญ ≈ '+b.toLocaleString()+' kcal (เป้าไม่เปลี่ยน)</span>':'')}''')
    body = rep(body, '<div><b id="rKm">0</b><span>กม. รวม</span></div>',
               '<div><b id="rKm">0</b><span>กม. รวม</span></div><div><b id="rKcal">0</b><span>kcal ใช้ไป</span></div>')
    css += "\n.stats{grid-template-columns:repeat(4,1fr)!important}\n.burn{flex-basis:100%;color:var(--run);font-weight:600}\n"
    return js, body, css


# ---------- one eat toggle per meal (no separate "ไม่ได้กิน") ----------
def patch_fit_eat_toggle(js):
    js = rep(js, '${sk?"":`<button class="chipbtn${eaten?" on":""}" data-eat="${i}" aria-pressed="${eaten}">${eaten?"กินแล้ว ✓":"กินแล้ว"}</button>`}<button class="chipbtn${sk?" on":""}" data-skip="${i}" aria-pressed="${!!sk}">${sk?"ไม่ได้กิน ✓ (กดยกเลิก)":"ไม่ได้กิน"}</button>',
             '<button class="chipbtn${eaten?" on":""}" data-eat="${i}" aria-pressed="${eaten}">${eaten?"กินแล้ว ✓":"ยังไม่กิน · แตะเมื่อกิน"}</button>')
    js = rep(js, '${sSk?"":`<button class="chipbtn${sEaten?" on":""}" data-eatsnack="1" aria-pressed="${sEaten}">${sEaten?"กินแล้ว ✓":"กินแล้ว"}</button>`}<button class="chipbtn${sSk?" on":""}" data-skip="s" aria-pressed="${!!sSk}">${sSk?"ไม่ได้กิน ✓ (กดยกเลิก)":"ไม่ได้กิน"}</button>',
             '<button class="chipbtn${sEaten?" on":""}" data-eatsnack="1" aria-pressed="${sEaten}">${sEaten?"กินแล้ว ✓":"ยังไม่กิน · แตะเมื่อกิน"}</button>')
    js = rep(js, 'q("[data-eat]").forEach(b=>b.onclick=()=>{toggleIdx(k,mealIdx(p,+b.dataset.eat));saveDay(k);render()});',
             'q("[data-eat]").forEach(b=>b.onclick=()=>{const dd=day(k);if(dd.n)delete dd.n[b.dataset.eat];toggleIdx(k,mealIdx(p,+b.dataset.eat));saveDay(k);render()});')
    js = rep(js, 'q("[data-eatsnack]").forEach(b=>b.onclick=()=>{toggleIdx(k,snackIdx(p));saveDay(k);render()});',
             'q("[data-eatsnack]").forEach(b=>b.onclick=()=>{const dd=day(k);if(dd.n)delete dd.n.s;toggleIdx(k,snackIdx(p));saveDay(k);render()});')
    return js


def patch_fit_totals_fix(js):
    # a meal counts as eaten only when its own checklist item is ticked (was compared by row number)
    return rep(js, 'K+=+e.k||0;P+=+e.p||0;if(c.includes(i)){EK+=+e.k||0;EP+=+e.p||0}',
               'K+=+e.k||0;P+=+e.p||0;if(c.includes(mealIdx(p,i))){EK+=+e.k||0;EP+=+e.p||0}')
