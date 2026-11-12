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
      text: 🚀 View Flight CSA-20
      link: /missions/csa-20
    - theme: alt
      text: 🌐 Live Constellation
      link: /constellations/
    - theme: alt
      text: 🛰️ Corolt-IV Fleet
      link: /vehicles/corolt-4

features:
  - title: 🌐 COROLTNET-MKO & LEO CONSTELLATION
    details: Dual-ring equatorial relay network with 9 active satellites — 5/6 MKO-600 km backbone nodes (240° continuous arc, 1,327 km phased arrays) + 4 LEO-300 km mesh nodes.
  - title: 🔬 KERBALISM & YEAR 2 «NOVA SCIENTIA»
    details: High-rate LAN telemetry streaming, component reliability management, Van Allen radiation boundary, and deep-space comms readiness.
  - title: 💻 AUTONOMOUS kOS GUIDANCE v5.0
    details: Universal two-burn orbital ascent, quarter-rate pad fueling, sub-second sidereal launch windows (±0.08° record), and Zero-Debris Stage 2 deorbiting.
---

<div class="csa-stats-grid">
  <div class="csa-stat-card">
    <div class="csa-stat-val">9 Nodes</div>
    <div class="csa-stat-lbl">5 MKO-600 + 4 LEO-300</div>
  </div>
  <div class="csa-stat-card">
    <div class="csa-stat-val">601.2 km</div>
    <div class="csa-stat-lbl">Operational MKO Ring</div>
  </div>
  <div class="csa-stat-card">
    <div class="csa-stat-val">ΔΦ = -0.08°</div>
    <div class="csa-stat-lbl">CSA-20 Insertion Record</div>
  </div>
  <div class="csa-stat-card">
    <div class="csa-stat-val">kOS v5.0</div>
    <div class="csa-stat-lbl">Direct Sidereal Guidance</div>
  </div>
</div>

<div class="csa-home-viz-section">
  <h2 class="csa-home-viz-heading">🌐 LIVE COROLTNET CONSTELLATION TELEMETRY</h2>
  <ConstellationVisualizer />
</div>

<style>
.csa-home-viz-section {
  max-width: 1152px;
  margin: 2.5rem auto 1rem;
  padding: 0 1.5rem;
}

.csa-home-viz-heading {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #f8fafc;
  text-align: center;
  border-top: none !important;
  margin-bottom: 0.5rem;
}
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
