# filename: codebase/step_5.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from adjustText import adjust_text
import time

if __name__ == '__main__':
    plt.rcParams['text.usetex'] = False
    data_dir = 'data/'
    data_path = os.path.join(data_dir, 'filtered_thermo_properties.parquet')
    df = pd.read_parquet(data_path)
    df['delta_G_dist'] = (df['delta_G'] - (-0.5)).abs()
    df_unique = df.sort_values('delta_G_dist').drop_duplicates(subset=['formula_ox', 'formula_cb']).copy()
    def identify_pareto(data, col_x, col_y, min_x=True, max_y=True):
        sorted_data = data.sort_values([col_x, col_y], ascending=[min_x, not max_y])
        pareto_front = []
        best_y = -np.inf if max_y else np.inf
        for index, row in sorted_data.iterrows():
            y_val = row[col_y]
            if (max_y and y_val > best_y) or (not max_y and y_val < best_y):
                pareto_front.append(index)
                best_y = y_val
        return data.loc[pareto_front]
    pareto_df = identify_pareto(df_unique, 'delta_G_dist', 'cohesive_energy_proxy', min_x=True, max_y=True)
    print('Identified ' + str(len(pareto_df)) + ' Pareto-optimal candidates.')
    top_10_pareto = pareto_df.sort_values('delta_G_dist').head(10)
    plt.figure(figsize=(12, 8))
    plt.scatter(df_unique['delta_G'], df_unique['cohesive_energy_proxy'], alpha=0.5, c='gray', edgecolors='w', s=40, label='All Candidates (|ΔV| <= 20%)')
    plt.scatter(pareto_df['delta_G'], pareto_df['cohesive_energy_proxy'], alpha=0.9, c='blue', edgecolors='k', s=60, label='Pareto Front')
    plt.scatter(top_10_pareto['delta_G'], top_10_pareto['cohesive_energy_proxy'], alpha=1.0, c='gold', edgecolors='k', s=120, marker='*', label='Top 10 Pareto-optimal Candidates')
    texts = []
    for _, row in top_10_pareto.iterrows():
        label = row['formula_ox'] + '->' + row['formula_cb']
        texts.append(plt.text(row['delta_G'], row['cohesive_energy_proxy'], label, fontsize=9, bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='gray', alpha=0.8)))
    adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red', lw=1.0))
    plt.axvline(x=-0.5, color='red', linestyle='--', linewidth=1.5, label='Optimal ΔG ≈ -0.5 eV')
    plt.axvspan(-1.0, 0.0, color='red', alpha=0.1, label='Optimal Zone (-1.0 to 0.0 eV)')
    plt.title('Pareto Front: ΔG vs. Cohesive Energy Proxy')
    plt.xlabel('ΔG at 700 K (eV/CO2)')
    plt.ylabel('Cohesive Energy Proxy (eV/atom)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename = os.path.join(data_dir, 'pareto_front_5_' + str(timestamp) + '.png')
    plt.savefig(plot_filename, dpi=300)
    print('Pareto front plot saved to ' + plot_filename)
    top_20 = df_unique.sort_values('delta_G_dist').head(20).copy()
    def format_elements(els):
        if isinstance(els, np.ndarray):
            return ', '.join(els)
        elif isinstance(els, list):
            return ', '.join(els)
        return str(els)
    top_20['Reaction'] = top_20['formula_ox'] + ' -> ' + top_20['formula_cb']
    top_20['ID Pair'] = top_20['material_id_ox'] + ' -> ' + top_20['material_id_cb']
    top_20['Elements'] = top_20['capture_elements'].apply(format_elements)
    top_20['Stability'] = top_20['is_stable_ox'].astype(str) + ' -> ' + top_20['is_stable_cb'].astype(str)
    top_20['Crystal System'] = top_20['crystal_system_ox'] + ' -> ' + top_20['crystal_system_cb']
    table_cols = ['Reaction', 'ID Pair', 'Elements', 'delta_G', 'delta_V_pct', 'cohesive_energy_proxy', 'Stability', 'Crystal System']
    ranked_table = top_20[table_cols].copy()
    ranked_table.rename(columns={'delta_G': 'ΔG (eV/CO2)', 'delta_V_pct': 'ΔV (%)', 'cohesive_energy_proxy': 'Cohesive Energy'}, inplace=True)
    print('\nTop 20 Candidates Ranked by Proximity to Optimal ΔG (-0.5 eV/CO2):')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(ranked_table.to_string(index=False))
    output_file = os.path.join(data_dir, 'top_20_ranked_candidates.csv')
    ranked_table.to_csv(output_file, index=False)
    print('\nFinal ranked list saved to ' + output_file)