#!/usr/bin/env bash
# LUCID H_R2 READOUT -- strictly read-only.
#
# Reads the frozen H_R2 confirmation analysis receipt and the two committed
# preregistrations and prints:
#   [0] completion / abort state of the driver chain
#   [A] the H_R2 pass/fail verdict and its four preregistered components
#   [B] per-seed frontier / in-envelope success + progress AUC, ratchet and fixed
#   [C] ratchet-minus-fixed delta per seed per component
#   [D] the six H_R0 mechanism gates per ratchet seed
#   [E] P1: each newly scored arm's frontier success AUC vs the preregistered
#       recency and uniform t(5) bands (bands are READ from the committed file)
#   [F] P1 informative sub-test (ratchet-minus-fixed > +3.0 pts on BOTH 8600 and 8602)
#   [G] P2: |new fixed@s8600 frontier AUC - prior_value| determinism check
#   [H] downstream gate status (historical bridge / Tier-2 support screen)
#   [I] P3 bands, for reference (not scorable from this receipt)
#
# This script writes NOTHING. It opens no GPU, signals no process, runs no git
# command that mutates state.  Safe to run while the driver is still alive.
#
# usage: readout.sh [ANALYSIS_JSON] [EXPOSURE_PREREG_JSON] [GRID_V2_PREREG_JSON]
set -uo pipefail

ANALYSIS="${1:-/home/linjiw/lucid-sonic/manifests/ratchet_confirmation_20260831/lucid_ratchet_confirmation_analysis.json}"
PREREG="${2:-/home/linjiw/lucid/receipts/manifests/lucid_frontier_exposure_law_preregistration_20260901.json}"
GRIDV2="${3:-/home/linjiw/lucid/receipts/manifests/lucid_frontier_grid_v2_preregistration_20260901.json}"
RAT_ROOT="${LUCID_RAT_ROOT:-/home/linjiw/lucid-sonic/manifests/ratchet_confirmation_20260831}"

PY=/usr/bin/python3

# ---------------------------------------------------------------- [0] state --
echo "=============================================================="
echo " LUCID H_R2 READOUT   (read-only)   $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "=============================================================="
echo
echo "[0] DRIVER / COMPLETION STATE"
echo "    root     : ${RAT_ROOT}"
if [[ -d "${RAT_ROOT}/.complete" ]]; then
    echo "    .complete: PRESENT  -> driver reached the end of main() cleanly"
else
    echo "    .complete: ABSENT   -> driver has NOT finished (or aborted)"
fi
DRIVER_ALIVE=no; kill -0 221231 2>/dev/null && DRIVER_ALIVE=yes
for pid in 221231 411832 411845; do
    if kill -0 "${pid}" 2>/dev/null; then
        echo "    pid ${pid}: ALIVE"
    else
        echo "    pid ${pid}: gone"
    fi
done
echo "    -- one-shot boundary markers (a .started with no single valid receipt = FAIL-CLOSED abort) --"
for d in "${RAT_ROOT}"/training/ratchet_s8600 "${RAT_ROOT}"/training/fixed_s8602 \
         "${RAT_ROOT}"/training/ratchet_s8602; do
    if [[ -d "${d}" ]]; then
        n=$(find "${d}" -maxdepth 1 -type f -name 'curriculum_comparison_ne1024_*.json' | wc -l)
        s=$([[ -e "${d}/.started" ]] && echo started || echo no-marker)
        st="OK"
        if [[ "${s}" == "started" && "${n}" -ne 1 ]]; then
            st=$([[ "${DRIVER_ALIVE}" == "yes" ]] && echo "IN-FLIGHT" || echo "ABORTED-FAIL-CLOSED")
        fi
        printf '    %-56s %-10s receipts=%s  %s\n' "training/$(basename "${d}")" "${s}" "${n}" "${st}"
    else
        printf '    %-56s %s\n' "training/$(basename "${d}")" "not created yet"
    fi
