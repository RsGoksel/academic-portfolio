# Paper 04 — Detecting Typo-Squat-by-Copy Supply-Chain Attacks

> **ResearchGate publication:** _(link pending upload)_

Forensic case study of a real impersonator GitHub repository that cloned a
legitimate dark-web OSINT project byte-identically and added one malicious
binary inside `.github/ISSUE_TEMPLATE/`. The paper documents a ten-point
pre-install audit checklist that catches the attack, proposes a
fifty-line Python tool (`forkdiff-audit`) that automates the decisive
binary-inventory check, and presents a ninety-minute classroom lab built
around the live forensic artefact.

## What is in this directory

| Path | Content |
|---|---|
| `figures/fig1_attack_anatomy.mmd` / `.png` | Anatomy of the impersonator-by-copy attack |
| `figures/fig2_audit_decision_tree.mmd` / `.png` | Ten-point audit decision tree with PASS / FAIL gates |
| `figures/fig3_forkdiff_audit_flow.mmd` / `.png` | `forkdiff-audit` tool flow |
| `figures/fig4_lab_timeline.txt` | Ninety-minute classroom lab timeline |
| `references/_style_notes.md` | Field writing conventions for supply-chain security |
| `CONTEXT.md` | Forensic methodology notes and detection rationale |

## Status

Forensic case study; the malicious artefact is quarantined and is not and
will not be redistributed in this repository or anywhere else. The
`forkdiff-audit` reference implementation appears in Appendix B of the
paper as a runnable Python module.

## A note on responsible disclosure

At the time of paper preparation the impersonator account had not yet been
contacted and the malicious repository had not yet been reported to GitHub.
The paper is structured so that both actions can occur before public
release; see §6 of the paper.
