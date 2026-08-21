# Model outputs

## 1. Clone topology

```text
normal cells
|
└── tumor_root
    |
    └── C1
        ├── C2
        └── C3
```


## 2. CCF output (PhyloWGS-style node labels)

```text
normal cells
|
+-- tumor_root
    |
    +-- C1  [CCF = phi_C1 = 1.00 (100%)]
        +-- C2  [CCF = phi_C2 = 0.60 (60%)]
        `-- C3  [CCF = phi_C3 = 0.25 (25%)]
```

`phi_v` is the cumulative cancer-cell fraction for clone `v` and all of its
descendants; it is not the local mass `eta_v`.

The percentages are illustrative. The actual run supplies the values in the
`phi` vector.

| clone | CCF |
|---|---|
| C1 | `phi_C1` → `1.00` (100%) |
| C2 | `phi_C2` → `0.60` (60%) |
| C3 | `phi_C3` → `0.25` (25%) |


## 3. SNV-to-clone assignment

```text
SNV_A, SNV_B ──▶ C1
SNV_C  ──▶ C2
SNV_D, SNV_E ──▶ C3
```
