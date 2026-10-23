# -*- coding: utf-8 -*-
"""Stick diagram v3 for lab2 DFF.

Floorplan (user-specified):
  left column : CLK inverter (separate, 0.5 um fingers, taller strips)
  upper block : INV1 + NOR1 (master) | INV2 + NOR2 (slave), shared p/n strips
  lower block : TG1..TG4 on one shared diffusion pair (X/QM/Y shared between TGs)
  middle      : VSS / CLK / CLKB / VDD horizontal lines between the blocks

Discipline: M1 horizontal, M2 vertical (no same-layer crossings).
"""
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont

WORK = Path(r"C:\Users\zzy\Desktop\WorkSpace\_agent_work\lab2_measurements")
OUT_SVG = WORK / "stick_v3.svg"
OUT_PNG = WORK / "stick_v3.png"

W, H = 1080, 634
S = 1.9  # PNG supersample

PD   = (206, 133, 16)
ND   = (46, 139, 87)
POLY = (211, 47, 47)
M1C  = (31, 91, 191)
M2C  = (142, 68, 173)
CONT = (17, 17, 17)
WELL = (184, 134, 11)
INK  = (34, 34, 34)
GRAY = (120, 120, 120)
FEED = (90, 50, 120)


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


def dashed_vline(x, y0, y1, color, w=2, dash=8, gap=6):
    yy = y0
    while yy < y1:
        vline(x, yy, min(yy + dash, y1), color, w)
        yy += dash + gap


def dashed_rect(x0, y0, x1, y1, color, w=2):
    dashed_vline(x0, y0, y1, color, w)
    dashed_vline(x1, y0, y1, color, w)
    xx = x0
    while xx < x1:
        hline(xx, min(xx + 8, x1), y0, color, w)
        hline(xx, min(xx + 8, x1), y1, color, w)
        xx += 14
    svg.append(
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" '
        f'stroke="{hx(color)}" stroke-width="{w}" stroke-dasharray="8,6"/>'
    )


def contact(x, y, s=7):
    rect(x - s / 2, y - s / 2, x + s / 2, y + s / 2, CONT)


def text(x, y, s, sz=12, color=INK, bold=False, anchor="la", halo=False):
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
    anch = {"la": "start", "ma": "middle", "mm": "middle", "ra": "end"}[anchor]
    svg.append(
        f'<text x="{x}" y="{y + sz * 0.9:.1f}" font-size="{sz}" fill="{hx(color)}" '
        f'font-weight="{"bold" if bold else "normal"}" text-anchor="{anch}">{s}</text>'
    )


# ---------------- vertical map ----------------
Y_VDD_T = 80                      # top VDD rail
YG0, YG1 = 92, 112                # top gutter (block labels live here)
YPU0, YPU1 = 118, 158             # upper p-strip
YPC = 138
YGAP_R, YGAP_IO, YGAP_JOG = 168, 184, 198   # upper internal gap lanes
YNU0, YNU1 = 206, 246             # upper n-strip
YNC = 226
Y_STUB = 260                      # bottom-gutter stub lane (X/Y -> INV gates)
Y_GTIP = 252                      # upper gate bottom tips
Y_VSS_M, Y_CLK, Y_CLKB, Y_VDD_M = 300, 318, 334, 350   # middle channel lines
Y_TGTIP = 366                     # TG p-gate top tips
YPL0, YPL1 = 390, 430             # lower p-strip
YPLC = 410
Y_D = 456                         # lower gap D lane
YNL0, YNL1 = 478, 518             # lower n-strip
YNLC = 498
Y_PGTIP_B, Y_NGTIP_T = 438, 448   # TG gate tips in lower gap
Y_VSS_B = 548                     # bottom VSS rail

