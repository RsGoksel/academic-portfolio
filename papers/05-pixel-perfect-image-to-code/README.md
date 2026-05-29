# Paper 05 — Iterative Visual Feedback Loops for Pixel-Faithful Image-to-Code

> **ResearchGate publication:** _(link pending upload)_

An architectural proposal and pre-registered benchmark design for
pixel-faithful image-to-code generation. The paper argues that the
seventy-to-eighty-five-percent fidelity ceiling of single-shot image-to-code
tools is a structural property of the generation pattern (rather than a
model-quality problem) and proposes a `generate → render → diff →
critique → patch` loop with a forced-improvement guardrail as the
architectural fix. The benchmark design contrasts single-shot baselines
against iterative variants on the Design2Code corpus plus a held-out
fifty-page brand-design set.

## What is in this directory

| Path | Content |
|---|---|
| `figures/fig1_pipeline.mmd` / `.png` | Full proposed pipeline flowchart |
| `figures/fig2_failure_mode_taxonomy.mmd` / `.png` | Three-cause taxonomy of single-shot failure |
| `figures/fig3_eval_conditions.txt` | Eight-condition matrix vs six metrics + five hypotheses |
| `figures/fig4_forced_improvement_loop.mmd` / `.png` | One iteration of the forced-improvement guardrail |
| `references/_style_notes.md` | Field writing conventions |
| `CONTEXT.md` | Architecture proposal and benchmark design notes |

## Status

Architecture proposal + pre-registered benchmark design; no measurements
are reported. Section 5 specifies the evaluation protocol so that other
groups can execute it.

## Related concurrent work

Two papers published subsequent to the design phase of this proposal
report independently developed iterative-feedback architectures:

- ReLook (arXiv:2510.11498)
- UI2Code^N-9B (arXiv:2511.08195; HuggingFace `zai-org/UI2Code_N`)

Both papers' results corroborate the architectural hypothesis we propose
to test. See §2.5 of the paper for the explicit framing.
