# Style notes — derived from the nine downloaded reference PDFs

These notes summarise recurring rhetorical and structural conventions in the
downloaded pre-2022 references. PAPER.md should mimic the dominant pattern
where possible.

## Field conventions

The corpus mixes two adjacent literatures: (i) Tor / dark-web measurement and
security papers (Falconieri 2019; Brunelle et al. 2021; the content-based
ranking paper of 2019 — arXiv 1910.02332), and (ii) general computer-vision /
vision–language foundation papers (CLIP, ViT, ViLBERT) and image-based web
classification (Aydos 2020, the random-image classifier 2019, De Fausti et
al. 2019). The security side reads as systems-oriented and pragmatic. The
vision side reads as benchmark-driven and uses tighter empirical claims.

A methodology paper that straddles both should keep:
- a security-paper Introduction (problem motivation, why current tooling
  fails, the proposed architecture in one paragraph);
- a vision-paper Related Work (organised by component rather than
  chronologically);
- explicit framing of contributions as bullet points at the end of §1.

## Phrasing patterns to imitate

- "We propose / we present / we describe" — the authors collective.
  Avoid the first person singular entirely. CLIP and ViT both use "we"
  throughout despite their large author lists.
- "To the best of our knowledge, no prior work has X." — common framing of
  novelty in both Falconieri 2019 and the ranking paper. Use sparingly and
  only where defensible.
- Numbers in claims: vision papers quote two- or three-significant-figure
  scores ("achieves 96.6% accuracy", "macro F1 of 93.7%"). When numbers
  are not yet available (this paper has none), substitute structural
  predictions ("we expect per-class F1 to differ most on the EmptyOrError
  and Parked categories, because their visual signatures are nearly
  indistinguishable from a failed render").
- Tor-side papers are explicit about ethics ("we removed datasets pictures
  which were identified as containing personal information"). Mirror this
  language in §5.4.
- Frame limitations openly. Brunelle et al. discuss URI shift as a known
  unavoidable nuisance; CLIP openly discusses biases and limitations of
  zero-shot prediction. Authors do not over-claim.

## Structural conventions

- IMRAD with explicit numbered sections and subsections. Subsection
  headings are short noun phrases ("The Crawler", "The Storage").
- Captioned figures referenced as "Figure 1", "Figure 2"; tables as
  "Table I", "Table II". For a Mermaid-only paper, reference Mermaid
  figures by the same convention.
- References cited as bracketed numbers in the dark-web measurement
  literature; author–year is also acceptable in the vision side. For
  consistency PAPER.md uses author–year (Lastname YEAR).
- Section §6 / Conclusions stays short — usually two paragraphs.

## What to avoid

- Marketing language: "robust", "comprehensive", "delve", "leverage" used
  more than once, "It is worth noting that". None of the references read
  like a product pitch.
- Over-confident claims about generalisation. CLIP and ViT both temper
  their conclusions with caveats about benchmark coverage.
- Speculative numbers. If no experiment has been run, do not produce
  fake F1 scores. State that §4 defines a protocol for future work.
- Decorative emoji, ASCII art outside designated figure files, or
  bibliography entries copied without a published venue. Where the
  underlying work is non-arxiv (Spitters 2014, Christin 2013, Moore & Rid
  2016, Owen & Savage 2015) the reference still lists the actual venue.

## Length and weight

The Tor measurement papers are short (4-12 pages, Brunelle 5pp, Falconieri
12pp). The vision foundation papers are long (CLIP 48pp, ViT 22pp,
ViLBERT 11pp). A 4000-7000 word methodology paper sits closer to the
vision style and should look like a workshop/conference submission, not
a journal article. Keep Related Work proportional — do not let it
crowd out §3 (the proposed pipeline) which carries the contribution.
