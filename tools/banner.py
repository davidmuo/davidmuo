"""Generate assets/banner-{light,dark}.svg.  usage: python -P tools/banner.py <fonts_dir> <out_dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgtext import Face  # noqa: E402

FONTS, OUT = sys.argv[1], sys.argv[2]
SANS = os.path.join(FONTS, "InterTight-VF.ttf")
MONO = os.path.join(FONTS, "IBMPlexMono-Medium.ttf")

THEMES = {
    "light": dict(bg="#f3f2ee", ink="#121212", grey="#6d6a64", rule="rgba(18,18,18,.12)",
                  pill="#ffffff", mark="#121212", star="#f3f2ee", live="#1f9d55"),
    "dark": dict(bg="#141415", ink="#f2f1ee", grey="#9a978f", rule="rgba(255,255,255,.10)",
                 pill="#1d1d20", mark="#f2f1ee", star="#141415", live="#3ddc84"),
}

W, H, PAD = 1280, 440, 64
WORDS = ["language-learning apps", "browser extensions", "real-time tools", "games", "data products"]
STEP = 2.6                       # seconds each word stays up
CYCLE = STEP * len(WORDS)

name_f = Face(SANS, 620)
lead_f = Face(SANS, 480)
word_f = Face(SANS, 560)
mono_f = Face(MONO)

# --- geometry -------------------------------------------------------------
name_d, _ = name_f.path("David Muo", 150, PAD - 6, 268, tracking=-0.045)

lead_txt = "First sketch to shipped code:"
LEAD_SIZE, BASE = 40, 352
lead_d, lead_w = lead_f.path(lead_txt, LEAD_SIZE, PAD, BASE, tracking=-0.02)
word_x = PAD + lead_w + 13

words = []
for w in WORDS:
    d, ww = word_f.path(w, LEAD_SIZE, word_x, BASE, tracking=-0.02)
    words.append((d, ww))

role_d, _ = mono_f.path("DESIGNER WHO ALSO BUILDS", 17, PAD + 56, 92, tracking=0.08)

pill_txt = "AVAILABLE FOR FREELANCE & REMOTE ROLES"
pill_size = 15
pill_tw = mono_f.width(pill_txt, pill_size, tracking=0.06)
pill_h, pill_padx, dot_gap = 40, 20, 22
pill_w = pill_padx + 8 + dot_gap + pill_tw + pill_padx
pill_x, pill_y = W - PAD - pill_w, 66
dot_cx, dot_cy = pill_x + pill_padx + 4, pill_y + pill_h / 2
pill_d, _ = mono_f.path(pill_txt, pill_size, dot_cx + 4 + dot_gap - 4, pill_y + pill_h / 2 + 5.3, tracking=0.06)

# 4-point star from the portfolio favicon (64-unit box), scaled into a 40px tile
STAR = "M32 9 Q34.6 29.4 55 32 Q34.6 34.6 32 55 Q29.4 34.6 9 32 Q29.4 29.4 32 9Z"
MARK, MX, MY = 40, PAD, 66

# three habits from the portfolio's "How I work": artist, designer, developer
TS, TG, TY = 118, 18, 150
TX = [W - PAD - (3 * TS + 2 * TG) + i * (TS + TG) for i in range(3)]
ag_w = name_f.width("Ag", 54, tracking=-0.03)
ag_d, _ = name_f.path("Ag", 54, TX[1] + (TS - ag_w) / 2, TY + 70, tracking=-0.03)
code_f = Face(MONO)
cd_w = code_f.width("</>", 40)
code_d, _ = code_f.path("</>", 40, TX[2] + (TS - cd_w) / 2, TY + 67)
labels = []
for i, lab in enumerate(["ARTIST", "DESIGNER", "DEVELOPER"]):
    lw = mono_f.width(lab, 11.5, tracking=0.1)
    d, _ = mono_f.path(lab, 11.5, TX[i] + (TS - lw) / 2, TY + TS - 17, tracking=0.1)
    labels.append(d)
A_CX, A_CY, A_R = TX[0] + TS / 2, TY + 50, 22


def tiles(c, t):
    out = []
    for i in range(3):
        out.append(f'<g class="t" style="animation-delay:-{i * 2:.0f}s">'
                   f'<rect x="{TX[i] + .5}" y="{TY + .5}" width="{TS - 1}" height="{TS - 1}" rx="22" fill="{c["pill"]}" stroke="{c["rule"]}"/>')
        if i == 0:
            out.append(f'<clipPath id="mix-{t}"><circle cx="{A_CX - 11}" cy="{A_CY}" r="{A_R}"/></clipPath>'
                       f'<circle cx="{A_CX - 11}" cy="{A_CY}" r="{A_R}" fill="#2563eb"/>'
                       f'<circle cx="{A_CX + 11}" cy="{A_CY}" r="{A_R}" fill="#ffd60a"/>'
                       f'<circle cx="{A_CX + 11}" cy="{A_CY}" r="{A_R}" fill="#3a9a77" clip-path="url(#mix-{t})"/>')
        elif i == 1:
            out.append(f'<path d="{ag_d}" fill="{c["ink"]}"/>')
        else:
            out.append(f'<path d="{code_d}" fill="{c["ink"]}"/>')
        out.append(f'<path d="{labels[i]}" fill="{c["grey"]}"/></g>')
    return "".join(out)


def svg(t):
    c = THEMES[t]
    per = 100 / len(WORDS)
    fade = 2.2  # % of cycle used for the in/out transitions
    keyframes = (f"0%{{opacity:0;transform:translateY(16px)}}"
                 f"{fade:.2f}%{{opacity:1;transform:translateY(0)}}"
                 f"{per - fade:.2f}%{{opacity:1;transform:translateY(0)}}"
                 f"{per:.2f}%{{opacity:0;transform:translateY(-16px)}}"
                 f"100%{{opacity:0;transform:translateY(-16px)}}")
    word_groups = []
    for i, (d, ww) in enumerate(words):
        caret = f'<rect class="caret" x="{word_x + ww + 6:.1f}" y="{BASE - 32}" width="3" height="40" rx="1.5" fill="{c["ink"]}"/>'
        word_groups.append(
            f'<g class="w{" w0" if i == 0 else ""}" style="animation-delay:{i * STEP:.2f}s"><path d="{d}" fill="{c["ink"]}"/>{caret}</g>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="David Muo. Designer who also builds. First sketch to shipped code. Available for freelance and remote roles.">
<style>
.w{{opacity:0;animation:cyc {CYCLE:.1f}s cubic-bezier(.7,0,.2,1) infinite}}
@keyframes cyc{{{keyframes}}}
.caret{{animation:blink 1.05s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.ring{{transform-origin:{dot_cx:.1f}px {dot_cy:.1f}px;animation:ping 2.4s cubic-bezier(0,0,.2,1) infinite}}
@keyframes ping{{0%{{transform:scale(1);opacity:.55}}75%,100%{{transform:scale(2.6);opacity:0}}}}
.star{{transform-origin:{MX + MARK / 2}px {MY + MARK / 2}px;animation:spin 9s cubic-bezier(.7,0,.2,1) infinite}}
@keyframes spin{{0%,30%{{transform:rotate(0)}}50%,80%{{transform:rotate(90deg)}}100%{{transform:rotate(180deg)}}}}
.t{{animation:bob 6s ease-in-out infinite}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
@media (prefers-reduced-motion:reduce){{.w,.caret,.ring,.star,.t{{animation:none}}.w0{{opacity:1}}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="28" fill="{c["bg"]}" stroke="{c["rule"]}"/>
<rect x="{MX}" y="{MY}" width="{MARK}" height="{MARK}" rx="10" fill="{c["mark"]}"/>
<g class="star"><path transform="translate({MX} {MY}) scale({MARK / 64})" d="{STAR}" fill="{c["star"]}"/></g>
<path d="{role_d}" fill="{c["grey"]}"/>
<rect x="{pill_x:.1f}" y="{pill_y}" width="{pill_w:.1f}" height="{pill_h}" rx="{pill_h / 2}" fill="{c["pill"]}" stroke="{c["rule"]}"/>
<circle class="ring" cx="{dot_cx:.1f}" cy="{dot_cy:.1f}" r="4.5" fill="{c["live"]}"/>
<circle cx="{dot_cx:.1f}" cy="{dot_cy:.1f}" r="4.5" fill="{c["live"]}"/>
<path d="{pill_d}" fill="{c["ink"]}"/>
<path d="{name_d}" fill="{c["ink"]}"/>
<path d="{lead_d}" fill="{c["grey"]}"/>
{tiles(c, t)}
{chr(10).join(word_groups)}
</svg>
"""


os.makedirs(OUT, exist_ok=True)
for t in THEMES:
    p = os.path.join(OUT, f"banner-{t}.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg(t))
    print(p, os.path.getsize(p))
print("longest line ends at", round(word_x + max(ww for _, ww in words)), "of", W - PAD)
