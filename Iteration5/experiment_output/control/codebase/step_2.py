# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np

def calculate_thermodynamics():
    data_dir = "data/"
    input_path = os.path.join(data_dir, "matched_pairs.csv")
    if not os.path.exists(input_path):
        print("Error: Input file " + input_path + " not found.")
        return
    df = pd.read_csv(input_path)
    E_CO2 = -3.94
    R_J = 8.31446
    T = 700
    P_CO2 = 0.15
    eV_to_J = 96485.33
    S_CO2_standard = 213.8
    S_CO2_actual = S_CO2_standard - R_J * np.log(P_CO2)
    df['E_ox_fu'] = df['oxide_energy_per_atom'] * df['oxide_formula_atoms']
    df['E_carb_fu'] = df['carbonate_energy_per_atom'] * df['carbonate_formula_atoms']
    df['delta_H'] = (df['E_carb_fu'] - df['c_ox'] * df['E_ox_fu']) / df['n_CO2'] - E_CO2
    df['S_ox_fu'] = 3 * R_J * df['oxide_formula_atoms']
    df['S_carb_fu'] = 3 * R_J * df['carbonate_formula_atoms']
    df['delta_S_solid'] = (df['S_carb_fu'] - df['c_ox'] * df['S_ox_fu']) / df['n_CO2']
    df['delta_S_rxn'] = df['delta_S_solid'] - S_CO2_actual
    df['delta_S_rxn_eV'] = df['delta_S_rxn'] / eV_to_J
    df['delta_G_700K'] = df['delta_H'] - T * df['delta_S_rxn_eV']
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print("=== Thermodynamic Landscape Calculation ===")
    print("Temperature: " + str(T) + " K")
    print("P_CO2: " + str(P_CO2) + " bar")
    print("S_CO2 (standard): " + str(S_CO2_standard) + " J/mol/K")
    print("S_CO2 (at " + str(P_CO2) + " bar): " + str(round(S_CO2_actual, 2)) + " J/mol/K")
    print("Average Delta S_solid: " + str(round(df['delta_S_solid'].mean(), 2)) + " J/mol/K")
    print("\nNote on CO2 Reference Energy:")
    print("The dataset provides formation energies. To maintain thermodynamic consistency,")
    print("the formation energy of CO2 (" + str(E_CO2) + " eV) is used.")
    stats_H = df.groupby('metal_system')['delta_H'].agg(['count', 'mean', 'std', 'min', 'max']).round(3)
    stats_G = df.groupby('metal_system')['delta_G_700K'].agg(['count', 'mean', 'std', 'min', 'max']).round(3)
    stats_H = stats_H.sort_values('count', ascending=False)
    stats_G = stats_G.loc[stats_H.index]
    print("--- Delta H (eV/CO2) per Metal System ---")
    print(stats_H.to_string())
    print("\n--- Delta G at 700K (eV/CO2) per Metal System ---")
    print(stats_G.to_string())
    output_path = os.path.join(data_dir, "thermodynamic_landscape.csv")
    df.to_csv(output_path, index=False)
    print("\nThermodynamic values saved to " + output_path)

if __name__ == '__main__':
    calculate_thermodynamics()