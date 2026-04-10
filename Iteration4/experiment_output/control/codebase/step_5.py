# filename: codebase/step_5.py
import sys
import os
sys.path.insert(0, os.path.abspath("codebase"))
import pandas as pd
import numpy as np
import os

if __name__ == '__main__':
    data_dir = 'data/'
    input_file = os.path.join(data_dir, 'thermal_impurity_filtered_candidates.csv')
    print('Loading candidates from ' + input_file + '...')
    df = pd.read_csv(input_file)
    initial_count = len(df)
    df_filtered = df[(df['ox_band_gap'] > 0.5) & (df['ox_is_metal'] == False)].copy()
    filtered_count = len(df_filtered)
    print('Filtered candidates based on ox_band_gap > 0.5 eV and ox_is_metal == False.')
    print('Candidates retained: ' + str(filtered_count) + ' out of ' + str(initial_count) + '.')
    if filtered_count > 0:
        dg_abs = df_filtered['delta_G_700K'].abs()
        dg_min, dg_max = dg_abs.min(), dg_abs.max()
        if dg_max > dg_min:
            score_dG = 1.0 - (dg_abs - dg_min) / (dg_max - dg_min)
        else:
            score_dG = 1.0
        tmelt = df_filtered['Tmelt_proxy']
        tmelt_min, tmelt_max = tmelt.min(), tmelt.max()
        if tmelt_max > tmelt_min:
            score_Tmelt = (tmelt - tmelt_min) / (tmelt_max - tmelt_min)
        else:
            score_Tmelt = 1.0
        bg = df_filtered['ox_band_gap']
        bg_min, bg_max = bg.min(), bg.max()
        if bg_max > bg_min:
            score_bg = (bg - bg_min) / (bg_max - bg_min)
        else:
            score_bg = 1.0
        df_filtered['score_dG'] = score_dG
        df_filtered['score_Tmelt'] = score_Tmelt
        df_filtered['score_bg'] = score_bg
        df_filtered['composite_score'] = (score_dG + score_Tmelt + score_bg) / 3.0
        df_filtered = df_filtered.sort_values('composite_score', ascending=False)
        print('\nScore Components:')
        print('- score_dG: 1.0 - normalized abs(Delta G at 700 K) (higher is closer to 0)')
        print('- score_Tmelt: normalized Tmelt_proxy (higher is more stable)')
        print('- score_bg: normalized band gap (higher is better insulator)')
        print('- composite_score: average of the three scores\n')
        print('--- Top 20 Final Ranked Candidates ---')
        top_20 = df_filtered.head(20)
        header = 'Rank | Oxide Formula | Carbonate Formula | Delta G 700K (eV) | Tmelt Proxy (K) | Band Gap (eV) | Score'
        print(header)
        print('-' * len(header))
        rank = 1
        for idx, row in top_20.iterrows():
            ox_form = str(row['oxide_formula'])
            carb_form = str(row['carbonate_formula'])
            dg = str(round(row['delta_G_700K'], 4))
            tmelt_val = str(round(row['Tmelt_proxy'], 1))
            bg_val = str(round(row['ox_band_gap'], 4))
            score_val = str(round(row['composite_score'], 4))
            print(str(rank).ljust(4) + ' | ' + ox_form.ljust(13) + ' | ' + carb_form.ljust(17) + ' | ' + dg.ljust(12) + ' | ' + tmelt_val.ljust(15) + ' | ' + bg_val.ljust(13) + ' | ' + score_val)
            rank += 1
        output_file = os.path.join(data_dir, 'final_ranked_candidates.csv')
        df_filtered.to_csv(output_file, index=False)
        print('\nFinal ranked candidates saved to ' + output_file)
    else:
        print('No candidates left to rank.')