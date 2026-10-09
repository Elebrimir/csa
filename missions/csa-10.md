# 📋 Mission Profile & Flight Plan: CSA-10 «Boreal Shoreline & Van Allen Penetration»

* **Mission Code**: `CSA-10`
* **Flight Director**: CSA Mission Control (Kerbin Space Center)
* **Launch Vehicle**: [Corolt-IIIb (Upgraded 800 EC Upper Stage)](/vehicles/corolt-3b)
* **Target Altitude**: **> 400 km** (Deep Space & Van Allen Belt Core)
* **Target Trajectory**: **Heading 005.0º NNE** (Coastal Polar Corridor)
* **Status**: 🟡 PRE-FLIGHT READINESS / LAUNCH CAMPAIGN ACTIVE

---

## 🎯 Mission Objectives

1. **Northbound Coastal Polar Flight Corridor (Heading 005.0º NNE)**:
   * Direct active guidance along **Heading 005.0º (North-North-East)** following Kerbin's eastern continental shoreline.
   * **Eliminate Retrograde Drag**: Completely abandon the westward retrograde heading flown on CSA-09, preserving the full $+174.5\text{ m/s}$ eastward rotational velocity as inertial momentum.
   * Guarantee that stage impact and payload recovery remain strictly within the coastal maritime corridor, preventing vessel crash onto inland mountains.
2. **Deep Outer Space Penetration (> 400 km)**:
   * Maximize ballistic apogee to plunge deep through the Van Allen radiation belt threshold (> 250 km) to collect the inaugural High Space radiation telemetry.
3. **Multi-Layer Dual-Burst Scientific Survey**:
   * Exploit the 800 EC upper stage battery pack with targeted instrument duty-cycling:
     * **Burst 1 (Upper Atmosphere 18–70 km)**: Run the Materials Mini-Lab (`2.04 EC/s`) for **30 seconds** during supersonic climb.
     * **Burst 2 (Low Space > 70 km)**: Run the Materials Mini-Lab for **90 seconds** in microgravity vacuum.
     * **Continuous Sensors**: Record continuous PresMat barometric pressure, Geiger radiation count, and micrometeorite impacts across all atmospheric and space regimes.
4. **Aerothermal Prograde Shielding & Subsonic Reentry Backflip**:
   * **Prograde Heat-Shielding**: Upon atmospheric entry ($< 70\text{ km}$), orient the craft strictly nosecone-first (`LOCK STEERING TO SRFPROGRADE`) to shield the lateral battery packs and scientific instruments behind the conical shock wave during hypersonic deceleration.
   * **Subsonic Backflip**: Once the atmosphere decelerates the vehicle to safe subsonic velocities ($< 280\text{ m/s}$ / $< 6,000\text{ m}$), execute an autonomous **180º backflip** to retrograde (`LOCK STEERING TO SRFRETROGRADE`), placing the nosecone into the trailing wake for clean, thermal-free parachute deployment.
5. **Autonomous Avionics & Parachute Reserve Protection**:
   * Enforce an inviolable **100 EC battery safety floor** in kOS to guarantee 100% powered avionics, real-time CommNet telemetry streaming, and automated parachute arming.
6. **Precision Coastal Splashdown & Naval Recovery**:
   * Touch down via `SR.Nosecone.625` parachute in the calm waters of the northern boreal bay ($\approx \text{Lat } +47.6^\circ\text{N}, \text{Lon } -74.7^\circ\text{W}$), $\sim 499\text{ km}$ downrange from KSC for immediate recovery ship salvage.

---

## 📊 Pre-Flight 3D Numerical Simulation & Trajectory Baseline

Simulated using high-precision 4th-order Runge-Kutta numerical integration in 3D rotating spherical coordinates (ECEF/ECI), accounting for Kerbin's exact sidereal rotation period ($21,549.4\text{ s}$), spherical Coriolis and centrifugal accelerations, and empirically calibrated aerodynamic drag ($C_d \cdot A = 0.963\text{ m}^2$):

| Flight Parameter | Pre-Flight Simulated Value | Operational Remarks |
| :--- | :--- | :--- |
| **Launch Azimuth / Heading** | **005.0º (North-North-East)** | Aligned with eastern continental coastline |
| **Pitch Kick Altitude** | **2,500 m** | Transition to 88.0º, descending smoothly to 54.0º at 45 km |
| **Stage 1 Burnout (RT-10 Hammer)** | **T+50.7 s @ 12.1 km** | Staging decoupler fires at $v \approx 540\text{ m/s}$ |
| **Stage 2 Burnout (SRM-XL)** | **T+109.8 s @ 62.4 km** | Active propulsion complete ($v_{surf} \approx 2,106\text{ m/s}$) |
| **Fairing Jettison** | **T+110 s (> 58 km)** | Unshrouds payload truss in vacuum |
| **Peak Apoapsis (Apogee)** | **415.51 km** | 🟢 **Deep Outer Space / Van Allen Core penetrated!** |
| **Time in Space (> 70 km)** | **~960 s (16.0 min)** | Extended microgravity and radiation sampling window |
| **Total Flight Duration** | **1,500.1 s (25.0 min)** | Complete ascent and soft parachute descent |
| **Downrange Distance** | **499.2 km along coast** | Northward travel following the -74.6º meridian axis |
| **Touchdown Coordinates** | **Lat +47.57º N, Lon -74.65º W** | Coastal waters of northern boreal gulf |
| **Final Battery at Touchdown** | **367.0 / 800.0 EC (45.9%)** | 🟢 **Large reserve safety margin over 100 EC floor!** |

### Pre-Flight Simulated Ascent & Electrical Power Curve
![CSA-10 Simulated Ascent](../assets/csa-10_simulated_ascent.svg)

---

