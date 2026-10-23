# 进度存档（2026-10-22 午）—— 全部指标测完 ✓

## 最终成绩单（典型角，含偏置+CMFB 全集成）
| 指标 | 实测 | 要求 | 判定 |
|---|---|---|---|
| DC 增益 | 60.3dB | >40 / 推荐 60 | ✓ |
| GBW | 1.42GHz | >1 / 推荐 2 | ✓ 及格 |
| PM 开环 | 56.8° | >50 / 推荐 65 | ✓ 及格 |
| PM 闭环差模 stb | **83°**（UGF 212MHz，环路增益 42.7dB） | — | ✓✓ |
| SR | 1.26V/ns | >0.5 / 推荐 1 | ✓ 推荐 |
| 摆幅 | **2.23Vpp,diff**（±1.1159V，对称差 1µV） | >0.8 / 推荐 1 | ✓✓ |
| 功耗 | 0.82mW（IDC=682.45µA，10-22 复测） | 越小越好 | ✓ |
| 外部偏置 | 仅 1×10µA | 仅 1 个 | ✓ |

## 测试/图片存档（slides_figs/）
tb_openloop_ac、result_openloop_ac、tb_stb_closed、result_sr、result_swing、result_stb_diff、tb_closedloop、schematic_amp、schematic_bias、schematic_cmfb

## 报告
`Desktop\IMEL7008\midterm_project\mid_term_report.pptx` 共 11 页：标题页 / 放大器结构 / 偏置 / CMFB / 开环tb / 开环结果 / 闭环stb tb / 闭环stb结果 / SR / 摆幅 / 汇总表（功耗按 682.45µA→0.82mW）

## 剩余可选项
- 共模环路 stb（diffstbprobe mode=common，目标 PM≥45°）
- 增益余量：二级四管 L 60n→100n、W 同比（PM7/8 30µ→50µ、NM4/5 6µ→10µ），预计 60.3→65dB
- PM0 尾管线性区挂账（|vds|68m<|vdsat|109m，参考设计同样临界）

---

# 以下为 2026-10-21 存档

## 重大发现：昨日 PDK 特征化数据全错
- p12ll 真实密度：gm/Id=17 → **1.2 µA/µm**（昨日记的 18 错 10 倍+，小数点看串）
- n12ll 真实密度：gm/Id≈12 → **~11.5 µA/µm**（昨日记的 50 错 4 倍）
- 全部尺寸按实测密度重算过

## 定稿参数（全部实测验证）
### 第一级（L=200n）
PM0 尾 70.4µ/16指、PM1/PM2 输入 24µ/8指、PM5/PM6 顶流源 35.2µ/8指、
PM3/PM4 P-Cas 22µ/8指、NM0/NM1 N-Cas 4.4µ/8指、NM2/NM3 折叠 **9µ/8指 → 6指VB4+2指Vctrl（CMFB）**
### 第二级（L=60n）
PM7/PM8 输入 30µ/12指、NM4/NM5 负载 6µ/12指、**Cc=30fF、Rz=2.2k**（PM 从 59°→66°）
### 偏置网络（外部仅 1×10µA；并联支路结构，文章的串联链在 1.2V LL 工艺下电压预算不够用不了）
- VB1：PM9 二极管 6.2µ/2指 → **0.7006V**；镜像管 PM10/11/15 同尺寸
- VB4：NM7 二极管 1.25µ/1指 → **0.584V**
- VB3：NM13 二极管 150n→**200n/L=400n** → **0.782V**（对 VB3 敏感度 ~35mV/mV，高阻节点）
- VB2：PM16 窄管二极管 300n/1指 → **0.434V**
### CMFB（已验证 Vocm≈0.6V ✓）
- 检测 R=100k×2 + Ccm=50f；VREF=100k×2 分压
- 误差放大器：PM17 尾 17.6µ/4指(接VB1)、PM18/19 输入 8.8µ/2指、NM17/18 镜像 1.1µ/1指，全 L=200n
- Vctrl 接法按知乎文章：Vocm 接左管、VREF 接右管、**Vctrl 从左边二极管侧引出**（控制 NMOS 用此极性）

## 实测性能（典型角，开环）
| 指标 | vdc 时代 | 接偏置+CMFB 后 | 要求 |
|---|---|---|---|
| DC 增益 | 65dB | ~62dB | >60 ✓ |
| GBW | 1.71GHz | 1.42GHz | >1 ✓（推荐 2 未到） |
| PM | 66° | 56.8° | >50 ✓ |
- PM 掉 4.5° 是 Ccm=50f 挂在输出端的固有代价（C2: 120f→170f）
- PM0 尾管 |vds|≈68m < |vdsat|≈109m，线性区挂账（参考设计同样临界）

## 明天任务（按顺序）
1. **闭环 stb**（评分点）：10k 单位增益反馈 + diffstbprobe，stb 1Hz–100G
   - mode=differential → PM 目标 ≥65°
   - mode=common → PM ≥45° 可接受；不够就 Ccm↑ 或受控指 2→1
2. **SR**：vpulse 0↔1.2V tr=10ps，tran 10ns，目标 ≥1.5V/ns（slides testbench 已搭好）
3. **摆幅**：闭环 dc 扫差分输入，目标 ≥1Vpp,diff
4. **功耗**：IDC(VDD)×1.2，目标 <1mW
5. 有余力再冲 GBW 2GHz（抬尾电流）

## testbench 备忘
- slides 版开环 testbench 已搭好并会用：VCVS E0/E1=±0.5、V8=600m 共模、vsin 要设 AC magnitude
- 项目截止 10/26
