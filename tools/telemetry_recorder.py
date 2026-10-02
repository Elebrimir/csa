#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Live Telemetry Recorder
Connects to Telemachus in Kerbal Space Program (http://127.0.0.1:8085).
Records real-time flight data to CSV and generates a mission report summary.
Converts Universal Time (UT) to Kerbin calendar date (6h days, 426d years).
"""

import urllib.request
import json
import time
import sys
import os
import csv
from datetime import datetime

TELEMACHUS_URL = "http://127.0.0.1:8085/telemachus/datalink"

# Telemachus API Query String
QUERY_API = (
    "?ut=t.universalTime"
    "&alt=v.altitude"
    "&rad_alt=v.heightFromTerrain"
    "&v_spd=v.verticalSpeed"
    "&orb_vel=v.orbitalVelocity"
    "&surf_vel=v.surfaceVelocity"
    "&apo=o.ApA"
    "&peri=o.PeA"
    "&g_force=v.geeForce"
    "&dyn_pres=v.dynamicPressure"
    "&throttle=f.throttle"
    "&stage=s.stage"
)

def ut_to_kerbin_date(ut):
    """Converts KSP Universal Time in seconds to Kerbin calendar date."""
    SECONDS_IN_HOUR = 3600
    HOURS_IN_DAY = 6
    SECONDS_IN_DAY = SECONDS_IN_HOUR * HOURS_IN_DAY
    DAYS_IN_YEAR = 426
    SECONDS_IN_YEAR = SECONDS_IN_DAY * DAYS_IN_YEAR

    year = int(ut // SECONDS_IN_YEAR) + 1
    rem_year = ut % SECONDS_IN_YEAR
    day = int(rem_year // SECONDS_IN_DAY) + 1
    rem_day = rem_year % SECONDS_IN_DAY
    hour = int(rem_day // SECONDS_IN_HOUR)
    rem_hour = rem_day % SECONDS_IN_HOUR
    minute = int(rem_hour // 60)
    second = int(rem_hour % 60)

    return f"Any {year}, Dia {day} ({hour:02d}h {minute:02d}m {second:02d}s)"

def check_connection():
    try:
        req = urllib.request.Request(f"{TELEMACHUS_URL}?test=v.altitude", headers={'User-Agent': 'CSA-Telemetry'})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            return "errors" not in data
    except Exception:
        return False

def record_flight(mission_name="CSA-03", interval=0.5):
    print(f"\n========================================================")
    print(f"       COROLT SPACE AGENCY (CSA) - TELEMETRY RECORDER   ")
    print(f"========================================================")
    print(f"[*] Comprovant connexió amb Telemachus (127.0.0.1:8085)...")

    if not check_connection():
        print(f"[!] Esperant que la nau estiga carregada a la rampa de llançament...")
        while not check_connection():
            time.sleep(1.0)

    print(f"[✓] Connexió establida! Obtenint data oficial de Kerbin...")
    
    # Query initial UT
    try:
        req = urllib.request.Request(f"{TELEMACHUS_URL}?ut=t.universalTime", headers={'User-Agent': 'CSA-Telemetry'})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode())
            initial_ut = float(data.get("ut", 0.0))
            kerbin_date = ut_to_kerbin_date(initial_ut)
            print(f"[📅] Data Oficial de Kerbin: {kerbin_date} (UT: {initial_ut:,.1f}s)")
    except Exception:
        initial_ut = 0.0
        kerbin_date = "Any 1, Dia ?"

    os.makedirs("missions", exist_ok=True)
    csv_file = f"missions/{mission_name}_telemetry.csv"
    
    fieldnames = [
        "timestamp", "UT", "MET", "altitude", "radar_alt", "vert_speed",
        "orbital_vel", "surface_vel", "apoapsis", "periapsis",
        "g_force", "dynamic_pressure", "throttle", "stage"
    ]
    
    start_time = None
    max_alt = 0.0
    max_vel = 0.0
    max_g = 0.0
    max_q = 0.0

    with open(csv_file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print(f"[*] Enregistrant telemetria a: {csv_file}")
        print(f"    (Prem Ctrl+C per aturar el registre i generar el resum)\n")
        print(f"{'MET (s)':>8} | {'Alt (m)':>9} | {'Spd (m/s)':>9} | {'Apo (km)':>8} | {'G-Force':>7} | {'Q (kPa)':>7}")
        print("-" * 62)

        try:
            while True:
                req = urllib.request.Request(f"{TELEMACHUS_URL}{QUERY_API}", headers={'User-Agent': 'CSA-Telemetry'})
                try:
                    with urllib.request.urlopen(req, timeout=3.0) as resp:
                        data = json.loads(resp.read().decode())
                except Exception:
                    time.sleep(interval)
                    continue
                
                now = time.time()
                if start_time is None:
                    start_time = now
                met = round(now - start_time, 1)

                ut = float(data.get("ut", initial_ut))
                alt = float(data.get("alt", 0.0))
                rad_alt = float(data.get("rad_alt", 0.0))
                v_spd = float(data.get("v_spd", 0.0))
                orb_vel = float(data.get("orb_vel", 0.0))
                surf_vel = float(data.get("surf_vel", 0.0))
                apo = float(data.get("apo", 0.0))
                peri = float(data.get("peri", 0.0))
                g_force = float(data.get("g_force", 0.0))
                q = float(data.get("dyn_pres", 0.0))
                throttle = float(data.get("throttle", 0.0))
                stage = int(data.get("stage", 0))

                max_alt = max(max_alt, alt)
                max_vel = max(max_vel, max(orb_vel, surf_vel))
                max_g = max(max_g, g_force)
                max_q = max(max_q, q)

                writer.writerow({
                    "timestamp": round(now, 2),
                    "UT": round(ut, 1),
                    "MET": met,
                    "altitude": round(alt, 1),
                    "radar_alt": round(rad_alt, 1),
                    "vert_speed": round(v_spd, 1),
                    "orbital_vel": round(orb_vel, 1),
                    "surface_vel": round(surf_vel, 1),
                    "apoapsis": round(apo, 1),
                    "periapsis": round(peri, 1),
                    "g_force": round(g_force, 2),
                    "dynamic_pressure": round(q, 2),
                    "throttle": round(throttle, 2),
                    "stage": stage
                })
                f.flush()

                print(f"{met:>8.1f} | {alt:>9.1f} | {surf_vel:>9.1f} | {apo/1000:>8.1f} | {g_force:>7.2f} | {q:>7.2f}", end="\r")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n" + "=" * 62)
            print(f"      REGISTRE COMPLETAT - RESUM DE MISSIÓ: {mission_name}")
            print("=" * 62)
            summary = f"""
## 📊 Telemetria Oficial - Missió {mission_name}
* **Data de Vol (Calendari Kerbin)**: {kerbin_date}
| Mètrica | Valor Registrat |
| :--- | :--- |
| **Durada de Vol (MET)** | {met:.1f} s |
| **Altitud Màxima Assolida** | {max_alt:,.1f} m ({(max_alt/1000):.2f} km) |
| **Velocitat Màxima** | {max_vel:,.1f} m/s |
| **Pressió Dinàmica Màxima (Max Q)** | {max_q:.2f} kPa |
| **Acceleració Màxima** | {max_g:.2f} G |

*Dades desades a `{csv_file}`.*
"""
            print(summary)
            with open(f"missions/{mission_name}_summary.md", "w") as sf:
                sf.write(summary)
            print(f"[✓] Resum en Markdown guardat a: missions/{mission_name}_summary.md")

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "CSA-03"
    record_flight(name)
