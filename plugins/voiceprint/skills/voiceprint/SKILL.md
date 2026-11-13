---
name: voiceprint
description: Build a personal writing-voice profile from someone's own writing (Slack, Microsoft Teams, Gmail/Outlook, Google Docs/Drive, Confluence, Jira/Linear/Asana, GitHub/GitLab, Glean via connectors, or pasted text and files), then draft or rewrite messages, emails, docs, tickets, and review comments in that voice. Use when the user says "learn how I write", "build my voice profile", "analyze my Slack writing style", "write this in my voice", "draft a Slack post like me", "make this sound like me", or asks to update an existing voice profile.
---

# Voiceprint

Two modes:
- **Build:** collect the user's own writing, measure it, read it, and write a portable profile (`voice-profile.md`).
- **Draft:** write or rewrite messages in the voice described by a profile.

Pick the mode from the request. If the user asks to draft and no profile exists, offer to build one first (or draft from a few pasted samples if they'd rather not).

Scripts are in `scripts/` next to this file and use only the Python 3 standard library. Run them with `python3 -I`.

---

## Build mode

### 1. Settle scope first
Before pulling anything, confirm with the user (one short round of questions):
- **Sources:** check which connectors this session has (Slack, Teams/Microsoft 365, Gmail, Google Docs/Drive, Confluence, Jira, Linear/Asana/monday, GitHub/GitLab, Glean), list them, and let the user choose. Pasted text and files always work.
- **Time window:** default is the last 30 days for chat and 90 days for email, docs, tickets and reviews.
- **Exclusions:** close or personal DMs or email threads, specific people, channels, folders or labels. Offer to show their top DM or email partners by count so they can choose.
- **Lead channels or projects** where they post as the lead. These are pulled with no time limit.
- **Who they are:** role, team, domain, in a line or two. This goes in the profile header. Don't infer it.
- **Redaction lists** (see `references/redaction.md`): extra names to mask beyond the people found in the corpus; internal terms to mask (codenames, customers, unreleased products, internal system names); internal domains.
- **Shareable or private profile:** default is **shareable**. Internal system names and codenames are generalized ("the messaging service", "an internal codename") and only generic industry and process jargon is kept. A **private** profile, for their own use only, may keep internal vocabulary they choose, but never PII, secrets, or confidential facts.

### 2. Collect
Follow `references/collecting.md`. It covers the corpus format and `kind` labels, per-connector steps (what to search, what to strip), how much is enough, and privacy. Write `corpus.jsonl` to a temporary working folder, never into a repo.

Give the user short progress notes ("pulled 1,240 messages, now reading lead channels").

### 2b. Redact before anything else
Do this right after collecting, before any analysis. Write the names, terms and domains lists to the working folder (add every person name you saw while collecting: DM partners, mentioned coworkers, email recipients). Then:
```bash
python3 -I scripts/redact.py raw.jsonl -o corpus.jsonl --names names.txt --terms terms.txt --domains domains.txt
rm raw.jsonl
```
All later steps read only the redacted `corpus.jsonl`. Report the replacement counts to the user (counts only, never the values). Regex is a safety net. While reading in step 4, treat anything confidential that slipped through as off-limits for the profile, following `references/redaction.md`.

### 3. Measure
```bash
python3 -I scripts/analyze.py /path/to/corpus.jsonl > /path/to/stats.json
```
This gives length distribution, casing, punctuation, emoji, dropped apostrophes, slang and fillers, top openers, n-grams, and elongated words. Templated mass messages inflate the n-grams. Ignore phrases that only come from one template.

Run it per register too, so chat volume doesn't drown out the rest:
```bash
python3 -I scripts/analyze.py corpus.jsonl --kind channel,group,dm
python3 -I scripts/analyze.py corpus.jsonl --kind email
python3 -I scripts/analyze.py corpus.jsonl --kind doc,wiki
python3 -I scripts/analyze.py corpus.jsonl --kind ticket,review,commit
```

### 4. Read
Numbers alone miss tone. Read real messages:
```bash
python3 -I scripts/sample.py /path/to/corpus.jsonl --limit 600            # casual + public mix
python3 -I scripts/sample.py /path/to/corpus.jsonl --kind lead --min-words 12 --maxchars 1500  # leadership posts
python3 -I scripts/sample.py /path/to/corpus.jsonl --kind email --maxchars 2000               # email
python3 -I scripts/sample.py /path/to/corpus.jsonl --kind doc,wiki --maxchars 2000            # docs / wiki
python3 -I scripts/sample.py /path/to/corpus.jsonl --kind ticket,review,commit --maxchars 1000 # tickets / reviews
```
While reading, note: distinct registers, how they open and close, how they disagree, how they ask for things, how they structure long posts, recurring phrases and jargon, and the quirks that make it sound like them. Read lead posts in full, because their structure matters.

### 5. Write the profile
Use `references/profile-template.md`. Back every claim with a stat or an example. Quote only short, work-safe lines with names swapped for `@name`. Describe private venting in general terms only.

The profile captures **how** they write, never **what** they wrote about. No PII and no company-confidential facts: unreleased plans, financials, internal metrics, customers, incidents, security details, org or HR matters. Rewrite an example quote with neutral placeholder content when the original carries any of that, and mark it as adapted. The full rules are in `references/redaction.md`.

Before saving, scan the draft and fix every hit:
```bash
python3 -I scripts/redact.py --check voice-profile.md --names names.txt --terms terms.txt --domains domains.txt
```
Then do the manual review checklist in `references/redaction.md`. Only save once the scan is clean and the checklist passes.

Save it as `voice-profile.md` in the current directory unless the user picks a path. Suggest also copying it to `~/.claude/voice-profile.md`, so draft mode finds it from any project.

### 6. Review with the user
Summarize the 5–6 most distinctive traits, say whether the profile is shareable or private, and report the redaction counts. Ask them to skim the file, especially the quoted examples, before sharing it. Then delete the working folder (corpus, stats, name/term lists) unless they want to keep it for a rebuild.

---

## Draft mode

### 1. Load the profile
Look in this order: a path the user gives → `./voice-profile.md` → `~/.claude/voice-profile.md`. Read the whole file. If none is found, say so and offer build mode.

### 2. Pick the register
Match the audience and medium to a register in the profile (casual DM, support reply, team announcement, lead post, email, doc or wiki, ticket, PR/MR description or review comment, stakeholder writing). If the profile has no section for that medium, use the closest register and say so. If it's unclear, pick the closest one and say which you used in one line. Never use a register the profile marks as private or venting unless the user explicitly asks.

### 3. Draft
- Match the profile's length for that medium. Chat is usually short; lead posts follow the profile's structure.
- Apply the surface style for that register: casing, punctuation, emoji, abbreviations, connectors. Keep recurring typos and slang out of formal registers even if the profile lists them.
- Use their signature openers, closers, and phrasing patterns, but don't overload one message with every quirk. One or two touches per short message reads natural; ten reads like parody.
- Keep their reasoning habits (for example, claim then reason, inviting pushback, crediting people).
- Don't invent facts, names, dates, numbers, or links. Use `<link>` / `@name` placeholders.
- Take content only from the user's request, never from the profile's examples. The profile is style, not source material.

### 4. Humanizer pass
Edit the draft with `references/humanizer.md` in its embedded mode. The profile is the writing sample, so where the two disagree, the profile's habits win: keep the connectors, slang, stretched words, emoji, section headers, and closers it lists. Cut the tells the profile doesn't show: not-X-but-Y contrasts, one-line closers, forced triads, inflated claims, and stock AI words. Keep every fact, name, number, and link.

### 5. Check and return
Check the draft against the profile's Do/Don't section and calibration examples. Return only the paste-ready draft. Put a chat burst on separate lines. Use emoji shortcodes for Slack. Add notes only if the user asks or something needs their input (a missing fact, an unclear register).

When rewriting the user's own draft, keep their meaning and facts exactly. Change only the voice.
