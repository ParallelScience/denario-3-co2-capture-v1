# Data Description: CO₂ Capture Materials from the Materials Project

## Overview

This dataset contains DFT-computed properties for 40,923 inorganic materials relevant to solid-sorbent CO₂ capture, drawn from the Materials Project database (April 2026). The materials are oxygen-containing compounds that include at least one element commonly used in CO₂ capture sorbents: Ca, Mg, Li, Na, K, Ba, Sr, Mn, Fe, Co, Ni, Cu, Zn, Al. The dataset spans both oxide precursors (the sorbent before capture) and carbonates (the CO₂-reacted products), enabling thermodynamic screening of capture reactions of the form:

    MₓOᵧ + CO₂ → MₓCO₃ + (byproducts)

All entries are near-thermodynamically-stable (energy above hull ≤ 0.1 eV/atom), meaning they are experimentally accessible candidates rather than hypothetical high-energy phases.

---

## File

### `/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet`

Parquet file, **40,923 rows × 15 columns**, readable with `pandas.read_parquet(...)` (requires `pyarrow`).

| Column | Type | Description | Range / Notes |
|---|---|---|---|
| `material_id` | str | Materials Project ID (e.g. `mp-2341`) | Unique identifier |
| `formula` | str | Reduced chemical formula (e.g. `CaCO3`, `MgO`) | Human-readable |
| `elements` | str | Comma-separated list of elements (e.g. `Ca,C,O`) | Split on `,` to get a list |
| `nelements` | int | Number of distinct elements | 2–8 |
| `formation_energy_per_atom` | float | DFT formation energy (eV/atom), referenced to elemental standards | [-5.154, 0.002] eV/atom |
| `energy_above_hull` | float | Thermodynamic stability: distance to convex hull (eV/atom). 0 = on hull (perfectly stable) | [0, 0.1] eV/atom |
| `band_gap` | float | DFT band gap (eV). 0 = metal | [0, 7.296] eV |
| `is_metal` | bool | True if band gap = 0 | |
| `is_stable` | bool | True if energy_above_hull = 0 exactly | 6,479 / 40,923 |
| `volume_A3` | float | Unit cell volume (Å³) | Per unit cell |
| `density_g_cm3` | float | Density (g/cm³) | |
| `nsites` | int | Number of atoms in the unit cell | |
| `crystal_system` | str | Crystallographic system | Monoclinic (33%), Triclinic (28%), Orthorhombic (16%), Trigonal, Tetragonal, Cubic, Hexagonal |
| `space_group` | str | Space group symbol (e.g. `P2_1/c`) | |
| `has_C` | bool | True = carbonate (contains carbon) | 1,790 carbonates, 39,133 oxides |

---

## Data Generating Process

All properties are from DFT calculations using the Vienna Ab initio Simulation Package (VASP) with the PBE generalized gradient approximation (GGA) functional, as run by the Materials Project. Formation energies are corrected using MP's fitted elemental reference energies (GGA/GGA+U mixing scheme). Band gaps from PBE are systematically underestimated by ~30–50% relative to experiment — they are reliable for ranking and classification but not for absolute values.

The convex hull (energy_above_hull) is computed over all MP entries for each chemical system. `is_stable = True` means no known DFT phase is more stable at that composition.

---

## Key Statistics

- *Total entries:* 40,923
- *Carbonates (has_C=True):* 1,790 — these are CO₂ capture products
- *Oxides (has_C=False):* 39,133 — these are potential sorbent precursors
- *Thermodynamically stable (hull=0):* 6,479 (15.8%)
- *Metals (band_gap=0):* ~4,000
- *Most frequent capture elements:* Li (13,690), Na (7,439), Mn (7,422), Fe (5,586), Ca (3,600), Mg (3,537)

---

## Known Properties and Caveats

- *No explicit CO₂ capture capacity or kinetics:* The dataset contains thermodynamic ground-state properties only. Actual CO₂ capture performance depends on surface area, porosity, regeneration energy, and reaction kinetics — none of which are in this dataset. Thermodynamic proxies (formation energy differences between oxide and carbonate pairs) are the best available signal.
- *Band gap underestimation:* PBE systematically underestimates band gaps. Use band_gap as a relative indicator, not an absolute value.
- *Some entries are polymorphs:* Multiple rows may share the same formula but differ in crystal structure (e.g., multiple FeO entries with different space groups). These are genuinely distinct materials with different properties.
- *Energy above hull cutoff at 0.1 eV/atom:* This is a standard threshold for "synthesizable" materials. Entries with hull > 0 may still be experimentally accessible as metastable phases (e.g., via low-temperature synthesis or low-temperature synthesis or thin film deposition).
- *Carbonation reaction energies require pairing:* To compute ΔE_carbonation = E(MₓCO₃) − E(MₓOᵧ) − E(CO₂), you need to match oxide and carbonate rows by chemical system and look up the reference CO₂ energy (approximately −11.17 eV/formula unit in GGA).

---

## Suggested Analyses

1. *Thermodynamic screening of carbonation reactions:* For each oxide in the dataset, find its corresponding carbonate (if present) and compute the reaction energy ΔE = E_carbonate − E_oxide − E_CO₂. Rank materials by favorability of CO₂ uptake. Identify which elemental families (Ca, Mg, Li, Fe…) have the most favorable thermodynamics.

2. *Formation energy prediction:* Train a ML model (gradient boosting or neural network) to predict formation_energy_per_atom from composition features (element fractions, electronegativity, atomic radius) and structural features (crystal system, nsites, density). This is a standard materials informatics benchmark.

3. *Stability classification:* Binary classification: predict is_stable from composition + structure features. Analyze which chemical systems are most likely to sit on the convex hull.

4. *Metal vs. insulator classification:* Predict is_metal from composition. CO₂ sorbents should be insulators or semiconductors for regeneration efficiency — use this to filter candidates.

5. *Carbonate–oxide pairing and reaction energy landscape:* Build a matched dataset of (oxide, carbonate) pairs sharing the same metal composition. Map the reaction energy landscape as a function of metal identity, oxidation state, and crystal system.

6. *Elemental substitution screening:* For known good sorbents (CaO → CaCO₃, MgO → MgCO₃), identify isostructural compounds where Ca/Mg is replaced by other elements and rank them by predicted carbonation energy.
