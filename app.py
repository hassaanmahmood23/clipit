import subprocess, os, glob, sys, wave, re, hashlib, shutil, json, zipfile
from flask import Flask, request, send_file, render_template_string
import numpy as np

app = Flask(__name__)
os.makedirs("cache", exist_ok=True)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ClipIt - Premium Studio</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box; font-family:'Inter', sans-serif;}
  body{background:#0C0C0E; color:#EDE8DE; margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:24px;}
  .shell{width:100%; max-width:1020px; background:#141416; border:1px solid #24241F; border-radius:28px; overflow:hidden; display:grid; grid-template-columns: 40% 60%; box-shadow:0 30px 80px rgba(0,0,0,0.7); position:relative;}
  .left{background:linear-gradient(160deg, #1A1A1E 0%, #0F0F11 55%, #1C1812 100%); padding:36px 34px; display:flex; flex-direction:column; justify-content:space-between; position:relative;}
  .left:before{content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg, transparent, #C6A664, transparent); opacity:0.6;}
  .eyebrow{font-size:10px; letter-spacing:3px; color:#C6A664; text-transform:uppercase; font-weight:600;}
  .logo{font-family:'Playfair Display', serif; font-size:56px; line-height:0.95; font-weight:400; margin:26px 0 12px; letter-spacing:-1px;}
  .logo i{font-style:italic; color:#C6A664;}
  .logo span{color:#C6A664;}
  .desc{color:#A8A29E; font-size:14px; line-height:1.65; font-weight:300; max-width:300px;}
  .badge{display:inline-flex; align-items:center; gap:6px; background:#1E1D18; border:1px solid #2E2B20; color:#C6A664; padding:6px 10px; border-radius:20px; font-size:11px; letter-spacing:0.5px; margin-top:16px; width:fit-content;}
  .badge-dot{width:6px; height:6px; background:#C6A664; border-radius:50%; box-shadow:0 0 8px #C6A664;}
  .features{margin-top:26px; display:flex; flex-direction:column; gap:13px;}
  .feat{display:flex; gap:12px; align-items:flex-start;}
  .feat-icon{width:32px; height:32px; background:#22221E; border:1px solid #2E2E28; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:14px; flex-shrink:0; color:#C6A664;}
  .feat b{font-size:13px; font-weight:500; display:block;}
  .feat small{color:#7A7A76; font-size:12px; display:block; margin-top:2px; font-weight:300;}
  .left-foot{display:flex; justify-content:space-between; margin-top:28px; padding-top:16px; border-top:1px solid #222; color:#666; font-size:10px; letter-spacing:1.5px; text-transform:uppercase;}
  .right{padding:30px 30px 26px; background:#141416; position:relative;}
  .right-head{display:flex; justify-content:space-between; align-items:center; margin-bottom:18px;}
  .right-head h2{margin:0; font-size:16px; font-weight:600;}
  .right-head p{margin:4px 0 0; color:#888; font-size:12.5px; font-weight:300;}
  .pill{font-size:11px; background:#1C1B17; border:1px solid #2A2820; color:#C6A664; padding:6px 10px; border-radius:20px; white-space:nowrap;}
  label{font-size:11px; color:#9A978F; letter-spacing:1.4px; text-transform:uppercase; display:block; margin:16px 0 9px; font-weight:500;}
  label:first-child{margin-top:0;}
  input[type=text]{width:100%; background:#0C0C0E; border:1px solid #2A2A2E; color:#EDE8DE; padding:14px 15px; border-radius:13px; font-size:14.5px; outline:none;}
  input:focus{border-color:#C6A664;}
  input::placeholder{color:#5A5A56;}
  .row{display:flex; gap:9px;}
  .opt{flex:1; background:#0C0C0E; border:1px solid #2A2A2E; color:#A8A29E; padding:12px 6px; border-radius:11px; text-align:center; cursor:pointer; font-size:13.5px;}
  .opt.active{background:#EDE8DE; color:#111; border-color:#EDE8DE; font-weight:600;}
  .pack-grid{display:grid; grid-template-columns:1fr 1fr; gap:10px;}
  .pack{background:#0C0C0E; border:1px solid #2A2A2E; border-radius:14px; padding:14px 12px; cursor:pointer; position:relative; transition:0.2s; text-align:left;}
  .pack.active{background:#1E1C15; border-color:#C6A664; box-shadow:0 0 0 1px #C6A664, 0 8px 20px rgba(198,166,100,0.15);}
  .pack-num{font-family:'Playfair Display', serif; font-size:26px; line-height:1; color:#EDE8DE;}
  .pack.active .pack-num{color:#C6A664;}
  .pack-name{font-size:12px; font-weight:600; margin-top:6px; color:#EDE8DE;}
  .pack-desc{font-size:11px; color:#777; margin-top:2px; font-weight:300; line-height:1.4;}
  .pack-tag{position:absolute; top:10px; right:10px; font-size:9px; letter-spacing:1px; background:#C6A664; color:#111; padding:4px 6px; border-radius:20px; font-weight:600; text-transform:uppercase;}
  .toggle{display:flex; justify-content:space-between; align-items:center; background:#0C0C0E; border:1px solid #2A2A2E; padding:13px 14px; border-radius:13px; margin-top:12px; cursor:pointer;}
  .toggle.active{border-color:#C6A664; background:#1C1B17;}
  .toggle b{font-size:13.5px; font-weight:500;}
  .toggle small{display:block; color:#777; font-size:12px; margin-top:2px; font-weight:300;}
  .switch{width:44px; height:24px; background:#333; border-radius:20px; position:relative; flex-shrink:0;}
  .switch:after{content:''; position:absolute; width:18px; height:18px; background:#fff; border-radius:50%; top:3px; left:3px; transition:0.2s;}
  .switch.on{background:#C6A664;}
  .switch.on:after{left:23px;}
  button{width:100%; background:#C6A664; color:#111; border:none; padding:16px; border-radius:13px; font-size:14.5px; font-weight:600; margin-top:18px; cursor:pointer;}
  button:hover{background:#D8BE82;}
  .note{text-align:center; color:#5A5A56; font-size:11px; margin-top:12px; line-height:1.5;}
  .loader{position:absolute; inset:0; background:rgba(12,12,14,0.97); backdrop-filter:blur(12px); display:none; flex-direction:column; align-items:center; justify-content:center; padding:36px 24px; text-align:center; z-index:20; border-radius:28px;}
  .loader.show{display:flex;}
  .loader-top{font-size:10px; letter-spacing:4px; color:#C6A664; text-transform:uppercase; font-weight:600; margin-bottom:16px;}
  .loader-logo{font-family:'Playfair Display', serif; font-size:48px; line-height:1; font-weight:400;}
  .loader-logo i{font-style:italic; color:#C6A664;}
  .loader-logo span{color:#C6A664;}
  .gold-line{width:48px; height:1px; background:linear-gradient(90deg, transparent, #C6A664, transparent); margin:16px 0 20px;}
  .ring-wrap{position:relative; width:86px; height:86px; margin-bottom:16px;}
  .ring{width:86px; height:86px; border:1px solid #26261F; border-top:1px solid #C6A664; border-radius:50%; animation:spin 1s linear infinite;}
  .ring-center{position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-family:'Playfair Display', serif; font-size:22px; color:#EDE8DE;}
  @keyframes spin{to{transform:rotate(360deg)}}
  .loader-title{font-size:18px; font-weight:600; margin:4px 0 6px; min-height:24px;}
  .loader-sub{color:#8A8880; font-size:13px; font-weight:300; min-height:20px; margin-bottom:18px; max-width:340px; line-height:1.5;}
  .bar-wrap{width:100%; max-width:360px; height:4px; background:#22221E; border-radius:20px; overflow:hidden;}
  .bar{height:100%; width:0%; background:linear-gradient(90deg, #8A6D3A, #C6A664, #EDE8DE); border-radius:20px; transition:width 0.4s; box-shadow:0 0 12px rgba(198,166,100,0.5);}
  .bar-row{display:flex; justify-content:space-between; width:100%; max-width:360px; margin-top:10px; font-size:11px; letter-spacing:1px;}
  .bar-row span:first-child{color:#777;}
  .bar-row span:last-child{color:#C6A664; font-weight:600;}
  .steps{display:flex; gap:8px; margin-top:20px; flex-wrap:wrap; justify-content:center;}
  .step{font-size:11px; padding:8px 12px; border-radius:20px; border:1px solid #2A2A2E; color:#777; background:#111;}
  .step.done{border-color:#C6A664; color:#C6A664; background:#1C1B17;}
  .step.active{border-color:#EDE8DE; color:#EDE8DE; background:#1A1A1E;}
  .loader-foot{margin-top:22px; color:#555; font-size:11px; letter-spacing:1px; line-height:1.6;}
  .done-box{display:none; margin-top:16px; background:#12261A; border:1px solid #22c55e; padding:12px 16px; border-radius:12px; text-align:center; width:100%; max-width:360px;}
  .done-box b{color:#4ade80; font-size:14px;}
  .done-box small{color:#bbf7d0; font-size:12px;}
  @media(max-width:760px){ body{padding:12px; align-items:flex-start;} .shell{grid-template-columns:1fr; border-radius:20px;} .left{padding:26px 24px;} .logo{font-size:44px;} .right{padding:24px 20px;} .loader{border-radius:20px;} }
</style>
</head>
<body>
<div class="shell">
  <div class="left">
    <div>
      <div class="eyebrow">Premium Clip Studio</div>
      <div class="logo">Clip<i>It</i><span>.</span></div>
      <div class="desc">Paste any YouTube link. Get back the moments everyone will share. No editing. No timeline.</div>
      <div class="badge"><span class="badge-dot"></span> Viral Engine V3 &nbsp;•&nbsp; Video + Live</div>
      <div class="features">
        <div class="feat"><div class="feat-icon">◉</div><div><b>Real Viral Detection</b><small>Reads words + listens to sound</small></div></div>
        <div class="feat"><div class="feat-icon">●</div><div><b>Works for Video & Live</b><small>Auto detects, no setting needed</small></div></div>
        <div class="feat"><div class="feat-icon">✦</div><div><b>Smart Cache</b><small>Same link = instant, no re-download</small></div></div>
        <div class="feat"><div class="feat-icon">↗</div><div><b>Fresh Clips Only</b><small>Never repeats a clip you already got</small></div></div>
      </div>
    </div>
    <div class="left-foot"><span>Est. 2026 — Islamabad</span><span>ClipIt Studio</span></div>
  </div>
  <div class="right">
    <div class="right-head"><div><h2>Create New Clip</h2><p>Paste link, choose pack, done</p></div><div class="pill">● Ready</div></div>
    <form id="cutForm" onsubmit="return handleSubmit(event)">
      <label>YouTube Link</label>
      <input type="text" name="url" placeholder="Paste any YouTube link here..." required>
      <label>Clip Duration</label>
      <div class="row"><div class="opt active" onclick="sel(this,'dur',15)">15 sec</div><div class="opt" onclick="sel(this,'dur',30)">30 sec</div><div class="opt" onclick="sel(this,'dur',60)">60 sec</div></div>
      <label>How Many Clips? — Choose Your Pack</label>
      <div class="pack-grid">
        <div class="pack" onclick="selPack(this,1)"><div class="pack-num">01</div><div class="pack-name">Solo</div><div class="pack-desc">1 best moment</div></div>
        <div class="pack active" onclick="selPack(this,3)"><div class="pack-tag">Popular</div><div class="pack-num">03</div><div class="pack-name">Trio</div><div class="pack-desc">3 top moments</div></div>
        <div class="pack" onclick="selPack(this,5)"><div class="pack-num">05</div><div class="pack-name">Creator Pack</div><div class="pack-desc">5 moments • 5 days</div></div>
        <div class="pack" onclick="selPack(this,10)"><div class="pack-num">10</div><div class="pack-name">Viral Batch</div><div class="pack-desc">10 moments • 10 days</div></div>
      </div>
      <label>Format</label>
      <div class="row"><div class="opt active" onclick="sel(this,'fmt','vertical')">Vertical 9:16</div><div class="opt" onclick="sel(this,'fmt','horizontal')">Horizontal 16:9</div></div>
      <div class="toggle active" id="autoToggle" onclick="toggleAuto()"><div><b>Auto Find Viral Moment <span style="color:#C6A664">• AI</span></b><small>Listens + reads words for viral hooks</small></div><div class="switch on" id="sw"></div></div>
      <div class="toggle active" id="freshToggle" onclick="toggleFresh()"><div><b>Fresh Clips Only <span style="color:#C6A664">• No Repeat</span></b><small>Same link again = next viral moments, not same</small></div><div class="switch on" id="swFresh"></div></div>
      <input type="hidden" name="duration" id="dur" value="15">
      <input type="hidden" name="count" id="count" value="3">
      <input type="hidden" name="format" id="fmt" value="vertical">
      <input type="hidden" name="auto" id="auto" value="1">
      <input type="hidden" name="fresh" id="fresh" value="1">
      <button type="submit" id="submitBtn">Create Viral Clips &nbsp; →</button>
      <div class="note">Works for normal videos + live streams automatically.<br>If you choose 3+ clips, you get a ZIP file.</div>
    </form>
  </div>
  <div class="loader" id="loader">
    <div class="loader-top">ClipIt &nbsp;•&nbsp; Premium Studio</div>
    <div class="loader-logo">Clip<i>It</i><span>.</span></div>
    <div class="gold-line"></div>
    <div class="ring-wrap"><div class="ring" id="ring"></div><div class="ring-center" id="ringPct">0%</div></div>
    <div class="loader-title" id="loadTitle">Checking link...</div>
    <div class="loader-sub" id="loadSub">Detecting if this is a video or a live stream.</div>
    <div class="bar-wrap"><div class="bar" id="bar"></div></div>
    <div class="bar-row"><span id="loadStepText">STEP 1 OF 4 — DOWNLOAD</span><span id="barText">0%</span></div>
    <div class="steps"><div class="step active" id="s1">○ &nbsp; Download</div><div class="step" id="s2">○ &nbsp; Read Words</div><div class="step" id="s3">○ &nbsp; Find Viral</div><div class="step" id="s4">○ &nbsp; Cut</div></div>
    <div class="done-box" id="doneBox"><span style="font-size:22px;">✅</span><br><b>DONE — CLIPS READY!</b><br><small>Your download has started. Check your Downloads folder.</small></div>
    <div class="loader-foot"><b>Finding the moments everyone will share...</b><br>Please do not close this tab. Your clips will download automatically.</div>
  </div>
</div>
<script>
function sel(el, id, val){ el.parentElement.querySelectorAll('.opt').forEach(o=>o.classList.remove('active')); el.classList.add('active'); document.getElementById(id).value = val; }
function selPack(el, val){ document.querySelectorAll('.pack').forEach(o=>o.classList.remove('active')); el.classList.add('active'); document.getElementById('count').value = val; }
let autoOn = true; let freshOn = true;
function toggleAuto(){ autoOn = !autoOn; document.getElementById('sw').classList.toggle('on', autoOn); document.getElementById('auto').value = autoOn ? 1 : 0; document.getElementById('autoToggle').classList.toggle('active', autoOn); }
function toggleFresh(){ freshOn = !freshOn; document.getElementById('swFresh').classList.toggle('on', freshOn); document.getElementById('fresh').value = freshOn ? 1 : 0; document.getElementById('freshToggle').classList.toggle('active', freshOn); }
async function handleSubmit(e){
  e.preventDefault();
  const form = document.getElementById('cutForm');
  const loader = document.getElementById('loader');
  const title = document.getElementById('loadTitle');
  const sub = document.getElementById('loadSub');
  const bar = document.getElementById('bar');
  const barText = document.getElementById('barText');
  const ringPct = document.getElementById('ringPct');
  const stepText = document.getElementById('loadStepText');
  const doneBox = document.getElementById('doneBox');
  const ring = document.getElementById('ring');
  const btn = document.getElementById('submitBtn');
  loader.classList.add('show');
  doneBox.style.display = 'none';
  ring.style.animation = 'spin 1s linear infinite';
  btn.disabled = true;
  let p = 0;
  function setP(val, t, s, step){ p = val; bar.style.width = p + '%'; barText.innerText = Math.floor(p) + '%'; ringPct.innerText = Math.floor(p) + '%'; if(t) title.innerText = t; if(s) sub.innerText = s; if(step) stepText.innerText = step; }
  function markDone(id, label){ const el=document.getElementById(id); el.className='step done'; el.innerHTML='✓ &nbsp; '+label; }
  function markActive(id, label){ const el=document.getElementById(id); el.className='step active'; el.innerHTML='◉ &nbsp; '+label; }
  setP(0, 'Checking link...', 'Detecting video or live stream automatically.', 'STEP 1 OF 4 — DOWNLOAD');
  markActive('s1','Download');
  let fake = setInterval(()=>{
    if(p < 96){
      p += Math.random()*1.5 + 0.5; if(p>96) p=96;
      bar.style.width = p + '%'; barText.innerText = Math.floor(p) + '%'; ringPct.innerText = Math.floor(p) + '%';
      if(p < 30){ title.innerText='Checking link...'; sub.innerText='Detecting video or live stream automatically.'; stepText.innerText='STEP 1 OF 4 — DOWNLOAD'; }
      else if(p < 55){ markDone('s1','Download'); markActive('s2','Read Words'); title.innerText='Reading what is said...'; sub.innerText='Looking for hooks, secrets, questions, stories.'; stepText.innerText='STEP 2 OF 4 — READ WORDS'; }
      else if(p < 85){ markDone('s2','Read Words'); markActive('s3','Find Viral'); title.innerText='Finding viral moments...'; sub.innerText='Combining loudness + viral words. Skipping clips you already have.'; stepText.innerText='STEP 3 OF 4 — FIND VIRAL MOMENTS'; }
      else { markDone('s3','Find Viral'); markActive('s4','Cut'); title.innerText='Cutting your viral clips...'; sub.innerText='Adding cinematic vertical blur. Making your ZIP.'; stepText.innerText='STEP 4 OF 4 — CUT & POLISH'; }
    }
  }, 400);
  try{
    const formData = new FormData(form);
    const res = await fetch('/cut', {method:'POST', body: formData});
    clearInterval(fake);
    if(!res.ok) throw new Error('Server error');
    const blob = await res.blob();
    setP(100, 'Done! Your clips are ready.', 'Your download has started. Check your Downloads folder.', 'DONE — 100% COMPLETE');
    markDone('s1','Download'); markDone('s2','Read Words'); markDone('s3','Find Viral'); markDone('s4','Cut');
    ring.style.animation = 'none';
    doneBox.style.display = 'block';
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const cd = res.headers.get('Content-Disposition') || '';
    const m = cd.match(/filename="?([^";]+)"?/);
    a.download = m ? m[1] : 'ClipIt_clips.zip';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>{ window.URL.revokeObjectURL(url); }, 5000);
    setTimeout(()=>{ loader.classList.remove('show'); btn.disabled=false; }, 2500);
  }catch(err){
    clearInterval(fake);
    title.innerText = 'Something went wrong';
    sub.innerText = 'Please try again with a shorter video or check the link.';
    stepText.innerText = 'ERROR — PLEASE TRY AGAIN';
    btn.disabled = false;
    setTimeout(()=>{ loader.classList.remove('show'); }, 3000);
  }
  return false;
}
</script>
</body>
</html>
"""

VIRAL_WORDS = {
    "secret":10, "nobody knows":10, "shocking":10, "crazy":8, "insane":8, "unbelievable":10,
    "mistake":8, "never":6, "always":5, "why":6, "how":5, "what if":8,
    "i can't believe":10, "you won't believe":10, "listen":6, "truth":8, "lie":7, "exposed":10,
    "money":7, "million":8, "billion":8, "rich":6, "failed":7, "success":6,
    "love":5, "hate":6, "scared":7, "afraid":7, "angry":6, "funny":6,
    "first time":7, "last time":7, "remember":5, "imagine":6, "promise":6,
}

def get_video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/|live/)([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)[:20]
    return hashlib.md5(url.encode()).hexdigest()[:12]

def parse_vtt_time(t):
    try:
        h,m,s = t.split(":")
        s, ms = s.split(".")
        return int(h)*3600 + int(m)*60 + int(s)
    except:
        return 0

def parse_vtt_float(t):
    try:
        parts = t.split(":")
        return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
    except:
        return float(parse_vtt_time(t))

def get_word_scores():
    scores = {}
    for f in glob.glob("*.vtt") + glob.glob("cache/*.vtt"):
        try:
            text = open(f, encoding="utf-8", errors="ignore").read()
            blocks = re.findall(r"(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)\n(.*?)(?:\n\n|\n$)", text, re.DOTALL)
            for start_t, end_t, words in blocks:
                start = parse_vtt_time(start_t)
                clean = re.sub(r"<[^>]+>", " ", words).lower().replace("\n"," ")
                score = 0
                for kw, pts in VIRAL_WORDS.items():
                    if kw in clean:
                        score += pts
                if "?" in clean:
                    score += 5
                if len(clean.split()) > 12:
                    score += 2
                if score > 0:
                    scores[start] = scores.get(start,0) + score
            if scores:
                return scores
        except: pass
    return {}

def load_history(vid, duration):
    path = f"cache/{vid}_history.json"
    if os.path.exists(path):
        try:
            data = json.load(open(path))
            return data.get(str(duration), [])
        except:
            return []
    return []

def save_history(vid, duration, starts):
    path = f"cache/{vid}_history.json"
    data = {}
    if os.path.exists(path):
        try: data = json.load(open(path))
        except: data = {}
    old = data.get(str(duration), [])
    for s in starts:
        if s not in old:
            old.append(s)
    data[str(duration)] = old
    json.dump(data, open(path, "w"))

def is_live_stream(url):
    try:
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--dump-json", "--no-download", url], capture_output=True, text=True, timeout=20)
        if r.stdout:
            info = json.loads(r.stdout.splitlines()[0])
            if info.get("is_live") is True:
                return True
            if info.get("live_status") == "is_live":
                return True
            return False
    except Exception as e:
        print("Live check failed, assume normal video:", e)
    return False

def download_subtitles_safe(url):
    try:
        print("Trying subtitles...")
        subprocess.run([sys.executable, "-m", "yt_dlp", "--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", "en.*", "--sub-format", "vtt", "--convert-subs", "vtt", "--ignore-errors", "-o", "input", url], capture_output=True, text=True, timeout=60)
        print("Subtitle files:", glob.glob("*.vtt"))
    except Exception as e:
        print("Subtitles failed:", e)

def ass_time(t):
    if t < 0: t = 0
    h = int(t//3600); m = int((t%3600)//60); s = int(t%60); cs = int((t - int(t))*100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def get_clip_subtitle_ass(start, duration, is_vertical=True):
    # Build ASS file - style is INSIDE file, no Windows quote problem
    vtts = glob.glob("*.vtt") + glob.glob("cache/*.vtt")
    if not vtts:
        print("NO VTT FOUND")
        return None
    try:
        text = open(vtts[0], encoding="utf-8", errors="ignore").read()
        blocks = re.findall(r"(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)\n(.*?)(?:\n\n|\n$)", text, re.DOTALL)
        events = []
        for s_t, e_t, words in blocks:
            s_f = parse_vtt_float(s_t)
            e_f = parse_vtt_float(e_t)
            if e_f < start or s_f > start + duration:
                continue
            clean = re.sub(r"<[^>]+>", "", words).replace("\n"," ").strip()
            if not clean:
                continue
            words_list = clean.split()
            chunk_size = 3
            num_chunks = (len(words_list) + chunk_size - 1)//chunk_size
            total_time = max(0.6 * num_chunks, e_f - s_f)
            time_per_chunk = max(0.6, total_time / max(1, num_chunks))
            for ci in range(0, len(words_list), chunk_size):
                chunk_text = " ".join(words_list[ci:ci+chunk_size])
                chunk_index = ci // chunk_size
                cs = s_f + chunk_index * time_per_chunk
                ce = cs + time_per_chunk
                ns = max(0, cs - start)
                ne = max(0, ce - start)
                if ne <= 0.1 or ns >= duration:
                    continue
                if ne - ns < 0.5:
                    ne = ns + 0.5
                # Escape ASS special chars
                safe_text = chunk_text.replace("{","").replace("}","")
                events.append(f"Dialogue: 0,{ass_time(ns)},{ass_time(ne)},TikTok,,0,0,0,,{safe_text}")
        print(f"Made {len(events)} ASS subtitle lines for clip at {start}s")
        if not events:
            return None
        # Vertical: MarginV 560 = your green circle. Horizontal: 70
        margin_v = 560 if is_vertical else 70
        fontsize = 50 if is_vertical else 24
        ass_path = f"clip_sub_{start}.ass"
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTok,Arial Black,{fontsize},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,1,2,20,20,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        open(ass_path, "w", encoding="utf-8").write(header + "\n".join(events))
        return ass_path
    except Exception as e:
        print("ASS build failed:", e)
        return None

def find_viral_starts(duration, count, auto, vid, fresh):
    if not auto:
        return [i * (duration + 10) for i in range(count)]
    subprocess.run(["ffmpeg","-y","-i","input.mp4","-vn","-ac","1","-ar","16000","audio.wav"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    per_sec = []
    if os.path.exists("audio.wav"):
        try:
            w = wave.open("audio.wav")
            data = w.readframes(w.getnframes()); w.close()
            samples = np.frombuffer(data, dtype=np.int16).astype(float)
            for i in range(0, len(samples), 16000):
                chunk = samples[i:i+16000]
                if len(chunk)==0: continue
                per_sec.append(np.sqrt(np.mean(chunk**2)))
        except: pass
    if per_sec:
        mx = max(per_sec) if max(per_sec)>0 else 1
        per_sec = [ (x/mx)*10 for x in per_sec]
    word_scores = get_word_scores()
    print(f"Word scores found: {len(word_scores)} seconds with viral words")
    total_len = max(len(per_sec), max(word_scores.keys())+duration if word_scores else len(per_sec))
    scores = []
    for start in range(0, max(1, total_len-duration)):
        loud = sum(per_sec[start:start+duration]) if start < len(per_sec) else 0
        word = sum([word_scores.get(sec,0) for sec in range(start, start+duration)])
        final = (loud*0.3)+(word*1.5) if word_scores else loud
        first_word = sum([word_scores.get(s,0) for s in range(start, start+2)])
        final += first_word*0.5
        scores.append((final, start))
    scores.sort(reverse=True)
    used = load_history(vid, duration) if fresh else []
    print("USED BEFORE:", used)
    picked = []
    for score, s in scores:
        if fresh and any(abs(s-u) < duration+5 for u in used):
            continue
        if all(abs(s-p) >= duration+5 for p in picked):
            picked.append(s)
        if len(picked) >= count:
            break
    if len(picked) < count:
        for score, s in scores:
            if all(abs(s-p) >= duration+5 for p in picked):
                picked.append(s)
            if len(picked) >= count:
                break
    picked.sort()
    while len(picked) < count:
        picked.append(0)
    print("VIRAL STARTS:", picked)
    return picked

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/cut", methods=["POST"])
def cut():
    url = request.form.get("url","").strip()
    duration = int(request.form.get("duration", 15))
    count = int(request.form.get("count", 3))
    fmt = request.form.get("format", "vertical")
    auto = request.form.get("auto","1") == "1"
    fresh = request.form.get("fresh","1") == "1"
    vid = get_video_id(url)
    cached_video = f"cache/{vid}.mp4"
    for f in glob.glob("clip*.mp4"):
        try: os.remove(f)
        except: pass
    for f in glob.glob("input.*"):
        try: os.remove(f)
        except: pass
    for f in glob.glob("*.vtt"):
        try: os.remove(f)
        except: pass
    for f in glob.glob("clip_sub_*.ass"):
        try: os.remove(f)
        except: pass
    for f in glob.glob("clip_sub_*.srt"):
        try: os.remove(f)
        except: pass
    for f in glob.glob("test.*"):
        try: os.remove(f)
        except: pass

    BEST_FMT = "bestvideo[height<=720]+bestaudio/best[height<=720]/best"

    live = is_live_stream(url)
    if live:
        print(f"LIVE DETECTED {vid}")
        subprocess.run([sys.executable, "-m", "yt_dlp", "-f", BEST_FMT, "--merge-output-format", "mp4", "--live-from-start", "-o", "input.mp4", url], check=False)
        if os.path.exists("input.mp4"):
            download_subtitles_safe(url)
    elif os.path.exists(cached_video):
        print(f"CACHE HIT {vid}")
        shutil.copy(cached_video, "input.mp4")
        for cf in glob.glob(f"cache/{vid}*.vtt"):
            shutil.copy(cf, os.path.basename(cf))
    else:
        print(f"CACHE MISS {vid}")
        subprocess.run([sys.executable, "-m", "yt_dlp", "-f", BEST_FMT, "--merge-output-format", "mp4", "-o", "input.mp4", url], check=False)
        if os.path.exists("input.mp4"):
            download_subtitles_safe(url)
            shutil.copy("input.mp4", cached_video)
            for vf in glob.glob("input*.vtt"):
                shutil.copy(vf, f"cache/{vid}.vtt"); break

    if not os.path.exists("input.mp4"):
        return "Download failed. Link is wrong or video is private. <a href='/'>Back</a>", 400
    starts = find_viral_starts(duration, count, auto, vid, fresh)
    if auto and not live:
        save_history(vid, duration, starts)
    made = []
    for i, start in enumerate(starts):
        out = f"clip{i+1}.mp4"
        is_vertical = (fmt == "vertical")
        if is_vertical:
            vf = "split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40[bg];[b]scale=1080:1080:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2"
        else:
            vf = "scale=1280:720"
        # NEW: ASS subtitles - no quotes, works on Windows
        ass_file = get_clip_subtitle_ass(start, duration, is_vertical=is_vertical)
        if ass_file:
            safe_ass = ass_file.replace("\\", "/").replace(":", "\\:")
            vf_final = vf + f",ass={safe_ass}"
            print(f"Burning ASS subtitles {ass_file} into {out}")
        else:
            vf_final = vf
            print(f"No subtitles for clip at {start}s")
        subprocess.run(["ffmpeg","-y","-ss",str(start),"-i","input.mp4","-t",str(duration),"-vf",vf_final,"-c:a","aac",out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(out):
            made.append(out)
    if not made:
        return "Cut failed. <a href='/'>Back</a>", 400
    if len(made) == 1:
        return send_file(made[0], as_attachment=True)
    zip_path = "clips.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for m in made:
            z.write(m)
    return send_file(zip_path, as_attachment=True, download_name=f"ClipIt_{vid}_{count}clips.zip")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)