# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
from datetime import datetime

plt.rcParams['text.usetex'] = False

ELEMENT_DESCRIPTORS = {
    'H': {'EN': 2.20, 'AR': 53, 'IR': 25},
    'Li': {'EN': 0.98, 'AR': 145, 'IR': 76},
    'Be': {'EN': 1.57, 'AR': 112, 'IR': 45},
    'B': {'EN': 2.04, 'AR': 87, 'IR': 27},
    'C': {'EN': 2.55, 'AR': 67, 'IR': 16},
    'N': {'EN': 3.04, 'AR': 56, 'IR': 16},
    'O': {'EN': 3.44, 'AR': 48, 'IR': 140},
    'F': {'EN': 3.98, 'AR': 42, 'IR': 133},
    'Na': {'EN': 0.93, 'AR': 190, 'IR': 102},
    'Mg': {'EN': 1.31, 'AR': 145, 'IR': 72},
    'Al': {'EN': 1.61, 'AR': 118, 'IR': 53.5},
    'Si': {'EN': 1.90, 'AR': 111, 'IR': 40},
    'P': {'EN': 2.19, 'AR': 98, 'IR': 38},
    'S': {'EN': 2.58, 'AR': 88, 'IR': 184},
    'Cl': {'EN': 3.16, 'AR': 79, 'IR': 181},
    'K': {'EN': 0.82, 'AR': 243, 'IR': 138},
    'Ca': {'EN': 1.00, 'AR': 194, 'IR': 100},
    'Sc': {'EN': 1.36, 'AR': 184, 'IR': 74.5},
    'Ti': {'EN': 1.54, 'AR': 176, 'IR': 60.5},
    'V': {'EN': 1.63, 'AR': 171, 'IR': 79},
    'Cr': {'EN': 1.66, 'AR': 166, 'IR': 61.5},
    'Mn': {'EN': 1.55, 'AR': 161, 'IR': 83},
    'Fe': {'EN': 1.83, 'AR': 156, 'IR': 78},
    'Co': {'EN': 1.88, 'AR': 152, 'IR': 74.5},
    'Ni': {'EN': 1.91, 'AR': 149, 'IR': 69},
    'Cu': {'EN': 1.90, 'AR': 145, 'IR': 73},
    'Zn': {'EN': 1.65, 'AR': 142, 'IR': 74},
    'Ga': {'EN': 1.81, 'AR': 136, 'IR': 62},
    'Ge': {'EN': 2.01, 'AR': 125, 'IR': 53},
    'As': {'EN': 2.18, 'AR': 114, 'IR': 58},
    'Se': {'EN': 2.55, 'AR': 103, 'IR': 198},
    'Br': {'EN': 2.96, 'AR': 94, 'IR': 196},
    'Rb': {'EN': 0.82, 'AR': 265, 'IR': 152},
    'Sr': {'EN': 0.95, 'AR': 219, 'IR': 118},
    'Y': {'EN': 1.22, 'AR': 212, 'IR': 90},
    'Zr': {'EN': 1.33, 'AR': 206, 'IR': 72},
    'Nb': {'EN': 1.6, 'AR': 198, 'IR': 64},
    'Mo': {'EN': 2.16, 'AR': 190, 'IR': 59},
    'Ru': {'EN': 2.2, 'AR': 178, 'IR': 62},
    'Rh': {'EN': 2.28, 'AR': 173, 'IR': 66.5},
    'Pd': {'EN': 2.20, 'AR': 169, 'IR': 86},
    'Ag': {'EN': 1.93, 'AR': 165, 'IR': 115},
    'Cd': {'EN': 1.69, 'AR': 161, 'IR': 95},
    'In': {'EN': 1.78, 'AR': 156, 'IR': 80},
    'Sn': {'EN': 1.96, 'AR': 145, 'IR': 69},
    'Sb': {'EN': 2.05, 'AR': 133, 'IR': 76},
    'Te': {'EN': 2.1, 'AR': 123, 'IR': 221},
    'I': {'EN': 2.66, 'AR': 115, 'IR': 220},
    'Cs': {'EN': 0.79, 'AR': 298, 'IR': 167},
    'Ba': {'EN': 0.89, 'AR': 253, 'IR': 135},
    'La': {'EN': 1.1, 'AR': 195, 'IR': 103.2},
    'Ce': {'EN': 1.12, 'AR': 185, 'IR': 101},
    'Pr': {'EN': 1.13, 'AR': 247, 'IR': 99},
    'Nd': {'EN': 1.14, 'AR': 206, 'IR': 98.3},
    'Sm': {'EN': 1.17, 'AR': 238, 'IR': 95.8},
    'Eu': {'EN': 1.2, 'AR': 231, 'IR': 117},
    'Gd': {'EN': 1.2, 'AR': 233, 'IR': 93.8},
    'Tb': {'EN': 1.2, 'AR': 225, 'IR': 92.3},
    'Dy': {'EN': 1.22, 'AR': 228, 'IR': 91.2},
    'Ho': {'EN': 1.23, 'AR': 226, 'IR': 90.1},
    'Er': {'EN': 1.24, 'AR': 226, 'IR': 89},
    'Tm': {'EN': 1.25, 'AR': 222, 'IR': 88},
    'Yb': {'EN': 1.1, 'AR': 222, 'IR': 102},
    'Lu': {'EN': 1.27, 'AR': 217, 'IR': 86.1},
    'Hf': {'EN': 1.3, 'AR': 208, 'IR': 71},
    'Ta': {'EN': 1.5, 'AR': 200, 'IR': 64},
    'W': {'EN': 2.36, 'AR': 193, 'IR': 60},
    'Re': {'EN': 1.9, 'AR': 188, 'IR': 53},
    'Os': {'EN': 2.2, 'AR': 185, 'IR': 63},
    'Ir': {'EN': 2.2, 'AR': 180, 'IR': 62.5},
    'Pt': {'EN': 2.28, 'AR': 177, 'IR': 62.5},
    'Au': {'EN': 2.54, 'AR': 174, 'IR': 137},
    'Hg': {'EN': 2.0, 'AR': 171, 'IR': 102},
    'Tl': {'EN': 1.62, 'AR': 156, 'IR': 150},
    'Pb': {'EN': 2.33, 'AR': 154, 'IR': 119},
    'Bi': {'EN': 2.02, 'AR': 143, 'IR': 103},
}

