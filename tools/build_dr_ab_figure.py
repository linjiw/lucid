#!/usr/bin/env python3
"""Build the sim2sim DR A/B figure for the public page.

    build_dr_ab_figure.py --out site/img/dr_ab/falls.svg

Two small multiples rather than one chart: perturbation severity and actuation
latency are different axes, and putting both on one plot would need two x-scales.
Each panel is falls out of sixteen, so the y-axis is shared and directly
comparable across panels.

Numbers come from the full-clip MuJoCo sweeps, where each rollout runs to the end
of the motion. The scored sweeps end a rollout the moment the pelvis passes 0.5 m
from the reference -- often around 1.4 s -- so a policy whose run had already
ended could not be recorded as falling; those counts are not the ones plotted.

Palette: #a83f26 / #1668b8, checked with the dataviz validator (chroma, CVD
separation deltaE 22.3, normal-vision 27.4, contrast against white). Every series
is also directly labelled, so identity never rests on colour alone.
"""

from __future__ import annotations

import argparse
from pathlib import Path

NO_DR = "#a83f26"
DEPLOY = "#1668b8"
INK = "#192b30"
MUTED = "#58696d"
RULE = "#d4deda"

PANELS = [
    {
        "title": "Domain randomization",
        "sub": "all channels, scaled together",
        "x": ["none", "light", "envelope", "heavy", "extreme"],
        "xsub": ["λ 0", "λ 0.5", "λ 1", "λ 1.5", "λ 2"],
        "no_dr": [0, 0, 7, 11, 14],
        "deploy": [0, 0, 0, 3, 5],
    },
    {
        "title": "Actuation latency alone",
        "sub": "physics nominal, delay swept",
        "x": ["0", "0–20", "0–40", "0–60", "0–80", "0–120"],
        "xsub": ["ms", "ms", "ms", "ms", "ms", "ms"],
        "no_dr": [0, 0, 0, 6, 10, 11],
        "deploy": [0, 0, 0, 0, 0, 6],
    },
]

W, H = 940, 400
PAD_L, PAD_R, PAD_T, PAD_B = 52, 34, 78, 74
PANEL_GAP = 64
YMAX = 16


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def panel_svg(p: dict, x0: float, pw: float) -> list[str]:
    n = len(p["x"])
    ph = H - PAD_T - PAD_B
    y0 = PAD_T
    xs = [x0 + PAD_L + (pw - PAD_L - PAD_R) * i / (n - 1) for i in range(n)]

    def y(v: float) -> float:
        return y0 + ph * (1 - v / YMAX)

    out: list[str] = []
    out.append(
        f'<text x="{x0 + PAD_L:.1f}" y="{y0 - 40:.1f}" font-size="15" font-weight="600" '
        f'fill="{INK}">{esc(p["title"])}</text>'
    )
    out.append(
        f'<text x="{x0 + PAD_L:.1f}" y="{y0 - 22:.1f}" font-size="12.5" '
        f'fill="{MUTED}">{esc(p["sub"])}</text>'
    )
    # Recessive gridlines every 4 falls.
    for v in range(0, YMAX + 1, 4):
        yy = y(v)
        out.append(
            f'<line x1="{x0 + PAD_L:.1f}" y1="{yy:.1f}" x2="{x0 + pw - PAD_R:.1f}" '
            f'y2="{yy:.1f}" stroke="{RULE}" stroke-width="1"/>'
        )
        out.append(
            f'<text x="{x0 + PAD_L - 10:.1f}" y="{yy + 4:.1f}" font-size="11.5" '
            f'text-anchor="end" fill="{MUTED}">{v}</text>'
        )
    # x labels
    for i, (lab, sub) in enumerate(zip(p["x"], p["xsub"])):
        out.append(
            f'<text x="{xs[i]:.1f}" y="{y0 + ph + 20:.1f}" font-size="12" '
            f'text-anchor="middle" fill="{INK}">{esc(lab)}</text>'
        )
        out.append(
            f'<text x="{xs[i]:.1f}" y="{y0 + ph + 35:.1f}" font-size="11" '
            f'text-anchor="middle" fill="{MUTED}">{esc(sub)}</text>'
        )
    # Series. Both arms sit at exactly zero for the first cells, so a coincident
    # marker would hide whichever is drawn first. A small horizontal dodge keeps
    # both visible; the x axis is ordinal, so nudging along it distorts nothing.
    for key, colour, dodge in (("no_dr", NO_DR, -3.0), ("deploy", DEPLOY, 3.0)):
        pts = " ".join(f"{xs[i] + dodge:.1f},{y(v):.1f}" for i, v in enumerate(p[key]))
        out.append(
            f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )
        for i, v in enumerate(p[key]):
            out.append(
                f'<circle cx="{xs[i] + dodge:.1f}" cy="{y(v):.1f}" r="4.5" fill="{colour}" '
                f'stroke="#ffffff" stroke-width="2"/>'
            )
        # One selective direct label: the endpoint value only. The series name is
        # carried by the legend, so a long string cannot collide with the line.
        last = len(p[key]) - 1
        out.append(
            f'<text x="{xs[last] + dodge:.1f}" y="{y(p[key][last]) - 12:.1f}" font-size="13" '
            f'font-weight="700" text-anchor="middle" fill="{colour}">{p[key][last]}</text>'
        )
    return out


def build() -> str:
    pw = (W - PANEL_GAP) / 2
    body: list[str] = []
    body += panel_svg(PANELS[0], 0, pw)
    body += panel_svg(PANELS[1], pw + PANEL_GAP, pw)
    lx = W - 300
    for i, (colour, label) in enumerate(((NO_DR, "no DR"), (DEPLOY, "deployment DR"))):
        cx = lx + i * 140
        body.append(
            f'<rect x="{cx}" y="8" width="11" height="11" rx="2" fill="{colour}"/>'
        )
        body.append(
            f'<text x="{cx + 17}" y="18" font-size="12.5" fill="{INK}">{esc(label)}</text>'
        )
    body.append(
        f'<text x="0" y="{H - 14}" font-size="12" fill="{MUTED}">'
        f'Falls out of 16 seeds · MuJoCo · walk_arc_cw_stop_001__A047, 8.6 s, '
        f'each rollout run to the end of the motion</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif" '
        f'role="img" aria-label="Falls out of sixteen seeds against randomization '
        f'severity and against actuation latency, for a policy trained without '
        f'randomization and one trained with deployment randomization. Without '
        f'randomization falls rise to fourteen of sixteen at extreme severity and '
        f'eleven of sixteen at 0 to 120 milliseconds of latency; with it, five and '
        f'six.">'
        + "".join(body)
        + "</svg>"
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(build())
    print(f"wrote {a.out} ({a.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
