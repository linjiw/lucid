"""Render the working Markdown to public HTML and an anonymous IEEE source."""

from pathlib import Path
import base64
from html import escape
import io
import re
import shutil
import markdown
import matplotlib
from matplotlib import mathtext
from matplotlib.font_manager import FontProperties

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "site").mkdir(exist_ok=True)
s = (ROOT / "paper/when-training-gets-easier.md").read_text()
mathematics = []


def hold_html_math(match):
    mathematics.append(match.group())
    return f"MATHPLACEHOLDER{len(mathematics)-1}END"


html = markdown.markdown(
    re.sub(r"\$[^$]+\$", hold_html_math, s), extensions=["tables", "fenced_code"]
)
# Embedded vector math remains readable without a CDN or browser account.
matplotlib.rcParams["svg.hashsalt"] = "diagnostic-inline-math"
for i, expression in enumerate(mathematics):
    buffer = io.BytesIO()
    mathtext.math_to_image(
        re.sub(r"\\mathcal\s+([A-Za-z])", r"\\mathcal{\1}", expression),
        buffer,
        prop=FontProperties(size=13),
        format="svg",
    )
    svg = re.sub(rb"<dc:date>.*?</dc:date>", b"", buffer.getvalue())
    encoded = base64.b64encode(svg).decode("ascii")
    markup = (
        '<img style="vertical-align:middle;max-width:100%" alt="'
        + escape(expression, quote=True)
        + '" src="data:image/svg+xml;base64,'
        + encoded
        + '">'
    )
    html = html.replace(f"MATHPLACEHOLDER{i}END", markup)
(ROOT / "site/paper.html").write_text(
    """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>When Training Gets Easier — working manuscript</title><style>body{max-width:960px;margin:3rem auto;padding:0 1.5rem;font:18px/1.6 Georgia,serif;color:#202c32}table{border-collapse:collapse;font:14px/1.4 sans-serif;width:100%}td,th{border:1px solid #ccd5d8;padding:.5rem}h1,h2,h3{line-height:1.2}pre{overflow:auto}a{color:#176b7b}</style></head><body><nav><a href="./">Project overview</a></nav>"""
    + html
    + "</body></html>"
)


