"""Assemble an anonymous diagnostic video using existing footage and measured plots."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=ROOT / "site/videos/frontier_story.mp4")
    parser.add_argument(
        "--source-manifest", type=Path, default=ROOT / "paper/evidence/historical-video-source.json"
    )
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    parts: list[Path] = []
    segments: list[dict] = []
    inputs = {"historical_replays": sha256(args.source)}
    source_binding = json.loads(args.source_manifest.read_text())
    if inputs["historical_replays"] != source_binding["source_video_sha256"]:
        raise ValueError("Source footage does not match the recorded policy/scale manifest")
    inputs["source_binding"] = sha256(args.source_manifest)

    def render(name: str, ffmpeg_args: list[str]) -> None:
        output = out / f"{name}.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                *ffmpeg_args,
                "-an",
                "-c:v",
                "libx264",
                "-threads",
                "2",
                "-preset",
                "fast",
                "-b:v",
                "1500k",
                "-maxrate",
                "2000k",
                "-bufsize",
                "3000k",
                "-pix_fmt",
                "yuv420p",
                "-r",
                "25",
                "-map_metadata",
                "-1",
                str(output),
            ],
            check=True,
        )
        duration = float(
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(output),
                ]
            )
        )
        segments.append({"name": name, "duration_seconds": duration})
        parts.append(output)

    def card(name: str, text: str, duration: int) -> None:
        path = out / f"{name}.txt"
        path.write_text(text)
        render(
            name,
            [
                "-f",
                "lavfi",
                "-i",
                f"color=c=0x12212b:s=1920x1080:r=25:d={duration}",
                "-vf",
                f"drawtext=fontfile={FONT}:textfile={path}:fontcolor=white:fontsize=44:"
                "line_spacing=24:x=90:y=170,setfield=prog",
            ],
        )

    card(
        "intro",
        "When Training Gets Easier\n"
        "Range Collapse and Tracking Drift in\nhumanoid robustness training\n\n"
        "Simulation-only diagnostic study\n"
        "Historical MuJoCo replays are separate from R0/R1/R2.\n"
        "All eight recorded illustration draws are shown.\n"
        "Quantitative MuJoCo panels use 32 draws per condition.",
        10,
    )

    # The existing source contains all eight recorded illustration draws, at each
    # of two scales. Keep all tiles, failed outcomes and original playback speed.
    replay_panels = [
        ("no_dr", 0, 0, "No randomization | Training seed 8600"),
        ("collapsed", 1920, 0, "Shrink-permitted variant A, collapsed | Training seed 8601"),
        ("fixed", 0, 614, "Fixed randomization | Training seed 8601"),
        ("never_shrink", 1920, 614, "Never-shrink | Training seed 8601"),
    ]
    for name, x, y, label in replay_panels:
        path = out / f"{name}_caption.txt"
        path.write_text(label + "\nReplay draws 1-8 | Scale 1.5 then 2.0 | No pushes")
        footer = out / f"{name}_footer.txt"
        footer.write_text(
            "Historical illustration | DR policies: seed 8601; no DR: seed 8600.\n"
            "Original tile outcomes retained; failed trials freeze at termination.\n"
            "No matched R0/R1 trajectory or world-path error is shown."
        )
        render(
            name,
            [
                "-i",
                str(args.source),
                "-vf",
                f"crop=1920:614:{x}:{y},pad=1920:1080:0:200:color=0x12212b,"
                f"drawtext=fontfile={FONT}:textfile={path}:fontcolor=white:fontsize=34:"
                f"line_spacing=16:x=60:y=55,drawtext=fontfile={FONT}:textfile={footer}:"
                "fontcolor=white:fontsize=28:line_spacing=14:x=60:y=865,setfield=prog",
            ],
        )

    figures = [
        (
            "inversion",
            "return_inversion",
            "Six shrink-permitted runs; twelve scored policies.\n"
            "The collapsed policies have the highest return, but lower external robustness.\n"
            "Range preservation alone is insufficient for robust performance.",
            10,
        ),
        (
            "retention",
            "retention_trajectory",
            "One trained origin, one motion; two continuation seeds.\n"
            "R1 passes all sampled complete retention checks; R0/R2 have no feasible sample.\n"
            "D includes global/local error in both protected conditions; L is completion loss.",
            14,
        ),
    ]
    for name, figure, caption, duration in figures:
        image = ROOT / f"paper/figures/{figure}.png"
        inputs[figure] = sha256(image)
        path = out / f"{name}_caption.txt"
        path.write_text(caption)
        render(
            name,
            [
                "-loop",
                "1",
                "-i",
                str(image),
                "-t",
                str(duration),
                "-vf",
                "scale=1800:760:force_original_aspect_ratio=decrease,"
                "pad=1920:1080:(ow-iw)/2:80:color=white,"
                f"drawtext=fontfile={FONT}:textfile={path}:fontcolor=black:fontsize=30:"
                "line_spacing=14:x=60:y=890,setfield=prog",
            ],
        )

    card(
        "closing",
        "Two measurements for robustness training\n\n"
        "Use fixed external evaluation conditions.\n"
        "Measure task quality relative to the origin.\n\n"
        "All tested R1 threshold-grid gains are positive on both seeds.\n"
        "This is a development tradeoff, not a general superiority result.\n\n"
        "Text and plot code assisted by OpenAI Codex (GPT-6).\n"
        "Recorded simulations; final author review pending.",
        11,
    )

    listing = out / "concat.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts))
    final = out / "diagnostic-video-draft.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(listing),
            "-c",
            "copy",
            "-map_metadata",
            "-1",
            "-movflags",
            "+faststart",
            str(final),
        ],
        check=True,
    )
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(final),
            ]
        )
    )
    stream = probe["streams"][0]
    if not (
        float(probe["format"]["duration"]) <= 180
        and final.stat().st_size <= 20_000_000
        and stream["height"] >= 480
        and Fraction(stream["r_frame_rate"]) >= 20
    ):
        raise ValueError("Video does not satisfy the checked conference media limits")
    frame_flags = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_frames",
                "-show_entries",
                "frame=interlaced_frame",
                "-of",
                "json",
                str(final),
            ]
        )
    )["frames"]
    if not frame_flags or any(frame["interlaced_frame"] for frame in frame_flags):
        raise ValueError("Progressive scan was not established for every decoded frame")
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"], check=True)
    probe["format"]["filename"] = final.name
    receipt = {
        "kind": "existing_footage_diagnostic_video",
        "new_simulation": False,
        "selection_rule": "All eight existing illustration draws (1-8), both scales, all four policies",
        "replay_training_seeds": {
            "no_dr": 8600,
            "collapsed_A": 8601,
            "fixed": 8601,
            "never_shrink": 8601,
        },
        "input_sha256": inputs,
        "builder_sha256": sha256(Path(__file__)),
        "output_sha256": sha256(final),
        "segments": segments,
        "probe": probe,
        "complete_decode": "passed",
        "progressive_frames_checked": len(frame_flags),
        "visual_inspection": "pending",
        "human_scientific_review": "pending",
        "author_approval": "pending",
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "path": str(final),
                "bytes": final.stat().st_size,
                "seconds": probe["format"]["duration"],
            }
        )
    )


if __name__ == "__main__":
    main()
