from __future__ import annotations

import html
import inspect
import logging
import re
import time
import uuid

import gradio as gr
from pydantic import ValidationError

from postwise.ai.client import get_client
from postwise.config import get_settings
from postwise.pipeline import PipelineError, run_pipeline
from postwise.render import build_view
from postwise.schemas import CreatorInput, Format, PipelineResult, Platform
from postwise.state import mark_made

logger = logging.getLogger("postwise.ui")

PLATFORM_CHOICES = [platform.value for platform in Platform]
FORMAT_CHOICES = [content_format.value for content_format in Format]

PAGE_BACKGROUND = "#F7F4EE"
CARD_BACKGROUND = "#FFFEFA"
BODY_TEXT = "#263044"
MUTED_TEXT = "#62697A"
ACCENT = "#4549A8"
ALT_BACKGROUND = "#F1EEE7"
SOFT_ACCENT = "#EEEDFA"
BORDER = "#D8D6CE"


def _light_theme_values(theme: gr.themes.Base) -> dict[str, str]:
    """Set all Gradio color/fill tokens, including dark variants, to light colors."""
    names = inspect.signature(theme.set).parameters
    values: dict[str, str] = {}
    text_colors = {
        "body_text_color": BODY_TEXT,
        "body_text_color_subdued": MUTED_TEXT,
        "block_info_text_color": MUTED_TEXT,
        "block_label_text_color": BODY_TEXT,
        "block_title_text_color": BODY_TEXT,
        "checkbox_label_text_color": BODY_TEXT,
        "input_placeholder_color": MUTED_TEXT,
        "table_text_color": BODY_TEXT,
        "accordion_text_color": BODY_TEXT,
        "link_text_color": ACCENT,
        "link_text_color_active": ACCENT,
        "link_text_color_hover": ACCENT,
        "link_text_color_visited": ACCENT,
        "checkbox_label_text_color_selected": CARD_BACKGROUND,
    }

    for name in names:
        base = name.removesuffix("_dark")
        if not (
            base.endswith("_color")
            or base.endswith("_fill")
            or base.startswith("color_")
            or base == "checkbox_check"
        ):
            continue

        if base in text_colors:
            color = text_colors[base]
        elif "text_color" in base:
            color = BODY_TEXT
        elif base == "checkbox_check":
            color = CARD_BACKGROUND
        elif base == "color_accent":
            color = ACCENT
        elif base == "color_accent_soft":
            color = SOFT_ACCENT
        elif "error" in base:
            color = "#7A2525" if "text" in base or "icon" in base else "#FCE9E5"
        elif "border_color_accent_subdued" in base:
            color = BORDER
        elif "selected" in base:
            color = ACCENT
        elif "focus" in base and "border" in base:
            color = ACCENT
        elif "border_color" in base:
            color = BORDER
        elif "link" in base or "loader" in base or "slider" in base:
            color = ACCENT
        elif "accent_soft" in base or "focus" in base or "hover" in base:
            color = SOFT_ACCENT
        elif "secondary" in base or "even_background" in base:
            color = ALT_BACKGROUND
        elif "body_background" in base:
            color = PAGE_BACKGROUND
        else:
            color = CARD_BACKGROUND
        values[name] = color
    return values


