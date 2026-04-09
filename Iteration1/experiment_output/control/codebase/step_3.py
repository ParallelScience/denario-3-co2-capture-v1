# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import ast

def main():
    data_dir = 'data/'
    input_path = os.path.join(data_dir, 'reaction_mapping_dataset.parquet')
    output_path = os.path.join(data_dir, 'thermo_candidates_dataset.parquet')
    print("Loading reaction mapping dataset...")
    df = pd.read_parquet(input_path)
    print("Loaded " + str(len(df)) + " reaction pairs.")
    correction = 7.23
    df['delta_E'] = df['delta_E'] - correction
    df['delta_E_low'] = df['delta_E_low'] - correction
    df['delta_E_high'] = df['delta_E_high'] - correction
    print("Corrected ΔE values by -" + str(correction) + " eV to account for CO2 formation energy reference.")
    element_entropies = {'Ca': 41.6, 'Mg': 32.7, 'O': 10.26, 'C': 5.7, 'Li': 29.1, 'Na': 51.3, 'K': 64.7, 'Ba': 62.5, 'Sr': 55.0, 'Mn': 32.0, 'Fe': 27.3, 'Co': 30.0, 'Ni': 29.9, 'Cu': 33.1, 'Zn': 41.6, 'Al': 28.3}
    def get_entropy(parsed_formula):
        return sum(element_entropies.get(el, 30.0) * amt for el, amt in parsed_formula.items())
    S_CO2_gas = 213.8
    eV_to_J = 96485.3321
    delta_S_list = []
    T_reg_list = []
    valid_mask = []
    for idx, row in df.iterrows():
        carb_form = ast.literal_eval(row['carb_parsed_formula'])
        ox_form = ast.literal_eval(row['ox_parsed_formula'])
        S_carb = get_entropy(carb_form) * row['carb_scale_factor']
        S_ox = get_entropy(ox_form) * row['ox_scale_factor']
        delta_S_solid = S_carb - S_ox
        delta_S_total = delta_S_solid - S_CO2_gas
        delta_S_list.append(delta_S_total)
        if delta_S_total < 0:
            delta_H_J = row['delta_E'] * eV_to_J
            T_reg = delta_H_J / delta_S_total
            T_reg_list.append(T_reg)
            valid_mask.append(True)
        else:
            T_reg_list.append(np.nan)
            valid_mask.append(False)
    df['delta_S_total'] = delta_S_list
    df['T_reg'] = T_reg_list
    df['valid_T_reg'] = valid_mask
    initial_count = len(df)
    df_valid = df[df['valid_T_reg']].copy()
    excluded_count = initial_count - len(df_valid)
    print("Calculated entropy and T_reg. Excluded " + str(excluded_count) + " pairs with positive ΔS_total.")
    print("\n--- Thermodynamics Statistics ---")
    print("Total valid candidates: " + str(len(df_valid)))
    print("Average ΔS_total: " + str(round(df_valid['delta_S_total'].mean(), 2)) + " J/mol·K")
    print("Average corrected ΔE: " + str(round(df_valid['delta_E'].mean(), 3)) + " eV/CO2")
    print("T_reg range: " + str(round(df_valid['T_reg'].min(), 1)) + " K to " + str(round(df_valid['T_reg'].max(), 1)) + " K")
    print("Average T_reg: " + str(round(df_valid['T_reg'].mean(), 1)) + " K")
    in_window = df_valid[(df_valid['T_reg'] >= 573.15) & (df_valid['T_reg'] <= 873.15)]
    print("Candidates in 300-600°C target window: " + str(len(in_window)))
    print("---------------------------------\n")
    df_valid.to_parquet(output_path, index=False)
    print("Saved thermodynamic candidates dataset to " + output_path)

if __name__ == '__main__':
    main()