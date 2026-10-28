"""PostWise UI. Run:  python postwise_ui.py   then open http://localhost:7860

I owns everything below the BACKEND CONTRACT block.
partner replaces build_plan() with the real model + code steps. Keep the
returned dict shape the same and the UI will not need to change.
"""
import html
import gradio as gr


def esc(x):
    return html.escape(str(x))


# ============ BACKEND CONTRACT (fake data for now) ============
def build_plan(niche, goal, hours, country, platforms, posts, dms):
    p = platforms[0] if platforms else "TikTok"
    return {
        "summary": [("90-day goal", goal or "Grow my audience"),
                    ("Time available", "%d hrs / week" % hours),
                    ("Audience", country or "Nigeria")],
        "direction": [
            {"kind": "Magnet", "color": "#3B3FB6", "title": "Pull new people in",
             "idea": "Short hooks built on the most surprising part of: %s." % niche},
            {"kind": "Authority", "color": "#0F8B8D", "title": "Prove you know it",
             "idea": "Explain one idea in 30 seconds, with one clear example."},
            {"kind": "Affinity", "color": "#C77700", "title": "Be likeable",
             "idea": "Show how you make your content and what you got wrong."}],
        "audience": {"source": "From your DM questions" if dms else "Suggestions (you shared no questions)",
                     "topics": ["How do I start with no equipment?", "What should my first video be?",
                                "How often should I post?"]},
        "rhythm": [{"day": "Mon", "time": "7 PM", "platform": p, "format": "Short video", "kind": "Magnet"},
                   {"day": "Wed", "time": "6 PM", "platform": p, "format": "Explainer", "kind": "Authority"},
                   {"day": "Fri", "time": "8 PM", "platform": p, "format": "Behind the scenes", "kind": "Affinity"}],
        "scoreboard": {"milestone": "Post 6 times and reach 300 average views per post in 30 days.",
                       "metrics": [{"name": "Average views per post", "now": 120, "target": 300},
                                   {"name": "Followers gained", "now": 40, "target": 150},
                                   {"name": "Comments per post", "now": 2, "target": 10}]},
        "posts": [{"slot": "Mon - Magnet", "score": 8, "text": "Nobody tells beginners this about %s..." % niche,
                   "fix": "Cut the first sentence. Start with the surprising fact."},
                  {"slot": "Wed - Authority", "score": 6, "text": "Here is the simple way to understand it:",
                   "fix": "Add one real example in the first 5 seconds."},
                  {"slot": "Fri - Affinity", "score": 4, "text": "So I tried this and it went badly.",
                   "fix": "Say what you learned, not only what failed."}],
    }
# ============ END BACKEND CONTRACT ============


# ---------- renderers: dict -> HTML ----------
def r_summary(items):
    cards = "".join('<div class="pw-card"><div class="pw-label">%s</div><div class="pw-big">%s</div></div>'
                    % (esc(k), esc(v)) for k, v in items)
    return '<div class="pw-grid">%s</div>' % cards


def r_direction(items):
    cards = "".join('<div class="pw-card pw-top" style="--c:%s"><span class="pw-tag" style="background:%s">%s</span>'
                    '<h4>%s</h4><p>%s</p></div>' % (i["color"], i["color"], esc(i["kind"]), esc(i["title"]), esc(i["idea"]))
                    for i in items)
    return '<div class="pw-grid">%s</div>' % cards


def r_audience(a):
    rows = "".join('<div class="pw-card"><p>%s</p></div>' % esc(t) for t in a["topics"])
    return '<div class="pw-label" style="margin:6px 0 10px">%s</div><div class="pw-grid">%s</div>' % (esc(a["source"]), rows)


def r_rhythm(rows):
    cells = "".join('<div class="pw-card"><div class="pw-big">%s</div><div class="pw-label">%s</div><p><b>%s</b><br>%s<br>%s</p></div>'
                    % (esc(r["day"]), esc(r["time"]), esc(r["kind"]), esc(r["platform"]), esc(r["format"])) for r in rows)
    return '<div class="pw-week">%s</div>' % cells


def r_score(s):
    cards = ""
    for m in s["metrics"]:
        pct = min(100, int(100 * m["now"] / m["target"]))
        cards += ('<div class="pw-card"><div class="pw-label">%s</div><div class="pw-big">%s <small>/ %s</small></div>'
                  '<div class="pw-bar"><span style="width:%d%%"></span></div></div>'
                  % (esc(m["name"]), esc(m["now"]), esc(m["target"]), pct))
    return ('<div class="pw-card" style="margin-bottom:12px"><div class="pw-label">30-day milestone</div><p>%s</p></div>'
            '<div class="pw-grid">%s</div>' % (esc(s["milestone"]), cards))


def r_posts(items):
    out = ""
    for p in items:
        col = "#1E9E6A" if p["score"] >= 8 else ("#C77700" if p["score"] >= 6 else "#C23B3B")
        out += ('<div class="pw-card" style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;gap:10px">'
                '<span class="pw-label">%s</span><b style="color:%s">%d / 10</b></div><p>%s</p>'
                '<div class="pw-bar"><span style="width:%d%%;background:%s"></span></div>'
                '<p style="margin-top:10px"><b>Fix:</b> %s</p></div>'
                % (esc(p["slot"]), col, p["score"], esc(p["text"]), p["score"] * 10, col, esc(p["fix"])))
    return out


EMPTY = ('<div class="pw-card pw-empty"><div class="pw-big">Your plan will appear here</div>'
         '<p class="p" style="margin-top:6px">Answer the questions and tap Build my plan.</p>'
         '<div class="pw-steps"><div class="pw-card"><b>1. Direction</b><p>What to make</p></div>'
         '<div class="pw-card"><b>2. Rhythm</b><p>When to post</p></div>'
         '<div class="pw-card"><b>3. Scoreboard</b><p>Whether it worked</p></div></div></div>')


