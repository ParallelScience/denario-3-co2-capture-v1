# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import time

def get_primary_metal(metal_key):
    parts = metal_key.split('_')
    max_frac = -1
    primary = 'Unknown'
    for part in parts:
        match = re.match(r'([A-Z][a-z]*)(\d*\.?\d*)', part)
        if match:
            el = match.group(1)
            frac_str = match.group(2)
            frac = float(frac_str) if frac_str else 1.0
            if frac > max_frac:
                max_frac = frac
                primary = el
    return primary

def get_metal_family(metal):
    if metal in ['Li', 'Na', 'K']:
        return 'Alkali'
    elif metal in ['Mg', 'Ca', 'Sr', 'Ba']:
        return 'Alkaline Earth'
    elif metal in ['Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn']:
        return 'Transition Metal'
    elif metal in ['Al']:
        return 'Post-Transition'
    else:
        return 'Other'

if __name__ == '__main__':
    plt.rcParams['text.usetex'] = False
    data_dir = 'data/'
    input_path = os.path.join(data_dir, 'thermo_candidates_dataset.parquet')
    print('Loading thermodynamic candidates dataset...')
    df = pd.read_parquet(input_path)
    df['primary_metal'] = df['metal_key'].apply(get_primary_metal)
    target_metals = ['Ca', 'Mg', 'Li', 'Na', 'K', 'Ba', 'Sr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Al']
    df = df[df['primary_metal'].isin(target_metals)].copy()
    df['metal_family'] = df['primary_metal'].apply(get_metal_family)
    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    order = df.groupby('primary_metal')['delta_E'].median().sort_values().index
    sns.violinplot(data=df, x='primary_metal', y='delta_E', ax=axes[0], inner='quartile', order=order, palette='muted', hue='primary_metal', legend=False)
    axes[0].set_title('Reaction Energy (delta E) by Primary Metal')
    axes[0].set_xlabel('Primary Metal')
    axes[0].set_ylabel('delta E (eV/CO2)')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(True, axis='y', linestyle='--', alpha=0.7)
    sns.scatterplot(data=df, x='stability_penalty', y='delta_E', hue='metal_family', ax=axes[1], alpha=0.7, palette='Set1')
    axes[1].set_title('Reaction Energy vs. Stability Penalty')
    axes[1].set_xlabel('Stability Penalty (eV/atom)')
    axes[1].set_ylabel('delta E (eV/CO2)')
    axes[1].grid(True, linestyle='--', alpha=0.7)
    axes[1].legend(title='Metal Family', bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=4, fontsize='small')
    df_valid_treg = df[(df['valid_T_reg']) & (df['T_reg'] > 0)].copy()
    sns.histplot(data=df_valid_treg, x='T_reg', bins=50, ax=axes[2], color='steelblue', edgecolor='black')
    axes[2].axvspan(573.15, 873.15, color='forestgreen', alpha=0.3, label='Target Window (573-873 K)')
    axes[2].set_title('Regeneration Temperature (T_reg) Distribution')
    axes[2].set_xlabel('T_reg (K)')
    axes[2].set_ylabel('Count')
    axes[2].grid(True, linestyle='--', alpha=0.7)
    axes[2].legend()
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename = 'thermodynamic_landscape_' + str(timestamp) + '.png'
    plot_filepath = os.path.join(data_dir, plot_filename)
    plt.savefig(plot_filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print('Saved to ' + plot_filepath)
    print('\n--- Thermodynamic Landscape Summary ---')
    print('Total materials plotted (filtered): ' + str(len(df)))
    print('Primary metals identified: ' + ', '.join(df['primary_metal'].unique()))
    print('\nMedian delta E by Primary Metal (eV/CO2):')
    median_delta_e = df.groupby('primary_metal')['delta_E'].median().sort_values()
    for metal, val in median_delta_e.items():
        print('  ' + metal + ': ' + str(round(val, 3)))
    print('\nStability Penalty Statistics (eV/atom):')
    print('  Min: ' + str(round(df['stability_penalty'].min(), 3)))
    print('  Max: ' + str(round(df['stability_penalty'].max(), 3)))
    print('  Mean: ' + str(round(df['stability_penalty'].mean(), 3)))
    print('\nRegeneration Temperature (T_reg) Statistics (K):')
    print('  Valid T_reg count (> 0 K): ' + str(len(df_valid_treg)))
    print('  Min: ' + str(round(df_valid_treg['T_reg'].min(), 1)))
    print('  Max: ' + str(round(df_valid_treg['T_reg'].max(), 1)))
    print('  Mean: ' + str(round(df_valid_treg['T_reg'].mean(), 1)))
    in_window = df_valid_treg[(df_valid_treg['T_reg'] >= 573.15) & (df_valid_treg['T_reg'] <= 873.15)]
    print('  Count in target window (573-873 K): ' + str(len(in_window)) + ' (' + str(round(len(in_window)/len(df_valid_treg)*100, 1)) + '%)')
    print('---------------------------------------')