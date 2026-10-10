# 🚀 Modular Orbital Launch Vehicle Family: Corolt-IV (Vector-IV)

> *"The historic leap from solid-fueled sounding rockets to multi-stage liquid orbital propulsion. Engineered to master controlled orbital insertion ($v_{\text{orb}} > 2,250\text{ m/s}$), deliver scientific satellites into Low Kerbin Orbit (LKO up to 300 km), and inaugurate deep-space probe missions."*

---

## 📐 Strategic Architecture & Program Transition

Following the definitive success of **Mission CSA-10** (solid-ground touchdown in the Kerbin Mountains, peak altitude $162.65\text{ km}$, and harvesting $+30.3\text{ science points}$), the CSA Flight Operations Directorate officially transitioned into the orbital era:
* **Vector-III Fleet Retirement**: Production of sounding rockets has ended.
* **Vector-IV (Corolt-IV) Authorization**: R&D funds ($> 89.8\text{ science points}$) allocated across liquid propulsion, pressure vessels, vacuum engines, and structural adapters (`gptt_liquidFueledRockets`, `gptt_tank1`, `gptt_liquid0`, `gptt_liquidVac0`, `gptt_const1`).
* **Modular Fleet Standard**: Rather than a single non-reusable design, the Corolt-IV is configured as a **modular three-variant launch vehicle family** sharing standard 1.25m tooling and avionics.

```text
                  COROLT-IV MODULAR LAUNCH VEHICLE FAMILY
                  
       COROLT-IV A                  COROLT-IV B                  COROLT-IV C
    [Light Orbital / Test]       [Standard Workhorse]       [Heavy / High Energy]
      Payload: 250 kg             Payload: 500 kg             Payload: 800+ kg
             ▲                           ▲                           ▲
            / \                         / \                         / \
           |   | Payload (0.25t)       |   | Payload (0.50t)       |   | Payload (0.80t)
           | S2| Belle-RLX81           | S2| Belle-RLX81           | S2| Belle-RLX81
           |===| (FL-T200)             |===| (FL-T400)             |===| (FL-T400+T200)
           |   |                       |   |                       |   |
           | S1| Single Core         [S] S1 [S] Core + 2x Shrimp   [S] S1 [S] Quad Core +
           |___| Etoh-140-TU           |___| Etoh-140-TU           [S]|__|[S] 4x Shrimp Boosters
```

---

## 🔬 Post-CSA-10 Telemetry Benchmarking & Empirical Physics

Flight data from Mission CSA-10 provided vital empirical calibration for the Corolt-IV aerodynamic and propulsion design:

| Engineering Parameter | CSA-10 Sounding Rocket Empirical Data | Vector-IV Design Adaptation | Impact on Vector-IV Orbital Performance |
| :--- | :---: | :---: | :--- |
| **Effective Drag ($C_d \cdot A$)** | $1.05\text{ m}^2$ (Unguided 0.625m stack) | **$0.35 - 0.45\text{ m}^2$** (Enclosed payload fairing) | Aerodynamic drag losses cut by $> 55\%$ despite 1.25m diameter. |
| **Dynamic Pressure (Max Q)** | $66.5\text{ kPa}$ (Hypersonic entry) / $42\text{ kPa}$ (Ascent) | **$< 38.0\text{ kPa}$** during transonic ascent | TWR limited to $1.50 - 1.55$ at liftoff prevents aero flutter and heating. |
| **Thrust Vector Authority** | $0^\circ$ (Fins only, steering lost at $> 38\text{ km}$) | **$2^\circ - 3^\circ$ Gimbal TVC** (Continuous active guidance) | Eliminates atmospheric gravity turn cutoff; guarantees zero-AoA vacuum burns. |
| **Vacuum Flight Efficiency** | Ballistic arc with fixed solid motor burnout | **Restartable liquid upper stage** ($I_{sp} = 272\text{ s}$) | Enables coasting to apoapsis ($100 - 300\text{ km}$) and circularization burn. |
| **Payload Structural Shock** | Peak deceleration $8.47\text{ G}$ at entry | **Peak acceleration $< 4.2\text{ G}$** during ascent | Protects delicate optical instruments, antennas, and solar cells. |

