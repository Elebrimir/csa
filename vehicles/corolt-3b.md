# 🚀 Active-Guidance Suborbital Launcher: Corolt-IIIb (CSA-07)

> *"Direct evolution of the Corolt-III fitted with aerodynamic control surfaces on both stages, empowering kOS to execute automated pitch kick maneuvers and downrange guidance toward the East."*

---

## 📐 General Technical Specifications

| Design Parameter | Engineering Value |
| :--- | :--- |
| **Manufacturer** | Corolt Space Agency (CSA) |
| **Vehicle Type** | Multi-Stage Inline Suborbital Launcher with Active Guidance |
| **Base Diameter (Stage 1)** | **1.25 m** (RT-10 «Hammer» Booster with thrust calibrated to 46%) |
| **Upper Diameter (Stage 2)** | **0.625 m** (Solid Rocket Motor SRM-XL) |
| **Gross Launch Mass** | **5.199 t (5,199 kg)** |
| **Payload Dry Mass** | **0.629 t (629 kg)** |
| **Recovered Mass at Splashdown** | **0.3015 t (301.5 kg)** |
| **Total Construction Cost** | **9,775.5 funds** |
| **Recovered Value at VAB Warehouse** | **7,301.0 funds** (74.7% economic return rate) |
| **Active Control Surfaces** | 4x `bluedog.Redstone.Fin.CtrlSurf` (Stage 1) + 4x `bluedog.Scout.Algol.Fin` (Stage 2) |
| **Recovery System** | Conical nosecone with integrated parachute `SR.Nosecone.625` |

---

## 🕹️ Flight Control System & Dynamics

Unlike the baseline Corolt-III (which relied on unguided fixed fins incapable of altering trajectory), the **Corolt-IIIb** variant integrates:
* **First Stage (Hammer)**: 4 Redstone-style movable fins (*Etoh-CS*) providing full yaw, pitch, and roll control during the dense atmospheric ascent.
* **Second Stage (SRM-XL)**: 4 Algol-style actuated fins (*Dioscuri-AFD1*) holding pitch attitude at 80º–82º up to 35–40 km altitude.
* **Flight Computer (kOS)**: Runs the autonomous ascent guidance program `corolt3_guided_ascent.ks` with onboard contingency handling `emergency_recovery.ks`.

---

## 🔬 Scientific Suite & Recoverable Payload

The complete upper section is housed inside an open 0.625m truss `SR.PayloadTruss.625`:
* ⏱️ **Atmospheric Pressure PresMat (`sensorBarometer`)**
* 🌡️ **Temperature 2HOT (`sensorThermometer`)**
* 🌪️ **Meteorological Survey Package (`SR.Payload.01`)**
* 🧪 **Aeronomy Sensor Array (`SR.Payload.02`)**
* ⚙️ **Engineering & Stress Package (`SR.Payload.04`)**
* 📡 **Advanced Sounding Package (`SR.Payload.03`)**
* ⚡ **Electrical Storage**: 100 EC battery (`batteryBankMini`) + 2x `nfex-battery-mini-1` (250 EC total).
* 💾 **CSA Avionics**: 2x `SR.ProbeCore` (32 MB each, 64 MB total).

---

## 📈 Calibrated Aerodynamic Drag Profile ($C_d \cdot A$)

Empirically extracted from high-fidelity telemetry during flight **CSA-07**:
* **Median Effective $C_d \cdot A$**: **1.727 m²**
* **Subsonic Regime (< Mach 0.8)**: 1.468 m²
* **Transonic Peak (Mach 0.8 – 1.2)**: 2.331 m²
* **Supersonic Regime (Mach 1.2 – 2.5)**: 1.813 m²
* **Hypersonic Regime (> Mach 4.5)**: 1.640 m²

---

## 📋 Operational Conclusion & History

The vehicle completed its operational debut with flying colors on mission **CSA-07** (Year 1, Day 65), soaring to 138.6 km and traveling over 315 km downrange. The instrument capsule performed a gentle ocean splashdown and was recovered in pristine condition into the VAB warehouse, recouping 74.7% of total construction funds.

