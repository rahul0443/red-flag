const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const EX=["USPS: Your package could not be delivered due to an unpaid customs fee of $1.99. Pay within 12 hours or it will be returned: http://usps-redelivery-help.top/pay",
"IRS FINAL NOTICE: You owe $2,847 in back taxes. A warrant will be issued for your arrest today. Call 855-555-0142 immediately and pay with Apple gift cards to resolve. Do not tell anyone.",
"CVS Pharmacy: Your prescription is ready for pickup at 123 Main St. Reply STOP to opt out.",
"Hi Sarah, are we still on for dinner Friday?"];
const I={
 link:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/></svg>',
 cal:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
 list:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4 6v6c0 4.5 3.2 8 8 9 4.8-1 8-4.5 8-9V6z"/></svg>',
 co:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21V8l8-5 8 5v13M9 21v-6h6v6"/></svg>',
 box:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="3"/><path d="M3 9h18"/></svg>',
 open:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
 spin:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M12 3a9 9 0 1 0 9 9" /></svg>',
 ok:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
 x:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
 bang:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"><path d="M12 6v8M12 18v.01"/></svg>',
 dash:'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"><path d="M7 12h10"/></svg>'};
const VICON={
 Scam:'<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4 6v6c0 4.5 3.2 8 8 9 4.8-1 8-4.5 8-9V6z"/><path d="m9.5 9.5 5 5m0-5-5 5"/></svg>',
 Suspicious:'<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4 6v6c0 4.5 3.2 8 8 9 4.8-1 8-4.5 8-9V6z"/><path d="M12 8.5v4.5M12 16.2v.01"/></svg>',
 Safe:'<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4 6v6c0 4.5 3.2 8 8 9 4.8-1 8-4.5 8-9V6z"/><path d="m8.8 12.3 2.4 2.4 4.2-4.6"/></svg>'};
const TOOLS=[["expand_url","Follow the link",I.link],["rdap_lookup","Domain age",I.cal],["check_blocklists","Phishing lists",I.list],["official_contact_check","Real company",I.co],["inspect_link_sandbox","Safe browser",I.box],["triage","Open-weight second opinion",I.open]];
const LABEL={expand_url:"Following the link",rdap_lookup:"Checking domain registration",check_blocklists:"Checking phishing lists",official_contact_check:"Comparing with the real company",inspect_link_sandbox:"Opening the link in an isolated browser"};
const ta=$("msg"),stage=$("stage"),logEl=$("log");
let busy=false,clockT=null,t0=0,lastVerdict=null,lastText="",triageV=null;

/* ---------- composer ---------- */
function sync(){
 ta.style.height="auto";ta.style.height=(ta.value?Math.min(320,Math.max(120,ta.scrollHeight)):120)+"px";
 const n=ta.value.length;$("count").textContent=n>3200?`${n}/4000`:"";$("count").className="count"+(n>3800?" warn":"");
 $("go").disabled=busy||!ta.value.trim()}
ta.addEventListener("input",sync);
ta.addEventListener("keydown",e=>{if(e.key==="Enter"&&(e.metaKey||e.ctrlKey)&&!$("go").disabled){e.preventDefault();$("go").click()}});
document.querySelectorAll("[data-ex]").forEach(b=>b.onclick=()=>{ta.value=EX[b.dataset.ex];sync();ta.focus()});
function setBusy(b){busy=b;["imgBtn","audBtn","recBtn"].forEach(id=>{if(!(id==="recBtn"&&rec))$(id).disabled=b});document.querySelectorAll(".ex").forEach(e=>e.disabled=b);ta.readOnly=b;sync()}

