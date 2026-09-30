# 🚀 Llançador Multietapa: Corolt-II (CSA-03)

> *"El salt a la frontera de l'espai: el primer coet de dues etapes de la Corolt Space Agency dissenyat per superar la línia de Karman (>70 km)."*

![Corolt-II Plànol KVV 1](../assets/vehicles/corolt-2_blueprint_1.png)

---

## 📐 Especificacions Tècniques Generals

| Paràmetre de Disseny | Valor d'Enginyeria |
| :--- | :--- |
| **Fabricant** | Corolt Space Agency (CSA) |
| **Tipus de Vehicle** | Coet Sonda Multietapa de 2 Fases (Two-Stage Sounding Rocket) |
| **Diàmetre Principal** | 0.625 m (Booster) $\rightarrow$ 0.35 m (Segona Etapa) |
| **Massa Total al Llançament** | **1.387 t (1.387 kg)** |
| **Massa Final de Càrrega Útil** | **0.167 t (167 kg)** |
| **Empenta Màxima al Llançament** | **28.00 kN** |
| **Ràtio Empenta/Pes (TWR)** | **2.06 (Inici Etapa 1)** $\rightarrow$ **2.04 (Inici Etapa 2)** |
| **Delta-v ($\Delta v$) Total** | **2.205 m/s (Nivell del mar) / 2.630 m/s (Buit)** |
| **Temps Total de Combustió** | **92,3 segons (58,5s Etapa 1 + 33,8s Etapa 2)** |
| **Separació d'Etapes** | Desacoblador de separació ràpida `SR.Decoupler` (0.35m) |
| **Recuperació** | Paracaigudes de càrrega miniatura al morro (`SR.Nosecone.35`) |

---

## 🔬 Arquitectura per Etapes

```
[Morro + Paracaigudes]
       │
[Càrrega Científica SR.Payload.02 + Bateria + Ordinador]
       │
[Segona Etapa: Motor Sòlid SRM-L 0.35m (4 aletes SR.Wing.03)]
       │
[Desacoblador Explosiu Mini 0.35m]
       │
[Primera Etapa: Booster SRM-XL 0.625m (4 aletes grans SR.Wing.02)]
```

### 1. Primera Etapa (Booster d'Ascens Atmosfèric):
* **Motor**: SRM-XL de 0.625m (`SR.Rocket.625.01`).
* **Empenta**: Limitada al 16% per aconseguir un ascens suau i controlat de **28 kN** (TWR inicial de 2.06).
* **Missió**: Travessar la capa densa de la troposfera durant **58,5 segons** d'acceleració constant, portant el vehicle fins a més de 25.000 metres d'altitud.
* **Estabilització**: 4 aletes d'alta resistència `SR.Wing.02` a la base.

### 2. Segona Etapa (Propulsió a Gran Altitud / Buit):
* **Motor**: SRM-L de 0.35m (`SR.Rocket.35.02`).
* **Missió**: Encesa immediatament després de la separació del booster, proporcionant **33,8 segons** d'impuls pur en l'aire fi per catapultar la càrrega útil cap a l'espai exterior.
* **Càrrega Útil**: El nou paquet científic d'anàlisi atmosfèrica i de radiació **`SR.Payload.02`**, alimentat per la bateria integrada `SR.Stack.Battery`.

---

## 🛠️ Esquemes d'Enginyeria KVV (Kronal Vessel Viewer)

### Vista en Secció i Components
![Corolt-II Plànol KVV 2](../assets/vehicles/corolt-2_blueprint_2.png)

### Esquema d'Integració i Aerodinàmica
![Corolt-II Plànol KVV 3](../assets/vehicles/corolt-2_blueprint_3.png)
