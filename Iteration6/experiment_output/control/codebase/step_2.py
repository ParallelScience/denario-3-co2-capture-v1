# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import seaborn as sns
import time

def calculate_theta_d(density, volume, nsites):
    density = np.maximum(density, 1e-4)
    molar_mass_cell = density * volume * 0.602214
    M_atom = molar_mass_cell / nsites
    V_m_atom = M_atom / density
    Tm = 1000.0
    theta_d = 137.0 * np.sqrt(Tm / (M_atom * (V_m_atom ** (2.0/3.0))))
    return theta_d

def debye_entropy_per_atom(theta_d, T):
    kB = 8.617333262145e-5
    x = theta_d / T
    if x < 1e-3:
        return 3.0 * kB * (4.0/3.0 - np.log(x))
    def integrand(t):
        if t == 0:
            return 0.0
        return (t**3) / (np.exp(t) - 1.0)
    integral, _ = integrate.quad(integrand, 0, x)
    return 3.0 * kB * ((4.0 / (x**3)) * integral - np.log(1.0 - np.exp(-x)))

if __name__ == '__main__':
    plt.rcParams['text.usetex'] = False
    data_dir = 'data/'
    data_path = os.path.join(data_dir, 'matched_pairs.parquet')
    pairs = pd.read_parquet(data_path)
    pairs['theta_d_ox'] = calculate_theta_d(pairs['density_g_cm3_ox'], pairs['volume_A3_ox'], pairs['nsites_ox'])
    pairs['theta_d_cb'] = calculate_theta_d(pairs['density_g_cm3_cb'], pairs['volume_A3_cb'], pairs['nsites_cb'])
    debye_entropy_vec = np.vectorize(debye_entropy_per_atom)
    pairs['S_vib_atom_ox'] = debye_entropy_vec(pairs['theta_d_ox'], 700.0)
    pairs['S_vib_atom_cb'] = debye_entropy_vec(pairs['theta_d_cb'], 700.0)
    pairs['atoms_per_metal_ox'] = pairs['parsed_total_atoms_ox'] / pairs['parsed_total_metals_ox']
    pairs['atoms_per_metal_cb'] = pairs['parsed_total_atoms_cb'] / pairs['parsed_total_metals_cb']
    pairs['w'] = pairs['parsed_c_count_cb'] / pairs['parsed_total_metals_cb']
    pairs['E_ox'] = pairs['formation_energy_per_atom_ox'] * pairs['atoms_per_metal_ox']
    pairs['E_cb'] = pairs['formation_energy_per_atom_cb'] * pairs['atoms_per_metal_cb']
    pairs['S_ox'] = pairs['S_vib_atom_ox'] * pairs['atoms_per_metal_ox']
    pairs['S_cb'] = pairs['S_vib_atom_cb'] * pairs['atoms_per_metal_cb']
    E_CO2 = -11.17
    S_CO2 = 0.00269
    T = 700.0
    P_CO2 = 0.15
    kB = 8.617333262145e-5
    pairs['delta_H'] = (pairs['E_cb'] - pairs['E_ox'] - pairs['w'] * E_CO2) / pairs['w']
    pairs['delta_S'] = (pairs['S_cb'] - pairs['S_ox'] - pairs['w'] * S_CO2) / pairs['w']
    pairs['delta_G'] = pairs['delta_H'] - T * pairs['delta_S'] - kB * T * np.log(P_CO2)
    pairs_exploded = pairs.explode('capture_elements')
    stats = pairs_exploded.groupby('capture_elements')[['delta_H', 'delta_G']].agg(['mean', 'median', 'min', 'max'])
    print('Thermodynamic Statistics per Capture Element Family (eV/CO2):')
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(stats.to_string())
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    sns.boxplot(data=pairs_exploded, x='capture_elements', y='delta_H', ax=axes[0], color='skyblue')
    axes[0].set_title('Distribution of Delta H per Capture Element')
    axes[0].set_xlabel('Capture Element')
    axes[0].set_ylabel('Delta H (eV/CO2)')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(axis='y', linestyle='--', alpha=0.7)
    sns.boxplot(data=pairs_exploded, x='capture_elements', y='delta_G', ax=axes[1], color='lightgreen')
    axes[1].set_title('Distribution of Delta G (700 K, 0.15 bar) per Capture Element')
    axes[1].set_xlabel('Capture Element')
    axes[1].set_ylabel('Delta G (eV/CO2)')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename = os.path.join(data_dir, 'thermo_distributions_2_' + str(timestamp) + '.png')
    plt.savefig(plot_filename, dpi=300)
    print('Box plot saved to ' + plot_filename)
    output_file = os.path.join(data_dir, 'thermo_properties.parquet')
    pairs.to_parquet(output_file, index=False)
    print('Calculated thermodynamic properties saved to ' + output_file)