# -*- coding: utf-8 -*-
"""Stick diagram: one latch's logic (INV + NOR2 with async reset R), finger level.

Schematic parameters (SMIC 55nm, L = 60 nm, unit finger 0.25 um):
  INV  : PMOS 1u/4f,  NMOS 500n/2f
  NOR2 : PMOS 2u/8f per input (series pair, 4x the NMOS finger count),
         NMOS 500n/2f per input (parallel pair)
Routing: VDD/VSS rails + substrate taps in M1; every signal in M2.
Output stays in this work folder only (never into Desktop\\IMEL7002).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WORK = Path(r"C:\Users\zzy\Desktop\WorkSpace\_agent_work\lab2_measurements")
OUT_SVG = WORK / "stick_latch.svg"
OUT_PNG = WORK / "stick_latch.png"

W, H = 790, 400
S = 2.2  # PNG supersample

PD   = (206, 133, 16)
ND   = (46, 139, 87)
POLY = (211, 47, 47)
M1C  = (31, 91, 191)
M2C  = (142, 68, 173)
CONT = (17, 17, 17)
WELL = (184, 134, 11)
INK  = (34, 34, 34)
GRAY = (120, 120, 120)


def hx(c):
    return "#%02x%02x%02x" % c


img = Image.new("RGB", (int(W * S), int(H * S)), "white")
d = ImageDraw.Draw(img)
FONT = r"C:\Windows\Fonts\arial.ttf"
FONB = r"C:\Windows\Fonts\arialbd.ttf"


def font(sz, bold=False):
    return ImageFont.truetype(FONB if bold else FONT, int(sz * S))


svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="Arial">',
    f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>',
]


def rect(x0, y0, x1, y1, color):
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=color)
    svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{hx(color)}"/>')


def hline(x0, x1, y, color, w=4):
    d.line([(x0 * S, y * S), (x1 * S, y * S)], fill=color, width=max(1, int(w * S)))
    svg.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{hx(color)}" stroke-width="{w}"/>')


def vline(x, y0, y1, color, w=4):
    d.line([(x * S, y0 * S), (x * S, y1 * S)], fill=color, width=max(1, int(w * S)))
    svg.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{hx(color)}" stroke-width="{w}"/>')


def dashed_rect(x0, y0, x1, y1, color, w=2):
    svg.append(
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" '
        f'stroke="{hx(color)}" stroke-width="{w}" stroke-dasharray="8,6"/>'
    )
    xx = x0
    while xx < x1:
        hline(xx, min(xx + 8, x1), y0, color, w)
        hline(xx, min(xx + 8, x1), y1, color, w)
        xx += 14
    yy = y0
    while yy < y1:
        vline(x0, yy, min(yy + 8, y1), color, w)
        vline(x1, yy, min(yy + 8, y1), color, w)
        yy += 14


def contact(x, y, s=6):
    rect(x - s / 2, y - s / 2, x + s / 2, y + s / 2, CONT)


def text(x, y, s, sz=11, color=INK, bold=False, anchor="la", halo=False):
    f = font(sz, bold)
    px, py = x * S, y * S
    if halo:
        bbox = d.textbbox((px, py), s, font=f, anchor=anchor)
        pad = 1.5 * S
        d.rectangle([bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad], fill="white")
        svg.append(
            f'<rect x="{bbox[0]/S:.1f}" y="{bbox[1]/S:.1f}" width="{(bbox[2]-bbox[0])/S:.1f}" '
            f'height="{(bbox[3]-bbox[1])/S:.1f}" fill="white"/>'
        )
    d.text((px, py), s, fill=color, font=f, anchor=anchor)
    anch = {"la": "start", "ma": "middle", "ra": "end"}[anchor]
    svg.append(
        f'<text x="{x}" y="{y + sz * 0.9:.1f}" font-size="{sz}" fill="{hx(color)}" '
        f'font-weight="{"bold" if bold else "normal"}" text-anchor="{anch}">{s}</text>'
    )


# ---------------- vertical map ----------------
Y_VDD = 64
Y_TIE = {"X": 78, "XM": 92, "R": 106}       # top gate-tie lanes (M2)
YP0, YP1, YPC = 116, 152, 134               # p-strip
Y_STUB = 174                                # p-only poly stub bottom
Y_LN_XM, Y_LN_QM = 182, 200                 # middle routing lanes (M2)
YN0, YN1, YNC = 212, 248, 230               # n-strip
Y_TIE_B = {"X": 262, "XM": 276, "R": 290}   # bottom gate-tie lanes (M2)
Y_VSS = 316

# ---------------- x map ----------------
INV_P = [150, 176, 202, 228]                # INV poly stripes (P4f)
INV_N = [150, 228]                          # NMOS fingers coincide with 1st/4th stripe
INV_L, INV_R = 137, 241
NOR_P = [330 + i * 24 for i in range(16)]   # 330..690: XM x8 then R x8
NOR_N = [330, 498, 522, 690]                # XM x2 + R x2 at group ends
NOR_L, NOR_R = 317, 703
X_TIE_X, XM_JOIN, R_JOIN = 64, 300, 726

# ================= title / legend =================
text(16, 10, "Latch Logic Stick Diagram — INV + NOR2 (async reset R)", 15, INK, True)
lx, ly = 16, 36
for color, name in [(PD, "p+"), (ND, "n+"), (POLY, "poly"), (M1C, "M1"), (M2C, "M2")]:
    hline(lx, lx + 18, ly, color, 5)
    text(lx + 22, ly - 6, name, 10)
    lx += 22 + 36
contact(lx + 2, ly)
text(lx + 9, ly - 6, "contact", 10)
lx += 66
dashed_rect(lx, ly - 6, lx + 18, ly + 6, WELL)
text(lx + 24, ly - 6, "N-well", 10)

text(189, 46, "INV (N2f/P4f)", 11, INK, True, anchor="ma", halo=True)
text(510, 46, "NOR2 (N2f+2f / P8f+8f)", 11, INK, True, anchor="ma", halo=True)

# ================= rails (M1) =================
hline(30, 745, Y_VDD, M1C, 6)
text(10, Y_VDD - 17, "VDD", 12, M1C, True, halo=True)
hline(30, 745, Y_VSS, M1C, 6)
text(10, Y_VSS + 6, "VSS", 12, M1C, True, halo=True)

# ================= N-well =================
dashed_rect(128, 110, 712, 156, WELL)
text(250, 110, "N-well", 9, WELL, True, halo=True)

# ================= strips =================
rect(INV_L, YP0, INV_R, YP1, PD)
rect(INV_L, YN0, INV_R, YN1, ND)
rect(NOR_L, YP0, NOR_R, YP1, PD)
rect(NOR_L, YN0, NOR_R, YN1, ND)

# ================= poly stripes =================
for x in INV_P:
    full = x in INV_N
    vline(x, Y_TIE["X"], Y_TIE_B["X"] if full else Y_STUB, POLY, 4)
for i, x in enumerate(NOR_P):
    sig = "XM" if i < 8 else "R"
    full = x in NOR_N
    vline(x, Y_TIE[sig], Y_TIE_B[sig] if full else Y_STUB, POLY, 4)

# ================= gate ties (M2) =================
# X: left vertical + top/bottom ties
hline(X_TIE_X, INV_P[-1], Y_TIE["X"], M2C)
hline(X_TIE_X, INV_P[-1], Y_TIE_B["X"], M2C)
vline(X_TIE_X, Y_TIE["X"], Y_TIE_B["X"], M2C)
contact(X_TIE_X, Y_TIE["X"])
contact(X_TIE_X, Y_TIE_B["X"])
for x in INV_P:
    contact(x, Y_TIE["X"])
for x in INV_N:
    contact(x, Y_TIE_B["X"])
text(38, Y_TIE["X"] - 7, "X", 12, M2C, True, halo=True)

# XM: join vertical at group edge + ties over XM stripes
hline(XM_JOIN, NOR_P[7], Y_TIE["XM"], M2C)
hline(XM_JOIN, NOR_P[7], Y_TIE_B["XM"], M2C)
vline(XM_JOIN, Y_TIE["XM"], Y_TIE_B["XM"], M2C)
contact(XM_JOIN, Y_TIE["XM"])
contact(XM_JOIN, Y_TIE_B["XM"])
for x in NOR_P[:8]:
    contact(x, Y_TIE["XM"])
for x in NOR_N[:2]:
    contact(x, Y_TIE_B["XM"])

# R: right vertical + ties over R stripes
hline(NOR_P[8], R_JOIN, Y_TIE["R"], M2C)
hline(NOR_P[8], R_JOIN, Y_TIE_B["R"], M2C)
vline(R_JOIN, Y_TIE["R"], Y_TIE_B["R"], M2C)
contact(R_JOIN, Y_TIE["R"])
contact(R_JOIN, Y_TIE_B["R"])
for x in NOR_P[8:]:
    contact(x, Y_TIE["R"])
for x in NOR_N[2:]:
    contact(x, Y_TIE_B["R"])
text(734, Y_TIE["R"] - 7, "R", 12, M2C, True, halo=True)

# ================= rail taps (M1) =================
# VDD taps: INV sources (3 regions), NOR series-chain VDD entry at R-group far end
for x in (143, 189, 234, 697):
    vline(x, Y_VDD, YP0 - 2, M1C)
    contact(x, Y_VDD)
    contact(x, YPC)
# VSS taps: INV sources, NOR parallel-NMOS sources (left / middle / right)
for x in (143, 234, 323, 510, 697):
    vline(x, YN1 + 2, Y_VSS, M1C)
    contact(x, YNC)
    contact(x, Y_VSS)

# ================= XM node: INV drains -> NOR XM gates (M2) =================
for x in (163, 215):
    vline(x, YPC, Y_LN_XM, M2C)
    contact(x, YPC)
vline(189, YNC, Y_LN_XM, M2C)
contact(189, YNC)
hline(163, XM_JOIN, Y_LN_XM, M2C)
contact(163, Y_LN_XM)
contact(215, Y_LN_XM)
contact(189, Y_LN_XM)
contact(XM_JOIN, Y_LN_XM)
text(246, Y_LN_XM - 15, "XM", 11, M2C, True, halo=True)

# ================= QM node: NOR output (M2) =================
vline(323, YPC, Y_LN_QM, M2C)
contact(323, YPC)
for x in (414, 606):
    vline(x, YNC, Y_LN_QM, M2C)
    contact(x, YNC)
hline(323, 745, Y_LN_QM, M2C)
contact(323, Y_LN_QM)
contact(414, Y_LN_QM)
contact(606, Y_LN_QM)
text(750, Y_LN_QM - 8, "QM", 12, M2C, True, halo=True)

# ================= captions =================
text(16, 338, "Fingers interdigitated, S/D shared. Unit finger W = 0.25 µm, L = 60 nm everywhere — "
              "same sizing as the DFF, no parameter change.", 10, GRAY)
text(16, 354, "NOR2 PMOS = 4× NMOS fingers: series PMOS 2 µm/8f per input (XM near the QM output, R near VDD); "
              "NMOS 0.5 µm/2f per input sharing the output diffusion.", 10, GRAY)
text(16, 370, "Power rails and well/substrate taps in M1; all signal routing in M2.", 10, GRAY)

svg.append("</svg>")
OUT_SVG.write_text("\n".join(svg), encoding="utf-8")
img.save(OUT_PNG)
print("wrote", OUT_SVG)
print("wrote", OUT_PNG)
