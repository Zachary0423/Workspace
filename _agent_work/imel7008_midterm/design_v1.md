# IMEL7008 Mid-term — 两级折叠Cascode全差分运放设计 v1

工艺：SMIC 55nm（器件 `n12ll`/`p12ll`，1.2V 器件）；VDD = 1.2V；CL = 100fF（每端对地）。
架构：**PMOS输入折叠Cascode + PMOS共源二级 + Miller(Cc)串联消零电阻(Rz) + 连续时间CMFB控制部分折叠电流源**。
（与课程 slides 示范架构相同，属"Two-Stage 加分项"；方法论走知乎文章的 gm/ID 流程。）

## 0. 指标与设计目标

| 指标 | 及格 | 推荐 | 本设计目标（留裕量） |
|---|---|---|---|
| DC Gain | >40dB | 60dB | ≥64dB |
| GBW | >1GHz | 2GHz | 实测 ≥2.2GHz（理想按 3GHz 设计） |
| PM | >50° | 65° | ~70° |
| Swing | >0.8Vpp,diff | 1Vpp,diff | ≥1.1Vpp,diff |
| SR | >0.5V/ns | 1V/ns | ≥1.5V/ns |
| 外部偏置 | — | 仅1个电流源 | 1×10µA 电流源，VREF 内部产生 |
| 功耗 | 越小越好 | — | 目标 <1mW（参考设计 7.45mW） |

## 1. 从 slides 原理图读出的参考设计真实数据（对照基准）

- 一级：尾 PM6=615µA；输入对 PM3/PM5 各 307µA（gm≈6.49mS，gm/Id≈21）；顶部 PM9/PM10 电流源 436µA；Cascode PM7/PM8、NM4/NM5 436µA；折叠电流源 NM2/NM3=599µA + CMFB 控制部分 NM11=144µA（占 144/743≈**19%**）
- 二级：PM14/NM9 每支 **2.32mA**（gm 27.1mS / 20.1mS）；**Cc=300fF**；Rz=R5/R6；CMFB 检测 R3/R4≈232k
- 偏置：外部 Iref≈10µA（PM22 二极管管）→ 低压 Cascode 镜像产生 Vtail/VGP1/VGP2/VGN1/VGN2；PMOS 尾管 vds 仅 ~114mV（vdsat 108mV，裕度极小——PMOS 输入在 Vicm=0.6V、1.2V 下的必然结果）
- Testbench：开环 = ±0.5 VCVS 差分驱动 + 600mV CM + 两端各 100fF；闭环 = 10K 电阻单位增益反馈 + diffstbprobe（stb 扫 1Hz–100G，mode 选 differential/common）；SR = vpulse 0↔1.2V、tr=10ps、tran 10ns conservative
- ADE 表达式：DC_Gain=`ymax(dB20(mag(VF("/VOUTD"))))`；BW=`bandwidth(VF("/VOUTD") 3 "low")`；GBW=`gainBwProd(VF("/VOUTD"))`；PM=`(180 - (-phaseMargin(VF("/VOUTD"))))`；Power=`IDC("/VDD/MINUS")*1.2`

## 2. 参数推导（按课程指标重算，文章数值不可直接抄）

### 2.1 补偿电容与 Gm1（GBW）
单极点近似下 `GBW = Gm1/(2π·Cc)`。
- 取 **Cc = 30fF**（=0.3CL，slides 经验值；Cc 小 → 同样电流下 GBW 更高、SR 更高）
- 寄生会使实测 GBW 比理想低 25~35%，按理想 3GHz 设计：
  **Gm1 = 2π × 3.0GHz × 30fF ≈ 565µS → 取 560µS**

### 2.2 Gm2 与相位裕度
次极点 `ωp2 ≈ Gm2/C2`，C2 = CL + 输出寄生 ≈ 100f + 20f = 120fF。
- 用 Rz 零点抵消 p2，但 p2 本身仍要 ≥ 2×实测GBW 保底：
  **Gm2 ≥ 2 × 2π × 2.2GHz × 120fF ≈ 3.3mS → 取 3.8mS**
- **Rz = (1/Gm2)·(1 + C2/Cc) ≈ (1/3.8m)×(1+4) ≈ 1.3kΩ**（初值 1.2k，仿真微调；零点压 p2 上）

### 2.3 增益 → R1、R2 要求
`Av = Gm1·R1 · Gm2·R2 ≥ 1600（64dB）`
- R1（一级输出阻抗，Cascode）≈ gm·ro²/3 量级，L=200nm 时估 250~400k
- R2 = ro11‖ro13，二级 L=60nm、250µA 时估 2.5~4k
- 估算 Av ≈ (560µ×300k)×(3.8m×3k) ≈ 168×11.4 ≈ 1900 ≈ **65.6dB** ✓
- ⚠️ 增益是本设计最紧的指标。若仿真不足 60dB：优先把一级 Cascode/电流源 L 加到 300~400nm；其次二级负载 L 加到 100nm

