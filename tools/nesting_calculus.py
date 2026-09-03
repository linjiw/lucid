#!/usr/bin/env python3
"""How much of a full-intensity batch is already as easy as an earlier stage?

The claim this quantifies: fixed domain randomization as configured here is
already a curriculum, so staging toward its distribution cannot withhold the easy
episodes it keeps supplying.

The argument is exact rather than statistical. ``dr_scaling.scale_range`` maps a
configured range affinely about its nominal, so the stage-``s`` range is

    [nominal - s*dev_lo,  nominal + s*dev_hi]

which sits inside the full range and has exactly ``s`` times its width. A draw at
full intensity is uniform on the full range, so:

* the probability that it lands inside the stage-``s`` range is exactly ``s``, for
  every channel, whatever the units or the asymmetry; and
* conditioned on landing there it is uniform on that range, which is precisely the
  stage-``s`` distribution.

So a full-intensity episode is not merely *sometimes* easy. Its easy sub-population
is distributionally identical to the stage it would have been curriculum-ed
through. Across ``C`` independently drawn channels the chance that one episode is
no harder than stage ``s`` on all of them is ``s**C``, and with 1024 environments
redrawing every episode the expected count per iteration is ``1024 * s**C``.

This holds for any affine-about-nominal range and needs no simulation, which is
why it is computed here rather than measured.

usage: nesting_calculus.py [--envs 1024] [--channels 6]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

#: The six channels the LUCID preset schedules, with the configured range and its
#: nominal, read from the event configs. Only the WIDTH matters to the result, so
#: the units differ harmlessly between rows.
CHANNELS = {
    "randomize_rigid_body_mass": {"range": [0.8, 1.5], "nominal": 1.0, "units": "mass multiplier"},
    "add_joint_default_pos": {"range": [-0.01, 0.01], "nominal": 0.0, "units": "rad offset"},
    "base_com": {"range": [-0.05, 0.05], "nominal": 0.0, "units": "m, the widest axis"},
    "push_robot": {"range": [-0.5, 0.5], "nominal": 0.0, "units": "m/s, planar"},
    "physics_material": {"range": [0.3, 1.6], "nominal": 0.95, "units": "static friction"},
    "randomize_action_delay": {"range": [0.0, 8.0], "nominal": 0.0, "units": "physics steps"},
}


def stage_range(spec: dict, s: float) -> list[float]:
    lo, hi = spec["range"]
    n = spec["nominal"]
    return [n - s * (n - lo), n + s * (hi - n)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--envs", type=int, default=1024)
    ap.add_argument("--channels", type=int, default=len(CHANNELS))
    ap.add_argument("--out", type=Path,
                    default=Path("receipts/analysis/lucid_nesting_calculus_20260903.json"))
    a = ap.parse_args(argv)

    stages = [0.25, 0.5, 0.6, 0.75, 0.9]
    rows = []
    for s in stages:
        per_channel = s
        joint = s ** a.channels
        rows.append({
            "stage": s,
            "share_of_draws_inside_the_stage_range_per_channel": round(per_channel, 4),
            "share_of_episodes_no_harder_than_the_stage_on_every_channel": round(joint, 6),
            "expected_such_environments_per_iteration": round(a.envs * joint, 1),
        })

    report = {
        "kind": "lucid_nesting_calculus",
        "schema_version": 1,
        "claim": ("Fixed randomization at full intensity already supplies, every iteration, a "
                  "sub-population of episodes distributionally identical to each earlier stage "
                  "of any curriculum that ramps toward it."),
        "why_exact": ("scale_range is affine about the nominal, so the stage-s range has exactly s "
                      "times the full width and sits inside it. A uniform full-intensity draw "
                      "therefore lands inside it with probability exactly s, and conditioned on "
                      "landing there is uniform on it, which IS the stage-s distribution."),
        "environments": a.envs,
        "channels_counted": a.channels,
        "per_channel_ranges": {k: {**v, "stage_0.5_range": stage_range(v, 0.5)}
                               for k, v in CHANNELS.items()},
        "table": rows,
        "reading": [
            f"At full intensity {rows[1]['share_of_draws_inside_the_stage_range_per_channel']:.0%} of draws on "
            "EVERY channel are already inside the half-intensity range.",
            f"{rows[3]['expected_such_environments_per_iteration']:.0f} of {a.envs} environments per iteration are "
            "no harder than a 0.75 stage on all six channels at once, and "
            f"{rows[1]['expected_such_environments_per_iteration']:.0f} are no harder than a 0.5 stage.",
            "A curriculum that ramps intensity therefore cannot show the policy anything fixed "
            "randomization withholds, and cannot withhold the easy episodes it supplies. It can "
            "only change how often each is seen.",
        ],
        "what_would_break_it": [
            "A target distribution that is CONCENTRATED rather than a range: a point target has no "
            "easy sub-population, which is why the point-versus-range arms exist.",
            "A channel drawn once per RUN rather than per episode, so a batch is homogeneous.",
            "A non-affine schedule that moves a range away from its nominal instead of widening it "
            "about it, so earlier stages are not nested inside the target.",
        ],
        "not_verified": [
            "This is a property of the sampling scheme, not a measurement of learning. It says a "
            "curriculum cannot change WHICH episodes exist, not that changing their frequency "
            "cannot matter at all.",
            "Channels are treated as independent draws, which they are here, and the push channel "
            "fires on an interval rather than at every reset, so its share is an approximation.",
        ],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=1) + "\n")

    print(f"{'stage':>6} {'per channel':>12} {'all six':>10} {'envs/iter':>10}")
    for r in rows:
        print(f"{r['stage']:>6.2f} {r['share_of_draws_inside_the_stage_range_per_channel']:>11.0%} "
              f"{r['share_of_episodes_no_harder_than_the_stage_on_every_channel']:>10.4f} "
              f"{r['expected_such_environments_per_iteration']:>10.1f}")
    print()
    for line in report["reading"]:
        print(" -", line)
    print(f"\nreceipt -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
