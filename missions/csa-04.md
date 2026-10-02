# 📋 Informe de Missió: CSA-04 «El Desafiament del Corolt-IIb»

* **Data del Llançament**: Any 1, Dia 35 (03h 56m 39s)
* **Operador de Vol / Comandament**: Control de Missions CSA (Cap Canaveral de Kerbin)
* **Vehicle Llançador**: [Corolt-IIb (Variant Multietapa Radial)](/vehicles/corolt-2b)
* **Estat de la Missió**: 🟢 ÈXIT DE RECUPERACIÓ I RÈCORD CIENTÍFIC (+10,4 punts de ciència)

---

## 🎯 Objectius de la Missió
1. **Estrena d'Instrumentació Científica Avançada**: Incorporació i validació operativa del Baròmetre BAROTRON (`sensorBarometer`), Termòmetre 2HOT (`sensorThermometer`) i el paquet d'anàlisi meteorològica `SRExperiment01`. *(Completat)*
2. **Assaig d'Alta Potència i Estabilització**: Avaluació de la configuració de 4 boosters auxiliars exteriors i estabilització giroscòpica per rotació (*spin stabilization*). *(Completat - dades d'estrès estructural crítiques)*
3. **Altitud Operativa**: Superació de la baixa atmosfera i assalt a les capes mitjanes-altes de Kerbin (>14 km). *(Completat - 14,49 km assolit)*
4. **Recuperació Íntegra**: Aterratge suau i recuperació al 100% de la càpsula d'instruments a les praderies de Kerbin. *(Completat)*

---

## 📊 Telemetria Oficial de Vol (Dades Registrades)

Dades capturades en temps real via enllaç telemètric Telemachus:

| Paràmetre de Vol | Intent 1 (CSA-04) | Vol Definitiu (CSA-04b) |
| :--- | :--- | :--- |
| **Altitud Màxima (Apoapsis)** | 669,7 m | **14.489,5 m (14,49 km)** |
| **Velocitat Màxima de Superfície** | 193,6 m/s (697 km/h) | **305,4 m/s (1.100 km/h)** *(a 6.897 m)* |
| **Pressió Dinàmica Màxima (Max Q)** | 20.354 kPa | **25.281,9 kPa** |
| **Desplegament del Paracaigudes** | 156,4 m | **1.666,3 m** |
| **Acceleració Màxima en Obertura** | 13,60 G | **19,40 G** |
| **Durada Total de Vol** | 62,7 s | **447,7 segons (7 min 28 s)** |
| **Lloc de Presa de Terra** | Praderies KSC (55,4 m) | **Praderies KSC (1.500 m altiplà)** |
| **Integritat de la Càrrega Útil** | 100% Recuperada | **100% Recuperada i Intacta** |

---

### Gràfica de Telemetria del Vol CSA-04b
![Telemetria de Vol CSA-04b](../assets/csa-04b_telemetry_plot.svg)

*(Gràfica de l'incident aerodinàmic inicial CSA-04 per a anàlisi d'enginyeria: [Veure Gràfica CSA-04](../assets/csa-04_telemetry_plot.svg))*

---

## 🔬 Rendiment Científic Històric (Kerbalism & R+D)

Aquest vol marca un punt d'inflexió per a la ciència de la CSA:
* **Baròmetre BAROTRON (`barometerScan@KerbinSrfLandedShores`)**: Primera mesura oficial de la pressió atmosfèrica de Kerbin.
* **Termòmetre 2HOT (`temperatureScan@KerbinSrfLandedShores`)**: Primer perfil tèrmic certificat per la CSA.
* **Paquet Meteorològic (`SRExperiment01@KerbinFlyingLowShores` i `SrfLanded`)**: Registre complet de paràmetres atmosfèrics en vol baix i superfície.
* **Telemetria Ambiental Kerbalism**: Enregistrament continu de dades durant els 7 minuts de descens.
* **Balanç d'R+D**: La recuperació de la càpsula ha aportat **+10,41 punts de ciència**, disparant el balanç de l'agència de 2,54 a **12,95 punts disponibles**!

> [!NOTE]
> **Diagnòstic d'Enginyeria sobre Emmagatzematge:** L'ordinador de bord (*Avionics Package*) disposa de 500 KB de capacitat de sèrie, quedant saturat davant dels 3,5 MB generats pels nous sensors. Per al pròxim vol s'actualitzarà la memòria del disc dur o s'incorporarà transmissió per ràdio en directe.

---

## ⚠️ Anàlisi de l'Incident Estructural i Lliçons d'Enginyeria

La campanya CSA-04 ha estat una de les més riques en aprenentatge d'enginyeria aeroespacial:
1. **Primer Intent (CSA-04):** Amb un TWR inicial extrem (>2.4) i 4 boosters radials sense SAS, el vehicle va assolir Max Q a només 400 m, patint una pèrdua de control aerodinàmic que va forçar un *looping* a 670 m i descens immediat en paracaigudes.
2. **Vol Definitiu (CSA-04b):** Es va aplicar reducció d'empenta i inclinació d'aletes per aconseguir estabilització giroscòpica per rotació (*spin stabilization*). La rotació va ser tan efectiva i violenta que la força centrífuga va estripar els ancoratges dels 4 boosters radials a baixa cota.
3. **Comportament del Tram Central:** Deslliurat dels boosters exteriors, el nucli central va continuar volant perfectament vertical i rígid, assolint els **14.489 metres** d'altitud màxima abans d'iniciar una reentrada suau i recuperar tots els instruments.

### Conclusió per al Programa Corolt:
S'abandona definitivament l'ús de boosters radials sense guiatge actiu. La futura classe **Corolt-III** serà un vehicle estrictament **en línia (tàndem)** amb motor inferior d'alta empenta (RT-10 «Hammer»).

---

## 📸 Vehicle de la Missió
![Corolt-IIb Plànol General](../assets/vehicles/corolt-2b_blueprint_1.png)
