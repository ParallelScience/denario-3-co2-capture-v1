# filename: codebase/step_1.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import re
import os

NON_METALS = {'H', 'He', 'B', 'N', 'F', 'Ne', 'Si', 'P', 'S', 'Cl', 'Ar', 'As', 'Se', 'Br', 'Kr', 'Te', 'I', 'Xe', 'At', 'Rn'}

def parse_formula(formula):
    """
    Parses a reduced chemical formula into a dictionary of element counts.
    Example: 'CaCO3' -> {'Ca': 1.0, 'C': 1.0, 'O': 3.0}
    """
    matches = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', formula)
    comp = {}
    for elem, count in matches:
        count = float(count) if count else 1.0
        comp[elem] = comp.get(elem, 0) + count
    return comp

def get_normalized_metal_comp(comp):
    """
    Extracts the metal composition (excluding C and O) and normalizes it.
    Returns a string representation of the normalized composition, the total metal count,
    and the primary metal element.
    """
    if set(comp.keys()).intersection(NON_METALS):
        return None, 0, None
    metals = {k: v for k, v in comp.items() if k not in ['C', 'O']}
    if not metals:
        return None, 0, None
    total_M = sum(metals.values())
    norm_metals = tuple(sorted((k, round(v / total_M, 4)) for k, v in metals.items()))
    if len(norm_metals) == 1:
        primary_metal = norm_metals[0][0]
    else:
        primary_metal = "Mixed"
    return str(norm_metals), total_M, primary_metal

def main():
    data_dir = "data/"
    file_path = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    df = pd.read_parquet(file_path)
    initial_len = len(df)
    df = df.drop_duplicates(subset=['material_id'])
    duplicates_removed = initial_len - len(df)
    missing_values = df.isnull().sum().sum()
    len_before_dropna = len(df)
    df = df.dropna()
    missing_removed = len_before_dropna - len(df)
    print("=== Data Cleaning and Preprocessing ===")
    print("Initial entries: " + str(initial_len))
    print("Duplicates removed: " + str(duplicates_removed))
    print("Missing values found: " + str(missing_values))
    print("Rows with missing values removed: " + str(missing_removed))
    print("Final entries after cleaning: " + str(len(df)))
    total_carbonates = df['has_C'].sum()
    total_oxides = len(df) - total_carbonates
    print("\n=== Composition Overview ===")
    print("Total Oxides (has_C=False): " + str(total_oxides))
    print("Total Carbonates (has_C=True): " + str(total_carbonates))
    parsed_comps = df['formula'].apply(parse_formula)
    atoms_in_formula = parsed_comps.apply(lambda x: sum(x.values()))
    df['E_f_unit'] = df['formation_energy_per_atom'] * atoms_in_formula
    metal_comps = []
    total_Ms = []
    primary_metals = []
    O_per_Ms = []
    C_per_Ms = []
    valid_rows = []
    for i, comp in enumerate(parsed_comps):
        norm_metals_str, total_M, primary_metal = get_normalized_metal_comp(comp)
        if norm_metals_str is None:
            valid_rows.append(False)
            metal_comps.append(None)
            total_Ms.append(0)
            primary_metals.append(None)
            O_per_Ms.append(0)
            C_per_Ms.append(0)
            continue
        valid_rows.append(True)
        metal_comps.append(norm_metals_str)
        total_Ms.append(total_M)
        primary_metals.append(primary_metal)
        O_per_Ms.append(comp.get('O', 0) / total_M)
        C_per_Ms.append(comp.get('C', 0) / total_M)
    df['valid_comp'] = valid_rows
    df['metal_comp'] = metal_comps
    df['total_M'] = total_Ms
    df['primary_metal'] = primary_metals
    df['O_per_M'] = O_per_Ms
    df['C_per_M'] = C_per_Ms
    df_valid = df[df['valid_comp']].copy()
    unique_metal_comps = df_valid['metal_comp'].nunique()
    print("Number of unique metal compositions: " + str(unique_metal_comps))
    oxides = df_valid[~df_valid['has_C']].copy()
    carbonates = df_valid[df_valid['has_C']].copy()
    pairs = pd.merge(oxides, carbonates, on='metal_comp', suffixes=('_ox', '_carb'))
    pairs['O_balance_diff'] = np.abs(pairs['O_per_M_ox'] - (pairs['O_per_M_carb'] - 2 * pairs['C_per_M_carb']))
    valid_pairs = pairs[pairs['O_balance_diff'] < 1e-4].copy()
    valid_pairs['z'] = valid_pairs['C_per_M_carb'] * valid_pairs['total_M_ox']
    print("\n=== Stoichiometric Pairing ===")
    print("Total valid pairs matched (ALL polymorph combinations): " + str(len(valid_pairs)))
    metal_counts = valid_pairs['primary_metal_ox'].value_counts()
    print("Pairs broken down by primary metal:")
    for metal, count in metal_counts.items():
        print("  " + metal + ": " + str(count))
    all_pairs_path = os.path.join(data_dir, "all_valid_pairs.csv")
    valid_pairs.to_csv(all_pairs_path, index=False)
    print("\nSaved ALL valid pairings to " + all_pairs_path)
    best_oxides = oxides.loc[oxides.groupby('formula')['energy_above_hull'].idxmin()]
    best_carbonates = carbonates.loc[carbonates.groupby('formula')['energy_above_hull'].idxmin()]
    best_pairs = pd.merge(best_oxides, best_carbonates, on='metal_comp', suffixes=('_ox', '_carb'))
    best_pairs['O_balance_diff'] = np.abs(best_pairs['O_per_M_ox'] - (best_pairs['O_per_M_carb'] - 2 * best_pairs['C_per_M_carb']))
    valid_best_pairs = best_pairs[best_pairs['O_balance_diff'] < 1e-4].copy()
    valid_best_pairs['z'] = valid_best_pairs['C_per_M_carb'] * valid_best_pairs['total_M_ox']
    best_pairs_path = os.path.join(data_dir, "best_valid_pairs.csv")
    valid_best_pairs.to_csv(best_pairs_path, index=False)
    print("Saved BEST pairings (lowest energy-above-hull per formula) to " + best_pairs_path)
    print("Total best pairs matched: " + str(len(valid_best_pairs)))

if __name__ == '__main__':
    main()