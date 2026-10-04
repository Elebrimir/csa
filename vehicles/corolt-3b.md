# 🚀 Llançador Suborbital de Guiatge Actiu: Corolt-IIIb (CSA-07)

> *"Evolució directa del Corolt-III equipada amb superfícies de control aerodinàmic mòbils a ambdues etapes, permetent a kOS executar maniobres de cabeceig (pitch kick) i guiatge horitzontal cap a l'Est."*

---

## 📐 Especificacions Tècniques Generals

| Paràmetre de Disseny | Valor d'Enginyeria |
| :--- | :--- |
| **Fabricant** | Corolt Space Agency (CSA) |
| **Tipus de Vehicle** | Llançador Suborbital Multietapa en Línia amb Guiatge Actiu |
| **Diàmetre de Base (Etapa 1)** | **1.25 m** (Booster RT-10 «Hammer» amb empenta calibrada al 46%) |
| **Diàmetre Superior (Etapa 2)** | **0.625 m** (Motor de combustible sòlid SRM-XL) |
| **Massa Total al Llançament** | **5.199 t (5.199 kg)** |
| **Massa de Càrrega Útil (Dry Mass)** | **0.629 t (629 kg)** |
| **Massa Recuperada a l'Aterratge** | **0.3015 t (301,5 kg)** |
| **Cost Total de Construcció** | **9.775,5 fons** |
| **Valor Recuperat al VAB Warehouse** | **7.301,0 fons** (74,7% de retorn econòmic) |
| **Superfícies de Control Actiu** | 4x \`bluedog.Redstone.Fin.CtrlSurf\` (Etapa 1) + 4x \`bluedog.Scout.Algol.Fin\` (Etapa 2) |
| **Recuperació** | Morro cònic amb paracaigudes integrat \`SR.Nosecone.625\` |

---

## 🕹️ Sistema de Control i Dinàmica de Vol

A diferència del Corolt-III estàndard (que utilitzava alerons passius fixes incapaços de maniobrar), la variant **Corolt-IIIb** incorpora:
* **Primera Etapa (Hammer)**: 4 superfícies mòbils tipus Redstone (*Etoh-CS*) que proporcionen ple control de guinyada, cabeceig i alabeig durant la fase densa atmosfèrica.
* **Segona Etapa (SRM-XL)**: 4 aletes mòbils tipus Algol (*Dioscuri-AFD1*) que mantenen el vector de cabeceig a 80º–82º fins a la cota de 35–40 km.
* **Ordinador de Bord (kOS)**: Executa el programa d'ascens autònom \`corolt3_guided_ascent.ks\` i disposa del procediment d'emergència \`emergency_recovery.ks\`.

---

## 🔬 Suite Científica i Càrrega Útil Recuperable

Tota la secció superior es troba muntada a l'interior d'una gàbia d'instruments oberta \`SR.PayloadTruss.625\`:
* ⏱️ **Pressió Atmosfèrica PresMat (\`sensorBarometer\`)**
* 🌡️ **Temperatura 2HOT (\`sensorThermometer\`)**
* 🌪️ **Meteorological Survey Package (\`SR.Payload.01\`)**
* 🧪 **Aeronomy Sensor Array (\`SR.Payload.02\`)**
* ⚙️ **Engineering & Stress Package (\`SR.Payload.04\`)**
* 📡 **Advanced Sounding Package (\`SR.Payload.03\`)**
* ⚡ **Emmagatzematge Elèctric**: Bateria de 100 EC (\`batteryBankMini\`) + 2x \`nfex-battery-mini-1\` (250 EC totals).
* 💾 **Aviònica CSA**: 2x \`SR.ProbeCore\` (32 MB cadascuna, 64 MB totals).

---

## 📈 Perfil Aerodinàmic Calibrat (Drag Empíric)

Extret a partir de la telemetria real de la missió **CSA-07**:
* **$C_d \cdot A$ Efectiu Medià**: **1.727 m²**
* **Coeficient Subsònic (< Mach 0.8)**: 1.468 m²
* **Pic Transònic (Mach 0.8 – 1.2)**: 2.331 m²
* **Règim Supersònic (Mach 1.2 – 2.5)**: 1.813 m²
* **Règim Hipersònic (> Mach 4.5)**: 1.640 m²

---

## 📋 Conclusió Operativa i Historial

El vehicle va debutar amb èxit rotund a la missió **CSA-07** (Any 1, Dia 65), creuant la frontera espacial fins a 138,6 km i recorrent més de 315 km mar endins. La càpsula va fer un amaratge suau a l'oceà i va ser recuperada íntegrament al magatzem del VAB, salvant el 74,7% del valor de la nau.
