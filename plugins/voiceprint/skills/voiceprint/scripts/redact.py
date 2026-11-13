#!/usr/bin/env python3
"""Strip PII and company-confidential details from a corpus or a finished profile.

Two modes:
  redact  python3 redact.py corpus.jsonl -o corpus.redacted.jsonl [options]
          Rewrites each line's text (and source) with placeholders. Writes a
          summary of what was replaced (counts only, never the values) to stderr.
  check   python3 redact.py --check voice-profile.md [options]
          Scans a text file and lists suspicious spans with line numbers, so they
          can be fixed by hand before the profile is saved or shared. Exit code 1
          if anything is found.

Options:
  --names FILE    one person name per line (coworkers, contacts) -> [NAME]
  --terms FILE    one internal term per line (codenames, customers, unreleased
                  products, internal systems) -> [INTERNAL]
  --domains FILE  one internal domain per line (corp.example.com) -> [INTERNAL-HOST]

Regex redaction is a safety net, not a guarantee. Names, codenames and
confidential facts written in plain words still need a human/model review.
Standard library only.
"""
import argparse
import collections
import json
import re
import sys

PATTERNS = [
    # secrets first so later patterns don't partially eat them
    ("SECRET", re.compile(r"\b(?:xox[abposr]-[A-Za-z0-9-]{10,}|gh[pousr]_[A-Za-z0-9]{20,}|glpat-[A-Za-z0-9_-]{20,}"
                          r"|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|sk-[A-Za-z0-9_-]{20,}"
                          r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b")),
    ("SECRET", re.compile(r"(?i)\b(?:password|passwd|pwd|secret|token|api[_-]?key|passcode)\s*[:=]\s*\S+")),
    ("SECRET", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----")),
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("URL", re.compile(r"<https?://[^>]+>|\bhttps?://[^\s>)\]]+|\bwww\.[^\s>)\]]+")),
    ("MENTION", re.compile(r"<@[A-Z0-9]+(?:\|[^>]*)?>|<!(?:here|channel|everyone)>|<#[A-Z0-9]+(?:\|[^>]*)?>")),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("CARD", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("PHONE", re.compile(r"(?<![\w.])(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?![\w.])")),
    ("IP", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")),
    ("UUID", re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")),
    ("ID", re.compile(r"\b(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{20,}\b")),
    ("ID", re.compile(r"\b\d{9,}\b")),
    ("ID", re.compile(r"\b[UWCDG](?=[A-Z0-9]*\d)[A-Z0-9]{8,11}\b")),
    ("TICKET", re.compile(r"\b(?!(?:UTF|SHA|ISO|RFC|COVID|TLS|SSL|MP|IPV|HTTP|CVE|AES|RSA|ECMA|TCP|UDP|IEEE|P|Q|H)-)[A-Z][A-Z0-9]{1,9}-\d{1,6}\b")),
    ("MONEY", re.compile(r"(?i)[$€£]\s?\d[\d,.]*(?:\s?(?:k|m|mm|b|bn|million|billion))?\b|\b\d[\d,.]*\s?(?:usd|dollars)\b")),
    ("ADDRESS", re.compile(r"\b\d{1,6}\s+(?:[A-Z][a-z]+\s){1,3}(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Ln|Lane|Way|Ct|Court|Pl|Place)\b\.?")),
]

PLACEHOLDER = {
    "SECRET": "[SECRET]", "EMAIL": "[EMAIL]", "URL": "<link>", "MENTION": "@name", "SSN": "[SSN]",
    "CARD": "[NUMBER]", "PHONE": "[PHONE]", "IP": "[IP]", "UUID": "[ID]", "ID": "[ID]",
    "TICKET": "[TICKET]", "MONEY": "[AMOUNT]", "ADDRESS": "[ADDRESS]",
    "NAME": "[NAME]", "INTERNAL": "[INTERNAL]", "INTERNAL-HOST": "[INTERNAL-HOST]",
}


def read_list(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        return sorted({l.strip() for l in f if l.strip() and not l.startswith("#")}, key=len, reverse=True)


def word_pattern(terms):
    if not terms:
        return None
    return re.compile(r"(?i)(?<![\w-])(?:" + "|".join(re.escape(t) for t in terms) + r")(?:'s)?(?![\w-])")


def build(names, terms, domains):
    pats = []
    if domains:
        pats.append(("INTERNAL-HOST", re.compile(r"(?i)\b[\w.-]*(?:" + "|".join(re.escape(d) for d in domains) + r")\b")))
    pats.extend(PATTERNS)
    for label, terms_ in (("INTERNAL", terms), ("NAME", names)):
        p = word_pattern(terms_)
        if p:
            pats.append((label, p))
    return pats


def redact_text(text, pats, counts):
    for label, pat in pats:
        text, n = pat.subn(PLACEHOLDER[label], text)
        if n:
            counts[label] += n
    return text


def redact_source(src, alias):
    m = re.match(r"^(\w+:)?(dm|chat):(.+)$", src or "")
    if not m:
        return src
    key = m.group(3).strip().lower()
    alias.setdefault(key, "person-%d" % (len(alias) + 1))
    return (m.group(1) or "") + m.group(2) + ":" + alias[key]


def run_redact(a, pats):
    counts, alias, n = collections.Counter(), {}, 0
    with open(a.input, encoding="utf-8") as f, open(a.output, "w", encoding="utf-8") as out:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line) if a.input.endswith(".jsonl") else {"text": line.rstrip("\n")}
            for field in ("text", "subject", "heading"):
                if obj.get(field):
                    obj[field] = redact_text(obj[field], pats, counts)
            if obj.get("source"):
                obj["source"] = redact_text(redact_source(obj["source"], alias), pats, counts)
            out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            n += 1
    summary = {"lines": n, "replacements": dict(counts), "dm_partners_aliased": len(alias)}
    print(json.dumps(summary, indent=1), file=sys.stderr)


def run_check(a, pats):
    hits = 0
    allowed = set(PLACEHOLDER.values())
    with open(a.check, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            for label, pat in pats:
                for m in pat.finditer(line):
                    if m.group(0) in allowed:
                        continue
                    hits += 1
                    span = m.group(0)
                    shown = span if label not in ("SECRET", "CARD", "SSN") else span[:4] + "…"
                    print(f"{a.check}:{i}: {label}: {shown}")
    print(f"{hits} suspicious span(s)", file=sys.stderr)
    sys.exit(1 if hits else 0)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", nargs="?")
    p.add_argument("-o", "--output")
    p.add_argument("--check", help="scan a text file instead of redacting")
    p.add_argument("--names")
    p.add_argument("--terms")
    p.add_argument("--domains")
    a = p.parse_args()
    pats = build(read_list(a.names), read_list(a.terms), read_list(a.domains))
    if a.check:
        run_check(a, pats)
    elif a.input and a.output:
        run_redact(a, pats)
    else:
        p.error("give INPUT -o OUTPUT to redact, or --check FILE to scan")


if __name__ == "__main__":
    main()
