# filename: codebase/step_5.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import time
import re

def get_primary_metal(metal_key):
    parts = metal_key.split('_')
    max_frac = -1
    primary = 'Unknown'
    for part in parts:
        match = re.match(r'([A-Z][a-z]*)(\d*\.?\d*)', part)
        if match:
            el = match.group(1)
            frac_str = match.group(2)
            frac = float(frac_str) if frac_str else 1.0
            if frac > max_frac:
                max_frac = frac
                primary = el
    return primary

if __name__ == '__main__':
    plt.rcParams['text.usetex'] = False
    data_dir = 'data/'
    input_path = os.path.join(data_dir, 'thermo_candidates_dataset.parquet')
    print('Loading thermodynamic candidates dataset...')
    df = pd.read_parquet(input_path)
    df['primary_metal'] = df['metal_key'].apply(get_primary_metal)
    target_metals = ['Ca', 'Mg', 'Li', 'Na', 'K', 'Ba', 'Sr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Al']
    df = df[df['primary_metal'].isin(target_metals)].copy()
    metal_props = {'Li': {'en': 0.98, 'radius': 0.76, 'ox': 1}, 'Na': {'en': 0.93, 'radius': 1.02, 'ox': 1}, 'K': {'en': 0.82, 'radius': 1.38, 'ox': 1}, 'Mg': {'en': 1.31, 'radius': 0.72, 'ox': 2}, 'Ca': {'en': 1.00, 'radius': 1.00, 'ox': 2}, 'Sr': {'en': 0.95, 'radius': 1.18, 'ox': 2}, 'Ba': {'en': 0.89, 'radius': 1.35, 'ox': 2}, 'Mn': {'en': 1.55, 'radius': 0.83, 'ox': 2}, 'Fe': {'en': 1.83, 'radius': 0.78, 'ox': 2}, 'Co': {'en': 1.88, 'radius': 0.745, 'ox': 2}, 'Ni': {'en': 1.91, 'radius': 0.69, 'ox': 2}, 'Cu': {'en': 1.90, 'radius': 0.73, 'ox': 2}, 'Zn': {'en': 1.65, 'radius': 0.74, 'ox': 2}, 'Al': {'en': 1.61, 'radius': 0.535, 'ox': 3}}
    df['en'] = df['primary_metal'].map(lambda x: metal_props[x]['en'])
    df['radius'] = df['primary_metal'].map(lambda x: metal_props[x]['radius'])
    df['ox'] = df['primary_metal'].map(lambda x: metal_props[x]['ox'])
    X = df[['en', 'radius', 'ox']]
    y = df['delta_E']
    X_mean = X.mean()
    X_std = X.std()
    X_scaled = (X - X_mean) / X_std
    X_scaled_sm = sm.add_constant(X_scaled)
    model = sm.OLS(y, X_scaled_sm).fit()
    print('\n--- Multivariate Regression Results ---')
    print('R-squared: ' + str(round(model.rsquared, 4)))
    print('Adjusted R-squared: ' + str(round(model.rsquared_adj, 4)))
    print('\nCoefficients and Standard Errors:')
    coef_df = pd.DataFrame({'Coefficient': model.params, 'Std_Error': model.bse, 't_value': model.tvalues, 'P>|t|': model.pvalues})
    print(coef_df.to_string())
    regression_results_path = os.path.join(data_dir, 'regression_results.csv')
    coef_df.to_csv(regression_results_path)
    print('\nSaved regression results to ' + regression_results_path)
    df['predicted_delta_E'] = model.predict(X_scaled_sm)
    plt.figure(figsize=(8, 8))
    plt.scatter(df['delta_E'], df['predicted_delta_E'], alpha=0.6, edgecolor='k', color='dodgerblue')
    min_val = min(df['delta_E'].min(), df['predicted_delta_E'].min())
    max_val = max(df['delta_E'].max(), df['predicted_delta_E'].max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Parity Line')
    plt.xlabel('Actual delta E (eV/CO2)')
    plt.ylabel('Predicted delta E (eV/CO2)')
    plt.title('Parity Plot: Predicted vs Actual delta E')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename = 'parity_plot_delta_E_' + str(timestamp) + '.png'
    plot_filepath = os.path.join(data_dir, plot_filename)
    plt.savefig(plot_filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print('Parity plot saved to ' + plot_filepath)
    print('\n--- Virtual Doping and Substitution Screening ---')
    hosts = ['Ca', 'Mg']
    doping_fractions = [0.25, 0.50, 0.75]
    optimal_min, optimal_max = -1.5, -0.5
    substitutions = []
    for host in hosts:
        host_props = metal_props[host]
        host_en_scaled = (host_props['en'] - X_mean['en']) / X_std['en']
        host_rad_scaled = (host_props['radius'] - X_mean['radius']) / X_std['radius']
        host_ox_scaled = (host_props['ox'] - X_mean['ox']) / X_std['ox']
        pure_pred = model.params['const'] + model.params['en']*host_en_scaled + model.params['radius']*host_rad_scaled + model.params['ox']*host_ox_scaled
        for dopant, d_props in metal_props.items():
            if dopant == host:
                continue
            if d_props['ox'] != host_props['ox']:
                continue
            radius_diff = abs(d_props['radius'] - host_props['radius']) / host_props['radius']
            if radius_diff > 0.20:
                continue
            for x in doping_fractions:
                mix_en = (1 - x) * host_props['en'] + x * d_props['en']
                mix_rad = (1 - x) * host_props['radius'] + x * d_props['radius']
                mix_ox = host_props['ox']
                mix_en_scaled = (mix_en - X_mean['en']) / X_std['en']
                mix_rad_scaled = (mix_rad - X_mean['radius']) / X_std['radius']
                mix_ox_scaled = (mix_ox - X_mean['ox']) / X_std['ox']
                pred_delta_E = model.params['const'] + model.params['en']*mix_en_scaled + model.params['radius']*mix_rad_scaled + model.params['ox']*mix_ox_scaled
                formula = host + str(1-x) + dopant + str(x)
                substitutions.append({'Host': host, 'Dopant': dopant, 'Dopant_Fraction': x, 'Formula_Prefix': formula, 'Radius_Mismatch': round(radius_diff, 3), 'Pure_Host_Pred_dE': round(pure_pred, 3), 'Doped_Pred_dE': round(pred_delta_E, 3), 'In_Optimal_Window': optimal_min <= pred_delta_E <= optimal_max})
    subs_df = pd.DataFrame(substitutions)
    if len(subs_df) > 0:
        subs_df = subs_df.sort_values('Doped_Pred_dE', ascending=False)
        subs_filepath = os.path.join(data_dir, 'virtual_substitutions.csv')
        subs_df.to_csv(subs_filepath, index=False)
        print('Saved virtual substitutions to ' + subs_filepath)
        print('\nTop 15 Virtual Substitutions (Ranked by Predicted delta E):')
        print(subs_df.head(15).to_string(index=False))
        optimal_subs = subs_df[subs_df['In_Optimal_Window']]
        print('\nSubstitutions falling in the optimal window (-1.5 to -0.5 eV): ' + str(len(optimal_subs)))
        if len(optimal_subs) > 0:
            print(optimal_subs.to_string(index=False))
        else:
            print('No substitutions fell strictly within the optimal window. Showing closest candidates:')
            subs_df['Dist_to_Opt'] = abs(subs_df['Doped_Pred_dE'] - (-1.0))
            closest = subs_df.sort_values('Dist_to_Opt').head(10)
            print(closest.drop(columns=['Dist_to_Opt']).to_string(index=False))
    else:
        print('No valid substitutions found based on constraints.')