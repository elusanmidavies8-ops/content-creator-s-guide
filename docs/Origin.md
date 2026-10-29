Postwise: a clear plan for creators who are just starting

**The problem.** Most beginner creators post without a plan. They don't know what to make, when to post, or whether it's working. The cause isn't a lack of creativity. Nobody gives them personal, goal-driven guidance. Industry surveys we reviewed report that about 69% of creators are financially unstable, 59% of beginners never monetize, and burnout is reported by 62–79%. These are global figures from secondary sources, and we use them as background, not as proof for Nigeria. Existing tools mostly report what already happened and assume you already have connected accounts and data. A beginner has neither.

**Our answer**. We turn the three guesses creators make every day — what to make, when to make it, and whether it worked — into three clear decisions. Users answer 5 required questions in under two minutes, with 2 optional ones that make the plan sharper.

**Who this serves**. Anyone who makes content and has to decide what to make next: writers, video creators, comedians, designers, podcasters. We serve the decision and pre-production layer — the thinking before the camera, the keyboard, or the mic. We do not shoot, edit, act, design, or run live analytics.

**Our Solution pipeline**
The design implementation uses an invented system called the DR system to track coherence and solution implementation of the product.

**Our DR system.** A DR is a numbered piece of the app. DR00 to DR08 are steps (what the app does). DR09 to DR13 are outputs (what the creator sees).

- · DR00 Input: the form the user fills in.
  The Questions;

1. What do you make, and who is it for? (one line)
2. What do you want in 90 days? (with a number if possible)
3. Hours per week you can give this
4. Where is your audience? (country or countries)
5. Where do you post, and in what format? (tap platforms + tap formats: text, short video, long video, carousel, audio)

Optional:

6. Paste up to 3 things you're proud of — posts, captions, or transcripts (this gives us your voice)
7. Paste things people often ask you in DMs or comments (this gives us your gaps)



- **DR01 Check:** the app checks the answers are complete and tidies them.


- **DR02 Understand the creator:** the AI turns their answers into a short profile (niche, audience, goal, voice).

- DR03 Measure their voice: plain code measures how they write and speak, from the posts, captions, or transcripts they paste. If they paste nothing, the app suggests a starting voice and labels it as a suggestion.

- **DR04 Find what the audience wants:**
  the app looks at their DM questions and spots topics people ask about that they haven't made content on, or creates suggestions if they don't have any.

- · DR05 Build the strategy: the AI sets their lane and three kinds of content (Magnet, Authority, Affinity);
  · A Magnet piece pulls new people in (the hook).
  · An Authority piece proves the user knows their stuff.
  · An Affinity piece makes people like the user.
    That's the strategy. It's just three buckets with ideas for the creator's niche, and code picks the three numbers to track.

- · DR06 Build the rhythm: code picks days, times, platforms and formats to fit their hours and the formats they chose in DR00.

- · DR07 Write the briefs: the AI drafts one Content Brief per slot in their voice — hook, outline, caption, CTA — shaped by the slot's format. For a writer the outline is the post body. For a video creator or comedian it's the premise and beats, not the performance.


- DR08 Score and fix: code scores each brief on hook strength, premise clarity, caption length, format fit and voice match, and gives one specific fix.

**What the creator gets (outputs)**

- **DR09 Content Direction** (made by DR05): their lane and three kinds of post. Solves "I don't know what to create."

- **DR10 What Your Audience Wants** (made by DR04): topics from their own DM questions, or clearly labelled suggestions if they share none. Solves "I don't know what my audience wants."

- **DR11 Weekly Rhythm** (made by DR06): days, times, platforms and formats sized to their hours. Solves "I don't know when to post."

- **DR12 Goal Path and Scoreboard** (made by DR05): a 30-day milestone and three numbers to check, based on their goal type (audience, community, customers or opportunities). Solves "I can't tell if it's working" and "I can't turn content into results."

- DR13 First 2 Weeks of Content Briefs (made by DR07 and DR08): ready briefs, each scored with one specific fix and a re-score button. Solves "my posts get little engagement" and "I don't know what to actually film or write.

**How it works.** Plain code validates creators answers, measures creators voice, finds gaps and builds the schedule. An open-weight model `openai/gpt-oss-120b` served via Groq  does three jobs only: reading creators  answers into a profile, building the strategy, and writing the drafts. Everything measurable stays in code, so results are transparent and fast.



