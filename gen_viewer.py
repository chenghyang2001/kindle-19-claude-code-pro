"""
gen_viewer.py — 掃描 pptx/png 目錄下所有 PNG，產生 index.html 投影片瀏覽器。

為什麼用 Python 產生靜態 HTML 而非直接用 JS 掃目錄：
  瀏覽器的 File API 無法直接列出本地目錄，必須預先嵌入檔案清單。
"""
import sys
import json
from pathlib import Path


def derive_label(stem: str) -> str:
    """
    從 PNG 檔名 stem 推導人類可讀 label。
    例：第01章_從聊天機器人到開發夥伴-s001 → 第01章 從聊天機器人到開發夥伴 [001]
    """
    # 以 "-s" 切分，右側為序號（如 001）
    parts = stem.rsplit("-s", 1)
    if len(parts) == 2:
        chapter_part = parts[0]     # 第01章_從聊天機器人到開發夥伴
        seq = parts[1]              # 001
        # 底線替換為空格，保留章節結構
        chapter_part = chapter_part.replace("_", " ", 1)
        return f"{chapter_part} [{seq}]"
    # 無法切分時直接回傳原始 stem（底線換空格）
    return stem.replace("_", " ")


def derive_chapter(stem: str) -> str:
    """
    從 PNG 檔名 stem 推導章節名稱（去掉序號部分）。
    例：第01章_從聊天機器人到開發夥伴-s001 → 第01章 從聊天機器人到開發夥伴
    """
    parts = stem.rsplit("-s", 1)
    chapter_raw = parts[0] if len(parts) == 2 else stem
    return chapter_raw.replace("_", " ", 1)


