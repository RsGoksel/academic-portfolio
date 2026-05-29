# Reference Pool — Paper 04 Style Notes

All references were retrieved (PDF on disk) or confirmed via Google Scholar metadata before citation.
Hard rule observed: nothing cited that we did not first retrieve in some form.
All works are pre-2022, satisfying the prior-art-only constraint of the bildiri portfolio.

## Retrieved PDFs (in `./` next to this file)

| Filename | Citation key | Notes on what it brings |
|---|---|---|
| `2005.09535.pdf` | Ohm 2020 | Foundational taxonomy of OSS supply-chain attacks. The single most important framing reference — provides the categorization (typosquatting, account hijack, malicious update, etc.) we extend with the "impersonator-by-copy" sub-pattern. |
| `1902.09217.pdf` | Zimmermann 2019 | npm ecosystem security study; quantifies how a small number of maintainer accounts transitively control a huge fraction of installs. We cite for the "trust signal aggregation" framing — why developers rely on author identity heuristics. |
| `2002.01139.pdf` | Duan 2020 | Cross-ecosystem (PyPI / npm / RubyGems) measurement study of supply-chain attacks. Empirical baseline for prevalence claims; describes the MalOSS analysis pipeline whose limitations our case study illustrates. |
| `2003.03471.pdf` | Taylor 2020 (SpellBound) | Defensive tool against typosquatting (orthographic Levenshtein-distance based). Directly contrasts with our setting: the impersonator chose a wholly different name, so name-distance defenses are useless. |
| `2102.06301.pdf` | Bagmar 2021 | Python-ecosystem-specific threat study. We cite for prevalence of malicious-package signals in PyPI and for static-analysis features that recur in literature. |
| `2112.10165.pdf` | Zahan 2021 | "Weak links in the npm supply chain" — identifies six dimensions of supply-chain weakness. We extend their framework with a seventh dimension (repository-payload weakness, distinct from package-metadata weakness). |

## Cited but not PDF-retrieved (metadata confirmed via Google Scholar)

These are cited because their existence and authorship were confirmed by Google Scholar searches in this session. The full text was not available for download via the academic search MCPs (paywall or non-open-access).

| Citation key | Source | What it brings |
|---|---|---|
| Pfretzschner & ben Othmane 2017 | ACM DL https://dl.acm.org/doi/abs/10.1145/3098954.3120928 | Early Node.js dependency-tree attack taxonomy. Confirmed via Google Scholar. We cite for the four-class dependency-attack taxonomy. |
| Garrett 2019 | IEEE ICSE NIER https://ieeexplore.ieee.org/abstract/document/8805698/ | Anomaly-detection approach for suspicious npm updates. Confirmed via Google Scholar. We cite as the closest prior art on "automated detection at the package level," contrasting with our repository-level setting. |
| Vu 2020 | IEEE-SecDev https://ieeexplore.ieee.org/abstract/document/9229803/ | Python-specific typosquatting and combosquatting study. Confirmed via Google Scholar. We cite for prevalence of name-collision attacks, contrasted with our name-distinct attack. |
| Vykopal 2017 (KYPO) | IEEE FIE https://ieeexplore.ieee.org/abstract/document/8190713/ | Cyber-range pedagogy. Confirmed via Google Scholar. We cite as the strongest precedent for using real adversarial artifacts in classroom settings. |
| Leune & Petrilli 2017 | ACM SIGITE https://dl.acm.org/doi/abs/10.1145/3125659.3125686 | CTF-style hands-on security education. Confirmed via Google Scholar. We cite for the active-learning framing of the proposed 90-minute lab. |

## Citation style

- IEEE-style numeric in-text, e.g. `[1]`, `[2, 3]`, `[4]–[7]`.
- References listed in citation order at the end.
- For URL-only references (no DOI), include the access date footnote-style.
- Author surnames first in narrative ("Ohm et al. [1] proposed…"), full author lists in bibliography.

## Voice and tone

- Past-tense reporting for empirical findings ("we found", "the attacker added").
- Present-tense for ongoing properties ("the upstream repository contains", "the LICENSE file is").
- First-person plural ("we audited", "we propose") consistent with single-author bildiri submissions in the İTÜ tradition.
- No emojis. No LLM tics ("delve", "in conclusion", "it is important to note", overuse of "robust").
- Numbers as digits when ≥ 10 or when units follow.
- File paths in monospace.

## What is deliberately NOT cited

- Post-2022 industry reports (Phylum, Sonatype State of the Supply Chain). These exist but violate the pre-2022 portfolio constraint.
- Crocker 2021 `colors`/`faker` npm incident. Widely discussed but the technical postmortem is industry-blog material, not an academic publication; mentioned in prose without citation.
- Generic security education textbooks. The two CTF/cyber-range papers above suffice.
