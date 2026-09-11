# Diagnostic paper and portable analysis build

The authoritative prose is `paper/when-training-gets-easier.md`. Build scripts generate `paper/anonymous.tex`, `site/paper.html`, and the five displayed figures. Edit the Markdown and builders, then regenerate; do not edit generated prose independently.

Use Python 3.11 and the versions in `paper/requirements-analysis.txt`, Tectonic 0.17.0, and Poppler's `pdfinfo`/`pdftotext`. The class is the unmodified PaperCept `ieeeconf.cls`. No template margins or font sizes are reduced.

From a clean checkout, unpack the declared anonymous data package to a chosen directory and run:

```sh
python -m pip install -r paper/requirements-analysis.txt
python tools/report_diagnostic_data.py --data /path/to/data --output /path/to/analysis
python tools/build_diagnostic_figures.py --data /path/to/data
python tools/build_diagnostic_paper.py
tectonic paper/anonymous.tex --outdir /path/to/build --keep-logs
python -m pytest tests/test_diagnostic_data.py -q
```

Alternatively, assemble and execute an isolated portable build:

```sh
python tools/build_diagnostic_package.py --data /path/to/data --output /path/to/package
```

The package includes the necessary prose, template, source scripts, hashed compact inputs, all constituent CSV tables and generated figures. `paper/data-dictionary.md` defines units, denominators, masking and panel identity. Regeneration uses no simulator, private source path or network account. Re-running the original training requires additional private checkpoints/assets and is a separate contract.

The private export step, performed only by an author with source access, is:

```sh
python tools/export_diagnostic_data.py --private-root /path/to/private-data --output /path/to/data
```

That exporter additionally requires the pinned SONIC environment (Torch and PyYAML). It verifies recorded continuation metric hashes, preserves the frozen receipts, and writes an identifying source map beside the data directory; the source map must not enter the anonymous archive.

The September 8 candidate is eight pages. Visual review and automated checks are recorded separately from human scientific review, author approval and portal validation. The optional video is assembled from existing simulation footage; no separate supplementary PDF is part of the submission.

For video assembly, install FFmpeg/ffprobe and DejaVu Sans, then run `python tools/build_submission_video.py --output /path/to/video`. The builder verifies the existing footage against `paper/evidence/historical-video-source.json`, retains all recorded tiles, checks media limits and decodes every output frame. Pass `--video-directory /path/to/video` to the package builder to include the video, source footage and binding. Assembly performs no simulation. New builds require renewed visual review; a recorded portal PDF test applies only to its exact PDF hash.
