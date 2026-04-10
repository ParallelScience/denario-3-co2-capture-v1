# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def get_primary_metal(elements_str, target_metals):
    if not isinstance(elements_str, str):
        return 'Unknown'
    els = elements_str.split(',')
    for m in target_metals:
        if m in els:
            return m
    return els[0] if els else 'Unknown'

def main():
    data_dir = 'data/'
    input_file = os.path.join(data_dir, 'reaction_energies.csv')
    df = pd.read_csv(input_file)
    CORRECTION = -7.23
    df['reaction_energy_per_CO2'] = df['reaction_energy_per_CO2'] + CORRECTION
    df['reaction_energy'] = df['reaction_energy'] + CORRECTION * df['c_count_reduced']
    EV_PER_KJ_MOL = 1 / 96.485332
    DELTA_S_STANDARD_KJ_MOL_K = -0.214
    DELTA_S_STANDARD_EV_K = DELTA_S_STANDARD_KJ_MOL_K * EV_PER_KJ_MOL
    R_EV_K = 8.617333262e-5
    P_CO2 = 0.15
    delta_S_eff_ev_k = DELTA_S_STANDARD_EV_K + R_EV_K * np.log(P_CO2)
    df['Teq_K'] = df['reaction_energy_per_CO2'] / delta_S_eff_ev_k
    df['Teq_K'] = df['Teq_K'].apply(lambda x: x if x > 0 else np.nan)
    T_eval = 700
    df['delta_G_700K'] = df['reaction_energy_per_CO2'] - T_eval * delta_S_eff_ev_k
    temperatures = np.arange(500, 1201, 100)
    for T in temperatures:
        df['delta_G_' + str(T) + 'K'] = df['reaction_energy_per_CO2'] - T * delta_S_eff_ev_k
    target_metals = ['Ca', 'Mg', 'Li', 'Na', 'K', 'Ba', 'Sr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Al']
    df['primary_metal'] = df['metal_elements'].apply(lambda x: get_primary_metal(x, target_metals))
    valid_teq = df.dropna(subset=['Teq_K'])
    plt.rcParams['text.usetex'] = False
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    sns.histplot(data=df, x='reaction_energy_per_CO2', hue='primary_metal', multiple='stack', ax=axes[0], palette='tab20')
    axes[0].set_title('(a) Reaction Energy (ΔE) Distribution')
    axes[0].set_xlabel('ΔE (eV/CO2)')
    axes[0].set_ylabel('Count')
    sns.scatterplot(data=valid_teq, x='reaction_energy_per_CO2', y='Teq_K', hue='primary_metal', ax=axes[1], palette='tab20', legend=False)
    axes[1].set_title('(b) Equilibrium Temperature vs ΔE')
    axes[1].set_xlabel('ΔE (eV/CO2)')
    axes[1].set_ylabel('Teq (K)')
    axes[1].axhline(500, color='gray', linestyle='--', alpha=0.5)
    axes[1].axhline(1200, color='gray', linestyle='--', alpha=0.5)
    if valid_teq['Teq_K'].max() > 4000:
        axes[1].set_ylim(0, 4000)
    sns.boxplot(data=df, x='primary_metal', y='delta_G_700K', ax=axes[2], palette='tab20')
    axes[2].set_title('(c) Gibbs Free Energy at 700 K')
    axes[2].set_xlabel('Primary Metal')
    axes[2].set_ylabel('ΔG at 700 K (eV/CO2)')
    axes[2].axhline(0, color='red', linestyle='--', alpha=0.5)
    axes[2].tick_params(axis='x', rotation=45)
    plt.tight_layout()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot_filename = 'thermodynamic_analysis_3_' + timestamp + '.png'
    plot_filepath = os.path.join(data_dir, plot_filename)
    plt.savefig(plot_filepath, dpi=300)
    output_file = os.path.join(data_dir, 'thermodynamic_results.csv')
    df.to_csv(output_file, index=False)

if __name__ == '__main__':
    main()