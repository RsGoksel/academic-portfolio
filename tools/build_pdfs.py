"""Build IEEE-ish PDFs from each PAPER.md.

Pipeline per paper:
  1. Render every figures/*.mmd to figures/<name>.png via mermaid.ink
  2. Build a PAPER_RENDER.md: prepend a pandoc YAML block with author/ORCID/affiliation,
     and replace every '`figures/fig*.mmd`' / 'figures/fig*.txt' reference in the body with
     an inline figure (image for .mmd, code block for .txt).
  3. Run pandoc → PAPER.pdf (xelatex engine, A4 paper, single column for readability).

Tool deps: requests, pandoc, xelatex (MiKTeX).
"""
import base64
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

BASE = Path(r"E:\Bildiri")

PAPERS = [
    "01-darkweb-search-engine-benchmark",
    "02-vlm-darknet-screenshots",
    "03-leak-site-classification",
    "04-supply-chain-audit-lab",
    "05-pixel-perfect-image-to-code",
]

AUTHOR_YAML = """---
title: "{title}"
author: "Kadir Göksel Gündüz"
date: "May 2026"
abstract: "{abstract_oneline}"
keywords:
  - {kw1}
  - {kw2}
  - {kw3}
geometry: margin=1in
fontsize: 11pt
linkcolor: blue
urlcolor: blue
colorlinks: true
documentclass: article
papersize: a4
header-includes:
  - \\usepackage{{authblk}}
  - \\usepackage{{graphicx}}
  - \\usepackage{{float}}
  - \\renewcommand{{\\thefootnote}}{{\\fnsymbol{{footnote}}}}
  - \\let\\oldsection\\section
---

\\thispagestyle{{empty}}

\\begin{{center}}
\\textbf{{Kadir Göksel Gündüz}}\\\\
\\textit{{Energy Institute, Istanbul Technical University (İTÜ)}}\\\\
Istanbul, Türkiye\\\\
\\texttt{{gokssel.gunduz@gmail.com}} \\textbar{{}} \\texttt{{gunduz25@itu.edu.tr}}\\\\
ORCID: 0009-0007-9120-5659
\\end{{center}}

\\vspace{{1em}}

"""

PAPER_KEYWORDS = {
    "01-darkweb-search-engine-benchmark": ("Tor", "dark-web information retrieval", "benchmark"),
    "02-vlm-darknet-screenshots":        ("vision-language models", "Tor hidden services", "classification"),
    "03-leak-site-classification":       ("ransomware", "LLM information extraction", "cyber threat intelligence"),
    "04-supply-chain-audit-lab":         ("supply-chain attacks", "security pedagogy", "forensic methodology"),
    "05-pixel-perfect-image-to-code":    ("image-to-code", "vision-language models", "iterative refinement"),
}


def mermaid_to_png(mmd_path: Path, png_path: Path) -> bool:
    """Render a Mermaid file to PNG via mermaid.ink."""
    src = mmd_path.read_text(encoding="utf-8")
    # Strip leading comments (% ... lines) — mermaid.ink chokes on some comment styles
    lines = [ln for ln in src.splitlines() if not ln.strip().startswith("%%")]
    src = "\n".join(lines).strip()
    # mermaid.ink: base64(JSON.stringify({code: source}))
    import json
    payload = json.dumps({"code": src, "mermaid": {"theme": "default"}})
    b64 = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    url = f"https://mermaid.ink/img/{b64}?type=png&bgColor=FFFFFF"
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and len(r.content) > 1000:
                png_path.write_bytes(r.content)
                print(f"    OK  {png_path.name} ({len(r.content)//1024} KB)")
                return True
            else:
                print(f"    attempt {attempt+1}: status={r.status_code} bytes={len(r.content)}")
        except Exception as e:
            print(f"    attempt {attempt+1}: {e}")
        time.sleep(2 + attempt * 2)
    print(f"    FAIL {mmd_path.name}")
    return False


