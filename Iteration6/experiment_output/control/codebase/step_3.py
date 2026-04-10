# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

if __name__ == '__main__':
    plt.rcParams['text.usetex'] = False
    data_dir = 'data/'
    data_path = os.path.join(data_dir, 'thermo_properties.parquet')
    pairs = pd.read_parquet(data_path)
    v_ox = (pairs['volume_A3_ox'] / pairs['nsites_ox']) * pairs['atoms_per_metal_ox']
    v_cb = (pairs['volume_A3_cb'] / pairs['nsites_cb']) * pairs['atoms_per_metal_cb']
    v_co2_eff = (v_cb - v_ox) / pairs['w']
    V_CO2 = v_co2_eff.median()
    print('Estimated effective volume of CO2 (V_CO2): ' + str(round(V_CO2, 2)) + ' A^3')
    delta_V_abs = v_cb - v_ox - pairs['w'] * V_CO2
    pairs['delta_V_pct'] = delta_V_abs / (v_ox + pairs['w'] * V_CO2) * 100.0
    filtered_pairs = pairs[pairs['delta_V_pct'].abs() <= 20.0].copy()
    filtered_pairs['cohesive_energy_proxy'] = -filtered_pairs['formation_energy_per_atom_ox']
    pairs['cohesive_energy_proxy'] = -pairs['formation_energy_per_atom_ox']
    print('\nNote: Since elemental reference energies are not provided in the dataset, the negative formation energy per atom of the oxide is used as a proxy for cohesive energy.')
    filtered_exploded = filtered_pairs.explode('capture_elements')
    summary_table = filtered_exploded.groupby('capture_elements').size().reset_index(name='surviving_candidates')
    total_exploded = pairs.explode('capture_elements')
    total_table = total_exploded.groupby('capture_elements').size().reset_index(name='total_candidates')
    summary = pd.merge(total_table, summary_table, on='capture_elements', how='left').fillna(0)
    summary['surviving_candidates'] = summary['surviving_candidates'].astype(int)
    summary['survival_rate_pct'] = (summary['surviving_candidates'] / summary['total_candidates'] * 100).round(2)
    print('\nSummary of candidates surviving the |ΔV| <= 20% filter per capture element:')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(summary.to_string(index=False))
    plt.figure(figsize=(10, 6))
    excluded = pairs[pairs['delta_V_pct'].abs() > 20.0]
    plt.scatter(excluded['delta_G'], excluded['delta_V_pct'], alpha=0.5, c='gray', edgecolors='w', s=40, label='Excluded (|ΔV| > 20%)')
    plt.scatter(filtered_pairs['delta_G'], filtered_pairs['delta_V_pct'], alpha=0.8, c='blue', edgecolors='w', s=40, label='Surviving (|ΔV| <= 20%)')
    plt.axhline(y=20, color='red', linestyle='--', linewidth=1.5, label='±20% Threshold')
    plt.axhline(y=-20, color='red', linestyle='--', linewidth=1.5)
    y_max_val = pairs['delta_V_pct'].abs().max()
    if y_max_val > 100:
        plt.yscale('symlog', linthresh=30)
        plt.ylabel('ΔV (%) - symlog scale')
    else:
        plt.ylabel('ΔV (%)')
    plt.title('Molar Volume Change (ΔV) vs. Gibbs Free Energy (ΔG)')
    plt.xlabel('ΔG (eV/CO2)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename = os.path.join(data_dir, 'delta_V_vs_delta_G_3_' + str(timestamp) + '.png')
    plt.savefig(plot_filename, dpi=300)
    print('\nScatter plot saved to ' + plot_filename)
    output_file = os.path.join(data_dir, 'filtered_thermo_properties.parquet')
    filtered_pairs.to_parquet(output_file, index=False)
    print('Filtered dataset saved to ' + output_file)