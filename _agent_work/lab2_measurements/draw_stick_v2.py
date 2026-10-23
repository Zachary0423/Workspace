# -*- coding: utf-8 -*-
"""Stick diagram v2 for lab2 DFF (TG master-slave, async reset R).

Renders both SVG (vector, for the report) and PNG (raster preview).
Drawing discipline: M1 = horizontal only, M2 = vertical only,
so no same-layer crossings ever occur. 1f = 0.25 um finger, L = 60 nm.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WORK = Path(r"C:\Users\zzy\Desktop\WorkSpace\_agent_work\lab2_measurements")
OUT_SVG = WORK / "stick_v2.svg"
OUT_PNG = WORK / "stick_v2.png"

W, H = 1580, 485
S = 1.75  # PNG supersample

# ---------------- colors ----------------
PD   = (206, 133, 16)    # p+ diffusion (ochre)
ND   = (46, 139, 87)     # n+ diffusion (green)
POLY = (211, 47, 47)     # poly (red)
M1C  = (31, 91, 191)     # metal 1 (blue)
M2C  = (142, 68, 173)    # metal 2 (purple)
CONT = (17, 17, 17)      # contact (black square)
WELL = (184, 134, 11)    # n-well outline (dashed ochre)
INK  = (34, 34, 34)
GRAY = (110, 110, 110)


def cv2hex(c):
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
    svg.append(
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" '
        f'fill="{cv2hex(color)}"/>'
    )


def hline(x0, x1, y, color, w=4):
    d.line([(x0 * S, y * S), (x1 * S, y * S)], fill=color, width=max(1, int(w * S)))
    svg.append(
        f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{cv2hex(color)}" '
        f'stroke-width="{w}"/>'
    )


def vline(x, y0, y1, color, w=4):
    d.line([(x * S, y0 * S), (x * S, y1 * S)], fill=color, width=max(1, int(w * S)))
    svg.append(
        f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{cv2hex(color)}" '
        f'stroke-width="{w}"/>'
    )


def dashed_hline(x0, x1, y, color, w=2, dash=7, gap=5):
    x = x0
    while x < x1:
        hline(x, min(x + dash, x1), y, color, w)
        x += dash + gap


def dashed_rect(x0, y0, x1, y1, color, w=2):
    dashed_hline(x0, x1, y0, color, w)
    dashed_hline(x0, x1, y1, color, w)
    yy = y0
    while yy < y1:
        vline(x0, yy, min(yy + 7, y1), color, w)
        vline(x1, yy, min(yy + 7, y1), color, w)
        yy += 12
    svg.append(
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" '
        f'stroke="{cv2hex(color)}" stroke-width="{w}" stroke-dasharray="7,5"/>'
    )


def contact(x, y, s=7):
    rect(x - s / 2, y - s / 2, x + s / 2, y + s / 2, CONT)


def text(x, y, s, sz=12, color=INK, bold=False, anchor="la", halo=False):
    f = font(sz, bold)
    px, py = x * S, y * S
    if halo:
        # white halo box behind text for legibility over wires
        bbox = d.textbbox((px, py), s, font=f, anchor=anchor)
        pad = 2 * S
        d.rectangle(
            [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad], fill="white"
        )
        svg.append(
            f'<rect x="{bbox[0]/S:.1f}" y="{bbox[1]/S:.1f}" '
            f'width="{(bbox[2]-bbox[0])/S:.1f}" height="{(bbox[3]-bbox[1])/S:.1f}" fill="white"/>'
        )
    d.text((px, py), s, fill=color, font=f, anchor=anchor)
    weight = "bold" if bold else "normal"
    anch = {"la": "start", "lm": "middle", "mm": "middle", "ma": "middle",
            "ra": "end", "rm": "middle"}[anchor]
    # PIL y = ascender top; SVG y = baseline
    svg.append(
        f'<text x="{x}" y="{y + sz * 0.9:.1f}" font-size="{sz}" fill="{cv2hex(color)}" '
        f'font-weight="{weight}" text-anchor="{anch}">{s}</text>'
    )


# ---------------- vertical geometry ----------------
Y_VDD = 76
Y_TK_CB, Y_TK_CLK, Y_TK_R = 92, 104, 116   # top gutter trunks (M1)
YP0, YP1 = 132, 172                        # p-strip
LANE = [190, 206, 222, 238, 254]           # M1 lanes in routing channel
YN0, YN1 = 272, 312                        # n-strip
Y_BK_CB, Y_BK_CLK = 328, 340               # bottom gutter trunks (M1)
Y_VSS = 358
YPC, YNC = 152, 292                        # contact y on p / n strip

# ---------------- sections ----------------
# (name, start_x) -- widths computed per kind
CLKI = dict(kind="inv", x=124,  tap=152,  gate=198, out=234,  end=264, outnet="CLKB",
            cap=["CLK INV", "N2f / P4f · 0.5 µm fingers"])
TG1  = dict(kind="tg",  x=274,  nl=298,   pg=332,   ng=366,   nr=398,  end=422,
            pgs="CLK", ngs="CLKB", cap=["TG1 fwd", "N2f / P4f"])
INV1 = dict(kind="inv", x=432,  tap=460,  gate=498, out=534,  end=564, outnet="XM",
            cap=["INV1", "N2f / P4f"])
NOR1 = dict(kind="nor", x=574,  vdd=602,  g1=642,   g2=688,   end=732,
            cap=["NOR1", "N2f / P8f · reset R"])
TG2  = dict(kind="tg",  x=742,  nl=766,   pg=800,   ng=834,   nr=866,  end=890,
            pgs="CLKB", ngs="CLK", cap=["TG2 fb", "N1f / P2f"])
TG3  = dict(kind="tg",  x=900,  nl=924,   pg=958,   ng=992,   nr=1024, end=1048,
            pgs="CLKB", ngs="CLK", cap=["TG3 fwd", "N2f / P4f"])
INV2 = dict(kind="inv", x=1058, tap=1086, gate=1124, out=1160, end=1190, outnet="QB",
            cap=["INV2", "N4f / P8f"])
NOR2 = dict(kind="nor", x=1200, vdd=1228, g1=1268,  g2=1314,  end=1358,
            cap=["NOR2", "N4f / P16f · reset R"])
TG4  = dict(kind="tg",  x=1368, nl=1392,  pg=1426,  ng=1460,  nr=1492, end=1516,
            pgs="CLK", ngs="CLKB", cap=["TG4 fb", "N1f / P2f"])

SEC = [CLKI, TG1, INV1, NOR1, TG2, TG3, INV2, NOR2, TG4]

# ================= title / legend =================
text(24, 16, "D-Flip-Flop Stick Diagram — TG Master–Slave Register with Asynchronous Reset",
     19, INK, True)
text(24, 40, "SMIC 55 nm · VDD = 0.9 V · L = 60 nm · 1f = 0.25 µm finger (CLK inverter uses 0.5 µm fingers)",
     12, GRAY)

lx = 24
ly = 62
for color, name, w in [(PD, "p+ diff", 26), (ND, "n+ diff", 26), (POLY, "poly", 26),
                       (M1C, "M1", 26), (M2C, "M2", 26)]:
    hline(lx, lx + w, ly, color, 6)
    text(lx + w + 6, ly - 8, name, 12)
    lx += w + 58
contact(lx + 4, ly, 7)
text(lx + 14, ly - 8, "contact", 12)
lx += 96
dashed_rect(lx, ly - 8, lx + 26, ly + 8, WELL, 2)
text(lx + 32, ly - 8, "N-well", 12)
text(W - 24, 40, "M1 horizontal · M2 vertical — no same-layer crossings", 12, GRAY,
     anchor="ra")

# ================= rails & trunks =================
hline(36, 1550, Y_VDD, M1C, 8)
text(20, Y_VDD - 8, "VDD", 14, M1C, True)
hline(36, 1550, Y_VSS, M1C, 8)
text(20, Y_VSS - 8, "VSS", 14, M1C, True)

# top gutter trunks (M1): CLKB / CLK / R
hline(36, 1550, Y_TK_CB, M1C, 4)
hline(52, 1426, Y_TK_CLK, M1C, 4)
hline(36, 1314, Y_TK_R, M1C, 4)
text(20, Y_TK_CB - 10, "CLKB", 11, M1C, True, halo=True)
text(28, Y_TK_CLK - 10, "CLK", 11, M1C, True, halo=True)
text(20, Y_TK_R - 10, "R", 11, M1C, True, halo=True)

# bottom gutter trunks
hline(36, 1550, Y_BK_CB, M1C, 4)
hline(64, 1460, Y_BK_CLK, M1C, 4)
text(20, Y_BK_CB - 10, "CLKB", 11, M1C, True, halo=True)
text(20, Y_BK_CLK - 10, "CLK", 11, M1C, True, halo=True)

# clock trunk links (M2): left CLK, right CLKB
vline(64, Y_TK_CLK, Y_BK_CLK, M2C)
contact(64, Y_TK_CLK)
contact(64, Y_BK_CLK)
vline(1550, Y_TK_CB, Y_BK_CB, M2C)
contact(1550, Y_TK_CB)
contact(1550, Y_BK_CB)

# ================= n-well =================
dashed_rect(112, 124, 1532, 178, WELL, 2)
text(120, 158, "N-well", 11, WELL, True, halo=True)

# ================= strips & gates per section =================
for s in SEC:
    if s["kind"] == "tg":
        rect(s["x"], YP0, s["end"], YP1, PD)
        rect(s["x"], YN0, s["end"], YN1, ND)
        # p-side gate (feed from top trunk)
        vline(s["pg"], 124, 184, POLY, 5)
        # n-side gate (feed from bottom trunk)
        vline(s["ng"], 248, 318, POLY, 5)
    elif s["kind"] == "inv":
        rect(s["x"], YP0, s["end"], YP1, PD)
        rect(s["x"], YN0, s["end"], YN1, ND)
        vline(s["gate"], 124, 320, POLY, 5)
    else:  # nor
        rect(s["x"], YP0, s["end"], YP1, PD)
        rect(s["x"], YN0, s["end"], YN1, ND)
        vline(s["g1"], 124, 320, POLY, 5)
        vline(s["g2"], 124, 320, POLY, 5)

# ================= rails taps =================
def rail_tap(x):
    vline(x, Y_VDD, YP0 - 4, M2C)   # VDD -> p-strip (separate from VSS side!)
    contact(x, Y_VDD)
    contact(x, YPC)
    vline(x, YN1 + 4, Y_VSS, M2C)   # n-strip -> VSS
    contact(x, YNC)
    contact(x, Y_VSS)


for x in (CLKI["tap"], INV1["tap"], INV2["tap"], NOR1["vdd"], NOR2["vdd"]):
    rail_tap(x)
# NOR parallel NMOS: VSS at both outer ends of n-strip
for x in (NOR1["x"] + 16, NOR1["end"] - 16, NOR2["x"] + 16, NOR2["end"] - 16):
    vline(x, YN1 + 4, Y_VSS, M2C)
    contact(x, YNC)
    contact(x, Y_VSS)

# ================= clock & reset gate feeds =================
def top_feed(x, trunk_y, label=None):
    vline(x, trunk_y, 124, M2C)
    contact(x, trunk_y)
    contact(x, 124)
    if label:
        text(x + 4, trunk_y + 4, label, 9, (90, 50, 120), halo=True)


def bot_feed(x, trunk_y, label=None):
    vline(x, 318, trunk_y, M2C)
    contact(x, trunk_y)
    contact(x, 318)
    if label:
        text(x + 4, 343, label, 9, (90, 50, 120))


# CLK inverter gate & TG gates
top_feed(CLKI["gate"], Y_TK_CLK, "CLK")
top_feed(TG1["pg"], Y_TK_CLK, "CLK")
top_feed(TG4["pg"], Y_TK_CLK, "CLK")
top_feed(TG2["pg"], Y_TK_CB, "CLKB")
top_feed(TG3["pg"], Y_TK_CB, "CLKB")
bot_feed(TG1["ng"], Y_BK_CLK, "CLK")
bot_feed(TG2["ng"], Y_BK_CLK, "CLK")
bot_feed(TG3["ng"], Y_BK_CLK, "CLK")
bot_feed(TG4["ng"], Y_BK_CB, "CLKB")
# reset feeds to NOR R-input gates
top_feed(NOR1["g2"], Y_TK_R)
top_feed(NOR2["g2"], Y_TK_R)

# ================= node wiring =================
def node_seg(verts, lane, contacts, label=None, lx=None, ly=None):
    """verts: list of (x, y0, y1) M2 verticals; lane: M1 horizontal spanning min..max x;
    contacts: x positions on the lane getting a contact."""
    for x, y0, y1 in verts:
        vline(x, y0, y1, M2C)
    xa = min(v[0] for v in verts)
    xb = max(v[0] for v in verts)
    hline(xa, xb, lane, M1C, 4)
    for x in contacts:
        contact(x, lane)
    if label:
        text(lx, ly, label, 13, M1C, True, halo=True)


# CLKB output of clock inverter -> CLKB trunks (top & bottom)
vline(CLKI["out"], Y_TK_CB, Y_BK_CB, M2C)
contact(CLKI["out"], Y_TK_CB)
contact(CLKI["out"], YPC)
contact(CLKI["out"], YNC)
contact(CLKI["out"], Y_BK_CB)
text(CLKI["out"] + 6, 200, "CLKB", 12, M2C, True, halo=True)

# D input
vline(TG1["nl"], YPC, YNC, M2C)
contact(TG1["nl"], YPC)
contact(TG1["nl"], YNC)
hline(70, TG1["nl"], LANE[0], M1C)
contact(TG1["nl"], LANE[0])
text(40, LANE[0] - 8, "D", 15, M1C, True)

# X : TG1--TG2 backbone + feed to INV1 gate
node_seg(
    [(TG1["nr"], YPC, YNC), (TG2["nr"], YPC, YNC)],
    LANE[4], [TG1["nr"], TG2["nr"]],
)
hline(TG1["nr"], INV1["gate"], LANE[3], M1C)
contact(TG1["nr"], LANE[3])
vline(INV1["gate"], 124, LANE[3], M2C)
contact(INV1["gate"], LANE[3])
contact(INV1["gate"], 124)
text(560, LANE[4] - 9, "X", 13, M1C, True, halo=True)

# XM : INV1 output -> NOR1 A input
vline(INV1["out"], YPC, YNC, M2C)
contact(INV1["out"], YPC)
contact(INV1["out"], YNC)
hline(INV1["out"], NOR1["g1"], LANE[1], M1C)
contact(INV1["out"], LANE[1])
vline(NOR1["g1"], 124, LANE[1], M2C)
contact(NOR1["g1"], LANE[1])
contact(NOR1["g1"], 124)
text(INV1["out"] + 6, LANE[1] - 9, "XM", 12, M1C, True, halo=True)

# QM : NOR1 output -> TG2 left, TG3 left (long lane)
qmv = [
    (NOR1["g1"] + (NOR1["g2"] - NOR1["g1"]) // 2, LANE[2], YNC),  # shared n-diff tap
    (NOR1["end"] - 16, YPC, LANE[2]),                             # p-out tap
    (TG2["nl"], YPC, YNC),
    (TG3["nl"], YPC, YNC),
]
node_seg(qmv, LANE[2],
         [v[0] for v in qmv] + [NOR1["end"] - 16])
contact(qmv[0][0], YNC)
contact(NOR1["end"] - 16, YPC)
contact(TG2["nl"], YPC)
contact(TG3["nl"], YPC)
contact(TG2["nl"], YNC)
contact(TG3["nl"], YNC)
text(815, LANE[2] - 9, "QM", 13, M1C, True, halo=True)

# Y : TG3--TG4 backbone + feed to INV2 gate
node_seg(
    [(TG3["nr"], YPC, YNC), (TG4["nr"], YPC, YNC)],
    LANE[4], [TG3["nr"], TG4["nr"]],
)
hline(TG3["nr"], INV2["gate"], LANE[0], M1C)
contact(TG3["nr"], LANE[0])
vline(INV2["gate"], 124, LANE[0], M2C)
contact(INV2["gate"], LANE[0])
contact(INV2["gate"], 124)
text(1230, LANE[4] - 9, "Y", 13, M1C, True, halo=True)

# QB : INV2 output -> NOR2 A input
vline(INV2["out"], YPC, YNC, M2C)
contact(INV2["out"], YPC)
contact(INV2["out"], YNC)
hline(INV2["out"], NOR2["g1"], LANE[1], M1C)
contact(INV2["out"], LANE[1])
vline(NOR2["g1"], 124, LANE[1], M2C)
contact(NOR2["g1"], LANE[1])
contact(NOR2["g1"], 124)
text(INV2["out"] + 6, LANE[1] - 9, "QB", 12, M1C, True, halo=True)

# Q : NOR2 output -> TG4 left -> output pin (right edge)
qv = [
    (NOR2["g1"] + (NOR2["g2"] - NOR2["g1"]) // 2, LANE[2], YNC),
    (NOR2["end"] - 16, YPC, LANE[2]),
    (TG4["nl"], YPC, YNC),
]
for x, y0, y1 in qv:
    vline(x, y0, y1, M2C)
xa, xb = qv[0][0], TG4["nl"]
hline(xa, 1520, LANE[2], M1C)
for x in (xa, qv[1][0], qv[2][0]):
    contact(x, LANE[2])
contact(qv[0][0], YNC)
contact(qv[1][0], YPC)
contact(qv[2][0], YPC)
contact(qv[2][0], YNC)
text(1462, LANE[2] - 9, "Q", 14, M1C, True, halo=True)

# ================= gate labels (below n-strip, above bottom trunks) ==========
for x, lab in [(CLKI["gate"], "CLK"), (INV1["gate"], "X"), (NOR1["g1"], "XM"),
               (NOR1["g2"], "R"), (INV2["gate"], "Y"), (NOR2["g1"], "QB"),
               (NOR2["g2"], "R")]:
    text(x - 8, 314, lab, 10, POLY, True)

# ================= section captions & brackets =================
for s in SEC:
    cx = (s["x"] + s["end"]) / 2
    text(cx, 378, s["cap"][0], 12, INK, True, anchor="ma")
    text(cx, 393, s["cap"][1], 10, GRAY, anchor="ma")

hline(274, 890, 414, GRAY, 1.5)
text(582, 420, "MASTER LATCH", 12, GRAY, True, anchor="ma")
hline(900, 1516, 414, GRAY, 1.5)
text(1208, 420, "SLAVE LATCH", 12, GRAY, True, anchor="ma")

text(24, 446,
     "Taps to VDD/VSS are well/substrate ties. Feedback TG gates are phased opposite to forward TGs. "
     "Series PMOS pair in each NOR shares diffusion (no contact between the two fingers).",
     11, GRAY)
text(24, 462,
     "Storage loop: X→INV1→XM→NOR1→QM→TG2→X (master) and Y→INV2→QB→NOR2→Q→TG4→Y (slave) — two inversions each.",
     11, GRAY)

svg.append("</svg>")
OUT_SVG.write_text("\n".join(svg), encoding="utf-8")
img.save(OUT_PNG)

# deliverables stay in this work folder; do NOT copy into Desktop\IMEL7002
print("wrote", OUT_SVG)
print("wrote", OUT_PNG)
