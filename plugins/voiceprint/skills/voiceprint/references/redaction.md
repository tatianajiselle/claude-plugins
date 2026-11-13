# Redaction: PII and company-confidential information

A voice profile describes **how someone writes**. It must not carry **what they wrote about**: no personal information about anyone, and no company intel. That applies to the saved corpus too, which should only ever exist in redacted form.

Two layers:
1. **`scripts/redact.py`:** regex and list-based masking, run on the raw corpus right after collection and again (`--check`) on the finished profile.
2. **Judgment:** while reading and writing, anything sensitive the regex missed is off-limits. Don't quote it, paraphrase it, or summarize it.

## What gets removed

### Personal information (PI / PII)
| Category | Examples | Handling |
|---|---|---|
| Names of people | coworkers, contacts, DM partners, email recipients, customers | `[NAME]` / `@name`; DM sources become `dm:person-N` |
| Contact details | emails, phone numbers, street addresses, handles | `[EMAIL]`, `[PHONE]`, `[ADDRESS]` |
| Government and financial IDs | SSNs, card numbers, bank or account numbers | `[SSN]`, `[NUMBER]` |
| Account and system IDs | Slack/user IDs, UUIDs, long numeric IDs, client IDs | `[ID]` |
| Network identifiers | IP addresses | `[IP]` |
| Sensitive personal details | health, family, relationships, religion, politics, location or schedule, finances, performance or HR matters | judgment: never in the profile |

### Company-confidential information
| Category | Examples | Handling |
|---|---|---|
| Secrets | tokens, API keys, passwords, private keys, passcodes | `[SECRET]` |
| Internal hosts and links | internal domains, wiki/repo/dashboard URLs | `[INTERNAL-HOST]`, `<link>` |
| Codenames and internal names | project codenames, unreleased products, internal service names, customer or partner names | `[INTERNAL]` via `--terms`; generalized in shareable profiles |
| Work item references | ticket keys, MR/PR numbers | `[TICKET]` |
| Financials | revenue, budgets, costs, pricing, deal values | `[AMOUNT]`; judgment for figures written in words |
| Plans and strategy | roadmaps, launch dates, unannounced features, experiments and their results | judgment: never in the profile |
| Metrics and performance data | internal KPIs, adoption or conversion numbers, SLOs, incident stats | judgment |
| Org and people matters | layoffs, reorgs, promotions, hiring, compensation, leveling | judgment |
| Security and incidents | vulnerabilities, incident details, access setups, auth configs | judgment |
| Legal and compliance | legal advice, audits, compliance scope, contracts | judgment |
| Opinions about named people or teams | criticism of specific coworkers, leaders or other teams | judgment: describe the *style* of candor only |

## Building the lists

Write these to the working folder (never to the repo), one entry per line:
- **`names.txt`:** every person name seen during collection (DM partners, @mentioned people, email recipients and senders, ticket assignees, reviewers). Include first names alone and full names. Add any the user names.
- **`terms.txt`:** codenames, product and feature names that aren't public, internal system and service names, customer and partner names, team names if the user wants. Ask the user, and suggest candidates you noticed (capitalized unfamiliar words, repeated acronyms).
- **`domains.txt`:** the company's internal domains and hostnames (for example `corp.example.com`, `internal.example.net`).

## Writing example quotes safely

Examples are what make a profile useful, so keep them, but make them clean:
1. Prefer quotes whose content is already generic ("lmk if you have thoughts or concerns!").
2. If a quote's *style* is perfect but its *content* is sensitive, rewrite the content with neutral filler and keep the structure, casing, punctuation and phrasing. Mark it `(adapted)`.
   - Original: "hey team! [project] moves to friday cuz [customer] found a blocker in [system] :disappointed:"
   - Adapted: "hey team! the release moves to friday cuz QA found a blocker :disappointed:" (adapted)
3. Keep quotes short (one line, under ~25 words).
4. No quotes at all from private venting, HR, health, or personal-life messages. Describe the style in general terms.

## Shareable vs private profile

- **Shareable (default):** generalize internal names in the jargon section ("an internal messaging service", "the team's risk-scoring tool"). Keep generic industry and process vocabulary (MR, feature flag, A/B test, sprint, rollout).
- **Private (opt-in):** may list internal vocabulary the user explicitly approves, so drafts sound native. Still no PII, secrets, or confidential facts. Mark the file header `PRIVATE: do not share`.

## Manual review checklist (before saving the profile)

- [ ] `redact.py --check` reports 0 hits, or each remaining hit is confirmed harmless (for example a public product name) and the user agreed.
- [ ] No person names except the profile owner's own first name in the title.
- [ ] No company, customer, partner, or codename references (shareable) or only user-approved ones (private).
- [ ] No numbers that reveal business data (revenue, users, adoption, costs, dates of unreleased launches).
- [ ] No details of incidents, security, legal, HR, layoffs, reorgs, performance, or compensation.
- [ ] No personal-life details (health, family, location, schedule).
- [ ] Every example quote is short and work-safe, and adapted examples are marked.
- [ ] The "Who I am" line has only what the user approved.

## Limits

Regex can't recognize every name, codename, or confidential fact written in plain words. The judgment layer and the user's own review are required, not optional. When unsure whether something is sensitive, leave it out.
