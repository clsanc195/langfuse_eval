"""Build the observability-comparison presentation as a .pptx.

Theme: professional engineering — white background, AMEX blue accents,
centered layouts, fact-focused. Run:

    .venv/bin/python docs/presentation/build_pptx.py

Output: docs/presentation/observability_comparison.pptx
"""
from __future__ import annotations

import os
import pathlib
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from copy import deepcopy
from lxml import etree

# ============================================================
# Theme
# ============================================================
AMEX_BLUE = RGBColor(0x00, 0x6F, 0xCF)
AMEX_BLUE_DARK = RGBColor(0x00, 0x47, 0x8F)
AMEX_BLUE_LIGHT = RGBColor(0xE6, 0xF1, 0xFB)
INK = RGBColor(0x1A, 0x1A, 0x1A)
INK_SOFT = RGBColor(0x4A, 0x4A, 0x4A)
LINE_SOFT = RGBColor(0xEC, 0xEC, 0xEC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
OK_GREEN = RGBColor(0x1A, 0x6F, 0x38)
WARN_AMBER = RGBColor(0xB2, 0x6F, 0x00)
NO_RED = RGBColor(0xB2, 0x33, 0x33)

FONT = "Helvetica"

# 16:9 widescreen
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


# ============================================================
# Helpers
# ============================================================

def new_presentation() -> Presentation:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_slide(prs: Presentation):
    layout = prs.slide_layouts[6]  # blank
    return prs.slides.add_slide(layout)


def set_bg_white(slide):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = WHITE


def add_text(slide, left, top, width, height, text, *, size=18, color=INK,
             bold=False, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP, font=FONT):
    tx = slide.shapes.add_textbox(left, top, width, height)
    tf = tx.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    return tx, tf


def add_paragraph(tf, text, *, size=14, color=INK, bold=False, align=PP_ALIGN.CENTER, font=FONT, space_before=6):
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    return p


def add_bullet(tf, text, *, size=14, color=INK, indent=0, font=FONT):
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.LEFT
    p.level = indent
    p.space_before = Pt(4)
    run = p.add_run()
    run.text = "•  " + text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.color.rgb = color
    return p


def add_h2(slide, text, *, top=Inches(0.5)):
    """Big AMEX-blue centered slide heading."""
    add_text(slide, Inches(0.5), top, Inches(12.333), Inches(0.8),
             text, size=32, color=AMEX_BLUE, bold=True, align=PP_ALIGN.CENTER)


def add_subtitle(slide, text, *, top=Inches(1.35), size=15, color=INK_SOFT):
    add_text(slide, Inches(0.5), top, Inches(12.333), Inches(0.5),
             text, size=size, color=color, align=PP_ALIGN.CENTER)


def add_footer(slide, slide_no=None, total=None):
    # subtle rule + page number bottom right
    line = slide.shapes.add_connector(1, Inches(0.5), Inches(7.0), Inches(12.833), Inches(7.0))
    line.line.color.rgb = LINE_SOFT
    line.line.width = Pt(0.5)
    if slide_no is not None and total is not None:
        add_text(slide, Inches(11.5), Inches(7.05), Inches(1.5), Inches(0.3),
                 f"{slide_no} / {total}", size=9, color=INK_SOFT,
                 align=PP_ALIGN.RIGHT)
    add_text(slide, Inches(0.5), Inches(7.05), Inches(10), Inches(0.3),
             "LLM Observability — A Comparative Evaluation",
             size=9, color=INK_SOFT, align=PP_ALIGN.LEFT)


def make_table(slide, left, top, width, height, headers, rows, *,
               header_color=AMEX_BLUE, body_text_color=INK,
               header_text_color=WHITE, font_size=12, header_size=12,
               first_col_bold=False):
    cols_n = len(headers)
    rows_n = len(rows) + 1
    table_shape = slide.shapes.add_table(rows_n, cols_n, left, top, width, height)
    table = table_shape.table

    # Header
    for ci, h in enumerate(headers):
        cell = table.cell(0, ci)
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_color
        cell.text = ""
        para = cell.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.LEFT
        run = para.add_run()
        run.text = h
        run.font.name = FONT
        run.font.size = Pt(header_size)
        run.font.bold = True
        run.font.color.rgb = header_text_color
        cell.margin_left = Inches(0.12)
        cell.margin_right = Inches(0.12)
        cell.margin_top = Inches(0.06)
        cell.margin_bottom = Inches(0.06)

    # Body
    for ri, row in enumerate(rows, start=1):
        for ci, val in enumerate(row):
            cell = table.cell(ri, ci)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE
            cell.text = ""
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.LEFT
            run = para.add_run()
            if isinstance(val, tuple):
                txt, color = val
            else:
                txt, color = str(val), body_text_color
            run.text = txt
            run.font.name = FONT
            run.font.size = Pt(font_size)
            run.font.color.rgb = color
            if first_col_bold and ci == 0:
                run.font.bold = True
            cell.margin_left = Inches(0.12)
            cell.margin_right = Inches(0.12)
            cell.margin_top = Inches(0.06)
            cell.margin_bottom = Inches(0.06)

    return table_shape


def _add_arrow_line(slide, x1, y1, x2, y2, color=INK, width_pt=1.5):
    """Add a straight arrow connector (line with arrowhead)."""
    conn = slide.shapes.add_connector(1, x1, y1, x2, y2)
    conn.line.color.rgb = color
    conn.line.width = Pt(width_pt)
    # add arrow head via XML
    line = conn.line._get_or_add_ln()
    nsmap = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    tail = etree.SubElement(line, qn('a:tailEnd'))
    tail.set('type', 'triangle')
    tail.set('w', 'med')
    tail.set('h', 'med')
    return conn


def add_rounded_node(slide, left, top, w, h, *, label, sublabel=None,
                     fill=AMEX_BLUE, text_color=WHITE, sub_color=None,
                     corner=0.12):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    # rounded corner adjustment
    try:
        shape.adjustments[0] = corner
    except Exception:
        pass
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.05); tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.05); tf.margin_bottom = Inches(0.05)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.name = FONT
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = text_color
    if sublabel:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(4)
        r2 = p2.add_run()
        r2.text = sublabel
        r2.font.name = FONT
        r2.font.size = Pt(10)
        r2.font.color.rgb = sub_color or text_color
    return shape