### 2.4 压摆率 → 电流下限
- 一级（差模）：SR1 = I1/(Cc + C1par) ≥ 1.5V/ns → I1 ≥ 1.5e9×45f ≈ **68µA → 取 80µA**
- 二级（每支，最差方向）：SR2 = (I2b − I1/2)/(CL+Cc) ≥ 1.5V/ns → I2b ≥ 235µA → **取 250µA**

### 2.5 电流与 gm/Id 分配（总功耗 0.87mW，参考设计的 1/8.6）

| 器件 | 作用 | Id | gm/Id | L | 备注 |
|---|---|---|---|---|---|
| PM1/2 | 一级输入对 | 40µA | **14** | 200n | → Gm1=560µS |
| PM0 | 一级尾电流 | 80µA | **17** | 200n | Vicm=0.6V 下尾管 Vds 仅~100mV，gm/Id 必须高（Vov≈110mV） |
| PM7/8 | 顶部电流源 | 40µA | 17 | 200n | 与尾管共栅 VB1（见下） |
| PM5/6 | PMOS Cascode | 40µA | 13 | 200n | |
| NM3/4 | NMOS Cascode | 40µA | 13 | 200n | 折叠极点 ≈ gm/(Cpar) ≈ 520µ/15f ≈ 5GHz+，需仿真确认对 PM 影响 |
| NM9/10 | 折叠电流源(固定+受控) | 80µA | 13 | 200n | 拆 A:B = 3:1，B 由 CMFB 控制（先 25%，不稳再降到 ~14%） |
| PM11/12 | 二级输入 | 250µA | **15** | 60n | → Gm2=3.8mS |
| NM13/14 | 二级电流负载 | 250µA | 13 | 60n | 增益不够时 L→100n |

电流汇总：一级 160µA + 二级 500µA + CMFB ~25µA + 偏置 ~40µA ≈ **725µA → P ≈ 0.87mW**

#### 一级尺寸（2026-10-20 按实测特征数据算出，全部 L=200n）

| 器件 | Id | gm/Id | Id/W(µA/µm) | W | fingers |
|---|---|---|---|---|---|
| PM1/PM2 输入对 | 40µA | 14 | ~29 (p12ll) | 1.4µ | 4×0.35µ |
| PM0 尾 | 80µA | 17 | ~18 (p12ll) | 4.4µ | 8×0.55µ |
| PM7/PM8 顶部电流源 | 40µA | 17 | ~18 (p12ll) | 2.2µ | 4×0.55µ |
| PM5/PM6 PMOS Cascode | 40µA | 13 | ~33 (p12ll) | 1.2µ | 4×0.30µ |
| NM3/NM4 NMOS Cascode | 40µA | 13 | ~50 (n12ll) | 0.8µ | 4×0.20µ |
| NM9/NM10 折叠电流源 | 80µA | 13 | ~50 (n12ll) | 1.6µ | 4×0.40µ：3 指接 VBN + 1 指接 Vctrl |

用户原理图实例名映射（2026-10-20）：PM0=尾、PM1/PM2=输入对、PM5/PM6=顶部电流源、PM3/PM4=PMOS Cascode、NM0/NM1=NMOS Cascode、NM2/NM3=折叠电流源。偏置网络：VB1=PM0+PM5/PM6 栅（三管共栅，gm/Id=17）、VB2=PM3/PM4 栅、VB3=NM0/NM1 栅、VB4=NM2/NM3 栅。VIP→PM1 漏交叉接右侧支路 → VIOP=VOUT+、VION=VOUT−。

偏置电压初值：VB1≈0.77V、VB2≈0.45V、VB3≈0.80V、VB4≈0.62V；工作点预算：T≈1.085V、A≈0.95V、B≈0.18V、Voc1≈0.65V；⚠️ PM0 |Vds|≈115mV ≈ vdsat，临界（同参考设计，风险①）

### 2.6 关键点：为什么是 PMOS 输入
Vicm = 0.6V（课程 testbench 用 600mV）。NMOS 输入需 Vicm ≥ Vgs+Vov ≈ 0.7V ✗；PMOS 输入需 Vicm + |Vgs| + Vov_tail ≤ 1.2V → 0.6+0.5+0.11 = 1.21V，勉强可行（参考设计就是这么做的，尾管 gm/Id≈17.6）。
二级输入管 PMOS：Voc1 高（≈0.6~0.65V），正好匹配 PMOS 输入的 CS 级（|Vgs11|≈0.55~0.6V）。

