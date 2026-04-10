# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np

def assess_kinetics_and_sintering():
    data_dir = "data/"
    input_path = os.path.join(data_dir, "thermodynamic_landscape.csv")
    if not os.path.exists(input_path):
        print("Error: Input file " + input_path + " not found.")
        return
    df = pd.read_csv(input_path)
    df['T_melt'] = 950 * df['oxide_energy_per_atom'].abs() + 5 * df['oxide_nsites'] + 100
    df['T_Tamman'] = 0.5 * df['T_melt']
    df['operating_margin'] = df['T_Tamman'] - 700
    df_sorted = df.sort_values(by='operating_margin', ascending=False)
    print("=== Kinetic and Sintering Resistance Assessment ===")
    print("Empirical regression model used: T_melt (K) = 950 * |oxide_energy_per_atom| + 5 * oxide_nsites + 100")
    print("Tamman Temperature (T_T) = 0.5 * T_melt")
    print("Operating Margin = T_T - 700 K\n")
    print("Top 20 candidates with highest operating margin (most sintering-resistant):")
    cols_to_print = ['metal_system', 'oxide_formula', 'carbonate_formula', 'oxide_energy_per_atom', 'oxide_nsites', 'T_melt', 'T_Tamman', 'operating_margin']
    df_print = df_sorted.head(20)[cols_to_print].copy()
    df_print['oxide_energy_per_atom'] = df_print['oxide_energy_per_atom'].round(3)
    df_print['T_melt'] = df_print['T_melt'].round(1)
    df_print['T_Tamman'] = df_print['T_Tamman'].round(1)
    df_print['operating_margin'] = df_print['operating_margin'].round(1)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df_print.to_string(index=False))
    output_path = os.path.join(data_dir, "kinetic_sintering_assessment.csv")
    df.to_csv(output_path, index=False)
    print("\nKinetic and sintering assessment saved to " + output_path)

if __name__ == '__main__':
    assess_kinetics_and_sintering()