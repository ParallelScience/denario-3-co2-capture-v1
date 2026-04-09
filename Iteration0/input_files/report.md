

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
        