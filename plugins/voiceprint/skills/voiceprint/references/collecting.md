# Collecting writing samples

Goal: build a corpus of the person's own writing as `raw.jsonl`, one object per line. Redact it into `corpus.jsonl` right away (see `redaction.md`) and delete the raw file:

```json
{"text": "hey team! quick update on ...", "source": "slack:#proj-launch", "kind": "channel", "ts": "2026-10-14T16:02:11Z"}
```

- `text`: the writing as-is. Keep the original casing, punctuation, emoji shortcodes, and typos.
- `source`: where it came from, prefixed by tool: `slack:#channel`, `slack:dm:<first name>`, `teams:<chat>`, `gmail`, `outlook`, `gdoc:<title>`, `confluence:<page>`, `jira:<KEY-123>`, `github:<repo>#<n>`, `gitlab:<project>!<n>`, `linear:<id>`, `paste`.
- `kind`: the register bucket. It drives how the text is analyzed and which profile sections it feeds.

| kind | Use for |
|---|---|
| `channel` | Slack / Teams public or private channel messages |
| `group` | group DMs / group chats |
| `dm` | 1:1 DMs / chats |
| `lead` | posts in projects or channels the person leads |
| `email` | email bodies they wrote |
| `doc` | Google Docs / Word / long-form docs (one paragraph or section per line) |
| `wiki` | Confluence / Notion-style pages |
| `ticket` | issue or ticket descriptions and comments (Jira, Linear, Asana, monday) |
| `review` | PR/MR descriptions and code review comments |
| `commit` | commit messages |
| `post` | blog posts, announcements outside chat |
| `other` | anything else |

- `ts`: optional timestamp.

Write the raw corpus to a temporary working folder (a scratchpad or `/tmp/voiceprint/`), never into the profile repo or anything that gets shared. While collecting, note every person name you see (DM partners, mentions, recipients, assignees, reviewers) for `names.txt`, plus candidate codenames and internal terms for `terms.txt`.

Only include text **the person wrote**. Leave out other people's replies, bot or automated messages, templates they didn't write (for example ticket templates, PR template headings), forwarded mail, and quoted text. When someone quotes another person and replies, keep only their reply.

## Before collecting: settle the scope with the user

Ask, and get answers before pulling anything:
1. **Sources.** Check which connectors are connected in this session, list them, and let the user pick. Text they paste or attach always works. Don't ask them to connect anything they didn't choose.
2. **Time window.** The default is the last 30 days for chat and the last 90 days for email, docs, tickets and reviews (lower volume). Go back further if a source is thin.
3. **What to leave out.** Offer to show their most frequent DM or email partners by count, so they can pick close or personal threads to skip. Respect any person, channel, folder or label they name.
4. **Lead channels or projects** where they post as the lead. Pull these with no time limit.
5. **Specific docs** they're proud of or consider typical. A few hand-picked docs beat many random ones.

Then pull each source and give short progress notes.

## Tool names