/* ---------- case view ---------- */
function resetCase(){
 logEl.innerHTML="";stage.innerHTML="";lastVerdict=null;triageV=null;
 $("checks").innerHTML=TOOLS.map(([k,n,ic])=>`<div class="check" id="ck-${k}"><div class="ic">${ic}</div><div><div class="nm">${n}</div><div class="st">Waiting</div></div></div>`).join("");
 stage.innerHTML=`<div class="card wait"><div><div class="orb"></div><b>Investigating</b>Checking links, domains and the real company</div></div>`;
 document.body.className="running";$("ttl").textContent="Investigating";say("Investigation started");window.scrollTo(0,0);t0=Date.now();clearInterval(clockT);
 const tick=()=>$("clock").textContent=((Date.now()-t0)/1000).toFixed(0)+"s";tick();clockT=setInterval(tick,1000)}
function setCheck(k,state,text,icon){
 const el=$("ck-"+k);if(!el)return;el.className="check "+state;
 if(icon)el.querySelector(".ic").innerHTML=icon;if(text!=null)el.querySelector(".st").textContent=text}
function log(cls,title,body){
 const li=document.createElement("li");li.className=cls;li.innerHTML=`<span class="bul"></span><div><div class="k">${esc(title)}</div>${body}</div>`;logEl.appendChild(li);return li}
function say(t){$("sr").textContent=t}
function caseText(t){$("caseMsg").textContent=t;lastText=t}

/* ---------- events ---------- */
function result(tool,r){
 if(r.error)return`<div class="chips"><span class="chip">${esc(r.error)}</span></div>`;
 if(tool==="expand_url"){const n=r.chain?.[r.chain.length-1]?.note;return`<div class="chips"><span class="chip">${r.redirect_count} redirect(s)</span><span class="chip">lands on ${esc(r.final_domain||"unknown")}</span>${n?`<span class="chip">${esc(n)}</span>`:""}</div>`}
 if(tool==="rdap_lookup")return`<div class="chips"><span class="chip">${r.age_days!=null?r.age_days+" days old":"age unknown"}</span>${r.registrar?`<span class="chip">${esc(r.registrar)}</span>`:""}</div>`;
 if(tool==="check_blocklists")return`<div class="chips"><span class="chip">${r.listed_in?.length?"listed in "+esc(r.listed_in.join(", ")):"not in known feeds"}</span>${(r.lookalike_signals||[]).map(s=>`<span class="chip t">${esc(s)}</span>`).join("")}</div>`;
 if(tool==="official_contact_check"){if(!r.known)return`<div class="chips"><span class="chip">brand not in our database</span></div>`;return`<div class="chips"><span class="chip">official: ${esc((r.official_domains||[]).join(", "))}</span>${"matches_official_domain" in r?`<span class="chip ${r.matches_official_domain?"":"t"}">${r.matches_official_domain?"domain matches":"domain does not match"}</span>`:""}</div>`}
 if(tool==="inspect_link_sandbox")return`<div class="chips"><span class="chip">${esc(r.title||"no page title")}</span></div>`+(r.screenshot_b64?`<img alt="The page, as seen inside the isolated browser" src="data:image/jpeg;base64,${r.screenshot_b64}">`:"");
 return`<code>${esc(JSON.stringify(r)).slice(0,200)}</code>`}