LIGHT_THEME = gr.themes.Default(
    primary_hue=gr.themes.colors.indigo,
    neutral_hue=gr.themes.colors.stone,
    font=["system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
).set(**_light_theme_values(gr.themes.Default()))

LIGHT_MODE_JS = """
() => {
    document.documentElement.classList.remove("dark");
    document.body?.classList.remove("dark");
    return [];
}
"""

BLOCKS_THEME: dict[str, gr.themes.Base] = {}
LAUNCH_THEME: dict[str, gr.themes.Base] = {}
if "theme" in inspect.signature(gr.Blocks).parameters:
    BLOCKS_THEME["theme"] = LIGHT_THEME
else:
    LAUNCH_THEME["theme"] = LIGHT_THEME

CUSTOM_CSS = """
:root {
    color-scheme: light;
}
body, .gradio-container {
    background: #F7F4EE !important;
    color: #263044 !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
footer {
    display: none !important;
}
#made-btn {
    display: none !important;
}
.gradio-container {
    max-width: 760px !important;
    margin: 0 auto !important;
    padding: 28px 20px 48px !important;
}
.gradio-container .main.fillable > .wrap,
.gradio-container .contain {
    width: 100% !important;
    max-width: 720px !important;
}
.gradio-container .main.fillable {
    padding: 0 !important;
}
.pw-header {
    margin-bottom: 28px !important;
    padding: 0 0 22px !important;
    border-bottom: 1px solid #D8D6CE !important;
}
.pw-title h1 {
    margin: 0 0 6px !important;
    color: #263044 !important;
    font-family: Georgia, "Times New Roman", serif !important;
    font-size: 36px !important;
    font-weight: 700 !important;
    letter-spacing: -0.035em !important;
}
.pw-tagline {
    margin: 0 !important;
    color: #62697A !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}
.pw-form, .pw-plan {
    gap: 22px !important;
}
.pw-form {
    padding: 28px !important;
    background: #FFFEFA !important;
    border: 1px solid #D8D6CE !important;
    border-radius: 18px !important;
    box-shadow: 0 12px 32px rgba(38, 48, 68, 0.06) !important;
}
.pw-form label, .pw-form .wrap label,
.pw-form [data-testid="block-label"],
.pw-form [data-testid="label"], .pw-form p {
    color: #263044 !important;
}
.pw-form .wrap, .pw-form [data-testid="textbox"],
.pw-form [data-testid="slider"], .pw-form [data-testid="checkboxgroup"] {
    background: transparent !important;
}
.pw-form input:not([type="checkbox"]):not([type="range"]),
.pw-form textarea, .pw-form select {
    background: #FFFEFA !important;
    border-color: #D8D6CE !important;
    color: #263044 !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
.pw-form input::placeholder, .pw-form textarea::placeholder {
    color: #62697A !important;
    opacity: 1 !important;
}
.pw-form input[type="checkbox"] {
    accent-color: #4549A8 !important;
}
.pw-form [role="checkbox"], .pw-form [role="radio"] {
    color: #263044 !important;
}
.pw-form input:focus, .pw-form textarea:focus {
    border-color: #4549A8 !important;
    box-shadow: 0 0 0 2px rgba(69, 73, 168, 0.16) !important;
}
.pw-form input[type="range"] {
    accent-color: #4549A8 !important;
}
.pw-primary button, .pw-action {
    background: #4549A8 !important;
    border: 0 !important;
    border-radius: 99px !important;
    color: #FFFEFA !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    min-height: 48px !important;
    padding: 0 24px !important;
}
.pw-primary button:hover, .pw-action:hover {
    background: #373B8F !important;
}
#build-status {
    color: #62697A !important;
    font-size: 14px !important;
}
.pw-lane-label, .pw-label {
    color: #62697A;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    line-height: 1.4;
    text-transform: uppercase;
}
.pw-lane {
    margin: 8px 0 12px;
    color: #263044;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(28px, 7vw, 40px);
    font-weight: 400;
    line-height: 1.18;
}
.pw-progress {
    margin: 0 0 32px;
    color: #62697A;
    font-size: 13px;
    line-height: 1.6;
}
.pw-hero-card {
    margin: 0 0 28px;
    padding: 32px;
    background: #FFFEFA;
    border: 1px solid #D8D6CE;
    border-radius: 16px;
    box-shadow: 0 8px 28px rgba(38, 48, 68, 0.05);
}
.pw-meta {
    margin: 0 0 28px;
    color: #62697A;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    line-height: 1.5;
    text-transform: uppercase;
}
.pw-hook {
    margin: 0 0 36px;
    color: #263044;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(25px, 6.5vw, 34px);
    font-weight: 400;
    line-height: 1.25;
    overflow-wrap: anywhere;
}
.pw-section {
    margin-top: 48px;
}
.pw-label {
    margin: 0 0 16px;
}
.pw-body {
    margin: 0;
    color: #263044;
    font-size: 15px;
    line-height: 1.6;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
}
.pw-fix {
    margin-top: 32px;
    padding: 14px 16px;
    background: #FFF3D6;
    border-radius: 10px;
    color: #4B3A16;
    font-size: 13px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}
.pw-score {
    margin: 14px 0 0;
    color: #62697A;
    font-size: 12px;
    line-height: 1.5;
}
.pw-hero-card .pw-action {
    margin-top: 28px;
    cursor: pointer;
    width: 100%;
}
.pw-complete {
    margin: 0 0 20px;
    padding: 12px 16px;
    background: #EEEDFA;
    border-radius: 10px;
    color: #263044;
    font-size: 14px;
    line-height: 1.6;
}
.pw-queue {
    display: grid;
    gap: 12px;
    margin: 0 0 28px;
}
.pw-queue-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    min-width: 0;
    padding: 18px 20px;
    background: #FFFEFA;
    border: 1px solid #D8D6CE;
    border-radius: 14px;
}
.pw-queue-copy {
    min-width: 0;
}
.pw-queue-day {
    margin: 0 0 6px;
    color: #62697A;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.pw-queue-hook {
    margin: 0;
    color: #263044;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 19px;
    line-height: 1.35;
    overflow-wrap: anywhere;
}
.pw-queue-state {
    flex: 0 0 18px;
    color: #62697A;
    font-size: 18px;
    text-align: center;
}
.pw-lock {
    position: relative;
    display: inline-block;
    width: 13px;
    height: 11px;
    margin-top: 5px;
    background: #62697A;
    border-radius: 2px;
}
.pw-lock::before {
    position: absolute;
    top: -6px;
    left: 3px;
    width: 7px;
    height: 8px;
    border: 1.5px solid #62697A;
    border-bottom: 0;
    border-radius: 6px 6px 0 0;
    content: "";
}
.pw-collapsed {
    margin: 0 0 24px;
    border-top: 1px solid #D8D6CE;
    border-bottom: 1px solid #D8D6CE;
}
.pw-collapsed summary {
    position: relative;
    padding: 20px 28px 20px 0;
    color: #263044;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    list-style: none;
}
.pw-collapsed summary::-webkit-details-marker {
    display: none;
}
.pw-collapsed summary::before {
    position: absolute;
    right: 6px;
    content: "▸";
}
.pw-collapsed[open] summary::before {
    content: "▾";
}
.pw-plan-content {
    padding: 4px 0 24px;
}
.pw-plan-block {
    margin-top: 28px;
}
.pw-plan-list {
    display: grid;
    gap: 12px;
    margin: 0;
    padding: 0;
    list-style: none;
}
.pw-plan-list li {
    color: #263044;
    font-size: 14px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}
.pw-plan-item-title {
    color: #263044;
    font-weight: 600;
}
.pw-footer {
    margin: 24px 0 0;
    color: #62697A;
    font-size: 12px;
    line-height: 1.6;
    text-align: center;
}
@media (max-width: 520px) {
    .gradio-container {
        padding: 24px 16px 36px !important;
    }
    .pw-hero-card {
        padding: 24px 20px;
    }
    .pw-form {
        padding: 20px 16px !important;
    }
    .pw-meta {
        margin-bottom: 22px;
        letter-spacing: 0.04em;
        overflow-wrap: anywhere;
    }
    .pw-queue-card {
        padding: 16px;
    }
}
"""

BLOCKS_CSS: dict[str, str] = {}
LAUNCH_CSS: dict[str, str] = {}
if "css" in inspect.signature(gr.Blocks).parameters:
    BLOCKS_CSS["css"] = CUSTOM_CSS
else:
    LAUNCH_CSS["css"] = CUSTOM_CSS
FONT_HEAD = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&'
    'family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
)
BLOCKS_HEAD: dict[str, str] = {}
LAUNCH_HEAD: dict[str, str] = {}
if "head" in inspect.signature(gr.Blocks).parameters:
    BLOCKS_HEAD["head"] = FONT_HEAD
