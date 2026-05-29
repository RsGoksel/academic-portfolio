# CONTEXT — Paper 03: LLM Classification of Ransomware Leak-Site Posts

> **Status:** Raw findings dump (2026-05-28). Do not delete. PAPER.md derives from this.

## Proposed contribution (methodology + small evaluation)

Apply frontier LLMs as multi-task classifiers over ransomware leak-site posts to extract structured features:

1. **Victim industry** (NAICS-aligned: Manufacturing, Healthcare, Financial Services, Education, Public Administration, Retail, Professional Services, Energy, Other)
2. **Data category claimed leaked** (PII, PHI, Financial Records, Source Code, Email Archives, Trade Secrets, Operational Data, Mixed/Unspecified)
3. **Negotiation status implied by post** (Initial threat / Countdown active / Data published / Negotiation succeeded — implied by post being taken down / Unknown)
4. **Approximate victim size signal** (Mentions revenue / employee count / industry rank; or Unknown)
5. **Geographic indicator of victim** (Country mentioned or inferable; or Unknown)

Output is a structured JSON record per post. Target use: a research-grade longitudinal dataset of ransomware ecosystem behavior, currently fragmented across vendor blog posts and one-off academic snapshots.

## Why this is feasible without new collection

Public academic mirrors of leak-site corpora exist and are already used in research:
- **`Ransomware.live`** publishes timestamped JSON of every observed leak-site post (CL0P, LockBit, AlphV/BlackCat, Akira, etc.) with the original post URL and HTML snapshot
- **Recorded Future** and **Mandiant** publish periodic snapshot dumps
- Academic mirrors at **CrySys Lab (BME)**, **Cambridge Cybercrime Centre** (DDoS-resistant archive, restricted academic access via signed DPA)
- **DarkOwl Vision** has academic licensing

This means the research can be done without us operating a fresh crawler — we work over a curated, ethics-cleared corpus that someone else captured.

## Why LLMs (vs. classical NLP)

- Posts are heterogeneous: some are templated press-release format, some are ASCII-art bravado, some are pure data dumps with metadata. Classical TF-IDF + logistic regression handles the first but not the others.
- Negotiation-status inference requires multi-step reading ("Countdown timer at 0; data appears in this post" → status = "Data published"). LLM zero-shot or few-shot is well-suited.
- Industry classification benefits from world knowledge that LLMs encode (knowing what "XYZ Corp" likely does without explicit signals in the post).

## Task design

- **Prompt format:** Structured output (JSON Schema) with explicit field constraints and an "Unknown" option per field. Reject hallucination by forcing "Unknown" when no in-text evidence exists.
- **Models:** Claude Sonnet 4.6 (cost-efficient primary), Claude Opus 4.7 (head-to-head ceiling), GPT-5 (head-to-head), Llama-3.3-70B or Qwen-2.5-72B (self-hosted open-source baseline).
- **Few-shot:** 3-5 hand-labeled examples per industry, included in the prompt.
- **Cross-validation:** Two-pass agreement — each model classifies independently, disagreements flagged for human review.

## Evaluation

- **Ground truth:** 1000 posts from `Ransomware.live` 2024-2025 window, two annotators label each (κ ≥ 0.7 target). Posts pre-filtered to exclude any actual leaked content payload (work only on the metadata + post text).
- **Metrics:** Per-field accuracy, macro-F1, error analysis by ransomware group.
- **Drift study:** Apply best model to historical posts (2020-2024) without retraining, report performance over time. Hypothesis: post conventions stabilize after a group's first ~30 posts.

## Outputs beyond the paper

A reusable annotation tool + open dataset (post-IRB approval and DPA negotiation with whichever mirror provides source) is a separate, parallel contribution.

## Why publishable

Existing academic work on ransomware leak sites:
- **Meland et al. 2020** (qualitative analysis of dark-web ransomware ecosystem)
- **Yilmaz et al. 2024** (quantitative study but uses manual coding, not LLMs, N=200)
- **Sophos 2023** annual State of Ransomware (industry report, no methodology rigor)

Nobody has published systematic LLM-based structured extraction over a 4-figure-N corpus with reproducible prompts. This is a clean methodology + dataset paper for **APWG eCrime, IEEE S&P workshops, or USENIX Security**.

## What our session contributed materially

- Confirmed OnionClaw's `--mode ransomware` includes 3 leak sites in its seed list (audited in T1b) — so if a future researcher wants to refresh the corpus rather than rely on existing mirrors, OnionClaw provides a starting set. (We did NOT exercise this mode in T4 — strictly excluded by the ethics catalog.)
- Pipeline architecture: OnionClaw fetch → HTML strip → LLM classifier → STIX 2.1 export (`sicry_to_stix` exists in v2.3.0). Demonstrates the full chain is buildable from open-source pieces.

## Ethics constraints (non-negotiable)

- **Never publish raw post text** in any paper or dataset release — paraphrase only.
- **No victim re-identification.** Anonymize victim names; geographic info aggregated to country only.
- **No interaction with ransomware operators.** Read-only access to mirrors; no engagement with the leak-site infrastructure itself.
- **DPA / IRB before corpus access.** Cambridge Cybercrime Centre archive requires signed DPA; most İTÜ ethics committees would require equivalent.
- **Embargo period.** Post-publication, the source corpus identifiers may be restricted to verified academic requesters via signed Code of Conduct.

## Limits

- **Selection bias.** Mirrors only see posts that survived the leak-site's own operational uptime. Posts taken down before crawler observation are missing.
- **Group-specific bias.** LockBit and CL0P dominate the visible corpus (~60% combined); rarer groups underrepresented.
- **Language bias.** Most posts are English; some are Russian or Spanish. LLM performance varies by language.
- **Adversarial framing.** Some groups deliberately mislead about victim identity or data size. We measure CLAIMED features, not ground-truth.

## Pre-2022 prior art for citation in PAPER.md

- Christin 2013 "Traveling the Silk Road" (foundational dark-web measurement methodology)
- Soska & Christin 2015 "Measuring the Longitudinal Evolution of the Online Anonymous Marketplace Ecosystem" (longitudinal methodology template)
- Moore & Rid 2016 "Cryptopolitik and the Darknet" (typology baseline)
- Hutchings & Holt 2014 "Crime Script for Online Stolen Data Markets"
- Ransomware-specific pre-2022: Connolly & Wall 2019, Cartwright et al. 2019, Meland et al. 2020
- LLM classification pre-2022: Brown et al. 2020 (GPT-3 few-shot), Wei et al. 2021 (Chain of Thought)
- Structured output / few-shot for NLP tasks: Sanh et al. 2021 (T0), Wang et al. 2022 (Super-NaturalInstructions)