## 🗺️ KAA Airspace Hazard & Maritime Exclusion Corridor Notice (NOTAM)

The **Kerbal Aviation Administration (KAA)** has published the official Airspace and Surface Hazard Notice for Mission **CSA-10**:

![KAA Airspace and Surface Hazard Map CSA-10](../assets/csa-10_faa_hazard_map.svg)

### KAA Mission Notices & Flight Directives:
* **NOTAM Reference**: `KAA-CSA10-2026-10` (Effective Window: Y1-D92).
* **Launch Azimuth**: $005.0\text{º}$ (Coastal Corridor Northward).
* **Hazard Zone 1 (Booster Debris Area)**: Designated drop sector at $\text{Lat } +1.4\text{º N}, \text{Lon } -74.5\text{º W}$ for the jettisoned RT-10 Hammer casing ($T+51\text{ s}$).
* **Primary Recovery Zone (Maritime)**: Parachute touchdown footprint at $\text{Lat } +47.6\text{º N}, \text{Lon } -74.7\text{º W}$ in northern coastal waters.
* **Corridor Clearance**: All civil commercial air traffic along the North-South eastern airways is diverted during the 30-minute launch window.

---

## 🔬 Scientific Yield Objectives & Target Return

Mission CSA-10 addresses high-priority scientific samples identified in the [Kerbin Science Matrix](/science/):

| Instrument / Experiment | Environmental Regime | Target Biome | Target Science Yield | Status & Execution Plan |
| :--- | :--- | :--- | :---: | :--- |
| **Bahía de Materiales (Mini-Lab)** | Upper Atmosphere (18 - 70 km) | `Global` | **+9.53 pts** | 30s duty cycle during high-speed atmospheric exit |
| **Bahía de Materiales (Mini-Lab)** | Low Space (70 - 250 km) | `Global` | **+9.22 pts** | 90s exposure at microgravity apogee |
| **Baròmetre PresMat** | Low Space (70 - 250 km) | `Global` | **+5.40 pts** | First vacuum pressure calibration |
| **Baròmetre PresMat** | Upper Atmosphere (18 - 70 km) | `Global` | **+3.68 pts** | Transonic aerodynamic boundary layer scan |
| **Baròmetre PresMat** | Low Atmosphere (0 - 18 km) | `Shores` | **+3.21 pts** | Sea-level baseline at liftoff |
| **Contador Geiger (Kerbalism)** | High Space (> 250 km) | `Global` | **+6.00 pts** | Van Allen belt inner core radiation scan |
| **Contador Geiger (Kerbalism)** | Low Space (70 - 250 km) | `Global` | **+4.50 pts** | Exospheric background baseline |
| **Sensor de Micrometeorits** | Low Space (70 - 250 km) | `Global` | **+3.59 pts** | Outer orbital dust flux recording |
| **TOTAL PROJECTED HARVEST** | | | **~35 - 45 pts** | **Propels CSA Science Pool to > 110 pts!** |

---

## ⚡ Electrical Power Budget (800 EC Bank)

| Flight Phase | Duration | Active Systems | Drain Rate | Power Consumed | Remaining Battery |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Boost Phase (0–110s)** | 110 s | Avionics, kOS, Sensors, SAS reaction wheel | 0.45 EC/s | 49.5 EC | **750.5 EC** |
| **Upper Atmo Mini-Lab Run** | 30 s | Mini-Lab active (2.04) + Base avionics (0.10) | 2.14 EC/s | 64.2 EC | **686.3 EC** |
| **Space Entry & Coast** | 40 s | Base idle: Avionics + kOS (SAS OFF!) | 0.10 EC/s | 4.0 EC | **682.3 EC** |
| **Low Space Mini-Lab Run** | 90 s | Mini-Lab active (2.04) + Base idle (0.10) | 2.14 EC/s | 192.6 EC | **489.7 EC** |
| **Van Allen Coast to Apogee** | 600 s | Base idle (kOS + Avionics + Geiger sensor) | 0.10 EC/s | 60.0 EC | **429.7 EC** |
| **Atmospheric Reentry (70–3 km)**| 120 s | Base idle + Aeronomy & PresMat packages | 0.20 EC/s | 24.0 EC | **405.7 EC** |
| **Parachute Terminal Descent** | 500 s | Avionics + Recovery Beacon + Parachute | 0.08 EC/s | 40.0 EC | **365.7 EC RESERVE!** 🟢 |

---

## 🚀 Pre-Flight Operational Checklist

### 1. Vehicle Assembly & Rollout (KCT)
* [x] **Booster Assembly**: `CoroltIIIb - Booster 10` retrieved from VAB Warehouse (100% complete).
* [x] **Upper Stage**: `Corolt III B Sup 10` assembled with dual battery upgrade (**800 EC total**).
* [x] **KCT Decision**: **Cancel construction of Booster 11** to pivot to Vector-IV.
* [ ] Roll out stack to Launch Pad.

### 2. Launch Execution Sequence
1. In flight operations terminal:
   ```bash
   cd /home/pablo-cortes/Documents/Corolt_Space_Agency
   python3 tools/telemetry_recorder.py CSA-10
   ```
2. In the kOS terminal on board the vessel:
   ```kos
   RUNPATH("0:/csa/csa10_guided_ascent.ks").
   ```
3. Verify autonomous liftoff, pitch kick at $2,500\text{ m}$ toward **Heading 005.0º**, 30s Upper Atmosphere Mini-Lab burst, Stage 2 burnout, SAS shutoff, fairing jettison at $> 58\text{ km}$, 90s Low Space Mini-Lab burst, Van Allen entry at $> 250\text{ km}$, apogee at $\sim 415\text{ km}$, parachute pre-arming at $15\text{ km}$, and splashdown in northern coastal waters.
