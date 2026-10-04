# 🚀 Inline Heavy Launcher: Corolt-III (CSA-05)

> *"Next-generation high-altitude launcher of the CSA, engineered with a purely tandem (inline) architecture to conquer the lower atmosphere and assault the upper layers of Kerbin."*

![Corolt-III General Blueprint KVV 1](../assets/vehicles/corolt-3_blueprint_1.png)

---

## 📐 General Technical Specifications

| Design Parameter | Engineering Value |
| :--- | :--- |
| **Manufacturer** | Corolt Space Agency (CSA) |
| **Vehicle Type** | Multi-Stage Inline (Tandem) Suborbital Launcher |
| **Base Diameter (Stage 1)** | **1.25 m** (RT-10 «Hammer» Booster) |
| **Upper Diameter (Stage 2)** | **0.625 m** (SRM-XL Motor + `SR.PayloadTruss.625` Open Cage) |
| **Gross Launch Mass** | **5.144 t (5,144 kg)** |
| **Payload Dry Mass** | **0.629 t (629 kg)** |
| **Total Delta-v ($\Delta v$)** | **2,721 m/s (Sea Level) / 3,196 m/s (Vacuum)** |
| **Initial Sea-Level TWR** | **1.80** (Stage 1) $\rightarrow$ **2.09** (Stage 2) |
| **Stage 1 Burn Time** | **51.5 seconds** |
| **Stage 2 Burn Time** | **46.8 seconds** |
| **Stabilization** | 4 aft skirt fins `SR_Wing_01` (3,400 K) + 4 upper fins `SR_Wing_02` |
| **Recovery System** | Conical nosecone with integrated parachute `SR.Nosecone.625` |

---

## 🔬 Scientific Suite & Instrument Bay

Corolt-III debuts the new 0.625 m open instrument truss (`SR.PayloadTruss.625`), allowing environmental sensors direct exposure to the airstream as mandated by Kerbalism:
* ⏱️ **PresMat Barometer (`sensorBarometer`)**: High-accuracy dynamic and static pressure log.
* 🌡️ **2HOT Thermometer (`sensorThermometer`)**: Fast-response thermal sensor.
* 🌪️ **Meteorological Survey Package (`SR.Payload.01`)**: Atmospheric and wind measurement.
* 🧪 **Aeronomy Sensor Array (`SR.Payload.02`)**: Upper-layer air density and composition analysis.
* ⚡ **Expanded Electrical System**: `batteryBankMini` (100 EC) + 2x `nfex-battery-mini-1` (250 EC total).
* 💾 **Dual CSA Avionics**: 2x `SR.ProbeCore` patched to 32 MB onboard storage each (64 MB total).

---

## 🛠️ KVV Engineering Blueprints (Kronal Vessel Viewer)

### Exploded Staging Detail
![Corolt-III Exploded View 2](../assets/vehicles/corolt-3_blueprint_2.png)

### Science Truss & Payload Bay Section
![Corolt-III Instrument Bay 3](../assets/vehicles/corolt-3_blueprint_3.png)

### Structural & Aerodynamic Profile
![Corolt-III Structural Profile 4](../assets/vehicles/corolt-3_blueprint_4.png)

---

## 📋 Operational Conclusion
Corolt-III proved aerodynamic stability in its maiden flight during mission CSA-05, reaching 20.43 km despite an upper stage ignition anomaly. With thermal/reliability fixes applied and storage expanded to 32 MB, the launcher entered service for suborbital space missions in **CSA-05b** and beyond.