done
for d in "${RAT_ROOT}"/evaluation/ratchet_s8600 "${RAT_ROOT}"/evaluation/fixed_s8600 \
         "${RAT_ROOT}"/evaluation/fixed_s8602 "${RAT_ROOT}"/evaluation/ratchet_s8602; do
    if [[ -d "${d}" ]]; then
        n=$(find "${d}" -maxdepth 1 -type f -name 'curriculum_robustness_ne512_*.json' | wc -l)
        s=$([[ -e "${d}/.started" ]] && echo started || echo no-marker)
        st="OK"
        if [[ "${s}" == "started" && "${n}" -ne 1 ]]; then
            st=$([[ "${DRIVER_ALIVE}" == "yes" ]] && echo "IN-FLIGHT" || echo "ABORTED-FAIL-CLOSED")
        fi
        printf '    %-56s %-10s receipts=%s  %s\n' "evaluation/$(basename "${d}")" "${s}" "${n}" "${st}"
    else
        printf '    %-56s %s\n' "evaluation/$(basename "${d}")" "not created yet"
    fi
done
# combined abort verdict
if [[ -d "${RAT_ROOT}/.complete" ]]; then
    echo "    ==> STATE: COMPLETED. The analysis receipt below is final and immutable."
elif [[ "${DRIVER_ALIVE}" == "yes" ]]; then
    echo "    ==> STATE: STILL RUNNING. Do not read the verdict yet; do not touch the worktree."
else
    echo "    ==> STATE: ABORTED. Driver 221231 is gone and .complete was never created."
    echo "        A boundary assert failed. Diagnose in this order, WITHOUT writing anything:"
    echo "          1. any receipt_dir above marked ABORTED-FAIL-CLOSED = that cell died mid-run."
    echo "             It is FAIL-CLOSED: never resume, never retry, never delete the .started dir."
    echo "             File a from-scratch deviation instead."
    echo "          2. all dirs OK but no analysis file  -> a validate_*_receipt jq assert failed,"
    echo "             or assert_preregistered_state failed (worktree dirty / code or frozen-input"
    echo "             hash mismatch / SONIC HEAD moved)."
    echo "          3. analysis file present (mode 444) but .complete absent -> analyze_ratchet.py"
    echo "             succeeded but the post-hoc jq gate failed (cell_count != 84, paired seeds"
    echo "             != [8600,8601,8602], status not in {pass,fail}, or superiority != false),"
    echo "             OR the replay-compare found the existing analysis irreproducible."
    echo "        NOTE: the driver has NO on-disk log. Its stdout/stderr are pipes into the"
    echo "        controlling agent session (pid 31015). Capture the failing line from that"
    echo "        transcript before it is lost; on-disk evidence is markers + receipts only."
    echo "        Eval/train logs (partial, not the driver's asserts):"
    echo "          /home/linjiw/lucid-sonic/outputs/ratchet_confirmation_20260831"
fi
echo
if [[ ! -f "${ANALYSIS}" ]]; then
    echo "ANALYSIS RECEIPT NOT PRESENT YET: ${ANALYSIS}"
    echo "Nothing to score. Re-run this script once .complete exists."
    exit 0
fi
echo "    analysis : ${ANALYSIS}"
echo "    mode     : $(stat -c '%a' "${ANALYSIS}")   (444 = chmod a-w applied by run_analysis)"
echo "    sha256   : $(sha256sum "${ANALYSIS}" | awk '{print $1}')"
echo "    mtime    : $(stat -c '%y' "${ANALYSIS}")"
echo

# ------------------------------------------------------------------ report --
"${PY}" - "${ANALYSIS}" "${PREREG}" "${GRIDV2}" <<'PY'
import json, pathlib, sys
from pathlib import Path

A = json.loads(Path(sys.argv[1]).read_text())
P = json.loads(Path(sys.argv[2]).read_text())
GRID = Path(sys.argv[3])