def add_circle_node(slide, cx, cy, r, *, label, fill=INK, text_color=WHITE):
    left = cx - r
    top = cy - r
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, 2*r, 2*r)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label
    run.font.name = FONT
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = text_color
    return shape


# ============================================================
# Slides
# ============================================================

def slide_title(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_text(s, Inches(0.5), Inches(2.4), Inches(12.333), Inches(1.2),
             "LLM Observability", size=64, color=AMEX_BLUE, bold=True)
    add_text(s, Inches(0.5), Inches(3.6), Inches(12.333), Inches(0.6),
             "A Comparative Evaluation", size=24, color=INK)
    add_text(s, Inches(0.5), Inches(4.3), Inches(12.333), Inches(0.5),
             "Langfuse · LangSmith · Galileo", size=18, color=INK_SOFT)
    add_text(s, Inches(0.5), Inches(6.5), Inches(12.333), Inches(0.4),
             "Carlos L Sanchez Vila  ·  2026", size=12, color=INK_SOFT)
    return s


def slide_problem(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "The Problem")
    add_text(s, Inches(2), Inches(2.0), Inches(9.333), Inches(2.0),
             ("Production LLM applications need observability.\n"
              "Three platforms compete to solve it.\n"
              "Choosing well affects developer velocity, evaluation rigor, "
              "hosting cost, and vendor lock-in."),
             size=20, color=INK, align=PP_ALIGN.CENTER)
    # callout box
    box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.5), Inches(4.6),
                              Inches(8.333), Inches(1.4))
    box.fill.solid(); box.fill.fore_color.rgb = AMEX_BLUE_LIGHT
    box.line.color.rgb = AMEX_BLUE
    box.line.width = Pt(1.0)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25); tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.2); tf.margin_bottom = Inches(0.2)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r1 = p.add_run(); r1.text = "Goal: "
    r1.font.name = FONT; r1.font.size = Pt(15); r1.font.bold = True; r1.font.color.rgb = AMEX_BLUE_DARK
    r2 = p.add_run(); r2.text = (
        "Build the same agent once. Trace it through all three platforms. Compare what we get — "
        "empirically, side-by-side, with the same code, the same data, the same prompts.")
    r2.font.name = FONT; r2.font.size = Pt(15); r2.font.color.rgb = INK
    return s


def slide_what_evaluated(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "What We Evaluated")
    add_subtitle(s, "Nineteen capability categories, ~120 features, three platforms")
    headers = ["Category", "Question answered"]
    rows = [
        ("Trace observability", "Can I see what my agent is doing?"),
        ("Sessions / threads", "Can I follow a multi-turn conversation?"),
        ("Scoring & evaluation", "How do I know if it's good?"),
        ("Datasets & experiments", "Can I regression-test it?"),
        ("Prompt management", "Can I version and deploy prompts?"),
        ("In-request guardrails", "Can I block bad outputs in flight?"),
        ("Monitoring & alerts", "Will I know when production breaks?"),
        ("Hosting & pricing", "What's the total cost of ownership?"),
        ("SDK ergonomics & ecosystem", "How much friction to integrate?"),
    ]
    make_table(s, Inches(2.5), Inches(2.0), Inches(8.333), Inches(4.6),
               headers, rows, font_size=13, header_size=13,
               first_col_bold=True)
    return s


