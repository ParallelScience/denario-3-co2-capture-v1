# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def main():
    data_dir = "data/"
    all_pairs_path = os.path.join(data_dir, "all_valid_pairs.csv")
    best_pairs_path = os.path.join(data_dir, "best_valid_pairs.csv")
    if not os.path.exists(all_pairs_path) or not os.path.exists(best_pairs_path):
        print("Error: Input files not found.")
        return
    df_all = pd.read_csv(all_pairs_path)
    df_best = pd.read_csv(best_pairs_path)
    y_all = df_all['O_per_M_ox'] * df_all['total_M_ox']
    z_all = df_all['z']
    passed_mask_y2z = np.abs(y_all - 2 * z_all) < 1e-4
    passed_count_y2z = passed_mask_y2z.sum()
    failed_count_y2z = len(df_all) - passed_count_y2z
    passed_mask_yz = np.abs(y_all - z_all) < 1e-4
    passed_count_yz = passed_mask_yz.sum()
    failed_count_yz = len(df_all) - passed_count_yz
    print("=== Oxygen Balance Check ===")
    print("Pairs passing the oxygen balance check (y=2z) as requested: " + str(passed_count_y2z) + " vs those that do not: " + str(failed_count_y2z))
    print("Pairs passing the physically correct oxygen balance check (y=z): " + str(passed_count_yz) + " vs those that do not: " + str(failed_count_yz))
    metal_counts = df_all['primary_metal_ox'].value_counts()
    print("\nMetal systems with the most pairs:")
    for metal, count in metal_counts.head(10).items():
        print("  " + str(metal) + ": " + str(count))
    E_CO2 = -11.17
    def calculate_delta_E(df):
        scale_factor = df['total_M_ox'] / df['total_M_carb']
        E_carb_scaled = df['E_f_unit_carb'] * scale_factor
        E_ox = df['E_f_unit_ox']
        z = df['z']
        delta_E = E_carb_scaled - E_ox - z * E_CO2
        delta_E_norm = delta_E / z
        return delta_E_norm
    df_all['delta_E_norm'] = calculate_delta_E(df_all)
    df_best['delta_E_norm'] = calculate_delta_E(df_best)
    print("\n=== Summary Statistics of Normalized Delta E (eV/CO2) per Metal Family ===")
    stats = df_all.groupby('primary_metal_ox')['delta_E_norm'].agg(['mean', 'median', 'std', 'min', 'max']).reset_index()
    stats = stats.sort_values('mean')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(stats.to_string(index=False))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_all, x='primary_metal_ox', y='delta_E_norm', order=stats['primary_metal_ox'])
    plt.title('Distribution of Normalized Reaction Energy (Delta E) per Metal Family')
    plt.xlabel('Primary Metal')
    plt.ylabel('Normalized Delta E (eV/CO2)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    boxplot_path = os.path.join(data_dir, "delta_E_boxplot_1_" + timestamp + ".png")
    plt.savefig(boxplot_path, dpi=300)
    plt.close()
    print("\nBox-plot saved to " + boxplot_path)
    plt.figure(figsize=(12, 8))
    sns.histplot(data=df_all, x='delta_E_norm', hue='primary_metal_ox', multiple="stack", bins=30, palette='tab20')
    plt.title('Distribution of Normalized Reaction Energy (Delta E) per Metal Family')
    plt.xlabel('Normalized Delta E (eV/CO2)')
    plt.ylabel('Count')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    dist_path = os.path.join(data_dir, "delta_E_distribution_2_" + timestamp + ".png")
    plt.savefig(dist_path, dpi=300)
    plt.close()
    print("Distribution plot saved to " + dist_path)
    plt.figure(figsize=(12, 8))
    min_val = df_all['delta_E_norm'].min()
    max_val = df_all['delta_E_norm'].max()
    if min_val == max_val:
        bins = np.linspace(min_val - 1, max_val + 1, 20)
    else:
        bins = np.linspace(min_val, max_val, 20)
    df_all['delta_E_bin'] = pd.cut(df_all['delta_E_norm'], bins=bins)
    heatmap_data = pd.crosstab(df_all['primary_metal_ox'], df_all['delta_E_bin'])
    heatmap_data = heatmap_data.div(heatmap_data.sum(axis=1), axis=0).fillna(0)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    heatmap_data.columns = [str(round(c, 2)) for c in bin_centers]
    sns.heatmap(heatmap_data, cmap='viridis', cbar_kws={'label': 'Fraction of Polymorphs'})
    plt.title('Heatmap of Normalized Delta E Distribution per Metal Family')
    plt.xlabel('Normalized Delta E (eV/CO2)')
    plt.ylabel('Primary Metal')
    plt.xticks(rotation=45)
    plt.tight_layout()
    heatmap_path = os.path.join(data_dir, "delta_E_heatmap_3_" + timestamp + ".png")
    plt.savefig(heatmap_path, dpi=300)
    plt.close()
    print("Heatmap saved to " + heatmap_path)
    df_all = df_all.drop(columns=['delta_E_bin'])
    df_all.to_csv(os.path.join(data_dir, "all_valid_pairs_with_energy.csv"), index=False)
    df_best.to_csv(os.path.join(data_dir, "best_valid_pairs_with_energy.csv"), index=False)
    print("\nSaved calculated reaction energies to data/all_valid_pairs_with_energy.csv and data/best_valid_pairs_with_energy.csv")

if __name__ == '__main__':
    main()