function checkFromResult(tool,r){
 if(r.error){
  if(tool==="rdap_lookup"&&/no registration/i.test(r.error))setCheck(tool,"bad","No registration record found",I.x);
  else if(tool==="inspect_link_sandbox")setCheck(tool,"warn","Page could not be opened",I.bang);
  else setCheck(tool,"warn","Could not check",I.bang);return}
 if(tool==="expand_url"){const n=r.redirect_count;setCheck(tool,"ok",n?`${n} redirect${n>1?"s":""} to ${r.final_domain}`:`Leads to ${r.final_domain||"unknown"}`,I.ok)}
 else if(tool==="rdap_lookup"){const d=r.age_days;if(d==null)setCheck(tool,"warn","Age unknown",I.bang);else if(d<90)setCheck(tool,"bad",`Registered ${d} days ago`,I.x);else setCheck(tool,"ok",`${d>730?Math.round(d/365)+" years":d+" days"} old`,I.ok)}
 else if(tool==="check_blocklists"){if(r.listed_in?.length)setCheck(tool,"bad","On a phishing blocklist",I.x);else if(r.lookalike_signals?.length)setCheck(tool,"bad",r.lookalike_signals[0],I.x);else if(r.suspicious_tld)setCheck(tool,"warn","Not listed, suspicious domain ending",I.bang);else setCheck(tool,"ok","Not on known lists",I.ok)}
 else if(tool==="official_contact_check"){if(!r.known)setCheck(tool,"warn","Company not in our database",I.bang);else if("matches_official_domain" in r)r.matches_official_domain?setCheck(tool,"ok","Matches the real domain",I.ok):setCheck(tool,"bad","Does not match the real domain",I.x);else setCheck(tool,"ok","Official details found",I.ok)}
 else if(tool==="inspect_link_sandbox"){const pw=r.password_fields>0||/password|sign in|log ?in/i.test(r.text||"");pw?setCheck(tool,"bad","Page asks you to log in",I.x):setCheck(tool,"ok","Opened safely",I.ok)}}

function handle(ev){
 const t=ev.type;
 if(t==="extracting"){log("","Reading",`<span>${ev.source==="voicemail"?"Muse Voice Transcribe is listening":"Muse Spark is reading the image"}</span>`);caseText(ev.source==="voicemail"?"Transcribing voicemail…":"Reading screenshot…")}
 else if(t==="extracted"){caseText(ev.text);log("res",ev.source==="voicemail"?"Transcript":"Text in screenshot",`<div class="quote" dir="auto">${esc(ev.text)}</div>`)}
 else if(t==="start"){log("","Message received",ev.urls_found?.length?`<span>${ev.urls_found.length} link${ev.urls_found.length>1?"s":""}: ${ev.urls_found.slice(0,3).map(u=>`<code>${esc(u)}</code>`).join(" ")}</span>`:"<span>No links found. Checking wording and claims.</span>");if(!ev.urls_found?.length)["expand_url","rdap_lookup","check_blocklists","inspect_link_sandbox"].forEach(k=>setCheck(k,"skip","No link to check",I.dash))}
 else if(t==="triage"){triageV=ev.verdict;renderAgree();setCheck("triage",ev.verdict==="Looks Safe"?"ok":ev.verdict==="Scam"?"bad":"warn",`${ev.verdict||"?"} · ${(ev.latency_ms/1000).toFixed(1)}s on open weights`,ev.verdict==="Looks Safe"?I.ok:ev.verdict==="Scam"?I.x:I.bang);log("res","Open-weight second opinion",`<span><b>${esc(ev.verdict||"?")}</b> in ${(ev.latency_ms/1000).toFixed(1)}s from <code>${esc(ev.model)}</code>, served by Baseten</span>`)}
 else if(t==="thought")log("",'Thinking',`<div class="think">${esc(ev.text)}</div>`);
 else if(t==="tool_call"){say((LABEL[ev.tool]||"Working")+"…");setCheck(ev.tool,"run","Checking…",I.spin);log("tool",LABEL[ev.tool]||ev.tool,`<code>${esc(ev.args.url||ev.args.domain||ev.args.brand||"")}</code>`)}
 else if(t==="tool_result"){checkFromResult(ev.tool,ev.result);log("res","Result",result(ev.tool,ev.result))}
 else if(t==="verdict"){finish(ev)}
 else if(t==="error"){fail(ev.message)}}