def slide_three_platforms(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "The Three Contenders")
    cols = [
        ("Langfuse", "OSS, MIT-licensed, self-hostable. Framework-agnostic. Cloud and on-prem.", "langfuse.com"),
        ("LangSmith", "Built by LangChain. SaaS-first, deepest LangGraph integration, most polished UX.", "smith.langchain.com"),
        ("Galileo", "Evaluation-first. Auto-metrics on every trace. Only platform with in-request guardrails.", "app.galileo.ai"),
    ]
    col_w = Inches(3.8)
    gap = Inches(0.2)
    total_w = col_w * 3 + gap * 2
    start_x = (SLIDE_W - total_w) / 2
    for i, (title, body, link) in enumerate(cols):
        x = start_x + (col_w + gap) * i
        # title bar
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.2), col_w, Inches(0.6))
        bar.fill.solid(); bar.fill.fore_color.rgb = AMEX_BLUE
        bar.line.fill.background()
        tf = bar.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = title
        r.font.name = FONT; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = WHITE
        # body
        body_box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.8), col_w, Inches(2.6))
        body_box.fill.solid(); body_box.fill.fore_color.rgb = WHITE
        body_box.line.color.rgb = LINE_SOFT
        body_box.line.width = Pt(0.75)
        bf = body_box.text_frame
        bf.word_wrap = True
        bf.margin_left = Inches(0.2); bf.margin_right = Inches(0.2)
        bf.margin_top = Inches(0.25); bf.margin_bottom = Inches(0.2)
        bp = bf.paragraphs[0]; bp.alignment = PP_ALIGN.CENTER
        br = bp.add_run(); br.text = body
        br.font.name = FONT; br.font.size = Pt(14); br.font.color.rgb = INK
        # link
        lp = bf.add_paragraph(); lp.alignment = PP_ALIGN.CENTER
        lp.space_before = Pt(20)
        lr = lp.add_run(); lr.text = link
        lr.font.name = FONT; lr.font.size = Pt(11); lr.font.color.rgb = AMEX_BLUE
    return s


def slide_approach(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "Our Approach")
    add_subtitle(s, "Built once. Ran three times.", size=18, color=INK)
    tx, tf = add_text(s, Inches(3), Inches(2.6), Inches(7.333), Inches(4.0),
                      "", size=16)
    tf.paragraphs[0].alignment = PP_ALIGN.LEFT
    add_bullet(tf, "One LangGraph agent — a permission-checking helpdesk bot", size=16)
    add_bullet(tf, "Four tools — chained by dependency", size=16)
    add_bullet(tf, "Five scenarios — covering 1 / 2 / 3 / 4 tool calls + an error path", size=16)
    add_bullet(tf, "Identical instrumentation pattern across all three platforms", size=16)
    add_bullet(tf, "Prompts pulled from each platform's registry at runtime", size=16)
    add_bullet(tf, "Datasets registered in each platform", size=16)
    return s