# ---------------- x map ----------------
# CLK inverter column
CI_L, CI_R = 158, 292
CI_TAP, CI_G, CI_OUT = 178, 230, 268
# upper block gates
INV1_G, INV1_OUT, INV1_TAP = 424, 494, 356
INV1_L, INV1_R = 340, 508
NOR1_G1, NOR1_G2, NOR1_TAP = 584, 626, 546
NOR1_L, NOR1_R = 530, 682
NOR1_NOUT = 601                   # shared n-diffusion output contact
INV2_G, INV2_OUT, INV2_TAP = 752, 786, 708
INV2_L, INV2_R = 692, 800
NOR2_G1, NOR2_G2, NOR2_TAP = 866, 908, 828
NOR2_L, NOR2_R = 812, 964
NOR2_NOUT = 887
NOR1_POUT, NOR2_POUT = 668, 950   # == QM / Q lower tap x (aligned)
# lower TG block
TL, TPR, TNR = 330, 1001, 1035
TG = [dict(pg=432, ng=466), dict(pg=584, ng=618), dict(pg=736, ng=770), dict(pg=888, ng=922)]
X_D, X_X, X_QM, X_Y, X_Q = 380, 520, 668, 824, 950
XDIV = 690                        # master | slave divider

# ================= title / legend =================
text(20, 14, "DFF Stick Diagram — CLK inv (left) · logic row (top) · TG row (bottom)", 17, INK, True)
lx, ly = 20, 46
for color, name in [(PD, "p+"), (ND, "n+"), (POLY, "poly"), (M1C, "M1"), (M2C, "M2")]:
    hline(lx, lx + 22, ly, color, 6)
    text(lx + 26, ly - 7, name, 11)
    lx += 26 + 42
contact(lx + 3, ly, 7)
text(lx + 11, ly - 7, "contact", 11)
lx += 78
dashed_rect(lx, ly - 7, lx + 22, ly + 7, WELL, 2)
text(lx + 28, ly - 7, "N-well", 11)
text(W - 20, 40, "M1 horizontal · M2 vertical", 11, GRAY, anchor="ra")

# ================= rails & middle lines =================
hline(60, 972, Y_VDD_T, M1C, 7)
text(28, Y_VDD_T - 8, "VDD", 13, M1C, True)
hline(60, 1035, Y_VSS_B, M1C, 7)
text(28, Y_VSS_B - 8, "VSS", 13, M1C, True)

hline(92, 956, Y_VSS_M, M1C, 4)
hline(92, 888, Y_CLK, M1C, 4)
hline(268, 922, Y_CLKB, M1C, 4)
hline(92, 998, Y_VDD_M, M1C, 4)
text(64, Y_VSS_M - 8, "VSS", 11, M1C, True, halo=True)
text(64, Y_CLK - 8, "CLK", 11, M1C, True, halo=True)
text(280, Y_CLKB - 8, "CLKB", 11, M1C, True, halo=True)
text(64, Y_VDD_M - 8, "VDD", 11, M1C, True, halo=True)

# ================= N-well boxes =================
dashed_rect(150, 106, 972, 172, WELL, 2)
dashed_rect(322, 384, 1043, 436, WELL, 2)
text(158, 108, "N-well", 10, WELL, True, halo=True)
text(330, 386, "N-well", 10, WELL, True, halo=True)

# ================= upper block strips =================
rect(CI_L, 110, CI_R, 166, PD)        # CLK inv: taller strips (0.5 um fingers)
rect(CI_L, 198, CI_R, 254, ND)
for l, r in [(INV1_L, INV1_R), (NOR1_L, NOR1_R), (INV2_L, INV2_R), (NOR2_L, NOR2_R)]:
    rect(l, YPU0, r, YPU1, PD)
    rect(l, YNU0, r, YNU1, ND)

# ================= lower TG strips =================
rect(TL, YPL0, TPR, YPL1, PD)
rect(TL, YNL0, TNR, YNL1, ND)

# ================= gates (poly) =================
vline(CI_G, 104, 258, POLY, 5)                      # CLK inv gate
for g in (INV1_G, NOR1_G1, NOR1_G2, INV2_G, NOR2_G1, NOR2_G2):
    vline(g, 112, Y_GTIP, POLY, 5)                  # full gates
for t in TG:
    vline(t["pg"], Y_TGTIP, Y_PGTIP_B, POLY, 5)     # TG p-gate
    vline(t["ng"], Y_NGTIP_T, 524, POLY, 5)         # TG n-gate

# ================= rail taps =================
def vdd_tap_up(x, ytop=YPU0, yc=YPC):
    vline(x, Y_VDD_T, ytop - 2, M2C)
    contact(x, Y_VDD_T)
    contact(x, yc)