# Escape text while preserving authored math and simple inline formatting.
def inline(text):
    stash = []

    def hold(match):
        stash.append(match.group())
        return f"ZZMATH{len(stash)-1}ZZ"

    text = re.sub(r"\$[^$]+\$", hold, text)
    changes = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "_": r"\_",
        "#": r"\#",
        "{": r"\{",
        "}": r"\}",
        "λ": r"$\lambda$",
        "δ": r"$\delta$",
        "≈": r"$\approx$",
        "²": r"$^2$",
        "≤": r"$\leq$",
        "≥": r"$\geq$",
        "∈": r"$\in$",
        "×": r"$\times$",
        "→": r"$\rightarrow$",
        "−": "-",
        "–": "--",
        "—": "---",
        "’": "'",
        "“": "``",
        "”": "''",
    }
    text = "".join(changes.get(c, c) for c in text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"`(.*?)`", r"\\texttt{\1}", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\\emph{\1}", text)
    for i, value in enumerate(stash):
        text = text.replace(f"ZZMATH{i}ZZ", value)
    return text


figures = {
    "3.": (
        "return_inversion",
        "Historical range trajectories and external outcomes. A and B are the shrink-permitted variants in Table 2; N is never-shrink and F is fixed. Plot labels use the variant plus seed offset from 8600 (A1 is lucid_rg/8601). All twelve points are fixed 8,000-iteration endpoints. The two collapsed policies have the highest returns; B2 ends at full range but has poor AUC.",
    ),
    "3.2": (
        "paired_seeds",
        "Never-shrink-minus-fixed AUC differences for all four decision components. Dots are paired training-seed differences; no line interpolates seed categories. Dashed vertical lines mark the one-sided degradation margins. All three seeds pass each empirical rule. Rollout variation is not training-seed uncertainty.",
    ),
    "4.": (
        "retention_trajectory",
        "Complete sampled retention and hard qualification from one origin. D takes the maximum over global/local errors in nominal/envelope conditions; L is worst completion loss. Dashed budget lines are 10 percent and 2 percentage points. Line segments guide the eye between evaluated checkpoints; they make no between-checkpoint guarantee. Both continuation seeds are displayed separately, with the origin at iteration zero.",
    ),
    "4.3": (
        "threshold_sensitivity",
        "Exploratory threshold sensitivity: endpoint R1-minus-origin hard qualification in percentage points. Columns vary local and rows global error limits; red outlines mark the unchanged primary 600/50 mm cell. Both seeds gain in all 25 combinations. The text also reports R0 and R2, including R0's negative cells.",
    ),
    "5.": (
        "mujoco_ladder",
        "Historical exported policies under independently implemented MuJoCo physics, with pushes disabled. Each point uses 32 draws. The collapsed policy leads the paired seed at scale 1 and trails it at scale 2; transfer of the ordering is condition-specific. These are not continuation checkpoints.",
    ),
}


def figure_tex(key):
    name, caption = figures[key]
    env = "figure*" if name in ("return_inversion", "retention_trajectory") else "figure"
    return (
        r"\begin{"
        + env
        + r"}[t]\centering\includegraphics[width=\linewidth]{figures/"
        + name
        + r".pdf}\caption{"
        + inline(caption)
        + r"}\end{"
        + env
        + "}"
    )


s = re.sub(r"(?<=\S)\n(?=[A-Za-z$*])", " ", s)
lines = s.splitlines()
out = []
i = 0
abstract = False
refs = False
pending_caption = None
while i < len(lines):
    line = lines[i]
    if line.startswith("# "):
        title = line[2:]
        i += 1
        continue
    if line.startswith("**Working manuscript"):
        i += 1
        continue
    if line == "## Abstract":
        out.append(r"\begin{abstract}")
        abstract = True
        i += 1
        continue
    if line.startswith("## "):
        if abstract:
            out.append(r"\end{abstract}")
            abstract = False
        heading = line[3:]
        if heading == "References":
            out.append(r"\section*{References}\small")
            refs = True
        elif heading == "Acknowledgments and AI-use Disclosure":
            out.append(r"\section*{Acknowledgments and AI-use Disclosure}")
        else:
            out.append(r"\section{" + inline(re.sub(r"^\d+\.\s*", "", heading)) + "}")
            key = heading.split()[0]
            if key in figures:
                out.append(figure_tex(key))
        i += 1
        continue
    if line.startswith("### "):
        out.append(r"\subsection{" + inline(re.sub(r"^\d+\.\d+\s*", "", line[4:])) + "}")
        key = line[4:].split()[0]
        if key in figures:
            out.append(figure_tex(key))
        i += 1
        continue
    if line.startswith("**Table "):
        pending_caption = inline(line)
        i += 1
        continue
    if line.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            r = [x.strip() for x in lines[i].strip("|").split("|")]
            if not all(re.fullmatch("[-: ]+", x) for x in r):
                rows.append(r)
            i += 1
        count = len(rows[0])
        env = (
            "table*"
            if count > 3 or (pending_caption and "Table 1." in pending_caption)
            else "table"
        )
        out.append(r"\begin{" + env + r"}[t]\small")
        if pending_caption:
            out.append(pending_caption + r"\par\medskip")
            pending_caption = None
        out.append(r"\begin{tabularx}{\linewidth}{" + ("X" * count) + r"}\hline")
        for j, row in enumerate(rows):
            out.append(" & ".join(inline(x) for x in row) + r" \\" + (r"\hline" if j == 0 else ""))
        out.append(r"\hline\end{tabularx}\end{" + env + "}")
        continue
    if re.match(r"^\d+\. ", line):
        out.append(r"\noindent " + inline(line) + r"\par")
        i += 1
        continue
    if refs and line.startswith("["):
        out.append(r"\noindent " + inline(line) + r"\par\medskip")
        i += 1
        continue
    out.append(inline(line))
    i += 1
header = (
    r"""\documentclass[letterpaper,10pt,conference]{ieeeconf}
\overrideIEEEmargins
\usepackage{amsmath,amssymb,graphicx,tabularx}
\usepackage{times}
\title{"""
    + inline(title)
    + r"""}
\author{Anonymous authors}
\begin{document}
\maketitle
\thispagestyle{empty}\pagestyle{empty}
"""
)
(ROOT / "paper/anonymous.tex").write_text(header + "\n".join(out) + "\n" + r"\end{document}" + "\n")
# Add the same measured figures/captions to the public manuscript.
page = (ROOT / "site/paper.html").read_text()
for key, (name, caption) in figures.items():
    tag = "h3" if key in ("3.2", "4.3") else "h2"
    pattern = r"(<" + tag + r">" + re.escape(key) + r"[^<]*</" + tag + r">)"
    markup = (
        '<figure><img style="max-width:100%" src="img/diagnostic/'
        + name
        + '.svg" alt="'
        + name.replace("_", " ")
        + '"><figcaption>'
        + caption
        + "</figcaption></figure>"
    )
    page = re.sub(pattern, lambda m: m.group(1) + markup, page)
    target = ROOT / "site/img/diagnostic"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "paper/figures" / f"{name}.svg", target / f"{name}.svg")
(ROOT / "site/paper.html").write_text(page)
print("Rendered working HTML and anonymous.tex")