def slide_langgraph(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "The Agent")
    add_subtitle(s, "LangGraph ReAct loop — agent node + tool node + conditional routing")

    # Layout (in inches): vertical center ~ 4.5
    y_center = Inches(4.0)
    h_node = Inches(1.2)

    # START circle at left
    add_circle_node(s, Inches(1.6), y_center, Inches(0.55),
                    label="START", fill=INK, text_color=WHITE)

    # agent rectangle
    agent_left = Inches(3.0); agent_top = y_center - h_node/2
    agent_w = Inches(2.5); agent_h = h_node
    add_rounded_node(s, agent_left, agent_top, agent_w, agent_h,
                     label="agent", sublabel="ChatAnthropic + tools",
                     fill=AMEX_BLUE, sub_color=RGBColor(0xCC, 0xE5, 0xF7))

    # tools rectangle below-right
    tools_left = Inches(6.4); tools_top = Inches(5.0)
    tools_w = Inches(4.6); tools_h = Inches(1.4)
    tools_shape = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                     tools_left, tools_top, tools_w, tools_h)
    tools_shape.fill.solid(); tools_shape.fill.fore_color.rgb = WHITE
    tools_shape.line.color.rgb = AMEX_BLUE
    tools_shape.line.width = Pt(2.5)
    try:
        tools_shape.adjustments[0] = 0.12
    except Exception:
        pass
    tf = tools_shape.text_frame
    tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = "ToolNode"
    r.font.name = FONT; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = AMEX_BLUE
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(2)
    r2 = p2.add_run(); r2.text = "get_ads_id · get_permissions"
    r2.font.name = FONT; r2.font.size = Pt(11); r2.font.color.rgb = INK_SOFT
    p3 = tf.add_paragraph(); p3.alignment = PP_ALIGN.CENTER
    r3 = p3.add_run(); r3.text = "check_admin_access · get_employee_profile"
    r3.font.name = FONT; r3.font.size = Pt(11); r3.font.color.rgb = INK_SOFT

    # END circle far right
    add_circle_node(s, Inches(11.4), y_center, Inches(0.55),
                    label="END", fill=INK, text_color=WHITE)

    # Arrows
    # START -> agent
    _add_arrow_line(s, Inches(2.15), y_center, agent_left, y_center,
                    color=INK, width_pt=2.5)

    # agent -> tools (blue, "if tool_calls")
    _add_arrow_line(s, agent_left + agent_w*0.7, y_center + h_node/2,
                    tools_left + tools_w*0.3, tools_top,
                    color=AMEX_BLUE, width_pt=2.5)
    # label
    add_text(s, Inches(5.5), Inches(4.6), Inches(2.5), Inches(0.4),
             "if tool_calls", size=12, color=AMEX_BLUE, bold=True,
             align=PP_ALIGN.LEFT)

    # tools -> agent (loops back)
    _add_arrow_line(s, tools_left + tools_w*0.2, tools_top,
                    agent_left + agent_w*0.3, y_center + h_node/2,
                    color=INK, width_pt=2.0)

    # agent -> END (else)
    _add_arrow_line(s, agent_left + agent_w, y_center - Inches(0.1),
                    Inches(10.85), y_center - Inches(0.1),
                    color=INK, width_pt=2.5)
    add_text(s, Inches(7.5), Inches(3.45), Inches(1.5), Inches(0.4),
             "else", size=12, color=INK, bold=True, align=PP_ALIGN.LEFT)

    # caption
    add_text(s, Inches(0.5), Inches(6.5), Inches(12.333), Inches(0.4),
             "Conditional edge: if last AIMessage contains tool_calls → tools, else → END",
             size=12, color=INK_SOFT, align=PP_ALIGN.CENTER)
    return s


def slide_tools(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "The Tools")
    add_subtitle(s, "Chained by dependency — each tool's output feeds the next")
    headers = ["Tool", "Input", "Output", "Used when…"]
    rows = [
        ("get_ads_id", "employee name", "ads_id", "any question"),
        ("get_permissions", "ads_id", "list of permissions", "\"what access does X have?\""),
        ("check_admin_access", "permissions, resource", "boolean", "\"does X have admin on Y?\""),
        ("get_employee_profile", "ads_id", "role / team / manager / tenure", "\"who is X, is access appropriate?\""),
    ]
    make_table(s, Inches(1.0), Inches(2.2), Inches(11.333), Inches(3.6),
               headers, rows, font_size=13, header_size=13, first_col_bold=True)
    return s


def slide_scenarios(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "The Scenarios")
    add_subtitle(s, "Same agent, varying complexity. The model decides how many tools to call.")
    headers = ["Scenario", "Question", "Tools called", "Eval style"]
    rows = [
        ("one_tool", "\"What's the ads_id for Jane Doe?\"", "1", "exact match"),
        ("two_tools", "\"What permissions does Alice Nguyen have?\"", "2", "set comparison"),
        ("three_tools", "\"Does Jane Doe have admin on billing-prod?\"", "3", "boolean"),
        ("judgment_call", "\"Explain who Jane Doe is and whether she should keep admin…\"", "4", "LLM-as-judge"),
        ("error_path", "\"What's the ads_id for Nobody McNobody?\"", "1*", "error handling"),
    ]
    make_table(s, Inches(0.8), Inches(2.2), Inches(11.733), Inches(3.6),
               headers, rows, font_size=12, header_size=12, first_col_bold=True)
    add_text(s, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.4),
             "* Returns an error string; agent should recover, not fabricate.",
             size=11, color=INK_SOFT, align=PP_ALIGN.LEFT)
    return s


