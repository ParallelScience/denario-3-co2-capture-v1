# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
from pymatgen.core import Composition

def calculate_reaction_energy():
    data_dir = "data/"
    input_file = os.path.join(data_dir, "processed_pairs.csv")
    print("Loading processed pairs from " + input_file + "...")
    df_pairs = pd.read_csv(input_file)
    initial_count = len(df_pairs)
    df_filtered = df_pairs[(df_pairs['carb_energy_above_hull'] <= 0.1) & (df_pairs['ox_energy_above_hull'] <= 0.1)].copy()
    filtered_count = len(df_filtered)
    print("Applied strict stability filter (energy_above_hull <= 0.1 eV/atom).")
    print("Pairs retained: " + str(filtered_count) + " out of " + str(initial_count) + ".")
    reaction_energies = []
    reaction_energies_per_co2 = []
    c_counts = []
    for idx, row in df_filtered.iterrows():
        carb_comp = Composition(row['carbonate_formula']).reduced_composition
        ox_comp = Composition(row['oxide_formula']).reduced_composition
        carb_num_atoms = carb_comp.num_atoms
        ox_num_atoms = ox_comp.num_atoms
        E_carb = row['carb_energy_per_atom'] * carb_num_atoms
        E_ox_raw = row['ox_energy_per_atom'] * ox_num_atoms
        carb_metals = {}
        for el in carb_comp.elements:
            if el.symbol not in ['C', 'O']:
                carb_metals[el.symbol] = carb_comp[el]
        ox_metals = {}
        for el in ox_comp.elements:
            if el.symbol not in ['C', 'O']:
                ox_metals[el.symbol] = ox_comp[el]
        if not carb_metals or not ox_metals:
            reaction_energies.append(np.nan)
            reaction_energies_per_co2.append(np.nan)
            c_counts.append(0)
            continue
        first_metal = list(carb_metals.keys())[0]
        scale_factor = carb_metals[first_metal] / ox_metals[first_metal]
        E_ox = E_ox_raw * scale_factor
        c_count = carb_comp['C']
        E_CO2 = -11.17 * c_count
        delta_E = E_carb - E_ox - E_CO2
        delta_E_per_co2 = delta_E / c_count if c_count > 0 else np.nan
        reaction_energies.append(delta_E)
        reaction_energies_per_co2.append(delta_E_per_co2)
        c_counts.append(c_count)
    df_filtered['reaction_energy'] = reaction_energies
    df_filtered['reaction_energy_per_CO2'] = reaction_energies_per_co2
    df_filtered['c_count_reduced'] = c_counts
    df_filtered = df_filtered.dropna(subset=['reaction_energy_per_CO2'])
    df_filtered = df_filtered.sort_values('reaction_energy_per_CO2', ascending=True)
    print("\n--- Top 20 Most Favorable Reactions (Lowest ΔE per CO2) ---")
    top_20 = df_filtered.head(20)
    i = 1
    for idx, row in top_20.iterrows():
        print(str(i) + ". " + row['oxide_formula'] + " (" + str(row['oxide_id']) + ") + CO2 -> " + row['carbonate_formula'] + " (" + str(row['carbonate_id']) + ") | ΔE = " + str(round(row['reaction_energy_per_CO2'], 4)) + " eV/CO2")
        i += 1
    print("\n--- Top 20 Least Favorable Reactions (Highest ΔE per CO2) ---")
    bottom_20 = df_filtered.tail(20)[::-1]
    i = 1
    for idx, row in bottom_20.iterrows():
        print(str(i) + ". " + row['oxide_formula'] + " (" + str(row['oxide_id']) + ") + CO2 -> " + row['carbonate_formula'] + " (" + str(row['carbonate_id']) + ") | ΔE = " + str(round(row['reaction_energy_per_CO2'], 4)) + " eV/CO2")
        i += 1
    output_file = os.path.join(data_dir, "reaction_energies.csv")
    df_filtered.to_csv(output_file, index=False)
    print("\nCalculated reaction energies saved to " + output_file)

if __name__ == '__main__':
    calculate_reaction_energy()