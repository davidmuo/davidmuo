"""Build animated project cards (assets/work/<id>.webp) from the portfolio's real captures.

usage: python -P tools/cards.py <fonts_dir> <portfolio_work_dir> <build_dir> <out_dir> [id ...]
Chrome draws the static card (type, window chrome); Pillow drops the clip into the window
and crossfades the tail into the head so the loop has no visible cut.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

FONTS, WORK, BUILD, OUT = (os.path.abspath(p) for p in sys.argv[1:5])
ONLY = set(sys.argv[5:])
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CW, CH, R = 800, 664, 30              # card size / corner radius
WX, WY, WW, BAR = 40, 140, 720, 34    # window
VW, VH = 720, 450                     # video area (16:10)
VX, VY = WX, WY + BAR
FPS, SECS, XFADE = 12, 7.0, 7
QUALITY = {"farmlink": 50}           # photographic footage compresses worse

PROJECTS = [
    # id, name, line, url label, bg, ink, clip, start
    ("linguaah", "Linguaah", "Learn a language from the videos you already watch",
     "Linguaah · Reader", "#ffdf00", "#111", "ext.mp4", 14.0),
    ("mepaint", "MePaint", "A painting studio where colour mixes like real pigment",
     "mepaint.vercel.app", "#1e8c63", "#fff", "clip.mp4", 5.0),
    ("syncwidme", "SyncWidMe", "Watch together, perfectly in sync",
     "syncup-jade.vercel.app", "#9b95ff", "#111", "flow.mp4", 17.0),
    ("farmlink", "FarmLink", "A produce marketplace that works on any phone",
     "farmlink-app.netlify.app", "#0e2a1e", "#fff", "clip.mp4", 0.2),
    ("ninjastrike", "Ninja Strike", "A wave-survival arena brawler, built without an engine",
     "Ninja Strike", "#e76f2e", "#111", "clip.mp4", 2.0),
    ("urbanpulse", "Urban Pulse", "7.6 million New York taxi trips, made legible",
     "dazzling-dusk-4b3f37.netlify.app", "#b8e468", "#111", "clip.mp4", 12.5),
]

ARROW = ('<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" '
         'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7M8 7h9v9"/></svg>')


def html(name, line, url, bg, ink):
    f = FONTS.replace("\\", "/")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:IT;src:url('file:///{f}/InterTight-VF.ttf');font-weight:100 900}}
@font-face{{font-family:PM;src:url('file:///{f}/IBMPlexMono-Medium.ttf')}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{CW}px;height:{CH}px;overflow:hidden;background:{bg}}}
body{{color:{ink};font-family:IT;-webkit-font-smoothing:antialiased;position:relative}}
.name{{position:absolute;left:{WX}px;top:34px;font-weight:640;font-size:44px;line-height:1;letter-spacing:-.035em}}
.line{{position:absolute;left:{WX}px;top:88px;font-weight:470;font-size:23.5px;line-height:1.2;letter-spacing:-.012em;opacity:.74}}
.go{{position:absolute;right:{WX}px;top:32px;width:48px;height:48px;border-radius:50%;
     border:1.5px solid color-mix(in srgb,{ink} 28%,transparent);display:grid;place-items:center}}
.win{{position:absolute;left:{WX}px;top:{WY}px;width:{WW}px;height:{BAR + VH}px;border-radius:14px;overflow:hidden;
     background:#d9d7d1;box-shadow:0 0 0 1px rgba(0,0,0,.10),0 30px 60px -22px rgba(0,0,0,.5),0 12px 24px -12px rgba(0,0,0,.25)}}
.bar{{height:{BAR}px;background:#fbfaf8;border-bottom:1px solid #e7e5df;display:flex;align-items:center;padding:0 14px;position:relative}}
.bar i{{width:10px;height:10px;border-radius:50%;background:#d6d3cc;margin-right:7px}}
.url{{position:absolute;left:50%;transform:translateX(-50%);font-family:PM;font-size:12.5px;color:#6d6a64;
      background:#f0eee9;border-radius:7px;padding:4px 14px;letter-spacing:.01em;white-space:nowrap}}
</style></head><body>
<div class="name">{name}</div><div class="line">{line}</div><div class="go">{ARROW}</div>
<div class="win"><div class="bar"><i></i><i></i><i></i><span class="url">{url}</span></div></div>
</body></html>"""


def render_base(pid, *args):
    hp = os.path.join(BUILD, f"{pid}.html")
    pp = os.path.join(BUILD, f"{pid}.png")
    with open(hp, "w", encoding="utf-8") as fh:
        fh.write(html(*args))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={CW},{CH}", "--virtual-time-budget=1500", f"--screenshot={pp}",
                    "file:///" + hp.replace("\\", "/")], check=True, capture_output=True)
    return Image.open(pp).convert("RGBA")


def frames(path, start):
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout.strip()
    w, h = map(int, probe.split(","))
    crop = f"crop={round(h * 1.6)}:{h}," if w / h > 1.61 else ""
    n = int(FPS * SECS) + XFADE
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-frames:v", str(n),
                          "-vf", f"fps={FPS},{crop}scale={VW}:{VH}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    size = VW * VH * 3
    return [Image.frombytes("RGB", (VW, VH), raw[i:i + size]) for i in range(0, len(raw) - size + 1, size)]


def main():
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    card_mask = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(card_mask).rounded_rectangle((0, 0, CW - 1, CH - 1), R, fill=255)
    vid_mask = Image.new("L", (VW, VH), 0)
    d = ImageDraw.Draw(vid_mask)
    d.rounded_rectangle((0, 0, VW - 1, VH - 1), 14, fill=255)
    d.rectangle((0, 0, VW - 1, 20), fill=255)

    for pid, name, line, url, bg, ink, clip, start in PROJECTS:
        if ONLY and pid not in ONLY:
            continue
        base = render_base(pid, name, line, url, bg, ink)
        fr = frames(os.path.join(WORK, pid, clip), start)
        # crossfade the last XFADE frames into the first ones, then start after them
        n = len(fr)
        for k in range(XFADE):
            i = n - XFADE + k
            fr[i] = Image.blend(fr[i], fr[k], (k + 1) / (XFADE + 1))
        fr = fr[XFADE:]
        out = []
        for f in fr:
            c = base.copy()
            c.paste(f, (VX, VY), vid_mask)
            c.putalpha(card_mask)
            out.append(c)
        p = os.path.join(OUT, f"{pid}.webp")
        out[0].save(p, save_all=True, append_images=out[1:], duration=round(1000 / FPS), loop=0,
                    quality=QUALITY.get(pid, 68), alpha_quality=100, method=4 if pid in QUALITY else 6, allow_mixed=pid not in QUALITY)
        out[0].save(os.path.join(BUILD, f"{pid}-still.png"))
        print(f"{pid:12s} {len(out)} frames  {os.path.getsize(p) / 1024:.0f} KB")


main()
