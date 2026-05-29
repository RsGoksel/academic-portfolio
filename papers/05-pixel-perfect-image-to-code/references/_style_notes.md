# References — Style and Provenance Notes

All ten PDFs in this folder are genuinely pre-2022 (publication or first arXiv version no later than 2021-12-31). Every paper is cited at least once in `../PAPER.md`. The two recent corroborating works named in `CONTEXT.md` — ReLook (arXiv 2510.11498) and UI2Code^N (arXiv 2511.08195) — are post-2022 and are deliberately **not** stored here; they are discussed in the body text of the paper with an explicit note that they appeared after the architecture proposed here was drafted.

## Inventory

| File | Year | Citation key | Why it is cited |
|---|---|---|---|
| `1411.4555.pdf` | 2015 | Vinyals2015 | Show-and-Tell. Seminal CNN encoder + LSTM decoder for image-to-text. Establishes the encoder-decoder pattern that later image-to-code work inherits. |
| `1502.03044.pdf` | 2015 | Xu2015 | Show, Attend and Tell. Adds soft and hard attention over image regions. Anticipates the patch-based attention that dominates today's VLMs. |
| `1611.01989.pdf` | 2016 | Balog2016 | DeepCoder. Learning to predict program properties from input-output examples; one of the first neural-guided program synthesis systems. Cited for the iterative search tradition. |
| `1705.07962.pdf` | 2017 | Beltramelli2017 | pix2code. The original GUI-screenshot to DSL-code paper. Direct ancestor of the problem this paper attacks. |
| `1706.03741.pdf` | 2017 | Christiano2017 | Deep RL from Human Preferences. Establishes preference-based comparison as a learning signal. Foundation for VLM-as-judge framing. |
| `1807.03168.pdf` | 2018 | Chen2018 | Execution-Guided Neural Program Synthesis. Generate-execute-correct loop in the programming domain. Closest pre-2022 architectural analogue of the visual feedback loop proposed here. |
| `1908.02265.pdf` | 2019 | Lu2019 | ViLBERT. Two-stream vision-language pretraining. Cited as background on the joint visual-textual representations that VLMs rely on. |
| `2009.01325.pdf` | 2020 | Stiennon2020 | Learning to summarize from human feedback. End-to-end demonstration that a learned reward model from pairwise comparison outperforms supervised baselines. Direct precedent for using a VLM as critic. |
| `2010.11929.pdf` | 2020 | Dosovitskiy2020 | An Image is Worth 16x16 Words (ViT). The patch-embedding mechanism whose lossy nature is the structural cause of pixel-grid imprecision in section 3.1. |
| `2103.00020.pdf` | 2021 | Radford2021 | CLIP. Joint image-text embedding via contrastive learning. The other foundation of every modern code-VLM. |

## Style conventions used in PAPER.md citations

- In-text format: `(Author Year)` for single author, `(Author and Author Year)` for two, `(Author et al. Year)` for three or more.
- Reference list entries follow ACM-style numbered order, sorted alphabetically by first author surname.
- ReLook and UI2Code^N appear in the body with their arXiv identifier inline (`arXiv:2510.11498`, `arXiv:2511.08195`) and a parenthetical note that they postdate this work's design. They are listed in a separate "Subsequent corroborating work" subsection of the References to make the timeline explicit.
- Design2Code numerical scores quoted in the body (GPT-5 93.7, UI2Code^N 92.5, Claude-4-Sonnet 85.1, UI-polish 95.0 vs 76.3) are sourced from the UI2Code^N paper and reported as-quoted, not re-measured.

## Excluded near-2022 papers

The following papers were considered but excluded as they cross the 2021-12-31 cutoff:

- Sketch2Code (Microsoft 2018-2019) — no canonical arXiv listing usable here; the original Microsoft Research blog post predates arXiv distribution. Mentioned by name in section 2.1 with a citation to the Microsoft technical report rather than an arXiv PDF.
- Pix2Struct (Lee et al. 2022) — published 2022, excluded.
- Self-Refine, Reflexion, Constitutional AI — all 2022 or later, excluded.
