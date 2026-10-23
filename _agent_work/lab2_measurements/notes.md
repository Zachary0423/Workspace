# IMEL7002 Lab2 — measurement notes

## Tsu-dd(1) boundary (D 0→1)

- Critical sweep point: **T = 962 ps** (`9.62e-10`)
  - Last T where Q still captures on the **first** CLK edge
  - **T = 963 ps** fails (Q rises only on the next CLK) → data-drop
- Waveform file (updated screenshot):
  `C:\Users\zzy\Desktop\IMEL7002\7002_lab2\images\tsu_dd_1_T962ps.png`
- **Must read D and CLK from the same T** (both eye-on at 9.62e-10)
- Markers @ ~450 mV:
  - D rising: **1.01874 ns**
  - CLK rising: **1.05744 ns**
- **Tsu-dd(1) = 1.05744 − 1.01874 = 38.7 ps**

## Measurement convention (Calculator)

- Capture clock = **CLK rising edge #2** (edge #1 ≈ 57 ps is unused early edge)
- Capture Q = **Q rising edge #2** (edge #1 ≈ 42 ps is startup glitch)
- D = rising edge #1
- Expressions:
  - `Tsu = cross(VT("/CLK") 0.45 2 "rising" ...) - cross(VT("/D") 0.45 1 "rising" ...)`
  - `tD  = cross(VT("/Q") 0.45 2 "rising" ...) - cross(VT("/D") 0.45 1 "rising" ...)`

## Tsu-opt(1) / tD(1) / Tclk→Q(1) (D 0→1)

- Plot: `C:\Users\zzy\Desktop\IMEL7002\7002_lab2\images\td_vs_tsu_1_opt.png`
- Sweep roughly T = 930p–962p; minimum on tD–Tsu curve:
  - **Tsu-opt(1) = 50.7421 ps ≈ 50.7 ps**
  - **tD(1) = 203.583 ps ≈ 203.6 ps**
  - **Tclk→Q(1) = tD − Tsu-opt = 203.583 − 50.7421 = 152.8409 ps ≈ 152.8 ps**
- Check point at T=900p: Tsu ≈ 100.5 ps (earlier single-run verify)

## Tsu-dd(0) boundary (D 1→0)

- Critical sweep point: **T = 994 ps** (`9.94e-10`)
- Plot: `C:\Users\zzy\Desktop\IMEL7002\7002_lab2\images\tsu_dd_0_T994ps.png`
- Markers @ ~450 mV:
  - D falling: **5.03397 ns**
  - CLK rising (capture): **5.05834 ns**
- **Tsu-dd(0) = 5.05834 − 5.03397 = 24.37 ps ≈ 24.4 ps**

## Tsu-opt(0) / tD(0) / Tclk→Q(0) (D 1→0)

- Plot: `C:\Users\zzy\Desktop\IMEL7002\7002_lab2\images\td_vs_tsu_0_opt.png`
- Calculator edges: CLK rising **#6**, D falling **#1**, Q falling **#3**
- Minimum on tD–Tsu curve:
  - **Tsu-opt(0) = 51.8313 ps ≈ 51.8 ps**
  - **tD(0) = 209.5926 ps ≈ 209.6 ps**
  - **Tclk→Q(0) = 209.5926 − 51.8313 = 157.7613 ps ≈ 157.8 ps**

## Thold(0) (hold for capturing 0)

