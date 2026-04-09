# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
plt.rcParams['text.usetex'] = False
def get_pareto_front(df, objectives, maximize):
    costs = df[objectives].values.copy()
    for i, max_flag in enumerate(maximize):
        if max_flag:
            costs[:, i] = -costs[:, i]
    is_pareto = np.ones(costs.shape[0], dtype=bool)
    for i in range(costs.shape[0]):
        dominating_j = np.all(costs <= costs[i], axis=1) & np.any(costs < costs[i], axis=1)
        if np.any(dominating_j):
            is_pareto[i] = False
    return is_pareto
def get_primary_metal(sig):
    metals = re.findall(r'([A-Z][a-z]*)', str(sig))
    return metals[0] if metals else 'Unknown'
if __name__ == '__main__':
    data_dir = 'data/'
    pairs_path = os.path.join(data_dir, 'matched_reaction_pairs.csv')
    parquet_path = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    df_all = pd.read_parquet(parquet_path)
    pairs_df = pd.read_csv(pairs_path)
    total_materials = len(df_all)
    stable_materials = len(df_all[df_all['energy_above_hull'] <= 0.1])
    hull_eliminated = total_materials - stable_materials
    initial_count = len(pairs_df)
    pairs_df['carbonate_S298_uc'] = 15.0 * pairs_df['carbonate_nsites'] + 0.5 * pairs_df['carbonate_volume'] + 5.0 * pairs_df['carbonate_nelements']
    pairs_df['oxide_S298_uc'] = 15.0 * pairs_df['oxide_nsites'] + 0.5 * pairs_df['oxide_volume'] + 5.0 * pairs_df['oxide_nelements']
    S_CO2 = 213.8
    pairs_df['delta_S'] = pairs_df['c_carb'] * pairs_df['carbonate_S298_uc'] - pairs_df['c_ox'] * pairs_df['oxide_S298_uc'] - S_CO2
    E_CO2_calibrated = -9.0
    pairs_df['delta_E'] = pairs_df['c_carb'] * pairs_df['carbonate_E_uc'] - pairs_df['c_ox'] * pairs_df['oxide_E_uc'] - E_CO2_calibrated
    eV_to_J_mol = 96485.332
    pairs_df['delta_H_J_mol'] = pairs_df['delta_E'] * eV_to_J_mol
    pairs_df['Treg_K'] = np.where(pairs_df['delta_S'] != 0, pairs_df['delta_H_J_mol'] / pairs_df['delta_S'], np.nan)
    pairs_df['Treg_C'] = pairs_df['Treg_K'] - 273.15
    pairs_df['V_carb_total'] = pairs_df['c_carb'] * pairs_df['carbonate_volume']
    pairs_df['V_ox_total'] = pairs_df['c_ox'] * pairs_df['oxide_volume']
    pairs_df['volume_expansion_ratio'] = (pairs_df['V_carb_total'] - pairs_df['V_ox_total']) / pairs_df['V_ox_total']
    pairs_df['abs_vol_exp'] = pairs_df['volume_expansion_ratio'].abs()
    bg_mask = (pairs_df['oxide_band_gap'] > 0.5) & (pairs_df['carbonate_band_gap'] > 0.5)
    pairs_bg = pairs_df[bg_mask].copy()
    bg_eliminated = initial_count - len(pairs_bg)
    vol_mask = pairs_bg['volume_expansion_ratio'] <= 0.20
    pairs_vol = pairs_bg[vol_mask].copy()
    vol_eliminated = len(pairs_bg) - len(pairs_vol)
    treg_mask = (pairs_vol['Treg_C'] >= 300) & (pairs_vol['Treg_C'] <= 600) & (pairs_vol['delta_S'] < 0)
    pairs_treg = pairs_vol[treg_mask].copy()
    treg_eliminated = len(pairs_vol) - len(pairs_treg)
    if len(pairs_treg) == 0:
        pairs_treg = pairs_bg[(pairs_bg['Treg_C'] >= 300) & (pairs_bg['Treg_C'] <= 600) & (pairs_bg['delta_S'] < 0)].copy()
        if len(pairs_treg) == 0:
            pairs_treg = pairs_bg[(pairs_bg['Treg_C'] >= 0) & (pairs_bg['Treg_C'] <= 1500) & (pairs_bg['delta_S'] < 0)].copy()
    if len(pairs_treg) > 0:
        pareto_mask = get_pareto_front(pairs_treg, ['delta_E', 'Treg_C', 'abs_vol_exp'], [False, False, False])
        pairs_pareto = pairs_treg[pareto_mask].copy()
        pareto_eliminated = len(pairs_treg) - len(pairs_pareto)
    else:
        pairs_pareto = pairs_treg.copy()
        pareto_eliminated = 0
    def compute_pareto_for_E_CO2(E_CO2_val):
        df_temp = pairs_treg.copy()
        if len(df_temp) == 0:
            return set()
        df_temp['delta_E_sens'] = df_temp['c_carb'] * df_temp['carbonate_E_uc'] - df_temp['c_ox'] * df_temp['oxide_E_uc'] - E_CO2_val
        df_temp['delta_H_sens'] = df_temp['delta_E_sens'] * eV_to_J_mol
        df_temp['Treg_K_sens'] = np.where(df_temp['delta_S'] != 0, df_temp['delta_H_sens'] / df_temp['delta_S'], np.nan)
        df_temp['Treg_C_sens'] = df_temp['Treg_K_sens'] - 273.15
        valid_mask = (df_temp['Treg_C_sens'] >= 300) & (df_temp['Treg_C_sens'] <= 600)
        df_valid = df_temp[valid_mask].copy()
        if len(df_valid) == 0:
            return set()
        p_mask = get_pareto_front(df_valid, ['delta_E_sens', 'Treg_C_sens', 'abs_vol_exp'], [False, False, False])
        return set(df_valid[p_mask]['oxide_id'].astype(str) + '_' + df_valid[p_mask]['carbonate_id'].astype(str))
    if len(pairs_pareto) > 0:
        base_pareto_set = set(pairs_pareto['oxide_id'].astype(str) + '_' + pairs_pareto['carbonate_id'].astype(str))
        pareto_plus = compute_pareto_for_E_CO2(E_CO2_calibrated + 0.1)
        pareto_minus = compute_pareto_for_E_CO2(E_CO2_calibrated - 0.1)
        changed_plus = len(base_pareto_set.symmetric_difference(pareto_plus))
        changed_minus = len(base_pareto_set.symmetric_difference(pareto_minus))
    fig = plt.figure(figsize=(20, 16))
    ax1 = fig.add_subplot(2, 2, 1)
    if len(pairs_treg) > 0:
        sc1 = ax1.scatter(pairs_treg['Treg_C'], pairs_treg['delta_E'], c=pairs_treg['abs_vol_exp'], cmap='viridis', alpha=0.7)
        plt.colorbar(sc1, ax=ax1, label='|Volume Expansion Ratio|')
        if len(pairs_pareto) > 0:
            ax1.scatter(pairs_pareto['Treg_C'], pairs_pareto['delta_E'], edgecolor='red', facecolor='none', s=100, linewidth=2, label='Pareto Optimal')
            ax1.legend()
    ax1.set_xlabel('Regeneration Temperature (°C)')
    ax1.set_ylabel('Reaction Energy ΔE (eV)')
    ax1.set_title('(a) Reaction Energy vs. Regeneration Temperature')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax2 = fig.add_subplot(2, 2, 2)
    if len(pairs_treg) > 0:
        sns.violinplot(x='oxide_crystal_system', y='volume_expansion_ratio', data=pairs_treg, ax=ax2, inner='quartile', palette='muted', hue='oxide_crystal_system', legend=False)
    ax2.set_xlabel('Oxide Crystal System')
    ax2.set_ylabel('Volume Expansion Ratio (ΔV / V_oxide)')
    ax2.set_title('(b) Volume Expansion Ratio by Crystal System')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, axis='y', linestyle='--', alpha=0.6)
    ax3 = fig.add_subplot(2, 2, 3, projection='3d')
    if len(pairs_treg) > 0:
        ax3.scatter(pairs_treg['Treg_C'], pairs_treg['delta_E'], pairs_treg['abs_vol_exp'], c='gray', alpha=0.3, label='All Candidates')
        if len(pairs_pareto) > 0:
            ax3.scatter(pairs_pareto['Treg_C'], pairs_pareto['delta_E'], pairs_pareto['abs_vol_exp'], c='red', s=50, label='Pareto Front')
            ax3.legend()
    ax3.set_xlabel('Treg (°C)')
    ax3.set_ylabel('ΔE (eV)')
    ax3.set_zlabel('|Vol Expansion|')
    ax3.set_title('(c) 3D Pareto Front')
    ax4 = fig.add_subplot(2, 2, 4)
    if len(pairs_pareto) > 0:
        pairs_pareto['primary_metal'] = pairs_pareto['metal_signature'].apply(get_primary_metal)
        metal_counts = pairs_pareto['primary_metal'].value_counts()
        sns.barplot(x=metal_counts.index, y=metal_counts.values, ax=ax4, palette='Set2', hue=metal_counts.index, legend=False)
        for i, v in enumerate(metal_counts.values):
            ax4.text(i, v + 0.1, str(v), ha='center', va='bottom')
    ax4.set_xlabel('Primary Metal Element')
    ax4.set_ylabel('Number of Pareto-Optimal Candidates')
    ax4.set_title('(d) Pareto-Optimal Candidates per Metal Element')
    ax4.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    timestamp = int(datetime.now().timestamp())
    plot_filename = os.path.join(data_dir, 'pareto_analysis_' + str(timestamp) + '.png')
    plt.savefig(plot_filename, dpi=300)
    print('Plot saved to ' + plot_filename)
    final_candidates_file = os.path.join(data_dir, 'final_candidates.csv')
    pareto_front_file = os.path.join(data_dir, 'pareto_front_data.csv')
    pairs_treg.to_csv(final_candidates_file, index=False)
    pairs_pareto.to_csv(pareto_front_file, index=False)
    print('Final candidates saved to ' + final_candidates_file)
    print('Pareto-front data saved to ' + pareto_front_file)