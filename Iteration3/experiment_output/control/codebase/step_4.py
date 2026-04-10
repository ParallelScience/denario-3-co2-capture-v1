# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def calculate_pareto_front(df, delta_E_CaO):
    df['obj1'] = np.abs(df['delta_E'] - delta_E_CaO)
    df['obj2'] = np.abs(df['T_reg'] - 723.15)
    df['obj3'] = np.abs(df['volume_expansion_ratio'])
    costs = df[['obj1', 'obj2', 'obj3']].values
    is_pareto = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        dominated = np.any(np.all(costs <= c, axis=1) & np.any(costs < c, axis=1))
        if dominated:
            is_pareto[i] = False
    df['is_pareto'] = is_pareto
    obj1_max = df['obj1'].max()
    obj2_max = df['obj2'].max()
    obj3_max = df['obj3'].max()
    obj1_norm = df['obj1'] / obj1_max if obj1_max > 0 else df['obj1']
    obj2_norm = df['obj2'] / obj2_max if obj2_max > 0 else df['obj2']
    obj3_norm = df['obj3'] / obj3_max if obj3_max > 0 else df['obj3']
    df['score'] = np.sqrt(obj1_norm**2 + obj2_norm**2 + obj3_norm**2)
    return df

def plot_scatter_dE_Treg(df, timestamp):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='T_reg', y='delta_E', hue='oxide_crystal_system', palette='tab10', alpha=0.7)
    plt.xlabel('Regeneration Temperature, T_reg (K)')
    plt.ylabel('Reaction Energy, delta E (eV/formula unit)')
    plt.title('Reaction Energy vs. Regeneration Temperature')
    plt.legend(title='Oxide Crystal System', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plot_path = os.path.join('data', 'scatter_dE_Treg_1_' + timestamp + '.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print('Scatter plot saved to ' + plot_path)

def plot_pareto_front(df, timestamp):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df[~df['is_pareto']], x='delta_E', y='volume_expansion_ratio', color='gray', alpha=0.5, label='Suboptimal')
    sns.scatterplot(data=df[df['is_pareto']], x='delta_E', y='volume_expansion_ratio', color='red', s=100, edgecolor='black', label='Pareto Optimal')
    plt.xlabel('Reaction Energy, delta E (eV/formula unit)')
    plt.ylabel('Volume Expansion Ratio (delta V / V_oxide)')
    plt.title('Pareto Front: Reaction Energy vs. Volume Expansion Ratio')
    plt.legend()
    plt.tight_layout()
    plot_path = os.path.join('data', 'pareto_dE_vol_2_' + timestamp + '.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print('Pareto front plot saved to ' + plot_path)

def plot_boxplot_dE_metal(df, timestamp):
    plt.figure(figsize=(12, 6))
    capture_elements = ['Ca', 'Mg', 'Li', 'Na', 'K', 'Ba', 'Sr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Al']
    present_elements = [el for el in capture_elements if el in df['primary_metal'].unique()]
    sns.boxplot(data=df, x='primary_metal', y='delta_E', order=present_elements, hue='primary_metal', palette='Set3', legend=False)
    plt.xlabel('Capture Element Family')
    plt.ylabel('Reaction Energy, delta E (eV/formula unit)')
    plt.title('Reaction Energy Distribution by Capture Element Family')
    plt.tight_layout()
    plot_path = os.path.join('data', 'boxplot_dE_metal_3_' + timestamp + '.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print('Box plot saved to ' + plot_path)

def main():
    sns.set_theme(style='whitegrid')
    plt.rcParams['text.usetex'] = False
    input_path = os.path.join('data', 'evaluated_candidates.parquet')
    if not os.path.exists(input_path):
        print('Error: ' + input_path + ' not found.')
        return
    df = pd.read_parquet(input_path)
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['delta_E', 'T_reg', 'volume_expansion_ratio']).copy()
    cao_mask = (df['oxide_formula'] == 'CaO') & (df['carbonate_formula'] == 'CaCO3')
    if cao_mask.any():
        delta_E_CaO = df.loc[cao_mask, 'delta_E'].iloc[0]
    else:
        ca_df = df[df['primary_metal'] == 'Ca']
        if not ca_df.empty:
            delta_E_CaO = ca_df['delta_E'].mean()
        else:
            delta_E_CaO = 4.66
    df = calculate_pareto_front(df, delta_E_CaO)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot_scatter_dE_Treg(df, timestamp)
    plot_pareto_front(df, timestamp)
    plot_boxplot_dE_metal(df, timestamp)
    pareto_df = df[df['is_pareto']].sort_values('score').head(20)
    print('\n=== Top 20 Pareto-Optimal Candidates ===')
    print('Ranked by distance to ideal objective point (delta E ~ CaO, T_reg ~ 450C, min volume expansion)')
    display_cols = ['oxide_formula', 'carbonate_formula', 'primary_metal', 'delta_E', 'T_reg', 'volume_expansion_ratio', 'score']
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(pareto_df[display_cols].to_string(index=False))

if __name__ == '__main__':
    main()