METRICS = ("success_rate", "progress_rate")
ENDPOINTS = ("frontier_auc", "in_envelope_auc")
LAT = "lat_50ms"
MODES = ("lucid_ratchet_rg", "fixed")
GATES = (
    ("configuration_gate",),
    ("telemetry_contract", "gate"),
    ("reach_lambda_095_by_step_500", "gate"),
    ("pi_decrease_control", "guard_is_only_legal_decrease_gate"),
    ("pi_decrease_control", "receipt_bind_count_gate"),
    ("terminal_1000_high_lambda_exposure", "gate"),
)
GATE_LABEL = ("config", "telemetry", "reach<=500", "decr-guard", "bind-count", "terminal-1k")


def dig(obj, *path, default=None):
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def fmt(value, width=10, places=6):
    if value is None:
        return "-".rjust(width)
    return f"{value:{width}.{places}f}"


def rule(char="-", n=110):
    print(char * n)


# ------------------------------------------------------------- [A] verdict --
print("[A] H_R2 VERDICT")
rule()
dec = A.get("preregistered_decision", {})
scope = A.get("claim_scope", {})
audit = A.get("instrument_audit", {})
print(f"    kind                                  : {A.get('kind')}")
print(f"    preregistered_decision.status         : {dec.get('status')}   <-- THE H_R2 PASS/FAIL VERDICT")
print(f"    preregistered_decision.mechanism_complete      : {dec.get('mechanism_complete')}")
print(f"    preregistered_decision.mechanism_pass          : {dec.get('mechanism_pass')}")
print(f"    preregistered_decision.capability_components_pass: {dec.get('capability_components_pass')}")
print(f"    preregistered_decision.noninferiority_decision_eligible: {dec.get('noninferiority_decision_eligible')}")
print(f"    preregistered_decision.noninferiority_claim_authorized : {dec.get('noninferiority_claim_authorized')}")
print(f"    preregistered_decision.superiority_claim_authorized    : {dec.get('superiority_claim_authorized')}")
print(f"    preregistered_decision.paired_training_seeds  : {dec.get('paired_training_seeds')}")
print(f"    claim_scope.status                    : {scope.get('status')}")
print(f"    instrument_audit.passed / cell_count  : {audit.get('passed')} / {audit.get('cell_count')}  (expect true / 84)")
print(f"    interpretation: {dec.get('interpretation')}")
print()
print("    four preregistered AUC components (each must pass its own frozen 2-of-3 margin):")
print(f"    {'component':<34}{'margin_pts':>11}{'mean_delta_pts':>16}{'within/paired':>15}{'verdict':>17}")
def comp_row(label, blk):
    margin = blk.get("margin_pts")
    md = blk.get("mean_delta_pts")
    return (f"    {label:<34}"
            f"{('n/a' if margin is None else f'{margin:.3f}'):>11}"
            f"{('n/a' if md is None else f'{md:.4f}'):>16}"
            f"{str(blk.get('within_margin_seeds')) + '/' + str(blk.get('num_paired_seeds')):>15}"
            f"{str(blk.get('verdict')):>17}")


for metric in METRICS:
    for endpoint in ENDPOINTS:
        print(comp_row(metric + ":" + endpoint, dig(A, "ratchet_vs_fixed", metric, endpoint, default={}) or {}))
for metric in METRICS:
    blk = dig(A, "ratchet_vs_fixed", metric, LAT, default={}) or {}
    print(comp_row(metric + ":" + LAT + " (SECONDARY)", blk))
print()