## 3. 偏置电路（仅 1 个外部 10µA 电流源）

照搬 slides 结构：Iref=10µA → PMOS 二极管 → 镜像出 Vtail（尾/顶部电流源栅压）；低压 Cascode 镜像支路产生 VGP1/VGP2（PMOS Cascode 偏置）、VGN1/VGN2（NMOS 电流源/Cascode 偏置）、VBN_2nd（二级 NMOS 负载栅压）。
- 镜像比例 ≤ 10：偏置支路 10µA ×8 = 80µA 一级管；×25 = 250µA 二级管
- **VREF(=0.6V) 内部产生**：两个 100kΩ 电阻从 VDD 分压（6µA），或 5µA 二极管管。首选电阻分压，简单且精确
- 所有偏置管 gm/Id 与对应主管相同，尺寸按电流比例缩 finger

## 4. CMFB（连续时间）

- 检测：Rcm = 2×100kΩ 接两输出（中点 = Vocm），对 R2(~3k) 负载影响 <3%
- 误差放大器：PMOS 输入对 + NMOS 镜像负载，尾电流 20µA；输入管 gm/Id=16（Voc2=0.6V 时 PMOS Vgs≈0.5V，尾管 Vds≈0.1V，跟参考设计同样的裕度问题→尾管 gm/Id 取 17+）
- Vctrl 接到折叠电流源 NM9B/10B（占总折叠电流的 1/4 起步）
- 反馈极性（必须负反馈）：Voc2↑ → Vctrl↓ → NM9B 电流↓ → Voc1↑ → PM11 电流↓ → Voc2↓ ✓
- Ccm ≈ 50fF 并在 Rcm 上（零点抵消 Rcm·Cgg 检测极点，文章 5.3-4 节）
- CMFB 环路：UGF ≈ 差模 GBW 的 ~1/4 ~ 0.5GHz 量级；稳定性靠 ①受控比例小 ②误差放大器 gm 够大（ωp4,CM = gmy/Cgg9B）。stb 仿真验证，PM_CM ≥ 45° 可接受、≥60° 好

## 5. 仿真计划（严格按 slides 流程，评分点①）

1. **DC**：所有管 sat 区、Vds > Vdsat + 50mV（尾管除外，>10mV 即可）；Voc1、Voc2≈0.6±20mV；Vctrl 与 VGN1 差 <100mV
2. **开环 AC**（slides p.15 testbench）：VOUTD 的 dB20/phase → DC_Gain / BW / GBW / PM（表达式见 §1）
3. **闭环 stb**（slides p.18：10K 单位增益反馈，diffstbprobe 串在输出）：mode=differential 测差模环路；mode=common 测共模环路（CMFB 稳定性）
4. **SR**：vpulse 0↔1.2V tr=10ps，tran 10ns conservative，测 VOUTD 上升/下降斜率
5. **Swing**：闭环 DC 扫差分输入，找差模增益掉 3dB 的输出范围（或直接大信号瞬态看跟随范围）
6. **Power**：IDC(VDD) × 1.2，含偏置与 CMFB

## 6. 迭代旋钮（仿真不达标时）

| 症状 | 调法 |
|---|---|
| GBW 不够 | 一级所有管 W ×(目标/实测)，电流不变（gm/Id 法标准迭代） |
| PM 不够 | 调 Rz（±20%）；再不够 ↑W11/12（Gm2）；最后 ↑Cc（会掉 GBW） |
| 增益不够 | 一级 Cascode/电流源 L：200n→300n/400n；二级负载 L→100n |
| SR 不够 | ↑尾电流 I1（同时按比例放大一级 W 保持 gm/Id） |
| 摆幅不够 | 降二级管 gm/Id（Vdsat↓） |
| CMFB 环路不稳 | 受控比例 1/4→1/7；误差放大器电流 ×2 |
| Vocm 偏 | 调 NM9B 与 NM13 的镜像比例（Vctrl≈VGN1 为佳） |

## 7. 风险清单

1. **尾管裕度**（~10mV）：工艺角下可能掉线性区 → 必要时 Vicm 侧说明或输入对 gm/Id 再抬高
2. **折叠极点吃 PM**：NM3/4 的 gm/Cpar 需 ≥3×GBW；不够就降 Cascode 管 gm/Id 到 10 或加电流
3. **增益 60dB 边际**：优先加长 L 解决，不动电流
4. **CMFB 环路 PM**：文章实测第一版只有 42°，靠"控 1/7 + 误差放大器翻倍"救回；我们直接从 1/4 起步、预留继续降的空间
