# filename: codebase/step_1.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import os

def preprocess_data():
    file_path = "/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet"
    df = pd.read_parquet(file_path)
    total_entries = len(df)
    num_carbonates = int(df['has_C'].sum())
    num_oxides = total_entries - num_carbonates
    unique_formulas_before = df['formula'].nunique()
    print("=== Dataset Statistics Before Polymorph Selection ===")
    print("Total entries: " + str(total_entries))
    print("Number of carbonates (has_C=True): " + str(num_carbonates))
    print("Number of oxides (has_C=False): " + str(num_oxides))
    print("Number of unique formulas: " + str(unique_formulas_before))
    print("\nDistribution of energy_above_hull (eV/atom):")
    print(df['energy_above_hull'].describe().to_string())
    df_sorted = df.sort_values(by='energy_above_hull')
    df_cleaned = df_sorted.drop_duplicates(subset='formula', keep='first').reset_index(drop=True)
    print("\n=== Dataset Statistics After Polymorph Selection ===")
    print("Total entries (unique formulas): " + str(len(df_cleaned)))
    print("Number of carbonates: " + str(int(df_cleaned['has_C'].sum())))
    print("Number of oxides: " + str(len(df_cleaned) - int(df_cleaned['has_C'].sum())))
    output_path = "data/cleaned_materials.parquet"
    df_cleaned.to_parquet(output_path)
    print("\nCleaned dataset saved to " + output_path)

if __name__ == '__main__':
    preprocess_data()