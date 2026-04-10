1. **Data Validation and Stoichiometric Parsing**:
   Validate the `formula` strings to ensure correct elemental parsing. Group materials by their metal-to-oxygen ratio to identify potential oxide-carbonate reaction pairs. For each unique chemical system, retain the most stable polymorph (lowest `energy_above_hull`) for both the oxide and carbonate to ensure thermodynamic screening is performed on the most experimentally accessible phases.

2. **Thermodynamic Reaction Energy Calculation**:
   Calculate the 0 K reaction energy $\Delta E = E(M_xCO_3) - E(M_xO_y) - E(CO_2)$ for all identified pairs. Use the reference energy for $CO_2$ consistent with the Materials Project GGA/PBE framework. Apply a strict filter requiring both the oxide precursor and the carbonate product to have an `energy_above_hull` $\le 0.1$ eV/atom to ensure the reaction pathway is thermodynamically viable.

3. **Gibbs Free Energy and Reaction Window Analysis**:
   Compute the Gibbs Free Energy of reaction $\Delta G(T, P) = \Delta H - T\Delta S$ for each pair. Incorporate $CO_2$ gas-phase entropy and enthalpy contributions from NIST-JANAF tables. Perform a sensitivity analysis by varying temperature (500 K to 1200 K) at a partial pressure of $P_{CO_2} = 0.15$ bar to identify the equilibrium temperature ($T_{eq}$) where $\Delta G \approx 0$.

4. **Topotactic Transition Verification**:
   Assess structural similarity between oxide-carbonate pairs using `StructureMatcher` to quantify the degree of oxygen-sublattice preservation. Exclude pairs with high structural dissimilarity or reconstructive transformations, prioritizing candidates where the oxygen packing density remains consistent to minimize mechanical failure during cycling.

5. **Thermal Stability and Sintering Proxy**:
   Estimate a melting point proxy for each candidate as a function of `formation_energy_per_atom` and `density` (as a proxy for lattice energy and bond strength). Filter out candidates with predicted melting points below 800 K to exclude materials prone to rapid sintering or liquid-phase formation at regeneration temperatures.

6. **Chemical Stability and Impurity Screening**:
   Perform impurity screening by filtering out materials containing elements known to be highly reactive with sulfur (e.g., specific high-alkali content materials) that are prone to forming low-melting-point sulfates. Prioritize materials that demonstrate thermodynamic robustness against common flue gas contaminants.

7. **Electronic Property Filtering**:
   Filter the remaining candidates based on the `band_gap` and `is_metal` columns. Prioritize materials with a `band_gap > 0.5 eV` to ensure the sorbent acts as an insulator or semiconductor, facilitating efficient thermal management during the endothermic regeneration cycle.

8. **Final Candidate Ranking**:
   Rank the filtered candidates using a weighted score that balances thermodynamic favorability ($\Delta G$ at 700 K), structural similarity (topotactic score), and thermal robustness (melting point proxy). Present the final list of materials that demonstrate both the capacity for $CO_2$ capture and the physical properties required to withstand industrial cycling conditions.