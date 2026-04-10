# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import re
import os

def parse_formula(formula):
    matches = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', formula)
    comp = {}
    for elem, count in matches:
        comp[elem] = comp.get(elem, 0) + (float(count) if count else 1.0)
    return comp

def get_metal_composition(comp):
    metals = {k: v for k, v in comp.items() if k not in ['C', 'O']}
    if not metals:
        return None
    total_metals = sum(metals.values())
    return tuple(sorted([(k, round(v / total_metals, 4)) for k, v in metals.items()]))

def get_metal_count(comp):
    return sum(v for k, v in comp.items() if k not in ['C', 'O'])

def get_formula_atoms(comp):
    return sum(comp.values())

def main():
    data_dir = "data/"
    input_path = os.path.join(data_dir, "co2_capture_materials.parquet")
    df = pd.read_parquet(input_path)
    df = df[df['energy_above_hull'] <= 0.1].copy()
    df['comp'] = df['formula'].apply(parse_formula)
    df['formula_atoms'] = df['comp'].apply(get_formula_atoms)
    df['total_formation_energy'] = df['formation_energy_per_atom'] * df['nsites']
    df['energy_per_fu'] = df['formation_energy_per_atom'] * df['formula_atoms']
    carbonates = df[df['has_C'] == True].copy()
    oxides = df[df['has_C'] == False].copy()
    carbonates['metal_comp'] = carbonates['comp'].apply(get_metal_composition)
    oxides['metal_comp'] = oxides['comp'].apply(get_metal_composition)
    carbonates = carbonates[carbonates['metal_comp'].notnull()]
    oxides = oxides[oxides['metal_comp'].notnull()]
    matches = []
    E_CO2 = -11.17
    for _, carb in carbonates.iterrows():
        carb_metal_comp = carb['metal_comp']
        carb_comp = carb['comp']
        carb_metals_count = get_metal_count(carb_comp)
        carb_C_count = carb_comp.get('C', 0)
        carb_O_count = carb_comp.get('O', 0)
        matching_oxides = oxides[oxides['metal_comp'] == carb_metal_comp]
        for _, ox in matching_oxides.iterrows():
            ox_comp = ox['comp']
            ox_metals_count = get_metal_count(ox_comp)
            ox_O_count = ox_comp.get('O', 0)
            k = carb_metals_count / ox_metals_count
            n = carb_C_count
            expected_O = k * ox_O_count + 2 * n
            if abs(expected_O - carb_O_count) < 1e-3:
                delta_E = carb['energy_per_fu'] - k * ox['energy_per_fu'] - n * E_CO2
                primary_metal = max(carb_metal_comp, key=lambda x: x[1])[0]
                matches.append({'carbonate_id': carb['material_id'], 'carbonate_formula': carb['formula'], 'oxide_id': ox['material_id'], 'oxide_formula': ox['formula'], 'primary_metal': primary_metal, 'delta_E': delta_E, 'k_oxide': k, 'n_CO2': n, 'carbonate_energy_per_fu': carb['energy_per_fu'], 'oxide_energy_per_fu': ox['energy_per_fu'], 'carbonate_total_formation_energy': carb['total_formation_energy'], 'oxide_total_formation_energy': ox['total_formation_energy'], 'carbonate_volume': carb['volume_A3'], 'oxide_volume': ox['volume_A3'], 'carbonate_nsites': carb['nsites'], 'oxide_nsites': ox['nsites'], 'carbonate_formula_atoms': carb['formula_atoms'], 'oxide_formula_atoms': ox['formula_atoms'], 'carbonate_band_gap': carb['band_gap'], 'oxide_band_gap': ox['band_gap'], 'carbonate_crystal_system': carb['crystal_system'], 'oxide_crystal_system': ox['crystal_system']})
    matches_df = pd.DataFrame(matches)
    capture_elements = ['Ca', 'Mg', 'Li', 'Na', 'K', 'Ba', 'Sr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Al']
    matches_df = matches_df[matches_df['primary_metal'].isin(capture_elements)]
    summary = matches_df.groupby('primary_metal').agg(num_pairs=('delta_E', 'count'), mean_delta_E=('delta_E', 'mean'), min_delta_E=('delta_E', 'min'), max_delta_E=('delta_E', 'max')).reset_index()
    summary = summary.set_index('primary_metal').reindex(capture_elements).fillna(0).reset_index()
    summary['num_pairs'] = summary['num_pairs'].astype(int)
    print("=== Oxide-Carbonate Pairing Summary ===")
    print("Reaction: k * Oxide + n * CO2 -> Carbonate")
    print("Delta E (eV/formula unit of Carbonate)")
    print("-" * 60)
    print(summary.to_string(index=False))
    output_path = os.path.join(data_dir, "matched_pairs.parquet")
    matches_df.to_parquet(output_path)
    print("\nMatched pairs saved to " + output_path)

if __name__ == '__main__':
    main()