def vss_tap_mid(x, ybot=YNU1, yc=YNC):
    vline(x, ybot + 2, Y_VSS_M, M2C)
    contact(x, yc)
    contact(x, Y_VSS_M)


for x in (CI_TAP, INV1_TAP, NOR1_TAP, INV2_TAP, NOR2_TAP):
    vdd_tap_up(x, 110 if x == CI_TAP else YPU0)
vdd_tap_up(CI_TAP, 110)
for x in (CI_TAP, INV1_TAP, NOR1_L + 16, NOR1_R - 16, INV2_TAP, NOR2_L + 16, NOR2_R - 16):
    vss_tap_mid(x, 254 if x == CI_TAP else YNU1)

# lower block well/substrate ties
for x in (348, 990):
    vline(x, Y_VDD_M, YPL0 - 2, M2C)
    contact(x, Y_VDD_M)
    contact(x, YPLC)
for x in (348, 1012):
    vline(x, YNL1 + 2, Y_VSS_B, M2C)
    contact(x, YNLC)
    contact(x, Y_VSS_B)

# ================= clock distribution =================
def feed_down(x, yline, ytip):
    vline(x, yline, ytip, M2C)
    contact(x, yline)
    contact(x, ytip)


feed_down(CI_G, Y_CLK, 258)                 # CLK inv gate
feed_down(TG[0]["pg"], Y_CLK, Y_TGTIP)      # TG1 p = CLK
feed_down(TG[3]["pg"], Y_CLK, Y_TGTIP)      # TG4 p = CLK
feed_down(TG[1]["ng"], Y_CLK, Y_NGTIP_T)    # TG2 n = CLK
feed_down(TG[2]["ng"], Y_CLK, Y_NGTIP_T)    # TG3 n = CLK
feed_down(TG[1]["pg"], Y_CLKB, Y_TGTIP)     # TG2 p = CLKB
feed_down(TG[2]["pg"], Y_CLKB, Y_TGTIP)     # TG3 p = CLKB
feed_down(TG[0]["ng"], Y_CLKB, Y_NGTIP_T)   # TG1 n = CLKB
feed_down(TG[3]["ng"], Y_CLKB, Y_NGTIP_T)   # TG4 n = CLKB

# CLKB generation: CLK-inv output -> CLKB line
vline(CI_OUT, YPC, Y_CLKB, M2C)
contact(CI_OUT, YPC)
contact(CI_OUT, YNC)
contact(CI_OUT, Y_CLKB)

# ================= upper block internal wiring =================
# R lane (reset) -> NOR g2 polys
hline(92, NOR2_G2, YGAP_R, M1C)
text(64, YGAP_R - 8, "R", 12, M1C, True, halo=True)
contact(NOR1_G2, YGAP_R)
contact(NOR2_G2, YGAP_R)

# XM lane: INV1 out -> NOR1 g1 poly ; QB lane: INV2 out -> NOR2 g1 poly
hline(INV1_OUT, NOR1_G1, YGAP_IO, M1C)
contact(NOR1_G1, YGAP_IO)
hline(INV2_OUT, NOR2_G1, YGAP_IO, M1C)
contact(NOR2_G1, YGAP_IO)
vline(INV1_OUT, YPC, YNC, M2C)      # INV1 out ties p/n taps
contact(INV1_OUT, YPC)
contact(INV1_OUT, YNC)
contact(INV1_OUT, YGAP_IO)
vline(INV2_OUT, YPC, YNC, M2C)
contact(INV2_OUT, YPC)
contact(INV2_OUT, YNC)
contact(INV2_OUT, YGAP_IO)
text(502, YGAP_IO - 15, "XM", 11, M1C, True, halo=True)
text(794, YGAP_IO - 15, "QB", 11, M1C, True, halo=True)

# QM / Q jogs in the gap: n-side shared tap <-> p-side tap
hline(NOR1_NOUT, NOR1_POUT, YGAP_JOG, M1C)
hline(NOR2_NOUT, NOR2_POUT, YGAP_JOG, M1C)