def extract_abstract(body: str) -> str:
    """Pull the Abstract section text from a PAPER.md (between ## Abstract and the next heading)."""
    m = re.search(r"##\s*Abstract\s*\n+(.*?)\n+##\s", body, re.S)
    if not m:
        m = re.search(r"##\s*Abstract\s*\n+(.*?)\n+---", body, re.S)
    if not m:
        return "Abstract not extractable from PAPER.md — see body."
    abs_text = m.group(1).strip()
    # Collapse internal whitespace, single paragraph
    abs_text = re.sub(r"\s+", " ", abs_text)
    return abs_text


def strip_top_title_and_abstract(body: str) -> str:
    """Drop the first '# Title', the Abstract section, and any cosmetic horizontal-rule
    separators (`---`) between sections — the YAML title block already renders title/author/
    abstract on a clean page, so the body should start straight with the first section."""
    # Drop everything up to and including '## Abstract' through the next ## heading
    body = re.sub(r"^#\s+.+?\n", "", body, count=1)  # remove first H1
    body = re.sub(r"##\s*Abstract\s*\n+.*?(?=\n##\s)", "", body, count=1, flags=re.S)
    # Strip cosmetic horizontal rules between sections (they render as \hrule lines in PDF
    # which a reviewer mistakes for stray em-dashes after the abstract)
    body = re.sub(r"^---\s*\n", "", body, flags=re.M)
    return body.lstrip()


def humanize_stem(stem: str) -> str:
    """fig1_pipeline -> 'Pipeline'."""
    parts = stem.split("_", 1)
    if len(parts) < 2:
        return stem
    label = parts[1].replace("_", " ").strip()
    return label[:1].upper() + label[1:]


def figure_number_from_stem(stem: str) -> str:
    """fig1_pipeline -> '1', fig4_xxx -> '4'."""
    m = re.match(r"fig(\d+)", stem)
    return m.group(1) if m else "?"


def build_figures_appendix(fig_dir: Path, fig_dir_rel: str) -> str:
    """Build a 'Figures' markdown section listing every PNG (rendered Mermaid) and .txt (ASCII) figure."""
    items = []

    # First the PNGs (rendered from Mermaid)
    pngs = sorted(fig_dir.glob("*.png"))
    txts = sorted(fig_dir.glob("*.txt"))

    # Sort by figure number when possible
    def sort_key(p):
        n = figure_number_from_stem(p.stem)
        return (int(n) if n.isdigit() else 999, p.name)

    pngs.sort(key=sort_key)
    txts.sort(key=sort_key)

    # Build entries — combine PNGs and ASCII txts, in figure-number order
    all_figs = sorted(
        [(p, "png") for p in pngs] + [(p, "txt") for p in txts],
        key=lambda x: sort_key(x[0]),
    )

    if not all_figs:
        return ""

    out = ["\n\n# Figures\n"]
    for p, kind in all_figs:
        num = figure_number_from_stem(p.stem)
        label = humanize_stem(p.stem)
        caption = f"**Figure {num}.** {label}."
        if kind == "png":
            out.append(f"\n{caption}\n\n![]({fig_dir_rel}/{p.name}){{width=85%}}\n")
        else:
            ascii_content = p.read_text(encoding="utf-8").rstrip()
            out.append(f"\n{caption}\n\n```text\n{ascii_content}\n```\n")
    return "\n".join(out)


