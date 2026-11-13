# Profile template

Fill each section from the stats (`analyze.py`) and the reading pass (`sample.py`). Every claim should be backed by numbers or real examples from the corpus. Leave a section out, or mark it "low confidence", rather than guessing. Write it as the person's own guide ("I", "my").

Keep quoted examples short (one line, under ~25 words) and work-safe, with names replaced by `@name` and links by `<link>`. The profile describes style, never content: no PII and no company-confidential facts. Adapt any example whose content is sensitive and mark it `(adapted)`; see `redaction.md`.

---

```markdown
# <Name>'s Writing & Talking Profile

Portable style guide. Load it into any Claude session and ask for drafts "in my voice".

Source: <N> items from <date range>, broken down by source (e.g. 1,800 Slack messages, 60 sent emails, 9 docs, 40 Jira comments, 25 MR reviews), plus <M> lead posts in <channels/projects>. Left out: <categories excluded>. Built <YYYY-MM-DD>. Redacted: PII and company-confidential details removed. <Shareable | PRIVATE: do not share>.

Who I am, for context: <role, team, domain in one or two lines. Ask the user; don't infer>.

## 1. The big picture
5–8 bullets with numbers: typical length (median/p90 words), casing, end punctuation, emoji rate, single-line vs paragraph habit, overall tone (warm/dry/direct/playful). If chat and long-form differ a lot (say, lowercase in Slack but polished in email), state the contrast here.

## 2. Registers
One subsection per distinct mode found in the corpus, each with 1–2 lines of description and 3–6 real examples. Common ones:
- A. Casual DM / banter
- B. Helping in a public or support channel
- C. Code review / technical pushback (if relevant)
- D. Short team announcements
- E. Strategic or stakeholder writing (recommendations, cross-team asks)
- F. Email: greeting and sign-off habits, subject line style, length, how formal it gets with execs vs peers
- G. Docs & wiki: how a doc opens (TL;DR? context first?), heading style, paragraph length, bullets vs prose, how they present tradeoffs and recommendations
- H. Tickets: how they write a description (problem → context → acceptance criteria?), comment tone
- I. PR/MR descriptions & review comments: description structure, how they phrase feedback (questions vs directives, prefixes like nit:), commit message style
- J. Private venting: describe in general terms only, no quotes, and mark it "never use publicly"
Only include registers the data supports, and label each with its source mix and confidence (for example "email: 42 sent emails, medium confidence").

## 3. Leadership-style posts (if lead posts exist)
- The shape of a typical lead post, step by step (greeting → framing → sections → asks → close)
- Section header conventions (emoji labels, bold, caps)
- List conventions (bullets, nesting, tags like TBD / reach / NOT DOING)
- Recurring moves: how they assign owners and dates, guard scope, restate decisions, close loops, give credit, invite pushback
- 3–5 short examples

## 4. Word usage & lexicon
- Top fillers and softeners, with counts
- Signature phrases grouped by use: openers, asks, thinking out loud, hedges, agreement, closers
- Spelling and typing habits: dropped apostrophes, abbreviations, recurring typos (flag: casual only), elongated words, double punctuation, smiley styles
- Emoji they reach for, and what each one means in their usage

## 5. Sentence structure
How sentences are built: run-ons vs short, connectors (and/so/--/..), reasoning order (claim → reason?), hedging patterns, quote-reply habit, inline lists, arrows, rhetorical questions, parentheticals and asides.

## 6. Jargon & domain vocabulary
Grouped: domain terms, systems and acronyms, process words, tools, company-speak. Terms they use naturally, not every term that appears once. In a shareable profile, generalize internal names and codenames ("an internal messaging service") and keep only generic industry and process vocabulary. In a private profile, list only internal terms the user approved.

## 7. Do / Don't
6–8 dos and 6–8 don'ts for writing as them. Include what to avoid (corporate filler, overly polished prose, registers that shouldn't leak into public posts).

## 8. Quick calibration examples
4–6 short drafted examples (one per common situation) that read like them. These can be lightly cleaned real messages or composites. Mark composites.
```