def slide_instrumentation(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "Instrumentation Effort")
    add_subtitle(s, "For a LangGraph agent — how much code does each platform require?")
    code_blocks = [
        ("Langfuse",
         "from langfuse.langchain import CallbackHandler\n\nagent.invoke(state, config={\n    \"callbacks\": [CallbackHandler()]\n})",
         "1 callback + 3 env vars"),
        ("LangSmith",
         "# no code change\n\nos.environ[\"LANGSMITH_TRACING\"] = \"true\"\n# + LANGSMITH_API_KEY\n# + LANGSMITH_PROJECT",
         "3 env vars, zero code"),
        ("Galileo",
         "from galileo.handlers.langchain import GalileoCallback\n\nagent.invoke(state, config={\n    \"callbacks\": [GalileoCallback()]\n})",
         "1 callback + 3 env vars"),
    ]
    col_w = Inches(3.9); gap = Inches(0.15)
    total_w = col_w * 3 + gap * 2
    start_x = (SLIDE_W - total_w) / 2
    for i, (title, code, sub) in enumerate(code_blocks):
        x = start_x + (col_w + gap) * i
        # title
        add_text(s, x, Inches(2.2), col_w, Inches(0.4),
                 title, size=18, color=AMEX_BLUE, bold=True, align=PP_ALIGN.CENTER)
        # code box
        box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.8), col_w, Inches(2.6))
        box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0xF7, 0xF8, 0xFA)
        box.line.color.rgb = AMEX_BLUE
        box.line.width = Pt(1.0)
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.15); tf.margin_right = Inches(0.1)
        tf.margin_top = Inches(0.15); tf.margin_bottom = Inches(0.15)
        first = True
        for line in code.split("\n"):
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run(); r.text = line if line else " "
            r.font.name = "Menlo"; r.font.size = Pt(10); r.font.color.rgb = INK
        # subtitle
        add_text(s, x, Inches(5.5), col_w, Inches(0.3),
                 sub, size=10, color=INK_SOFT, align=PP_ALIGN.CENTER)
    add_text(s, Inches(0.5), Inches(6.3), Inches(12.333), Inches(0.5),
             "Outside LangChain code, all three require explicit instrumentation:\n"
             "Langfuse @observe, LangSmith @traceable, Galileo @log.",
             size=11, color=INK_SOFT, align=PP_ALIGN.CENTER)
    return s


def slide_comparison_table(prs, title, subtitle, headers, rows, *,
                           caption=None, table_top=Inches(2.2),
                           table_height=Inches(4.2), font_size=12):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, title)
    add_subtitle(s, subtitle)
    make_table(s, Inches(0.8), table_top, Inches(11.733), table_height,
               headers, rows, font_size=font_size, header_size=font_size,
               first_col_bold=True)
    if caption:
        add_text(s, Inches(0.5), Inches(6.5), Inches(12.333), Inches(0.6),
                 caption, size=11, color=INK_SOFT, align=PP_ALIGN.CENTER)
    return s


def _ok():    return ("✅", OK_GREEN)
def _star():  return ("⭐", AMEX_BLUE)
def _warn():  return ("⚠️", WARN_AMBER)
def _no():    return ("❌", NO_RED)


def slide_trace_tree(prs):
    return slide_comparison_table(
        prs,
        "Trace Tree",
        "All three render the same hierarchy: agent → tool → agent → tool → …",
        ["Capability", "Langfuse", "LangSmith", "Galileo"],
        [
            ("Hierarchical span tree", _ok(), _star(), _ok()),
            ("LLM call detail (prompt, completion, tokens)", _ok(), _ok(), _ok()),
            ("Tool call detail (input, output, status)", _ok(), _ok(), _ok()),
            ("Latency rollups (p50/p95/p99)", _ok(), _star(), _ok()),
            ("Cost tracking (built-in pricing)", _ok(), _ok(), _ok()),
            ("Streaming response capture", _ok(), _star(), _ok()),
        ],
        caption="⭐ best-in-class · ✅ supported · ⚠️ partial · ❌ missing",
    )


def slide_sessions(prs):
    s = slide_comparison_table(
        prs,
        "Multi-turn / Sessions",
        "Three turns of a conversation, grouped under one ID",
        ["", "Langfuse", "LangSmith", "Galileo"],
        [
            ("Term", "Session", "Thread", "Session"),
            ("Metadata key", "langfuse_session_id", "thread_id", "session_id"),
            ("UI rendering", "list of traces", ("⭐ chat UI", AMEX_BLUE), "list of traces"),
            ("Per-session aggregates", _ok(), _ok(), _ok()),
            ("Session-level scoring", _ok(), _ok(), _warn()),
        ],
        caption="Winner: LangSmith Threads — only platform with a true chat-UI rendering of multi-turn data.",
    )
    return s


def slide_scoring(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "Scoring & Evaluation")
    add_subtitle(s, "All three support auto-running evaluators. The difference is what runs by default.")
    headers = ["", "Setup effort", "What runs by default"]
    rows = [
        ("Langfuse", "configure: model + prompt + filter + sampling", "nothing — opt-in"),
        ("LangSmith", "configure: Online Evaluator rule", "nothing — opt-in"),
        ("Galileo", ("zero config", AMEX_BLUE),
         "Tool Selection · Action Completion · Context Adherence · Instruction Adherence · Tool Error Rate · Hallucination · Toxicity · PII"),
    ]
    make_table(s, Inches(0.6), Inches(2.2), Inches(12.133), Inches(2.5),
               headers, rows, font_size=12, header_size=12, first_col_bold=True)

    box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(5.0),
                              Inches(10.333), Inches(1.5))
    box.fill.solid(); box.fill.fore_color.rgb = AMEX_BLUE_LIGHT
    box.line.color.rgb = AMEX_BLUE; box.line.width = Pt(1.0)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25); tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.2); tf.margin_bottom = Inches(0.2)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    r1 = p.add_run(); r1.text = "Once configured, "
    r1.font.name = FONT; r1.font.size = Pt(13); r1.font.bold = True; r1.font.color.rgb = AMEX_BLUE_DARK
    r2 = p.add_run(); r2.text = (
        "Langfuse and LangSmith evaluators run server-side on every matching trace, the same way Galileo's auto-metrics do. "
        "The real choice is whether the defaults pick the rubric for you, or whether you pick it yourself.")
    r2.font.name = FONT; r2.font.size = Pt(13); r2.font.color.rgb = INK
    return s


