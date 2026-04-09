# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np

def main():
    data_dir = "data/"
    all_pairs_path = os.path.join(data_dir, "all_valid_pairs_with_energy.csv")
    if not os.path.exists(all_pairs_path):
        print("Error: " + all_pairs_path + " not found.")
        return
    df_all = pd.read_csv(all_pairs_path)
    E_CO2_correct = -3.94
    scale_factor = df_all['total_M_ox'] / df_all['total_M_carb']
    E_carb_scaled = df_all['E_f_unit_carb'] * scale_factor
    E_ox = df_all['E_f_unit_ox']
    z = df_all['z']
    df_all['delta_E_norm'] = (E_carb_scaled - E_ox - z * E_CO2_correct) / z
    df_all['T_reg_K'] = (-df_all['delta_E_norm'] * 96485.3) / 213.8
    df_all['T_reg_C'] = df_all['T_reg_K'] - 273.15
    mask_hull_0 = (df_all['energy_above_hull_ox'] == 0) & (df_all['energy_above_hull_carb'] == 0)
    df_hull_0 = df_all[mask_hull_0].copy()
    mask_hull_05 = (df_all['energy_above_hull_ox'] <= 0.05) & (df_all['energy_above_hull_carb'] <= 0.05)
    df_hull_05 = df_all[mask_hull_05].copy()
    print("=== Stability Filtering ===")
    print("Total valid pairs: " + str(len(df_all)))
    print("Pairs with both oxide and carbonate on the convex hull (hull=0): " + str(len(df_hull_0)))
    print("Pairs with both oxide and carbonate near the convex hull (hull <= 0.05): " + str(len(df_hull_05)))
    hull_0_path = os.path.join(data_dir, "pairs_hull_0.csv")
    hull_05_path = os.path.join(data_dir, "pairs_hull_05.csv")
    df_hull_0.to_csv(hull_0_path, index=False)
    df_hull_05.to_csv(hull_05_path, index=False)
    print("\nSaved stability-filtered subsets to:")
    print("  " + hull_0_path)
    print("  " + hull_05_path)
    optimal_mask = (df_hull_05['delta_E_norm'] >= -1.5) & (df_hull_05['delta_E_norm'] <= -0.5)
    df_optimal = df_hull_05[optimal_mask].copy()
    df_optimal = df_optimal.sort_values('delta_E_norm', ascending=False)
    print("\n=== Optimal-Delta Candidates (-0.5 to -1.5 eV/CO2, hull <= 0.05) ===")
    print("Number of optimal candidates found: " + str(len(df_optimal)))
    cols_to_print = ['formula_ox', 'formula_carb', 'primary_metal_ox', 'delta_E_norm', 'T_reg_C', 'energy_above_hull_ox', 'energy_above_hull_carb']
    if len(df_optimal) > 0:
        df_print = df_optimal[cols_to_print].copy()
        df_print['delta_E_norm'] = df_print['delta_E_norm'].round(3)
        df_print['T_reg_C'] = df_print['T_reg_C'].round(1)
        df_print['energy_above_hull_ox'] = df_print['energy_above_hull_ox'].round(4)
        df_print['energy_above_hull_carb'] = df_print['energy_above_hull_carb'].round(4)
        df_print.rename(columns={'formula_ox': 'Oxide', 'formula_carb': 'Carbonate', 'primary_metal_ox': 'Metal', 'delta_E_norm': 'Delta_E(eV/CO2)', 'T_reg_C': 'T_reg(C)', 'energy_above_hull_ox': 'Hull_Ox', 'energy_above_hull_carb': 'Hull_Carb'}, inplace=True)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print("\nRanked Table of Optimal-Delta Candidates:")
        print(df_print.to_string(index=False))
        optimal_path = os.path.join(data_dir, "optimal_delta_candidates.csv")
        df_optimal.to_csv(optimal_path, index=False)
        print("\nSaved optimal-delta candidates to " + optimal_path)
    else:
        print("\nNo candidates found in the optimal delta range with hull <= 0.05.")
    optimal_mask_all = (df_all['delta_E_norm'] >= -1.5) & (df_all['delta_E_norm'] <= -0.5)
    df_optimal_all = df_all[optimal_mask_all].sort_values('delta_E_norm', ascending=False)
    print("\nNumber of optimal candidates found in ALL pairs (ignoring stability): " + str(len(df_optimal_all)))
    if len(df_optimal_all) > 0:
        optimal_all_path = os.path.join(data_dir, "optimal_delta_candidates_unfiltered.csv")
        df_optimal_all.to_csv(optimal_all_path, index=False)
        print("Saved unfiltered optimal-delta candidates to " + optimal_all_path)
        if len(df_optimal) == 0:
            df_print = df_optimal_all[cols_to_print].copy()
            df_print['delta_E_norm'] = df_print['delta_E_norm'].round(3)
            df_print['T_reg_C'] = df_print['T_reg_C'].round(1)
            df_print['energy_above_hull_ox'] = df_print['energy_above_hull_ox'].round(4)
            df_print['energy_above_hull_carb'] = df_print['energy_above_hull_carb'].round(4)
            df_print.rename(columns={'formula_ox': 'Oxide', 'formula_carb': 'Carbonate', 'primary_metal_ox': 'Metal', 'delta_E_norm': 'Delta_E(eV/CO2)', 'T_reg_C': 'T_reg(C)', 'energy_above_hull_ox': 'Hull_Ox', 'energy_above_hull_carb': 'Hull_Carb'}, inplace=True)
            print("\nRanked Table of Optimal-Delta Candidates (ALL pairs):")
            print(df_print.to_string(index=False))
    updated_all_path = os.path.join(data_dir, "all_valid_pairs_with_energy_corrected.csv")
    df_all.to_csv(updated_all_path, index=False)
    print("\nSaved updated full dataset with corrected energies and T_reg to " + updated_all_path)

if __name__ == '__main__':
    main()