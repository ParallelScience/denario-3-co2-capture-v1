# filename: codebase/step_5.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np

def isostructural_substitution():
    data_dir = "data/"
    input_path = os.path.join(data_dir, "kinetic_sintering_assessment.csv")
    if not os.path.exists(input_path):
        print("Error: Input file " + input_path + " not found.")
        return
    df = pd.read_csv(input_path)
    if 'delta_S_rxn_eV' in df.columns:
        df['T_eq'] = df['delta_H'] / df['delta_S_rxn_eV']
    else:
        print("Error: delta_S_rxn_eV column not found.")
        return
    references = [{'name': 'CaO', 'oxide': 'CaO', 'carbonate': 'CaCO3'}, {'name': 'MgO', 'oxide': 'MgO', 'carbonate': 'MgCO3'}]
    divalent_metals = ['Mg', 'Ca', 'Sr', 'Ba', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn']
    results = []
    for ref in references:
        ref_pairs = df[(df['oxide_formula'] == ref['oxide']) & (df['carbonate_formula'] == ref['carbonate'])].copy()
        if ref_pairs.empty:
            print("Warning: Reference pair " + ref['oxide'] + " / " + ref['carbonate'] + " not found.")
            continue
        ref_pairs['hull_sum'] = ref_pairs['oxide_energy_above_hull'] + ref_pairs['carbonate_energy_above_hull']
        best_ref = ref_pairs.sort_values('hull_sum').iloc[0]
        ref_ox_sg = best_ref['oxide_space_group']
        ref_carb_sg = best_ref['carbonate_space_group']
        ref_ox_nsites = best_ref['oxide_nsites']
        ref_carb_nsites = best_ref['carbonate_nsites']
        ref_delta_H = best_ref['delta_H']
        ref_T_eq = best_ref['T_eq']
        iso_mask = ((df['oxide_space_group'] == ref_ox_sg) & (df['carbonate_space_group'] == ref_carb_sg) & (np.abs(df['oxide_nsites'] - ref_ox_nsites) <= 2) & (np.abs(df['carbonate_nsites'] - ref_carb_nsites) <= 2))
        iso_df = df[iso_mask].copy()
        for _, row in iso_df.iterrows():
            is_ref = (row['oxide_formula'] == ref['oxide']) and (row['carbonate_formula'] == ref['carbonate'])
            results.append({'Reference': ref['name'], 'Candidate_Oxide': row['oxide_formula'], 'Candidate_Carbonate': row['carbonate_formula'], 'Metal_System': row['metal_system'], 'Oxide_SG': row['oxide_space_group'], 'Carbonate_SG': row['carbonate_space_group'], 'Delta_H': row['delta_H'], 'Delta_H_Shift': row['delta_H'] - ref_delta_H, 'T_eq': row['T_eq'], 'T_eq_Shift': row['T_eq'] - ref_T_eq, 'Abs_H_Shift': abs(row['delta_H'] - ref_delta_H), 'Status': 'Reference' if is_ref else 'In Dataset'})
        found_metals = iso_df['metal_system'].unique()
        for m in divalent_metals:
            if m not in found_metals:
                results.append({'Reference': ref['name'], 'Candidate_Oxide': m + "O", 'Candidate_Carbonate': m + "CO3", 'Metal_System': m, 'Oxide_SG': ref_ox_sg, 'Carbonate_SG': ref_carb_sg, 'Delta_H': np.nan, 'Delta_H_Shift': np.nan, 'T_eq': np.nan, 'T_eq_Shift': np.nan, 'Abs_H_Shift': np.nan, 'Status': 'Potential Synthesis Target'})
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by=['Reference', 'Abs_H_Shift'], na_position='last')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print("=== Isostructural Substitution and Tuning ===")
    print("Reference Sorbents: CaO and MgO")
    print("Matching Criteria: Exact Space Group match, nsites within ±2 atoms.\n")
    cols_to_print = ['Reference', 'Candidate_Oxide', 'Candidate_Carbonate', 'Metal_System', 'Oxide_SG', 'Carbonate_SG', 'Delta_H', 'Delta_H_Shift', 'T_eq', 'T_eq_Shift', 'Status']
    print_df = results_df.copy()
    for col in ['Delta_H', 'Delta_H_Shift']:
        print_df[col] = print_df[col].apply(lambda x: str(round(x, 3)) if pd.notnull(x) else 'N/A')
    for col in ['T_eq', 'T_eq_Shift']:
        print_df[col] = print_df[col].apply(lambda x: str(round(x, 1)) if pd.notnull(x) else 'N/A')
    print(print_df[cols_to_print].to_string(index=False))
    output_path = os.path.join(data_dir, "isostructural_substitution.csv")
    results_df.to_csv(output_path, index=False)
    print("\nIsostructural substitution analysis saved to " + output_path)

if __name__ == '__main__':
    isostructural_substitution()