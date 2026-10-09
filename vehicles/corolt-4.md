# 🚀 Next-Generation Quasiorbital Launcher: Corolt-IV (Vector-IV)

> *"The historic leap from solid-fueled sounding rockets to controlled liquid propulsion. Engineered to achieve orbital velocity ($> 2,200\text{ m/s}$) and deliver the Corolt Space Agency's inaugural artificial satellite into Low Kerbin Orbit (LKO)."*

---

## 📐 Strategic Architecture & Program Transition

Following the culmination of the Corolt-III / Vector-III sounding rocket campaign with **Mission CSA-10**, the CSA Flight Operations Directorate has officially decreed the closure of the solid-propellant sounding lineage:
* **Vector-III Fleet Retirement**: Production of subsequent Corolt-IIIb units (including *Booster 11*) has been canceled in the Kerbal Construction Time (KCT) queue.
* **Vector-IV (Corolt-IV) Authorization**: R&D funds totaling $> 75\text{ science points}$ have been earmarked to unlock the foundational liquid rocketry branches:
  * `gptt_liquidFueledRockets` & `gptt_tank1`: 1.25m and 0.625m liquid propellant tanks and tail assemblies.
  * `gptt_liquid0`: High-thrust sea-level booster engines (*LV-T15 Valiant*, *Etoh-340 Feldspar*, *Easton-50 Viking*).
  * `gptt_liquidVac0` & `gptt_liquid1`: Upper stage vacuum-optimized restartable engines (*Belle-RLX81 Agena*, *Alpha JA10 Able*).

```text
EVOLUTION TIMELINE:
[Corolt-I (0.35m Sounding)] ➔ [Corolt-II (Unguided)] ➔ [Corolt-IIIb (Guided Solids)] ➔ 🚀 [COROLT-IV (Liquid Quasiorbital)]
```

---

## ⚙️ Preliminary Engineering Specifications (Vector-IV Baseline)

| Design Parameter | Preliminary Value | Engineering Rationale |
| :--- | :--- | :--- |
| **Manufacturer** | Corolt Space Agency (CSA) | Kerbin Space Center Design Bureau |
| **Vehicle Class** | Two-Stage Inline Liquid Launch Vehicle | Quasiorbital / Low Kerbin Orbit (LKO) |
| **Gross Launch Mass** | **~12.5 – 15.0 t (12,500 – 15,000 kg)** | Scaled for orbital energy requirements |
| **Base Diameter (Stage 1)**| **1.25 m** | Standard aerodynamically streamlined airframe |
| **Upper Diameter (Stage 2)**| **0.625 m / 0.9375 m** | High-expansion vacuum optimized stage |
| **Stage 1 Propulsion** | **LV-T15 'Valiant' or Etoh-140/340 Series** | Liquid Fuel + Oxidizer with gimbal thrust vector control |
| **Stage 2 Propulsion** | **Belle-RLX81 (Agena) or JA10 'Alpha' (Able)**| High $I_{sp}$ ($> 310\text{ s}$) in vacuum with multiple re-ignitions |
| **Payload Capacity to LKO**| **250 – 400 kg** | Orbital science satellites, comm relays, recover capsules |
| **Guidance System** | **kOS Autonomous Flight Computer + Reaction Wheels**| True orbital insertion guidance (`launch_to_orbit.ks`) |
| **Electrical Architecture**| **High-Efficiency Solar Panels + Rechargeable Banks** | Unlimited orbital operational lifetime |

---

## 🎯 Primary Operational Capabilities

### 1. Gimbal Thrust Vector Control (TVC)
Unlike the Corolt-IIIb which depended entirely on atmospheric aerodynamic fins for attitude control (losing steering authority above 40 km), the Corolt-IV incorporates **gimbaled liquid engines**. This provides continuous, high-authority steering throughout the entire vacuum ascent, enabling precise gravity turn profiles and zero AoA flight through Max Q.

### 2. Vacuum Restart & Circularization
Solid rocket motors cannot be throttled or extinguished once ignited. The Corolt-IV's liquid upper stage allows the flight computer to cut off thrust at apogee injection, coast ballistically to peak altitude, and execute a dedicated **circularization burn** ($\Delta v \approx 400 - 600\text{ m/s}$) to close the orbit.

### 3. Extended Orbital Science Missions
With the capability to sustain closed orbits at $80\times 80\text{ km}$ or $120\times 120\text{ km}$:
* Sustained space radiation experiments over multiple planetary orbits.
* Deployment of the inaugural **Corolt CommNet Constellation** for unbroken global communications.
* Atmospheric entry capsule recovery tests with ablative heat shielding.

---

## 📋 Program Milestones & Rollout Schedule

1. **Phase 1 (Post CSA-10)**: Unlock liquid rocketry and propellant tank nodes at KSC R&D Center.
2. **Phase 2**: VAB construction and Kronal Vessel Viewer (KVV) orthographic blueprint generation.
3. **Phase 3**: Static fire test of Stage 1 liquid powerpack on the launchpad.
4. **Phase 4**: **Mission CSA-11** — Maiden suborbital qualification and high-velocity reentry test of Vector-IV.
5. **Phase 5**: **Mission CSA-12** — Inaugural orbital launch attempt (*Orbital Vanguard-1*).
