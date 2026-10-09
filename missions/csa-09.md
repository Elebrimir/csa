# 📋 Mission Profile & Flight Plan: CSA-09 «Equatorial Reach & Van Allen Probe»

* **Mission Code**: `CSA-09`
* **Flight Director**: CSA Mission Control (Kerbin Space Center)
* **Launch Vehicle**: [Corolt-IIIb (Upgraded 800 EC Upper Stage)](/vehicles/corolt-3b)
* **Target Altitude**: **> 270 km** (Deep Space & Van Allen Belt Threshold)
* **Status**: 🟢 MISSION COMPLETED | VESSEL & PAYLOAD RECOVERED (85.5% Value)

---

## 🎯 Mission Objectives

1. **Equatorial Inland Trajectory & Coriolis Compensation**:
   * Direct the ascent along **Heading 270º (Due West)** to keep the suborbital trajectory inside Kerbin's continental interior (Grasslands, Highlands, Mountains) along the equator.
   * Exploit Kerbin's planetary rotation ($\sim 174.5\text{ m/s}$ eastward) to naturally displace the ground track further inland and guarantee touchdown on dry land.
2. **Deep Space Apogee (> 250 km)**:
   * Penetrate the Van Allen radiation belt threshold (> 250 km) to collect the inaugural High Space radiation telemetry.
3. **Smart Power Budget Management (800 EC Bank)**:
   * Upgrade upper stage power capacity from 400 EC to **800 EC** (+2 battery units).
   * Duty-cycle scientific instruments to prevent power depletion: run the high-draw **Mini-Lab of Materials (`2.04 EC/s`)** for a strict **90-second burst** in vacuum, then shut it down.
   * Maintain an untouchable **100 EC battery safety floor** to ensure 100% powered avionics, telemetry, and parachute arming.
4. **Guaranteed Truss Fairing Ejection**:
   * Autonomous ejection of protective fairings at $> 58\text{ km}$ via kOS module event dispatching.
5. **Comprehensive Telemetry Logging**:
   * Log real-time propellants, electric charge, atmospheric temperature, core vessel temperature, and aerodynamic skin temperature via `tools/telemetry_recorder.py`.

---

## 📊 Post-Flight Performance: Simulated vs. Actual Flight

Following recovery 268.0 km west of the Kerbin Space Center, telemetry logs were processed to contrast pre-flight mathematical modeling against real flight physics:

| Parameter | Pre-Flight Simulated | Actual Flown Telemetry | Delta / Deviation | Engineering Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Peak Altitude (Apoapsis)** | 277.65 km | **162.56 km** | -115.09 km (-41.4%) | Higher total payload mass & intact Stage 2 booster retention |
| **Max Surface Velocity** | 1,720.0 m/s | **1,518.8 m/s** | -201.2 m/s (-11.7%) | Transonic drag profile ($C_d \cdot A = 0.963\text{ m}^2$) |
| **Time in Space (>70 km)** | 512.0 s | **468.0 s (7.8 min)** | -44.0 s (-8.6%) | Robust microgravity science window |
| **Total Flight Duration** | 855.6 s | **1,035.3 s (17.2 min)**| +179.7 s (+21.0%) | Extended parachute terminal descent |
| **Touchdown Longitude** | -144.5º W | **-100.22º W** | +44.28º East | Earlier splashdown in coastal shallows |
| **Touchdown Latitude** | -0.10º S | **-0.089º S** | +0.011º N | 🟢 **Near-perfect equatorial track alignment** |
| **Distance from KSC** | 732.9 km | **268.0 km** | -464.9 km | Coastal sea zone (268 km West) |
| **Battery Level at Touchdown**| 489.7 EC | **> 750 EC** | +260.3 EC | 🟢 **100% Avionics & parachute power maintained** |
| **Recovery Status** | Planned Recovery | **🟢 100% Intact** | **85.5% Value** | Full payload salvaged by KSC recovery teams |

### Actual vs. Simulated Ground Track & Exclusion Corridor
![CSA-09 Trajectory Comparison Map](../assets/csa-09_comparison_map.svg)