def slide_galileo_metrics(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "Galileo's Headline Feature")
    add_subtitle(s, "Auto-metrics on every trace. No config, no prompt template, no sampling rate.")
    headers = ["Metric", "What it measures"]
    rows = [
        ("Tool Selection Quality", "Did the agent pick correct tools?"),
        ("Action Completion", "Did the multi-step task finish?"),
        ("Context Adherence", "Did the response stay grounded in tool outputs?"),
        ("Instruction Adherence", "Did it follow the system prompt?"),
        ("Tool Error Rate", "Fraction of tool calls that errored"),
        ("Hallucination (ChainPoll)", "Fabricated facts not in source material"),
        ("Toxicity / PII", "Safety signals"),
    ]
    make_table(s, Inches(2.0), Inches(2.0), Inches(9.333), Inches(4.0),
               headers, rows, font_size=13, header_size=13, first_col_bold=True)
    add_text(s, Inches(0.5), Inches(6.3), Inches(12.333), Inches(0.6),
             "Trade-off: opinionated defaults catch obvious problems out of the box;\n"
             "can be noise for teams with specific quality rubrics.",
             size=11, color=INK_SOFT, align=PP_ALIGN.CENTER)
    return s


def slide_prompts(prs):
    return slide_comparison_table(
        prs,
        "Prompt Management",
        "All three offer versioned prompt registries. The data models diverge.",
        ["", "Langfuse", "LangSmith", "Galileo"],
        [
            ("Versioning model", "sequential + mutable labels", ("⭐ git-style commits", AMEX_BLUE), "sequential only"),
            ("Format", "raw string OR chat", "LangChain Runnable", "chat messages only"),
            ("Scoping", "project", "workspace", "project"),
            ("Public sharing", _no(), ("⭐ Prompt Hub", AMEX_BLUE), _no()),
            ("Idempotent push", _no(), ("⭐ 409 native", AMEX_BLUE), _no()),
            ("Pull from SDK", "string", "Runnable", "JSON-parse needed"),
        ],
        table_top=Inches(2.0), table_height=Inches(4.4),
    )


def slide_datasets(prs):
    return slide_comparison_table(
        prs,
        "Datasets & Experiments",
        "Registries of inputs / expected outputs. Run the agent. Compare runs.",
        ["", "Langfuse", "LangSmith", "Galileo"],
        [
            ("Create dataset via SDK", _ok(), _ok(), _ok()),
            ("Trace → dataset promotion", _ok(), ("⭐ one-click", AMEX_BLUE), _ok()),
            ("Splits (train / test / eval)", _no(), ("⭐ unique", AMEX_BLUE), _no()),
            ("Item-level immutable versions", _warn(), _star(), _warn()),
            ("Synthetic dataset generation", _no(), _no(), ("⭐ unique", AMEX_BLUE)),
            ("Pairwise A/B comparison UI", _warn(), ("⭐ unique", AMEX_BLUE), _warn()),
        ],
        table_top=Inches(2.0), table_height=Inches(4.4),
    )


def slide_guardrails(prs):
    s = slide_comparison_table(
        prs,
        "In-Request Guardrails",
        "The category Galileo owns alone — sits in the request path, blocks bad outputs in flight.",
        ["", "Langfuse", "LangSmith", "Galileo"],
        [
            ("Real-time blocking / modification", _no(), _no(), ("⭐ Protect", AMEX_BLUE)),
            ("Hallucination block in flight", _no(), _no(), _star()),
            ("PII redaction at gateway", _no(), _no(), _star()),
            ("Toxicity / safety blocking", _no(), _no(), _star()),
            ("Custom guardrail rules", _no(), _no(), _star()),
        ],
        caption="Langfuse and LangSmith are post-hoc observability.\n"
                "Galileo Protect operates pre-response. Different product category.",
    )
    return s