def build_html(template: str, images: list[dict], chapters: list[str], chapter_start: dict[str, int]) -> str:
    """
    將 HTML 模板中的佔位字串替換為實際資料。
    使用 JSON 序列化確保 JS 字串安全跳脫。
    """
    total = len(images)
    total_str = str(total)

    # JS 陣列元素：{"file":"png/xxx.png","label":"..."}
    images_js = ",".join(
        json.dumps({"file": im["file"], "label": im["label"]}, ensure_ascii=False)
        for im in images
    )

    # JS 字串陣列：["第01章 xxx","第02章 yyy",...]
    chapters_js = ",".join(json.dumps(ch, ensure_ascii=False) for ch in chapters)

    # JS 物件鍵值：{"第01章 xxx":0,"第02章 yyy":8,...}
    chapter_map_js = ",".join(
        f"{json.dumps(ch, ensure_ascii=False)}:{idx}"
        for ch, idx in chapter_start.items()
    )

    html = template
    # __TOTAL__ 出現多處（badge + slide-info + updateUI），全部替換
    html = html.replace("__TOTAL__", total_str)
    html = html.replace("__IMAGES_JS__", images_js)
    html = html.replace("__CHAPTERS_JS__", chapters_js)
    html = html.replace("__CHAPTER_MAP_JS__", chapter_map_js)
    return html


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Code Pro — 投影片瀏覽器</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0f172a;color:#e2e8f0;font-family:system-ui,sans-serif;height:100vh;display:flex;flex-direction:column;overflow:hidden}
#header{background:#1e293b;padding:10px 16px;display:flex;align-items:center;gap:12px;flex-shrink:0;border-bottom:1px solid #334155}
#title{font-size:15px;font-weight:600;color:#38bdf8;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#badge{background:#0ea5e9;color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600;white-space:nowrap}
#zoom-badge{background:#1e3a5f;color:#7dd3fc;padding:2px 8px;border-radius:12px;font-size:12px;white-space:nowrap}
#tips{color:#94a3b8;font-size:11px;white-space:nowrap}
#main{display:flex;flex:1;overflow:hidden;min-height:0}
#sidebar{width:200px;background:#1e293b;border-right:1px solid #334155;overflow-y:auto;flex-shrink:0;padding:8px 0}
#sidebar h3{font-size:11px;color:#64748b;padding:8px 12px 4px;text-transform:uppercase;letter-spacing:.05em}
.ch-btn{display:block;width:100%;text-align:left;padding:6px 12px;font-size:11px;color:#94a3b8;background:none;border:none;cursor:pointer;border-left:2px solid transparent;line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ch-btn:hover{background:#1e3a5f;color:#e2e8f0}
.ch-btn.active{background:#1e3a5f;border-left-color:#38bdf8;color:#e0f2fe;font-weight:600}
#viewer-wrap{flex:1;display:flex;flex-direction:column;overflow:hidden;min-width:0}
#viewer{flex:1;overflow:hidden;position:relative;background:#0f172a;cursor:grab;user-select:none}
#viewer.dragging{cursor:grabbing}
#img{position:absolute;transform-origin:0 0;max-width:none;pointer-events:none}
#nav-bar{background:#1e293b;padding:6px 12px;display:flex;align-items:center;gap:8px;border-top:1px solid #334155;flex-shrink:0}
#prev,#next{background:#334155;border:none;color:#e2e8f0;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:14px}
#prev:hover,#next:hover{background:#475569}
#slide-info{flex:1;text-align:center;font-size:12px;color:#94a3b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#fit-btn{background:#1e3a5f;border:1px solid #38bdf8;color:#7dd3fc;padding:3px 10px;border-radius:6px;cursor:pointer;font-size:11px}
.auto-wrap{position:relative}
.auto-group{display:flex}
#auto-btn{background:#1e3a5f;border:1px solid #38bdf8;border-right:none;color:#7dd3fc;padding:3px 10px;border-radius:6px 0 0 6px;cursor:pointer;font-size:11px;white-space:nowrap}
#auto-btn.playing{background:#0ea5e9;color:#fff;border-color:#0ea5e9}
#auto-speed-btn{background:#1e3a5f;border:1px solid #38bdf8;color:#7dd3fc;padding:3px 6px;border-radius:0 6px 6px 0;cursor:pointer;font-size:11px}
#auto-speed-btn.playing{background:#0ea5e9;color:#fff;border-color:#0ea5e9}
#speed-menu{position:absolute;bottom:calc(100% + 4px);right:0;background:#1e293b;border:1px solid #334155;border-radius:6px;overflow:hidden;display:none;z-index:100;min-width:80px}
#speed-menu.open{display:block}
.speed-opt{display:block;padding:6px 16px;font-size:11px;color:#94a3b8;cursor:pointer;white-space:nowrap;background:none;border:none;width:100%;text-align:left}
.speed-opt:hover,.speed-opt.selected{background:#1e3a5f;color:#e0f2fe}
#thumbs{height:90px;background:#0f172a;overflow-x:auto;overflow-y:hidden;display:flex;align-items:center;gap:4px;padding:4px 8px;flex-shrink:0;border-top:1px solid #1e293b;scrollbar-width:thin}
.thumb{height:76px;width:auto;cursor:pointer;border:2px solid transparent;border-radius:3px;opacity:.6;flex-shrink:0;transition:all .15s}
.thumb.active{border-color:#38bdf8;opacity:1}
.thumb:hover{opacity:.85}
</style>
</head>
<body>
<div id="header">
  <div id="title">Claude Code Pro — 投影片瀏覽器</div>
  <span id="badge">__TOTAL__ 張</span>
  <span id="zoom-badge">100%</span>
  <span id="tips">← → 換頁 · 滾輪縮放 · 拖曳平移 · 雙擊還原</span>
</div>
<div id="main">
  <div id="sidebar"><h3>章節</h3><div id="ch-list"></div></div>
  <div id="viewer-wrap">
    <div id="viewer"><img id="img" src="" alt=""></div>
    <div id="nav-bar">
      <button id="prev">◄</button>
      <div id="slide-info">1 / __TOTAL__</div>
      <button id="next">►</button>
      <button id="fit-btn">Fit</button>
      <div class="auto-wrap">
        <div class="auto-group">
          <button id="auto-btn">&#9658; 自動播放</button>
          <button id="auto-speed-btn">&#9660;</button>
        </div>
        <div id="speed-menu">
          <button class="speed-opt selected" data-ms="3000">3 秒</button>
          <button class="speed-opt" data-ms="5000">5 秒</button>
          <button class="speed-opt" data-ms="10000">10 秒</button>
          <button class="speed-opt" data-ms="15000">15 秒</button>
        </div>
      </div>
    </div>
    <div id="thumbs"></div>
  </div>
</div>
<script>
const IMAGES=[__IMAGES_JS__];
const CHAPTERS=[__CHAPTERS_JS__];
const CHAPTER_START={__CHAPTER_MAP_JS__};
let cur=0,scale=1,tx=0,ty=0,dragging=false,startX,startY,startTx,startTy;
const viewer=document.getElementById("viewer");
const img=document.getElementById("img");
const thumbsEl=document.getElementById("thumbs");
const badge=document.getElementById("zoom-badge");
const info=document.getElementById("slide-info");
const chList=document.getElementById("ch-list");
CHAPTERS.forEach((ch,i)=>{
  const btn=document.createElement("button");
  btn.className="ch-btn";btn.textContent=ch;
  btn.onclick=()=>goTo(CHAPTER_START[ch]);
  chList.appendChild(btn);
});
IMAGES.forEach((im,i)=>{
  const t=document.createElement("img");
  t.className="thumb";t.src=im.file;t.title=im.label;
  t.onclick=()=>goTo(i);thumbsEl.appendChild(t);
});
function applyTransform(){
  img.style.transform="matrix("+scale+",0,0,"+scale+","+tx+","+ty+")";
  badge.textContent=Math.round(scale*100)+"%";
}
function loadImage(){
  img.onload=()=>{
    const PAD=24;
    scale=Math.min((viewer.clientWidth-PAD*2)/img.naturalWidth,(viewer.clientHeight-PAD*2)/img.naturalHeight);
    tx=(viewer.clientWidth-img.naturalWidth*scale)/2;
    ty=(viewer.clientHeight-img.naturalHeight*scale)/2;
    applyTransform();
  };
  img.src=IMAGES[cur].file;
}
function updateUI(){
  info.textContent=(cur+1)+" / __TOTAL__ — "+IMAGES[cur].label;
  document.querySelectorAll(".thumb").forEach((t,i)=>t.classList.toggle("active",i===cur));
  const t=thumbsEl.children[cur];if(t)t.scrollIntoView({inline:"center",block:"nearest"});
  document.querySelectorAll(".ch-btn").forEach((btn,i)=>{
    const cs=CHAPTER_START[CHAPTERS[i]];
    const ce=i+1<CHAPTERS.length?CHAPTER_START[CHAPTERS[i+1]]:IMAGES.length;
    btn.classList.toggle("active",cur>=cs&&cur<ce);
  });
}
function goTo(n){if(n<0)n=0;if(n>=IMAGES.length)n=IMAGES.length-1;cur=n;loadImage();updateUI();}
viewer.addEventListener("wheel",e=>{
  e.preventDefault();
  const f=e.deltaY<0?1.13:1/1.13;
  const ns=Math.min(Math.max(scale*f,0.1),25);
  const vr=viewer.getBoundingClientRect();
  const cx=e.clientX-vr.left,cy=e.clientY-vr.top;
  tx=cx-(cx-tx)*(ns/scale);ty=cy-(cy-ty)*(ns/scale);scale=ns;applyTransform();
},{passive:false});
viewer.addEventListener("mousedown",e=>{dragging=true;viewer.classList.add("dragging");startX=e.clientX;startY=e.clientY;startTx=tx;startTy=ty;});
document.addEventListener("mousemove",e=>{if(!dragging)return;tx=startTx+(e.clientX-startX);ty=startTy+(e.clientY-startY);applyTransform();});
document.addEventListener("mouseup",()=>{dragging=false;viewer.classList.remove("dragging");});
viewer.addEventListener("dblclick",()=>loadImage());
document.addEventListener("keydown",e=>{
  if(e.key==="ArrowRight"||e.key==="ArrowDown")goTo(cur+1);
  if(e.key==="ArrowLeft"||e.key==="ArrowUp")goTo(cur-1);
});
document.getElementById("prev").onclick=()=>goTo(cur-1);
document.getElementById("next").onclick=()=>goTo(cur+1);
document.getElementById("fit-btn").onclick=()=>loadImage();
let autoTimer=null,autoMs=3000;
const autoBtn=document.getElementById("auto-btn");
const autoSpeedBtn=document.getElementById("auto-speed-btn");
const speedMenu=document.getElementById("speed-menu");
function stopAutoPlay(){
  if(autoTimer){clearInterval(autoTimer);autoTimer=null;}
  autoBtn.textContent="▶ 自動播放";
  autoBtn.classList.remove("playing");
  autoSpeedBtn.classList.remove("playing");
}
function startAutoPlay(){
  stopAutoPlay();
  autoTimer=setInterval(()=>goTo(cur+1>=IMAGES.length?0:cur+1),autoMs);
  autoBtn.textContent="⏸ 自動播放";
  autoBtn.classList.add("playing");
  autoSpeedBtn.classList.add("playing");
}
autoBtn.onclick=()=>{autoTimer?stopAutoPlay():startAutoPlay();};
autoSpeedBtn.onclick=(e)=>{e.stopPropagation();speedMenu.classList.toggle("open");};
document.addEventListener("click",()=>speedMenu.classList.remove("open"));
document.querySelectorAll(".speed-opt").forEach(btn=>{
  btn.onclick=(e)=>{
    e.stopPropagation();
    autoMs=+btn.dataset.ms;
    document.querySelectorAll(".speed-opt").forEach(b=>b.classList.remove("selected"));
    btn.classList.add("selected");
    speedMenu.classList.remove("open");
    if(autoTimer)startAutoPlay();
  };
});
document.addEventListener("keydown",e=>{if(e.key==="Escape")stopAutoPlay();},true);
goTo(0);
</script>
</body>
</html>"""


def main() -> None:
    try:
        png_dir = Path.home() / "workspace" / "claude-code-pro-resources" / "pptx" / "png"
        if not png_dir.is_dir():
            print(f"錯誤：找不到目錄 {png_dir}", file=sys.stderr)
            sys.exit(1)

        png_files = sorted(png_dir.glob("*.png"))
        if not png_files:
            print(f"錯誤：{png_dir} 底下沒有任何 .png 檔", file=sys.stderr)
            sys.exit(1)

        # 建立 IMAGES 陣列（相對路徑，index.html 與 png/ 同層）
        images: list[dict] = []
        for p in png_files:
            images.append({
                "file": f"png/{p.name}",
                "label": derive_label(p.stem),
            })

        # 建立 CHAPTERS 清單（去重，保留出現順序）
        seen: set[str] = set()
        chapters: list[str] = []
        chapter_start: dict[str, int] = {}
        for idx, p in enumerate(png_files):
            ch = derive_chapter(p.stem)
            if ch not in seen:
                seen.add(ch)
                chapters.append(ch)
                chapter_start[ch] = idx

        # 替換模板佔位字串並寫出 index.html
        html_content = build_html(HTML_TEMPLATE, images, chapters, chapter_start)
        html_path = Path.home() / "workspace" / "claude-code-pro-resources" / "pptx" / "index.html"
        html_path.write_text(html_content, encoding="utf-8")

        size = html_path.stat().st_size
        print(f"完成：{html_path} ({size} bytes)")

    except OSError as e:
        print(f"錯誤：無法讀取或寫入檔案 — {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未預期錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
