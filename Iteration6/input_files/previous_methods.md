1. **Data Preprocessing and Stoichiometric Mapping**:
   Parse the `formula` strings to extract metal-to-oxygen ratios. Group materials into potential reaction pairs $(M_xO_y, M_xCO_3)$ that share identical metal stoichiometry. Implement robust parsing to handle complex formulas and ensure that the matching logic accounts for multiple polymorphs per composition. Filter the dataset to retain only entries with `energy_above_hull` $\le 0.1$ eV/atom to ensure experimental accessibility. Focus on "simple" carbonation reactions ($M_xO_y + CO_2 \rightarrow M_xCO_3$) to maintain thermodynamic consistency.

2. **Refined Thermodynamic Landscape Calculation**:
   Calculate the reaction enthalpy $\Delta H \approx \Delta E$ at 0 K. Use a consistent reference energy for $CO_2$ gas derived from the dataset's internal energy values for C and $O_2$ (or the standard MP GGA/PBE reference energy of -11.17 eV/formula unit, verified against the dataset's energy scale). Estimate the Gibbs free energy $\Delta G(T, P)$ at $P_{CO_2} = 0.15$ bar by approximating the solid-state entropy change using a constant entropy per atom ($S \approx 3k_B$ per atom) for both oxide and carbonate phases, while using NIST-JANAF tables for the gas-phase entropy of $CO_2$.

3. **Mechanical Integrity and Volume Change Analysis**:
   Calculate the molar volume change $\Delta V = V(M_xCO_3) - V(M_xO_y) - V(CO_2)$. Normalize this by the volume of the oxide precursor to obtain the percentage volume expansion. Filter out candidates where $|\Delta V| > 20\%$, as these are prone to mechanical decrepitation and poor diffusion kinetics during cycling.

4. **Kinetic and Sintering Resistance Assessment**:
   Estimate the melting point $T_{melt}$ for each candidate using a predictive regression model based on `formation_energy_per_atom` and `nsites`. Calculate the "Tamman temperature" ($T_T \approx 0.5 \times T_{melt}$) as a proxy for the onset of significant surface diffusion. Prioritize materials where the target operating temperature is significantly below $T_T$ to minimize sintering-induced surface area loss.

5. **Negative Control Validation**:
   Identify known "poor" sorbents within the dataset—specifically materials that form carbonates with extremely low formation energies (making them impossible to regenerate) or those with excessive volume expansion. Run these through the pipeline to ensure the scoring function correctly penalizes them, validating the pipeline's ability to distinguish between stable and regenerable materials.

6. **Pareto Front Construction**:
   Construct a 2D Pareto front analysis to identify optimal candidates. Plot $\Delta G$ (at 700 K) against $\Delta V$ (volume change) and $\Delta G$ against an elemental abundance proxy (based on frequency in the Earth's crust). This visualization will identify materials that balance thermodynamic favorability with structural and economic viability.

7. **Isostructural Substitution and Tuning**:
   Select the top mixed-metal oxide candidates from the Pareto front. Perform a virtual substitution analysis by identifying isostructural compounds in the dataset where the primary metal cation is replaced by a different ion. Calculate the shift in $T_{eq}$ for these substituted pairs to establish a linear "tuning rule" for sorbent design. If the substituted compounds are not present in the dataset, flag them as high-potential targets for future synthesis.

8. **Final Candidate Selection**:
   Synthesize the results into a final ranked list. Prioritize materials that reside on the Pareto front, exhibit $\Delta V < 20\%$, and demonstrate a $T_{eq}$ within the 600 K–900 K range. Provide the final selection of materials, categorized by their potential for industrial application based on the tuned thermodynamic and structural criteria.