function finish(v){
 lastVerdict=v;clearInterval(clockT);document.body.className="done";$("ttl").textContent="Result";say(`Verdict: ${v.verdict}, ${Math.round((v.confidence||0)*100)} percent confident. ${v.summary}`);
 document.querySelectorAll(".check").forEach(c=>{if(c.classList.contains("run")||c.querySelector(".st").textContent==="Waiting"){c.className="check skip";c.querySelector(".st").textContent="Not needed";c.querySelector(".ic").innerHTML=I.dash}});
 if(!["Scam","Suspicious","Looks Safe"].includes(v.verdict))v={...v,verdict:"Suspicious"};
 const k=v.verdict==="Looks Safe"?"Safe":v.verdict,pct=Math.round((v.confidence||0)*100);
 const shot=[...logEl.querySelectorAll("img")].pop();
 const ev=(v.evidence||[]).map(e=>`<li><span class="dot ${esc(e.severity)}"></span><div dir="auto">${esc(e.finding)}<span class="src">${esc(e.source)}</span></div></li>`).join("");
 stage.innerHTML=`<div class="card verdict ${k}" role="status"><div class="vhead"><div class="gauge"><svg viewBox="0 0 96 96"><circle class="tr" cx="48" cy="48" r="42"/><circle class="fg" id="fg" cx="48" cy="48" r="42"/></svg><div class="ico">${VICON[k]}</div></div><div><div class="vtitle" id="vtitle" tabindex="-1">${esc(v.verdict)}</div><div class="vconf">${pct}% confident · ${Math.round((Date.now()-t0)/1000)} seconds</div></div></div>
 <div class="vbody"><p class="sum" dir="auto" id="sum">${esc(v.summary)}</p>${v.tactics?.length?`<div class="chips">${v.tactics.map(x=>`<span class="chip t">${esc(x)}</span>`).join("")}</div>`:""}
 <div class="agree" id="agree"></div><div class="advice"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8v.01"/></svg><div><b>What to do</b><span>${esc(v.advice)}</span></div></div>
 ${shot?`<div class="shotbox"><div class="evh" style="margin-top:0">What the link opens</div><div class="win"><div class="tb"><i></i><i></i><i></i><span>Isolated browser</span></div><img alt="The page the link opens" src="${shot.src}"></div><div class="cap">Captured inside an isolated cloud browser. Nothing was opened on your device.</div></div>`:""}
 ${ev?`<div class="evh">Evidence</div><ul class="ev">${ev}</ul>`:""}
 ${k!=="Safe"?`<div class="report"><div class="evh" style="margin:0">Report it (US)</div><a href="https://reportfraud.ftc.gov" target="_blank" rel="noopener noreferrer">FTC ReportFraud</a><a href="https://www.ic3.gov" target="_blank" rel="noopener noreferrer">FBI IC3</a><a href="sms:7726" rel="noopener">Forward the text to 7726</a></div>`:""}
 <div class="actions"><button class="btn2" id="copyBtn">Copy report</button>${navigator.share?'<button class="btn2" id="shareBtn">Share</button>':""}<button class="btn2" id="againBtn">Check another</button></div></div></div>`;
 renderAgree();
 requestAnimationFrame(()=>requestAnimationFrame(()=>{$("fg").style.strokeDashoffset=264*(1-Math.max(.04,v.confidence||0))}));
 $("copyBtn").onclick=copyReport;$("againBtn").onclick=again;if($("shareBtn"))$("shareBtn").onclick=()=>navigator.share({title:"Red Flag verdict",text:reportText()}).catch(()=>{});
 $("vtitle").focus({preventScroll:true});window.scrollTo({top:0,behavior:"smooth"})}
function fail(msg){
 clearInterval(clockT);document.body.className="done";$("ttl").textContent="Could not check";say("Could not check: "+msg);
 stage.innerHTML=`<div class="card"><div class="errcard"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 2 20h20zM12 10v4M12 17v.01"/></svg><div><b>We could not check that</b><p>${esc(msg)}</p><div class="actions" style="margin-top:16px"><button class="btn2" id="againBtn">Try again</button></div></div></div></div>`;
 $("againBtn").onclick=again}
