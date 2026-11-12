# 🌐 CoroltNet: Dual-Ring Equatorial Satellite Constellation

The **CoroltNet** system is the flagship orbital telecommunications and science relay infrastructure of the Corolt Space Agency (CSA). Operating across two synchronized equatorial rings (**LEO at 300 km** and **MKO at 600 km**), the network currently comprises **9 active relay satellites** providing continuous inter-satellite cross-links and deep-space communications to the Kerbal Space Center (KSC).

---

## 🛰️ Live Interactive Orbital Tracker

<ConstellationVisualizer />

---

## 📊 Live Node Fleet Specifications

| Spacecraft | Launch Mission | Status | Altitude ($Ap \times Pe$) | Orbital Period | Relative Phase | Relay Antenna | CommNet Channel |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CoroltSat-1B** | [CSA-12](/missions/csa-12) | 🟢 **ACTIVE** | 311.49 × 300.02 km | 2,882.093 s (48.03 min) | 0.00° (LEO Slot 0 Anchor) | Codac-A23 (650 km Relay) | `CoroltSat-LEO` (100) |
| **CoroltSat-1D** | [CSA-14](/missions/csa-14) | 🟢 **ACTIVE** | 308.33 × 303.24 km | 2,882.251 s (48.04 min) | +34.57° (LEO Slot 1) | Codac-A23 (650 km Relay) | `CoroltSat-LEO` (100) |
| **CoroltSat-1E** | [CSA-15](/missions/csa-15) | 🟢 **ACTIVE** | 302.62 × 299.59 km | 2,859.949 s (47.67 min) | -9.73° (LEO Slot 2) | Codac-A23 (650 km Relay) | `CoroltSat-LEO` (100) |
| **CoroltSat-1C** | [CSA-13](/missions/csa-13) | 🟢 **ACTIVE** | 308.79 × 302.65 km | 2,881.922 s (48.03 min) | +129.00° (LEO Slot 3) | Codac-A23 (650 km Relay) | `CoroltSat-LEO` (100) |
| **CoroltSat-1F** | [CSA-16](/missions/csa-16) | 🟢 **ACTIVE** | 601.15 × 598.88 km | 4,395.164 s (73.25 min) | 0.00° (MKO Node 0 Anchor) | 3x Codac-A23 (1,327 km Array) | `CoroltNet-MKO` (101) |
| **CoroltSat-1G** | [CSA-17](/missions/csa-17) | 🟢 **ACTIVE** | 601.15 × 598.93 km | 4,395.282 s (73.25 min) | +59.16° (MKO Node 1) | 3x Codac-A23 (1,327 km Array) | `CoroltNet-MKO` (101) |
| **CoroltSat-1H** | [CSA-18](/missions/csa-18) | 🟢 **ACTIVE** | 601.14 × 598.89 km | 4,395.165 s (73.25 min) | +120.08° (MKO Node 2) | 3x Codac-A23 (1,327 km Array) | `CoroltNet-MKO` (101) |
| **CoroltSat-1I** | [CSA-19](/missions/csa-19) | 🟢 **ACTIVE** | 601.16 × 598.88 km | 4,395.178 s (73.25 min) | +179.46° (MKO Node 3 Antipode) | 3x Codac-A23 (1,327 km Array) | `CoroltNet-MKO` (101) |
| **CoroltSat-1J** | [CSA-20](/missions/csa-20) | 🟢 **ACTIVE** | 601.15 × 598.90 km | 4,395.204 s (73.25 min) | +239.92° (MKO Node 4 Record) | 3x Codac-A23 (1,327 km Array) | `CoroltNet-MKO` (101) |
| **CoroltSat-1K** | *CSA-21* | ⏳ **QUEUED** | 600.00 × 600.00 km | 4,395.164 s (Target) | +300.00° (MKO Node 5) | 3x Codac-A23 (1,327 km Array) | `CoroltNet-MKO` (101) |
---

## 🌐 CoroltNet-MKO: Medium Kerbin Orbit Backbone (600 km)

