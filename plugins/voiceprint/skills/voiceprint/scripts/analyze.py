#!/usr/bin/env python3
"""Compute writing-style stats from a corpus of one person's messages.

Input: a .jsonl file (one {"text": ..., "source": ..., "kind": ...} per line)
or a .txt file (one message per line; blank lines are skipped).
Output: JSON stats on stdout. Standard library only.

Usage: python3 analyze.py corpus.jsonl [--top 60] [--kind email,doc]
"""
import argparse
import collections
import json
import re
import statistics
import sys

EMOJI_CODE = re.compile(r":[a-z0-9_+\-]+:")
EMOJI_UNI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
URL = re.compile(r"<https?://[^>]+>|https?://\S+")
MENTION = re.compile(r"<@[A-Z0-9]+>|@\w+")
CODE = re.compile(r"```.*?```", re.S)
WORD = re.compile(r"[a-z']+")
STOP = set("""a an the and or but if of to in on at for with by from as is are was were be been
it this that these those i you he she we they me my your our their them his her its so do does did
not no yes can will would should could have has had just than then there here what when where who
how which about into out up down over also all any some more most very""".split())
CONTRACTIONS = ["im", "ive", "ill", "dont", "cant", "didnt", "isnt", "wasnt", "youre", "theyre",
                "thats", "whats", "doesnt", "wont", "havent", "wouldnt", "couldnt", "shouldnt", "lets"]
SLANG = ["lol", "lmao", "haha", "hahaha", "omg", "idk", "tbh", "imo", "fwiw", "btw", "lmk", "ngl",
         "fyi", "tysm", "ty", "np", "rn", "u", "ur", "cuz", "tho", "prob", "gonna", "wanna", "kinda",
         "yeah", "yep", "yup", "nope", "ok", "okay", "kk", "hmm", "ooh", "ugh", "yay", "woohoo",
         "awesome", "cool", "nice", "sweet", "perfect", "totally", "super", "literally", "honestly",
         "actually", "basically", "definitely", "xd"]


def load(path):
    msgs = []
    with open(path, encoding="utf-8") as f:
        if path.endswith(".jsonl"):
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if obj.get("text"):
                    msgs.append(obj)
        else:
            msgs = [{"text": l.rstrip("\n")} for l in f if l.strip()]
    return msgs


def clean(t):
    return re.sub(r"\s+", " ", MENTION.sub(" ", URL.sub(" ", CODE.sub(" ", t)))).strip()


def ratio(n, d):
    return round(n / d, 3) if d else 0.0


def ngrams(words, n):
    return zip(*(words[i:] for i in range(n)))


def stats(msgs, top):
    texts = [m["text"] for m in msgs]
    cleaned = [clean(t) for t in texts]
    cleaned = [c for c in cleaned if c]
    n = len(cleaned)
    lengths = sorted(len(c.split()) for c in cleaned)
    words_all, first2 = [], collections.Counter()
    bi, tri = collections.Counter(), collections.Counter()
    for c in cleaned:
        ws = WORD.findall(c.lower())
        words_all.extend(ws)
        if ws:
            first2[" ".join(ws[:2])] += 1
        bi.update(" ".join(g) for g in ngrams(ws, 2))
        tri.update(" ".join(g) for g in ngrams(ws, 3))
    wf = collections.Counter(words_all)
    joined = "\n".join(cleaned)
    emoji = collections.Counter(EMOJI_CODE.findall("\n".join(texts)))
    emoji.update(EMOJI_UNI.findall("\n".join(texts)))
    apos = {w: wf[w] for w in CONTRACTIONS if wf[w]}
    by_kind = collections.Counter(m.get("kind", "unknown") for m in msgs)
    by_source = collections.Counter(m.get("source", "unknown") for m in msgs)
    return {
        "messages": n,
        "by_kind": dict(by_kind),
        "top_sources": by_source.most_common(25),
        "length_words": {
            "median": statistics.median(lengths) if lengths else 0,
            "p90": lengths[int(len(lengths) * 0.9)] if lengths else 0,
            "max": lengths[-1] if lengths else 0,
        },
        "share_starting_lowercase": ratio(sum(1 for c in cleaned if c[0].islower()), n),
        "share_ending_period": ratio(sum(1 for c in cleaned if c.endswith(".")), n),
        "share_ending_question": ratio(sum(1 for c in cleaned if c.endswith("?")), n),
        "share_with_exclamation": ratio(sum(1 for c in cleaned if "!" in c), n),
        "share_with_emoji": ratio(sum(1 for t in texts if EMOJI_CODE.search(t) or EMOJI_UNI.search(t)), len(texts)),
        "share_multi_sentence": ratio(sum(1 for c in cleaned if re.search(r"[.!?]\s+\S", c)), n),
        "capital_I_vs_lower_i": [len(re.findall(r"\bI\b", joined)), len(re.findall(r"\bi\b", joined))],
        "ellipses": len(re.findall(r"\.\.+", joined)),
        "double_dash": len(re.findall(r"\s--\s", joined)),
        "em_dash": joined.count("—"),
        "stacked_punct": len(re.findall(r"[!?]{2,}", joined)),
        "elongated_words": collections.Counter(w for w in words_all if re.search(r"([a-z])\1\1", w)).most_common(20),
        "dropped_apostrophe_counts": apos,
        "apostrophe_contractions": len(re.findall(r"\b\w+['\u2019](m|ve|ll|t|re|s|d)\b", joined.lower())),
        "slang_and_fillers": {w: wf[w] for w in SLANG if wf[w]},
        "top_content_words": [(w, c) for w, c in wf.most_common(top * 4) if w not in STOP][:top],
        "top_openers": first2.most_common(top),
        "top_bigrams": [(g, c) for g, c in bi.most_common(top * 3) if not all(x in STOP for x in g.split())][:top],
        "top_trigrams": tri.most_common(top),
        "top_emoji": emoji.most_common(30),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("corpus")
    p.add_argument("--top", type=int, default=60)
    p.add_argument("--kind", help="comma-separated kinds to include, e.g. email,doc")
    a = p.parse_args()
    msgs = load(a.corpus)
    if a.kind:
        keep = set(a.kind.split(","))
        msgs = [m for m in msgs if m.get("kind") in keep]
    if not msgs:
        sys.exit("no messages found in " + a.corpus)
    json.dump(stats(msgs, a.top), sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
