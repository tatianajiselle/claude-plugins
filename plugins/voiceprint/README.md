# voiceprint

A Claude skill that learns how you write and then drafts messages that sound like you.

1. **Build:** point it at your own writing through whatever connectors you have, or paste text and attach files. It measures your style per register, reads a sample of real writing, and writes a portable `voice-profile.md`.
2. **Draft:** ask for a Slack message, email, doc section, ticket, PR description, or review comment "in my voice", and it writes from that profile.

## Supported sources

All optional. Use whichever you have connected.

| Source | What it captures |
|---|---|
| Slack | Chat voice, team announcements, lead posts |
| Microsoft Teams (Microsoft 365) | Same as Slack, for Teams orgs |
| Gmail / Outlook (Microsoft 365) | Email voice: greetings, sign-offs, formality with execs vs peers |
| Google Docs / Drive (or Word/OneDrive) | Long-form: how you open a doc, structure arguments, present tradeoffs |
| Confluence | Wiki pages and page comments |
| Jira / Linear / Asana / monday | Ticket descriptions and comments |
| GitHub / GitLab | PR/MR descriptions, review comments, commit messages |
| Glean | One search across many of the above, filtered to what you wrote |
| Pasted text / files | `.txt`, `.md`, `.eml`, `.mbox`, `.docx`, `.pdf`, Slack export JSON |

The skill finds connector tools by what they do (search, read) rather than by exact name, so it works with claude.ai connectors, local MCP servers, or enterprise gateways.

The profile covers:
- the numbers: message length, casing, punctuation, emoji rate
- your registers (casual chat, support, announcements, lead posts, stakeholder writing, email, docs, tickets, code review)
- the structure of your leadership posts
- signature phrases, typing quirks, sentence structure, jargon
- do/don't rules and calibration examples

## Install

**Claude Code:** at the prompt of a session:
```
/plugin install voiceprint --marketplace tatianajiselle/claude-plugins
```
Answer `y` to add the marketplace, then pick a scope.

**claude.ai:** zip the `skills/voiceprint` folder and upload it as a custom skill in Settings.

Requirements: Python 3 (standard library only). For live sources, the matching connector or MCP server, with read and search access to your own content.

## Use

Build your profile:
```
build my voice profile from the last month of my slack. skip my DMs with my partner and best friend.
my lead channels are #proj-onboarding and #proj-search-v2
```
```
learn how I write from my sent email and google docs from the last 3 months, plus my jira comments
and gitlab MR reviews
```
```
learn how I write from these emails (attached) and the paragraphs below
```

Draft with it:
```
write this in my voice: tell the team the release moved to friday because QA found a blocker
```
```
draft a kickoff post for the build team like I usually do
```
```
make this sound like me: <paste draft>
```
```
write the PR description for this branch in my voice
```

Draft mode looks for the profile at a path you give, then `./voice-profile.md`, then `~/.claude/voice-profile.md`.

## Scripts

Both scripts are standard-library Python and can be run on their own.

| Script | What it does |
|---|---|
| `scripts/analyze.py corpus.jsonl [--kind email,doc]` | Style stats as JSON: length, casing, punctuation, emoji, slang, openers, n-grams |
| `scripts/sample.py corpus.jsonl [--kind lead]` | Deduped, readable sample for the reading pass |
| `scripts/redact.py raw.jsonl -o corpus.jsonl [--names --terms --domains]` | Masks PII and company-confidential details; `--check FILE` scans a profile and lists anything left |

The corpus format is JSONL with `text`, `source`, `kind`, and an optional `ts` (see `skills/voiceprint/references/collecting.md`). Plain `.txt` with one message per line also works.

## Privacy

- **PII and company intel are stripped.** Right after collection, `redact.py` masks names, emails, phones, addresses, IDs, secrets and tokens, internal hosts and links, ticket numbers, money amounts, and any codenames or customer names you list. Only the redacted copy is analyzed, and the raw copy is deleted. The finished profile is scanned again and reviewed against a checklist (no plans, financials, metrics, incidents, HR or org matters, or personal details) before it's saved. See `skills/voiceprint/references/redaction.md`.
- Profiles are **shareable** by default, with internal names generalized. You can opt into a **private** profile that keeps internal vocabulary you approve, but never PII or confidential facts.
- Everything runs locally in your Claude session. The skill never sends your messages to outside services.
- Only your own messages are collected, and you choose what to leave out before anything is pulled.
- The profile quotes short, work-safe examples and replaces names with `@name`. Review it before sharing, because it is built from your real messages.
- Check your workplace's policy on exporting or analyzing workplace data (Slack, email, docs) before using it on a work account.

## Layout

```
skills/voiceprint/
├── SKILL.md                      # build + draft instructions
├── references/
│   ├── collecting.md             # corpus format, per-connector steps, privacy
│   ├── redaction.md              # PII + company-intel rules, review checklist
│   ├── profile-template.md       # profile structure
│   ├── humanizer.md              # AI-writing tells to cut (vendored, MIT)
│   └── humanizer-LICENSE
└── scripts/
    ├── analyze.py                # style stats
    ├── redact.py                 # PII / confidential masking + profile scan
    └── sample.py                 # deduped reading sample
```

## Credits

`references/humanizer.md` is vendored from [blader/humanizer](https://github.com/blader/humanizer) (MIT, see `references/humanizer-LICENSE`).