function again(){if(busy)return;document.body.className="";stage.innerHTML="";window.scrollTo({top:0,behavior:"smooth"});ta.focus({preventScroll:true})}
$("backBtn").onclick=again;
addEventListener("keydown",e=>{if(e.key==="Escape"&&document.body.classList.contains("done"))again()});
function renderAgree(){
 const el=$("agree");if(!el||!lastVerdict||!triageV)return;
 const same=triageV===lastVerdict.verdict,flag=x=>x==="Looks Safe"?0:1,close=same||flag(triageV)===flag(lastVerdict.verdict);
 el.className="agree"+(close?"":" no");
 el.innerHTML=same?`<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg><span><b>Two models agree.</b> Muse Spark and open-weight Muse Spark Open both say ${esc(triageV)}.</span>`
  :close?`<span>Open-weight Muse Spark Open said <b>${esc(triageV)}</b>; both models flag it as a risk.</span>`
  :`<span><b>The models disagree.</b> Open-weight Muse Spark Open said ${esc(triageV)}. Treat this message with extra caution.</span>`}
function reportText(){
 const v=lastVerdict;if(!v)return"";
 return`Red Flag verdict: ${v.verdict} (${Math.round((v.confidence||0)*100)}% confident)\n${v.summary}\n\nEvidence:\n${(v.evidence||[]).map(e=>`- [${e.severity}] ${e.finding} (${e.source})`).join("\n")}\n\nWhat to do: ${v.advice}\n\nMessage checked:\n${lastText}`}
function copyReport(){
 const txt=reportText();if(!txt)return;
 navigator.clipboard.writeText(txt).then(()=>{$("copyBtn").textContent="Copied";setTimeout(()=>{const b=$("copyBtn");if(b)b.textContent="Copy report"},1800)},()=>{})}

/* ---------- transport ---------- */
async function run(url,init,shownText){
 resetCase();setBusy(true);caseText(shownText||"");let got=false;
 try{
  const res=await fetch(url,init);
  if(res.status===422){fail("That input could not be checked. It may be empty or longer than 4000 characters.");setBusy(false);return}
  if(!res.ok)throw new Error("status "+res.status);
  const rd=res.body.getReader(),dec=new TextDecoder();let buf="";
  while(true){const{done,value}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});
   let i;while((i=buf.indexOf("\n\n"))>=0){const line=buf.slice(0,i).replace(/^data: /,"");buf=buf.slice(i+2);if(!line)continue;let ev;try{ev=JSON.parse(line)}catch(e){continue}if(ev.type==="verdict"||ev.type==="error")got=true;handle(ev)}}
  if(!got)fail("The check ended without an answer. Please try again.")
 }catch(e){fail("We lost the connection to the server. Please try again.")}
 clearInterval(clockT);setBusy(false)}
