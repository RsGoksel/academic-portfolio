# Paper 03 — Structured Classification of Ransomware Leak-Site Posts with LLMs

> **ResearchGate publication:** _(link pending upload)_

A methodology and pre-registered evaluation for extracting five structured
fields (victim industry, data category, negotiation status, victim-size
signal, geographic indicator) from ransomware leak-site posts using
large language models in JSON-schema-constrained output mode. Sources from
a public academic mirror under a signed data-processing agreement; no raw
post text is republished.

## What is in this directory

| Path | Content |
|---|---|
| `figures/fig1_pipeline.mmd` / `.png` | Mirror corpus → preprocessing → primary + secondary classifier → human review → dataset |
| `figures/fig2_extraction_fields.mmd` / `.png` | Field-value enumeration for the five-field schema |
| `figures/fig3_two_pass_agreement.mmd` / `.png` | Two-pass agreement sequence with human-review routing |
| `figures/fig4_drift_study_design.txt` | Window design for the frozen-model drift study (2020-2025) |
| `references/_style_notes.md` | Citation discipline and field writing conventions |
| `CONTEXT.md` | Methodology development notes |

## Status

Methodology + pre-registered evaluation; the calibration corpus has not yet
been processed. The published artefact release plan (annotation tool +
prompt templates) is conditional on IRB approval and DPA negotiation.

## Ethics

- No raw post text is or will be republished.
- Victim names are not retained in any artefact.
- The project does not interact with the leak-site infrastructure itself.
- IRB approval and a signed DPA with the mirror operator are preconditions
  for running the calibration phase.
