# PDK 特征化操作指南（gm/ID 曲线扫描）

目的：拿到 SIMC 55nm 的 `n12f`/`p12f` 器件数据，我来算所有 W/L。
你只需要搭 2 个简单 schematic + 跑 DC 扫描 + 导出 CSV（或截图）。

## 1. 测试电路（NMOS / PMOS 各一个）

- 从 PDK 库放一个 **n12f**（4 端口）：D 接 VDS 电压源，G 接 VGS 电压源，S 和 B 接地
- PMOS（p12f）：S、B 接 VDD(1.2V)，G 接 VGS 源（0→1.2V 扫），D 接 VDS 源
- W 随便固定一个值（如 W=10µm，finger 数按 PDK 默认），**L 设为变量 `L_var`**
- 器件 OP 标注打开：id, gm, gds, vgs, vds, vdsat, vth, cgg（或 cgs/cgd/cgb）

## 2. 仿真设置

- DC 仿真，主扫 **VGS：0 → 1.2V**，步长 5mV
- 参数扫描两层：
  - `L_var` = 60n, 100n, 150n, 200n, 300n, 400n
  - VDS = 0.3V, 0.6V（PMOS 用 −0.3/−0.6 或源端接法的等效值）
- 共 6×2 = 12 条曲线/每种管

## 3. 需要导出的量（每个工作点）

用 Calculator 从 OP 里取（NMOS 为例，注意符号取绝对值）：
1. `gm/Id` = OP("gm")/OP("id")
2. `gmro`（本征增益）= OP("gm")/OP("gds")
3. `Id/W` = OP("id")/W
4. `cgg`（总栅电容，若有）
5. `vdsat`、`vth`（顺手记录）

导出方式任选：
- **首选**：ViVA 里画出曲线后 Graph → Export → CSV，丢到 `_agent_work/imel7008_midterm/pdk_data/`（或微信/邮件发我路径）
- 备选：关键曲线截图（gm/Id~Vgs、gmro~gm/Id、Id/W~gm/Id 各一张，L 全部叠在一起）

## 4. 拿到数据后我做什么

- 由 gm/Id 表查每个管子的 Vgs（→ 偏置电压设计值）
- 由 Id/W 查每个管子的 W
- 由 gmro 核算增益（R1、R2），不够就调 L
- 由 cgg 估算折叠极点/输出寄生，校核 PM
- 输出：完整器件尺寸表（W/L/finger）+ 偏置电路尺寸 + CMFB 尺寸

## 5. 注意事项

- 器件用 **n12f/p12f**（slides 原理图里标注的 1.2V 管），别用错成高压管
- NMOS 衬底接地，PMOS 衬底接源极（课程允许 PMOS 消衬偏）
- 扫描时 W 用单 finger 或固定 finger 数都行，但最后报告 Id/W 时注明条件
