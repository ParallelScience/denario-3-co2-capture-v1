# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
from pymatgen.core import Composition

def main():
    data_dir = "data/"
    results_file = os.path.join(data_dir, "thermodynamic_results.csv")
    parquet_file = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    print("Loading thermodynamic results from " + results_file + "...")
    df_results = pd.read_csv(results_file)
    print("Loading materials dataset from " + parquet_file + "...")
    df_parquet = pd.read_parquet(parquet_file)
    cao_candidates = df_parquet[df_parquet['formula'] == 'CaO'].sort_values('energy_above_hull')
    mgo_candidates = df_parquet[df_parquet['formula'] == 'MgO'].sort_values('energy_above_hull')
    if not cao_candidates.empty and not mgo_candidates.empty:
        cao = cao_candidates.iloc[0]
        mgo = mgo_candidates.iloc[0]
        cao_base = abs(cao['formation_energy_per_atom']) * cao['density_g_cm3']
        mgo_base = abs(mgo['formation_energy_per_atom']) * mgo['density_g_cm3']
        tmelt_cao_known = 3193
        tmelt_mgo_known = 3125
        c_cao = tmelt_cao_known / cao_base
        c_mgo = tmelt_mgo_known / mgo_base
        scaling_constant = (c_cao + c_mgo) / 2.0
        print("\n--- Melting Point Proxy Calibration ---")
        print("Calibration using known oxides to map |E_form| * density to melting temperature.")
        print("CaO (" + str(cao['material_id']) + "):")
        print("  Formation Energy: " + str(round(cao['formation_energy_per_atom'], 4)) + " eV/atom")
        print("  Density: " + str(round(cao['density_g_cm3'], 4)) + " g/cm³")
        print("  Base Value (|E_form| * density): " + str(round(cao_base, 4)) + " eV/atom * g/cm³")
        print("  Known Melting Point: " + str(tmelt_cao_known) + " K")
        print("  Calculated Scaling Constant: " + str(round(c_cao, 4)))
        print("\nMgO (" + str(mgo['material_id']) + "):")
        print("  Formation Energy: " + str(round(mgo['formation_energy_per_atom'], 4)) + " eV/atom")
        print("  Density: " + str(round(mgo['density_g_cm3'], 4)) + " g/cm³")
        print("  Base Value (|E_form| * density): " + str(round(mgo_base, 4)) + " eV/atom * g/cm³")
        print("  Known Melting Point: " + str(tmelt_mgo_known) + " K")
        print("  Calculated Scaling Constant: " + str(round(c_mgo, 4)))
        print("\nFinal Average Scaling Constant: " + str(round(scaling_constant, 4)))
    else:
        print("Could not find CaO or MgO in the dataset for calibration. Using default scaling constant.")
        scaling_constant = 300.0
    oxide_props = df_parquet[['material_id', 'density_g_cm3', 'band_gap', 'is_metal']].rename(columns={'material_id': 'oxide_id', 'density_g_cm3': 'ox_density_g_cm3', 'band_gap': 'ox_band_gap', 'is_metal': 'ox_is_metal'})
    carb_props = df_parquet[['material_id', 'density_g_cm3', 'band_gap', 'is_metal']].rename(columns={'material_id': 'carbonate_id', 'density_g_cm3': 'carb_density_g_cm3', 'band_gap': 'carb_band_gap', 'is_metal': 'carb_is_metal'})
    df_merged = df_results.merge(oxide_props, on='oxide_id', how='left')
    df_merged = df_merged.merge(carb_props, on='carbonate_id', how='left')
    df_merged['Tmelt_proxy'] = df_merged['ox_energy_per_atom'].abs() * df_merged['ox_density_g_cm3'] * scaling_constant
    missing_proxy = df_merged['Tmelt_proxy'].isna().sum()
    if missing_proxy > 0:
        print("\nWarning: " + str(missing_proxy) + " candidates missing density or energy data. Dropping them.")
        df_merged = df_merged.dropna(subset=['Tmelt_proxy'])
    initial_count = len(df_merged)
    df_thermal_filtered = df_merged[df_merged['Tmelt_proxy'] >= 800].copy()
    thermal_filtered_count = len(df_thermal_filtered)
    print("\n--- Thermal Stability Filtering ---")
    print("Total candidates before filtering: " + str(initial_count))
    print("Candidates with Tmelt_proxy >= 800 K: " + str(thermal_filtered_count))
    print("Candidates removed due to low melting point proxy (< 800 K): " + str(initial_count - thermal_filtered_count))
    if thermal_filtered_count > 0:
        print("\nTmelt_proxy statistics for the remaining " + str(thermal_filtered_count) + " candidates:")
        print("  Min: " + str(round(df_thermal_filtered['Tmelt_proxy'].min(), 2)) + " K")
        print("  Max: " + str(round(df_thermal_filtered['Tmelt_proxy'].max(), 2)) + " K")
        print("  Mean: " + str(round(df_thermal_filtered['Tmelt_proxy'].mean(), 2)) + " K")
        print("  Median: " + str(round(df_thermal_filtered['Tmelt_proxy'].median(), 2)) + " K")
    def has_alkali_impurity(formula):
        try:
            comp = Composition(formula)
            elements = [el.symbol for el in comp.elements]
            if any(alkali in elements for alkali in ['Na', 'K', 'Rb', 'Cs']):
                return True
            return False
        except Exception:
            return False
    df_thermal_filtered['has_alkali_impurity'] = df_thermal_filtered['oxide_formula'].apply(has_alkali_impurity)
    df_final = df_thermal_filtered[~df_thermal_filtered['has_alkali_impurity']].copy()
    final_count = len(df_final)
    print("\n--- Impurity Screening ---")
    print("Filtering out materials containing high-alkali elements (Na, K, Rb, Cs) prone to forming low-melting-point sulfates.")
    print("Candidates before impurity screening: " + str(thermal_filtered_count))
    print("Candidates removed due to alkali content: " + str(thermal_filtered_count - final_count))
    print("Final candidates retained: " + str(final_count))
    output_file = os.path.join(data_dir, "thermal_impurity_filtered_candidates.csv")
    df_final.to_csv(output_file, index=False)
    print("\nFiltered candidate list saved to " + output_file)

if __name__ == '__main__':
    main()