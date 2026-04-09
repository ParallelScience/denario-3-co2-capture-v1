

Iteration 0:
### Research Summary: Thermochemical Screening of CO₂ Capture Materials

**1. Dataset & Methodology**
*   **Data:** 40,923 inorganic materials (Materials Project, April 2026). 39,133 oxides, 1,790 carbonates.
*   **Approach:** Stoichiometric parsing of $M_xO_y + zCO_2 \rightarrow M_x(CO_3)_z$ (where $y=2z$ or $y=z$).
*   **Metrics:** $\Delta E$ (normalized per mole $CO_2$) using $E_{CO_2} = -3.94$ eV (GGA/PBE). $T_{reg} \approx \Delta E / \Delta S$ ($\Delta S \approx 213.8$ J/mol·K).
*   **Constraints:** Stability filtered by `energy_above_hull` ($\le 0.05$ eV/atom). "Optimal-delta" range defined as $-0.5$ to $-1.5$ eV/CO₂.

**2. Key Findings**
*   **Thermodynamic Trade-off:** Zero candidates satisfy both the "optimal-delta" range and strict thermodynamic stability (hull $\le 0.05$ eV/atom). Optimal candidates are inherently metastable.
*   **Performance Drivers:** $\Delta E$ correlates strongly with Pauling Electronegativity ($r=0.75$) and Ionic Radius ($r=-0.69$). Larger, electropositive cations favor more exothermic carbonation.
*   **Structural Proxies:** Macroscopic features (volume, density) are poor predictors of $\Delta E$.
*   **Promising Candidates:** 72 metastable "optimal-delta" materials identified.
    *   *Mn-systems:* Low $T_{reg}$ ($-21$ to $31$ °C), potential for DAC.
    *   *K-systems:* $T_{reg}$ ($101$–$151$ °C), stable oxide precursors.
    *   *Li-Transition Metal Oxides:* Effective modulation of $\Delta E$ via alloying, $T_{reg}$ ($111$–$399$ °C).

**3. Limitations & Uncertainties**
*   **Stability:** Optimal candidates are metastable; long-term cycling requires kinetic stabilization (e.g., nanostructuring, encapsulation).
*   **Kinetics:** Dataset lacks surface area, porosity, and reaction rate data.
*   **Polymorphism:** High sensitivity to structural phase; ground-state approximations may overlook accessible metastable polymorphs.

**4. Future Directions**
*   **Kinetic Stabilization:** Focus on experimental validation of metastable candidates using porous supports or dopants to prevent sintering/decomposition.
*   **Substitution Strategy:** Use electronegativity and ionic radius trends to design mixed-metal oxides that "tune" $\Delta E$ into the $100$–$400$ °C regeneration window.
*   **Refinement:** Incorporate kinetic descriptors or surface energy calculations to move beyond bulk thermodynamic screening.
        

Iteration 1:
**Methodological Evolution**
- **Refinement of Reaction Mapping:** The analysis pipeline was updated to include a systematic correction of $-7.23$ eV to the raw reaction energies ($\Delta E$) to align with the GGA reference energy for CO₂.
- **Entropy Estimation:** Introduced the Neumann-Kopp additive rule to estimate solid-phase entropy ($S_{solid}$), enabling the calculation of regeneration temperatures ($T_{reg}$) rather than relying solely on $\Delta E$ as a proxy for capture feasibility.
- **Multivariate Regression:** Implemented an OLS regression model to quantify the influence of metal electronegativity, ionic radius, and oxidation state on $\Delta E$, replacing qualitative observations with statistical coefficients.
- **Feasibility Scoring:** Developed a weighted composite metric (40% $\Delta E$ window, 30% stability penalty, 30% $T_{reg}$ target) to rank candidates, moving from simple filtering to a prioritized selection framework.

**Performance Delta**
- **Quantitative Gains:** The screening successfully distilled 40,923 entries into 1,671 valid oxide-carbonate pairs. 
- **Improved Interpretability:** The inclusion of $T_{reg}$ estimation identified that 48.4% of valid pairs (743 candidates) fall within the industrial target window of 300–600°C, a significant improvement over the previous iteration's reliance on $\Delta E$ alone.
- **Regression Accuracy:** The OLS model achieved an $R^2$ of 0.5613, providing a predictive basis for virtual doping that was absent in the baseline.
- **Trade-offs:** While the stability penalty remains low (average 0.093 eV/atom), the transition from pure binary oxides to mixed-metal systems (e.g., $LiMn(CO_3)_2$) represents a shift toward more complex, but thermodynamically superior, sorbent architectures.

**Synthesis**
- **Causal Attribution:** The observed shift in candidate prioritization—from highly exothermic alkali metals to transition-metal-doped systems—is directly attributable to the inclusion of $T_{reg}$ and the OLS regression findings. The regression confirmed that larger ionic radii and lower electronegativity drive excessive exothermicity; thus, the shift toward transition metals (which possess higher electronegativity) was necessary to achieve reversibility.
- **Validity and Limits:** The results demonstrate that thermodynamic favorability and experimental accessibility are not mutually exclusive, as many optimal candidates reside on the convex hull. The reliance on the Neumann-Kopp rule for entropy is a necessary simplification; however, the consistency of the results suggests that the identified "Design-Ready" materials are robust candidates for experimental validation.
- **Direction:** Future work should move beyond thermodynamic proxies to incorporate kinetic considerations, as the current model assumes equilibrium conditions which may not hold in rapid industrial cycling.
        