- Plot: `C:\Users\zzy\Desktop\IMEL7002\7002_lab2\images\thold_0_W950ps.png`
- Critical sweep point: **W = 950 ps** (`9.5e-10`)
- Capture CLK rising @ **2.05743 ns**
- D rising (leave 0) @ **2.02692 ns**
- **Thold(0) = 2.02692 − 2.05743 = −30.51 ps ≈ −30.5 ps**
- Partial: Tsu-dd(0)+Thold(0) = 24.4 + (−30.5) = **−6.1 ps**
- Tw / tD,max (pre-layout, for later summary table — do not put in report body yet):
  - Tsu-dd(1)+Thold(1) = 38.7 + (−16.2) = **22.5 ps**
  - Tsu-dd(0)+Thold(0) = 24.4 + (−30.5) = **−6.1 ps**
  - **Tw = max(22.5, −6.1) = 22.5 ps**
  - **tD,max = max(tD(1), tD(0)) = max(203.6, 209.6) = 209.6 ps**
  - **fmax:** T=140p still toggles (period 2T=280ps); T=135p fails
  - \(f_{\max}=1/280\,\mathrm{ps}=3.57\,\mathrm{GHz}\)
  - Plots: `images/fmax_T140p_a.png` (pass), `images/fmax_T135p.png` (fail)
  - CLK direct vpulse (no driver buffer) for fmax only
- **P10 = 6.48 μW** (written in report §6)
  - With DFF: P(VDD)=3.761 μW, P(VDD_DRV)=15.942 μW
  - Baseline (DFF removed, driver outputs open): P(VDD_DRV,baseline)=13.222 μW
  - FOM1 preview: (209.6+22.5)^2×6.48 ≈ 3.49×10^5
- Clock-only D=0:
  - Normal (with DFF): P(VDD)=2.165 μW, P(VDD_DRV)=15.132 μW
  - Baseline (outputs open): P(VDD_DRV,baseline)=12.599 μW
  - **P_clk(D=0)=2.165+15.132-12.599=4.70 μW**
- Clock-only D=1 (assumed order: normal then baseline):
  - Normal: P(VDD)=2.371 μW, P(VDD_DRV)=15.170 μW
  - Baseline: P(VDD_DRV,baseline)=12.599 μW
  - **P_clk(D=1)=2.371+15.170-12.599=4.94 μW**
- **P_clock-only = (4.70+4.94)/2 = 4.82 μW** (written in report §7)
- Still need: summary table later (Tw, tD,max, FOM1, etc.)

## Thold(1) (hold for capturing 1)

- Plot: `C:\Users\zzy\Desktop\IMEL7002\7002_lab2\images\thold_1_W962ps.png`
- Critical sweep point: **W = 962 ps** (`9.62e-10`) — last successful capture (Q still rises)
- Capture CLK = rising @ **2.05835 ns** (450 mV)
- D falling @ **2.0422 ns** (450 mV) for this W
- **Thold(1) = 2.0422 − 2.05835 = −16.15 ps ≈ −16.2 ps** (negative hold: D may fall slightly before CLK)
- Partial window: Tsu-dd(1)+Thold(1) = 38.7 + (−16.2) = **22.5 ps**
  (full Tw still needs Tsu-dd(0) and Thold(0))

## Sizing (locked by user)

- Unit finger W = 0.25 µm, L = 60 nm
- Feedback TG: N 1f / P 2f
- Forward path: N 2f / P 4f
- NOR series PMOS: ~4× NMOS (N 2f → P 8f)
- CLK inverter: N 2f / P 4f
- Output inverter (Q): N 4f / P 8f

## Stick diagram v2 (2026-10-16)

- Generator: `draw_stick_v2.py` (dual output: SVG vector + 1.75x PNG, same primitive list)
- Outputs stay in this folder only: `stick_v2.svg/.png`（v3 同；用户要求一律不写进 IMEL7002）
- Topology confirmed from schematic zoom: TG1(D→X), INV1(X→XM), NOR1(XM,R)→QM, TG2(QM→X) |
  TG3(QM→Y), INV2(Y→QB), NOR2(QB,R)→Q, TG4(Q→Y); CLK inv separate (0.5 µm fingers)
- Drawing discipline: M1 horizontal only, M2 vertical only → zero same-layer crossings;
  CLK/CLKB/R on gutter trunks with M2 links at both ends; NOR = series PMOS + parallel NMOS
  sharing the output diffusion; feedback TG gates phased opposite to forward TGs
- v1 (`draw_stick.py`, `stick_diagram.png`) kept for reference only — superseded