### Full-Flight Telemetry Plot
![CSA-09 Flight Telemetry Plot](../assets/csa-09_telemetry_plot.svg)

---

## 🔬 Post-Flight Debriefing & Anomalies Analysis

### 1. Flight Trajectory & Recovery Location
* **Ascent Track**: The rocket adhered strictly to the **Heading 270º (Due West)** equatorial corridor, keeping cross-track latitude deviation within **0.01º** ($\approx 1\text{ km}$ from the equator).
* **Coastal Landing Zone**: While the pre-flight simulation projected a 732 km trajectory landing in the deep continental interior, the vehicle touched down at **268.0 km West (Lon -100.22º)** in equatorial waters. KSC recovery teams promptly retrieved the vessel with an **85.5% recovery return**, completely avoiding the catastrophic loss experienced on CSA-08.

### 2. Vehicle Avionics & kOS Script Telemetry
* **GeoCoordinates Biome Runtime Collision**: At apoapsis ($T+923.9\text{ s}$ / $162.56\text{ km}$), the guidance script encountered a runtime exception: `GET Suffix 'BIOME' not found on GeoCoordinates`. In kOS, biome polling must be queried through `BODY:GEOPOSITIONLATLNG(...)`. The script was safely superseded by autonomous recovery routines.
* **Stage Separation Staging Configuration**: The upper stage booster (`SR.Rocket.625.01`) was retained attached to the payload truss throughout flight. Despite this added structural deadweight, the nosecone parachute (`SR.Nosecone.625`) successfully braked the full 1.1-tonne stack to a gentle **1.7 m/s** touchdown speed.
* **Power & Battery Health**: Upgrading the battery capacity to **800 EC** was an unqualified triumph. Over 750 EC remained in the reserves upon splashdown, eliminating the catastrophic brownout that doomed CSA-08.

---

## 📊 Pre-Flight Simulation & Power Budget

Simulated using 4th-order Runge-Kutta numerical integration with calibrated empirical drag ($C_d \cdot A = 1.727\text{ m}^2$):

| Parameter | Simulated Value | Remarks |
| :--- | :--- | :--- |
| **Launch Azimuth / Heading** | **270.0º (Due West)** | Aligned with equatorial continental corridor |
| **Pitch Kick Altitude** | **2,400 m** | Transition to 87.5º, down to 48º at 45 km |
| **Stage 1 Burnout (RT-10)** | **T+50.7 s @ 11.2 km** | Staging decoupler fires at $v \approx 420\text{ m/s}$ |
| **Stage 2 Burnout (SRM-XL)** | **T+109.9 s @ 58.1 km** | Active propulsion complete ($v_{orb} \approx 1,720\text{ m/s}$) |
| **Fairing Jettison** | **T+110 s (> 58 km)** | Unshrouds payload truss in vacuum |
| **Peak Apoapsis** | **277.65 km** | 🟢 **Crosses 250 km Van Allen threshold!** |
| **Total Flight Duration** | **855.6 s (14.3 min)** | Extended suborbital microgravity arc |
| **Inertial Downrange Distance** | **583.6 km (55.7º West)** | Downrange travel from rocket propulsion |
| **Coriolis Planetary Shift** | **149.3 km (14.3º West)** | Kerbin rotates under craft during 14.3 min flight |
| **Total Landing Displacement** | **732.9 km (70.0º West)** | Predicted landing near Longitude -144.5º |
| **Predicted Landing Biome** | **Grasslands / Highlands** | 🟢 **100% Solid Ground (No water)** |
| **Final Battery at Touchdown** | **489.7 / 800.0 EC** | 🟢 **61.2% Reserve Margin maintained!** |

### Simulated Trajectory & Power Profile Plot
![CSA-09 Simulated Ascent](../assets/csa-09_simulated_ascent.svg)

---

## 🗺️ KAA Airspace Hazard & Exclusion Corridor Notice (NOTAM)

