# -*- coding: utf-8 -*-
"""Stick diagram for lab2 DFF: CLK inv | Master | Slave."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"C:\Users\zzy\Desktop\WorkSpace\_agent_work\lab2_measurements\stick_diagram.png")
OUT_LAB = Path(r"C:\Users\zzy\Desktop\IMEL7002\7002_lab2\images\stick_diagram.png")

W, H = 1400, 780
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 18)
    font_s = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 14)
    font_b = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 20)
except OSError:
    font = font_s = font_b = ImageFont.load_default()

# Colors (common stick-diagram convention)
C_NWELL = (255, 250, 205)      # light yellow
C_PDIFF = (210, 140, 70)       # brown / p+
C_NDIFF = (60, 170, 90)        # green / n+
C_POLY = (220, 40, 40)         # red
C_M1 = (40, 90, 220)           # blue
C_CONTACT = (20, 20, 20)
C_ZONE = (230, 230, 235)

MARGIN_L, MARGIN_R = 70, 40
TOP, BOT = 120, 640
VDD_Y, VSS_Y = 150, 610
PDIFF_Y0, PDIFF_Y1 = 200, 300
NDIFF_Y0, NDIFF_Y1 = 450, 550
MID_Y = 375

# Horizontal zones (x ranges)
# CLK inv wider pitch (0.5um fingers) — leftmost alone
x0 = MARGIN_L
zones = [
    ("CLK inverter\n(0.5 µm finger)", x0, x0 + 220),
    ("Master latch\n(0.25 µm finger)", x0 + 240, x0 + 700),
    ("Slave latch\n(0.25 µm finger)", x0 + 720, x0 + 1280),
]


def rect(xy, fill=None, outline=None, width=2):
    d.rectangle(xy, fill=fill, outline=outline, width=width)


def line(xy, fill, width=3):
    d.line(xy, fill=fill, width=width)


def contact(cx, cy, s=8):
    rect([cx - s, cy - s, cx + s, cy + s], fill=C_CONTACT)


def poly_gate(x, y0, y1, label=None):
    line([(x, y0), (x, y1)], C_POLY, 5)
    if label:
        d.text((x - 8, y0 - 22), label, fill=C_POLY, font=font_s)


def diff_strip(x0, x1, y0, y1, color):
    rect([x0, y0, x1, y1], fill=color, outline=(40, 40, 40), width=1)


# Title + legend
d.text((MARGIN_L, 20), "DFF Stick Diagram (planning)", fill=(0, 0, 0), font=font_b)
legend = [
    (C_PDIFF, "p+ diffusion"),
    (C_NDIFF, "n+ diffusion"),
    (C_POLY, "poly"),
    (C_M1, "metal1"),
    (C_NWELL, "N-well"),
]
lx = MARGIN_L
for col, name in legend:
    rect([lx, 55, lx + 22, 75], fill=col, outline=(0, 0, 0), width=1)
    d.text((lx + 28, 55), name, fill=(0, 0, 0), font=font_s)
    lx += 160
d.text((lx, 55), "black square = contact", fill=(0, 0, 0), font=font_s)

# Zone backgrounds
for name, za, zb in zones:
    rect([za, TOP, zb, BOT], fill=C_ZONE, outline=(120, 120, 120), width=2)
    d.text((za + 10, TOP + 8), name, fill=(40, 40, 40), font=font_s)

# N-well spanning PMOS region
rect(
    [MARGIN_L - 10, PDIFF_Y0 - 25, zones[-1][2] + 10, MID_Y - 20],
    fill=C_NWELL,
    outline=(180, 160, 40),
    width=2,
)
d.text((MARGIN_L, PDIFF_Y0 - 48), "N-well", fill=(140, 120, 20), font=font_s)

# VDD / VSS rails
line([(MARGIN_L - 20, VDD_Y), (zones[-1][2] + 20, VDD_Y)], C_M1, 8)
line([(MARGIN_L - 20, VSS_Y), (zones[-1][2] + 20, VSS_Y)], C_M1, 8)
d.text((20, VDD_Y - 12), "VDD", fill=C_M1, font=font_b)
d.text((20, VSS_Y - 12), "VSS", fill=C_M1, font=font_b)

# ---- CLK inverter (left) ----
za, zb = zones[0][1], zones[0][2]
# wider diffusion for 0.5um finger
diff_strip(za + 40, zb - 40, PDIFF_Y0, PDIFF_Y1, C_PDIFF)
diff_strip(za + 40, zb - 40, NDIFF_Y0, NDIFF_Y1, C_NDIFF)
gx = (za + zb) // 2
poly_gate(gx, PDIFF_Y0 - 10, NDIFF_Y1 + 10, "CLK")
# CLKB metal out
line([(gx + 35, MID_Y), (zb + 15, MID_Y)], C_M1, 4)
d.text((gx + 40, MID_Y - 22), "CLKB", fill=C_M1, font=font_s)
# supply taps
contact(za + 55, (PDIFF_Y0 + PDIFF_Y1) // 2)
contact(zb - 55, (PDIFF_Y0 + PDIFF_Y1) // 2)
contact(za + 55, (NDIFF_Y0 + NDIFF_Y1) // 2)
contact(zb - 55, (NDIFF_Y0 + NDIFF_Y1) // 2)
line([(za + 55, PDIFF_Y0), (za + 55, VDD_Y)], C_M1, 3)
line([(za + 55, NDIFF_Y1), (za + 55, VSS_Y)], C_M1, 3)
d.text((za + 50, BOT - 30), "separate column\n(wider devices)", fill=(80, 80, 80), font=font_s)

# ---- Master ----
za, zb = zones[1][1], zones[1][2]
# shared strips
diff_strip(za + 20, zb - 20, PDIFF_Y0, PDIFF_Y1, C_PDIFF)
diff_strip(za + 20, zb - 20, NDIFF_Y0, NDIFF_Y1, C_NDIFF)
# gates: TG_in, INV, NOR stack (2), TG_fb  — schematic style
gates_m = [
    (za + 80, "TG"),
    (za + 180, "INV"),
    (za + 300, "NOR"),
    (za + 380, "NOR"),
    (za + 500, "TG"),
]
for x, lab in gates_m:
    poly_gate(x, PDIFF_Y0 - 5, NDIFF_Y1 + 5)
    d.text((x - 12, NDIFF_Y1 + 12), lab, fill=C_POLY, font=font_s)

# D input
line([(za - 15, NDIFF_Y0 + 30), (za + 80, NDIFF_Y0 + 30)], C_M1, 3)
d.text((za - 35, NDIFF_Y0 + 8), "D", fill=C_M1, font=font_b)
contact(za + 80, NDIFF_Y0 + 30, 6)

# R into NOR region
line([(za + 300, PDIFF_Y0 - 40), (za + 340, PDIFF_Y0 - 40), (za + 340, PDIFF_Y0)], C_M1, 3)
d.text((za + 250, PDIFF_Y0 - 55), "R", fill=C_M1, font=font_b)

# QM out to slave
line([(zb - 30, MID_Y), (zb + 20, MID_Y)], C_M1, 4)
d.text((zb - 50, MID_Y - 22), "QM", fill=C_M1, font=font_s)
contact(zb - 30, MID_Y, 6)

# CLK/CLKB labels on TG
d.text((za + 55, PDIFF_Y0 - 28), "CLK/CLKB", fill=C_POLY, font=font_s)

# supply contacts sample
for x in (za + 40, za + 250, zb - 40):
    contact(x, (PDIFF_Y0 + PDIFF_Y1) // 2, 5)
    contact(x, (NDIFF_Y0 + NDIFF_Y1) // 2, 5)
    line([(x, PDIFF_Y0), (x, VDD_Y)], C_M1, 2)
    line([(x, NDIFF_Y1), (x, VSS_Y)], C_M1, 2)

# ---- Slave ----
za, zb = zones[2][1], zones[2][2]
diff_strip(za + 20, zb - 20, PDIFF_Y0, PDIFF_Y1, C_PDIFF)
diff_strip(za + 20, zb - 20, NDIFF_Y0, NDIFF_Y1, C_NDIFF)
gates_s = [
    (za + 80, "TG"),
    (za + 200, "INV"),
    (za + 320, "NOR"),
    (za + 400, "NOR"),
    (za + 500, "TG"),
]
for x, lab in gates_s:
    poly_gate(x, PDIFF_Y0 - 5, NDIFF_Y1 + 5)
    d.text((x - 12, NDIFF_Y1 + 12), lab, fill=C_POLY, font=font_s)

# stronger output stage note
d.text((za + 160, BOT - 35), "stronger INV/NOR (more fingers)", fill=(80, 80, 80), font=font_s)

# Q / QB
line([(zb - 80, MID_Y), (zb + 30, MID_Y)], C_M1, 4)
d.text((zb - 10, MID_Y - 22), "Q", fill=C_M1, font=font_b)
contact(zb - 80, MID_Y, 6)
line([(za + 200, NDIFF_Y0 - 25), (za + 200, NDIFF_Y0)], C_M1, 3)
d.text((za + 175, NDIFF_Y0 - 48), "QB", fill=C_M1, font=font_b)

# R
line([(za + 320, PDIFF_Y0 - 40), (za + 360, PDIFF_Y0 - 40), (za + 360, PDIFF_Y0)], C_M1, 3)
d.text((za + 300, PDIFF_Y0 - 55), "R", fill=C_M1, font=font_b)

for x in (za + 40, za + 280, zb - 40):
    contact(x, (PDIFF_Y0 + PDIFF_Y1) // 2, 5)
    contact(x, (NDIFF_Y0 + NDIFF_Y1) // 2, 5)
    line([(x, PDIFF_Y0), (x, VDD_Y)], C_M1, 2)
    line([(x, NDIFF_Y1), (x, VSS_Y)], C_M1, 2)

# Bottom note
d.text(
    (MARGIN_L, H - 50),
    "Left → right: CLK inv (alone, 0.5 µm) | Master | Slave.  Shared diffusion within each latch; power rails continuous.",
    fill=(40, 40, 40),
    font=font_s,
)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT_LAB.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT)
img.save(OUT_LAB)
print("wrote", OUT)
print("wrote", OUT_LAB)
