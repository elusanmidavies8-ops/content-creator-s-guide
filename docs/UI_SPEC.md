# Postwise UI — build specification

## 0. How to use this document

You are building one file: `postwise_ui.py` at the repo root. It is a Gradio
app. Nothing else changes.

Read these three files first — they are the contract this UI consumes:

- `src/postwise/render.py` — the one function you call: `build_view(result, session_id)`
- `src/postwise/schemas.py` — the models that flow through it
- `src/postwise/state.py` — the four functions that track "I made it"

Do not modify any file in `src/`. If the UI needs a field that
`build_view` doesn't return, stop and ask — the fix belongs in `render.py`,
not in a hack inside `postwise_ui.py`.

Everything below is in scope. Anything not described here is not.

---

## 1. What Postwise is (30-second context)

Postwise is a content planning tool for beginner creators. They answer five
required questions (and up to two optional ones). Postwise produces a plan
that answers three questions: **what to make, when to post, did it work.**

The plan is a **queue, not a dashboard.** The creator sees **one post to
make now**, three waiting behind it, and a plan they can read in a minute.
That is the entire product.

Existing tools show dashboards. Postwise shows a document that ends in one
action.

---

## 2. What to build — two states, one page

The page has two states. Only one is visible at a time.

### State 1 — the form (initial)

- Title block: "Postwise" and the tagline "A clear plan for creators who
  are just starting" (keep current styling).
- Five required fields (see §5).
- Two optional fields collapsed under "Make the plan sharper".
- One primary button: **Build my plan**.

### State 2 — the plan (after submit)

Below the title block, the page becomes:

```
────────────────────────────────────────────────────────────────
YOUR LANE                                           small caps
Relatable everyday comedy for Nigerian Gen Z.       large serif

You've made 0 of 4 this week.                       small, muted
────────────────────────────────────────────────────────────────

  ┌──────────────────────────────────────────────────────────┐
  │ TUE EVENING · INSTAGRAM · SHORT VIDEO              small  │
  │                                                            │
  │ POV: you forgot your matric number on day one    LARGE    │
  │                                                            │
  │ PREMISE & BEATS                                   small    │
  │ First day chaos. Panic. Fake confidence.          body    │
  │ Punchline.                                                 │
  │                                                            │
  │ CAPTION                                           small    │
  │ first day energy 😂 #nigeriancomedy               body    │
  │                                                            │
  │ CTA                                               small    │
  │ Follow for more campus chaos                      body    │
  │                                                            │
  │ One fix → widen the hook to 40-80 chars          callout  │
  │ Score: 82/100                                     muted    │
  │                                                            │
  │ [ I made it ]                                     primary  │
  └──────────────────────────────────────────────────────────┘

  Then Wednesday
  The 3-second rule every skit needs                          🔒

  Then Friday
  Day in the life on campus                                   🔒

  Then Saturday
  [4th brief hook]                                            🔒

  ▸ The plan behind all this

────────────────────────────────────────────────────────────────
Built in 2.1s · 3 AI calls · 5 answers                     optional footer
```

**That's the whole page.** No tabs. No accordions per section. The
"plan behind all this" is the only collapsible element.

After a "I made it" click:

- Progress line updates: **You've made 1 of 4 this week.**
- Next brief becomes the hero.
- Previous hero becomes a locked card in the queue, marked **made**.
- The queue slides up (or, simpler: the whole plan HTML is re-rendered from
  `build_view` — same visual, updated content).

When all briefs are made:

- Hero stays on the last brief, with a small "All 4 done. Next week opens
  Monday." message. Do not show an empty state — show the last brief with a
  completion banner.

---

## 3. The data contract

You call exactly one function:

```python
from postwise.render import build_view

view = build_view(result, session_id)
```

`view` has this shape (this is the shape; comments are illustrative only):

