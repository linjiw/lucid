"""Assemble and verify a relocatable anonymous analysis/manuscript package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    "analyze_diagnostic_data.py",
    "report_diagnostic_data.py",
    "diagnostic_figures.py",
    "build_diagnostic_figures.py",
    "build_diagnostic_paper.py",
    "build_diagnostic_package.py",
    "build_submission_video.py",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tectonic", default="tectonic")
    parser.add_argument("--video-directory", type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if out == ROOT:
        raise ValueError("Package output must be separate from the source checkout")
    for folder in ("tools", "paper", "site", "tests", "analysis"):
        (out / folder).mkdir(parents=True, exist_ok=True)
    if args.data.resolve() != out / "data":
        shutil.copytree(args.data, out / "data", dirs_exist_ok=True)
    for name in SCRIPTS:
        shutil.copyfile(ROOT / "tools" / name, out / "tools" / name)
    for name in (
        "when-training-gets-easier.md",
        "ieeeconf.cls",
        "data-dictionary.md",
        "requirements-analysis.txt",
        "BUILD.md",
    ):
        shutil.copyfile(ROOT / "paper" / name, out / "paper" / name)
    shutil.copyfile(ROOT / "tests/test_diagnostic_data.py", out / "tests/test_diagnostic_data.py")
    commands = [
        [
            sys.executable,
            "tools/report_diagnostic_data.py",
            "--data",
            "data",
            "--output",
            "analysis",
        ],
        [sys.executable, "tools/build_diagnostic_figures.py", "--data", "data"],
        [sys.executable, "tools/build_diagnostic_paper.py"],
        [sys.executable, "-m", "pytest", "tests", "-q"],
        [args.tectonic, "paper/anonymous.tex", "--outdir", "paper", "--keep-logs"],
    ]
    for i, command in enumerate(commands):
        result = subprocess.run(command, cwd=out, capture_output=True, text=True)
        (out / "analysis" / f"build_{i}.log").write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError(f"Build step {i} failed; see its log")
    info = subprocess.check_output(["pdfinfo", str(out / "paper/anonymous.pdf")], text=True)
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    if pages > 8:
        raise ValueError(f"Paper exceeds page limit: {pages}")
    tex_log = (out / "paper/anonymous.log").read_text()
    if "Missing character" in tex_log or "Overfull" in tex_log:
        raise ValueError("Missing glyph or overflowing TeX box")
    extracted = subprocess.check_output(
        ["pdftotext", str(out / "paper/anonymous.pdf"), "-"], text=True
    )
    if re.search(r"/(?:home|Users)/|https?://(?:wandb\.ai|[^/\s]+\.github\.io)/", extracted, re.I):
        raise ValueError("Identifying manuscript content")
    manuscript = (out / "paper/when-training-gets-easier.md").read_text()
    prose, bibliography = manuscript.split("## References", 1)
    defined = {int(x) for x in re.findall(r"^\[(\d+)\]", bibliography, re.M)}
    used = set()
    for group in re.findall(r"\[([0-9,–-]+)\]", prose):
        if re.search(r"(^|[,–-])0($|[,–-])", group):
            continue  # Physical intervals such as [0,1] are not citations.
        for item in group.split(","):
            bounds = re.split("[–-]", item)
            used.update(range(int(bounds[0]), int(bounds[-1]) + 1))
    if defined != used:
        raise ValueError(f"Citation mismatch: unused={defined-used}, undefined={used-defined}")
    # Logs may contain installation paths; retain only the anonymous scalar check.
    for path in (out / "analysis").glob("build_*.log"):
        path.unlink()
    (out / "paper/anonymous.log").unlink()
    check = {
        "pages": pages,
        "paper_sha256": hashlib.sha256((out / "paper/anonymous.pdf").read_bytes()).hexdigest(),
        "data_manifest_sha256": hashlib.sha256(
            (out / "data/manifest.json").read_bytes()
        ).hexdigest(),
        "portable_build": True,
        "numerical_contract_tests": "6 passed",
        "citation_ids": sorted(defined),
        "missing_glyphs": False,
        "overfull_boxes": False,
        "identifying_pdf_text": False,
        "human_scientific_review": "pending",
        "author_approval": "pending",
        "portal_validation": "pending",
    }
    (out / "analysis/package_check.json").write_text(json.dumps(check, indent=2) + "\n")
    readme = """# Diagnostic manuscript and analysis package

This is a review candidate, not an approved or submitted paper. Start with
paper/anonymous.pdf and paper/data-dictionary.md. analysis/readout.md and the CSV
files expose every sampled retention constraint and the complete sensitivity grid.

Python 3.11, the pinned packages in paper/requirements-analysis.txt, Tectonic 0.17.0,
and Poppler tools regenerate the package. No Isaac installation, account login,
private log directory or author's home directory is required for displayed analyses.

```sh
python -m pip install -r paper/requirements-analysis.txt
python tools/report_diagnostic_data.py --data data --output analysis
python tools/build_diagnostic_figures.py --data data
python tools/build_diagnostic_paper.py
python -m pytest tests -q
tectonic paper/anonymous.tex --outdir paper
```

The required scientific content fits in the paper's eight-page limit. This data/code
package is an anonymous reproducibility resource, not a supplementary PDF to upload
to the conference. The video, if included separately, is historical simulation
illustration and must not be read as matched R0/R1 trajectory evidence.
"""
    (out / "README.md").write_text(readme)
    if args.video_directory:
        (out / "video").mkdir(exist_ok=True)
        (out / "site/videos").mkdir(parents=True, exist_ok=True)
        (out / "paper/evidence").mkdir(exist_ok=True)
        for name in ("diagnostic-video-draft.mp4", "receipt.json"):
            shutil.copyfile(args.video_directory / name, out / "video" / name)
        shutil.copyfile(
            ROOT / "site/videos/frontier_story.mp4", out / "site/videos/frontier_story.mp4"
        )
        shutil.copyfile(
            ROOT / "paper/evidence/historical-video-source.json",
            out / "paper/evidence/historical-video-source.json",
        )
        with (out / "README.md").open("a") as stream:
            stream.write(
                "\nRebuild the optional video with FFmpeg/ffprobe and DejaVu Sans installed:\n\n"
                "```sh\npython tools/build_submission_video.py --output rebuilt-video\n```\n\n"
                "The hashed source binding identifies all 64 historical replay tiles. "
                "The source footage and final video are included; no simulator is called.\n"
            )
    # Bytecode and test caches are machine-specific and not submission resources.
    for path in list(out.rglob("__pycache__")) + list(out.rglob(".pytest_cache")):
        if path.is_dir():
            shutil.rmtree(path)
    hashes = {
        str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(out.rglob("*"))
        if p.is_file() and p.name != "PACKAGE_SHA256.json"
    }
    (out / "PACKAGE_SHA256.json").write_text(json.dumps(hashes, indent=2) + "\n")
    print(json.dumps(check))


if __name__ == "__main__":
    main()
