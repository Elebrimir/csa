# 📋 Mission Report: CSA-05 «Corolt-III Maiden Flight»

* **Launch Date**: Year 1, Day 45 (05h 43m 28s)
* **Flight Director / Operations**: CSA Mission Control (Kerbin Launch Complex)
* **Launch Vehicle**: [Corolt-III (Tandem Architecture)](/vehicles/corolt-3)
* **Mission Status**: 🟢 UPPER ATMOSPHERE FLIGHT AND FULL PAYLOAD RECOVERY (+7.14 science points)

---

## 🎯 Mission Objectives
1. **Corolt-III Operational Debut**: Inaugurate heavy 100% inline (tandem) architecture with RT-10 «Hammer» (1.25 m) booster and SRM-XL (0.625 m) upper stage. *(Achieved)*
2. **Break Lower Atmosphere Frontier**: Cross the 18 km boundary for the first time in CSA history into the **Upper Atmosphere (`FlyingHigh`)** domain. *(Achieved - 20.43 km)*
3. **Multidisciplinary Atmospheric Profiling**: Simultaneous sampling of barometric pressure, ambient temperature, aeronomy, and meteorology. *(Achieved)*
4. **Recovery at KSC**: Stable ballistic reentry and parachute splashdown/landing adjacent to Space Center facilities. *(Achieved - 100% recovered)*

---

## 📊 Official Flight Telemetry (Recorded Data)

Captured in real time during flight via Telemachus telemetry downlink:

| Flight Parameter | Recorded Value CSA-05 | Status and Remarks |
| :--- | :--- | :--- |
| **Peak Altitude (Apoapsis)** | **20,432.3 m (20.43 km)** | 🟢 **New CSA Altitude Record** |
| **Maximum Surface Speed** | **470.9 m/s (1,695 km/h)** | 🟢 Exceeded Mach 1.5 in clean ascent |
| **Peak Dynamic Pressure (Max Q)** | **29,600.6 kPa** | 🟢 Impeccable structural rigidity |
| **Maximum Acceleration** | **3.10 G** | 🟢 Nominal structural load profile |
| **Parachute Deployment** | **1,600 m (Reefed) / 800 m (Full)** | 🟢 Gentle opening and deceleration |
| **Touchdown Velocity** | **5.9 m/s** | 🟢 Soft surface contact |
| **Total Recorded Flight Time** | **777.4 seconds (12 min 57 s)** | 🟢 Complete mission telemetry logged |
| **Landing Location** | KSC Grasslands (adjacent to runway) | 🟢 Immediate recovery |

---

### Flight Telemetry Plot (CSA-05)
![CSA-05 Telemetry Plot](../assets/csa-05_telemetry_plot.svg)

---

## 🔬 Scientific Yield & Memory Diagnosis

Despite a propulsion anomaly in the upper stage, the mission established major progress in high-altitude atmospheric science:
* **Entry into Upper Atmosphere (`FlyingHigh`)**: Crossing 18,000 meters altitude triggered the first verified scientific readings of Kerbin's upper atmosphere.
* **Recorded Data Volumes**:
  * ⏱️ BAROTRON Barometer (`sensorBarometer`): 0.4 MB recorded.
  * 🌪️ Meteorological Package (`SRExperiment01`): 0.6 MB recorded.
  * 🧪 Aeronomy Sensor (`SRExperiment02`): 0.5 MB recorded.
  * 📈 Avionics Telemetry: 0.8 MB recorded.
* **R&D Science Haul**: Full capsule recovery yielded **+7.14 net science points**, taking agency reserves to **10.09 points**!

> [!NOTE]
> **Engineering Memory Diagnosis:** Standard avionics units (2.00 MB each) saturated under the large datasets required by Aeronomy (5 MB) and continuous Barometer readings (3.5 MB). The official CSA engineering patch `csa_avionics.cfg` was deployed to provide **32 MB onboard hard drives** on future vehicles.

---

## ⚠️ Second Stage Anomaly Investigation

At T+55 seconds into ascent (13.7 km altitude, 453 m/s), flight telemetry recorded an anomaly:
* `[00:00:55]: SRM-XL Sounding Rocket Motor ignition failure`.
* The second-stage SRM-XL solid motor suffered an **ignition misfire** under Kerbalism engine reliability checks following clean separation from the lower booster.
* **Ballistic Design Triumph:** The initial impulse delivered by the RT-10 «Hammer» was so robust and vertical that purely on ballistic momentum, the vehicle coasted to **20,432 meters**, successfully achieving the high-altitude science goal without the upper stage firing.

---

## 📸 Mission Vehicle
* [Complete Corolt-III Technical Specifications](/vehicles/corolt-3)

