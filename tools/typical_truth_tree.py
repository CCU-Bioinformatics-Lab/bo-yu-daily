"""Typical HP-aware truth tree: the control for the stress-test tree in draw_hp_truth_tree.py.

Same data model as draw_hp_truth_tree.py (SNV, GENOME, LOST, PROP, CHILDREN). Each parameter
is set from measured TRACERx 421 / PCAWG / HG008 values; see
lab_report/2026-10-25_typical_truth_tree/README.md for the evidence per parameter.

  purity 0.40          TRACERx 421 tumour median 0.39
  3 clones, linear     TRACERx 421 single region: 73% linear; PCAWG 21% have 2 subclones
  CCF 1.00/0.58/0.29   TRACERx 421 single-region subclone CCF median 0.58, q25 0.29
  70% SNVs clonal      TRACERx 100 median 30% subclonal
  seg A HP1 +1 gain    subclonal (C2); early/clonal = 3/(3+7) = 0.30 (PCAWG median 0.28)
  seg D cnLOH          subclonal (C3 only); loses t6 -> 3/200 = 1.5% SNVs lost
  segment shares       A 6%, D 4%, C 90% of SNVs (subclonal CN ~10%; PCAWG median 7.6%)

install(T) copies these globals into the draw_hp_truth_tree module, so its helpers
(ccf, copies, snv_truth, dominant_cn, ...) work on this tree unchanged.
"""

PURITY = 0.40
PROP = {"C1": 0.42, "C2": 0.29, "C3": 0.29}  # fraction of tumour cells
CHILDREN = {"C1": ["C2"], "C2": ["C3"], "C3": []}
SEGS = ["A", "C", "D"]

# SNV role -> (origin clone, HP, segment)
SNV = {
    "t1": ("C1", "HP1", "A"),  # before the HP1 gain -> multiplicity 2 in C2/C3
    "t2": ("C1", "HP2", "A"),  # on the non-gained HP -> multiplicity 1
    "t3": ("C1", "HP1", "C"), "t4": ("C1", "HP2", "C"),
    "t5": ("C1", "HP1", "D"),  # before cnLOH -> multiplicity 2 in C3
    "t6": ("C1", "HP2", "D"),  # lost in C3 by cnLOH
    "t7": ("C2", "HP1", "A"),  # after the gain -> multiplicity 1
    "t8": ("C2", "HP1", "C"), "t9": ("C2", "HP2", "C"),
    "t10": ("C3", "HP1", "D"),  # after cnLOH -> multiplicity 1
    "t11": ("C3", "HP1", "C"), "t12": ("C3", "HP2", "C"),
}

# SNVs per role (200 in total: C1 140, C2 36, C3 24)
N_SNV = {"t1": 3, "t2": 7, "t3": 62, "t4": 62, "t5": 3, "t6": 3,
         "t7": 2, "t8": 17, "t9": 17, "t10": 2, "t11": 11, "t12": 11}

GENOME = {
    "N": {s: {"HP1": [[]], "HP2": [[]]} for s in SEGS},
    "C1": {"A": {"HP1": [["t1"]], "HP2": [["t2"]]},
           "C": {"HP1": [["t3"]], "HP2": [["t4"]]},
           "D": {"HP1": [["t5"]], "HP2": [["t6"]]}},
    "C2": {"A": {"HP1": [["t1", "t7"], ["t1"]], "HP2": [["t2"]]},
           "C": {"HP1": [["t3", "t8"]], "HP2": [["t4", "t9"]]},
           "D": {"HP1": [["t5"]], "HP2": [["t6"]]}},
    "C3": {"A": {"HP1": [["t1", "t7"], ["t1"]], "HP2": [["t2"]]},
           "C": {"HP1": [["t3", "t8", "t11"]], "HP2": [["t4", "t9", "t12"]]},
           "D": {"HP1": [["t5", "t10"], ["t5"]], "HP2": []}},
}
LOST = {"C3": [("D", "HP2", "t6")]}


def install(T):
    """Point the draw_hp_truth_tree module T at this tree."""
    for name in ("PURITY", "PROP", "CHILDREN", "SEGS", "SNV", "GENOME", "LOST", "N_SNV"):
        setattr(T, name, globals()[name])
    T.CELL = {"N": 1 - PURITY, **{c: PURITY * p for c, p in PROP.items()}}
