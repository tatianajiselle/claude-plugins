#!/usr/bin/env python3
"""Dedupe a corpus and print a readable sample for qualitative review.

Drops near-duplicate templated messages (same text after the first few words),
trims long messages, and prints them grouped by kind/source so the model can
read the person's real phrasing. Standard library only.

Usage: python3 sample.py corpus.jsonl [--limit 600] [--maxchars 500] [--kind lead]
"""
import argparse
import json
import random
import re


def load(path):
    with open(path, encoding="utf-8") as f:
        if path.endswith(".jsonl"):
            return [json.loads(l) for l in f if l.strip()]
        return [{"text": l.rstrip("\n")} for l in f if l.strip()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("corpus")
    p.add_argument("--limit", type=int, default=600)
    p.add_argument("--maxchars", type=int, default=500)
    p.add_argument("--kind", help="comma-separated kinds to include, e.g. lead or email,doc")
    p.add_argument("--min-words", type=int, default=0)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args()
    seen, out = set(), []
    for m in load(a.corpus):
        t = re.sub(r"\s+", " ", m.get("text", "")).strip()
        if not t or (a.kind and m.get("kind") not in a.kind.split(",")) or len(t.split()) < a.min_words:
            continue
        key = re.sub(r"^\S+\s+\S+\s+", "", t.lower())[:60]
        if key in seen:
            continue
        seen.add(key)
        tag = m.get("kind", "msg") + ("/" + m["source"] if m.get("source") else "")
        out.append(f"{tag}> {t[:a.maxchars]}{'…' if len(t) > a.maxchars else ''}")
    if len(out) > a.limit:
        random.Random(a.seed).shuffle(out)
        out = out[:a.limit]
    print(f"# {len(out)} messages (deduped)")
    print("\n".join(out))


if __name__ == "__main__":
    main()
