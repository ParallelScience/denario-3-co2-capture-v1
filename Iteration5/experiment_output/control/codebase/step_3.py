# filename: codebase/step_3.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime

def analyze_volume_change():
    data_dir = "data/"
    input_path = os.path.join(data_dir, "thermodynamic_landscape.csv")
    if not os.path.exists(input_path):
        print("Error: Input file " + input_path + " not found.")
        return
    df = pd.read_csv(input_path)
    df['V_ox_fu'] = df['oxide_volume'] * df['oxide_formula_atoms'] / df['oxide_nsites']
    df['V_carb_fu'] = df['carbonate_volume'] * df['carbonate_formula_atoms'] / df['carbonate_nsites']
    df['delta_V_pct'] = ((df['V_carb_fu'] - df['c_ox'] * df['V_ox_fu']) / (df['c_ox'] * df['V_ox_fu'])) * 100
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print("=== Volume Expansion Analysis ===")
    print("Total reaction pairs: " + str(len(df)))
    print("\nDistribution of Volume Expansion (ΔV %):")
    print(df['delta_V_pct'].describe().to_string())
    robust_df = df[df['delta_V_pct'].abs() <= 20.0].copy()
    print("\nNumber of mechanically robust candidates (|ΔV| <= 20%): " + str(len(robust_df)))
    df['abs_delta_V'] = df['delta_V_pct'].abs()
    smallest_dv = df.sort_values('abs_delta_V').head(10)
    cols_to_show = ['metal_system', 'oxide_formula', 'carbonate_formula', 'delta_V_pct']
    print("\nTop 10 candidates with smallest absolute volume change:")
    print(smallest_dv[cols_to_show].to_string(index=False))
    df = df.drop(columns=['abs_delta_V'])
    plt.rcParams['text.usetex'] = False
    plt.figure(figsize=(10, 6))
    plt.hist(df['delta_V_pct'], bins=100, color='skyblue', edgecolor='black')
    plt.axvline(x=20, color='red', linestyle='--', label='+20% Limit')
    plt.axvline(x=-20, color='red', linestyle='--', label='-20% Limit')
    plt.title('Distribution of Solid Volume Expansion (ΔV %)')
    plt.xlabel('Volume Expansion (%)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename = "volume_expansion_histogram_" + str(timestamp) + ".png"
    plot_path = os.path.join(data_dir, plot_filename)
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print("\nHistogram saved to " + plot_path)
    output_path = os.path.join(data_dir, "mechanically_robust_candidates.csv")
    robust_df.to_csv(output_path, index=False)
    print("Mechanically robust candidates saved to " + output_path)

if __name__ == '__main__':
    analyze_volume_change()