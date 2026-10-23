# -*- coding: utf-8 -*-
"""Rebuild lab2 Chinese PDF with figures from the English original.

Work files stay under WorkSpace; only the output PDF is written to lab2
when the user asks to update it.
"""
from pathlib import Path

import pymupdf
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

LAB2 = Path(r"C:\Users\zzy\Desktop\IMEL7002\7002_lab2")
SRC = LAB2 / "lab2_2026.pdf"
OUT_PDF = LAB2 / "lab2_2026_中文版.pdf"
WORK = Path(__file__).resolve().parent
IMG = WORK / "img_extract"
IMG.mkdir(parents=True, exist_ok=True)

FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
pdfmetrics.registerFont(TTFont("MSYH", FONT_PATH, subfontIndex=0))
pdfmetrics.registerFont(TTFont("MSYH-Bold", FONT_PATH, subfontIndex=1))


def extract_images():
    src = pymupdf.open(SRC)
    mat = pymupdf.Matrix(2.5, 2.5)

    # Fig1: symbol view only (no caption)
    clip1 = pymupdf.Rect(95, 195, 510, 370)
    pix = src[0].get_pixmap(matrix=mat, clip=clip1)
    pix.save(str(IMG / "fig1.png"))

    # Fig2: schematic + timing; include feedback wires, exclude English caption (y≈595)
    clip2 = pymupdf.Rect(100, 215, 515, 590)
    pix = src[1].get_pixmap(matrix=mat, clip=clip2)
    pix.save(str(IMG / "fig2.png"))

    def save_xref(xref, name):
        pix = pymupdf.Pixmap(src, xref)
        if pix.n - pix.alpha > 3:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        path = IMG / name
        pix.save(str(path))
        return path

    save_xref(31, "sim_tsu_dd_1.png")
    save_xref(35, "plot_td_tsu_1.png")
    save_xref(37, "sim_tsu_dd_0.png")

    p_a = save_xref(41, "_xref41.png")
    p_b = save_xref(42, "_xref42.png")
    a = Image.open(p_a)
    b = Image.open(p_b)
    if a.size[0] * a.size[1] < b.size[0] * b.size[1]:
        a.save(IMG / "plot_td_tsu_0.png")
        b.save(IMG / "sim_hold.png")
    else:
        b.save(IMG / "plot_td_tsu_0.png")
        a.save(IMG / "sim_hold.png")
    p_a.unlink(missing_ok=True)
    p_b.unlink(missing_ok=True)
    src.close()


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CNTitle",
            fontName="MSYH-Bold",
            fontSize=16,
            leading=22,
            spaceAfter=6,
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNSubtitle",
            fontName="MSYH",
            fontSize=12,
            leading=18,
            spaceAfter=10,
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNH1",
            fontName="MSYH-Bold",
            fontSize=12,
            leading=18,
            spaceBefore=12,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNBody",
            fontName="MSYH",
            fontSize=10,
            leading=15,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNCaption",
            fontName="MSYH",
            fontSize=9,
            leading=13,
            spaceBefore=4,
            spaceAfter=10,
            alignment=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNCell",
            fontName="MSYH",
            fontSize=8.5,
            leading=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNCellBold",
            fontName="MSYH-Bold",
            fontSize=8.5,
            leading=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CNNote",
            fontName="MSYH",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#444444"),
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    return styles


def P(text, style):
    return Paragraph(text, style)


def fit_image(path, max_w, max_h=None):
    im = Image.open(path)
    w, h = im.size
    scale = max_w / w
    if max_h is not None:
        scale = min(scale, max_h / h)
    return RLImage(str(path), width=w * scale, height=h * scale)


