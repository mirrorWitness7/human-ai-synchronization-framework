#!/usr/bin/env python3
"""
Token Counter Utility
- Counts tokens in files for audit (approximate or exact if `tiktoken` installed)
- Helps measure Tokens→Coherence and track prompt bloat/drift

Usage:
  python tools/token_counter.py . --model gpt-4o --ext .md,.py,.json --json tokens_report.json --csv tokens_report.csv
"""
import os
import sys
import argparse
import json
import csv
from datetime import datetime

# Optional exact tokenization
try:
    import tiktoken
except Exception:
    tiktoken = None

def approx_token_count(text: str) -> int:
    # Calibrated approximation: ~4 chars/token average for English-like text
    # Add small overhead for newlines/markdown
    return max(1, int((len(text) + text.count("\n")) / 4))

def exact_token_count(text: str, model: str = "gpt-4o") -> int:
    if tiktoken is None:
        return approx_token_count(text)
    try:
        enc = tiktoken.get_encoding("cl100k_base")
    except Exception:
        # Fallback to model lookup if available
        try:
            enc = tiktoken.encoding_for_model(model)
        except Exception:
            return approx_token_count(text)
    return len(enc.encode(text))

def scan_files(root: str, exts: list[str]) -> list[str]:
    paths = []
    for base, _, files in os.walk(root):
        for fn in files:
            if not exts:  # no filter → include all
                paths.append(os.path.join(base, fn))
            else:
                if any(fn.lower().endswith(e.lower()) for e in exts):
                    paths.append(os.path.join(base, fn))
    return sorted(paths)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file or folder to audit")
    ap.add_argument("--model", default="gpt-4o", help="tokenizer model hint (if tiktoken available)")
    ap.add_argument("--ext", default=".md,.py,.json", help="comma-separated file extensions to include (blank = all)")
    ap.add_argument("--json", dest="json_out", default="", help="optional JSON output path")
    ap.add_argument("--csv", dest="csv_out", default="", help="optional CSV output path")
    args = ap.parse_args()

    root = args.path
    exts = [e.strip() for e in args.ext.split(",") if e.strip()] if args.ext is not None else []

    paths = []
    if os.path.isdir(root):
        paths = scan_files(root, exts)
    elif os.path.isfile(root):
        paths = [root]
    else:
        print(f"[!] Path not found: {root}")
        sys.exit(1)

    results = []
    total_tokens = 0
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
        except Exception as e:
            print(f"[skip] {p}: {e}")
            continue
        tokens = exact_token_count(txt, args.model)
        total_tokens += tokens
        results.append({
            "path": p,
            "tokens": tokens,
            "bytes": len(txt.encode('utf-8', errors='ignore'))
        })

    results.sort(key=lambda r: r["tokens"], reverse=True)

    # Console summary
    print(f"\n== Token Audit ({datetime.utcnow().isoformat()}Z) ==")
    print(f" Scanned: {len(results)} files\n Total tokens: {total_tokens:,}\n")
    print(" Top files:")
    for r in results[:10]:
        print(f"  - {r['path']}  ::  {r['tokens']:,} tokens")

    payload = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "model_hint": args.model,
        "total_tokens": total_tokens,
        "files": results
    }

    if args.json_out:
        try:
            with open(args.json_out, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"\n[✓] JSON written → {args.json_out}")
        except Exception as e:
            print(f"[x] JSON write failed: {e}")

    if args.csv_out:
        try:
            with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["path", "tokens", "bytes"])
                for r in results:
                    w.writerow([r["path"], r["tokens"], r["bytes"]])
            print(f"[✓] CSV written  → {args.csv_out}")
        except Exception as e:
            print(f"[x] CSV write failed: {e}")

if __name__ == "__main__":
    main()
