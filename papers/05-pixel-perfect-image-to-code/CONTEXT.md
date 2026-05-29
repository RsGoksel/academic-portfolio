# CONTEXT — Paper 05: Iterative Visual Feedback for Pixel-Faithful Image-to-Code

> **Status:** Raw findings dump (2026-05-28). Do not delete. PAPER.md derives from this.
> Source material: prior session's research synthesis in `C:\tmp\mcp-scrape\report\research_local_image_to_code.md` (8233-MCP local-dataset scan) + `research_web_image_to_code.md` (2026 web research with citations) + `ACTION_PLAN_pixel_perfect_clone.md` (final recommendations).

## Problem statement

When given a reference image — a UI mockup, a screenshot, a design — and asked to "reproduce this exactly" in HTML/CSS or React/Tailwind, all currently-shipped tools (Vercel v0, Bolt.new, Lovable, Cursor Composer with image, Builder.io Visual Copilot, Locofy.ai Lightning, Anima, Google Stitch, Webcrumbs, MagicPath, Polymet, GPT Engineer, Tldraw "Make Real", and the various screenshot-to-code open-source baselines) produce results that cluster around **70-85% "vibes match"** — they capture the general structure but consistently fail on brand-exact colors, flex/grid alignment, logos, micro-spacing, and z-stack ordering.

This failure is not user error or prompt insufficiency. The session's research showed it is a **structural property of single-shot `image → code` generation**.

## Root-cause analysis (from research)

Three convergent causes:

### 1. Vision encoder destroys pixel-grid precision

Modern VLMs encode an input image as a sequence of patch embeddings (Vision Transformer or similar). Each patch (typically 14×14 or 16×16 pixels) is mapped to a single vector. Within-patch detail is information-theoretically lost. For UI work, this means precise 1-pixel borders, 8-pixel grid alignment, and crisp text edges are reconstructed by the language model essentially by guessing — well-calibrated guesses, but guesses.

### 2. No error-correction signal in single-shot generation

A human designer iterates: produce a draft → look at it next to the target → spot what's off → fix → look again. The fundamental closing-of-the-loop step (look at what I just produced) is absent from `image → code` tools. They generate code once and ship it. There is no second pass that asks "does the produced HTML, when rendered, actually match the reference?"

### 3. Internal aesthetic priors pull output toward the model's "house style"

The model has been trained on huge amounts of clean shadcn/Material/Bootstrap UI. When asked to reproduce an off-brand design, it has a strong gravitational pull toward those familiar patterns. Outputs are "vibes-corrected" toward the training mode, away from the reference.

## The actually-effective fix (from research)

Two 2025-2026 papers independently arrived at the same architecture and reported significant improvements:

- **ReLook** (arXiv 2510.11498) — `generate → render → VLM-critic → diff → patch` with a forced-improvement guardrail (only accept new code if the visual similarity score strictly exceeds the best-so-far). Reports 50:30:20 human-preference wins over its single-shot baseline.

- **UI2Code^N** (arXiv 2511.08195) — A 9B-parameter open-source model explicitly trained on the iterative-feedback paradigm. Reports 92.5 on Design2Code (matches GPT-5 at 93.7, surpasses Claude-4-Sonnet at 85.1) and **95.0 on UI-polish** (Claude-4-Sonnet: 76.3). HuggingFace: `zai-org/UI2Code_N`.

Independently corroborated by the **Kombai** commercial product (currently ~75-80% fidelity on internal benchmarks, the highest of commercial tools) which also runs an internal render-and-critique loop, and by the **RenderLens MCP** (the only MCP in our local 8233-server scan that exposes the pixel-diff loop as a first-class operation — `render(code) → JPEG`, `diff(a, b) → pixel-level metric + heatmap`).

## Recommended pipeline (concrete, today)

```
Reference image (PNG/JPG/Figma URL)
        │
        ▼
[Ingest]
  • If Figma URL → Figma Dev Mode MCP (tokens + layout JSON; "cheat code" — pixel re-derivation is harder than reading metadata)
  • If raw image → just-every screenshot MCP (Claude-Vision-optimized 1072×1072 tiles) + NEURIA analyze_reference_url (token extraction)
        │
        ▼
[Generate first draft]
  • 21st.dev magic MCP (component-level shadcn-based)
  • OR v0-mcp (full-UI Vercel v0)
  • OR direct LLM call to Claude Opus 4.7
  • Constrained by a shadcn MCP for design-system consistency
        │
        ▼
[Render]
  • Playwright MCP → HTML to PNG at the target resolution
        │
        ▼
[Verify — the critical step that existing tools skip]
  • RenderLens diff() → pixel-level fidelity score + heatmap
  • NEURIA score_html → independent quantitative judge
        │
        ▼
[Critique + patch]
  • Pass three images to Claude Opus 4.7: target, rendered, diff overlay
  • Request: "Identify the largest single fidelity gap; emit a minimal CSS/HTML patch."
  • Apply patch, re-render, re-score.
  • Forced-improvement guardrail: accept new code only if score > best_so_far. Otherwise revert and try a different patch direction.
  • Cap at 5 iterations (diminishing returns beyond).
        │
        ▼
Output: HTML/CSS that is pixel-faithful within the iteration budget
```

