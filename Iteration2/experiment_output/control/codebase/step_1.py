# filename: codebase/step_1.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import re
import os

def parse_composition(formula):
    matches = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', formula)
    comp = {}
    for elem, count in matches:
        comp[elem] = float(count) if count else 1.0
    return comp

def get_unit_cell_composition(formula, nsites):
    comp = parse_composition(formula)
    total_atoms = sum(comp.values())
    multiplier = nsites / total_atoms
    return {k: v * multiplier for k, v in comp.items()}

def get_metal_signature(uc_comp):
    metals = {k: v for k, v in uc_comp.items() if k not in ['C', 'O']}
    if not metals:
        return None
    total_metals = sum(metals.values())
    return tuple(sorted((k, round(v / total_metals, 4)) for k, v in metals.items()))

def get_total_metal_atoms(uc_comp):
    return sum(v for k, v in uc_comp.items() if k not in ['C', 'O'])

if __name__ == '__main__':
    input_path = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    output_file = 'data/matched_reaction_pairs.csv'
    print('Loading dataset from ' + input_path + ' ...')
    df = pd.read_parquet(input_path)
    print('Applying stability filter (energy_above_hull <= 0.1 eV/atom)...')
    df_stable = df[df['energy_above_hull'] <= 0.1].copy()
    print('Number of stable materials: ' + str(len(df_stable)) + ' out of ' + str(len(df)))
    df_stable['E_uc'] = df_stable['formation_energy_per_atom'] * df_stable['nsites']
    print('Parsing chemical formulas and computing unit cell compositions...')
    df_stable['uc_comp'] = df_stable.apply(lambda row: get_unit_cell_composition(row['formula'], row['nsites']), axis=1)
    df_stable['metal_sig'] = df_stable['uc_comp'].apply(get_metal_signature)
    df_stable['N_metal'] = df_stable['uc_comp'].apply(get_total_metal_atoms)
    df_stable['N_carbon'] = df_stable['uc_comp'].apply(lambda c: c.get('C', 0.0))
    oxides = df_stable[(~df_stable['has_C']) & (df_stable['metal_sig'].notnull())]
    carbonates = df_stable[(df_stable['has_C']) & (df_stable['metal_sig'].notnull()) & (df_stable['N_carbon'] > 0)]
    print('Number of stable oxides: ' + str(len(oxides)))
    print('Number of stable carbonates: ' + str(len(carbonates)))
    print('Matching oxide precursors with carbonate products based on metal identity...')
    E_CO2 = -11.17
    matches = []
    oxides_grouped = oxides.groupby('metal_sig')
    carbonates_grouped = carbonates.groupby('metal_sig')
    common_sigs = set(oxides_grouped.groups.keys()).intersection(set(carbonates_grouped.groups.keys()))
    for sig in common_sigs:
        ox_group = oxides_grouped.get_group(sig)
        carb_group = carbonates_grouped.get_group(sig)
        for _, carb in carb_group.iterrows():
            N_C = carb['N_carbon']
            c_carb = 1.0 / N_C
            carb_E_uc = carb['E_uc']
            carb_N_metal = carb['N_metal']
            carb_O = carb['uc_comp'].get('O', 0.0)
            for _, ox in ox_group.iterrows():
                c_ox = (carb_N_metal / N_C) / ox['N_metal']
                ox_E_uc = ox['E_uc']
                ox_O = ox['uc_comp'].get('O', 0.0)
                delta_E = c_carb * carb_E_uc - c_ox * ox_E_uc - E_CO2
                delta_O = c_carb * carb_O - (c_ox * ox_O + 2.0)
                matches.append({'carbonate_id': carb['material_id'], 'oxide_id': ox['material_id'], 'carbonate_formula': carb['formula'], 'oxide_formula': ox['formula'], 'metal_signature': sig, 'delta_E': delta_E, 'c_carb': c_carb, 'c_ox': c_ox, 'delta_O': delta_O, 'carbonate_E_uc': carb_E_uc, 'oxide_E_uc': ox_E_uc, 'carbonate_nsites': carb['nsites'], 'oxide_nsites': ox['nsites'], 'carbonate_volume': carb['volume_A3'], 'oxide_volume': ox['volume_A3'], 'carbonate_density': carb['density_g_cm3'], 'oxide_density': ox['density_g_cm3'], 'carbonate_crystal_system': carb['crystal_system'], 'oxide_crystal_system': ox['crystal_system'], 'carbonate_band_gap': carb['band_gap'], 'oxide_band_gap': ox['band_gap'], 'carbonate_formation_energy_per_atom': carb['formation_energy_per_atom'], 'oxide_formation_energy_per_atom': ox['formation_energy_per_atom'], 'carbonate_nelements': carb['nelements'], 'oxide_nelements': ox['nelements'], 'carbonate_elements': carb['elements'], 'oxide_elements': ox['elements']})
    matches_df = pd.DataFrame(matches)
    print('Total valid reaction pairs found: ' + str(len(matches_df)))
    target_elements = ['Ca', 'Mg', 'Li', 'Na', 'K', 'Ba', 'Sr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Al']
    pair_counts = {elem: 0 for elem in target_elements}
    for sig in matches_df['metal_signature']:
        for elem, _ in sig:
            if elem in pair_counts:
                pair_counts[elem] += 1
    print('\nSummary of oxide-carbonate pairs found per metal element:')
    print('-' * 50)
    print('Element    | Number of Pairs')
    print('-' * 50)
    for elem in target_elements:
        print(elem + ' ' * (10 - len(elem)) + ' | ' + str(pair_counts[elem]))
    print('-' * 50)
    matches_df['metal_signature'] = matches_df['metal_signature'].apply(lambda x: '_'.join([str(k) + str(v) for k, v in x]))
    matches_df.to_csv(output_file, index=False)
    print('\nMatched dataset saved to ' + output_file)