# --------------------------------------------------------- [B] per-seed AUC --
print("[B] PER-SEED AUC  (ratchet = lucid_ratchet_rg, fixed = fixed; normalized trapezoid, rate scale [0,1])")
rule()
seeds = sorted({
    s
    for mode in MODES
    for metric in METRICS
    for endpoint in ENDPOINTS
    for s in (dig(A, "arms", mode, metric, endpoint, "per_seed", default={}) or {})
})
print(f"    {'seed':<7}{'metric':<15}{'endpoint':<17}{'ratchet':>12}{'fixed':>12}{'delta':>12}{'delta_pts':>12}")
for seed in seeds:
    for metric in METRICS:
        for endpoint in ENDPOINTS:
            r = dig(A, "arms", "lucid_ratchet_rg", metric, endpoint, "per_seed", seed, "auc")
            f = dig(A, "arms", "fixed", metric, endpoint, "per_seed", seed, "auc")
            d = None if (r is None or f is None) else r - f
            print(f"    {seed:<7}{metric:<15}{endpoint:<17}{fmt(r,12)}{fmt(f,12)}{fmt(d,12)}"
                  f"{('-'.rjust(12) if d is None else f'{100.0*d:12.4f}')}")
    for metric in METRICS:
        r = dig(A, "arms", "lucid_ratchet_rg", metric, LAT, "per_seed", seed)
        f = dig(A, "arms", "fixed", metric, LAT, "per_seed", seed)
        d = None if (r is None or f is None) else r - f
        print(f"    {seed:<7}{metric:<15}{LAT + ' (2nd)':<17}{fmt(r,12)}{fmt(f,12)}{fmt(d,12)}"
              f"{('-'.rjust(12) if d is None else f'{100.0*d:12.4f}')}")
print()
print("    frontier cells (phys_125/150/175/200), success_rate:")
print(f"    {'seed':<7}{'mode':<19}{'phys_125':>11}{'phys_150':>11}{'phys_175':>11}{'phys_200':>11}{'AUC':>12}")
for seed in seeds:
    for mode in MODES:
        blk = dig(A, "arms", mode, "success_rate", "frontier_auc", "per_seed", seed, default={})
        cells = blk.get("cells", {})
        print(f"    {seed:<7}{mode:<19}" + "".join(fmt(cells.get(c), 11) for c in
              ("phys_125", "phys_150", "phys_175", "phys_200")) + fmt(blk.get("auc"), 12))
print()

# ---------------------------------------------------------- [C] deltas only --
print("[C] RATCHET MINUS FIXED, PER SEED  (per preregistered component; margin is one-sided)")
rule()
print(f"    {'component':<34}{'seed':<8}{'ratchet':>11}{'fixed':>11}{'delta_pts':>12}{'within_margin':>15}{'favorable':>11}")
for metric in METRICS:
    for endpoint in ENDPOINTS:
        blk = dig(A, "ratchet_vs_fixed", metric, endpoint, "per_seed", default={}) or {}
        for seed in sorted(blk):
            b = blk[seed]
            print(f"    {metric + ':' + endpoint:<34}{seed:<8}{fmt(b['ratchet'],11)}{fmt(b['fixed'],11)}"
                  f"{b['delta_pts']:>12.4f}{str(b['within_noninferiority_margin']):>15}"
                  f"{str(b['strictly_favorable']):>11}")
print()

# --------------------------------------------------------- [D] H_R0 gates ---
print("[D] H_R0 MECHANISM GATES  (ratchet arms only; ALL six must read 'pass' on every paired seed)")
rule()
per_seed = dig(A, "mechanism", "per_seed", default={}) or {}
summ = dig(A, "mechanism", "summary", default={}) or {}
print(f"    {'seed':<7}" + "".join(f"{lab:>13}" for lab in GATE_LABEL) + f"{'ALL':>7}")
for seed in sorted(per_seed):
    blk = per_seed[seed]
    vals = [dig(blk, *g, default="MISSING") for g in GATES]
    allp = summ.get("per_seed_all_gates_pass", {}).get(seed)
    print(f"    {seed:<7}" + "".join(f"{str(v):>13}" for v in vals) + f"{str(allp):>7}")
    if any(v == "MISSING" for v in vals):
        print(f"      NOTE seed {seed}: a gate key is absent -- this receipt predates the "
              "confirmation analyzer's six-gate schema; ALL was computed on a shorter gate list.")
