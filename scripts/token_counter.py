#!/usr/bin/env python3
"""
Token Counter (repo-wide)

- If `tiktoken` is installed, uses exact model tokenization (gpt-4o, gpt-4, gpt-3.5, etc.).
- Otherwise, falls back to a reasonable approximation (~4 chars/token avg).

Usage:
  python scripts/token_counter.py path/to/file_or_dir [--model gpt-4o] [--ext .md,.py,.json] [--json out.json] [--csv out.csv]

Examples:
  python scripts/token_counter.py . --model gpt-4o --ext .md,.py --json tokens.json
  python scripts/token_counter.py README.md
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import List, Dict, Tuple

# ----------------------------
# Optional exact tokenization
# ----------------------------
def get_encoder(model_name: str):
    try:
        import tiktoken  # type: ignore
        return tiktoken.get_encoding("cl100k_base") if "gpt-4" in model_name or "gpt-3.5" in model_name or "gpt-4o" in model_name else tiktoken.get_encoding("p50k_base")
    except Exception:
        return None

def count_tokens_exact(text: str, encoder) -> int:
    try:
        return len(encoder.encode(text))
    except Exception:
        return None  # fall back

# ----------------------------
# Fallback approximation
# ----------------------------
# Roughly: 1 token ≈ 4 chars in English (incl. spaces/punct).
# We also bias a bit using word + punctuation splits.
def count_tokens_approx(text: str) -> int:
    if not text:
        return 0
    # Heuristic blend: char-based + word-based
    chars = len(text)
    words = len(re.findall(r"\S+", text))
    # Weighted combo to better fit typical repo text (markdown/code)
    approx_by_chars = max(1, round(chars / 4.1))
    approx_by_words = max(1, round(words * 1.33))  # many words map to >1 token
    return max(approx_by_chars, approx_by_words)

# ----------------------------
# File utilities
# ----------------------------
DEFAULT_EXTS = [".md", ".markdown", ".txt", ".py", ".json", ".yaml", ".yml", ".csv", ".toml", ".ini", ".cfg", ".js", ".ts"]

def should_include(path: str, allow_exts: List[str]) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in allow_exts

def iter_files(root: str, allow_exts: List[str]):
    if os.path.isfile(root):
        if should_include(root, allow_exts):
            yield root
        return
    for base, _, files in os.walk(root):
        # skip common build/cache dirs
        if any(skip in base.lower() for skip in [".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"]):
            continue
        for f in files:
            path = os.path.join(base, f)
            if should_include(path, allow_exts):
                yield path

def read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        sys.stderr.write(f"[WARN] Could not read {path}: {e}\n")
        return ""

# ----------------------------
# Main logic
# ----------------------------
def main():
    ap = argparse.ArgumentParser(description="Count tokens for files or folders.")
    ap.add_argument("path", help="File or directory")
    ap.add_argument("--model", default="gpt-4o", help="Model name hint for exact tokenization (if tiktoken available). Default: gpt-4o")
    ap.add_argument("--ext", default=",".join(DEFAULT_EXTS), help="Comma-separated list of file extensions to include")
    ap.add_argument("--json", dest="json_out", default=None, help="Write detailed JSON report to this path")
    ap.add_argument("--csv", dest="csv_out", default=None, help="Write CSV summary to this path")
    args = ap.parse_args()

    allow_exts = [e.strip().lower() for e in args.ext.split(",") if e.strip()]
    encoder = get_encoder(args.model)

    rows: List[Dict] = []
    total_tokens = 0
    files_counted = 0

    for path in iter_files(args.path, allow_exts):
        text = read_text(path)
        if not text:
            continue

        exact = count_tokens_exact(text, encoder) if encoder else None
        approx = count_tokens_approx(text)

        tokens = exact if exact is not None else approx
        rows.append({
            "path": path,
            "tokens": tokens,
            "method": "exact" if exact is not None else "approx",
            "chars": len(text)
        })
        total_tokens += tokens
        files_counted += 1

    # Sort longest → shortest by tokens
    rows.sort(key=lambda r: r["tokens"], reverse=True)

    # Console summary
    print(f"\nToken Counter — {datetime.utcnow().isoformat()}Z")
    print(f"Root: {os.path.abspath(args.path)}")
    print(f"Model hint: {args.model} (method={'exact' if encoder else 'approx'})")
    print(f"Included extensions: {', '.join(allow_exts)}")
    print(f"Files counted: {files_counted}")
    print("-" * 70)
    top = rows[:10]
    for r in top:
        print(f"{r['tokens']:>8}  [{r['method'][:5]}]  {r['path']}")
    if len(rows) > 10:
        print(f"... (+{len(rows)-10} more)")
    print("-" * 70)
    print(f"TOTAL TOKENS ≈ {total_tokens}")
    print("Note: Install `tiktoken` for exact counts on GPT-family models:")
    print("      pip install tiktoken\n")

    # JSON output
    if args.json_out:
        report = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "root": os.path.abspath(args.path),
            "model_hint": args.model,
            "method": "exact" if encoder else "approx",
            "total_tokens": total_tokens,
            "files_counted": files_counted,
            "rows": rows
        }
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[OK] JSON report written → {args.json_out}")

    # CSV output
    if args.csv_out:
        try:
            import csv
            with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["path", "tokens", "method", "chars"])
                for r in rows:
                    w.writerow([r["path"], r["tokens"], r["method"], r["chars"]])
            print(f"[OK] CSV written → {args.csv_out}")
        except Exception as e:
            sys.stderr.write(f"[WARN] CSV write failed: {e}\n")

if __name__ == "__main__":
    main()