# ================= node verticals =================
# X : lower TG taps -> INV1 gate (stub at bottom gutter)
vline(X_X, Y_GTIP + 8, YNLC, M2C)
contact(X_X, YPLC)
contact(X_X, YNLC)
contact(X_X, Y_STUB)
hline(INV1_G, X_X, Y_STUB, M1C)
contact(INV1_G, Y_STUB)
vline(INV1_G, Y_GTIP, Y_STUB, M2C)
contact(INV1_G, Y_GTIP)
text(X_X + 8, 440, "X", 12, M1C, True, halo=True)

# Y : lower TG taps -> INV2 gate
vline(X_Y, Y_GTIP + 8, YNLC, M2C)
contact(X_Y, YPLC)
contact(X_Y, YNLC)
contact(X_Y, Y_STUB)
hline(INV2_G, X_Y, Y_STUB, M1C)
contact(INV2_G, Y_STUB)
vline(INV2_G, Y_GTIP, Y_STUB, M2C)
contact(INV2_G, Y_GTIP)
text(X_Y + 8, 440, "Y", 12, M1C, True, halo=True)

# QM : NOR1 out (p & shared n) -> lower TG taps
vline(NOR1_POUT, YPC, YNLC, M2C)
vline(NOR1_NOUT, YGAP_JOG, YNC, M2C)
contact(NOR1_POUT, YPC)
contact(NOR1_NOUT, YNC)
contact(NOR1_NOUT, YGAP_JOG)
contact(NOR1_POUT, YGAP_JOG)
contact(NOR1_POUT, YPLC)
contact(NOR1_POUT, YNLC)
text(NOR1_POUT + 8, 366, "QM", 12, M1C, True, halo=True)

# Q : NOR2 out (p & shared n) -> lower TG taps -> output
vline(NOR2_POUT, YPC, YNLC, M2C)
vline(NOR2_NOUT, YGAP_JOG, YNC, M2C)
contact(NOR2_POUT, YPC)
contact(NOR2_NOUT, YNC)
contact(NOR2_NOUT, YGAP_JOG)
contact(NOR2_POUT, YGAP_JOG)
contact(NOR2_POUT, YPLC)
contact(NOR2_POUT, YNLC)
text(NOR2_POUT + 8, 366, "Q", 13, M1C, True, halo=True)

# D input lane
hline(92, X_D, Y_D, M1C)
text(64, Y_D - 8, "D", 13, M1C, True, halo=True)
vline(X_D, YPLC, YNLC, M2C)
contact(X_D, YPLC)
contact(X_D, YNLC)
contact(X_D, Y_D)

# ================= block labels =================
text(CI_G, YG0, "CLK INV", 11, INK, True, anchor="ma")
text(INV1_G, YG0, "INV1", 11, INK, True, anchor="ma")
text((NOR1_G1 + NOR1_G2) / 2, YG0, "NOR1", 11, INK, True, anchor="ma")
text(INV2_G, YG0, "INV2", 11, INK, True, anchor="ma")
text((NOR2_G1 + NOR2_G2) / 2, YG0, "NOR2", 11, INK, True, anchor="ma")
text(430, 64, "MASTER", 11, GRAY, True, anchor="ma")
text(870, 64, "SLAVE", 11, GRAY, True, anchor="ma")
dashed_vline(XDIV, 88, Y_VSS_B - 6, GRAY, 1.5)

for t, name in zip(TG, ["TG1 fwd", "TG2 fb", "TG3 fwd", "TG4 fb"]):
    text((t["pg"] + t["ng"]) / 2, 566, name, 10, GRAY, anchor="ma")

# ================= sizing notes =================
text(20, 586, "CLK INV: N2f / P4f · 0.5 µm fingers (separate, taller strips)", 10, GRAY)
text(20, 600, "Logic row: INV1 N2f/P4f · NOR1 N2f/P8f · INV2 N4f/P8f · NOR2 N4f/P16f — "
              "NOR: series PMOS share diffusion, parallel NMOS share the output diffusion", 10, GRAY)
text(20, 614, "TG row: forward TG1/TG3 N2f/P4f · feedback TG2/TG4 N1f/P2f — "
              "adjacent TGs share diffusion at X, QM, Y", 10, GRAY)

print("wrote", OUT_SVG)
print("wrote", OUT_PNG)