print(f"    mechanism.summary.all_available_seeds_pass      : {summ.get('all_available_seeds_pass')}")
print(f"    mechanism.summary.blocking_observed_seeds       : {summ.get('blocking_observed_seeds')}")
print("    detail (first lambda>=0.95 step / blocked PI-decrease rows / unguarded decreases / terminal high-lambda frac):")
for seed in sorted(per_seed):
    blk = per_seed[seed]
    print(f"      seed {seed}: first_reach_step="
          f"{dig(blk, 'reach_lambda_095_by_step_500', 'first_reach_step')}"
          f"  blocked_rows={dig(blk, 'pi_decrease_control', 'blocked_pi_decrease_rows')}"
          f"  actual_decreases={dig(blk, 'pi_decrease_control', 'actual_decrease_rows')}"
          f"  unguarded={dig(blk, 'pi_decrease_control', 'unguarded_decrease_rows')}"
          f"  terminal_high_lambda_fraction={dig(blk, 'terminal_1000_high_lambda_exposure', 'high_lambda_fraction')}")
print()

# ------------------------------------------------------------------- [E] P1 --
print("[E] P1  -- frontier SUCCESS AUC vs the PREREGISTERED bands (bands read from the committed file)")
print(f"    source: {sys.argv[2]}")
rule()
p1 = dig(P, "frozen_predictions", "P1_pending_H_R2_ladders", default={}) or {}
per_arm = p1.get("per_arm", {}) or {}
print(f"    {'arm':<26}{'observed':>11}{'recency pt':>12}{'recency band':>22}{'R':>4}"
      f"{'uniform pt':>12}{'uniform band':>22}{'U':>4}")
p1_rows = []
for arm in sorted(per_arm):
    mode, _, sd = arm.partition("@s")
    seed = sd
    obs = dig(A, "arms", mode, "success_rate", "frontier_auc", "per_seed", seed, "auc")
    row = {"arm": arm, "mode": mode, "seed": seed, "observed": obs}
    cols = ""
    for law in ("recency_H2000", "uniform"):
        band = per_arm[arm].get(law, {}) or {}
        lo, hi, pt = band.get("lo"), band.get("hi"), band.get("point")
        if obs is None or lo is None or hi is None:
            verdict = "?"
        else:
            verdict = "PASS" if (lo <= obs <= hi) else "FAIL"
        row[law] = {"lo": lo, "hi": hi, "point": pt, "verdict": verdict}
        cols += f"{fmt(pt,12,5)}{f'[{lo:.5f}, {hi:.5f}]':>22}{('P' if verdict=='PASS' else ('F' if verdict=='FAIL' else '?')):>4}"
    p1_rows.append(row)
    print(f"    {arm:<26}{fmt(obs,11)}" + cols)
print()
missing = [r["arm"] for r in p1_rows if r["observed"] is None]
if missing:
    print(f"    NOT SCORED IN THIS RECEIPT: {missing}")
rf = [r for r in p1_rows if r["observed"] is not None]
if rf:
    nr = sum(r["recency_H2000"]["verdict"] == "PASS" for r in rf)
    nu = sum(r["uniform"]["verdict"] == "PASS" for r in rf)
    print(f"    P1 RECENCY BAND : {nr}/{len(rf)} scored arms inside band -> "
          f"{'PASS' if nr == len(rf) else 'FAIL'}"
          + ("" if nr == len(rf) else "  (outside: "
             + ", ".join(r["arm"] for r in rf if r["recency_H2000"]["verdict"] != "PASS") + ")"))
    print(f"    P1 UNIFORM BAND : {nu}/{len(rf)} scored arms inside band -> "
          f"{'PASS' if nu == len(rf) else 'FAIL'}"
          + ("" if nu == len(rf) else "  (outside: "
             + ", ".join(r["arm"] for r in rf if r["uniform"]["verdict"] != "PASS") + ")"))
    if len(rf) < 4:
        print(f"    (only {len(rf)} of the 4 preregistered arms are present in this receipt)")
print(f"    falsification weight (from file): {p1.get('falsification_weight')}")
print()

