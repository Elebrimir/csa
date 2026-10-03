# 📋 Informe de Missió: CSA-05b «El Salt a l'Espai i la Lliçó de CommNet»

* **Data del Llançament**: Any 1, Dia 56 (05h 16m 15s UT 1193389)
* **Operador de Vol / Comandament**: Control de Missions CSA (Cap Canaveral de Kerbin)
* **Vehicle Llançador**: [Corolt-III (Unitat 02 - Tàndem)](/vehicles/corolt-3)
* **Estat de la Missió**: 🟡 ÈXIT SUBORBITAL ESPACIAL (240 km) | PÈRDUA EN REENTRADA (Impacte per fallada d'enllaç de control)

---

## 🎯 Objectius de la Missió
1. **Superació de la Frontera de l'Espai (Línia de Kármán, 70 km)**: Validar la capacitat del Corolt-III per impulsar càrregues útils a l'espai exterior (`InSpaceLow`). *(Assolit amb escreix — 240,34 km)*
2. **Combustió Plena de Dues Etapes en Tàndem**: Comprovar el rendiment continuat del booster RT-10 «Hammer» (1,25 m) i de la segona etapa SRM-XL (0,625 m) després de la fallada d'ignició del vol CSA-05. *(Assolit — Ignició i combustió impecables)*
3. **Resistència Aerotèrmica a la Reentrada Hipersònica**: Monitoritzar l'estabilitat i la pressió dinàmica ($Q$) en caiguda lliure des de més de 200 km. *(Assolit — Màx Q de 52,29 kPa a Mach 5,3)*
4. **Recuperació Íntegra de la Càpsula**: Desplegament de paracaigudes a cota segura i rescat al KSC. *(No assolit — Impacte contra el terreny)*

---

## 📊 Telemetria Oficial de Vol (Dades Registrades)

Dades capturades en temps real via enllaç telemètric continu de bord (Telemachus):

| Paràmetre de Vol | Valor Registrat CSA-05b | Estat i Observacions |
| :--- | :--- | :--- |
| **Altitud Màxima (Apoapsis)** | **240.336,8 m (240,34 km)** | 🟢 **Rècord Absolut CSA (Espai Exterior)** |
| **Velocitat Màxima de Superfície** | **1.624,4 m/s (5.847,8 km/h)** | 🟢 Superat Mach 5,3 en reentrada |
| **Pressió Dinàmica Màxima (Max Q)** | **52.286,6 Pa (52,29 kPa)** | 🟢 Resistència aerodinàmica excel·lent |
| **Acceleració Màxima** | **10,91 G** | 🟡 Deceleració atmosfèrica intensa |
| **Temps a l'Espai (> 70 km)** | **670,8 s (11 min 11 s)** | 🟢 Primera estada prolongada a l'espai |
| **Desplegament del Paracaigudes** | *No executat* | 🔴 Comanda bloquejada per falta de senyal |
| **Velocitat d'Impacte a Terra** | **116,7 m/s (420 km/h)** | 🔴 Destrucció de la unitat per col·lisió |
| **Cota d'Impacte** | **896,8 m s.n.m.** | Terreny continental a l'est del KSC |
| **Durada Total de Vol** | **1.011,8 s (16 min 52 s)** | Telemetria transmesa fins l'impacte |

---

### Gràfica de Telemetria del Vol CSA-05b
![Telemetria de Vol CSA-05b](../assets/csa-05b_telemetry_plot.svg)

---

## 🔬 Anàlisi de Rendiment de Propulsió

A diferència del vol CSA-05, on el motor SRM-XL va patir una fallada d'ignició, la segona unitat del Corolt-III va funcionar a la perfecció:
* **Etapa 1 (RT-10 «Hammer»)**: Va cremar durant 31 segons, accelerant la nau fins als 475 m/s i deixant-la a 12 km d'altitud.
* **Separació i Etapa 2 (SRM-XL)**: La ignició a gran altitud va ser instantània. En un entorn de molt baixa densitat atmosfèrica, el motor va desenvolupar el seu impuls específic complet de buit, disparant la velocitat vertical fins a catapultar l'apogeu fins als **240 km**, molt per damunt dels 50 km previstos inicialment.
* **Comportament Balístic**: La nau va passar més d'11 minuts en condicions de microgravetat pura a l'espai exterior abans d'iniciar el retorn.

---

## ⚠️ Anàlisi de la Fallada de Recuperació (RCA - Root Cause Analysis)

A T+16 minuts, durant la fase terminal de reentrada:
1. **Límit d'Abast de l'Antena Interna**: El mòdul d'aviònica `SR.ProbeCore` de Sounding Rockets disposa únicament d'una antena integrada de **3,25 km** d'abast.
2. **Pèrdua d'Enllaç de Control CommNet**: En trobar-se lluny del KSC i fora de cobertura d'estacions terrestres properes, la sonda va quedar en estat `Sense Senyal` (*No signal*).
3. **Bloqueig de Comandes**: En les sondes robòtiques sense pilot, el protocol de CommNet bloqueja l'execució d'ordres manuals d'etapes o menús si no hi ha enllaç actiu.
4. **Seqüència Fatal**: L'ordre d'obertura del paracaigudes enviada des de la consola de vol no es va poder transmetre a la nau, precipitant la càpsula contra el terreny a 116,7 m/s.

---

## 🛡️ Decisions d'Enginyeria per a Missions Futures

La pèrdua de la unitat 02 ha aportat un aprenentatge incalculable que transforma immediatament els procediments de la CSA:

1. **Incorporació Obligatòria d'Antena Externa (`SurfAntenna`)**:
   * S'ha verificat la disponibilitat del node tecnològic `gptt_comm1`.
   * Totes les futures variants del Corolt-III incorporaran l'antena de superfície **Communotron 16-S**, garantint cobertura ininterrompuda des de qualsevol punt de Kerbin.
2. **Protocol d'Armat Mecànic de Paracaigudes (*Arm Parachute*)**:
   * Els paracaigudes s'armaran abans de l'enlairament per permetre el desplegament autònom per pressió baromètrica, fins i tot en cas d'apagada total de ràdio.
3. **Transició cap al Control Autònom (kOS)**:
   * S'ha iniciat el desenvolupament d'un ordinador de bord programable amb scripts de **kOS** (`corolt3_flight.ks`), delegant el control d'etapes i obertura de seguretat a la CPU interna de la nau sense dependència de decisions manuals remotes.

---

## 📸 Vehicle de la Missió
* [Fitxa Tècnica Completa del Corolt-III](/vehicles/corolt-3)
