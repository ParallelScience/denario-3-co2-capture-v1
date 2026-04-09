1. **Reaction Space Mapping and Mass Balance**:
   Implement a matching algorithm to identify all possible carbonation pathways for each metal system. For each oxide precursor ($M_xO_y$), search for all carbonate phases ($M_aCO_3$) and potential byproduct oxides ($M_bO_c$) in the dataset. Define the reaction as $Reactant\_Phase + CO_2 \rightarrow Product\_Phase + \sum (Byproduct\_Phases)$. Ensure global mass balance for all elements (M, C, O) is satisfied for every reaction pair.

2. **Thermodynamic Filtering and Stability Thresholding**:
   Apply a strict filter of `energy_above_hull` ≤ 0.1 eV/atom for all phases involved in the reaction (precursors, products, and byproducts). Discard any reaction pathway where any participating phase exceeds this stability threshold to ensure experimental accessibility.

3. **Data-Driven Entropy Estimation**:
   Fetch experimental $S_{298}$ values or high-fidelity calculated vibrational entropy data from the Materials Project API using `pymatgen` to create a training set. Train a Random Forest regressor using structural features (`volume_A3`, `density_g_cm3`, `nsites`, `crystal_system`) and composition features to predict $S_{298}$ for all phases. Use cross-validation to prevent overfitting and ensure the model is decoupled from the final candidate ranking.

4. **Regeneration Temperature ($T_{reg}$) Calculation**:
   Calculate the reaction enthalpy $\Delta H \approx \Delta E$ and the reaction entropy $\Delta S = S_{products} - S_{reactants} - S_{CO_2(gas)}$, where $S_{CO_2(gas)} = 213.8$ J/mol·K. Compute $T_{reg} = \Delta H / \Delta S$. Discard reactions where $\Delta S \geq 0$ or where $T_{reg}$ is non-physical, and filter for candidates with $T_{reg}$ in the 300–600°C range.

5. **Structural Compatibility and Kinetic Proxy**:
   Quantify structural fatigue by calculating the "Volume Expansion Ratio" ($\Delta V / V_{oxide}$) for each reaction. Additionally, compare the `space_group` and `crystal_system` of the reactant and product to identify symmetry preservation. Flag materials with a volume expansion ratio > 20% as high-risk for sorbent pulverization.

6. **Electronic and Physical Filtering**:
   Apply an electronic filter to prioritize insulators/semiconductors. Use the `band_gap` column to filter for candidates with `band_gap > 0.5 eV` to account for PBE underestimation, as metallic phases are often poor candidates for industrial regeneration.

7. **Pareto-Front Candidate Selection**:
   Instead of weighted scoring, identify the Pareto-optimal set of materials in the 3D objective space of (1) $\Delta E$ (calibrated against known industrial sorbents like CaO), (2) $T_{reg}$ (300–600°C), and (3) Volume Expansion Ratio. This identifies non-dominated candidates that offer the best trade-offs between thermodynamics, regeneration feasibility, and structural stability.

8. **Sensitivity Analysis and Validation**:
   Perform a sensitivity check by varying the reference energy of $CO_2$ by $\pm 0.1$ eV. Re-calculate $\Delta E$ and $T_{reg}$ for the top-ranked Pareto candidates to ensure the ranking is robust against DFT systematic errors. Validate the final list by cross-referencing with known industrial sorbents to ensure the model captures established high-performance materials.