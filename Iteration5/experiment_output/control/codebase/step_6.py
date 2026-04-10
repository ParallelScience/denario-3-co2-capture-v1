# filename: codebase/step_6.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time

def final_scoring_and_visualization():
    data_dir = 'data/'
    input_path = os.path.join(data_dir, 'kinetic_sintering_assessment.csv')
    if not os.path.exists(input_path):
        print('Error: Input file ' + input_path + ' not found.')
        return
    df = pd.read_csv(input_path)
    df['V_ox_fu'] = df['oxide_volume'] * df['oxide_formula_atoms'] / df['oxide_nsites']
    df['V_carb_fu'] = df['carbonate_volume'] * df['carbonate_formula_atoms'] / df['carbonate_nsites']
    df['delta_V_pct'] = ((df['V_carb_fu'] - df['c_ox'] * df['V_ox_fu']) / (df['c_ox'] * df['V_ox_fu'])) * 100
    G_abs = df['delta_G_700K'].abs()
    df['norm_G'] = 1.0 - (G_abs - G_abs.min()) / (G_abs.max() - G_abs.min())
    V_abs = df['delta_V_pct'].abs()
    df['norm_V'] = 1.0 - (V_abs - V_abs.min()) / (V_abs.max() - V_abs.min())
    M = df['operating_margin']
    df['norm_M'] = (M - M.min()) / (M.max() - M.min())
    df['composite_score'] = df['norm_G'] + df['norm_V'] + df['norm_M']
    df_sorted = df.sort_values('composite_score', ascending=False)
    top_20 = df_sorted.head(20)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print('=== Final Ranked Candidates (Top 20) ===')
    cols_to_print = ['metal_system', 'oxide_formula', 'carbonate_formula', 'delta_G_700K', 'delta_V_pct', 'operating_margin', 'composite_score']
    print_df = top_20[cols_to_print].copy()
    print_df['delta_G_700K'] = print_df['delta_G_700K'].round(3)
    print_df['delta_V_pct'] = print_df['delta_V_pct'].round(2)
    print_df['operating_margin'] = print_df['operating_margin'].round(1)
    print_df['composite_score'] = print_df['composite_score'].round(3)
    print(print_df.to_string(index=False))
    output_csv = os.path.join(data_dir, 'final_ranked_candidates.csv')
    df_sorted.to_csv(output_csv, index=False)
    print('\nFinal ranked list saved to ' + output_csv)
    plt.rcParams['text.usetex'] = False
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    ax = axs[0, 0]
    poor_mask = (df['delta_V_pct'].abs() > 20) | (df['delta_G_700K'] < -1.5) | (df['delta_G_700K'] > 0.5)
    good_mask = ~poor_mask
    ax.scatter(df[poor_mask]['delta_V_pct'], df[poor_mask]['delta_G_700K'], alpha=0.5, color='red', label='Poor Sorbents (|Delta V| > 20% or extreme Delta G)')
    ax.scatter(df[good_mask]['delta_V_pct'], df[good_mask]['delta_G_700K'], alpha=0.7, color='green', label='Good Sorbents')
    ax.set_xlabel('Volume Expansion Delta V (%)')
    ax.set_ylabel('Delta G at 700K (eV/CO2)')
    ax.set_title('Pareto Front: Delta G vs Delta V')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax = axs[0, 1]
    top_metals = df['metal_system'].value_counts().head(10).index
    sns.boxplot(data=df[df['metal_system'].isin(top_metals)], x='metal_system', y='delta_H', ax=ax, hue='metal_system', legend=False, palette='Set3')
    ax.set_xlabel('Metal System')
    ax.set_ylabel('Delta H (eV/CO2)')
    ax.set_title('Delta H by Top 10 Elemental Families')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3)
    ax = axs[1, 0]
    ax.hist(df['operating_margin'], bins=50, color='skyblue', edgecolor='black')
    ax.axvline(0, color='red', linestyle='--', label='Zero Margin (T_T = 700K)')
    ax.set_xlabel('Operating Margin (K)')
    ax.set_ylabel('Frequency')
    ax.set_title('Tamman Temperature Margin Distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax = axs[1, 1]
    iso_path = os.path.join(data_dir, 'isostructural_substitution.csv')
    if os.path.exists(iso_path):
        iso_df = pd.read_csv(iso_path)
        iso_plot = iso_df[iso_df['Status'] == 'In Dataset'].dropna(subset=['Delta_H_Shift']).copy()
        iso_plot = iso_plot.sort_values('Delta_H_Shift')
        iso_plot['label'] = iso_plot['Reference'] + ' -> ' + iso_plot['Candidate_Carbonate']
        ax.bar(iso_plot['label'], iso_plot['Delta_H_Shift'], color='orange', edgecolor='black')
        ax.set_xlabel('Substitution')
        ax.set_ylabel('Delta H Shift (eV/CO2)')
        ax.set_title('Isostructural Substitution Energy Shifts')
        ax.tick_params(axis='x', rotation=90)
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'Isostructural data not found', ha='center', va='center')
        ax.set_title('Isostructural Substitution Energy Shifts')
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename = 'multi_panel_analysis_1_' + str(timestamp) + '.png'
    plot_path = os.path.join(data_dir, plot_filename)
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print('\nMulti-panel figure saved to ' + plot_path)

if __name__ == '__main__':
    final_scoring_and_visualization()