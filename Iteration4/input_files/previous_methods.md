1. **Data Preprocessing and Polymorph Selection**:
   Group the dataset by `formula`. For each unique formula, identify all entries and select only the polymorph with the lowest `energy_above_hull` to represent the most stable version of that phase. This ensures that subsequent reaction energy calculations are based on the most experimentally viable materials.

2. **Stoichiometric Reaction Mapping**:
   Implement a parsing algorithm to identify all possible carbonation reactions of the form $Reactant\_Phase + CO_2 \rightarrow Product\_Phase + \sum Byproduct\_Phases$. For each metal-containing system, iterate through all combinations of oxide precursors and carbonate products. Ensure global mass balance for all elements (M, C, O) and select the specific combination of byproduct phases that results in the lowest total reaction energy ($\Delta E$) for each unique (oxide, carbonate) pair.

3. **Thermodynamic Reaction Energy Calculation**:
   Calculate the reaction energy $\Delta E = \sum E_{products} - \sum E_{reactants} - E_{CO_2}$, where $E_{CO_2} = -11.17$ eV/formula unit. Apply a strict filter of `energy_above_hull` ≤ 0.1 eV/atom for all participating phases (reactants, products, and byproducts) to ensure the entire reaction pathway is thermodynamically accessible.

4. **Entropy Estimation and Gibbs Free Energy**:
   Estimate the vibrational entropy ($S_{298}$) for each solid phase using the Dulong-Petit limit ($S \approx 3Nk_B$ per atom). Acknowledge this as an upper-bound approximation for the 300–600°C range. Use $S_{CO_2(gas)} = 213.8$ J/mol·K to calculate the reaction entropy $\Delta S = S_{products} - S_{reactants} - S_{CO_2(gas)}$.

5. **Regeneration Temperature and Hysteresis Analysis**:
   Calculate the regeneration temperature $T_{reg} = \Delta H / \Delta S$, approximating $\Delta H \approx \Delta E$. Define the hysteresis energy as $\Delta E_{hysteresis} = | \Delta E_{carbonation} - \Delta E_{decomposition} |$. Flag reactions with high $\Delta E_{hysteresis}$ (> 0.5 eV) as having significant kinetic barriers or potential for thermodynamic trapping, prioritizing candidates with minimal hysteresis for reversible cycling.

6. **Structural and Kinetic Feasibility**:
   Assess structural integrity by calculating the "Volume Expansion Ratio" ($\Delta V / V_{oxide}$). Filter out candidates where the volume expansion exceeds 20% to mitigate risks of material pulverization. Categorize crystal systems into 3D frameworks versus lower-dimensionality structures (1D/2D) to prioritize structural stability.

7. **Electronic Filtering**:
   Apply a filter based on the `band_gap` column. Prioritize candidates with `band_gap > 0.5 eV` to ensure the material acts as an insulator or semiconductor, which is preferred for industrial regeneration efficiency and thermal management.

8. **Pareto-Optimal Candidate Ranking**:
   Construct a 3D objective space consisting of (1) $\Delta E$ (normalized to CaO), (2) $T_{reg}$ (targeting 300–600°C), and (3) Volume Expansion Ratio. Identify the Pareto-optimal set of materials that provide the best trade-offs between thermodynamic favorability, regeneration feasibility, and structural stability. Validate the top-ranked candidates against known industrial sorbent literature.