# ---------------------------------------------- [F] P1 informative sub-test --
print("[F] P1 INFORMATIVE SUB-TEST  -- ratchet-minus-fixed POSITIVE on BOTH 8600 and 8602, each gap > +3.0 pts")
rule()
sub_seeds = ["8600", "8602"]
gaps, ok = {}, True
for seed in sub_seeds:
    b = dig(A, "ratchet_vs_fixed", "success_rate", "frontier_auc", "per_seed", seed, default=None)
    if b is None:
        r = dig(A, "arms", "lucid_ratchet_rg", "success_rate", "frontier_auc", "per_seed", seed, "auc")
        f = dig(A, "arms", "fixed", "success_rate", "frontier_auc", "per_seed", seed, "auc")
        g = None if (r is None or f is None) else 100.0 * (r - f)
    else:
        g = b["delta_pts"]
    gaps[seed] = g
    hit = (g is not None and g > 3.0)
    ok = ok and hit
    print(f"    seed {seed}: ratchet-minus-fixed frontier success = "
          f"{'MISSING' if g is None else f'{g:+.4f} pts'}   > +3.0 pts ? {'YES' if hit else 'no'}")
if any(gaps[s] is None for s in sub_seeds):
    print("    SUB-TEST: NOT EVALUABLE (a seed is missing from this receipt)")
else:
    print(f"    SUB-TEST TRIGGERED: {'YES' if ok else 'NO'}"
          f"   (prior probability under pure seed noise SD 0.0157 ~ 0.4%)")
    if ok:
        print("    -> exposure alone does NOT explain the ratchet arm; a non-exposure mechanism")
        print("       (warm-up ramp, RNG divergence, optimizer path) must be investigated.")
    ref = dig(A, "ratchet_vs_fixed", "success_rate", "frontier_auc", "per_seed", "8601", "delta_pts")
    print("    reference (screening seed, NOT part of the sub-test): 8601 gap = "
          + ("MISSING" if ref is None else f"{ref:+.4f} pts"))
print()

# ------------------------------------------------------------------- [G] P2 --
print("[G] P2 DETERMINISM CHECK  -- fixed@s8600 re-scored at the SAME evaluation seed 8700, same panel")
rule()
p2 = dig(P, "frozen_predictions", "P2_determinism_check", default={}) or {}
prior = float(p2.get("prior_value"))
new = dig(A, "arms", "fixed", "success_rate", "frontier_auc", "per_seed", "8600", "auc")
# Every frontier AUC is an exact dyadic rational N/3072 (four 512-env cells, trapezoid
# weights 1/6,1/3,1/3,1/6).  The preregistration stored the PRIOR only to 6 dp, so a raw
# |new - 0.904622| reads ~3.96e-07 even under perfect bit-determinism.  Report the literal
# difference the prediction asks for, and settle the verdict on the exact rational.
DENOM = 3072
prior_n = round(prior * DENOM)
print(f"    prior_value (from committed preregistration) : {prior}")
print(f"    prior as the exact receipt rational          : {prior_n}/{DENOM} = {prior_n / DENOM!r}")
print(f"    (the committed file stores a 6-dp rounding; |{prior_n}/{DENOM} - {prior}| = "
      f"{abs(prior_n / DENOM - prior):.3e})")
if new is None:
    print("    new fixed@s8600 frontier success AUC        : MISSING from this receipt")
    print("    VERDICT: NOT EVALUABLE")
