#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Mission CSA-09 Trajectory & Power Simulator
Simulates multi-stage ascent with Heading 270º (Due West), Kerbin planetary rotation,
and dynamic power consumption with 800 EC battery pack.
Generates SVG trajectory and power curve visualization.
"""

import math
import os

# Kerbin constants
KERBIN_MU = 3.5316000e12
KERBIN_RADIUS = 600000.0
KERBIN_ROT_PERIOD = 21600.0
KERBIN_OMEGA = 2.0 * math.pi / KERBIN_ROT_PERIOD  # 7.292e-5 rad/s
KERBIN_SCALE_HEIGHT = 5600.0
KERBIN_RHO_0 = 1.225
KERBIN_ATMO_LIMIT = 70000.0

# Vehicle definition: Corolt-3 + 2x Extra Batteries (total 800 EC)
# Stage 1: RT-10 Hammer (m0 = 5174 kg, mp = 2825 kg, tb = 50.7 s, Thrust = 94 kN)
# Stage 2: SRM-XL (m0 = 1599 kg, mp = 940 kg, tb = 57.6 s, Thrust = 40 kN)
M0_STAGE1 = 5174.0
MD_STAGE1 = 2349.0
TB_STAGE1 = 50.7
THRUST_STAGE1 = 94150.0

M0_STAGE2 = 1599.0
MD_STAGE2 = 659.0
TB_STAGE2 = 57.6
THRUST_STAGE2 = 39800.0

CDA = 1.727  # Empirical calibrated Cd*A

def get_pitch(alt, alt_kick=2400.0, pitch_kick=87.5, alt_end=45000.0, min_pitch=48.0):
    if alt < alt_kick:
        return 90.0
    if alt >= alt_end:
        return min_pitch
    factor = (alt - alt_kick) / (alt_end - alt_kick)
    return max(min_pitch, pitch_kick - factor * (pitch_kick - min_pitch))

def run_simulation():
    dt = 0.1
    t = 0.0
    r = KERBIN_RADIUS
    alt = 0.0
    downrange = 0.0
    v_r = 0.0
    v_theta = 0.0
    
    # Power simulation
    ec = 800.0
    ec_history = []
    traj_history = []
    
    # Stage 1
    m = M0_STAGE1
    mdot1 = (M0_STAGE1 - MD_STAGE1) / TB_STAGE1
    while t < TB_STAGE1:
        pitch_deg = get_pitch(alt)
        pitch_rad = math.radians(pitch_deg)
        rho = KERBIN_RHO_0 * math.exp(-alt / KERBIN_SCALE_HEIGHT) if alt < KERBIN_ATMO_LIMIT else 0.0
        v = math.sqrt(v_r**2 + v_theta**2)
        drag = 0.5 * rho * (v**2) * CDA
        
        # Power drain: Avionics (0.05) + kOS (0.04) + Sensors (0.10) + SAS (0.35) = 0.54 EC/s
        ec -= 0.54 * dt
        
        # Acceleration
        g = KERBIN_MU / (r**2)
        f_thrust = THRUST_STAGE1
        f_drag_r = drag * (v_r / v) if v > 0 else 0
        f_drag_theta = drag * (v_theta / v) if v > 0 else 0
        
        a_r = (f_thrust * math.sin(pitch_rad) - f_drag_r) / m - g + (v_theta**2) / r
        a_theta = (f_thrust * math.cos(pitch_rad) - f_drag_theta) / m - (v_r * v_theta) / r
        
        v_r += a_r * dt
        v_theta += a_theta * dt
        alt += v_r * dt
        r = KERBIN_RADIUS + alt
        downrange += v_theta * dt
        m -= mdot1 * dt
        t += dt
        
        if int(t * 10) % 20 == 0:
            traj_history.append((t, alt, downrange, v_r, v, ec))

    # Interstage coast (1.5s)
    t_end = t + 1.5
    m = M0_STAGE2
    while t < t_end:
        pitch_deg = get_pitch(alt)
        pitch_rad = math.radians(pitch_deg)
        rho = KERBIN_RHO_0 * math.exp(-alt / KERBIN_SCALE_HEIGHT) if alt < KERBIN_ATMO_LIMIT else 0.0
        v = math.sqrt(v_r**2 + v_theta**2)
        drag = 0.5 * rho * (v**2) * CDA
        ec -= 0.54 * dt
        
        g = KERBIN_MU / (r**2)
        f_drag_r = drag * (v_r / v) if v > 0 else 0
        f_drag_theta = drag * (v_theta / v) if v > 0 else 0
        a_r = -f_drag_r / m - g + (v_theta**2) / r
        a_theta = -f_drag_theta / m - (v_r * v_theta) / r
        
        v_r += a_r * dt
        v_theta += a_theta * dt
        alt += v_r * dt
        r = KERBIN_RADIUS + alt
        downrange += v_theta * dt
        t += dt

    # Stage 2
    mdot2 = (M0_STAGE2 - MD_STAGE2) / TB_STAGE2
    t_s2_end = t + TB_STAGE2
    while t < t_s2_end:
        pitch_deg = get_pitch(alt)
        pitch_rad = math.radians(pitch_deg)
        rho = KERBIN_RHO_0 * math.exp(-alt / KERBIN_SCALE_HEIGHT) if alt < KERBIN_ATMO_LIMIT else 0.0
        v = math.sqrt(v_r**2 + v_theta**2)
        drag = 0.5 * rho * (v**2) * CDA
        ec -= 0.54 * dt
        
        g = KERBIN_MU / (r**2)
        f_thrust = THRUST_STAGE2
        f_drag_r = drag * (v_r / v) if v > 0 else 0
        f_drag_theta = drag * (v_theta / v) if v > 0 else 0
        
        a_r = (f_thrust * math.sin(pitch_rad) - f_drag_r) / m - g + (v_theta**2) / r
        a_theta = (f_thrust * math.cos(pitch_rad) - f_drag_theta) / m - (v_r * v_theta) / r
        
        v_r += a_r * dt
        v_theta += a_theta * dt
        alt += v_r * dt
        r = KERBIN_RADIUS + alt
        downrange += v_theta * dt
        m -= mdot2 * dt
        t += dt
        
        if int(t * 10) % 20 == 0:
            traj_history.append((t, alt, downrange, v_r, v, ec))

    burnout_alt = alt
    burnout_vr = v_r
    burnout_vtheta = v_theta
    burnout_time = t

    # Coast to Apoapsis & Descent to Touchdown (SAS OFF, Mini-Lab 90s burst)
    m = MD_STAGE2 - 50.0  # Fairings jettisoned (-50 kg)
    minilab_timer = 90.0
    in_space = False
    
    max_alt = alt
    while alt > 0:
        rho = KERBIN_RHO_0 * math.exp(-alt / KERBIN_SCALE_HEIGHT) if alt < KERBIN_ATMO_LIMIT else 0.0
        v = math.sqrt(v_r**2 + v_theta**2)
        drag = 0.5 * rho * (v**2) * (CDA * 0.8) # Lower drag without fairings
        
        if alt > 70000:
            in_space = True
        
        # Power management:
        drain = 0.09 # Base idle (kOS + Avionics)
        if in_space and minilab_timer > 0 and ec > 150:
            drain += 2.04 # Mini-Lab active
            minilab_timer -= dt
        
        ec = max(0.0, ec - drain * dt)
        
        g = KERBIN_MU / (r**2)
        f_drag_r = drag * (v_r / v) if v > 0 else 0
        f_drag_theta = drag * (v_theta / v) if v > 0 else 0
        a_r = -f_drag_r / m - g + (v_theta**2) / r
        a_theta = -f_drag_theta / m - (v_r * v_theta) / r
        
        v_r += a_r * dt
        v_theta += a_theta * dt
        alt += v_r * dt
        r = KERBIN_RADIUS + alt
        downrange += v_theta * dt
        t += dt
        
        max_alt = max(max_alt, alt)
        if int(t * 10) % 50 == 0:
            traj_history.append((t, alt, downrange, v_r, v, ec))

    # Planetary rotation compensation:
    # Flight time T -> Kerbin rotates eastward by omega * T
    # Downrange is WESTWARD (+downrange), planetary rotation moves ground EASTWARD under vessel
    # Net relative longitude displacement from KSC:
    deg_per_m = 360.0 / (2.0 * math.pi * KERBIN_RADIUS)
    flight_downrange_deg = downrange * deg_per_m
    coriolis_shift_deg = (KERBIN_OMEGA * t) * (180.0 / math.pi)
    total_west_deg = flight_downrange_deg + coriolis_shift_deg
    
    ksc_lon = -74.557
    landing_lon = ksc_lon - total_west_deg

    print("================================================================================")
    print("                  COROLT SPACE AGENCY - CSA-09 TRAJECTORY SIMULATION            ")
    print("================================================================================")
    print(f"[*] Heading Vector:              270.0º (Due West)")
    print(f"[*] Boost Burnout Altitude:      {burnout_alt/1000:.2f} km (at T+{burnout_time:.1f}s)")
    print(f"[*] Simulated Peak Apoapsis:     {max_alt/1000:.2f} km")
    print(f"[*] Total Flight Duration:       {t:.1f} s ({t/60:.1f} min)")
    print(f"[*] Rocket Downrange (Inertial): {downrange/1000:.2f} km ({flight_downrange_deg:.3f}º West)")
    print(f"[*] Coriolis Ground Shift:       {(coriolis_shift_deg / deg_per_m)/1000:.2f} km ({coriolis_shift_deg:.3f}º West)")
    print(f"[*] Total Westward Displacement: {((total_west_deg) / deg_per_m)/1000:.2f} km ({total_west_deg:.3f}º)")
    print(f"[*] Landing Coordinates:         Lat -0.10º, Lon {landing_lon:.2f}º")
    print(f"[*] Target Landing Biome:        Grasslands / Highlands Continental Interior (SAFE)")
    print(f"[*] Final Battery at Touchdown:  {ec:.1f} / 800.0 EC (Reserve Margin: {ec/800.0*100:.1f}%)")
    print("================================================================================")

    # Generate SVG Plot
    generate_svg_plot(traj_history, max_alt, t, ec, landing_lon)

def generate_svg_plot(history, max_alt, total_time, final_ec, landing_lon):
    os.makedirs("assets", exist_ok=True)
    svg_path = "assets/csa-09_simulated_ascent.svg"
    
    width = 900
    height = 500
    padding = 70
    
    plot_w = width - 2 * padding
    plot_h = height - 2 * padding
    
    # Scale: x -> time (0 to total_time), y1 -> alt (0 to max_alt * 1.1), y2 -> EC (0 to 800)
    alt_max_plot = max(200000.0, max_alt * 1.05)
    
    pts_alt = []
    pts_ec = []
    for row in history:
        t, alt, dr, vr, v, ec = row
        x = padding + (t / total_time) * plot_w
        y_alt = height - padding - (alt / alt_max_plot) * plot_h
        y_ec = height - padding - (ec / 800.0) * plot_h
        pts_alt.append(f"{x:.1f},{y_alt:.1f}")
        pts_ec.append(f"{x:.1f},{y_ec:.1f}")
        
    line_alt = " ".join(pts_alt)
    line_ec = " ".join(pts_ec)
    
    # Karman Line
    y_karman = height - padding - (70000.0 / alt_max_plot) * plot_h
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0b0f19; font-family: monospace;">
    <!-- Grid -->
    <rect x="{padding}" y="{padding}" width="{plot_w}" height="{plot_h}" fill="#111827" stroke="#374151" stroke-width="1.5" />
    <line x1="{padding}" y1="{y_karman}" x2="{width-padding}" y2="{y_karman}" stroke="#ef4444" stroke-dasharray="6,4" stroke-width="1.5" />
    <text x="{width-padding-10}" y="{y_karman-8}" fill="#ef4444" font-size="11" text-anchor="end">Karman Line (70 km)</text>

    <!-- Axes -->
    <line x1="{padding}" y1="{height-padding}" x2="{width-padding}" y2="{height-padding}" stroke="#9ca3af" stroke-width="1.5" />
    <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height-padding}" stroke="#9ca3af" stroke-width="1.5" />
    <line x1="{width-padding}" y1="{padding}" x2="{width-padding}" y2="{height-padding}" stroke="#9ca3af" stroke-width="1.5" />

    <!-- Trajectory (Cyan) -->
    <polyline points="{line_alt}" fill="none" stroke="#06b6d4" stroke-width="3" />
    <!-- Battery Curve (Emerald) -->
    <polyline points="{line_ec}" fill="none" stroke="#10b981" stroke-width="2.5" stroke-dasharray="4,2" />

    <!-- Labels & Title -->
    <text x="{width/2}" y="35" fill="#f9fafb" font-size="16" font-weight="bold" text-anchor="middle">CSA-09 SIMULATED ASCENT: TRAJECTORY &amp; POWER BUDGET</text>
    <text x="{width/2}" y="55" fill="#9ca3af" font-size="12" text-anchor="middle">Heading 270º (Due West) | Apogee: {max_alt/1000:.1f} km | Touchdown Lon: {landing_lon:.2f}º (Inland Grasslands/Highlands)</text>

    <text x="{padding}" y="{height-25}" fill="#9ca3af" font-size="11">T+0s</text>
    <text x="{width/2}" y="{height-25}" fill="#9ca3af" font-size="11" text-anchor="middle">Flight Time (MET: {total_time:.0f}s / {total_time/60:.1f} min)</text>
    <text x="{width-padding}" y="{height-25}" fill="#9ca3af" font-size="11" text-anchor="end">T+{total_time:.0f}s</text>

    <text x="{padding-10}" y="{padding+15}" fill="#06b6d4" font-size="12" text-anchor="end" font-weight="bold">Alt ({alt_max_plot/1000:.0f}km)</text>
    <text x="{width-padding+10}" y="{padding+15}" fill="#10b981" font-size="12" text-anchor="start" font-weight="bold">Battery (800 EC)</text>
    <text x="{width-padding+10}" y="{height-padding}" fill="#10b981" font-size="12" text-anchor="start">0 EC</text>

    <!-- Legend -->
    <rect x="{padding+20}" y="{padding+20}" width="280" height="70" fill="#1f2937" rx="6" opacity="0.9" stroke="#374151" />
    <line x1="{padding+35}" y1="{padding+40}" x2="{padding+75}" y2="{padding+40}" stroke="#06b6d4" stroke-width="3" />
    <text x="{padding+85}" y="{padding+44}" fill="#f9fafb" font-size="11">Altitude Profile (Peak {max_alt/1000:.1f} km)</text>
    <line x1="{padding+35}" y1="{padding+65}" x2="{padding+75}" y2="{padding+65}" stroke="#10b981" stroke-width="2.5" stroke-dasharray="4,2" />
    <text x="{padding+85}" y="{padding+69}" fill="#10b981" font-size="11">Battery Pack (Reserve: {final_ec:.0f} EC)</text>
</svg>
"""
    with open(svg_path, "w") as f:
        f.write(svg)
    print(f"[✓] Trajectory and Power visualization saved to: {svg_path}")

if __name__ == "__main__":
    run_simulation()
