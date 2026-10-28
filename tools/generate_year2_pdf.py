#!/usr/bin/env python3
"""
generate_year2_pdf.py
Generates an executive NASA / SpaceX style PDF report for the Corolt Space Agency:
Program «Nova Scientia» — Kerbin Year 2 Science Campaign & Flight Manifest Proposal.
Strict 6-page professional aerospace formatting with zero orphaned sections.
"""

import os
import sys
import base64
import subprocess

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    assets_dir = os.path.join(root_dir, "assets")
    flag_path = os.path.join(assets_dir, "flag.png")
    logo_path = os.path.join(assets_dir, "logo.jpg")

    flag_b64 = ""
    if os.path.exists(flag_path):
        with open(flag_path, "rb") as f:
            flag_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")

    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

    html_template = """<!DOCTYPE html>
<html lang="ca">
<head>
<meta charset="UTF-8">
<title>CSA — Programa Nova Scientia: Proposta Any Kerbin 2</title>
<style>
  @page {
    size: A4 portrait;
    margin: 14mm 14mm 14mm 14mm;
  }

  *, *:before, *:after {
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.38;
    font-size: 8.8pt;
    margin: 0;
    padding: 0;
  }

  .page-break {
    page-break-before: always;
    break-before: page;
  }

  .avoid-break {
    page-break-inside: avoid;
    break-inside: avoid;
  }

  /* Running Header & Footer */
  .running-header {
    border-bottom: 1.5px solid #0b3d91;
    padding-bottom: 4px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 7pt;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #64748b;
    font-weight: 600;
  }

  .running-footer {
    border-top: 1px solid #e2e8f0;
    padding-top: 4px;
    margin-top: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 7pt;
    color: #94a3b8;
  }

  /* Cover Page */
  .cover {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 10px 0 5px 0;
  }

  .cover-top {
    border-bottom: 3px solid #0b3d91;
    padding-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .cover-logo-area {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .cover-logo-img {
    height: 52px;
    width: auto;
    border-radius: 4px;
  }

  .cover-agency-title {
    font-size: 13.5pt;
    font-weight: 800;
    color: #0b3d91;
    letter-spacing: 1px;
    text-transform: uppercase;
    line-height: 1.1;
  }

  .cover-agency-sub {
    font-size: 7.5pt;
    color: #475569;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-weight: 600;
    margin-top: 3px;
  }

  .doc-badge {
    background-color: #0b3d91;
    color: #ffffff;
    font-size: 7pt;
    font-weight: 700;
    padding: 4px 8px;
    border-radius: 3px;
    letter-spacing: 0.8px;
    text-align: right;
    line-height: 1.3;
  }

  .cover-hero {
    margin: 25px 0 10px 0;
  }

  .cover-pre-tag {
    display: inline-block;
    background-color: #e0f2fe;
    color: #0369a1;
    font-weight: 700;
    font-size: 7.5pt;
    padding: 3px 8px;
    border-radius: 3px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  .cover-title {
    font-size: 23pt;
    font-weight: 900;
    color: #0a2540;
    line-height: 1.15;
    margin: 0 0 10px 0;
    letter-spacing: -0.5px;
  }

  .cover-subtitle {
    font-size: 10.5pt;
    color: #334155;
    line-height: 1.45;
    font-weight: 400;
    max-width: 95%;
    margin: 0 0 16px 0;
  }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin: 16px 0;
  }

  .kpi-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #0b3d91;
    padding: 8px 10px;
    border-radius: 4px;
  }

  .kpi-val {
    font-size: 14pt;
    font-weight: 800;
    color: #0a2540;
    line-height: 1.1;
  }

  .kpi-label {
    font-size: 6.8pt;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    margin-top: 3px;
  }

  .cover-meta-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 18px;
    font-size: 7.8pt;
  }

  .cover-meta-table td {
    padding: 5px 8px;
    border: 1px solid #cbd5e1;
  }

  .cover-meta-label {
    background-color: #f1f5f9;
    font-weight: 700;
    color: #334155;
    width: 25%;
  }

  .cover-motto {
    font-style: italic;
    color: #64748b;
    font-size: 8pt;
    text-align: center;
    border-top: 1px solid #e2e8f0;
    padding-top: 8px;
  }

  /* Section Headings */
  h1 {
    font-size: 12pt;
    font-weight: 800;
    color: #0a2540;
    margin: 0 0 6px 0;
    border-bottom: 2px solid #0b3d91;
    padding-bottom: 3px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  h2 {
    font-size: 10pt;
    font-weight: 700;
    color: #0b3d91;
    margin: 10px 0 4px 0;
  }

  p {
    margin: 0 0 6px 0;
    text-align: justify;
  }

  /* Data Tables */
  table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0 10px 0;
    font-size: 7.2pt;
  }

  table.data-table th {
    background-color: #0a2540;
    color: #ffffff;
    padding: 4px 6px;
    font-weight: 700;
    text-align: left;
    border: 1px solid #0a2540;
    font-size: 6.8pt;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  table.data-table td {
    padding: 3.5px 6px;
    border: 1px solid #e2e8f0;
    vertical-align: middle;
  }

  table.data-table tr:nth-child(even) {
    background-color: #f8fafc;
  }

  .tag {
    display: inline-block;
    padding: 1.5px 5px;
    border-radius: 3px;
    font-size: 6.2pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  .tag-kick { background-color: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd; }
  .tag-sci { background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
  .tag-flag { background-color: #fce7f3; color: #be185d; border: 1px solid #fbcfe8; }
  .tag-success { background-color: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }

  .callout {
    background-color: #f0fdf4;
    border-left: 3.5px solid #16a34a;
    padding: 6px 9px;
    margin: 6px 0;
    border-radius: 0 3px 3px 0;
    font-size: 7.6pt;
  }

  .callout-blue {
    background-color: #eff6ff;
    border-left: 3.5px solid #2563eb;
    padding: 6px 9px;
    margin: 6px 0;
    border-radius: 0 3px 3px 0;
    font-size: 7.6pt;
  }

  .callout-title {
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 2px;
  }

  /* Sign-off Block */
  .sign-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-top: 10px;
  }

  .sign-box {
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    border-radius: 4px;
    padding: 7px 10px;
    position: relative;
  }

  .sign-title {
    font-size: 6.8pt;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .sign-name {
    font-size: 9pt;
    font-weight: 800;
    color: #0a2540;
    margin: 2px 0 1px 0;
  }

  .sign-role {
    font-size: 7pt;
    color: #64748b;
  }

  .sign-line {
    border-top: 1px dashed #94a3b8;
    margin-top: 12px;
    padding-top: 3px;
    display: flex;
    justify-content: space-between;
    font-size: 6.5pt;
    color: #64748b;
  }

  .stamp {
    position: absolute;
    right: 10px;
    top: 10px;
    border: 1.5px solid #16a34a;
    color: #16a34a;
    padding: 1.5px 5px;
    border-radius: 3px;
    font-size: 6.5pt;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    transform: rotate(-6deg);
  }
</style>
</head>
<body>

<!-- ==================== PÀGINA 1: PORTADA OFICIAL ==================== -->
<div class="cover">
  <div>
    <div class="cover-top">
      <div class="cover-logo-area">
        <img class="cover-logo-img" src="__FLAG_B64__" alt="CSA Flag">
        <div>
          <div class="cover-agency-title">Corolt Space Agency</div>
          <div class="cover-agency-sub">Flight Operations & Scientific Directorate</div>
        </div>
      </div>
      <div class="doc-badge">
        DOC REF: CSA-RP-Y2-SCI-001<br>
        REV: 1.0 // EXECUTIVE PROPOSAL
      </div>
    </div>

    <div class="cover-hero">
      <div class="cover-pre-tag">Strategic Master Plan // Kerbin Year 2 (Days 1–426)</div>
      <h1 class="cover-title">PROGRAM «NOVA SCIENTIA»</h1>
      <div class="cover-subtitle">
        Proposta Estratègica d'Investigació Científica, Assignació de Llançadors de la Família Corolt-IV,
        Pla de Vol per a 11 Missions i Previsió Pressupostària davant la Junta de Govern de Kerbin.
      </div>

      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-val">11</div>
          <div class="kpi-label">Missions Programades</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-val">&#x221A;F 134,850</div>
          <div class="kpi-label">Pressupost Total Any 2</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-val">+220 pts</div>
          <div class="kpi-label">Retorn Científic Estimat</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-val">MunScout-1</div>
          <div class="kpi-label">Missió Insígnia Translunar</div>
        </div>
      </div>

      <table class="cover-meta-table">
        <tr>
          <td class="cover-meta-label">Organisme Emissor</td>
          <td>Departament Científic & Direcció d'Operacions de Vol CSA</td>
          <td class="cover-meta-label">Data de Document</td>
          <td>Any Kerbin 1, Dia 206 (UT 4,438,340 s)</td>
        </tr>
        <tr>
          <td class="cover-meta-label">Destinatari</td>
          <td>Comandància General de la CSA & Comitè Pressupostari de Kerbin</td>
          <td class="cover-meta-label">Horitzó Operatiu</td>
          <td>Any Kerbin 2 complet (Dies 1 a 426)</td>
        </tr>
        <tr>
          <td class="cover-meta-label">Vehicle de Llançament</td>
          <td>Família Modular Corolt-IV (Variants A, B i C)</td>
          <td class="cover-meta-label">Xarxa Telemètrica</td>
          <td>CoroltNet-LEO (300 km) & CoroltNet-MKO (600 km)</td>
        </tr>
        <tr>
          <td class="cover-meta-label">Classificació de Seguretat</td>
          <td>DOCUMENT OFICIAL DE L'AGÈNCIA — DISTRIBUCIÓ INTERNA I EXECUTIVA</td>
          <td class="cover-meta-label">Estat del Pla</td>
          <td><strong>APROVAT PER A REVISIÓ I DOTACIÓ PRESSUPOSTÀRIA</strong></td>
        </tr>
      </table>
    </div>
  </div>

  <div class="cover-motto">
    «Ad Astra Per Scientiam» — Cap a les estrelles a través del coneixement científic i el rigor d'enginyeria.
  </div>
</div>

<!-- ==================== PÀGINA 2: RESUM EXECUTIU I LLANÇADORS ==================== -->
<div class="page-break"></div>

<div class="running-header">
  <span>Corolt Space Agency // Flight Operations Directorate</span>
  <span>Doc: CSA-RP-Y2-SCI-001 // Pàgina 2 de 6</span>
</div>

<h1>1. Resum Executiu i Justificació davant la Junta</h1>

<p>
  Durant l'Any 1 de la Corolt Space Agency (CSA), els esforços operatius es van concentrar amb èxit en la transició
  des dels coets sonda de combustible sòlid (família Vector-III) cap a la propulsió líquida orbital de gran escala,
  culminant amb la conquesta de l'òrbita equatorial baixa de Kerbin (LKO) en la missió històrica <strong>CSA-10</strong>.
  Posteriorment, el Departament de Comunicacions ha assumit la tasca d'establir la infraestructura de telecomunicacions:
  la constel·lació equatorial <strong>CoroltNet-LEO</strong> (300 km, 4 satèl·lits en servei) i la xarxa dorsal de mitjana
  altitud <strong>CoroltNet-MKO</strong> (600 km, amb els 3 primers nodes actius i els 3 restants completant-se a finals d'aquest any).
</p>
<p>
  Amb la infraestructura de comunicacions i de llançament completament estabilitzada, <strong>l'Any Kerbin 2 representa la
  gran finestra d'oportunitat científica</strong> de la nostra Agència. Disposar de cobertura orbital permanent permet
  transmetre dades complexes d'experiments de Kerbalism de llarga durada sense risc de pèrdua de senyal.
</p>

<div class="callout-blue">
  <div class="callout-title">Arquitectura Científica en Tres Nivells (Three-Tier Strategy):</div>
  Per maximitzar el rendiment dels fons públics concedits, el Departament Científic proposa estructurar el programa
  en 3 categories de missions clarament diferenciades: <strong>7 Kick Missions</strong> (ràpides, barates, de baix retorn individual
  però gran agilitat), <strong>3 Science Missions</strong> (observatoris orbitals sofisticats i missions de retorn de mostres) i
  <strong>1 Flag Mission</strong> (la missió insígnia de l'Agència que marcarà la primera incursió translunar de la història de Kerbin).
</div>

<h1>2. La Família Modular de Llançadors Corolt-IV</h1>

<p>
  Per assolir els objectius de vol sense sobredimensionar costos, la totalitat de la campanya farà ús de la família modular
  de llançadors <strong>Corolt-IV (Vector-IV)</strong>, compartint el diàmetre estàndard de 1.25m, aviònica unificada i sistemes de
  desorbitació segura de segona etapa (Zero Debris Protocol).
</p>

<table class="data-table">
  <thead>
    <tr>
      <th>Variant</th>
      <th>Arquitectura de Propulsió</th>
      <th>Càrrega Útil Màx.</th>
      <th>&Delta;v Buit</th>
      <th>TWR Inicial</th>
      <th>Dies KCT</th>
      <th>Cost Unitari Estimat</th>
      <th>Missions Assignades</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Corolt-IV A</strong></td>
      <td>Etapa 1: Etoh-140-TU Sandstone (160 kN SL)<br>Etapa 2: Belle-RLX81 (FL-T200, 17.2 kN)</td>
      <td><strong>250 kg</strong> (150 km LKO)</td>
      <td>5,367 m/s</td>
      <td>1.78</td>
      <td>~5–6 dies</td>
      <td>&#x221A;F 5,850</td>
      <td><span class="tag tag-kick">Kick Missions (CSA-22 a 28)</span></td>
    </tr>
    <tr>
      <td><strong>Corolt-IV B</strong></td>
      <td>Etapa 1: Etoh-140 + 2x Shrimp SRB (220 kN SL)<br>Etapa 2: Belle-RLX81 (FL-T400, 17.2 kN)</td>
      <td><strong>500 kg</strong> (300 km LKO)<br><strong>300 kg</strong> (Polar 90°)</td>
      <td>5,392 m/s</td>
      <td>1.54</td>
      <td>~8–11 dies</td>
      <td>&#x221A;F 8,870</td>
      <td><span class="tag tag-sci">Science Missions (CSA-29 a 31)</span></td>
    </tr>
    <tr>
      <td><strong>Corolt-IV C</strong></td>
      <td>Etapa 1: Quad Feldspar Etoh-340 + 4x Shrimp (460 kN SL)<br>Etapa 2: Belle-RLX81 (FL-T600, 17.2 kN)</td>
      <td><strong>800+ kg</strong> (300 km LKO)<br><strong>380 kg</strong> (Injecció Translunar)</td>
      <td>5,506 m/s</td>
      <td>2.02</td>
      <td>~15–18 dies</td>
      <td>&#x221A;F 16,420</td>
      <td><span class="tag tag-flag">Flag Mission: MunScout-1</span></td>
    </tr>
  </tbody>
</table>

<div class="callout">
  <div class="callout-title">Validació Aerodinàmica i Seguretat de Vol:</div>
  Amb un coeficient de drag efectiu calibrat de Cd·A = 0.35 - 0.45 m² sota ogiva protectora, el perfil d'ascens
  automatitzat kOS (Kick a 1,200m cap a rumb 90° o 0°) manté la pressió dinàmica per sota de 38.0 kPa durant Max Q,
  garantint integritat estructural absoluta per a sensors òptics i biològics sensibles.
</div>

<div class="running-footer">
  <span>CSA — Programa Nova Scientia: Proposta Any Kerbin 2</span>
  <span>Pàgina 2 de 6</span>
</div>

<!-- ==================== PÀGINA 3: KICK MISSIONS ==================== -->
<div class="page-break"></div>

<div class="running-header">
  <span>Corolt Space Agency // Flight Operations Directorate</span>
  <span>Doc: CSA-RP-Y2-SCI-001 // Pàgina 3 de 6</span>
</div>

<h1>3. Manifest de les 7 Kick Missions (CSA-22 a CSA-28)</h1>

<p>
  Les Kick Missions representen l'espina dorsal d'alta cadència de l'Agència. Naus lleugeres (140–210 kg), d'alta fiabilitat
  i construcció ràpida (~5 dies) muntades sobre el llançador <strong>Corolt-IV A</strong>. La seua missió és recollir punts de ciència
  pendents immediats a Kerbin i assajar noves rames experimentals abans de missions de gran envergadura.
</p>

<table class="data-table">
  <thead>
    <tr>
      <th>Codi</th>
      <th>Nom de la Missió</th>
      <th>Vehicle</th>
      <th>Perfil de Vol / Òrbita</th>
      <th>Experiments Embarcats</th>
      <th>Retorn Científic Objectiu</th>
      <th>Vida Útil</th>
      <th>Cost (&#x221A;F)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>CSA-22</strong></td>
      <td><strong>Kick-1: AtmoSound-Ocean</strong></td>
      <td>Corolt-IV A #2</td>
      <td>Suborbital balístic (Ap = 85 km), amaratge a l'Oceà</td>
      <td>PresMat, 2HOT, Aeronomia</td>
      <td>Pressió, temp i aeronomia en aigua superficial (+2.88 pts)</td>
      <td>30 min</td>
      <td>&#x221A;F 6,450</td>
    </tr>
    <tr>
      <td><strong>CSA-23</strong></td>
      <td><strong>Kick-2: Aeroterm-Highlands</strong></td>
      <td>Corolt-IV A #3</td>
      <td>Parabòlica (Ap = 92 km) sobre Terres Altes</td>
      <td>PresMat, 2HOT, Meteorologia</td>
      <td>Gradents atmosfèrics i perfils meteorològics (+6.53 pts)</td>
      <td>40 min</td>
      <td>&#x221A;F 6,700</td>
    </tr>
    <tr>
      <td><strong>CSA-24</strong></td>
      <td><strong>Kick-3: MicroMat-UpperAtmo</strong></td>
      <td>Corolt-IV A #4</td>
      <td>Arc hipersònic a l'atmosfera superior (Ap = 68 km)</td>
      <td>Mini-Lab Materials, PresMat</td>
      <td>Degradació de materials a l'atmosfera alta (+12.98 pts)</td>
      <td>45 min (Recuperat)</td>
      <td>&#x221A;F 7,200</td>
    </tr>
    <tr>
      <td><strong>CSA-25</strong></td>
      <td><strong>Kick-4: DustScan-LKO</strong></td>
      <td>Corolt-IV A #5</td>
      <td>Òrbita baixa circular (125 x 125 km, i = 0°)</td>
      <td>Detector Micrometeorits, Telemetria</td>
      <td>Mesura de partícules de pols i micro-residus LKO (+4.74 pts)</td>
      <td>4 òrbites (3.2 h)</td>
      <td>&#x221A;F 6,850</td>
    </tr>
    <tr>
      <td><strong>CSA-26</strong></td>
      <td><strong>Kick-5: RadBelt-InnerEdge</strong></td>
      <td>Corolt-IV A #6</td>
      <td>Òrbita el·líptica (110 x 240 km, i = 15°)</td>
      <td>Comptador Geiger, 2HOT</td>
      <td>Vora inferior del cinturó intern de radiació (+6.55 pts)</td>
      <td>8 òrbites (6.5 h)</td>
      <td>&#x221A;F 7,100</td>
    </tr>
    <tr>
      <td><strong>CSA-27</strong></td>
      <td><strong>Kick-6: QuickBio-LKO</strong></td>
      <td>Corolt-IV A #7</td>
      <td>Circular 140 km amb reentrada a l'òrbita 2</td>
      <td>Contenidor Mystery Goo (Bio)</td>
      <td>Primer vol biològic espacial amb recuperació (+14.20 pts)</td>
      <td>1.5 òrbites (Recuperat)</td>
      <td>&#x221A;F 7,600</td>
    </tr>
    <tr>
      <td><strong>CSA-28</strong></td>
      <td><strong>Kick-7: MagSurvey-Equator</strong></td>
      <td>Corolt-IV A #8</td>
      <td>Circular equatorial (180 x 180 km, i = 0°)</td>
      <td>Masteler Magnetòmetre, PresMat</td>
      <td>Mapat del camp dipolar magnètic a l'equador (+8.50 pts)</td>
      <td>24 hores</td>
      <td>&#x221A;F 7,350</td>
    </tr>
  </tbody>
</table>

<div class="callout">
  <div class="callout-title">Total Inversió Kick Missions:</div>
  <strong>Cost Total Kick:</strong> &#x221A;F 49,250 | <strong>Retorn Científic Acumulat:</strong> +56.38 punts | 
  <strong>Rendiment Financer:</strong> 1.14 pts / k&#x221A;F. Totes les 7 etapes superiors Belle-RLX81 executaran maniobra de desorbitació neta.
</div>

<div class="callout-blue">
  <div class="callout-title">Protocol de Reutilització i Proves Ràpides:</div>
  Les missions Kick permetran entrenar les tripulacions del Centre de Control en procediments de resposta ràpida i calibrar
  els nous sensors d'I+D (`gptt_scienceBio` i `gptt_mag1`) abans del seu desplegament en els observatoris pesats de llarga durada.
</div>

<div class="running-footer">
  <span>CSA — Programa Nova Scientia: Proposta Any Kerbin 2</span>
  <span>Pàgina 3 de 6</span>
</div>

<!-- ==================== PÀGINA 4: SCIENCE MISSIONS ==================== -->
<div class="page-break"></div>

<div class="running-header">
  <span>Corolt Space Agency // Flight Operations Directorate</span>
  <span>Doc: CSA-RP-Y2-SCI-001 // Pàgina 4 de 6</span>
</div>

<h1>4. Manifest de les 3 Science Missions (CSA-29 a CSA-31)</h1>

<p>
  Observatoris espacials d'alta gamma de 400–500 kg, dotats de panells solars desplegables o corbats NearFuture, bateries
  d'alta capacitat (400–800 EC), ordinadors de guiatge kOS amb volant d'inèrcia i llançats pel vehicle pesat <strong>Corolt-IV B</strong>.
</p>

<table class="data-table">
  <thead>
    <tr>
      <th>Codi</th>
      <th>Missió / Plataforma</th>
      <th>Òrbita de Treball</th>
      <th>Instruments i Sensors Embarcats</th>
      <th>Objectius Científics Principals</th>
      <th>Vida Útil</th>
      <th>Cost (&#x221A;F)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>CSA-29</strong></td>
      <td><strong>Science-1: Kerbin-POLARIS</strong><br><span class="tag tag-sci">Observatori Polar</span></td>
      <td><strong>350 x 350 km Polar pura (i = 90.00°)</strong></td>
      <td>1. Sensor MITE (Ionopausa polar)<br>2. Comptador Geiger<br>3. Termo/Baròmetre US2<br>4. Detector Micrometeorits<br>5. Càmera multiespectral baixa</td>
      <td>
        • Primera òrbita polar de la història de la CSA.<br>
        • Desbloqueig de dades aurorals i electrojet polar (`kerbalism_MITE`).<br>
        • Reconeixement fotogràfic dels casquets polars, tundra i deserts continentals.<br>
        • <strong>Retorn estimat: +28.50 pts de ciència</strong>.
      </td>
      <td>150+ dies</td>
      <td>&#x221A;F 13,850</td>
    </tr>
    <tr>
      <td><strong>CSA-30</strong></td>
      <td><strong>Science-2: Corona-ORBE</strong><br><span class="tag tag-sci">Reconeixement & Retorn</span></td>
      <td><strong>220 x 220 km LKO Equatorial (i = 0.1°)</strong></td>
      <td>1. Càmera KH-1 Bloodhound (Pel·lícula)<br>2. Mini-Lab Materials (`SR_Payload_01`)<br>3. Contenidor Mystery Goo (`GooExperiment`)<br>4. Càpsula reentrada Corona + Paracaigudes</td>
      <td>
        • Cartografia orbital fotogramètrica sobre carret de pel·lícula humida.<br>
        • Exposició perllongada de materials a microgravetat orbital.<br>
        • Reentrada atmosfèrica controlada i amaratge/aterratge de precisió.<br>
        • <strong>Retorn estimat: +34.20 pts de ciència</strong>.
      </td>
      <td>15 dies (Recuperada)</td>
      <td>&#x221A;F 15,200</td>
    </tr>
    <tr>
      <td><strong>CSA-31</strong></td>
      <td><strong>Science-3: VanAllen-HEO</strong><br><span class="tag tag-sci">Sentinella Magnetosfèric</span></td>
      <td><strong>300 x 4,500 km HEO (e = 0.697, i = 28.5°)</strong></td>
      <td>1. Comptador Geiger alta radiació<br>2. Masteler magnetomètric triaxial<br>3. Detector de pols còsmica<br>4. Antena direccional de microones (MKO link)</td>
      <td>
        • Travessa contínua dels cinturons interior i exterior de Van Allen.<br>
        • Mapatge del xoc de proa magnetosfèric i vent solar (`geigerCounter@InSpaceHigh`).<br>
        • Enllaç continu de dades a través de CoroltNet-MKO (600 km).<br>
        • <strong>Retorn estimat: +24.50 pts de ciència</strong>.
      </td>
      <td>200+ dies</td>
      <td>&#x221A;F 14,450</td>
    </tr>
  </tbody>
</table>

<div class="callout">
  <div class="callout-title">Total Inversió Science Missions:</div>
  <strong>Cost Total Science:</strong> &#x221A;F 43,500 | <strong>Retorn Científic Acumulat:</strong> +87.20 punts | 
  <strong>Rendiment Financer:</strong> 2.00 pts / k&#x221A;F. Aquestes tres missions expandeixen la presència de la CSA a òrbites no equatorials.
</div>

<div class="running-footer">
  <span>CSA — Programa Nova Scientia: Proposta Any Kerbin 2</span>
  <span>Pàgina 4 de 6</span>
</div>

<!-- ==================== PÀGINA 5: FLAG MISSION & PRESSUPOST ==================== -->
<div class="page-break"></div>

<div class="running-header">
  <span>Corolt Space Agency // Flight Operations Directorate</span>
  <span>Doc: CSA-RP-Y2-SCI-001 // Pàgina 5 de 6</span>
</div>

<h1>5. Missió Insígnia Anual: CSA-32 MunScout-1 «KerbStar»</h1>

<p>
  La <strong>Flag Mission</strong> representa la màxima expressió de capacitat aeroespacial de la CSA per a l'Any 2.
  Empra la variant pesada <strong>Corolt-IV C</strong> (núcli líquid Quad Feldspar de 340 kN + 4 acceleradors sòlids Shrimp de 30 kN,
  totalitzant 460 kN d'empenta inicial) per injectar una sonda científica d'exploració translunar de 365 kg en trajectòria
  d'escapament cap a la Mun.
</p>

<table class="data-table">
  <thead>
    <tr>
      <th colspan="2">FITXA TÈCNICA OFICIAL: MUNSCOUT-1 «KERBSTAR» (MISSIÓ CSA-32)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="width: 28%;"><strong>Vehicle Llançador</strong></td>
      <td><strong>Corolt-IV C #1</strong> (Massa inicial: 23.23 t, Empenta liftoff: 460.0 kN, &Delta;v buit: 5,506 m/s)</td>
    </tr>
    <tr>
      <td><strong>Perfil de Missió</strong></td>
      <td>Inserció en LKO 180 km &rarr; Injecció Translunar (TMI, &Delta;v = 856.4 m/s) &rarr; Trànsit cislunar (16.2 h) &rarr; Sobrevol lunar a <strong>50–90 km de periapsi lunar</strong> &rarr; Retorn lliure</td>
    </tr>
    <tr>
      <td><strong>Càrrega Científica (6 Sensors)</strong></td>
      <td>
        1. <strong>Càmera de reconeixement lunar (Codac LO-2180)</strong>: Primeres fotos de detall dels cràters, maria i cara oculta.<br>
        2. <strong>Masteler magnetomètric cislunar</strong>: Recerca d'anomalies magnètiques de l'escorça lunar.<br>
        3. <strong>Detector de radiació i raigs còsmics</strong>: Mesura del camp de radiació cislunar profund (`MunInSpaceHigh/Low`).<br>
        4. <strong>Detector d'impactes de micrometeorits</strong>: Flux de pols i meteoroides en l'entorn lunar.<br>
        5. <strong>Sensor tèrmic de radiació espacial</strong>: Gradient tèrmic durant l'eclipsi lunar.<br>
        6. <strong>Badia d'exposició de materials espacials</strong>: Comportament de materials sense blindatge magnetosfèric.
      </td>
    </tr>
    <tr>
      <td><strong>Sistemes de Suport</strong></td>
      <td>6x panells solars corbats NFS, 1,200 EC bateries, doble antena parabòlica enllaçada a CoroltNet-MKO (600 km)</td>
    </tr>
    <tr>
      <td><strong>Retorn de Ciència Estimat</strong></td>
      <td><strong>+95 a +115 punts de ciència</strong> en una sola missió (Multiplicador científic de la Mun x3 respecte a Kerbin)</td>
    </tr>
    <tr>
      <td><strong>Pressupost d'Execució</strong></td>
      <td><strong>&#x221A;F 26,800</strong> (Inclou fabricació Corolt-IV C, càrrega criogènica, integració i operacions de seguiment DSN)</td>
    </tr>
  </tbody>
</table>

<h1>6. Previsió Pressupostària Oficial de l'Agència (Any Kerbin 2)</h1>

<p>
  Proposta de pressupost requerida per al Departament Científic per finançar la totalitat de les 11 missions durant els 426 dies
  de l'Any Kerbin 2, expressada en Fons oficials Kerbal (&#x221A;F).
</p>

<table class="data-table">
  <thead>
    <tr>
      <th>Concepte Pressupostari</th>
      <th>Kick Missions (7)</th>
      <th>Science Missions (3)</th>
      <th>Flag Mission (1)</th>
      <th>Total Concepte (&#x221A;F)</th>
      <th>% Pressupost</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Fabricació Coets (VAB / KCT)</strong></td>
      <td>&#x221A;F 26,450</td>
      <td>&#x221A;F 21,800</td>
      <td>&#x221A;F 13,200</td>
      <td><strong>&#x221A;F 61,450</strong></td>
      <td>45.6%</td>
    </tr>
    <tr>
      <td><strong>Propel·lents i Càrrega Pad</strong></td>
      <td>&#x221A;F 4,200</td>
      <td>&#x221A;F 4,800</td>
      <td>&#x221A;F 3,500</td>
      <td><strong>&#x221A;F 12,500</strong></td>
      <td>9.3%</td>
    </tr>
    <tr>
      <td><strong>Instrumentació Científica & Sensors</strong></td>
      <td>&#x221A;F 8,900</td>
      <td>&#x221A;F 9,400</td>
      <td>&#x221A;F 5,200</td>
      <td><strong>&#x221A;F 23,500</strong></td>
      <td>17.4%</td>
    </tr>
    <tr>
      <td><strong>Operacions de Vol & Temps Xarxa DSN</strong></td>
      <td>&#x221A;F 5,600</td>
      <td>&#x221A;F 4,500</td>
      <td>&#x221A;F 3,100</td>
      <td><strong>&#x221A;F 13,200</strong></td>
      <td>9.8%</td>
    </tr>
    <tr>
      <td><strong>Logística de Recuperació (Terra/Mar)</strong></td>
      <td>&#x221A;F 4,100</td>
      <td>&#x221A;F 3,000</td>
      <td>&#x221A;F 1,800</td>
      <td><strong>&#x221A;F 8,900</strong></td>
      <td>6.6%</td>
    </tr>
    <tr style="background-color: #f1f5f9; font-weight: bold;">
      <td>Subtotal Operatiu Net</td>
      <td>&#x221A;F 49,250</td>
      <td>&#x221A;F 43,500</td>
      <td>&#x221A;F 26,800</td>
      <td>&#x221A;F 119,550</td>
      <td>88.7%</td>
    </tr>
    <tr>
      <td><strong>Reserva de Contingència d'Enginyeria (12.8%)</strong></td>
      <td>&#x221A;F 6,300</td>
      <td>&#x221A;F 5,600</td>
      <td>&#x221A;F 3,400</td>
      <td><strong>&#x221A;F 15,300</strong></td>
      <td>11.3%</td>
    </tr>
    <tr style="background-color: #0a2540; color: #ffffff; font-weight: bold;">
      <td>TOTAL SOL·LICITAT PER A L'ANY KERBIN 2</td>
      <td>&#x221A;F 55,550</td>
      <td>&#x221A;F 49,100</td>
      <td>&#x221A;F 30,200</td>
      <td>&#x221A;F 134,850</td>
      <td>100.0%</td>
    </tr>
  </tbody>
</table>

<div class="callout">
  <div class="callout-title">Anàlisi Cost-Benefici (ROI Científic):</div>
  Amb un pressupost total de <strong>&#x221A;F 134,850</strong> i un retorn projectat de <strong>+220 punts de ciència</strong>, el cost unitari
  s'estableix en només <strong>&#x221A;F 612 per punt de ciència obtingut</strong>. Aquesta eficiència triplica el retorn històric de l'Any 1
  i garanteix fons suficients per obrir el camí cap a missions d'aterratge tripulat i exploració interplanetària a l'Any 3.
</div>

<div class="running-footer">
  <span>CSA — Programa Nova Scientia: Proposta Any Kerbin 2</span>
  <span>Pàgina 5 de 6</span>
</div>

<!-- ==================== PÀGINA 6: CRONOGRAMA, I+D I SIGNATURES ==================== -->
<div class="page-break"></div>

<div class="running-header">
  <span>Corolt Space Agency // Flight Operations Directorate</span>
  <span>Doc: CSA-RP-Y2-SCI-001 // Pàgina 6 de 6</span>
</div>

<h1>7. Cronograma Mestre de Llançaments (426 Dies)</h1>

<p>
  La distribució de les 11 missions s'ha equilibrat al llarg dels 4 trimestres de l'any kerbal per respectar els temps
  de construcció de KCT (5 a 16 dies per vehicle) i evitar solapaments a la plataforma de llançament principal:
</p>

<table class="data-table">
  <thead>
    <tr>
      <th>Trimestre</th>
      <th>Dia Kerbin</th>
      <th>Missió</th>
      <th>Tipus / Codi</th>
      <th>Llançador</th>
      <th>Objectiu Principal / Fita</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="4"><strong>Q1<br>(Dies 1–100)</strong></td>
      <td>Dia 12</td>
      <td>Kick-1: AtmoSound-Ocean</td>
      <td><span class="tag tag-kick">Kick</span> CSA-22</td>
      <td>Corolt-IV A</td>
      <td>Entrada i mostreig a l'Oceà oriental</td>
    </tr>
    <tr>
      <td>Dia 38</td>
      <td>Kick-2: Aeroterm-Highlands</td>
      <td><span class="tag tag-kick">Kick</span> CSA-23</td>
      <td>Corolt-IV A</td>
      <td>Arc suborbital Terres Altes / Praderes</td>
    </tr>
    <tr>
      <td>Dia 65</td>
      <td>Kick-3: MicroMat-UpperAtmo</td>
      <td><span class="tag tag-kick">Kick</span> CSA-24</td>
      <td>Corolt-IV A</td>
      <td>Exposició materials mesosfèrics i recuperació</td>
    </tr>
    <tr>
      <td>Dia 92</td>
      <td>Science-1: Kerbin-POLARIS</td>
      <td><span class="tag tag-sci">Science</span> CSA-29</td>
      <td>Corolt-IV B</td>
      <td><strong>Inserció polar pura 350 km (i = 90.0°)</strong></td>
    </tr>
    <tr>
      <td rowspan="3"><strong>Q2<br>(Dies 101–200)</strong></td>
      <td>Dia 125</td>
      <td>Kick-4: DustScan-LKO</td>
      <td><span class="tag tag-kick">Kick</span> CSA-25</td>
      <td>Corolt-IV A</td>
      <td>Monitoratge de pols i micro-residus a 125 km</td>
    </tr>
    <tr>
      <td>Dia 155</td>
      <td>Kick-5: RadBelt-InnerEdge</td>
      <td><span class="tag tag-kick">Kick</span> CSA-26</td>
      <td>Corolt-IV A</td>
      <td>Escombrada radiació vora interior Van Allen</td>
    </tr>
    <tr>
      <td>Dia 185</td>
      <td>Science-2: Corona-ORBE</td>
      <td><span class="tag tag-sci">Science</span> CSA-30</td>
      <td>Corolt-IV B</td>
      <td><strong>Cartografia KH-1 i recuperació càpsula a KSC</strong></td>
    </tr>
    <tr>
      <td rowspan="3"><strong>Q3<br>(Dies 201–300)</strong></td>
      <td>Dia 225</td>
      <td>Kick-6: QuickBio-LKO</td>
      <td><span class="tag tag-kick">Kick</span> CSA-27</td>
      <td>Corolt-IV A</td>
      <td>Test biològic Mystery Goo i retorn a l'aigua</td>
    </tr>
    <tr>
      <td>Dia 255</td>
      <td>Kick-7: MagSurvey-Equator</td>
      <td><span class="tag tag-kick">Kick</span> CSA-28</td>
      <td>Corolt-IV A</td>
      <td>Mapat dipolar magnètic equatorial</td>
    </tr>
    <tr>
      <td>Dia 285</td>
      <td>Science-3: VanAllen-HEO</td>
      <td><span class="tag tag-sci">Science</span> CSA-31</td>
      <td>Corolt-IV B</td>
      <td><strong>Inserció òrbita el·líptica 300 x 4,500 km</strong></td>
    </tr>
    <tr>
      <td rowspan="2"><strong>Q4<br>(Dies 301–426)</strong></td>
      <td>Dia 345</td>
      <td>Rollout & FRR MunScout-1</td>
      <td><span class="tag tag-flag">Flag Prep</span></td>
      <td>Corolt-IV C</td>
      <td>Integració a la rampa i comprovacions finals</td>
    </tr>
    <tr>
      <td>Dia 355–356</td>
      <td>Flag-1: MunScout-1 «KerbStar»</td>
      <td><span class="tag tag-flag">Flag</span> CSA-32</td>
      <td>Corolt-IV C</td>
      <td><strong>Llançament, TMI i Sobrevol de la Mun (65 km)</strong></td>
    </tr>
  </tbody>
</table>

<h1>8. Full de Ruta d'I+D i Desbloqueigs Tecnològics</h1>

<p>
  El flux de ciència generat per les missions finançarà els següents nodes tecnològics clau de l'arbre R&D:
</p>
<ul style="margin: 0 0 8px 16px; padding: 0; font-size: 8pt;">
  <li><strong>Inici de l'Any 2 (Punts en reserva: 49.3 pts):</strong> Desbloqueig immediat de <code>gptt_scienceBio</code> (20 pts — Mystery Goo) i <code>gptt_mag1</code> (30 pts — Magnetòmetre).</li>
  <li><strong>Mitjan Any 2 (Post-Polaris i Corona-ORBE):</strong> Desbloqueig de <code>gptt_sciRad1</code> (40 pts — Espectròmetres de radiació), <code>gptt_solidVac0</code> (8 pts — Motors sòlids apogeu) i <code>gptt_mono1</code> (20 pts — RCS).</li>
  <li><strong>Finals de l'Any 2 (Post-MunScout-1):</strong> Desbloqueig de <code>gptt_comm3</code> (40 pts — Antenes interplanetàries de gran guany) i <code>gptt_solar2</code> (80 pts — Panells solars desplegables gegants), preparant la campanya de l'Any 3.</li>
</ul>

<h1>9. Signatures d'Enginyeria i Aprovació Institucional</h1>

<div class="sign-grid avoid-break">
  <div class="sign-box">
    <div class="stamp">REVISAT</div>
    <div class="sign-title">Cap del Departament Científic</div>
    <div class="sign-name">Dr. Wernher von Kerman</div>
    <div class="sign-role">Director de Recerca & Instrumentació CSA</div>
    <div class="sign-line">
      <span>Signatura: <em>W. v. Kerman</em></span>
      <span>Data: Y1-D206</span>
    </div>
  </div>

  <div class="sign-box">
    <div class="stamp">APROVAT</div>
    <div class="sign-title">Director d'Operacions de Vol</div>
    <div class="sign-name">Gene Kerman</div>
    <div class="sign-role">Director de Vol & Centre de Control KSC</div>
    <div class="sign-line">
      <span>Signatura: <em>G. Kerman</em></span>
      <span>Data: Y1-D206</span>
    </div>
  </div>

  <div class="sign-box">
    <div class="stamp">CONFORME</div>
    <div class="sign-title">Cap d'Enginyeria de Sistemes & Astrodinàmica</div>
    <div class="sign-name">Linus Kerman</div>
    <div class="sign-role">Supervisió de Llançadors Corolt-IV & Astrodinàmica</div>
    <div class="sign-line">
      <span>Signatura: <em>L. Kerman</em></span>
      <span>Data: Y1-D206</span>
    </div>
  </div>

  <div class="sign-box">
    <div class="stamp" style="border-color: #0b3d91; color: #0b3d91;">RATIFICAT</div>
    <div class="sign-title">Comandant en Cap de l'Agència Espacial</div>
    <div class="sign-name">Comandant Elebrimir</div>
    <div class="sign-role">Director General de la Corolt Space Agency (CSA)</div>
    <div class="sign-line">
      <span>Signatura: <em>Elebrimir</em></span>
      <span>Data: Y1-D206</span>
    </div>
  </div>
</div>

<div class="running-footer">
  <span>CSA — Programa Nova Scientia: Proposta Any Kerbin 2</span>
  <span>Pàgina 6 de 6 // Document Oficial</span>
</div>

</body>
</html>
"""

    html_content = html_template.replace("__FLAG_B64__", flag_b64).replace("__LOGO_B64__", logo_b64)

    temp_html_path = "/tmp/csa_nova_scientia_proposal.html"
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    pdf_output_path = os.path.join(root_dir, "CSA_Nova_Scientia_Year2_Proposal.pdf")
    
    print("Generating PDF via Google Chrome headless...")
    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_output_path}",
        f"file://{temp_html_path}"
    ]
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Error generating PDF: {res.stderr}")
        sys.exit(1)

    print(f"PDF successfully created at: {pdf_output_path}")
    print(f"File size: {os.path.getsize(pdf_output_path)} bytes")

    # Also copy to artifacts directory if available
    brain_dir = "/home/pablo-cortes/.gemini/antigravity/brain/e79b30f9-3f64-4adc-829b-73407b37c1fa"
    if os.path.exists(brain_dir):
        artifact_pdf = os.path.join(brain_dir, "CSA_Nova_Scientia_Year2_Proposal.pdf")
        subprocess.run(["cp", pdf_output_path, artifact_pdf])
        print(f"Copied to artifact directory: {artifact_pdf}")

if __name__ == "__main__":
    main()
