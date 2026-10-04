#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Ascent Trajectory Simulator & kOS Guidance Optimizer
Simulates multi-stage rocket ascents from Kerbin using 4th-order Runge-Kutta (RK4) integration.
Predicts burnout trajectory, apoapsis, periapsis, and aerodynamic / gravitational losses.
Optimizes kOS pitch-kick parameters (ALT_KICK, PITCH_INICIAL) before real flight execution.
"""

import sys
import os
import json
import argparse
import numpy as np

# ==============================================================================
# KERBIN PHYSICAL CONSTANTS
# ==============================================================================
KERBIN_MU = 3.5316000e12        # Gravitational parameter (m^3/s^2)
KERBIN_RADIUS = 600000.0        # Equatorial radius (m)
KERBIN_ROT_PERIOD = 21600.0     # Sidereal rotation period (s) = 6 hours
KERBIN_OMEGA = 2.0 * np.pi / KERBIN_ROT_PERIOD # Angular velocity (rad/s)
KERBIN_V_ROT = KERBIN_OMEGA * KERBIN_RADIUS    # Equatorial surface speed (~174.53 m/s)
KERBIN_ATMO_LIMIT = 70000.0     # Atmosphere cutoff altitude (m)
KERBIN_SCALE_HEIGHT = 5600.0    # Scale height (m)
KERBIN_RHO_0 = 1.225            # Sea-level atmospheric density (kg/m^3)
KERBIN_P_0 = 101325.0           # Sea-level atmospheric pressure (Pa)

# ==============================================================================
# VEHICLE PRESETS
# ==============================================================================
DEFAULT_VEHICLES = {
    "corolt-3": {
        "name": "Corolt-III (Arquitectura Tàndem)",
        "cda_default": 1.50,
        "stages": [
            {
                "name": "Etapa 1 (RT-10 «Hammer»)",
                "m_initial": 5144.0,
                "m_propellant": 2825.0,
                "burn_time": 50.7,
                "thrust_vac": 96500.0,
                "thrust_asl": 91800.0,
            },
            {
                "name": "Separació Interetapa",
                "m_initial": 2319.0, # 5144 - 2825
                "m_propellant": 0.0,
                "burn_time": 1.5,
                "thrust_vac": 0.0,
                "thrust_asl": 0.0,
            },
            {
                "name": "Etapa 2 (SRM-XL)",
                "m_initial": 1569.0, # after 750kg casing jettison
                "m_propellant": 940.0,
                "burn_time": 57.6,
                "thrust_vac": 41200.0,
                "thrust_asl": 38400.0,
            }
        ],
        "m_dry": 629.0
    }
}

def load_calibrated_cda(vehicle_key):
    aero_file = f"vehicles/{vehicle_key}_aero.json"
    if os.path.exists(aero_file):
        try:
            with open(aero_file, 'r') as f:
                data = json.load(f)
                return float(data.get("calibrated_cda_m2", 1.50))
        except Exception:
            pass
    return DEFAULT_VEHICLES.get(vehicle_key, {}).get("cda_default", 1.50)

# ==============================================================================
# SIMULATION ENGINE (RK4)
# ==============================================================================
class AscentSimulator:
    def __init__(self, vehicle_config, cda=None):
        self.vehicle = vehicle_config
        self.cda = cda if cda is not None else vehicle_config.get("cda_default", 1.50)

    def atmosphere_density(self, alt):
        if alt >= KERBIN_ATMO_LIMIT or alt < 0:
            return 0.0
        return KERBIN_RHO_0 * np.exp(-alt / KERBIN_SCALE_HEIGHT)

    def guidance_pitch(self, alt, alt_kick, pitch_kick, alt_end_turn=35000.0, min_pitch=30.0):
        """
        Replicates Corolt Space Agency kOS guidance law:
        LOCK targetPitch TO MAX(min_pitch, pitch_kick - ((SHIP:ALTITUDE - alt_kick) / (alt_end_turn - alt_kick)) * (pitch_kick - min_pitch)).
        """
        if alt < alt_kick:
            return 90.0
        if alt >= alt_end_turn:
            return min_pitch
        factor = (alt - alt_kick) / (alt_end_turn - alt_kick)
        target = pitch_kick - factor * (pitch_kick - min_pitch)
        return max(min_pitch, target)

    def equations_of_motion(self, t, state, thrust, m, alt_kick, pitch_kick, alt_end_turn, min_pitch):
        r, theta, vr, vt = state
        h = max(0.0, r - KERBIN_RADIUS)

        # Commanded pitch from local surface horizon
        pitch_deg = self.guidance_pitch(h, alt_kick, pitch_kick, alt_end_turn, min_pitch)
        pitch_rad = np.radians(pitch_deg)

        # Thrust components
        if m > 0 and thrust > 0:
            a_thrust_r = (thrust / m) * np.sin(pitch_rad)
            a_thrust_t = (thrust / m) * np.cos(pitch_rad)
        else:
            a_thrust_r = 0.0
            a_thrust_t = 0.0

        # Atmospheric relative velocity (surface frame)
        v_surft = vt - KERBIN_OMEGA * r
        v_rel = np.sqrt(vr**2 + v_surft**2)

        # Aerodynamic drag
        rho = self.atmosphere_density(h)
        q = 0.5 * rho * (v_rel**2)
        f_drag = q * self.cda

        if v_rel > 1e-4 and m > 0:
            a_drag_r = -(f_drag / m) * (vr / v_rel)
            a_drag_t = -(f_drag / m) * (v_surft / v_rel)
        else:
            a_drag_r = 0.0
            a_drag_t = 0.0

        # Polar equations of motion in inertial coordinates
        dr = vr
        dtheta = vt / r
        dvr = (vt**2 / r) - (KERBIN_MU / (r**2)) + a_thrust_r + a_drag_r
        dvt = -(vr * vt / r) + a_thrust_t + a_drag_t

        return np.array([dr, dtheta, dvr, dvt]), {
            "h": h, "v_rel": v_rel, "q": q, "drag": f_drag,
            "pitch": pitch_deg, "a_thrust": np.sqrt(a_thrust_r**2 + a_thrust_t**2),
            "a_drag": np.sqrt(a_drag_r**2 + a_drag_t**2)
        }

    def simulate(self, alt_kick=1200.0, pitch_kick=82.0, alt_end_turn=35000.0, min_pitch=30.0, dt=0.1):
        # Initial conditions on launch pad
        r = KERBIN_RADIUS + 78.8 # KSC Launchpad elevation
        theta = 0.0
        vr = 0.0
        vt = KERBIN_V_ROT # Carried by planetary rotation
        t = 0.0

        state = np.array([r, theta, vr, vt], dtype=float)

        telemetry = []
        loss_gravity = 0.0
        loss_drag = 0.0

        for stage_idx, stage in enumerate(self.vehicle["stages"]):
            m_init = stage["m_initial"]
            m_prop = stage["m_propellant"]
            duration = stage["burn_time"]
            t_vac = stage["thrust_vac"]
            t_asl = stage["thrust_asl"]
            mdot = m_prop / duration if duration > 0 else 0.0

            n_steps = max(1, int(round(duration / dt)))
            actual_dt = duration / n_steps

            for step in range(n_steps):
                t_stage = step * actual_dt
                m = m_init - mdot * t_stage

                # Dynamic pressure & atmospheric pressure factor for thrust
                h_curr = state[0] - KERBIN_RADIUS
                p_ratio = np.exp(-h_curr / KERBIN_SCALE_HEIGHT) if h_curr < KERBIN_ATMO_LIMIT else 0.0
                thrust = t_vac - p_ratio * (t_vac - t_asl)

                # RK4 Integration
                k1, info1 = self.equations_of_motion(t, state, thrust, m, alt_kick, pitch_kick, alt_end_turn, min_pitch)
                k2, _ = self.equations_of_motion(t + 0.5 * actual_dt, state + 0.5 * actual_dt * k1, thrust, m - 0.5 * mdot * actual_dt, alt_kick, pitch_kick, alt_end_turn, min_pitch)
                k3, _ = self.equations_of_motion(t + 0.5 * actual_dt, state + 0.5 * actual_dt * k2, thrust, m - 0.5 * mdot * actual_dt, alt_kick, pitch_kick, alt_end_turn, min_pitch)
                k4, _ = self.equations_of_motion(t + actual_dt, state + actual_dt * k3, thrust, m - mdot * actual_dt, alt_kick, pitch_kick, alt_end_turn, min_pitch)

                state += (actual_dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
                t += actual_dt

                # Accumulate delta-v losses
                g_local = KERBIN_MU / (state[0]**2)
                gamma = np.arctan2(state[2], state[3] - KERBIN_OMEGA * state[0]) if (state[2] != 0 or (state[3] - KERBIN_OMEGA * state[0]) != 0) else np.pi / 2
                loss_gravity += g_local * np.sin(gamma) * actual_dt
                loss_drag += (info1["drag"] / m) * actual_dt if m > 0 else 0.0

                telemetry.append({
                    "t": t, "alt": state[0] - KERBIN_RADIUS, "theta": state[1],
                    "downrange_km": (KERBIN_RADIUS * state[1]) / 1000.0,
                    "vr": state[2], "vt": state[3],
                    "v_surf": info1["v_rel"], "pitch": info1["pitch"],
                    "q_kpa": info1["q"] / 1000.0, "mass": m, "stage": stage_idx + 1
                })

        # Calculate orbital elements at burnout
        r_bo = state[0]
        vr_bo = state[2]
        vt_bo = state[3]
        v_bo = np.sqrt(vr_bo**2 + vt_bo**2)
        h_bo = r_bo - KERBIN_RADIUS

        energy = 0.5 * (v_bo**2) - (KERBIN_MU / r_bo)
        if energy < 0:
            a = -KERBIN_MU / (2.0 * energy)
            h_ang = r_bo * vt_bo
            ecc = np.sqrt(max(0.0, 1.0 + (2.0 * energy * (h_ang**2)) / (KERBIN_MU**2)))
            apoapsis = a * (1.0 + ecc) - KERBIN_RADIUS
            periapsis = a * (1.0 - ecc) - KERBIN_RADIUS
            period = 2.0 * np.pi * np.sqrt((a**3) / KERBIN_MU)
        else:
            # Escape trajectory
            a = -KERBIN_MU / (2.0 * energy)
            h_ang = r_bo * vt_bo
            ecc = np.sqrt(1.0 + (2.0 * energy * (h_ang**2)) / (KERBIN_MU**2))
            apoapsis = float('inf')
            periapsis = a * (1.0 - ecc) - KERBIN_RADIUS
            period = float('inf')

        # Find max Q and max G experienced
        max_q = max(row["q_kpa"] for row in telemetry)

        return {
            "burnout_t": t,
            "burnout_alt": h_bo,
            "burnout_v_inertial": v_bo,
            "burnout_v_surf": telemetry[-1]["v_surf"],
            "apoapsis": apoapsis,
            "periapsis": periapsis,
            "eccentricity": ecc,
            "period": period,
            "max_q_kpa": max_q,
            "loss_gravity": loss_gravity,
            "loss_drag": loss_drag,
            "telemetry": telemetry
        }

# ==============================================================================
# GUIDANCE OPTIMIZER (GRID SEARCH)
# ==============================================================================
def optimize_guidance(simulator, target="max_apoapsis", alt_range=(800, 2600, 200), pitch_range=(76.0, 88.0, 1.0)):
    print(f"\n================================================================================")
    print(f"       COROLT SPACE AGENCY (CSA) - kOS GUIDANCE OPTIMIZER (GRID SEARCH)        ")
    print(f"================================================================================")
    print(f"• Vehicle: {simulator.vehicle['name']}")
    print(f"• Cd·A Calibrat: {simulator.cda:.3f} m²")
    print(f"• Rangs: Cota Kick [{alt_range[0]}m .. {alt_range[1]}m], Pitch [{pitch_range[0]}º .. {pitch_range[1]}º]")
    print(f"• Objectiu: {target.upper()}\n")

    results = []
    total_evals = ((alt_range[1] - alt_range[0]) // alt_range[2] + 1) * int((pitch_range[1] - pitch_range[0]) / pitch_range[2] + 1)
    eval_count = 0

    print(f"{'Alt Kick (m)':>12} | {'Pitch (º)':>9} | {'Apoapsi (km)':>12} | {'Max Q (kPa)':>11} | {'Loss Grav (m/s)':>15} | {'Loss Drag (m/s)':>15}")
    print("-" * 84)

    best_res = None
    best_metric = -float('inf')

    for alt_k in range(alt_range[0], alt_range[1] + 1, alt_range[2]):
        for p_k in np.arange(pitch_range[0], pitch_range[1] + 0.1, pitch_range[2]):
            eval_count += 1
            res = simulator.simulate(alt_kick=float(alt_k), pitch_kick=float(p_k))

            ap_km = res["apoapsis"] / 1000.0
            results.append({
                "alt_kick": alt_k,
                "pitch_kick": p_k,
                "apoapsis_km": ap_km,
                "max_q": res["max_q_kpa"],
                "loss_grav": res["loss_gravity"],
                "loss_drag": res["loss_drag"],
                "total_loss": res["loss_gravity"] + res["loss_drag"]
            })

            metric = ap_km if target == "max_apoapsis" else - (res["loss_gravity"] + res["loss_drag"])
            if metric > best_metric:
                best_metric = metric
                best_res = results[-1]

    # Print top 5 candidates
    sorted_res = sorted(results, key=lambda x: x["apoapsis_km"], reverse=True)
    for r in sorted_res[:10]:
        marker = " <-- [ÒPTIM]" if r == best_res else ""
        print(f"{r['alt_kick']:>12} | {r['pitch_kick']:>9.1f} | {r['apoapsis_km']:>12.2f} | {r['max_q']:>11.2f} | {r['loss_grav']:>15.1f} | {r['loss_drag']:>15.1f}{marker}")

    print("\n" + "=" * 84)
    print(f"🎯 CONFIGURACIÓ RECOMANADA PER AL SCRIPT DE kOS:")
    print("=" * 84)
    print(f"DECLARE PARAMETER PITCH_INICIAL IS {best_res['pitch_kick']:.1f}, ALT_KICK IS {best_res['alt_kick']}, RUMB IS 90.")
    print(f"• Apoapsi Teòrica Estimada: {best_res['apoapsis_km']:.2f} km")
    print(f"• Pèrdues Totals de Vol: {best_res['total_loss']:.1f} m/s (Gravetat: {best_res['loss_grav']:.1f} m/s | Drag: {best_res['loss_drag']:.1f} m/s)")
    print(f"• Pressió Dinàmica Màxima (Max Q): {best_res['max_q']:.2f} kPa")
    print("=" * 84)

    return best_res

# ==============================================================================
# CLI INTERFACE
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Corolt Space Agency Ascent Simulator & kOS Optimizer")
    parser.add_argument("--vehicle", default="corolt-3", choices=list(DEFAULT_VEHICLES.keys()), help="Vehicle profile")
    parser.add_argument("--alt-kick", type=float, default=1200.0, help="Cota d'inici de pitch kick (m)")
    parser.add_argument("--pitch-kick", type=float, default=82.0, help="Angle de cabeceig inicial després del kick (º)")
    parser.add_argument("--cda", type=float, default=None, help="Producte de drag efectiu Cd*A (m^2)")
    parser.add_argument("--optimize", action="store_true", help="Executa optimització per cerca en malla (Grid Search)")
    parser.add_argument("--target", default="max_apoapsis", choices=["max_apoapsis", "min_losses"], help="Criteri d'optimització")
    parser.add_argument("--plot", type=str, default=None, help="Ruta del fitxer per desar gràfica SVG/PNG de trajectòria")

    args = parser.parse_args()

    v_config = DEFAULT_VEHICLES[args.vehicle]
    cda = args.cda if args.cda is not None else load_calibrated_cda(args.vehicle)

    sim = AscentSimulator(v_config, cda=cda)

    if args.optimize:
        optimize_guidance(sim, target=args.target)
    else:
        res = sim.simulate(alt_kick=args.alt_kick, pitch_kick=args.pitch_kick)
        print("=" * 70)
        print(f"🚀 CSA ASCENT TRAJECTORY SIMULATION: {v_config['name']}")
        print("=" * 70)
        print(f"• Paràmetres kOS: ALT_KICK = {args.alt_kick:.0f} m | PITCH_INICIAL = {args.pitch_kick:.1f}º")
        print(f"• Producte de Drag (Cd·A): {cda:.3f} m²")
        print("-" * 70)
        print(f"• Temps a Fi de Propulsió: T+{res['burnout_t']:.1f} s")
        print(f"• Cota de Burnout: {res['burnout_alt']/1000.0:.2f} km")
        print(f"• Velocitat Inercial a Burnout: {res['burnout_v_inertial']:.1f} m/s")
        print(f"• Velocitat Superficial a Burnout: {res['burnout_v_surf']:.1f} m/s")
        print(f"• Apoapsi Teòrica (Ap): {res['apoapsis']/1000.0:.2f} km")
        print(f"• Periapsi Teòric (Pe): {res['periapsis']/1000.0:.2f} km")
        print(f"• Excentricitat: {res['eccentricity']:.4f}")
        print(f"• Pressió Dinàmica Màx (Max Q): {res['max_q_kpa']:.2f} kPa")
        print(f"• Pèrdues Gravitatòries (Delta-v): {res['loss_gravity']:.1f} m/s")
        print(f"• Pèrdues Aerodinàmiques (Delta-v): {res['loss_drag']:.1f} m/s")
        print("=" * 70)

        if args.plot:
            try:
                import matplotlib.pyplot as plt
                t_list = [row["t"] for row in res["telemetry"]]
                alt_list = [row["alt"] / 1000.0 for row in res["telemetry"]]
                v_list = [row["v_surf"] for row in res["telemetry"]]
                pitch_list = [row["pitch"] for row in res["telemetry"]]

                fig, ax1 = plt.subplots(figsize=(10, 6))
                ax1.set_title(f"CSA Ascent Simulation - {v_config['name']}\nALT_KICK: {args.alt_kick}m | PITCH: {args.pitch_kick}º | Ap: {res['apoapsis']/1000:.1f}km")
                ax1.plot(t_list, alt_list, 'b-', label="Altitud (km)")
                ax1.set_xlabel("Temps de Vol (s)")
                ax1.set_ylabel("Altitud (km)", color='b')
                ax1.grid(True, linestyle="--", alpha=0.6)

                ax2 = ax1.twinx()
                ax2.plot(t_list, v_list, 'r--', label="Velocitat Superfície (m/s)")
                ax2.plot(t_list, pitch_list, 'g-.', label="Pitch (º)")
                ax2.set_ylabel("Velocitat (m/s) / Pitch (º)", color='r')

                os.makedirs(os.path.dirname(args.plot) or ".", exist_ok=True)
                plt.savefig(args.plot, dpi=150, bbox_inches='tight')
                print(f"[✓] Gràfica de trajectòria desada a: {args.plot}")
            except Exception as e:
                print(f"[!] No s'ha pogut generar la gràfica: {e}")

if __name__ == "__main__":
    main()