def make_table(data, col_widths, styles):
    cell = styles["CNCell"]
    bold = styles["CNCellBold"]
    rows = []
    for r, row in enumerate(data):
        out = []
        for c, val in enumerate(row):
            st = bold if (r == 0 or c == 0) else cell
            out.append(Paragraph(str(val), st))
        rows.append(out)
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#666666")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def build_pdf():
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )
    W = doc.width
    story = []

    story.append(P("IMEL 7002：项目二", styles["CNTitle"]))
    story.append(P("CMOS D触发器设计与版图项目（中文译本）", styles["CNSubtitle"]))
    story.append(
        P(
            "原文：lab2_2026.pdf · 本文件为课程要求中文翻译，供阅读参考；插图取自英文原文。",
            styles["CNNote"],
        )
    )

    story.append(P("一、项目概述", styles["CNH1"]))
    story.append(
        P(
            "设计、优化并完成一颗 CMOS D 触发器（DFF）的原理图与版图。"
            "本项目旨在加强电路设计、电路分析、VLSI 版图，以及通过 wiki 进行交流与报告的能力。"
            "项目将介绍 CMOS DFF 设计中的折中权衡，帮助理解 DFF 的设计考虑及其相关参数。"
            "项目分为两部分：原理图设计与版图。",
            styles["CNBody"],
        )
    )
    story.append(fit_image(IMG / "fig1.png", W * 0.92, 70 * mm))
    story.append(
        P(
            "图1：项目二符号视图。Q 端接 Project 1 的非反相 buffer；"
            "CLK 与 D 经 Project 1 buffer 驱动后进入 DFF；测量点在 DFF 引脚处。",
            styles["CNCaption"],
        )
    )

    story.append(P("二、设计参数（表1）", styles["CNH1"]))
    table1 = [
        ["参数", "要求"],
        ["工艺", "SMIC 55，标准 VT core 晶体管"],
        ["电源电压", "0.9 V"],
        [
            "Q 端负载",
            "Project 1 的非反相 buffer（原文图1中标为 From Project 1）；负载 buffer 由 VDD_LOAD 供电",
        ],
        [
            "CLK 与 D 输入",
            "理想脉冲源，经 Project 1 buffer 作为驱动后接到 DFF；驱动 buffer 由独立电源 VDD_DRV 供电。功耗定义见表3。",
        ],
        ["输入升降时间", "20 ps"],
        ["工作频率", "1 GHz"],
        ["报告数据范围", "只报告与 DFF 相关的数据；两侧 buffer（两级反相器）不计入"],
        [
            "寄存器类型",
            "可采用任意类型寄存器构成 D 触发器，但必须带复位（reset）功能。建议以课上讲过的结构为起点。",
        ],
        ["最高工作频率", "按原文图2示例方法，求出最高工作频率 fmax"],
    ]
    story.append(make_table(table1, [32 * mm, W - 32 * mm], styles))
    story.append(Spacer(1, 6))

    story.append(P("三、需报告的结果（表2）", styles["CNH1"]))
    story.append(
        P(
            "须同时报告 版图前（pre-layout） 与 版图后（post-layout） 仿真结果，包括（但不限于）："
            "Tsu-dd(1)、Tsu-dd(0)；Thold(1)、Thold(0)；Tsu-opt(1)、Tsu-opt(0)；"
            "Tclk→Q(1)、Tclk→Q(0)；tD(1)、tD(0)；Tw；fmax；P10；Clock-only power；"
            "版图面积；FOM1 / FOM2。",
            styles["CNBody"],
        )
    )
    story.append(
        P(
            "最终成绩取决于优值 FOM1、FOM2（定义见下）、最高工作频率、版图面积，以及报告的完整程度。",
            styles["CNBody"],
        )
    )
    story.append(fit_image(IMG / "fig2.png", W * 0.92, 85 * mm))
    story.append(
        P(
            "图2：用 toggle 测试求 fmax 的示例（带 Reset；时钟频率逐步提高，"
            "观察 Q 是否仍在每个上升沿满摆幅翻转）。",
            styles["CNCaption"],
        )
    )

    story.append(P("四、优值 Figure of Merit", styles["CNH1"]))
    story.append(P("两个优值定义如下（越小越好）：", styles["CNBody"]))
    story.append(
        P(
            "FOM1（版图前）= (tD,max + Tw)² × P10<br/>"
            "其中时间单位为 ps，P10 单位为 μW。<br/>"
            "FOM2（版图后）= (tD,max + Tw)² × P10 ×（版图面积，单位 μm²）",
            styles["CNBody"],
        )
    )
    story.append(
        P(
            "tD,max = max(tD(1), tD(0))，为最优 setup 下最坏情况的 D→Q 延迟；"
            "Tw 为 setup–hold 窗口；P10 为 10% 数据翻转率下的功耗（含时钟功耗）。"
            "将时间项平方，是为了避免仅靠缩小所有晶体管、电路变慢来“改善”FOM。"
            "所有量按表3定义测量。",
            styles["CNBody"],
        )
    )

    story.append(P("五、测量定义（表3）", styles["CNH1"]))
    table3 = [
        ["量", "定义"],
        [
            "时序参考",
            "所有时间均在 DFF 引脚处、信号穿越 50% VDD 的时刻之间测量。时钟参考为 CLK 的上升沿。",
        ],
        [
            "Tsu-dd(1)/(0)",
            "数据丢失建立时间（data-drop setup）：Q 仍能采到新 D 值的最小 setup 时间（分别对应 D 上升 / 下降）。以 1 ps 步进扫描 D 边沿得到。",
        ],
        ["Tsu-opt(1)/(0)", "使 tD(1)/tD(0) 取最小值时的 setup 时间。"],
        [
            "Tclk→Q(1)/(0)",
            "在 Tsu-opt 条件下，从 CLK 上升沿到 Q 上升 / 下降的延迟。",
        ],
        [
            "tD(1)/(0)",
            "D→Q 延迟：从 D 边沿到 Q 边沿（tD = Tsu + Tclk→Q），在 Tsu-opt 下测量。",
        ],
        [
            "Thold(1)/(0)",
            "CLK 上升沿之后，D 仍须保持为 1 / 0 以便 Q 采到该值的最短时间（见原文 hold 测量说明）。可以为负。",
        ],
        ["tD,max", "max(tD(1), tD(0))"],
        [
            "Tw",
            "Setup–hold 窗口：max( Tsu-dd(1)+Thold(1), Tsu-dd(0)+Thold(0) )",
        ],
        [
            "fmax",
            "按原文图2的 toggle 测试：Q 仍能在每个时钟上升沿以满摆幅翻转时的最高时钟频率。",
        ],
        [
            "P10",
            "10% 数据活动下的功耗：CLK=1 GHz、R=0，在 20 ns 稳态窗口内取平均功耗；其间 D 变化两次（在某一时钟下降沿上升，10 个周期后再下降）。"
            "P10 = P(VDD) + P(VDD_DRV) − P(VDD_DRV, baseline)。"
            "baseline 为去掉 DFF、驱动输出悬空的相同仿真，用以扣除驱动本身功耗，保留 DFF 经 CLK、D 引脚取用的功耗。VDD_LOAD 不计。",
        ],
        [
            "Clock-only power",
            "测法同 P10，但 D 保持恒定：分别在 D=0 与 D=1 各测一次，报告二者平均。只报告，不用于 FOM。",
        ],
        [
            "版图面积",
            "DFF 所有绘制层的外接矩形面积（含 N-well，不含文字标注）。well/衬底接触与电源轨必须落在该框内；版图须 DRC、LVS 通过。",
        ],
    ]
    story.append(make_table(table3, [36 * mm, W - 36 * mm], styles))

    story.append(P("六、如何测 DFF 时序（报告指南摘要）", styles["CNH1"]))
    story.append(
        P(
            "示例所用结构与课上相同，建议作起点；任意带复位的寄存器类型均可（见表1）。"
            "电路为上升沿触发，并带异步复位。做两套仿真：分别覆盖 "
            "Tsu-dd(1)、Tsu-opt(1)、Thold(0)、Tclk→Q(1)、tD(1) 与 "
            "Tsu-dd(0)、Tsu-opt(0)、Thold(1)、Tclk→Q(0)、tD(0)。"
            "用脉冲电压源产生 D 与 CLK，扫描 D 升/降沿延迟，得到数据丢失边界，并得到 setup、hold、clk→Q；"
            "Tsu-opt 取 Td 最小时的 setup。仿真中 R 脚始终接地（复位无效）。",
            styles["CNBody"],
        )
    )

    story.append(P("七、报告须提交内容", styles["CNH1"]))
    bullets = [
        "提供原理图截图，并给出 DFF 的全部尺寸细节。",
        "提供版图截图与 stick diagram，说明版图策略。",
        "提供 DRC、LVS 通过截图。",
        "按上文表格报告数据（pre 与 post 仿真结果都要）。",
        "按原文示例提供全部仿真结果截图。",
        "报告 P10 与 clock-only power，含驱动 baseline 仿真（见表3）。",
        "报告 Tw、FOM1（pre-layout）与 FOM2（post-layout）。",
    ]
    for b in bullets:
        story.append(P("• " + b, styles["CNBody"]))

    story.append(PageBreak())
    story.append(P("八、仿真示例说明（原文数值示例）", styles["CNH1"]))
    story.append(P("D 由 0→1 时：", styles["CNBody"]))
    story.append(fit_image(IMG / "sim_tsu_dd_1.png", W, 85 * mm))
    story.append(
        P(
            "波形中，仍能使 Q 置 1 的最晚 D 上升沿对应 Tsu-dd(1)；再晚 1 ps 则 Q 保持 0。"
            "原文示例：Tsu-dd(1) = 49 ps。",
            styles["CNCaption"],
        )
    )
    story.append(
        P("扫描得到 tD(1)–Tsu(1) 曲线，tD 最小处得最优 setup：", styles["CNBody"])
    )
    story.append(fit_image(IMG / "plot_td_tsu_1.png", W * 0.72, 80 * mm))
    story.append(
        P(
            "tD(1) 最小时：Tsu-opt(1)=68 ps，tD(1)=242 ps，Tclk→Q(1)=174 ps。",
            styles["CNCaption"],
        )
    )

    story.append(P("D 由 1→0 时（同法）：", styles["CNBody"]))
    story.append(fit_image(IMG / "sim_tsu_dd_0.png", W, 85 * mm))
    story.append(P("原文示例：Tsu-dd(0)=30 ps。", styles["CNCaption"]))
    story.append(fit_image(IMG / "plot_td_tsu_0.png", W * 0.72, 80 * mm))
    story.append(
        P(
            "tD(0) 最小时：Tsu-opt(0)=48 ps，tD(0)=235 ps，Tclk→Q(0)=187 ps。",
            styles["CNCaption"],
        )
    )

    story.append(P("Hold 时间 thold(1) 说明：", styles["CNH1"]))
    story.append(fit_image(IMG / "sim_hold.png", W, 90 * mm))
    story.append(
        P(
            "通过移动 D 信号的下降沿缩小脉冲宽度，当 Q 由 1 变为 0 时记录 thold。",
            styles["CNCaption"],
        )
    )

    story.append(
        P(
            "说明：本 PDF 为 lab2_2026.pdf 的中文翻译整理版，公式与测量定义以英文原文为准；"
            "图1、图2及波形截图已从原文嵌入。",
            styles["CNNote"],
        )
    )

    doc.build(story)
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    extract_images()
    build_pdf()