def slide_hosting(prs):
    return slide_comparison_table(
        prs,
        "Hosting & Pricing",
        "Self-host availability, free-tier shape, signup friction.",
        ["", "Langfuse", "LangSmith", "Galileo"],
        [
            ("OSS free self-host", ("⭐ MIT", AMEX_BLUE), _no(), _no()),
            ("Managed SaaS", "✅ Cloud", _star(), _ok()),
            ("Enterprise self-host", _ok(), "✅ Helm", "✅ VPC"),
            ("Free tier", "Hobby OR self-host forever", "Developer · 5k traces/mo", "Free · work email required"),
            ("Personal email signup", _ok(), _ok(), _no()),
            ("Public pricing", _ok(), _ok(), ("⚠️ some tiers", WARN_AMBER)),
        ],
        table_top=Inches(2.0), table_height=Inches(4.4),
    )


def slide_unique_wins(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "Where Each Uniquely Wins")
    cols = [
        ("Langfuse", [
            "Only OSS / free self-host",
            "Mutable label pointers for prompt deployment",
            "Both raw-string AND chat prompt formats",
            "Most mature OTEL ingestion",
            "Full local dev via docker",
            "HIPAA via self-host control",
        ]),
        ("LangSmith", [
            "Zero-config LangChain integration",
            "Threads UI for chat debugging",
            "Pairwise experiment comparison",
            "Public Prompt Hub",
            "Dataset splits",
            "Trace-aware Playground",
            "Most polished monitoring",
        ]),
        ("Galileo", [
            "Auto-metrics on every trace",
            "Galileo Protect — only in-request guardrails",
            "Log Streams within a project",
            "Synthetic dataset generation",
            "Built-in PII detection",
            "ChainPoll hallucination method",
            "Continuous learning on metrics",
        ]),
    ]
    col_w = Inches(3.9); gap = Inches(0.15)
    total_w = col_w * 3 + gap * 2
    start_x = (SLIDE_W - total_w) / 2
    for i, (title, items) in enumerate(cols):
        x = start_x + (col_w + gap) * i
        # title
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.0), col_w, Inches(0.55))
        bar.fill.solid(); bar.fill.fore_color.rgb = AMEX_BLUE
        bar.line.fill.background()
        tf = bar.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = title
        r.font.name = FONT; r.font.size = Pt(17); r.font.bold = True; r.font.color.rgb = WHITE
        # body
        body = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.55), col_w, Inches(4.4))
        body.fill.solid(); body.fill.fore_color.rgb = WHITE
        body.line.color.rgb = LINE_SOFT; body.line.width = Pt(0.75)
        bf = body.text_frame; bf.word_wrap = True
        bf.margin_left = Inches(0.2); bf.margin_right = Inches(0.15)
        bf.margin_top = Inches(0.2); bf.margin_bottom = Inches(0.15)
        first = True
        for item in items:
            p = bf.paragraphs[0] if first else bf.add_paragraph()
            first = False
            p.alignment = PP_ALIGN.LEFT
            p.space_before = Pt(6)
            r = p.add_run(); r.text = "•  " + item
            r.font.name = FONT; r.font.size = Pt(12); r.font.color.rgb = INK
    return s


def slide_decision(prs):
    return slide_comparison_table(
        prs,
        "Decision Guidance",
        "If your priority is X, pick Y.",
        ["If your priority is…", "Pick"],
        [
            ("Free self-host, OSS, data sovereignty", ("Langfuse", AMEX_BLUE)),
            ("Lowest-friction LangChain / LangGraph integration", ("LangSmith", AMEX_BLUE)),
            ("Most polished chat / multi-turn debugging", ("LangSmith (Threads)", AMEX_BLUE)),
            ("Eval-first agent quality without setup", ("Galileo", AMEX_BLUE)),
            ("Real-time production guardrails in the request path", ("Galileo (no peer)", AMEX_BLUE)),
            ("Lowest cost at high trace volume", ("Langfuse self-host", AMEX_BLUE)),
            ("Dataset / experiment workflow with pairwise compare", ("LangSmith", AMEX_BLUE)),
            ("Public prompt sharing / community library", ("LangSmith Prompt Hub", AMEX_BLUE)),
            ("Least vendor lock-in", ("Langfuse (OSS + OTEL)", AMEX_BLUE)),
        ],
        table_top=Inches(2.0), table_height=Inches(4.6),
    )