def patch_figure_refs(body: str, fig_dir: Path, fig_dir_rel: str) -> str:
    """Append all figures as a Figures section before the References section.

    If the body already contains a '## Figures' section (e.g. paper 03 written by controller),
    replace it with the auto-generated one so the captions and inline images are consistent.
    Otherwise insert just before '## References' (or at end if no References heading).
    """
    figs_block = build_figures_appendix(fig_dir, fig_dir_rel)
    if not figs_block:
        return body

    # Remove existing '## Figures' or '# Figures' section if present
    body = re.sub(
        r"\n##? Figures\n.*?(?=\n##? |\Z)",
        "\n",
        body, count=1, flags=re.S,
    )

    # Insert before References / Bibliography heading, OR before Appendix, OR at end
    insertion_targets = [
        r"\n##? References\b",
        r"\n##? Bibliography\b",
        r"\n##? Appendix\b",
    ]
    for pat in insertion_targets:
        m = re.search(pat, body)
        if m:
            return body[: m.start()] + figs_block + body[m.start():]
    return body + figs_block


def build_pdf(slug: str):
    print(f"\n=== {slug} ===")
    paper_dir = BASE / slug
    paper_md = paper_dir / "PAPER.md"
    fig_dir = paper_dir / "figures"
    render_md = paper_dir / "PAPER_RENDER.md"
    pdf_out = paper_dir / "PAPER.pdf"

    if not paper_md.exists():
        print(f"  SKIP — no PAPER.md")
        return False

    # 1) Render every .mmd to .png
    print("  Rendering Mermaid figures...")
    mmds = sorted(fig_dir.glob("*.mmd"))
    for m in mmds:
        png = fig_dir / (m.stem + ".png")
        if png.exists():
            print(f"    cached  {png.name}")
            continue
        mermaid_to_png(m, png)

    # 2) Build PAPER_RENDER.md
    body = paper_md.read_text(encoding="utf-8")
    # Extract original title and abstract first
    title_m = re.match(r"#\s+(.+)", body)
    title = title_m.group(1).strip() if title_m else slug
    abstract = extract_abstract(body)

    # Strip original title + abstract
    body_no_top = strip_top_title_and_abstract(body)

    # Insert a "Figures" section with all PNGs + ASCII txts inline, before References
    body_patched = patch_figure_refs(body_no_top, fig_dir, "figures")

    # Build YAML front-matter
    # Abstract: single-line with quotes escaped, NO sentence splitting (preserves periods)
    abstract_oneline = abstract.replace('"', "'").replace("\n", " ").strip()
    abstract_oneline = re.sub(r"\s+", " ", abstract_oneline)
    kw1, kw2, kw3 = PAPER_KEYWORDS[slug]
    head = AUTHOR_YAML.format(
        title=title.replace('"', '\\"'),
        abstract_oneline=abstract_oneline,
        kw1=kw1, kw2=kw2, kw3=kw3,
    )
    render_md.write_text(head + body_patched, encoding="utf-8")
    print(f"  wrote {render_md.name} ({render_md.stat().st_size//1024} KB)")

    # 3) Run pandoc
    print("  Running pandoc -> PDF...")
    cmd = [
        "pandoc",
        str(render_md),
        "-o", str(pdf_out),
        "--pdf-engine=xelatex",
        "--from=markdown+yaml_metadata_block+raw_tex",
        "--standalone",
        "--variable=mainfont:Times New Roman",
        "--variable=monofont:Consolas",
        "--variable=sansfont:Arial",
        "--resource-path", str(paper_dir),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=paper_dir, timeout=600)
        if r.returncode != 0:
            print(f"  PANDOC FAIL (rc={r.returncode}):")
            print("  STDERR:", r.stderr[-2000:])
            return False
        if pdf_out.exists():
            sz = pdf_out.stat().st_size
            print(f"  OK  {pdf_out.name} ({sz//1024} KB)")
            return True
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return False
    return False


def main():
    only = set(sys.argv[1:]) or set(PAPERS)
    ok = []
    fail = []
    for slug in PAPERS:
        if slug in only or slug.split("-")[0] in only:
            if build_pdf(slug):
                ok.append(slug)
            else:
                fail.append(slug)
    print(f"\n=== SUMMARY ===")
    print(f"OK   ({len(ok)}): {ok}")
    print(f"FAIL ({len(fail)}): {fail}")


if __name__ == "__main__":
    main()