---

## ⚙️ Detailed Engineering Breakdown by Variant

---

### 1. COROLT-IV A — Light Orbital & Qualification Variant (250 kg Payload)
Designed for small scientific satellites, camera reconnaissance packages, and suborbital/orbital test flights.

* **Payload Capacity**: $250\text{ kg}$ ($0.25\text{ t}$) to $150\text{ km}$ LKO.
* **Liftoff Mass ($m_0$)**: $9.17\text{ t}$.
* **Liftoff Thrust**: $160.0\text{ kN}$ (Sea Level).
* **Liftoff TWR**: **$1.78$**.
* **Total Vacuum $\Delta v$**: **$5,367\text{ m/s}$**.

#### Bill of Materials & Assembly Order (VAB Stack Top to Bottom):
1. **Payload Section**:
   * Nose Fairing / Aerodynamic Shield: `SR.PayloadFairing.625` or BDB 0.625m Fairing ($0.05\text{ t}$).
   * Probe Core / Avionics: `probeCoreSphere_v2` (Stayputnik) or BDB Pathfinder ($0.05\text{ t}$).
   * Scientific Payload: PresMat Barometer, 2HOT Thermometer, Geiger Counter ($0.02\text{ t}$).
   * Power & Comms: `battery-rad-125` ($80\text{ EC}$) + `SurfAntenna` ($0.03\text{ t}$).
   * Ballast / Structure / Separation: Decoupler TD-06 `Decoupler_0` ($0.01\text{ t}$).
2. **Stage 2 (Upper Stage)**:
   * Upper Fuel Tank: 1x `fuelTankSmall` (FL-T200) — $1.0\text{ t}$ Propellant, $0.125\text{ t}$ Dry.
   * Upper Stage Engine: 1x `bluedog_Agena_Engine_XLR81` (Belle-RLX81) — Thrust $17.2\text{ kN}$, $I_{sp} = 272\text{ s}$, Mass $0.09\text{ t}$, Gimbal $3^\circ$.
   * Interstage Decoupler: 1x `Decoupler_1` (TD-12 1.25m Decoupler) ($0.04\text{ t}$).
3. **Stage 1 (Booster Core)**:
   * Propellant Tanks: 1x `fuelTank_long` (FL-T800) + 1x `fuelTank` (FL-T400) — $6.0\text{ t}$ Propellant, $0.75\text{ t}$ Dry.
   * Core Engine: 1x `bluedog_Redstone_A7_TailUnit` (Etoh-140-TU Sandstone) — Thrust $160\text{ kN}$ SL / $182\text{ kN}$ Vac, $I_{sp} = 218/249\text{ s}$, Mass $0.75\text{ t}$, Gimbal $2^\circ$.
   * Aerodynamic Fins: 4x `basicFin` mounted radially at the tail ($0.08\text{ t}$).

---

### 2. COROLT-IV B — Standard Workhorse Variant (500 kg Payload to 300 km LKO)
The primary workhorse of the Corolt Space Agency. Tailored to launch multi-instrument environmental satellites into circularized orbits up to $300\text{ km}$.

* **Payload Capacity**: **$500\text{ kg}$ ($0.50\text{ t}$)** to circular $300\text{ km}$ LKO.
* **Liftoff Mass ($m_0$)**: **$14.59\text{ t}$**.
* **Liftoff Thrust**: **$220.0\text{ kN}$** ($160\text{ kN}$ core + $2 \times 30\text{ kN}$ solids).
* **Liftoff TWR**: **$1.54$** (optimal aerodynamic envelope through Max Q).
* **Total Vacuum $\Delta v$**: **$5,392\text{ m/s}$** (core + boosters $2,250\text{ m/s}$, upper stage $3,142\text{ m/s}$).

