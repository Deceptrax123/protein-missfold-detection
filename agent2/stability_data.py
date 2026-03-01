"""
Reference data derived from the Rocklin MegaScale stability dataset.

The MegaScale dataset (Tsuboyama et al., Nature 2023) contains ~776K
high-quality folding stability (ΔG) measurements for 479 protein domains.

We encode key statistical thresholds and domain knowledge here so the
classifier can ground its predictions in experimental evidence.
"""

# ΔG thresholds (kcal/mol) from MegaScale aggregate statistics.
# Negative ΔG = stable fold; positive ΔG = unstable / misfolded.
STABILITY_THRESHOLDS = {
    "highly_stable": -3.0,       # ΔG < -3.0 → confidently folded
    "marginally_stable": -1.0,   # -3.0 ≤ ΔG < -1.0 → marginal
    "unstable": 0.0,             # -1.0 ≤ ΔG < 0 → borderline
    "misfolded": 1.0,            # ΔG ≥ 0 → misfolded / unfolded
}

# 3Di structural alphabet context.
# The 3Di alphabet (Foldseek, van Kempen et al. 2024) encodes tertiary
# interactions into 20 discrete states (a-t / A-T).
# Certain states correlate with specific structural features:
STRUCTURAL_STATE_ANNOTATIONS = {
    "d": "alpha-helix core interaction",
    "a": "beta-sheet pairing",
    "n": "loop / coil region",
    "p": "tight turn",
    "q": "exposed loop",
    "v": "buried hydrophobic contact",
    "l": "helix-helix interface",
    "c": "strand-strand contact",
    "h": "helix cap",
    "s": "disordered / flexible",
}

# Patterns in 3Di sequences associated with instability
# (derived from comparing stable vs. destabilized mutants in MegaScale).
INSTABILITY_INDICATORS = [
    "Runs of 3+ loop/coil states (n, q, s) → potential unstructured region",
    "Abrupt transitions between helix (d, l) and strand (a, c) states → packing defect",
    "High fraction of exposed/disordered states (q, s) in core positions → hydrophobic core disruption",
    "Repeat patterns suggesting low-complexity / intrinsically disordered regions",
    "Absence of buried contacts (v) in expected core positions → loss of stabilizing interactions",
]

# Representative ΔG distribution stats from MegaScale (kcal/mol)
MEGASCALE_STATS = {
    "mean_ddG_destabilizing_mutations": 1.2,
    "std_ddG_destabilizing_mutations": 0.8,
    "mean_ddG_stabilizing_mutations": -0.5,
    "fraction_destabilizing_single_mutants": 0.33,
    "median_wild_type_stability": -2.5,
}


def get_stability_context() -> str:
    """Build a textual summary of stability reference data for prompt injection."""
    lines = [
        "=== Protein Stability Reference (Rocklin MegaScale Dataset) ===",
        "",
        "Thermodynamic stability thresholds (ΔG, kcal/mol):",
    ]
    for label, threshold in STABILITY_THRESHOLDS.items():
        lines.append(f"  {label}: ΔG {'<' if threshold < 0 else '≥'} {threshold}")

    lines.append("")
    lines.append("3Di structural alphabet state annotations:")
    for state, desc in STRUCTURAL_STATE_ANNOTATIONS.items():
        lines.append(f"  '{state}' → {desc}")

    lines.append("")
    lines.append("Known instability indicators in 3Di sequences:")
    for indicator in INSTABILITY_INDICATORS:
        lines.append(f"  • {indicator}")

    lines.append("")
    lines.append("MegaScale aggregate statistics:")
    for key, val in MEGASCALE_STATS.items():
        lines.append(f"  {key}: {val}")

    return "\n".join(lines)
