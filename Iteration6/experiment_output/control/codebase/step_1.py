# filename: codebase/step_1.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import time
import os

def parse_formula(formula):
    matches = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', formula)
    comp = {}
    for el, num in matches:
        count = float(num) if num else 1.0
        comp[el] = comp.get(el, 0.0) + count
    return comp

def get_base_composition_key(formula):
    comp = parse_formula(formula)
    if 'C' in comp:
        c_count = comp['C']
        comp['O'] = comp.get('O', 0.0) - 2.0 * c_count
        comp['C'] = 0.0
    if comp.get('O', 0.0) < -1e-4:
        return None
    comp = {el: c for el, c in comp.items() if c > 1e-4}
    metals = {el: c for el, c in comp.items() if el not in ['O', 'C']}
    total_metals = sum(metals.values())
    if total_metals < 1e-4:
        return None
    norm_comp = {el: round(c / total_metals, 5) for el, c in comp.items()}
    key = tuple(sorted(norm_comp.items()))
    return key

def get_composition_features(formula):
    comp = parse_formula(formula)
    total_atoms = sum(comp.values())
    c_count = comp.get('C', 0.0)
    metals = {el: c for el, c in comp.items() if el not in ['O', 'C']}
    total_metals = sum(metals.values())
    return pd.Series({'parsed_total_atoms': total_atoms, 'parsed_c_count': c_count, 'parsed_total_metals': total_metals})

if __name__ == '__main__':
    plt.rcParams['text.usetex'] = False
    data_path = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    df = pd.read_parquet(data_path)
    df_filtered = df[df['energy_above_hull'] <= 0.1].copy()
    df_filtered['base_key'] = df_filtered['formula'].apply(get_base_composition_key)
    df_filtered = df_filtered.dropna(subset=['base_key']).copy()
    features = df_filtered['formula'].apply(get_composition_features)
    df_filtered = pd.concat([df_filtered, features], axis=1)
    oxides = df_filtered[~df_filtered['has_C']].copy()
    carbonates = df_filtered[df_filtered['has_C']].copy()
    pairs = pd.merge(oxides, carbonates, on='base_key', suffixes=('_ox', '_cb'))
    pair_counts = pairs.groupby('base_key').size().reset_index(name='polymorph_pair_count')
    pairs = pairs.merge(pair_counts, on='base_key')
    capture_elements_list = ['Ca', 'Mg', 'Li', 'Na', 'K', 'Ba', 'Sr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Al']
    def extract_capture_elements(base_key):
        return [el for el, frac in base_key if el in capture_elements_list]
    pairs['capture_elements'] = pairs['base_key'].apply(extract_capture_elements)
    pairs = pairs[pairs['capture_elements'].apply(len) > 0].copy()
    pairs_exploded = pairs.explode('capture_elements')
    pairs_per_element = pairs_exploded['capture_elements'].value_counts()
    plt.figure(figsize=(10, 6))
    pairs_per_element.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Number of Matched Oxide-Carbonate Pairs per Capture Element')
    plt.xlabel('Capture Element')
    plt.ylabel('Number of Matched Pairs')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename = os.path.join('data', 'matched_pairs_per_element_1_' + str(timestamp) + '.png')
    plt.savefig(plot_filename, dpi=300)
    pairs['base_key_str'] = pairs['base_key'].apply(str)
    pairs_to_save = pairs.drop(columns=['base_key'])
    output_file = os.path.join('data', 'matched_pairs.parquet')
    pairs_to_save.to_parquet(output_file, index=False)