else:
    diff = abs(new - prior)
    new_scaled = new * DENOM
    exact = abs(new_scaled - prior_n) < 1e-9
    print(f"    new fixed@s8600 frontier success AUC        : {new!r}")
    print(f"    new as N/{DENOM}                             : {new_scaled:.6f}"
          f"   (expect exactly {prior_n})")
    print(f"    |new - {prior}|  (as predicted)         : {diff!r}")
    if diff == 0.0:
        print("    VERDICT: EXACTLY 0 -- DETERMINISM HOLDS (and the prior was stored at full precision)")
    elif exact:
        print(f"    VERDICT: DETERMINISM HOLDS. The literal difference {diff:.3e} is ENTIRELY the")
        print(f"             preregistration's 6-dp transcription of {prior_n}/{DENOM}; the re-scored")
        print( "             AUC is bit-identical to the prior. This is NOT evaluator or panel drift.")
    else:
        print(f"    VERDICT: NONZERO BEYOND TRANSCRIPTION -> EVALUATOR OR PANEL DRIFT")
        print(f"             {diff!r} = {100.0 * diff:.6f} pts; N differs by "
              f"{new_scaled - prior_n:+.6f} of {DENOM}ths")
        print( "             Same checkpoint, same evaluation seed 8700, same 512-alias panel, so this")
        print( "             is NOT sampling noise. File it as an instrument deviation BEFORE using any")
        print( "             P1 or P3 number, and before activating the historical bridge.")
    cells = dig(A, "arms", "fixed", "success_rate", "frontier_auc", "per_seed", "8600", "cells", default={}) or {}
    if cells:
        print("    per-cell (x512): " + "  ".join(
            f"{c}={cells[c] * 512:.1f}" for c in ("phys_125", "phys_150", "phys_175", "phys_200") if c in cells))
print(f"    falsification weight (from file): {p2.get('falsification_weight')}")
print()

# ------------------------------------------------- [H] downstream gate state --
print("[H] DOWNSTREAM GATE STATUS")
rule()
status = dec.get("status")
mech_all = summ.get("per_seed_all_gates_pass", {}) or {}
bridge_checks = [
    ("kind == lucid_ratchet_analysis", A.get("kind") == "lucid_ratchet_analysis"),
    ("instrument_audit.passed", audit.get("passed") is True),
    ("instrument_audit.cell_count == 84", audit.get("cell_count") == 84),
    ("instrument_audit.paired_training_seeds == [8600,8601,8602]",
     audit.get("paired_training_seeds") == ["8600", "8601", "8602"]),
    ("claim_scope.status == three_seed_decision", scope.get("status") == "three_seed_decision"),
    ("claim_scope.noninferiority_decision_eligible", scope.get("noninferiority_decision_eligible") is True),
    ("decision.status in {pass, fail}", status in ("pass", "fail")),
    ("decision.mechanism_complete", dec.get("mechanism_complete") is True),
    ("decision.mechanism_pass", dec.get("mechanism_pass") is True),
    ("decision.paired_training_seeds == [8600,8601,8602]",
     dec.get("paired_training_seeds") == ["8600", "8601", "8602"]),
    ("decision.noninferiority_decision_eligible", dec.get("noninferiority_decision_eligible") is True),
    ("decision.superiority_claim_authorized == false", dec.get("superiority_claim_authorized") is False),
    ("mechanism per_seed_all_gates_pass == {8600:t,8601:t,8602:t}",
     mech_all == {"8600": True, "8601": True, "8602": True}),
    ("mechanism.summary.all_available_seeds_pass", summ.get("all_available_seeds_pass") is True),
    ("inputs.robustness_receipts length == 6", len(dig(A, "inputs", "robustness_receipts", default=[]) or []) == 6),
    ("inputs.training_receipts length == 3", len(dig(A, "inputs", "training_receipts", default=[]) or []) == 3),
]
tier2_checks = bridge_checks[:6] + [
    ("decision.status == pass  (STRICT)", status == "pass"),
    ("decision.mechanism_pass", dec.get("mechanism_pass") is True),
    ("decision.capability_components_pass", dec.get("capability_components_pass") is True),
    ("decision.noninferiority_claim_authorized", dec.get("noninferiority_claim_authorized") is True),
    ("decision.superiority_claim_authorized == false", dec.get("superiority_claim_authorized") is False),
    ("mechanism.summary.all_available_seeds_pass", summ.get("all_available_seeds_pass") is True),
]
print("    HISTORICAL BRIDGE (P3 instrument) -- run_ratchet_historical_bridge.sh validate_h_r2_gate")
print("      accepts decision.status 'pass' OR 'fail'; requires ALL H_R0 mechanism gates")
for label, okc in bridge_checks:
    print(f"      [{'ok' if okc else 'XX'}] {label}")
