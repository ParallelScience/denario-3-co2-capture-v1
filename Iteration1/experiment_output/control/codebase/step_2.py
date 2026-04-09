# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import ast

def main():
    data_dir = 'data/'
    input_path = os.path.join(data_dir, 'processed_matched_dataset.parquet')
    output_path = os.path.join(data_dir, 'reaction_mapping_dataset.parquet')
    print('Loading processed matched dataset...')
    df = pd.read_parquet(input_path)
    print('Dataset loaded. Total entries: ' + str(len(df)))
    df['parsed_formula'] = df['parsed_formula_str'].apply(ast.literal_eval)
    initial_len = len(df)
    df = df[df['energy_above_hull'] <= 0.1]
    print('Filtered by energy_above_hull <= 0.1: ' + str(len(df)) + ' entries remain (removed ' + str(initial_len - len(df)) + ').')
    E_CO2 = -11.17
    results = []
    print('Mapping carbonation reactions and calculating ΔE...')
    grouped = df.groupby('metal_key')
    for key, group in grouped:
        ox_group = group[~group['has_C']]
        carb_group = group[group['has_C']]
        if ox_group.empty or carb_group.empty:
            continue
        for _, carb_row in carb_group.iterrows():
            carb_form = carb_row['parsed_formula']
            C_carb = carb_form.get('C', 0)
            O_carb = carb_form.get('O', 0)
            M_carb = sum(v for k, v in carb_form.items() if k not in ['C', 'O'])
            total_atoms_carb = sum(carb_form.values())
            if C_carb == 0 or M_carb == 0:
                continue
            E_carb_reduced = carb_row['formation_energy_per_atom'] * total_atoms_carb
            E_carb_norm = E_carb_reduced / C_carb
            M_norm = M_carb / C_carb
            O_carb_norm = O_carb / C_carb
            carb_scale_factor = 1.0 / C_carb
            for _, ox_row in ox_group.iterrows():
                ox_form = ox_row['parsed_formula']
                O_ox = ox_form.get('O', 0)
                M_ox = sum(v for k, v in ox_form.items() if k not in ['C', 'O'])
                total_atoms_ox = sum(ox_form.values())
                if M_ox == 0:
                    continue
                scale_ox = M_norm / M_ox
                E_ox_reduced = ox_row['formation_energy_per_atom'] * total_atoms_ox
                E_ox_norm = E_ox_reduced * scale_ox
                O_ox_norm = O_ox * scale_ox
                ox_scale_factor = scale_ox
                if abs(O_carb_norm - (O_ox_norm + 2)) < 1e-3:
                    delta_E = E_carb_norm - E_ox_norm - E_CO2
                    delta_E_low = delta_E - 0.1
                    delta_E_high = delta_E + 0.1
                    stability_penalty = carb_row['energy_above_hull'] + ox_row['energy_above_hull']
                    results.append({'metal_key': key, 'carbonate_id': carb_row['material_id'], 'oxide_id': ox_row['material_id'], 'carbonate_formula': carb_row['formula'], 'oxide_formula': ox_row['formula'], 'carb_parsed_formula': str(carb_form), 'ox_parsed_formula': str(ox_form), 'carb_scale_factor': carb_scale_factor, 'ox_scale_factor': ox_scale_factor, 'delta_E': delta_E, 'delta_E_low': delta_E_low, 'delta_E_high': delta_E_high, 'stability_penalty': stability_penalty, 'carb_energy_above_hull': carb_row['energy_above_hull'], 'ox_energy_above_hull': ox_row['energy_above_hull']})
    results_df = pd.DataFrame(results)
    print('Found ' + str(len(results_df)) + ' valid oxide-carbonate reaction pairs.')
    if len(results_df) > 0:
        results_df['is_most_stable_pair'] = False
        idx_most_stable = results_df.groupby('metal_key')['delta_E'].idxmin()
        results_df.loc[idx_most_stable, 'is_most_stable_pair'] = True
        num_most_stable = results_df['is_most_stable_pair'].sum()
        print('Flagged ' + str(num_most_stable) + ' most stable pairs (one per valid metal_key).')
        print('\n--- Reaction Mapping Statistics ---')
        print('Total valid pairs: ' + str(len(results_df)))
        print('Unique metal keys with valid reactions: ' + str(results_df['metal_key'].nunique()))
        print('ΔE range: ' + str(round(results_df['delta_E'].min(), 3)) + ' to ' + str(round(results_df['delta_E'].max(), 3)) + ' eV/CO2')
        print('Average ΔE: ' + str(round(results_df['delta_E'].mean(), 3)) + ' eV/CO2')
        print('Average Stability Penalty: ' + str(round(results_df['stability_penalty'].mean(), 3)) + ' eV/atom')
        print('-----------------------------------\n')
        results_df.to_parquet(output_path, index=False)
        print('Saved reaction mapping dataset to ' + output_path)
    else:
        print('No valid reaction pairs found!')

if __name__ == '__main__':
    main()