#### Bill of Materials & Assembly Order (VAB Stack Top to Bottom):
1. **Payload Section (Orbital Science Probe CSA-S1 — 500 kg)**:
   * Aerodynamic Fairing: 1.25m payload fairing or 0.625m truss fairing ($0.08\text{ t}$).
   * Probe Core: `probeCoreSphere_v2` / BDB Pathfinder with kOS flight computer ($0.05\text{ t}$).
   * Full Science Bay:
     * `SR_Payload_01` (Materials Study Mini-Lab) ($0.05\text{ t}$)
     * `bluedog_Micrometeorite` (Micrometeoroid detector) ($0.015\text{ t}$)
     * `kerbalism-geigercounter` (Radiation counter) ($0.005\text{ t}$)
     * `sensorBarometer` & `sensorThermometer` ($0.01\text{ t}$)
   * Power & Comms: 2x `battery-rad-125` ($160\text{ EC}$) + `longAntenna` (Communotron 16) ($0.05\text{ t}$).
   * Separation: 1x `Decoupler_0` (TD-06) ($0.01\text{ t}$).
2. **Stage 2 (Upper Stage / Orbital Insertion & Circularization)**:
   * Upper Fuel Tank: 1x `fuelTank` (FL-T400) — $2.0\text{ t}$ Propellant, $0.25\text{ t}$ Dry.
   * Upper Engine: 1x `bluedog_Agena_Engine_XLR81` (Belle-RLX81) — Thrust $17.2\text{ kN}$, $I_{sp} = 272\text{ s}$, Mass $0.09\text{ t}$, Gimbal $3^\circ$.
   * Burn Time: $310.2\text{ s}$ (capable of multiple restarts).
   * Interstage Decoupler: 1x `Decoupler_1` (TD-12 1.25m Decoupler) ($0.04\text{ t}$).
3. **Stage 1 (Booster Core — 1.25m)**:
   * Propellant Tanks: 2x `fuelTank_long` (FL-T800) — $8.0\text{ t}$ Propellant, $1.0\text{ t}$ Dry.
   * Core Engine: 1x `bluedog_Redstone_A7_TailUnit` (Etoh-140-TU Sandstone) — Thrust $160\text{ kN}$ SL, Mass $0.75\text{ t}$, Gimbal $2^\circ$.
   * Tail Fins: 4x `bluedog_Delta_Fin` or `basicFin` ($0.08\text{ t}$).
4. **Stage 0 (Strap-on Solid Boosters — 2x Lateral)**:
   * Boosters: 2x `Shrimp` (F3S0 Solid Rocket Motor) — $30\text{ kN}$ SL each ($60\text{ kN}$ total).
   * Radial Decouplers: 2x `radialDecoupler` or `smallHardpoint`.
   * Burn Time: $10.2\text{ s}$ (provides initial kick off the pad, jettisoned cleanly at $T+11\text{ s}$).

---

### 3. COROLT-IV C — Heavy / High Energy Variant (800+ kg LKO or Trans-Munar Injection)
Engineered for deep exospheric exploration, high-radiation belt probes, and trans-Munar injection trajectories.

* **Payload Capacity**: $800\text{ kg}$ to $300\text{ km}$ circular LKO, or $350 - 400\text{ kg}$ on Trans-Munar Injection (TMI).
* **Liftoff Mass ($m_0$)**: $23.23\text{ t}$.
* **Liftoff Thrust**: **$460.0\text{ kN}$** ($340\text{ kN}$ core + $4 \times 30\text{ kN}$ solids).
* **Liftoff TWR**: **$2.02$**.
* **Total Vacuum $\Delta v$**: **$5,506\text{ m/s}$**.

#### Bill of Materials & Assembly Order (VAB Stack Top to Bottom):
1. **Payload Section (Heavy Probe / Lunar Scout — 800 kg)**:
   * Aerodynamic Fairing: 1.25m Expanded Fairing.
   * Probe Core: Advanced Avionics + Reaction Wheel + CommNet Dish.
   * Advanced Instrument Cluster + Deployable Solar Panels.
   * Separation: 1x `Decoupler_0` or `Decoupler_1`.
2. **Stage 2 (Extended Upper Stage)**:
   * Upper Fuel Tanks: 1x `fuelTank` (FL-T400) + 1x `fuelTankSmall` (FL-T200) — $3.0\text{ t}$ Propellant, $0.375\text{ t}$ Dry.
   * Upper Engine: 1x `bluedog_Agena_Engine_XLR81` (Belle-RLX81) — Thrust $17.2\text{ kN}$, $I_{sp} = 272\text{ s}$.
   * Burn Time: $465.2\text{ s}$.
   * Interstage Decoupler: 1x `Decoupler_1` (TD-12).