Connector tool names vary by host (claude.ai connectors, local MCP servers, enterprise gateways). Find the right tool by what it does (search, read, list) instead of assuming a name. If a needed capability is missing (for example, search works but there's no full-text read), say so and use what's available.

---

## Slack (Slack MCP connector)

1. **Find the user's Slack ID** with the user or profile lookup tool, or ask for it.
2. **Search their messages** and page through every result:
   - `from:<@USERID> after:YYYY-MM-DD` (or `from:me` if supported)
   - Sort by timestamp if possible. Keep paging until results run out.
   - If results are capped per query, split the window by week (`after:` + `before:`).
3. **Lead channels:** `from:<@USERID> in:#channel-name` with no date filter. If the channel name is unknown, search `from:<@USERID> <project keyword>` and count which channels come back.
4. **Threads:** when a lead post has replies, read the thread and keep the user's own replies.
5. **`kind`:** set from the channel type (DM, group DM, channel). Use `lead` for lead channels.
6. **Full text:** if search returns truncated previews, fetch full text via the channel or thread read tool for messages over ~40 words.

Don't fall back to scraping the Slack web app if the connector isn't available.

## Microsoft Teams (Microsoft 365 connector)

Same approach as Slack. Search or list chats and channel messages sent by the user in the window, and label `dm` / `group` / `channel` / `lead`. Use the source prefix `teams:`.

## Email (Gmail, Outlook via Microsoft 365)

1. Search **sent mail** only: Gmail `in:sent after:YYYY/MM/DD`, Outlook the Sent Items folder with a date filter.
2. For each message, keep **only the body the user wrote**:
   - Cut quoted history (`>` lines, "On <date>, <name> wrote:", "From: ... Sent: ...", "-----Original Message-----").
   - Cut signatures (lines after `--`, or a repeated block at the end of many emails), legal footers, and calendar boilerplate.
3. Skip auto-generated mail (calendar accepts, auto-replies, notifications).
4. One corpus line per email (`kind: email`). Keep the subject line as a separate field `subject` if useful. Subjects show their headline style.
5. If there are hundreds, sample across recipients and lengths instead of taking only the newest.

## Google Docs / Drive (and Word/OneDrive via Microsoft 365)

1. Ask for specific docs first. Otherwise search files **owned by the user** and modified in the window (types: docs; skip sheets and slides unless they have real prose).
2. Read each doc's full text. Only use docs the user authored, or sections clearly theirs. Shared docs with many editors are noisy.
3. Split into paragraphs or sections, one line each (`kind: doc`), and keep headings with a `heading` field or as their own lines. Heading and section structure is part of their doc voice.
4. Skip pasted content (tables of data, copied specs, code blocks, meeting notes they didn't write).

## Confluence (Atlassian connector)

Search pages **created by** the user (CQL `creator = currentUser()` or the user's account ID, plus a date filter). Read the page bodies and split by section (`kind: wiki`). Also pull the user's footer and inline **comments** as `kind: wiki` with `source: confluence:<page>#comment`. Comments are closer to their chat voice.

## Jira (Atlassian connector)

1. Issues **reported by** the user in the window (JQL `reporter = currentUser() AND created >= -90d`). Use the description text (`kind: ticket`).
2. **Comments by** the user: JQL can't filter by comment author everywhere. Read comments on issues they reported, are assigned to, or recently viewed (`reporter = currentUser() OR assignee = currentUser() OR issue in issueHistory()`), and keep the ones they authored.
3. Strip issue templates and auto-generated fields. Keep their own words.

## Linear / Asana / monday

Same as Jira: issues or tasks they created plus comments they wrote, `kind: ticket`, source prefixed with the tool name.

## GitHub / GitLab

1. **PR/MR descriptions** they authored in the window: GitHub `author:<user> type:pr`, GitLab merge requests with `author_username`. Strip PR template headings and checklists they didn't write (`kind: review`).
2. **Review comments** they left on others' PRs/MRs (`kind: review`). This is often the clearest view of how they give feedback.
3. **Commit messages** (optional, `kind: commit`): subject line + body, skipping merge commits and bot commits.
4. Drop code blocks and diffs. Keep the prose around them.

## Glean (enterprise search)

Useful as one entry point across Slack, Docs, Confluence, Jira and email when the person has it. Filter to documents or messages **authored by** the user, then fetch full content for each hit (search results are often snippets). Label `kind` by the underlying source app. Watch for duplicates if you also pulled that app directly.

## Pasted text and files

- **Pasted text in chat:** split on blank lines or one message per line. Ask if the boundaries are unclear. `source: paste`.
- **Files:** `.txt`, `.md`, `.eml`, `.mbox`, `.csv`, `.json`, `.docx`, `.pdf`. Extract text and apply the email or doc cleanup rules above.
- **Slack export** (`channel/YYYY-MM-DD.json`): keep entries whose `user` matches their ID and use `text`.

---

## How much is enough

- Chat: aim for ~300+ messages.
- Long-form (email/docs/wiki): aim for ~5,000+ words.
- Tickets/reviews: ~30+ items.

A source below these levels still helps. In the profile, mark the registers it informs as **low confidence**.

## Balance

If one source dominates (for example 3,000 Slack messages versus 20 emails), analyze each `kind` separately, using `--kind` on both scripts, so the email and doc registers aren't drowned out by chat stats.

## Privacy

- Redact PII and company-confidential details immediately after collection with `scripts/redact.py`, following `references/redaction.md`. Only the redacted corpus is used for analysis, and the raw file is deleted.
- Keep everything local. Never send corpus content to external services or URLs.
- Offer to delete the working folder (corpus, stats, name and term lists) when done.