Why this works where single-shot fails:
- The diff is a **mechanical pixel-level signal** — no aesthetic prior can override what the camera sees.
- The critic VLM is asked a **narrower task** (find one biggest delta and propose patch) — much easier than the open-ended generation problem.
- The forced-improvement guardrail **prevents regression** from speculative patches.

## Local-dataset confirmation

The 8233-server scrape of mcpservers.org returned only **one** MCP server that implements this loop end-to-end: **RenderLens** (`renderlens-dev`). Every other tool labeled "frontend AI" in the dataset is a single-shot generator. Tier-2 plumbing pieces exist (screenshot, vision wrapper, Figma bridges) but no other server wires verify+iterate.

This is the gap. The paper's contribution is to systematize the iterative-loop architecture, evaluate it head-to-head against single-shot baselines on a public benchmark, and release the pipeline as a reusable scaffold.

## Proposed experimental contribution

**Benchmark suite:** Design2Code (Si et al. 2024 — though arXiv 2403 puts this just outside 2022, the test set is the de facto standard) + a fresh held-out set of 50 brand-design pages drawn from real-world examples (Stripe, Linear, Vercel, GitHub homepages — public, no copyright issue for academic measurement).

**Conditions to compare:**
1. Single-shot Claude Opus 4.7 (baseline)
2. Single-shot v0
3. Single-shot Kombai
4. Iterative Opus + Playwright + pixelmatch (3 iters)
5. Iterative Opus + Playwright + pixelmatch (5 iters)
6. Iterative Opus + RenderLens MCP (5 iters)
7. UI2Code^N-9B single-shot
8. UI2Code^N-9B iterative

**Metrics:**
- Pixel-similarity (SSIM, MSE)
- Layout-structural similarity (DOM tree edit distance)
- Human preference (forced-choice pairwise, N=10 evaluators × 50 examples)
- Cost per output ($ for API, GPU-seconds for self-host)
- Wall-clock time

**Hypothesis:** Conditions 4-6 and 8 will outperform 1-3 and 7 by a margin large enough to be visible in human preference. RenderLens (condition 6) will outperform raw pixelmatch (5) by a small margin due to better critic prompting. UI2Code^N iterative (8) will be the best cost-adjusted condition.

## Why publishable

The result that "iterative visual feedback fixes single-shot's failure modes" is intuitive but the existing literature only has two papers (ReLook, UI2Code^N) demonstrating it, both fairly recent, both with internal models. A **clean head-to-head on public benchmarks with reproducible scaffolding** has not been published. The MCP-server framing also makes the contribution **practically reusable** — any team can drop in the proposed pipeline within a day.

Fit: HCI venues (CHI, UIST), generative-AI workshops (NeurIPS / ICLR workshop tracks), or software-engineering venues with HCI overlap (ICSE / FSE).

## Limits

- **Benchmark is biased.** Design2Code samples are clean clearnet web pages, not the harder real-world cases (heavy JS, animations, custom fonts).
- **Critic model = critique cost.** Each iteration adds a frontier VLM call. Cost-benefit favors iteration only up to ~5 rounds; beyond that, diminishing returns.
- **Reproducibility.** Pixel-similarity is sensitive to rendering environment (browser version, font fallbacks). Need to pin the headless browser version.
- **Generalization.** Method assumes you have a render target. For tasks where the target is a text description rather than an image, the loop doesn't directly apply.

## Pre-2022 prior art for citation

- Pix2Code (Beltramelli 2017) — original image-to-code seed work
- Sketch2Code: a deep learning system to map hand-drawn UIs to code (Microsoft Research 2018-2019)
- ScreenAI (Baechler et al. 2024, slightly post-2022 but earlier blog/preprint)
- WebSight dataset (HuggingFace 2023, slightly post-2022)
- Image-to-text and image-to-structure foundational work: Pix2Struct (Lee et al. 2022 — borderline; cite for completeness)
- ViT (Dosovitskiy et al. 2020) — vision encoder architecture
- CLIP (Radford et al. 2021) — vision-language joint embedding
- Self-correction / self-refine in LLMs: Madaan et al. 2023 Self-Refine is too recent; for pre-2022 use Bai et al. 2022 Constitutional AI as the closest seed work; or Shinn et al. 2023 Reflexion (too recent)
- Reflection in interactive task agents: Pre-2022 grounding work in IMRAD-style human-feedback loop: Stiennon et al. 2020 (learning to summarize from human feedback), Christiano et al. 2017 (deep reinforcement learning from human preferences)

Pre-2022 papers are sparser here because the iterative-feedback framing for image-to-code is genuinely new. The PAPER.md should acknowledge this and frame the contribution as connecting two existing threads: (a) the long tradition of iterative refinement in HCI/programming and (b) the modern VLM-as-judge paradigm.
