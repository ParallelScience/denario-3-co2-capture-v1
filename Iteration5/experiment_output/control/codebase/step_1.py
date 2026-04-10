# filename: codebase/step_1.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import re
import os

def parse_formula(formula):
    parsed = {}
    matches = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', formula)
    for element, count in matches:
        if count == '':
            count = 1.0
        else:
            count = float(count)
        parsed[element] = parsed.get(element, 0) + count
    return parsed

def get_base_composition_key(formula):
    parsed = parse_formula(formula)
    metals = {k: v for k, v in parsed.items() if k not in ['C', 'O']}
    total_metals = sum(metals.values())
    if total_metals == 0:
        return None
    norm = {k: v / total_metals for k, v in parsed.items()}
    base_O = norm.get('O', 0.0) - 2.0 * norm.get('C', 0.0)
    base_comp = {}
    for k, v in norm.items():
        if k not in ['C', 'O']:
            if abs(v) > 1e-4:
                base_comp[k] = v
    if abs(base_O) > 1e-4:
        base_comp['O'] = base_O
    key_parts = []
    for k in sorted(base_comp.keys()):
        val_rounded = round(base_comp[k], 4)
        key_parts.append(k + str(val_rounded))
    return "".join(key_parts)

def get_formula_atoms(formula):
    return sum(parse_formula(formula).values())

def get_metal_system(formula):
    parsed = parse_formula(formula)
    metals = [k for k in parsed.keys() if k not in ['C', 'O']]
    return "-".join(sorted(metals))

def get_metal_count(formula):
    parsed = parse_formula(formula)
    return sum(v for k, v in parsed.items() if k not in ['C', 'O'])

if __name__ == '__main__':
    data_path = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    df = pd.read_parquet(data_path)
    df_filtered = df[df['energy_above_hull'] <= 0.1].copy()
    df_filtered['base_key'] = df_filtered['formula'].apply(get_base_composition_key)
    df_filtered['formula_atoms'] = df_filtered['formula'].apply(get_formula_atoms)
    df_filtered['metal_system'] = df_filtered['formula'].apply(get_metal_system)
    df_filtered['metal_count'] = df_filtered['formula'].apply(get_metal_count)
    df_filtered['c_count'] = df_filtered['formula'].apply(lambda x: parse_formula(x).get('C', 0.0))
    df_filtered = df_filtered.dropna(subset=['base_key'])
    df_carb = df_filtered[df_filtered['has_C'] == True]
    df_ox = df_filtered[df_filtered['has_C'] == False]
    common_keys = set(df_carb['base_key']).intersection(set(df_ox['base_key']))
    pairs = []
    for key in common_keys:
        ox_group = df_ox[df_ox['base_key'] == key]
        carb_group = df_carb[df_carb['base_key'] == key]
        for _, ox_row in ox_group.iterrows():
            for _, carb_row in carb_group.iterrows():
                ox_metals = ox_row['metal_count']
                carb_metals = carb_row['metal_count']
                c_ox = carb_metals / ox_metals
                n_CO2 = carb_row['c_count']
                pair = {'base_key': key, 'metal_system': carb_row['metal_system'], 'oxide_id': ox_row['material_id'], 'carbonate_id': carb_row['material_id'], 'oxide_formula': ox_row['formula'], 'carbonate_formula': carb_row['formula'], 'c_ox': c_ox, 'n_CO2': n_CO2, 'oxide_formula_atoms': ox_row['formula_atoms'], 'carbonate_formula_atoms': carb_row['formula_atoms'], 'oxide_energy_per_atom': ox_row['formation_energy_per_atom'], 'carbonate_energy_per_atom': carb_row['formation_energy_per_atom'], 'oxide_nsites': ox_row['nsites'], 'carbonate_nsites': carb_row['nsites'], 'oxide_volume': ox_row['volume_A3'], 'carbonate_volume': carb_row['volume_A3'], 'oxide_density': ox_row['density_g_cm3'], 'carbonate_density': carb_row['density_g_cm3'], 'oxide_band_gap': ox_row['band_gap'], 'carbonate_band_gap': carb_row['band_gap'], 'oxide_energy_above_hull': ox_row['energy_above_hull'], 'carbonate_energy_above_hull': carb_row['energy_above_hull'], 'oxide_is_stable': ox_row['is_stable'], 'carbonate_is_stable': carb_row['is_stable'], 'oxide_crystal_system': ox_row['crystal_system'], 'carbonate_crystal_system': carb_row['crystal_system'], 'oxide_space_group': ox_row['space_group'], 'carbonate_space_group': carb_row['space_group'], 'oxide_elements': ox_row['elements'], 'carbonate_elements': carb_row['elements']}
                pairs.append(pair)
    pairs_df = pd.DataFrame(pairs)
    print("=== Summary Statistics ===")
    print("Total materials after stability filter (<= 0.1 eV/atom): " + str(len(df_filtered)))
    print("Total oxides: " + str(len(df_ox)))
    print("Total carbonates: " + str(len(df_carb)))
    print("Total matched oxide-carbonate pairs found: " + str(len(pairs_df)))
    print("Number of unique metal systems in pairs: " + str(pairs_df['metal_system'].nunique()))
    print("\nPolymorph counts per composition (Top 10):")
    formula_counts = df_filtered['formula'].value_counts()
    print(formula_counts.head(10).to_string())
    print("\nAverage polymorphs per composition: " + str(round(formula_counts.mean(), 2)))
    output_path = 'data/matched_pairs.csv'
    pairs_df.to_csv(output_path, index=False)
    print("\nMatched pairs saved to " + output_path)