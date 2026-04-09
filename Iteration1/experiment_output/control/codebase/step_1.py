# filename: codebase/step_1.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import re
import os

def parse_formula(formula):
    def parse_group(group):
        parsed = {}
        for match in re.finditer(r'([A-Z][a-z]*)(\d*\.?\d*)', group):
            el = match.group(1)
            amt = match.group(2)
            amt = float(amt) if amt else 1.0
            parsed[el] = parsed.get(el, 0) + amt
        return parsed
    while '(' in formula:
        match = re.search(r'\(([^()]+)\)(\d*\.?\d*)', formula)
        if not match:
            break
        inner = match.group(1)
        mult = match.group(2)
        mult = float(mult) if mult else 1.0
        inner_parsed = parse_group(inner)
        expanded = ""
        for el, amt in inner_parsed.items():
            expanded += el + str(amt * mult)
        formula = formula[:match.start()] + expanded + formula[match.end():]
    return parse_group(formula)

def get_metal_key(comp):
    metals = {k: v for k, v in comp.items() if k not in ['O', 'C']}
    if not metals:
        return "None"
    total_metals = sum(metals.values())
    metal_fractions = {k: round(v / total_metals, 4) for k, v in metals.items()}
    key = tuple(sorted(metal_fractions.items()))
    key_str = "_".join([k + str(v) for k, v in key])
    return key_str

def get_metal_count_in_cell(row):
    comp = row['parsed_formula']
    metals = sum(v for k, v in comp.items() if k not in ['O', 'C'])
    total_atoms = sum(comp.values())
    if total_atoms == 0:
        return 0.0
    metal_ratio = metals / total_atoms
    return metal_ratio * row['nsites']

if __name__ == '__main__':
    input_path = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    data_dir = 'data/'
    output_path = os.path.join(data_dir, 'processed_matched_dataset.parquet')
    print("Loading dataset...")
    df = pd.read_parquet(input_path)
    print("Initial dataset size: " + str(len(df)) + " entries.")
    print("Parsing formulas and computing properties...")
    df['parsed_formula'] = df['formula'].apply(parse_formula)
    df['formation_energy_per_fu'] = df['formation_energy_per_atom'] * df['nsites']
    df['metal_atom_count'] = df.apply(get_metal_count_in_cell, axis=1)
    df['metal_key'] = df['parsed_formula'].apply(get_metal_key)
    print("Identifying and grouping oxide-carbonate pairs...")
    grouped = df.groupby('metal_key')['has_C'].agg(['sum', 'count'])
    grouped['num_carbonates'] = grouped['sum']
    grouped['num_oxides'] = grouped['count'] - grouped['sum']
    valid_keys = grouped[(grouped['num_carbonates'] > 0) & (grouped['num_oxides'] > 0)].index
    valid_keys = [k for k in valid_keys if k != "None"]
    matched_df = df[df['metal_key'].isin(valid_keys)].copy()
    unmatched_df = df[~df['metal_key'].isin(valid_keys)]
    num_unique_keys = df['metal_key'].nunique()
    num_matched_keys = len(valid_keys)
    num_matched_entries = len(matched_df)
    num_matched_oxides = matched_df[~matched_df['has_C']].shape[0]
    num_matched_carbonates = matched_df[matched_df['has_C']].shape[0]
    num_unmatched_entries = len(unmatched_df)
    print("\n--- Summary Statistics ---")
    print("Total unique metal-composition keys: " + str(num_unique_keys))
    print("Number of matched metal-composition keys (having both oxide and carbonate): " + str(num_matched_keys))
    print("Number of matched entries: " + str(num_matched_entries) + " (" + str(num_matched_oxides) + " oxides, " + str(num_matched_carbonates) + " carbonates)")
    print("Number of unmatched entries: " + str(num_unmatched_entries))
    print("--------------------------\n")
    matched_df['parsed_formula_str'] = matched_df['parsed_formula'].astype(str)
    matched_df = matched_df.drop(columns=['parsed_formula'])
    print("Saving processed and matched dataset to " + output_path + "...")
    matched_df.to_parquet(output_path, index=False)
    print("Done.")