# Human–AI Synchronization Framework

Research-driven concepts exploring cognitive alignment between human decision systems and AI governance architectures.  
This repo combines **conceptual blueprints** (CCRP, law-based stress tests, SMP) with **lightweight, auditable utilities** so others can reproduce and measure coherence.

> Goal: Move beyond control-based alignment toward **reciprocal, auditable synchronization** between humans and AI.

---

## Contents

- `docs/` — concept notes (CCRP, laws, governance optics), playbooks, audits
- `demos/` — tiny, runnable examples (prompt sets, scoring guides)
- `tools/` — instrumentation (token/coherence audits, report exporters)
- `lawbook-index.md` — index of demo laws (e.g., Defensiveness, Stress Reflex, Sunk Cost, Panic-as-Story)
- `README.md` — this file

---

## Core Ideas (very short)

- **CCRP** (Collapse → Coherence → Rebuild): design governance for paradox + failure, not against it.  
- **Law-based Demos**: small tests that probe predictable failure modes (defensiveness, stress reflex, sunk cost, narrative panic).  
- **SMP** (Shadow Memory Protocol): user-controlled anchors to reconstruct context each session without hidden memory.  
- **Fossils**: compressed truth artifacts; validate via multi-model triangulation (e.g., ChatGPT + Gemini).

---

## 🔍 Token/Coherence Audit (Utility)

To keep synchronization honest, we include a **Token Counter Utility** that audits files and reports approximate or exact token usage.
This helps quantify:
- **Tokens→Coherence**: fewer tokens to reconstruct context = stronger SMP anchoring.
- **Frame Integrity**: track drift when prompts grow or when stress tests (laws) are applied.
- **Convergence % (manual step)**: compare compressed summaries across models.

### Install (optional exact tokenizer)
```bash
pip install tiktoken
```

### Run
```bash
# Audit entire repo (Markdown, Python, JSON)
python tools/token_counter.py . --model gpt-4o --ext .md,.py,.json --json tokens_report.json

# Single file
python tools/token_counter.py docs/overview.md
```

### Output
- Console summary (top token-heavy files)
- `tokens_report.json` (timestamped, per-file counts)
- `tokens_report.csv` (optional) for spreadsheets/dashboards

**Notes**
- With `tiktoken` → exact counts for many OpenAI encodings.  
- Without it → uses calibrated approximation (≈ 1 token per 4 chars).

---

## Demos (suggested layout)

- `demos/law01-defensiveness/`  
- `demos/law02-stress-reflex/`  
- `demos/law03-sunk-cost/`  
- `demos/law04-panic-story/`  
Each demo includes: `prompts.json` (examples), `scoring.md` (rubric), `analysis.py` (stub to plug your model call).

---

## Ethics & Scope

This is **research-only**. Do not use the demos to manipulate people, target individuals, or perform clinical assessments. Keep all datasets redacted and consented.

---

## License

MIT — open for research and discussion. Non-commercial use preferred.
