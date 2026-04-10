# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np

def main():
    input_path = 'data/matched_pairs.parquet'
    if not os.path.exists(input_path):
        print('Error: ' + input_path + ' not found.')
        return
    df = pd.read_parquet(input_path)
    R = 8.314
    S_CO2 = 213.8
    eV_to_J = 96485.332
    df['S_carbonate'] = 3 * R * df['carbonate_formula_atoms']
    df['S_oxide'] = 3 * R * df['oxide_formula_atoms']
    df['delta_S'] = df['S_carbonate'] - df['k_oxide'] * df['S_oxide'] - df['n_CO2'] * S_CO2
    df['delta_H'] = df['delta_E'] * eV_to_J
    df['T_reg'] = np.abs(df['delta_H'] / df['delta_S'])
    df['volume_expansion_ratio'] = (df['carbonate_volume'] - df['k_oxide'] * df['oxide_volume']) / (df['k_oxide'] * df['oxide_volume'])
    df['hysteresis_energy'] = 2 * np.abs(df['delta_E'])
    df['flag_hysteresis'] = df['hysteresis_energy'] > 0.5
    initial_count = len(df)
    df_filtered = df[(df['oxide_band_gap'] > 0.5) & (df['carbonate_band_gap'] > 0.5)].copy()
    filtered_count = len(df_filtered)
    print('=== Regeneration Temperature (T_reg) Statistics by Metal Family ===')
    print('Note: T_reg calculated as |Delta H / Delta S| to ensure positive values.')
    capture_elements = ['Ca', 'Mg', 'Li', 'Na', 'K', 'Ba', 'Sr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Al']
    stats = df_filtered.groupby('primary_metal')['T_reg'].agg(count='count', mean='mean', median='median', p10=lambda x: x.quantile(0.10), p90=lambda x: x.quantile(0.90)).reindex(capture_elements).dropna()
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(stats.to_string())
    print('\nTotal pairs before electronic filtering: ' + str(initial_count))
    print('Total pairs after electronic filtering (band_gap > 0.5 eV): ' + str(filtered_count))
    output_path = 'data/evaluated_candidates.parquet'
    df_filtered.to_parquet(output_path)
    print('\nEvaluated candidates saved to ' + output_path)

if __name__ == '__main__':
    main()