else:
    LAUNCH_HEAD["head"] = FONT_HEAD

OUTLINE_LABELS = {
    "text": "OUTLINE",
    "short_video": "PREMISE & BEATS",
    "long_video": "PREMISE & BEATS",
    "carousel": "SLIDES",
    "audio": "SEGMENTS",
}


def parse_goal_number(text: str) -> int | None:
    """Pull the first number out of goal_90d. '1,000 followers' -> 1000."""
    match = re.search(r"\b([\d,]+)\b", text)
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


def _text(value: object) -> str:
    return html.escape(str(value)) if value is not None else ""


def _upper(value: object) -> str:
    return _text(value).replace("_", " ").upper()


def _section(label: str, content: object) -> str:
    return (
        '<section class="pw-section">'
        f'<p class="pw-label">{_text(label)}</p>'
        f'<p class="pw-body">{_text(content)}</p>'
        "</section>"
    )


def _format_score(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{value:g}"
    return _text(value)


def _render_hero(card: dict[str, object], complete: bool) -> str:
    day = _upper(card.get("day"))
    daypart = _upper(card.get("daypart"))
    platform = _upper(card.get("platform"))
    content_format = _upper(card.get("format"))
    format_value = str(card.get("format") or "")
    outline_label = OUTLINE_LABELS.get(format_value, "OUTLINE")

    completion = (
        '<p class="pw-complete">All posts are done. Next week opens Monday.</p>' if complete else ""
    )
    button = (
        '<button class="pw-action" type="button" '
        "onclick=\"document.querySelector('#made-btn button, button#made-btn')?.click()\">"
        "I made it</button>"
        if not card.get("made")
        else ""
    )
    return (
        '<article class="pw-hero-card">'
        f"{completion}"
        f'<p class="pw-meta">{day} {daypart} · {platform} · {content_format}</p>'
        f'<h2 class="pw-hook">{_text(card.get("hook"))}</h2>'
        f"{_section(outline_label, card.get('outline'))}"
        f"{_section('CAPTION', card.get('caption'))}"
        f"{_section('CTA', card.get('cta'))}"
        f'<div class="pw-fix">One fix → {_text(card.get("fix"))}</div>'
        f'<p class="pw-score">Score: {_format_score(card.get("score"))}/100</p>'
        f"{button}"
        "</article>"
    )


def _render_queue(queue: list[dict[str, object]]) -> str:
    if not queue:
        return ""
    cards: list[str] = []
    for card in queue:
        state = (
            '<span class="pw-queue-state" aria-label="Made">✓</span>'
            if card.get("made")
            else '<span class="pw-queue-state" aria-label="Locked">'
            '<span class="pw-lock" aria-hidden="true"></span></span>'
        )
        cards.append(
            '<article class="pw-queue-card">'
            '<div class="pw-queue-copy">'
            f'<p class="pw-queue-day">Then {_upper(card.get("day"))}</p>'
            f'<p class="pw-queue-hook">{_text(card.get("hook"))}</p>'
            "</div>"
            f"{state}"
            "</article>"
        )
    return f'<div class="pw-queue">{"".join(cards)}</div>'


def _render_plan_details(plan: dict[str, object]) -> str:
    direction = plan.get("direction", [])
    audience = plan.get("audience", {})
    rhythm = plan.get("rhythm", [])
    metrics = plan.get("metrics", [])

    direction_items = (
        "".join(
            '<li><span class="pw-plan-item-title">'
            f"{_upper(item.get('pillar'))}:</span> {_text(item.get('idea'))}</li>"
            for item in direction
            if isinstance(item, dict)
        )
        if isinstance(direction, list)
        else ""
    )
    topic_list = audience.get("topics", []) if isinstance(audience, dict) else []
    audience_source = audience.get("source") if isinstance(audience, dict) else ""
    source_label = "from your DMs" if audience_source == "dm" else "suggested"
    topic_items = (
        "".join(f"<li>{_text(topic)}</li>" for topic in topic_list if isinstance(topic, str))
        if isinstance(topic_list, list)
        else ""
    )
    rhythm_items = (
        "".join(
            '<li><span class="pw-plan-item-title">'
            f"{_upper(item.get('day'))} {_upper(item.get('daypart'))} · "
            f"{_upper(item.get('platform'))} · {_upper(item.get('format'))}</span>"
            f" · {_upper(item.get('pillar'))}</li>"
            for item in rhythm
            if isinstance(item, dict)
        )
        if isinstance(rhythm, list)
        else ""
    )
    metric_items = (
        "".join(
            '<li><span class="pw-plan-item-title">'
            f"{_text(item.get('name'))}:</span> {_text(item.get('why'))}</li>"
            for item in metrics
            if isinstance(item, dict)
        )
        if isinstance(metrics, list)
        else ""
    )

    return (
        '<details class="pw-collapsed">'
        "<summary>The plan behind all this</summary>"
        '<div class="pw-plan-content">'
        '<section class="pw-plan-block">'
        '<p class="pw-label">YOUR GOAL</p>'
        f'<p class="pw-body">{_text(plan.get("goal"))}</p>'
        f'<p class="pw-body">{_text(plan.get("milestone_description"))}</p>'
        "</section>"
        '<section class="pw-plan-block">'
        '<p class="pw-label">DIRECTION</p>'
        f'<ul class="pw-plan-list">{direction_items}</ul>'
        "</section>"
        '<section class="pw-plan-block">'
        f'<p class="pw-label">AUDIENCE · {_text(source_label)}</p>'
        f'<ul class="pw-plan-list">{topic_items}</ul>'
        "</section>"
        '<section class="pw-plan-block">'
        '<p class="pw-label">WEEKLY RHYTHM</p>'
        f'<ul class="pw-plan-list">{rhythm_items}</ul>'
        "</section>"
        '<section class="pw-plan-block">'
        '<p class="pw-label">WHAT TO MEASURE</p>'
        f'<ul class="pw-plan-list">{metric_items}</ul>'
        "</section>"
        "</div>"
        "</details>"
    )


def render_plan_html(view: dict[str, object], elapsed: float, answer_count: int) -> str:
    """Render the view contract returned by postwise.render.build_view."""
    progress = view.get("progress", {})
    if not isinstance(progress, dict):
        progress = {}
    made = int(progress.get("made", 0))
    total = int(progress.get("total", 0))
    hero = view.get("hero")
    queue = view.get("queue", [])
    plan = view.get("plan", {})
    if not isinstance(plan, dict):
        plan = {}

    hero_html = ""
    if isinstance(hero, dict):
        hero_html = _render_hero(hero, total > 0 and made >= total)
    else:
        hero_html = '<p class="pw-body">No posts are available in this plan.</p>'
    queue_html = (
        _render_queue(queue)
        if isinstance(queue, list) and all(isinstance(card, dict) for card in queue)
        else ""
    )
    calls = 2 + total

    return (
        '<main class="pw-plan">'
        "<header>"
        '<p class="pw-lane-label">YOUR LANE</p>'
        f'<h1 class="pw-lane">{_text(view.get("lane"))}</h1>'
        f'<p class="pw-progress">You&#39;ve made {made} of {total} this week.</p>'
        "</header>"
        f"{hero_html}"
        f"{queue_html}"
        f"{_render_plan_details(plan)}"
        f'<p class="pw-footer">Built in {elapsed:.1f}s · {calls} AI calls · '
        f"{answer_count} answers</p>"
        "</main>"
    )


def on_submit(
    makes_and_audience: str | None,
    goal_90d: str | None,
    hours_per_week: int | float,
    audience_locations_text: str | None,
    platforms: list[str] | None,
    formats: list[str] | None,
    samples_text: str | None,
    dm_questions_text: str | None,
):
    makes_and_audience = makes_and_audience or ""
    goal_90d = goal_90d or ""
    audience_locations_text = audience_locations_text or ""
    samples_text = samples_text or ""
    dm_questions_text = dm_questions_text or ""

    if not makes_and_audience.strip():
        raise gr.Error("Tell us what you make first.")
    if not goal_90d.strip():
        raise gr.Error("Tell us what you want in 90 days.")
    if not platforms:
        raise gr.Error("Pick at least one platform.")
    if not formats:
        raise gr.Error("Pick at least one format.")

    locations = [part.strip() for part in audience_locations_text.split(",") if part.strip()]
    if not locations:
        raise gr.Error("Tell us where your audience is.")

    samples = [line.strip() for line in samples_text.splitlines() if line.strip()][:3]
    dm_questions = [line.strip() for line in dm_questions_text.splitlines() if line.strip()][:20]
    try:
        creator_input = CreatorInput(
            makes_and_audience=makes_and_audience.strip(),
            goal_90d=goal_90d.strip(),
            goal_number=parse_goal_number(goal_90d),
            hours_per_week=int(hours_per_week),
            audience_locations=locations,
            platforms=[Platform(platform) for platform in platforms],
            formats=[Format(content_format) for content_format in formats],
            samples=samples,
            dm_questions=dm_questions,
        )
    except ValidationError as exc:
        raise gr.Error("Please check your answers and try again.") from exc

    yield (
        "Building your plan...",
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
        gr.update(),
    )
    started = time.perf_counter()
    session_id = str(uuid.uuid4())
    try:
        client = get_client(get_settings())
        result = run_pipeline(creator_input, client)
    except PipelineError as exc:
        logger.exception("Pipeline failed at %s", exc.step)
        yield "", gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        raise gr.Error("Something went wrong while building your plan. Please try again.") from exc
    except ValueError as exc:
        logger.exception("Could not configure the plan generator")
        yield "", gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
        raise gr.Error("Something went wrong while building your plan. Please try again.") from exc

    elapsed = time.perf_counter() - started
    view = build_view(result, session_id)
    answer_count = 5 + bool(samples) + bool(dm_questions)
    html_content = render_plan_html(view, elapsed, answer_count)
    yield (
        "",
        html_content,
        session_id,
        result,
        {"elapsed": elapsed, "answer_count": answer_count},
        gr.update(visible=False),
        gr.update(visible=True),
    )


def on_made(
    session_id: str | None,
    result: PipelineResult | None,
    render_stats: dict[str, float | int] | None,
):
    if not session_id or result is None:
        return gr.update()
    view = build_view(result, session_id)
    hero = view.get("hero")
    if not isinstance(hero, dict):
        return gr.update()
    mark_made(session_id, str(hero["slot_id"]))
    stats = render_stats or {}
    return render_plan_html(
        view=build_view(result, session_id),
        elapsed=float(stats.get("elapsed", 0)),
        answer_count=int(stats.get("answer_count", 5)),
    )


with gr.Blocks(title="PostWise", **BLOCKS_CSS, **BLOCKS_HEAD, **BLOCKS_THEME) as demo:
    with gr.Column(elem_classes=["pw-header"]):
        gr.Markdown("# PostWise", elem_classes=["pw-title"])
        gr.Markdown(
            "A clear plan for creators who are just starting",
            elem_classes=["pw-tagline"],
        )
    session_state = gr.State(value=None)
    result_state = gr.State(value=None)
    render_stats_state = gr.State(value=None)

    with gr.Column(visible=True, elem_classes=["pw-form"]) as form_column:
        makes_and_audience = gr.Textbox(
            label="What do you make, and who is it for?",
            lines=1,
        )
        goal_90d = gr.Textbox(
            label="What do you want in 90 days?",
            lines=1,
        )
        hours_per_week = gr.Slider(
            minimum=1,
            maximum=20,
            value=5,
            step=1,
            label="Hours per week you can give this",
        )
        audience_locations = gr.Textbox(
            label="Where is your audience?",
            lines=1,
            placeholder="Separate locations with commas",
        )
        platforms = gr.CheckboxGroup(
            choices=PLATFORM_CHOICES,
            label="Platforms",
        )
        formats = gr.CheckboxGroup(
            choices=FORMAT_CHOICES,
            label="Formats",
        )
        with gr.Accordion("Make the plan sharper", open=False):
            samples = gr.Textbox(
                label="Paste up to 3 posts, captions, or transcripts.",
                lines=3,
                max_lines=3,
                placeholder="One per line",
            )
            dm_questions = gr.Textbox(
                label="Questions people ask you in DMs or comments.",
                lines=4,
                max_lines=20,
                placeholder="One per line",
            )
        submit_btn = gr.Button(
            "Build my plan",
            variant="primary",
            elem_classes=["pw-primary"],
        )
        build_status = gr.Markdown("", elem_id="build-status")

    with gr.Column(visible=False, elem_classes=["pw-plan"]) as plan_column:
        plan_html = gr.HTML()

    made_btn = gr.Button("I made it", elem_id="made-btn")
    submit_btn.click(
        on_submit,
        inputs=[
            makes_and_audience,
            goal_90d,
            hours_per_week,
            audience_locations,
            platforms,
            formats,
            samples,
            dm_questions,
        ],
        outputs=[
            build_status,
            plan_html,
            session_state,
            result_state,
            render_stats_state,
            form_column,
            plan_column,
        ],
        show_progress="hidden",
    )
    made_btn.click(
        on_made,
        inputs=[session_state, result_state, render_stats_state],
        outputs=[plan_html],
        show_progress="hidden",
    )
    demo.load(None, js=LIGHT_MODE_JS, queue=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo.launch(server_port=7860, **LAUNCH_CSS, **LAUNCH_HEAD, **LAUNCH_THEME)
