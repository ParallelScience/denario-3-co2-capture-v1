1. **Stoichiometric Parsing and Reaction Mapping**:
   Parse the `formula` strings to identify metal-to-oxygen ratios. Normalize all formulas to a fixed number of metal atoms to identify reaction pairs $(M_xO_y, M_xO_z(CO_3)_w)$ that share identical metal-to-non-carbonate-oxygen ratios. Filter all pairs to ensure both the oxide and the carbonate reside within the $\le 0.1$ eV/atom `energy_above_hull` threshold to maintain experimental accessibility.

2. **Refined Thermodynamic Landscape Calculation**:
   Calculate the reaction enthalpy $\Delta H \approx \Delta E$ at 0 K using the reference energy for $CO_2$ of -11.17 eV/formula unit. Estimate the Debye temperature ($\Theta_D$) for each solid phase using the Lindemann criterion based on the provided `density`, `nsites`, and molar volume. Use $\Theta_D$ to calculate the vibrational entropy contribution and determine the Gibbs free energy $\Delta G(T, P)$ at $P_{CO_2} = 0.15$ bar, incorporating temperature-dependent entropy for $CO_2$ gas from NIST-JANAF tables.

3. **Strict Mechanical Integrity Filtering**:
   Calculate the molar volume change $\Delta V = V(M_xCO_3) - V(M_xO_y) - V(CO_2)$. Apply a hard filter to exclude all candidates where $|\Delta V| > 20\%$. This threshold acts as a binary "go/no-go" constraint to prevent pore blockage and particle pulverization. Only materials passing this filter will proceed to the ranking stage.

4. **Stability and Cohesive Energy Proxy**:
   Use the `formation_energy_per_atom` as the primary metric for thermodynamic stability. To approximate cohesive energy, reconstruct the total energy relative to isolated atoms by utilizing the Materials Project's elemental reference energies. Prioritize materials with higher relative cohesive energy as a proxy for surface mobility resistance and sintering resistance at operating temperatures.

5. **Sensitivity Analysis for Flue Gas Fluctuations**:
   Perform a sensitivity analysis on the "Goldilocks" candidates (those with favorable $\Delta G$ and low $\Delta V$) by varying the $CO_2$ partial pressure from 0.05 bar to 0.5 bar. Identify candidates that maintain thermodynamic stability and favorable reaction thermodynamics across this range, ensuring the sorbent remains robust under typical industrial flue gas fluctuations.

6. **Stability Prediction for Missing Compositions**:
   Train a Random Forest classifier on the full 40,923-entry dataset to predict `is_stable` status based on composition (element fractions, electronegativity, atomic radius) and structural features (crystal system, density, nsites). Use this model to evaluate the stability of high-potential but currently "missing" compositions to identify candidates for future experimental synthesis.

7. **Pareto Ranking and Selection**:
   Construct a 2D Pareto front analysis using only the subset of candidates that passed the $\Delta V \le 20\%$ mechanical integrity filter. Plot $\Delta G$ (at 700 K) against the cohesive energy proxy. Rank candidates based on their proximity to the "optimal-delta" zone—where the reaction is spontaneous yet reversible.

8. **Final Candidate Synthesis**:
   Compile the final ranked list of sorbent precursors. Categorize the materials by their chemical system (e.g., alkali-metal vs. transition-metal based) and provide the calculated $\Delta G$, $\Delta V$, and cohesive energy proxy for each. Highlight the top-performing candidates that demonstrate both thermodynamic viability and structural robustness for industrial CO₂ capture.