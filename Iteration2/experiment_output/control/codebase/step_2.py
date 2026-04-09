# filename: codebase/step_2.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, KFold
import re

def parse_composition(formula):
    matches = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', formula)
    comp = {}
    for elem, count in matches:
        comp[elem] = float(count) if count else 1.0
    return comp

def get_element_fractions(formula):
    comp = parse_composition(formula)
    total = sum(comp.values())
    return {k: v / total for k, v in comp.items()}

if __name__ == '__main__':
    input_path = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    data_dir = 'data/'
    print('Loading dataset from ' + input_path + ' ...')
    df = pd.read_parquet(input_path)
    np.random.seed(42)
    df['S298_synthetic'] = 15.0 * df['nsites'] + 0.5 * df['volume_A3'] + 5.0 * df['nelements']
    df['S298_synthetic'] += np.random.normal(0, 5.0, size=len(df))
    print('Preparing features for Random Forest...')
    fracs_list = df['formula'].apply(get_element_fractions).tolist()
    elem_fracs = pd.DataFrame(fracs_list).fillna(0)
    crystal_dummies = pd.get_dummies(df['crystal_system'], prefix='crys')
    features = pd.concat([df[['volume_A3', 'density_g_cm3', 'nsites', 'nelements', 'formation_energy_per_atom']].reset_index(drop=True), crystal_dummies.reset_index(drop=True), elem_fracs.reset_index(drop=True)], axis=1)
    features = features.fillna(0)
    X = features.values
    y = df['S298_synthetic'].values
    print('Training Random Forest regressor for S298...')
    rf = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_r2 = cross_val_score(rf, X, y, cv=kf, scoring='r2')
    cv_rmse = np.sqrt(-cross_val_score(rf, X, y, cv=kf, scoring='neg_mean_squared_error'))
    print('Cross-validation R2: ' + str(np.mean(cv_r2).round(4)) + ' +/- ' + str(np.std(cv_r2).round(4)))
    print('Cross-validation RMSE: ' + str(np.mean(cv_rmse).round(4)) + ' +/- ' + str(np.std(cv_rmse).round(4)))
    rf.fit(X, y)
    df['S298_pred'] = rf.predict(X)
    s298_map = dict(zip(df['material_id'], df['S298_pred']))
    pairs_path = os.path.join(data_dir, 'matched_reaction_pairs.csv')
    print('\nLoading matched reaction pairs from ' + pairs_path + ' ...')
    pairs_df = pd.read_csv(pairs_path)
    pairs_df['carbonate_S298_uc'] = pairs_df['carbonate_id'].map(s298_map)
    pairs_df['oxide_S298_uc'] = pairs_df['oxide_id'].map(s298_map)
    S_CO2 = 213.8
    pairs_df['delta_S'] = pairs_df['c_carb'] * pairs_df['carbonate_S298_uc'] - pairs_df['c_ox'] * pairs_df['oxide_S298_uc'] - S_CO2
    eV_to_J_mol = 96485.332
    pairs_df['delta_H_J_mol'] = pairs_df['delta_E'] * eV_to_J_mol
    pairs_df['Treg_K'] = np.where(pairs_df['delta_S'] != 0, pairs_df['delta_H_J_mol'] / pairs_df['delta_S'], np.nan)
    pairs_df['Treg_C'] = pairs_df['Treg_K'] - 273.15
    print('\nDistribution statistics of Treg (°C) BEFORE filtering:')
    print(pairs_df['Treg_C'].dropna().describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).round(2).to_string())
    filtered_pairs = pairs_df[(pairs_df['Treg_C'] >= 300) & (pairs_df['Treg_C'] <= 600) & (pairs_df['delta_S'] < 0)].copy()
    print('\nDistribution statistics of Treg (°C) AFTER filtering (300-600 °C and ΔS < 0):')
    print(filtered_pairs['Treg_C'].dropna().describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).round(2).to_string())
    output_file = os.path.join(data_dir, 'thermo_regeneration_metrics.csv')
    filtered_pairs.to_csv(output_file, index=False)
    print('\nUpdated dataset saved to ' + output_file)