#!/usr/bin/env python3
"""How much of a full-intensity batch is already as easy as an earlier stage?

CORRECTED 2026-09-03. The first version of this tool answered with a single number,
182 of 1024 environments, and that number was wrong. It raised the per-channel
probability to the SIXTH power, once per channel, when the draws are per DIMENSION:
the joint-offset term alone draws independently for each of 29 joints, mass for
three bodies, centre of mass for three axes, pushes for six components, the
material for three coefficients, and the delay once. That is 45 independent scalar
draws per episode, not 6, and the answer moves by eleven orders of magnitude across
that range. The exponent is not a detail; it IS the answer.

So this tool no longer reports one number. It reports the whole curve against
effective dimensionality, because how many dimensions actually drive difficulty is
something we do not know and did not measure. Twenty-nine joint offsets of one
hundredth of a radian probably do not each contribute as much as a push impulse
does, so the truth is somewhere between the extremes and closer to the low end,
but "probably" is not a measurement.

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

    stages = [0.5, 0.75, 0.9]
    #: How many INDEPENDENT scalar draws an episode makes. 45 is the count from the
    #: configs; the lower numbers are what it would be if difficulty were dominated
    #: by a few channels rather than spread evenly over all of them.
    dimensionalities = [1, 3, 6, 10, 20, 45]
    rows = []
    for k in dimensionalities:
        rows.append({
            "effective_dimensions": k,
            **{f"envs_per_iteration_no_harder_than_stage_{s}": round(a.envs * (s ** k), 4)
               for s in stages},
        })

    report = {
        "kind": "lucid_nesting_calculus",
        "schema_version": 2,
        "supersedes": ("schema 1 of this receipt, which reported 182 of 1024 environments as if it "
                       "were a measurement. It raised the per-channel probability to the sixth "
                       "power when the draws are per dimension and there are 45 of them, and the "
                       "answer spans eleven orders of magnitude over the plausible range."),
        "what_survives_exactly": ("Per PARAMETER, the supports are nested: the stage-s range sits "
                                  "inside the full range and a full-intensity draw lands in it with "
                                  "probability exactly s. No parameter VALUE is withheld by fixed "
                                  "randomization that a curriculum would introduce."),
        "what_does_not_survive": ("The claim that whole EPISODES as easy as an earlier stage appear "
                                  "in every batch. That is the joint event across every independent "
                                  "draw, and its frequency depends on how many dimensions actually "
                                  "drive difficulty, which we have not measured. At six effective "
                                  "dimensions it is 182 environments per iteration; at the 45 the "
                                  "configs actually draw, it is 0.002."),
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
            "Exact and unaffected by the correction: on EVERY individual parameter, a "
            "full-intensity draw is inside the half-intensity range half the time. Fixed "
            "randomization withholds no parameter value that a curriculum would introduce.",
            "Not established: how often a whole episode is as easy as an earlier stage. Over the "
            "45 independent draws the configs actually make it is essentially never; if difficulty "
            "is dominated by a handful of channels it is hundreds of environments per iteration. "
            "We did not measure which, so this cannot carry the weight the first version put on it.",
            "The consequence for the project is therefore weaker than first written. Nesting alone "
            "does not explain why no curriculum has won here; it rules out one explanation, that a "
            "curriculum introduces parameter values fixed randomization never shows.",
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

    print(f"{'effective dims':>14} " + " ".join(f"{'stage ' + str(s):>14}" for s in stages)
          + f"   (of {a.envs} environments per iteration)")
    for r in rows:
        print(f"{r['effective_dimensions']:>14} " +
              " ".join(f"{r[f'envs_per_iteration_no_harder_than_stage_{s}']:>14.4g}" for s in stages))
    print()
    for line in report["reading"]:
        print(" -", line)
    print(f"\nreceipt -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
