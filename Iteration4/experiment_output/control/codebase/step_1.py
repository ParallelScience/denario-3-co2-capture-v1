# filename: codebase/step_1.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import os
from pymatgen.core import Composition

def parse_formula_fast(formula):
    """
    Parses a chemical formula to extract its metal signature, metal elements, 
    and atom counts for metals, carbon, and oxygen.
    
    Args:
        formula (str): The chemical formula to parse.
        
    Returns:
        dict or None: A dictionary containing the parsed properties, or None if parsing fails 
                      or no metal elements are found.
    """
    try:
        comp = Composition(formula).reduced_composition
        metal_dict = {}
        c_count = 0
        o_count = 0
        
        for el in comp.elements:
            if el.symbol == 'C':
                c_count = comp[el]
            elif el.symbol == 'O':
                o_count = comp[el]
            else:
                metal_dict[el.symbol] = comp[el]
                
        if not metal_dict:
            return None
            
        metal_comp = Composition(metal_dict)
        metal_signature = metal_comp.reduced_formula
        metal_count = metal_comp.num_atoms
        
        metal_elements = ",".join(sorted([el.symbol for el in metal_comp.elements]))
        
        return {
            'metal_signature': metal_signature,
            'metal_elements': metal_elements,
            'metal_count': metal_count,
            'c_count': c_count,
            'o_count': o_count
        }
    except Exception:
        return None

if __name__ == '__main__':
    data_dir = "data/"
    file_path = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    print("Loading dataset from " + file_path + "...")
    df = pd.read_parquet(file_path)
    df = df.dropna(subset=['formula'])
    df_stable = df.sort_values('energy_above_hull').drop_duplicates(subset=['formula'], keep='first').copy()
    print("Parsing formulas to extract metal signatures...")
    parsed_list = []
    for formula in df_stable['formula']:
        parsed_list.append(parse_formula_fast(formula))
    df_parsed = pd.DataFrame(parsed_list, index=df_stable.index)
    df_stable = pd.concat([df_stable, df_parsed], axis=1)
    df_stable = df_stable.dropna(subset=['metal_signature'])
    oxides = df_stable[df_stable['c_count'] == 0]
    carbonates = df_stable[df_stable['c_count'] > 0]
    print("Identifying oxide-carbonate reaction pairs...")
    pairs = []
    for _, carb in carbonates.iterrows():
        matching_oxides = oxides[oxides['metal_signature'] == carb['metal_signature']]
        for _, ox in matching_oxides.iterrows():
            pairs.append({
                'carbonate_id': carb['material_id'],
                'carbonate_formula': carb['formula'],
                'oxide_id': ox['material_id'],
                'oxide_formula': ox['formula'],
                'metal_signature': carb['metal_signature'],
                'metal_elements': carb['metal_elements'],
                'carb_metal_count': carb['metal_count'],
                'ox_metal_count': ox['metal_count'],
                'c_count': carb['c_count'],
                'carb_energy_per_atom': carb['formation_energy_per_atom'],
                'ox_energy_per_atom': ox['formation_energy_per_atom'],
                'carb_nsites': carb['nsites'],
                'ox_nsites': ox['nsites'],
                'carb_energy_above_hull': carb['energy_above_hull'],
                'ox_energy_above_hull': ox['energy_above_hull']
            })
    df_pairs = pd.DataFrame(pairs)
    target_metals = ['Ca', 'Mg', 'Li', 'Na', 'K', 'Ba', 'Sr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Al']
    print("\n--- Summary Statistics ---")
    print("Total initial entries: " + str(len(df)))
    print("Unique formulas (chemical systems) retained: " + str(len(df_stable)))
    print("Total oxide entries (c_count == 0): " + str(len(oxides)))
    print("Total carbonate entries (c_count > 0): " + str(len(carbonates)))
    print("Total valid oxide-carbonate pairs found: " + str(len(df_pairs)))
    print("\nValid pairs found per metal family:")
    for metal in target_metals:
        count = sum(1 for elements in df_pairs['metal_elements'] if metal in elements.split(','))
        print("  " + metal + ": " + str(count))
    output_file = os.path.join(data_dir, "processed_pairs.csv")
    df_pairs.to_csv(output_file, index=False)
    print("\nProcessed pairs saved to " + output_file)