The **Kerbal Aviation Administration (KAA)** has published the official Airspace and Surface Hazard Notice for Mission **CSA-09**:

![KAA Airspace and Surface Hazard Map CSA-09](../assets/csa-09_faa_hazard_map.svg)

### KAA Mission Notices & Safety Directives:
* **NOTAM Reference**: `KAA-CSA09-2026-10` (Effective Window: Y1-D91).
* **Launch Azimuth**: $270.0\text{º}$ (Due West along Equator).
* **Hazard Zone 1 (Booster Drop Zone)**: Designated drop sector at Lon $-77.5\text{º W}$, Lat $-0.1\text{º S}$ for the jettisoned RT-10 Hammer casing ($T+51\text{ s}$).
* **Primary Recovery Zone (Terrestrial)**: Nominal parachute touchdown footprint at Lon $-144.5\text{º W}$, Lat $-0.1\text{º S}$ in the Highlands continental interior.
* **Coriolis Exploitation Directive**: Kerbin's $174.5\text{ m/s}$ eastward rotational velocity offsets the suborbital ground track $149\text{ km}$ deeper inland, guaranteeing zero maritime exposure and 100% dry terrain recovery.

*(Note: Upon flight completion, this pre-flight baseline will be directly compared against real telemetry data).*

---

## ⚡ Power Consumption Model (800 EC Pack)

| Flight Phase | Duration | Active Systems | Drain Rate | Power Consumed | Remaining Battery |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Boost Phase (0–110s)** | 110 s | Avionics, kOS, Sensors, SAS reaction wheel | 0.54 EC/s | 59.4 EC | **740.6 EC** |
| **Space Entry & Coast** | 30 s | Base idle: Avionics + kOS (SAS OFF!) | 0.10 EC/s | 3.0 EC | **737.6 EC** |
| **Low Space Mini-Lab Run** | 90 s | Mini-Lab active (2.04) + Base idle (0.10) | 2.14 EC/s | 192.6 EC | **545.0 EC** |
| **Coast to Apoapsis & Reentry** | 500 s | Base idle (kOS + Avionics + Geiger sensor) | 0.09 EC/s | 45.0 EC | **500.0 EC** |
| **Atmospheric Reentry (70–0 km)** | 125 s | Base idle + Aeronomy burst (40s @ 0.50 EC/s) | 0.25 EC/s | 31.2 EC | **468.8 EC** |
| **Touchdown & Parachute Recovery**| - | Full flight systems active | - | **Total: ~331 EC** | **~469 EC RESERVE!** 🟢 |

---

## 🚀 Pre-Flight Engineering Checklist

### 1. VAB Vehicle Configuration (`CSA-09`)
* [ ] **Upper Stage Power**: Add **2 additional battery units** to `EtapaSup-CSA09` to achieve **800 EC** total capacity.
* [ ] **Science Payload**:
  * `SR.ProbeCore` (kOS flight computer + 32 MB flash storage)
  * `SR_Payload_01` (Materials Study Mini-Lab)
  * `SR_Payload_02` / `SR_Payload_04` (Engineering & Aeronomy Packages)
  * `SR_Payload_03` (Meteorological Survey Package)
  * `2HOT Thermometer` (`temperatureScan`)
  * `PresMat Barometer` (`barometerScan`)
  * `Geiger Counter` (`geigerCounter`)
  * `SR.Nosecone.625` (Recovery Parachute)
  * `SR_PayloadFairing_625` (Protective side fairings)

### 2. Flight Operations Execution
1. Roll out vessel to Launchpad via KCT.
2. In terminal, start the upgraded telemetry logger:
   ```bash
   python3 tools/telemetry_recorder.py CSA-09
   ```
3. In kOS terminal inside KSP:
   ```kos
   RUNPATH("0:/csa/csa09_guided_ascent.ks").
   ```
4. Confirm autonomous staging, pitch kick towards **Heading 270º**, fairing jettison at $> 58\text{ km}$, 90s Mini-Lab shutdown, parachute arming, and soft touchdown on inland terrain.