def get_weighted_descriptor(comp_str, descriptor_key):
    try:
        comp = ast.literal_eval(comp_str)
        val = 0.0
        for elem, frac in comp:
            if elem in ELEMENT_DESCRIPTORS:
                val += ELEMENT_DESCRIPTORS[elem][descriptor_key] * frac
            else:
                return np.nan
        return val
    except Exception:
        return np.nan

def main():
    data_dir = "data/"
    input_path = os.path.join(data_dir, "all_valid_pairs_with_energy_corrected.csv")
    if not os.path.exists(input_path):
        return
    df = pd.read_csv(input_path)
    df['EN_mean'] = df['metal_comp'].apply(lambda x: get_weighted_descriptor(x, 'EN'))
    df['AR_mean'] = df['metal_comp'].apply(lambda x: get_weighted_descriptor(x, 'AR'))
    df['IR_mean'] = df['metal_comp'].apply(lambda x: get_weighted_descriptor(x, 'IR'))
    df_clean = df.dropna(subset=['EN_mean', 'AR_mean', 'IR_mean', 'delta_E_norm', 'volume_A3_ox', 'density_g_cm3_ox']).copy()
    descriptors = ['EN_mean', 'AR_mean', 'IR_mean', 'volume_A3_ox', 'density_g_cm3_ox']
    descriptor_names = {
        'EN_mean': 'Pauling Electronegativity',
        'AR_mean': 'Atomic Radius (pm)',
        'IR_mean': 'Ionic Radius (pm)',
        'volume_A3_ox': 'Oxide Volume (A^3)',
        'density_g_cm3_ox': 'Oxide Density (g/cm^3)'
    }
    results = []
    for desc in descriptors:
        pearson_corr, p_p = pearsonr(df_clean[desc], df_clean['delta_E_norm'])
        spearman_corr, p_s = spearmanr(df_clean[desc], df_clean['delta_E_norm'])
        results.append({
            'Descriptor': descriptor_names[desc],
            'Pearson_r': round(pearson_corr, 4),
            'Pearson_p': format(p_p, '.4e'),
            'Spearman_r': round(spearman_corr, 4),
            'Spearman_p': format(p_s, '.4e')
        })
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    stats_df = df_clean[descriptors + ['delta_E_norm']].describe()
    print(stats_df.to_string())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    for i, desc in enumerate(descriptors):
        ax = axes[i]
        sns.regplot(data=df_clean, x=desc, y='delta_E_norm', ax=ax, scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
        ax.set_title("Delta E vs " + descriptor_names[desc])
        ax.set_xlabel(descriptor_names[desc])
        ax.set_ylabel("Normalized Delta E (eV/CO2)")
        ax.grid(True, linestyle='--', alpha=0.7)
    axes[-1].set_visible(False)
    plt.tight_layout()
    plot_path = os.path.join(data_dir, "descriptor_correlations_" + timestamp + ".png")
    plt.savefig(plot_path, dpi=300)
    plt.close('all')
    output_path = os.path.join(data_dir, "final_processed_dataset_with_descriptors.csv")
    df_clean.to_csv(output_path, index=False)
    stats_path = os.path.join(data_dir, "descriptor_summary_statistics.csv")
    stats_df.to_csv(stats_path)

if __name__ == '__main__':
    main()