```python
{
    "session_id": str,  # opaque; pass to state functions
    "lane": str,  # e.g. "Relatable everyday comedy for Nigerian Gen Z."
    "hero": {  # one brief card — see §3.1
        "slot_id": str,
        "pillar": "magnet" | "authority" | "affinity",
        "platform": "instagram" | "tiktok" | "youtube" | ...,
        "format": "text" | "short_video" | "long_video" | "carousel" | "audio",
        "day": "mon" | "tue" | ...,
        "daypart": "morning" | "afternoon" | "evening",
        "hook": str,
        "outline": str,
        "caption": str,
        "cta": str,
        "score": float,  # 0-100
        "fix": str,  # one sentence
        "made": bool,
        "locked": False,
        "is_hero": True,
    },
    "queue": [  # 0..N more cards, same shape as hero
        {
            "slot_id": str,
            "pillar": str,
            "platform": str,
            "format": str,
            "day": str,
            "daypart": str,
            "hook": str,
            "outline": str,
            "caption": str,
            "cta": str,
            "score": float,
            "fix": str,
            "made": bool,
            "locked": True,
            "is_hero": False,
        },
        ...,
    ],
    "progress": {
        "made": int,  # 0..total
        "total": int,  # number of briefs
        "ratio": float,  # 0.0..1.0
    },
    "plan": {
        "goal": str,  # e.g. "1,666 by day 30"
        "milestone_description": str,
        "direction": [  # exactly 3 items
            {"pillar": "magnet" | "authority" | "affinity", "idea": str},
            ...,
        ],
        "audience": {
            "source": "dm" | "suggested",
            "topics": [str, ...],
        },
        "rhythm": [  # one per weekly slot
            {
                "day": str,
                "daypart": str,
                "platform": str,
                "format": str,
                "pillar": str,
            },
            ...,
        ],
        "metrics": [  # exactly 3 items
            {"name": str, "why": str},
            ...,
        ],
    },
}
```

### 3.1 The card — one shape, rendered two ways

The hero and every queue card use the same dict shape. They render
differently:

- **Hero card:** full content, primary button "I made it", `is_hero=True`,
  `locked=False`.
- **Queue card:** collapsed, shows only the day + hook, dimmed, `locked=True`,
  no button. Shows a lock icon on the right.

Queue cards are not clickable. They exist to show rhythm — "this is what's
next."

---

## 4. Layout rules

