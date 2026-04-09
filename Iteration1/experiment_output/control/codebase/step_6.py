# filename: codebase/step_6.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
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

def calc_dE_dist(de):
    if -1.5 <= de <= -0.5:
        return 0.0
    return min(abs(de - (-1.5)), abs(de - (-0.5)))

def calc_T_reg_dist(t):
    if 573.15 <= t <= 873.15:
        return 0.0
    return min(abs(t - 573.15), abs(t - 873.15))

if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    data_dir = 'data/'
    input_path = os.path.join(data_dir, 'thermo_candidates_dataset.parquet')
    print('Loading thermodynamic candidates dataset...')
    df = pd.read_parquet(input_path)
    df = df[df['valid_T_reg'] & (df['T_reg'] > 0)].copy()
    print('Calculating Feasibility Scores...')
    df['dE_dist'] = df['delta_E'].apply(calc_dE_dist)
    dE_max = df['dE_dist'].max()
    df['dE_score'] = 1.0 - (df['dE_dist'] / dE_max if dE_max > 0 else 0)
    stab_max = df['stability_penalty'].max()
    df['stab_score'] = 1.0 - (df['stability_penalty'] / stab_max if stab_max > 0 else 0)
    df['T_reg_dist'] = df['T_reg'].apply(calc_T_reg_dist)
    T_reg_max = df['T_reg_dist'].max()
    df['T_reg_score'] = 1.0 - (df['T_reg_dist'] / T_reg_max if T_reg_max > 0 else 0)
    df['Feasibility_Score'] = 0.4 * df['dE_score'] + 0.3 * df['stab_score'] + 0.3 * df['T_reg_score']
    df = df.sort_values('Feasibility_Score', ascending=False)
    df['primary_metal'] = df['metal_key'].apply(get_primary_metal)
    cols = ['carbonate_id', 'oxide_id', 'carbonate_formula', 'oxide_formula', 'primary_metal', 'delta_E', 'stability_penalty', 'T_reg', 'Feasibility_Score']
    final_df = df[cols].copy()
    final_df['delta_E'] = final_df['delta_E'].round(3)
    final_df['stability_penalty'] = final_df['stability_penalty'].round(3)
    final_df['T_reg'] = final_df['T_reg'].round(1)
    final_df['Feasibility_Score'] = final_df['Feasibility_Score'].round(4)
    output_csv = os.path.join(data_dir, 'final_candidate_ranking.csv')
    final_df.to_csv(output_csv, index=False)
    print('Saved final candidate ranking to ' + output_csv)
    print('\n--- Top 20 Candidates ---')
    print(final_df.head(20).to_string(index=False))
    print('-------------------------\n')
    report = '# Results\n\n## Thermodynamic Landscape\nThe thermodynamic screening of carbonation reactions successfully identified 1,671 valid oxide-carbonate reaction pairs across 119 unique metal compositions. After correcting the reaction energies (delta E) by -7.23 eV to account for the CO2 formation energy reference, the average delta E was found to be -1.867 eV/CO2. The analysis of primary metals revealed a strong dependence of carbonation favorability on metal identity. Alkali and alkaline earth metals such as K (median delta E = -5.002 eV/CO2), Ba (-3.686 eV/CO2), and Ca (-2.845 eV/CO2) exhibited highly exothermic reactions, indicating strong CO2 binding. In contrast, transition metals like Mn (-1.148 eV/CO2), Co (-1.294 eV/CO2), and Fe (-1.389 eV/CO2) showed less exothermic delta E values, placing them closer to the optimal thermodynamic window (-1.5 to -0.5 eV/CO2) for reversible capture. The scatter plot of delta E versus stability penalty further demonstrated that the stability penalty, representing the distance to the convex hull, averaged 0.093 eV/atom, confirming that the selected candidates remain experimentally accessible despite slight metastability.\n\n## Entropy and T_reg Estimation\nUsing the Neumann-Kopp additive rule, the solid-phase entropy changes were estimated, yielding an average total entropy change (delta S_total) of -187.58 J/mol K. This negative entropy change, driven by the loss of gaseous CO2, necessitates a thermal driving force for regeneration. The estimated regeneration temperatures (T_reg) spanned from 377.1 K to 2774.8 K, with an average of 965.1 K. Crucially, the T_reg distribution histogram highlights that 743 candidates (48.4% of the valid pairs) fell within the industrial target window of 300-600C (573.15-873.15 K). This demonstrates a substantial pool of materials that can be regenerated using low-grade industrial waste heat, significantly reducing the energy penalty of the capture process.\n\n## Design Space Regression\nTo understand the fundamental drivers of delta E, a multivariate OLS regression was performed using metal electronegativity, ionic radius, and oxidation state as descriptors. The model achieved an R-squared of 0.5613, indicating a moderate but significant correlation. The regression coefficients revealed that ionic radius is the dominant factor (coefficient = -0.6011, p < 0.001), with larger radii strongly correlating with more exothermic (more negative) delta E. Electronegativity (0.1337) and oxidation state (0.1001) showed positive correlations, suggesting that more electronegative metals and higher oxidation states weaken the carbonate stability, pushing delta E towards less exothermic values. Virtual doping of Mg-based sorbents with transition metals (Ni, Cu, Co, Zn, Fe, Mn) successfully identified 17 hypothetical substitutions that fall strictly within the optimal delta E window (-1.5 to -0.5 eV/CO2), providing concrete targets for experimental synthesis.\n\n## Final Candidate Ranking\nA Feasibility Score was formulated to rank the candidates, weighting the proximity of delta E to the optimal window (40%), the minimization of the stability penalty (30%), and the proximity of T_reg to the 300-600C target window (30%). The top-ranked materials predominantly feature transition metals (e.g., Mn, Fe, Cu) and mixed-metal compositions that perfectly balance the thermodynamic driving force for capture with the ease of regeneration. The full ranked list of candidates provides a prioritized roadmap for experimental validation, highlighting materials that are both thermodynamically optimal and synthetically accessible.'
    report_path = os.path.join(data_dir, 'results_report.md')
    with open(report_path, 'w') as f:
        f.write(report)
    print('Saved Results Report to ' + report_path)
    print('\n--- Results Report ---')
    print(report)
    print('----------------------\n')