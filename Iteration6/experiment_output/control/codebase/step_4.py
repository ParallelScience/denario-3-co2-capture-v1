# filename: codebase/step_4.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import time
import re

if __name__ == '__main__':
    plt.rcParams['text.usetex'] = False
    data_dir = 'data/'
    data_path = '/home/node/work/projects/co2_capture_v1/co2_capture_materials.parquet'
    df = pd.read_parquet(data_path)
    def parse_formula(formula):
        matches = re.findall(r'([A-Z][a-z]*)(\d*\.?\d*)', formula)
        comp = {}
        for el, num in matches:
            count = float(num) if num else 1.0
            comp[el] = comp.get(el, 0.0) + count
        return comp
    electronegativity = {'H': 2.2, 'Li': 0.98, 'Be': 1.57, 'B': 2.04, 'C': 2.55, 'N': 3.04, 'O': 3.44, 'F': 3.98, 'Na': 0.93, 'Mg': 1.31, 'Al': 1.61, 'Si': 1.9, 'P': 2.19, 'S': 2.58, 'Cl': 3.16, 'K': 0.82, 'Ca': 1.0, 'Sc': 1.36, 'Ti': 1.54, 'V': 1.63, 'Cr': 1.66, 'Mn': 1.55, 'Fe': 1.83, 'Co': 1.88, 'Ni': 1.91, 'Cu': 1.9, 'Zn': 1.65, 'Ga': 1.81, 'Ge': 2.01, 'As': 2.18, 'Se': 2.55, 'Br': 2.96, 'Rb': 0.82, 'Sr': 0.95, 'Y': 1.22, 'Zr': 1.33, 'Nb': 1.6, 'Mo': 2.16, 'Ru': 2.2, 'Rh': 2.28, 'Pd': 2.2, 'Ag': 1.93, 'Cd': 1.69, 'In': 1.78, 'Sn': 1.96, 'Sb': 2.05, 'Te': 2.1, 'I': 2.66, 'Cs': 0.79, 'Ba': 0.89, 'La': 1.1, 'Ce': 1.12, 'Pr': 1.13, 'Nd': 1.14, 'Sm': 1.17, 'Eu': 1.2, 'Gd': 1.2, 'Tb': 1.1, 'Dy': 1.22, 'Ho': 1.23, 'Er': 1.24, 'Tm': 1.25, 'Yb': 1.1, 'Lu': 1.27, 'Hf': 1.3, 'Ta': 1.5, 'W': 2.36, 'Re': 1.9, 'Os': 2.2, 'Ir': 2.2, 'Pt': 2.28, 'Au': 2.54, 'Hg': 2.0, 'Tl': 1.62, 'Pb': 2.33, 'Bi': 2.02}
    atomic_radius = {'H': 0.25, 'Li': 1.45, 'Be': 1.05, 'B': 0.85, 'C': 0.7, 'N': 0.65, 'O': 0.6, 'F': 0.5, 'Na': 1.8, 'Mg': 1.5, 'Al': 1.25, 'Si': 1.1, 'P': 1.0, 'S': 1.0, 'Cl': 1.0, 'K': 2.2, 'Ca': 1.8, 'Sc': 1.6, 'Ti': 1.4, 'V': 1.35, 'Cr': 1.4, 'Mn': 1.4, 'Fe': 1.4, 'Co': 1.35, 'Ni': 1.35, 'Cu': 1.35, 'Zn': 1.35, 'Ga': 1.3, 'Ge': 1.25, 'As': 1.15, 'Se': 1.15, 'Br': 1.15, 'Rb': 2.35, 'Sr': 2.0, 'Y': 1.8, 'Zr': 1.55, 'Nb': 1.45, 'Mo': 1.45, 'Ru': 1.3, 'Rh': 1.35, 'Pd': 1.4, 'Ag': 1.6, 'Cd': 1.55, 'In': 1.55, 'Sn': 1.45, 'Sb': 1.45, 'Te': 1.4, 'I': 1.4, 'Cs': 2.6, 'Ba': 2.15, 'La': 1.95, 'Ce': 1.85, 'Pr': 1.85, 'Nd': 1.85, 'Sm': 1.85, 'Eu': 1.85, 'Gd': 1.8, 'Tb': 1.75, 'Dy': 1.75, 'Ho': 1.75, 'Er': 1.75, 'Tm': 1.75, 'Yb': 1.75, 'Lu': 1.75, 'Hf': 1.55, 'Ta': 1.45, 'W': 1.35, 'Re': 1.35, 'Os': 1.3, 'Ir': 1.35, 'Pt': 1.35, 'Au': 1.35, 'Hg': 1.5, 'Tl': 1.9, 'Pb': 1.8, 'Bi': 1.6}
    def get_features(formula):
        comp = parse_formula(formula)
        total_atoms = sum(comp.values())
        mean_en, mean_ar, valid_en, valid_ar = 0.0, 0.0, 0.0, 0.0
        for el, count in comp.items():
            frac = count / total_atoms
            en, ar = electronegativity.get(el), atomic_radius.get(el)
            if en is not None:
                mean_en += en * frac
                valid_en += frac
            if ar is not None:
                mean_ar += ar * frac
                valid_ar += frac
        return pd.Series({'mean_electronegativity': mean_en / valid_en if valid_en > 0 else np.nan, 'mean_atomic_radius': mean_ar / valid_ar if valid_ar > 0 else np.nan})
    features_df = df['formula'].apply(get_features)
    df_model = pd.concat([df, features_df], axis=1)
    X = df_model[['mean_electronegativity', 'mean_atomic_radius', 'density_g_cm3', 'nsites', 'volume_A3', 'nelements', 'crystal_system']]
    y = df_model['is_stable'].astype(int)
    numeric_features = ['mean_electronegativity', 'mean_atomic_radius', 'density_g_cm3', 'nsites', 'volume_A3', 'nelements']
    categorical_features = ['crystal_system']
    preprocessor = ColumnTransformer(transformers=[('num', SimpleImputer(strategy='median'), numeric_features), ('cat', Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), categorical_features)])
    clf = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1))])
    scoring = ['roc_auc', 'precision', 'recall', 'f1']
    cv_results = cross_validate(clf, X, y, cv=5, scoring=scoring, n_jobs=-1)
    print('\n--- Stability Prediction Model Metrics ---')
    print('Cross-validated ROC-AUC: {:.4f} +/- {:.4f}'.format(np.mean(cv_results['test_roc_auc']), np.std(cv_results['test_roc_auc'])))
    clf.fit(X, y)
    rf = clf.named_steps['classifier']
    cat_encoder = clf.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
    cat_features = cat_encoder.get_feature_names_out(categorical_features)
    all_features = numeric_features + list(cat_features)
    importances = rf.feature_importances_
    indices = np.argsort(importances)[::-1]
    plt.figure(figsize=(12, 6))
    plt.title('Feature Importances for is_stable Prediction')
    plt.bar(range(len(all_features)), importances[indices], align='center', color='teal', edgecolor='black')
    plt.xticks(range(len(all_features)), [all_features[i] for i in indices], rotation=45, ha='right')
    plt.ylabel('Relative Importance')
    plt.tight_layout()
    timestamp = int(time.time())
    plot_filename_1 = os.path.join(data_dir, 'feature_importance_4_' + str(timestamp) + '.png')
    plt.savefig(plot_filename_1, dpi=300)
    filtered_data_path = os.path.join(data_dir, 'filtered_thermo_properties.parquet')
    filtered_pairs = pd.read_parquet(filtered_data_path)
    correction = 11.17 - 3.94
    filtered_pairs['delta_G'] = filtered_pairs['delta_G'] - correction
    filtered_pairs['delta_H'] = filtered_pairs['delta_H'] - correction
    filtered_pairs.to_parquet(filtered_data_path, index=False)
    unique_pairs = filtered_pairs.sort_values('delta_G').drop_duplicates(subset=['formula_ox', 'formula_cb']).copy()
    unique_pairs['delta_G_dist'] = (unique_pairs['delta_G'] - (-0.5)).abs()
    def identify_pareto(df, col_x, col_y, min_x=True, max_y=True):
        sorted_df = df.sort_values(col_x, ascending=min_x)
        pareto_front, best_y = [], -np.inf if max_y else np.inf
        for index, row in sorted_df.iterrows():
            y_val = row[col_y]
            if (max_y and y_val > best_y) or (not max_y and y_val < best_y):
                pareto_front.append(index)
                best_y = y_val
        return df.loc[pareto_front]
    pareto_candidates = identify_pareto(unique_pairs, 'delta_G_dist', 'cohesive_energy_proxy', min_x=True, max_y=True)
    top_10 = pareto_candidates.head(10).copy() if len(pareto_candidates) >= 10 else unique_pairs.sort_values('delta_G_dist').head(10).copy()
    pressures, T, kB, P_ref = np.linspace(0.05, 0.5, 50), 700.0, 8.617333262145e-5, 0.15
    plt.figure(figsize=(10, 6))
    sensitivity_results = []
    for _, row in top_10.iterrows():
        delta_G_P = row['delta_G'] - kB * T * np.log(pressures / P_ref)
        plt.plot(pressures, delta_G_P, label=row['formula_ox'] + ' -> ' + row['formula_cb'], linewidth=2)
        for p, dg in zip(pressures, delta_G_P):
            sensitivity_results.append({'formula_ox': row['formula_ox'], 'formula_cb': row['formula_cb'], 'P_CO2_bar': p, 'delta_G_eV': dg})
    plt.title('Sensitivity Analysis: delta G vs. CO2 Partial Pressure (at 700 K)')
    plt.xlabel('CO2 Partial Pressure (bar)')
    plt.ylabel('delta G (eV/CO2)')
    plt.axvline(x=0.15, color='red', linestyle='--', alpha=0.5, label='Reference P=0.15 bar')
    plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize='small')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot_filename_2 = os.path.join(data_dir, 'sensitivity_analysis_4_' + str(timestamp) + '.png')
    plt.savefig(plot_filename_2, dpi=300, bbox_inches='tight')
    pd.DataFrame(sensitivity_results).to_parquet(os.path.join(data_dir, 'sensitivity_results.parquet'), index=False)
    metrics_df = pd.DataFrame({'Metric': ['ROC-AUC', 'Precision', 'Recall', 'F1 Score'], 'Mean': [np.mean(cv_results['test_roc_auc']), np.mean(cv_results['test_precision']), np.mean(cv_results['test_recall']), np.mean(cv_results['test_f1'])], 'Std': [np.std(cv_results['test_roc_auc']), np.std(cv_results['test_precision']), np.std(cv_results['test_recall']), np.std(cv_results['test_f1'])]})
    metrics_df.to_csv(os.path.join(data_dir, 'stability_model_metrics.csv'), index=False)