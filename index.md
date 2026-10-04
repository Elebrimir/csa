---
layout: home

hero:
  name: "COROLT SPACE AGENCY"
  text: "AD ASTRA PER SCIENTIAM"
  tagline: "Advanced aerospace engineering, high-fidelity telemetry, and autonomous kOS guidance."
  image:
    src: /assets/flag.png
    alt: Corolt Space Agency Flag
  actions:
    - theme: brand
      text: 🚀 View Flight CSA-07
      link: /missions/csa-07
    - theme: alt
      text: 📡 Corolt-III Fleet
      link: /vehicles/corolt-3

features:
  - title: 🌌 SUBORBITAL & ORBITAL CONQUEST
    details: High-altitude space exploration (245 km), gravity turn ascent profiles, and autonomous CoroltNet constellation.
  - title: 🔬 KERBALISM REALISM & LIFE SUPPORT
    details: Real-time science transmission, Mach 5+ aerothermal heating, Van Allen radiation belts, and strict power budgeting.
  - title: 💻 AUTONOMOUS kOS CONTROL & TELEMETRY
    details: Ground-independent KerboScript flight execution and continuous high-rate multivariable telemetry streams.
---

<div class="csa-stats-grid">
  <div class="csa-stat-card">
    <div class="csa-stat-val">245.0 km</div>
    <div class="csa-stat-lbl">Altitude Record (Apoapsis)</div>
  </div>
  <div class="csa-stat-card">
    <div class="csa-stat-val">Mach 5.4</div>
    <div class="csa-stat-lbl">Hypersonic Velocity</div>
  </div>
  <div class="csa-stat-card">
    <div class="csa-stat-val">100 %</div>
    <div class="csa-stat-lbl">Autonomous Recovery</div>
  </div>
  <div class="csa-stat-card">
    <div class="csa-stat-val">kOS v1.0</div>
    <div class="csa-stat-lbl">Programmable Avionics</div>
  </div>
</div>

<style>
.csa-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  max-width: 1152px;
  margin: 3rem auto 1rem;
  padding: 0 1.5rem;
}

.csa-stat-card {
  background: linear-gradient(135deg, rgba(12, 19, 36, 0.8) 0%, rgba(6, 10, 20, 0.95) 100%);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 10px;
  padding: 1.5rem 1rem;
  text-align: center;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.csa-stat-card:hover {
  transform: translateY(-4px);
  border-color: #00e5ff;
}

.csa-stat-val {
  font-family: 'Orbitron', sans-serif;
  font-size: 2rem;
  font-weight: 900;
  color: #00e5ff;
  letter-spacing: 0.05em;
  text-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
}

.csa-stat-lbl {
  font-size: 0.85rem;
  text-transform: uppercase;
  color: #94a3b8;
  letter-spacing: 0.08em;
  margin-top: 0.5rem;
  font-weight: 600;
}
</style>