- **One column.** Max width 720px. Centered.
- **Paper, not dashboard.** Off-white body (#F4F5FD is fine — keep current).
  White cards with soft borders. No dark mode.
- **Serif for the lane and hero hook.** Sans-serif elsewhere. The lane and
  hook are the "title" of the document.
- **Section labels are small caps, muted, letter-spaced.** e.g.
  `YOUR LANE`, `CAPTION`, `CTA`. Never louder than the content.
- **Score is muted, not celebrated.** `82/100` in small grey text. Not a
  badge, not a bar. The `fix` line is the coaching. The score is a number.
- **The `fix` line is the only callout.** Small background tint (soft warm
  yellow is fine). Prefix with "One fix →".
- **Spacing is generous.** Line-height 1.6 for body text. 48px between
  sections. 16px between label and content.
- **The form is boring.** Same fields, same labels, same order as the
  current app. No personality on the form — all personality is in the plan.
- **Mobile at 375px**: single column, no horizontal scroll, hero readable
  without zoom. This is the primary form factor — creators are on phones.

---

## 5. Form fields — exact list

This is the data you collect, in the order they appear. Every field maps to
a `CreatorInput` field. See `src/postwise/schemas.py` for types.

### Required (5)

1. **What do you make, and who is it for?** — single-line text box.
   `CreatorInput.makes_and_audience: str`

2. **What do you want in 90 days?** — single-line text box.
   `CreatorInput.goal_90d: str`
   Also: parse the first number in the text and pass it as
   `CreatorInput.goal_number: int | None` if present. See §6 for the helper.

3. **Hours per week you can give this** — slider 1 to 20, default 5.
   `CreatorInput.hours_per_week: int`

4. **Where is your audience?** — single-line text box.
   `CreatorInput.audience_locations: list[str]` (split on comma, strip
   whitespace).

5. **Where do you post, and in what format?**
   - **Platforms** — checkboxes, one from each of:
     `youtube`, `tiktok`, `instagram`, `x`, `linkedin`, `facebook`,
     `threads`, `substack`, `medium`, `blog`, `podcast`
     → `CreatorInput.platforms: list[Platform]`
   - **Formats** — checkboxes, one from each of:
     `text`, `short_video`, `long_video`, `carousel`, `audio`
     → `CreatorInput.formats: list[Format]`

   **Both must be non-empty.** If either is empty, show a validation error
   before submitting.

### Optional (2)

Under a collapsed "Make the plan sharper" disclosure:

6. **Paste up to 3 posts, captions, or transcripts.** — textarea. One per
   line. Max 3 lines.
   `CreatorInput.samples: list[str]`

7. **Questions people ask you in DMs or comments.** — textarea. One per
   line. Max 20 lines.
   `CreatorInput.dm_questions: list[str]`

Empty optional fields are fine. The pipeline will return "suggested"
content for anything missing, clearly labelled in the plan.

---

## 6. Backend wiring

### The submit callback

```python
import re
import uuid

from postwise.ai.client import get_client
from postwise.config import get_settings
from postwise.pipeline import run_pipeline
from postwise.render import build_view
from postwise.schemas import CreatorInput


def parse_goal_number(text: str) -> int | None:
    """Pull the first number out of goal_90d. '1,000 followers' -> 1000."""
    m = re.search(r"\b([\d,]+)\b", text)
    if not m:
        return None
    try:
        return int(m.group(1).replace(",", ""))
    except ValueError:
        return None


def on_submit(
    makes_and_audience,
    goal_90d,
    hours_per_week,
    audience_locations_text,
    platforms,
    formats,
    samples_text,
    dm_questions_text,
):
    # Basic validation
    if not makes_and_audience.strip():
        raise gr.Error("Tell us what you make first.")
    if not platforms:
        raise gr.Error("Pick at least one platform.")
    if not formats:
        raise gr.Error("Pick at least one format.")

    locations = [s.strip() for s in audience_locations_text.split(",") if s.strip()]
    if not locations:
        raise gr.Error("Tell us where your audience is.")

    samples = [line.strip() for line in samples_text.splitlines() if line.strip()][:3]
    dms = [line.strip() for line in dm_questions_text.splitlines() if line.strip()][:20]

    inp = CreatorInput(
        makes_and_audience=makes_and_audience.strip(),
        goal_90d=goal_90d.strip(),
        goal_number=parse_goal_number(goal_90d),
        hours_per_week=int(hours_per_week),
        audience_locations=locations,
        platforms=platforms,
        formats=formats,
        samples=samples,
        dm_questions=dms,
    )

    session_id = str(uuid.uuid4())
    result = run_pipeline(inp, get_client(get_settings()))
    view = build_view(result, session_id)

    # Return: HTML for the plan, the session_id, and the full result.
    # The result is stored in gr.State so "I made it" can re-render without
    # re-calling the pipeline.
    return (
        render_plan_html(view),
        session_id,  # -> gr.State
        result,  # -> gr.State
        gr.update(visible=False),  # hide form column
        gr.update(visible=True),  # show plan column
    )
```

### The "I made it" callback

```python
from postwise.state import mark_made, get_progress
from postwise.render import build_view


def on_made(session_id: str, result):
    # Look up the current hero's slot from the current view
    view = build_view(result, session_id)
    hero = view["hero"]
    if hero is None:
        return gr.update(), gr.update()

    mark_made(session_id, hero["slot_id"])

    # Rebuild view and re-render
    new_view = build_view(result, session_id)
    return render_plan_html(new_view)
```

### Gradio state

```python
with gr.Blocks(...) as demo:
    session_state = gr.State(value=None)   # holds session_id
    result_state = gr.State(value=None)    # holds PipelineResult

    # Form column (visible=True initially)
    # Plan column (visible=False initially)

    submit_btn.click(
        on_submit,
        inputs=[...form fields...],
        outputs=[
            plan_html,          # the rendered plan
            session_state,
            result_state,
            form_column,
            plan_column,
        ],
    )

    # The "I made it" button is inside the rendered HTML.
    # Wire it via a hidden Gradio button — see §6.1.
```

### 6.1 Wiring "I made it" when the button is inside HTML

The hero card contains an "I made it" button. That button lives inside the
HTML string. Gradio's `gr.Button` can't be inside a `gr.HTML` block.

**Two options. Pick option A for v1.**

**Option A — hidden real button, triggered by JS:**

```python
made_btn = gr.Button("I made it", visible=False)
made_btn.click(
    on_made,
    inputs=[session_state, result_state],
    outputs=[plan_html],
)
```

In `render_plan_html`, the "I made it" `<button>` inside the HTML gets an
`onclick` that clicks the hidden Gradio button:

```html
<button onclick="document.querySelector('#made-btn').click()">I made it</button>
```

And the hidden button is rendered with `elem_id="made-btn"`:
```python
made_btn = gr.Button("I made it", visible=False, elem_id="made-btn")
```

That's the whole trick. It's ugly but it works in every Gradio version.

**Option B — real Gradio button below the HTML** (only if Option A fails
in your version of Gradio): render the hero content as `gr.HTML` with no
button, and place a real `gr.Button("I made it", variant="primary")` right
below it. Functionally identical. Use this if Option A misbehaves.

---

## 7. Format-specific rendering

The `outline` field means different things depending on `card["format"]`.
The **label** above the outline changes; the content is rendered as-is with
`white-space: pre-wrap` so newlines in the outline are preserved.

| `format` | Section label | Notes |
|---|---|---|
| `text` | `OUTLINE` | The outline IS the post body. Render as prose. |
| `short_video` | `PREMISE & BEATS` | Not a script. Beats, not lines. |
| `long_video` | `PREMISE & BEATS` | Same as short_video. |
| `carousel` | `SLIDES` | Slide-by-slide. May contain numbers. Render as-is. |
| `audio` | `SEGMENTS` | Segment outline. Prose. |

Hooks, captions, and CTAs are rendered the same way for every format.

Do not try to split the outline into "beat 1, beat 2" yourself. If the
pipeline returned line breaks, `pre-wrap` shows them. If it returned one
paragraph, that's the outline. Trust the content.

---

## 8. Multi-platform and multi-format

A creator may pick **one** platform or **five**. They may pick **one** format
or **all five**. The pipeline alternates slots across everything they picked.

The card carries `platform` and `format` per slot. Your renderer must show
both — never assume a single platform or format. Example: a creator with
`platforms=[instagram, tiktok]` and `formats=[text, short_video]` will see
cards alternating:

- hero: `TUE EVENING · INSTAGRAM · SHORT VIDEO`
- queue[0]: `THU EVENING · TIKTOK · TEXT`
- queue[1]: `FRI EVENING · INSTAGRAM · SHORT VIDEO`
- queue[2]: `SAT EVENING · TIKTOK · TEXT`

Just render whatever's in the card. That's the whole rule.

---

## 9. Visual style — keep the current CSS, small changes

Keep the existing CSS from the current `postwise_ui.py`:

- Indigo primary: `#3B3FB6`
- Body background: `#F4F5FD`
- White cards, soft borders: `#e3e5f6`
- Inter font
- Rounded corners (16px cards, 99px pills)

**Adjustments needed:**

| Change | Why |
|---|---|
| Remove `.pw-grid`, `.pw-week`, `.pw-steps` CSS classes | No grids anymore — single column. |
| Remove the tab CSS | No tabs. |
| Remove the hero pill in the header | Keep the hero, drop the pill. Or keep — it's fine. |
| Add `.pw-hero-card` (hero brief) — larger padding, larger type | Hero is the main event. |
| Add `.pw-queue-card` (queue brief) — smaller, dimmed | Locked state. |
| Add `.pw-fix` — soft yellow background, small text | The one callout. |
| Add `.pw-progress` — muted small line below the lane | "You've made 0 of 4" |
| Add `.pw-collapsed` — the disclosure header | "▸ The plan behind all this" |

The CSS you already have is the aesthetic. You're reusing it, not rewriting it.

---

## 10. What NOT to do (hard list)

Every item below is a real failure mode. Do not do any of them.

1. **No tabs.** No `gr.Tabs()`. No tabbed section navigation.
2. **No dark mode.** No `js` call toggling dark. No `prefers-color-scheme` branching.
3. **No spinners.** If the pipeline takes longer than 1 second, show a simple line "Building your plan..." with no animation.
4. **No numbered inputs.** No "1.", "2.", "3." before field labels.
5. **No emojis in the UI chrome.** Content can have emojis (the creator's caption might). The frame around it should not.
6. **No "AI-generated" text.** The only AI mention is the small footer line at the bottom: "Built in 2.1s · 3 AI calls". Nothing else references AI.
7. **Do not display the 5 sub-scores.** Only `score` (the overall) and `fix`. The rubric — hook, premise, caption_length, format_fit, voice — is invisible to the creator.
8. **Do not show the pipeline trace expandable in v1.** Skip it. It's a v2 feature.
9. **Do not modify `src/`.** If the UI needs a field that `build_view` doesn't return, ask. Don't reach into `render.py`.
10. **Do not add more fields to the form.** Five required, two optional, that's it.
11. **Do not change the DR number semantics.** DR01 is DR01. Don't renumber or skip numbers in comments.
12. **Do not show more than one hero at a time.** Exactly one brief is "now." Everything else is queue.

---

## 11. Testing checklist

Before pushing, run through this list locally.

### Setup

```bash
# From repo root
uv pip install -e ".[dev]"

# .env with fake provider — no API key needed
echo "POSTWISE_LLM_PROVIDER=fake" > .env

# Run
python postwise_ui.py
```

### Test cases

**T1 — the form**
- [ ] Five required fields visible, in the described order
- [ ] Optional fields collapsed under "Make the plan sharper"
- [ ] Both platform AND format checkboxes are present and required
- [ ] Clicking "Build my plan" with empty fields shows a clear error

**T2 — the plan renders**
- [ ] After submit, form disappears, plan appears
- [ ] Lane appears at top, in serif type
- [ ] Progress line reads "You've made 0 of 4 this week." (or 3, or 5 — matches slot count)
- [ ] Hero card shows: platform · format label at top, hook large, outline, caption, cta, one fix, score, "I made it" button
- [ ] Queue shows remaining briefs, dimmed, with lock icons
- [ ] "The plan behind all this" is collapsed by default

**T3 — the disclosure**
- [ ] Click "The plan behind all this" — expands
- [ ] Shows: goal, milestone, three direction pillars, audience topics (with "from your DMs" or "suggested" label), full rhythm list, three metrics
- [ ] Click again — collapses

**T4 — the "I made it" click**
- [ ] Click "I made it" on the hero
- [ ] Progress line goes 0/4 → 1/4
- [ ] Hero becomes the next brief (previously queue[0])
- [ ] Previous hero is now in the queue, marked as made (checkmark instead of lock)
- [ ] Repeat until all made
- [ ] At 4/4, hero shows the last brief with a completion message

**T5 — multi-platform, multi-format**
- [ ] Submit with platforms = [instagram, tiktok], formats = [text, short_video]
- [ ] Card labels show alternating platforms and formats as expected
- [ ] No two consecutive cards share the same platform AND format (unless only one platform/format was chosen)

**T6 — no optional fields**
- [ ] Submit with empty samples and empty DMs
- [ ] Plan still renders
- [ ] Audience section in the disclosure says "suggested" and lists 3 topics
- [ ] Voice still produces briefs (voice profile is marked "suggested" internally, invisible to the creator)

**T7 — the AI failure path**
- [ ] Comment out `.env` (or set `POSTWISE_LLM_PROVIDER=groq` with no key)
- [ ] Submit
- [ ] Gradio shows a clear error ("something went wrong") — not a raw traceback
- [ ] Logs show the underlying `PipelineError` with a step ID

**T8 — mobile**
- [ ] Resize browser to 375px width (DevTools mobile view)
- [ ] No horizontal scroll
- [ ] Hero card readable without zoom
- [ ] "I made it" button reachable with thumb
- [ ] Queue cards stack cleanly

---

## 12. How to iterate

1. **Build the form first.** Get it submitting with fake data (the current `build_plan` is fine as placeholder) — verify the state transition (form hides, plan shows) works.
2. **Wire the real pipeline.** Replace `build_plan` with `run_pipeline` + `build_view`. Verify the plan renders with real data.
3. **Build the hero card.** One card, one brief. Verify every field renders.
4. **Build the queue cards.** Three (or however many) below the hero. Locked style.
5. **Build the disclosure.** Collapsed by default, expands on click.
6. **Wire the "I made it" button.** Hidden-button trick from §6.1. Verify progress updates.
7. **Run the full testing checklist.** Fix what fails.

Do not try to build everything at once. Six small increments beat one big rewrite.

If you're stuck on any step, comment out everything above it and rebuild from the last working version.

If the whole thing feels wrong — the layout, the CSS, the flow — stop and ask before continuing. Do not push a broken UI.

---

## 13. What success looks like

At the end, a stranger opens the app:

1. Sees a form, answers five questions in under 2 minutes
2. Clicks "Build my plan"
3. Sees a lane, a progress line, and **one post to make now**
4. Scrolls — sees three more waiting, a rhythm they can feel
5. Opens "The plan behind all this" — sees the argument
6. Clicks "I made it" — progress advances, next post unlocks
7. Screenshots the hero card and sends it to a friend

If they get to step 7, the UI works. That screenshot is the whole product.

---

*End of spec. If anything is unclear, ask before building. If anything conflicts with what you already have in `postwise_ui.py`, this spec wins — the current version was a starting point, not a final shape.*