3. **Stage 1 (High-Thrust Quad Core — 1.25m)**:
   * Propellant Tanks: 3x `fuelTank_long` (FL-T800) — $12.0\text{ t}$ Propellant, $1.50\text{ t}$ Dry.
   * Core Engine: 1x `bluedog_Redstone_QuadEngine` (Etoh-340-QTU Feldspar Quad Engine) — Thrust $340\text{ kN}$ SL, Mass $1.60\text{ t}$.
   * Steering Support: 2x `bluedog_Jupiter_Vernier` or 4x steerable tail fins for attitude control.
4. **Stage 0 (Strap-on Solid Boosters — 4x Lateral)**:
   * Boosters: 4x `Shrimp` (F3S0) or 2x `solidBooster1-1` (BACC Thumper).
   * Radial Decouplers: 4x radial decouplers with inward-tilted nosecones for clean separation.

---

## 🚦 Flight Operations Protocol & Staging Sequence (Reference: COROLT-IV B)

```text
Staging Order:
[Stage 3] Ignition: Pad Liftoff -> Stage 1 Core (Etoh-140) + Stage 0 Boosters (2x Shrimp)
[Stage 2] Jettison: T+11s -> Booster Decoupling (2x Shrimp jettisoned clear of core)
[Stage 1] Staging:  T+115s (~48 km altitude) -> Stage 1 MECO, Stage 1 Decouple (TD-12) & Fairing Jettison
[Stage 0] Insertion: T+117s -> Stage 2 Ignition (Belle-RLX81) -> Orbital insertion & Circularization at Apogee
```

1. **Action Groups Standard (kOS Integration)**:
   * `AG1`: Toggle Atmospheric Sensors (PresMat, 2HOT, Aeronomy) during early ascent.
   * `AG2`: Toggle Space Sensors (Geiger Counter, Materials Mini-Lab, Micrometeoroids) once reaching $> 70\text{ km}$.
   * `AG3`: Deploy Comms Antennas & Solar Arrays upon orbital insertion.
   * `Abort`: Shutdown Stage 1 & Fire Stage 2 Escape Decoupler.
2. **Ascent Guidance Profile**:
   * **Pitch Kick**: Altitude $1,200\text{ m}$ at $v \approx 110\text{ m/s}$ $\rightarrow$ initial pitch $84^\circ$ towards Heading $90^\circ$ (East).
   * **Gravity Turn**: Autonomous zero-AoA hold through Max Q ($v = 280 - 450\text{ m/s}$ between $6\text{ km}$ and $14\text{ km}$).
   * **Core Burnout**: Altitude $\sim 48\text{ km}$, apoapsis $\sim 95 - 110\text{ km}$. Stage 1 separates.
   * **Coast Phase**: Vehicle coasts unpowered through the exosphere ($70\text{ km}$ to apoapsis).
   * **Circularization Burn**: Belle-RLX81 ignites at $T - 15\text{ s}$ before apoapsis ($\Delta v \approx 420\text{ m/s}$) to close orbit into $120\times 120\text{ km}$ or continues to $300\times 300\text{ km}$.

---

## 📜 Operational Flight Log & Production Fleet

| Serial / Unit | Configuration | Mission Assigned | Payload | Flight Date | Apogee / Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`COROLT IVB - B1`** | Corolt-IV B | **[CSA-11](/missions/csa-11)** | `CoroltSat-1A` ($248\text{ kg}$) | Year 1, Day 93 | 🟡 **269.1 km** (Historic maiden ascent, kOS guidance validated, upper stage Belle anomaly) |
| **`COROLT IVB - B2`** | Corolt-IV B | **[CSA-12](/missions/csa-12)** | `CoroltSat-1B` ($248\text{ kg}$) | Year 1, Day 159 | 🟢 **$305.9\times 299.6\text{ km}$** (100% Historic Orbital Insertion, $e=0.0035$, CoroltSat-1B Deployed & Active) |