def run(niche, goal, hours, country, platforms, posts, dms):
    if not niche or not niche.strip():
        raise gr.Error("Tell us what you make and who it is for first.")
    plan = build_plan(niche.strip(), goal, int(hours), country, platforms, posts, dms)
    return (r_summary(plan["summary"]), r_direction(plan["direction"]), r_audience(plan["audience"]),
            r_rhythm(plan["rhythm"]), r_score(plan["scoreboard"]), r_posts(plan["posts"]))


CSS = """
.gradio-container {max-width: 1180px !important; margin: auto;}
.pw-hero {background: #3B3FB6; border-radius: 20px; padding: 30px 26px; margin: 8px 0 4px;}
.pw-hero h1 {font-size: 2.4rem; font-weight: 800; letter-spacing: -0.02em; color: #fff !important; margin: 8px 0 0;}
.pw-hero p {margin: 6px 0 0; color: #DADCFB !important; font-size: 1.05rem;}
.pw-pill {display: inline-block; background: #fff; color: #3B3FB6; font-size: .75rem; font-weight: 700; padding: 3px 12px; border-radius: 99px;}
footer {display: none !important;}
.tab-nav button.selected {color: #3B3FB6 !important; border-color: #3B3FB6 !important; font-weight: 700;}
.pw-steps {display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 16px; text-align: left;}
.pw-steps b {color: #3B3FB6;}
.pw-grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px;}
.pw-week {display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;}
.pw-card {background: #fff; color: #1b1d3a; border: 1px solid #e3e5f6; border-radius: 16px; padding: 16px;}
.pw-card h4 {margin: 10px 0 6px; font-size: 1rem;}
.pw-card p {margin: 0; color: #4a4d6e; font-size: .92rem; line-height: 1.5;}
.pw-top {border-top: 4px solid var(--c);}
.pw-label {font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; color: #6b6e8f;}
.pw-big {font-size: 1.35rem; font-weight: 800; color: #1b1d3a; line-height: 1.25;}
.pw-big small {font-size: .85rem; font-weight: 500; color: #6b6e8f;}
.pw-tag {display: inline-block; font-size: .72rem; font-weight: 700; padding: 2px 10px; border-radius: 99px; color: #fff;}
.pw-bar {height: 8px; background: #eceefb; border-radius: 99px; overflow: hidden; margin-top: 10px;}
.pw-bar span {display: block; height: 100%; border-radius: 99px; background: #3B3FB6;}
.pw-empty {text-align: center; padding: 48px 16px; color: #4a4d6e;}
"""

PLATFORMS = ["YouTube Shorts", "TikTok", "Instagram", "X (Twitter)", "Facebook", "LinkedIn"]
theme = gr.themes.Soft(
    primary_hue="indigo", neutral_hue="slate", radius_size="lg",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="#F4F5FD", body_background_fill_dark="#F4F5FD",
    body_text_color="#1b1d3a", body_text_color_dark="#1b1d3a",
    block_background_fill="#FFFFFF", block_background_fill_dark="#FFFFFF",
    block_border_width="1px", block_shadow="none",
    block_label_text_color="#1b1d3a", block_label_text_color_dark="#1b1d3a",
    input_background_fill="#F7F8FE", input_background_fill_dark="#F7F8FE",
    button_primary_background_fill="#3B3FB6", button_primary_background_fill_dark="#3B3FB6",
    button_primary_background_fill_hover="#2E3296", button_primary_background_fill_hover_dark="#2E3296",
    button_primary_text_color="#FFFFFF", button_primary_text_color_dark="#FFFFFF",
)

with gr.Blocks(theme=theme, css=CSS, title="PostWise", js="() => { document.body.classList.remove('dark'); }") as demo:
    gr.HTML('<div class="pw-hero"><span class="pw-pill">What to post. When to post. Did it work.</span><h1>PostWise</h1><p>A clear plan for creators who are just starting</p></div>')
    with gr.Row():
        with gr.Column(scale=2, min_width=300):
            niche = gr.Textbox(label="1. What do you make, and who is it for?", placeholder="e.g. Short history videos for Nigerian students")
            goal = gr.Textbox(label="2. What do you want in 90 days?", placeholder="e.g. 1,000 followers")
            hours = gr.Slider(1, 20, value=5, step=1, label="3. Hours per week you can give this")
            country = gr.Textbox(label="4. Where is your audience?", placeholder="e.g. Nigeria, Ghana")
            platforms = gr.CheckboxGroup(PLATFORMS, label="5. Where do you post?")
            with gr.Accordion("Optional: make the plan sharper", open=False):
                posts = gr.Textbox(label="Up to 3 posts you are proud of", lines=4)
                dms = gr.Textbox(label="Questions people ask you in DMs or comments", lines=4)
            btn = gr.Button("Build my plan", variant="primary", size="lg")
        with gr.Column(scale=3, min_width=320):
            summary = gr.HTML(EMPTY)
            with gr.Tabs():
                with gr.Tab("Direction"):
                    t1 = gr.HTML()
                with gr.Tab("Audience"):
                    t2 = gr.HTML()
                with gr.Tab("Weekly rhythm"):
                    t3 = gr.HTML()
                with gr.Tab("Scoreboard"):
                    t4 = gr.HTML()
                with gr.Tab("First 2 weeks"):
                    t5 = gr.HTML()
    btn.click(run, [niche, goal, hours, country, platforms, posts, dms], [summary, t1, t2, t3, t4, t5])

demo.launch()