print(f"      => BRIDGE ACTIVATION: {'UNBLOCKED by this receipt' if all(c for _, c in bridge_checks) else 'BLOCKED'}")
print()
print("    TIER-2 SUPPORT SCREEN -- run_support_screen.sh assert_h_r2_passed")
print("      requires decision.status == 'pass' (a FAIL hard-blocks Tier-2)")
for label, okc in tier2_checks:
    print(f"      [{'ok' if okc else 'XX'}] {label}")
print(f"      => TIER-2 ACTIVATION: {'UNBLOCKED by this receipt' if all(c for _, c in tier2_checks) else 'BLOCKED'}")
print()

# ------------------------------------------------------------------- [I] P3 --
print("[I] P3 (PRIMARY) -- NOT scorable from this receipt; needs the 42-cell historical bridge")
rule()
p3 = dig(P, "frozen_predictions", "P3_collapse_arm_PRIMARY", default={}) or {}
print(f"    arm        : lucid_rg seed 8601 (predeclared anti-gating collapse, final lambda 0.062)")
print(f"    comparator : fixed@s8601 = {dig(p3, 'comparator', 'fixed@s8601')}")
print(f"    recency    : point {dig(p3,'recency_H2000','point')}  band "
      f"[{dig(p3,'recency_H2000','lo')}, {dig(p3,'recency_H2000','hi')}]  E={dig(p3,'recency_H2000','exposure')}")
print(f"    uniform    : point {dig(p3,'uniform','point')}  band "
      f"[{dig(p3,'uniform','lo')}, {dig(p3,'uniform','hi')}]  E={dig(p3,'uniform','exposure')}")
AMEND = pathlib.Path("/home/linjiw/lucid/receipts/manifests/lucid_frontier_preregistration_amendment_20260901.json")
if AMEND.is_file():
    A = json.loads(AMEND.read_text())
    print(f"    AMENDMENT {AMEND.name} IS IN FORCE (parent commit {A.get('parent_commit')}):")
    print("      A1  the INTERVAL OBJECTS are authoritative, NOT the outcomes_exhaustive prose edges.")
    print("          authoritative: recency [0.67376, 0.77569]   uniform [0.76087, 0.89047]")
    print("      A2  P2 is an exact-rational determinism check: round(new*3072) == 2779. Not |diff|==0.")
    print("      A3  the held-out band costs ~16% of resolution (spread +18.5%, noise +40.9%);")
    print("          the parent file's 'costs no resolution' wording is superseded.")
    print("      A5  P3 must be scored BEFORE any evaluator change (evaluator byte-pinned at 308e2415).")
else:
    print("    WARNING: amendment file not found; the parent file states the P3 edges twice with")
    print("             different roundings. Prefer the interval objects.")
print("    decision buckets (edges restated per amendment A1):")
print(f"      {'law_falsified_low':<38} < 0.67376")
print(f"      {'recency_favored':<38} [0.67376, 0.76087)")
print(f"      {'ambiguous_no_discrimination':<38} [0.76087, 0.77569]   <- discriminates nothing")
print(f"      {'uniform_favored':<38} (0.77569, 0.881836)")
print(f"      {'collapse_is_cosmetic_LAW_FALSIFIED':<38} >= 0.881836")
print(f"    global falsification rule: {P.get('global_falsification')}")
print()
print(f"    sequencing (grid v2 preregistration {GRID}):")
for step in (json.loads(GRID.read_text()).get("sequencing", []) if GRID.is_file() else []):
    print(f"      - {step}")
print()
rule("=")
print(f"H_R2 VERDICT = {status!r}    |    bridge {'UNBLOCKED' if all(c for _, c in bridge_checks) else 'BLOCKED'}"
      f"    |    Tier-2 {'UNBLOCKED' if all(c for _, c in tier2_checks) else 'BLOCKED'}")
rule("=")
PY