def slide_weaknesses(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "Honest Weaknesses")
    cols = [
        ("Langfuse",
         "UI polish trails LangSmith. Monitoring dashboards less mature. "
         "Self-host = self-operate (cost moves from license to ops)."),
        ("LangSmith",
         "SaaS-only at the community tier. No free self-host. "
         "Vendor-tied to LangChain even though it works elsewhere via @traceable."),
        ("Galileo",
         "Work-email signup gate. SDK API churn between versions. "
         "Documentation lighter than the others. Smaller framework ecosystem. "
         "Pricing less transparent."),
    ]
    col_w = Inches(3.9); gap = Inches(0.15)
    total_w = col_w * 3 + gap * 2
    start_x = (SLIDE_W - total_w) / 2
    for i, (title, body) in enumerate(cols):
        x = start_x + (col_w + gap) * i
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.4), col_w, Inches(0.55))
        bar.fill.solid(); bar.fill.fore_color.rgb = WARN_AMBER
        bar.line.fill.background()
        tf = bar.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = title
        r.font.name = FONT; r.font.size = Pt(17); r.font.bold = True; r.font.color.rgb = WHITE
        body_box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.95), col_w, Inches(3.0))
        body_box.fill.solid(); body_box.fill.fore_color.rgb = WHITE
        body_box.line.color.rgb = LINE_SOFT; body_box.line.width = Pt(0.75)
        bf = body_box.text_frame; bf.word_wrap = True
        bf.margin_left = Inches(0.2); bf.margin_right = Inches(0.2)
        bf.margin_top = Inches(0.25); bf.margin_bottom = Inches(0.2)
        bp = bf.paragraphs[0]; bp.alignment = PP_ALIGN.LEFT
        br = bp.add_run(); br.text = body
        br.font.name = FONT; br.font.size = Pt(13); br.font.color.rgb = INK
    return s


def slide_repo(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_h2(s, "What This Repo Proves")
    tx, tf = add_text(s, Inches(2.0), Inches(2.0), Inches(9.333), Inches(4.5),
                      "", size=14)
    tf.paragraphs[0].alignment = PP_ALIGN.LEFT
    items = [
        "Same LangGraph agent, instrumented for all three platforms — no code branching",
        "Prompts pushed to all three registries — content-aware, idempotent push",
        "Datasets registered in each platform with the correct per-platform schema",
        "Sessions / threads grouping verified end-to-end",
        "Programmatic scores attached via SDK (Langfuse, LangSmith)",
        "LLM-as-judge auto-evaluators running on every trace (Galileo) or on filtered traces (Langfuse, LangSmith)",
        "5 scenarios × 3 platforms × 11 notebooks — all validated headlessly",
    ]
    for item in items:
        add_bullet(tf, item, size=15)
    return s


def slide_demo(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_text(s, Inches(0.5), Inches(2.6), Inches(12.333), Inches(1.4),
             "Live Demo", size=64, color=AMEX_BLUE, bold=True)
    add_text(s, Inches(0.5), Inches(4.0), Inches(12.333), Inches(0.6),
             "Same agent. Three platforms. Side by side.", size=22, color=INK)
    add_text(s, Inches(0.5), Inches(5.0), Inches(12.333), Inches(0.8),
             "Watch the same trace in Langfuse, LangSmith, and Galileo.\n"
             "See what's identical, what diverges, what each platform makes easy.",
             size=14, color=INK_SOFT, align=PP_ALIGN.CENTER)
    return s


def slide_questions(prs):
    s = blank_slide(prs); set_bg_white(s)
    add_text(s, Inches(0.5), Inches(2.8), Inches(12.333), Inches(1.4),
             "Questions?", size=64, color=AMEX_BLUE, bold=True)
    add_text(s, Inches(0.5), Inches(4.5), Inches(12.333), Inches(0.6),
             "observability_comparison/", size=15, color=INK_SOFT, font="Menlo")
    add_text(s, Inches(0.5), Inches(5.0), Inches(12.333), Inches(0.6),
             "docs/comparison.md  ·  docs/feature_matrix.md  ·  docs/recording_guide.md",
             size=12, color=INK_SOFT, font="Menlo")
    return s


# ============================================================
# Build
# ============================================================

def main():
    prs = new_presentation()
    builders = [
        slide_title,
        slide_problem,
        slide_what_evaluated,
        slide_three_platforms,
        slide_approach,
        slide_langgraph,
        slide_tools,
        slide_scenarios,
        slide_instrumentation,
        slide_trace_tree,
        slide_sessions,
        slide_scoring,
        slide_galileo_metrics,
        slide_prompts,
        slide_datasets,
        slide_guardrails,
        slide_hosting,
        slide_unique_wins,
        slide_decision,
        slide_weaknesses,
        slide_repo,
        slide_demo,
        slide_questions,
    ]
    slides = []
    for builder in builders:
        slides.append(builder(prs))
    total = len(slides)
    # Add footer to non-title slides
    for i, slide in enumerate(slides, start=1):
        if i in (1, total - 1, total):
            continue
        add_footer(slide, slide_no=i, total=total)

    out = pathlib.Path(__file__).parent / "observability_comparison.pptx"
    prs.save(out)
    print(f"Wrote {out}  ({total} slides)")


if __name__ == "__main__":
    main()