$("go").onclick=()=>{const text=ta.value.trim();if(!text||busy)return;
 run("/api/investigate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})},text)};

/* ---------- screenshots ---------- */
async function normalizeImage(file){
 try{const bmp=await createImageBitmap(file),k=Math.min(1,2000/Math.max(bmp.width,bmp.height)),c=document.createElement("canvas");
  c.width=Math.max(1,Math.round(bmp.width*k));c.height=Math.max(1,Math.round(bmp.height*k));
  const g=c.getContext("2d");g.fillStyle="#fff";g.fillRect(0,0,c.width,c.height);g.drawImage(bmp,0,0,c.width,c.height);
  const b=await new Promise(r=>c.toBlob(r,"image/jpeg",.92));if(!b)throw 0;return b}catch(e){return null}}
function sendFile(url,blob,name,label){const fd=new FormData();fd.append("file",blob,name);run(url,{method:"POST",body:fd},label)}
async function sendImage(file){
 const b=await normalizeImage(file);
 if(!b){resetCase();fail("That file could not be opened as an image. Try a normal screenshot (PNG or JPEG).");return}
 sendFile("/api/investigate/image",b,"upload.jpg","Reading screenshot…")}
$("imgBtn").onclick=()=>$("imgIn").click();
$("imgIn").onchange=e=>{const f=e.target.files[0];if(f)sendImage(f);e.target.value=""};
document.addEventListener("paste",e=>{const it=[...(e.clipboardData?.items||[])].find(i=>i.type.startsWith("image/"));if(it&&!busy){e.preventDefault();sendImage(it.getAsFile())}});

/* ---------- voicemail (Meta ASR takes WAV: convert in the browser) ---------- */
async function toWav(blob){
 const ac=new (window.AudioContext||window.webkitAudioContext)();const buf=await ac.decodeAudioData(await blob.arrayBuffer());ac.close();
 const sr=16000,off=new OfflineAudioContext(1,Math.ceil(buf.duration*sr),sr),src=off.createBufferSource();src.buffer=buf;src.connect(off.destination);src.start();
 const pcm=(await off.startRendering()).getChannelData(0),out=new DataView(new ArrayBuffer(44+pcm.length*2));
 const w=(o,t)=>[...t].forEach((c,i)=>out.setUint8(o+i,c.charCodeAt(0)));
 w(0,"RIFF");out.setUint32(4,36+pcm.length*2,true);w(8,"WAVEfmt ");out.setUint32(16,16,true);out.setUint16(20,1,true);out.setUint16(22,1,true);out.setUint32(24,sr,true);out.setUint32(28,sr*2,true);out.setUint16(32,2,true);out.setUint16(34,16,true);w(36,"data");out.setUint32(40,pcm.length*2,true);
 for(let i=0;i<pcm.length;i++)out.setInt16(44+i*2,Math.max(-1,Math.min(1,pcm[i]))*0x7fff,true);
 return new Blob([out],{type:"audio/wav"})}
async function sendAudio(blob,name){
 try{sendFile("/api/investigate/audio",await toWav(blob),name+".wav","Transcribing voicemail…")}
 catch(e){resetCase();fail("Could not read that audio file. Try a normal voicemail recording (WAV, MP3 or M4A).")}}
$("audBtn").onclick=()=>$("audIn").click();
$("audIn").onchange=e=>{const f=e.target.files[0];if(f)sendAudio(f,f.name.replace(/\.[^.]+$/,""));e.target.value=""};
let rec=null,chunks=[];
$("recBtn").onclick=async()=>{
 if(rec){rec.stop();return}
 try{const st=await navigator.mediaDevices.getUserMedia({audio:true});chunks=[];rec=new MediaRecorder(st);
  rec.ondataavailable=e=>chunks.push(e.data);
  rec.onstop=()=>{st.getTracks().forEach(t=>t.stop());rec=null;$("recBtn").classList.remove("rec");$("recTxt").textContent="Record";sendAudio(new Blob(chunks),"recording")};
  rec.start();$("recBtn").classList.add("rec");$("recTxt").textContent="Stop and check"}
 catch(e){resetCase();fail("The microphone is not available. Allow microphone access, or upload a recording instead.")}};

/* ---------- drag and drop ---------- */
let dragDepth=0;
addEventListener("dragenter",e=>{if(busy)return;e.preventDefault();dragDepth++;$("drop").classList.add("on")});
addEventListener("dragleave",()=>{dragDepth=Math.max(0,dragDepth-1);if(!dragDepth)$("drop").classList.remove("on")});
addEventListener("dragover",e=>e.preventDefault());
addEventListener("drop",e=>{e.preventDefault();dragDepth=0;$("drop").classList.remove("on");if(busy)return;
 const f=e.dataTransfer?.files?.[0];if(!f)return;
 if(f.type.startsWith("audio/")||/\.(wav|mp3|m4a|ogg|webm)$/i.test(f.name))sendAudio(f,f.name.replace(/\.[^.]+$/,""));
 else sendImage(f)});
sync();