Inaugurated by **Mission CSA-16**, **CoroltNet-MKO** represents the high-altitude deep-space communications backbone of the Corolt Space Agency:
* **Nominal Architecture**: 6-satellite regular hexagon at **600.0 km circular equatorial orbit** ($\Delta \theta = 60.0^\circ$).
* **Payload Power**: 3x Codac-A23 high-gain microwave relays operating in an omnidirectional phased array ($D_{\max} > 1,327\text{ km}$).
* **Inter-Satellite Geometry**: Adjacent chord distance $d = 1,200.0\text{ km}$, clearing Kerbin's surface by **$439.2\text{ km}$** with zero planetary occlusion.
* **Drift Suppression**: Operational period locked to $T = 4,395.23\text{ s}$ ($+0.09\text{ s}$ delta), suppressing natural drift to less than $0.036^\circ\text{/day}$.

---

## 📐 Constellation Geometry & Line-of-Sight Physics

### 1. Inter-Satellite Range vs. Antenna Power (40.0° Mesh Spacing)
In a circular orbit with radius $R_{\text{orb}} = R_{\text{Kerbin}} + h = 600\text{ km} + 301\text{ km} = 901\text{ km}$, the Euclidean line-of-sight distance (chord length $d$) between two nodes separated by an angular distance $\Delta \theta$ is:

$$d = 2 \cdot R_{\text{orb}} \cdot \sin\left(\frac{\Delta \theta}{2}\right)$$

For the nominal constellation design spacing ($\Delta \theta = 40.0^\circ$):

$$d = 2 \cdot 901\text{ km} \cdot \sin(20.0^\circ) = 1,802\text{ km} \cdot 0.34202 = \mathbf{616.4\text{ km}}$$

Because the effective relay power of the Codac-A23 omnidirectional relay is **650.0 km**:

$$d = 616.4\text{ km} < 650.0\text{ km} \quad \Longrightarrow \quad 100\% \text{ Link Margin}$$

Adjacent nodes maintain permanent direct microwave cross-links without requiring directional dish tracking.

### 2. Horizon Clearance & Planetary Occlusion
Kerbin has an equatorial radius of $R_{\text{Kerbin}} = 600\text{ km}$. From a 301 km orbital altitude, the maximum angular line-of-sight horizon before the planetary sphere occludes the signal is:

$$\alpha = \arccos\left(\frac{R_{\text{Kerbin}}}{R_{\text{orb}}}\right) = \arccos\left(\frac{600}{901}\right) \approx 48.2^\circ$$

$$\Delta \theta_{\max} = 2 \alpha \approx \mathbf{96.4^\circ}$$

At $\Delta \theta = 40.0^\circ$, the inter-satellite line of sight passes **246 km above Kerbin's surface**, well outside the exosphere (70 km), completely eliminating atmospheric plasma degradation or terrain shadowing.

### 3. Interleaved Deployment Strategy
To guarantee immediate mission utility while the full 9-node ring is assembled:
1. **Phase 1 (Equatorial Triangulation)**: Nodes at 0.0° (`1B`), +120.0°, and +240.0° provide global ground station coverage to every sector of Kerbin.
2. **Phase 2 (Mesh Ring Closure)**: Subsequent launches fill the 40.0° intervals (+40.0°, +80.0°, +160.0°, +200.0°, +280.0°, +320.0°) to establish the continuous closed-loop relay mesh ring.

---

## 🛠️ Ground Station Network Integration (DSN)

* **Primary DSN Hub**: Kerbal Space Center (KSC) — Lat 0.0°, Lon 0.0°
* **Frequency Tuning**: Frequency Channel `100` (`CoroltSat-LEO`) and Channel `101` (`CoroltNet-MKO`)
* **Redundancy Protocol**: Ground station tracking automated via CommNet Constellation scenario routing. When line-of-sight to KSC is lost on the night-side hemisphere, signals hop across adjacent nodes to route science telemetry back to Mission Control in real time.

