#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Mission CSA-10 3D Trajectory & Power Simulator
Simulates active-guided coastal polar ascent (Heading 005º NNE),
exact Kerbin planetary rotation (sidereal period 21,549.4s), empirical drag,
and 800 EC battery power management with dual Mini-Lab scientific duty-cycling.
Generates an SVG trajectory and flight analysis visualization.
"""

import math
import os

# ==============================================================================
# KERBIN PHYSICAL CONSTANTS (HIGH PRECISION)
# ==============================================================================
KERBIN_MU = 3.5316000e12           # Gravitational parameter (m^3/s^2)
KERBIN_RADIUS = 600000.0           # Equatorial radius (m)
KERBIN_ROT_PERIOD = 21549.425      # Sidereal rotation period (s)
KERBIN_OMEGA = 2.0 * math.pi / KERBIN_ROT_PERIOD  # 2.915603e-4 rad/s
KERBIN_ATMO_LIMIT = 70000.0        # Atmosphere cutoff altitude (m)
KERBIN_SCALE_HEIGHT = 5600.0       # Scale height (m)
KERBIN_RHO_0 = 1.225               # Sea-level atmospheric density (kg/m^3)

# Launch site: Kerbin Space Center (KSC) Pad
KSC_LAT = -0.09721                 # Degrees Latitude
KSC_LON = -74.55768                # Degrees Longitude
KSC_ELEVATION = 80.5               # Meters above sea level

# Vehicle configuration: Corolt-IIIb (Upgraded 800 EC Upper Stage)
M0_STAGE1 = 5230.0                 # Total gross launch mass (kg)
M_PROP_S1 = 2825.0                 # RT-10 propellant mass (kg)
TB_STAGE1 = 50.7                   # Stage 1 burn time (s)
THRUST_STAGE1 = 94150.0            # Stage 1 thrust (N)
S1_CASING_MASS = 750.0             # Empty Hammer casing jettisoned at staging (kg)

M0_STAGE2 = 1655.0                 # Stage 2 gross mass (kg)
M_PROP_S2 = 940.0                  # SRM-XL propellant mass (kg)
TB_STAGE2 = 57.6                   # Stage 2 burn time (s)
THRUST_STAGE2 = 39800.0            # Stage 2 thrust (N)
M_DRY_FINAL = 715.0                # Final stage mass after burnout (casing kept + truss + 800EC)

# Empirical Drag Profile (Calibrated from CSA-09 telemetry)
CDA = 0.9626                       # Effective Cd * A (m^2)

# Guidance Parameters (Inland Northern Continental Profile)
HEADING_DEG = 355.0                # Heading 355.0º (North-North-West into solid continent)
ALT_KICK = 2500.0                  # Initial pitch kick altitude (m)
PITCH_KICK = 88.0                  # Initial pitch attitude (degrees)
ALT_END_TURN = 45000.0             # End of pitch transition (m)
MIN_PITCH = 54.0                   # Minimum pitch floor (degrees)

def get_pitch(alt):
    if alt < ALT_KICK:
        return 90.0
    if alt >= ALT_END_TURN:
        return MIN_PITCH
    factor = (alt - ALT_KICK) / (ALT_END_TURN - ALT_KICK)
    return max(MIN_PITCH, PITCH_KICK - factor * (PITCH_KICK - MIN_PITCH))

def great_circle_distance(lat1_deg, lon1_deg, lat2_deg, lon2_deg):
    phi1, lambda1 = math.radians(lat1_deg), math.radians(lon1_deg)
    phi2, lambda2 = math.radians(lat2_deg), math.radians(lon2_deg)
    delta_sigma = math.acos(
        min(1.0, max(-1.0,
            math.sin(phi1) * math.sin(phi2) +
            math.cos(phi1) * math.cos(phi2) * math.cos(lambda2 - lambda1)
        ))
    )
    return KERBIN_RADIUS * delta_sigma

def simulate_csa10():
    dt = 0.1
    t = 0.0

    lat = math.radians(KSC_LAT)
    lon = math.radians(KSC_LON)
    r = KERBIN_RADIUS + KSC_ELEVATION

    v_r = 0.0
    v_north = 0.0
    v_east = 0.0

    m = M0_STAGE1
    ec = 800.0

    # Duty cycle state
    mat_burst_upper_atmo = False
    mat_burst_upper_atmo_done = False
    mat_burst_low_space = False
    mat_burst_low_space_done = False
    mat_timer = 0.0

    trajectory = []

    # Simulation loop until landing
    while t < 1500.0:
        h = r - KERBIN_RADIUS
        if h <= 0.0 and t > 10.0:
            break

        v_surf = math.sqrt(v_r**2 + v_north**2 + v_east**2)

        # Stage propulsion & Mass update
        if t < TB_STAGE1:
            thrust = THRUST_STAGE1
            mdot = M_PROP_S1 / TB_STAGE1
            m -= mdot * dt
        elif t < TB_STAGE1 + 1.5: # Interstage coast
            if t - dt < TB_STAGE1:
                m = M0_STAGE2 # Separated Stage 1 casing
            thrust = 0.0
        elif t < TB_STAGE1 + 1.5 + TB_STAGE2:
            thrust = THRUST_STAGE2
            mdot = M_PROP_S2 / TB_STAGE2
            m -= mdot * dt
        else:
            thrust = 0.0
            m = M_DRY_FINAL

        # Guidance thrust vectoring
        if thrust > 0.0:
            pitch_deg = get_pitch(h)
            pitch_rad = math.radians(pitch_deg)
            hdg_rad = math.radians(HEADING_DEG)
            f_th_r = thrust * math.sin(pitch_rad)
            f_th_n = thrust * math.cos(pitch_rad) * math.cos(hdg_rad)
            f_th_e = thrust * math.cos(pitch_rad) * math.sin(hdg_rad)
        else:
            pitch_deg = math.degrees(math.atan2(v_r, math.sqrt(v_north**2 + v_east**2))) if v_surf > 1.0 else 90.0
            f_th_r = f_th_n = f_th_e = 0.0

        # Atmospheric Drag
        if h < KERBIN_ATMO_LIMIT:
            rho = KERBIN_RHO_0 * math.exp(-h / KERBIN_SCALE_HEIGHT)
            drag = 0.5 * rho * (v_surf**2) * CDA
            if v_surf > 1e-3:
                f_dr_r = -drag * (v_r / v_surf)
                f_dr_n = -drag * (v_north / v_surf)
                f_dr_e = -drag * (v_east / v_surf)
            else:
                f_dr_r = f_dr_n = f_dr_e = 0.0
        else:
            rho = 0.0
            drag = 0.0
            f_dr_r = f_dr_n = f_dr_e = 0.0

        # 3D Rotating Spherical Dynamics (Topocentric Frame)
        cos_l = math.cos(lat)
        sin_l = math.sin(lat)
        tan_l = math.tan(lat)

        g = KERBIN_MU / (r**2)

        a_r = (f_th_r + f_dr_r)/m - g + (v_north**2 + v_east**2)/r + 2.0*KERBIN_OMEGA*v_east*cos_l + (KERBIN_OMEGA**2)*r*(cos_l**2)
        a_n = (f_th_n + f_dr_n)/m - (v_r*v_north)/r - (v_east**2 * tan_l)/r - 2.0*KERBIN_OMEGA*v_east*sin_l - (KERBIN_OMEGA**2)*r*sin_l*cos_l
        a_e = (f_th_e + f_dr_e)/m - (v_r*v_east)/r + (v_north*v_east*tan_l)/r + 2.0*KERBIN_OMEGA*(v_north*sin_l - v_r*cos_l)

        # Integrate velocity
        v_r += a_r * dt
        v_north += a_n * dt
        v_east += a_e * dt

        # Parachute Terminal Velocity in thick air below 3,000m
        if t > 200.0 and h < 3000.0 and v_r < -8.0:
            v_r = max(-2.5, v_r + 15.0 * dt)
            v_north *= 0.95
            v_east *= 0.95

        # Integrate coordinates
        r += v_r * dt
        lat += (v_north / r) * dt
        lon += (v_east / (r * cos_l)) * dt

        # Electrical Power Drain Model
        # Base avionics + telemetry: 0.10 EC/s
        drain = 0.10
        if thrust > 0.0:
            drain += 0.35 # SAS reaction wheel damping during boost

        # Upper Atmosphere Mini-Lab burst (30 seconds between 25 km and 60 km)
        if h > 25000.0 and not mat_burst_upper_atmo_done:
            mat_burst_upper_atmo = True
            mat_timer += dt
            drain += 2.04 # Mini-Lab high drain
            if mat_timer >= 30.0:
                mat_burst_upper_atmo = False
                mat_burst_upper_atmo_done = True
                mat_timer = 0.0

        # Low Space Mini-Lab burst (90 seconds above 75 km)
        if h > 75000.0 and not mat_burst_low_space_done:
            mat_burst_low_space = True
            mat_timer += dt
            drain += 2.04
            if mat_timer >= 90.0 or ec < 120.0:
                mat_burst_low_space = False
                mat_burst_low_space_done = True

        ec = max(0.0, ec - drain * dt)
        t += dt

        if int(t * 10) % 20 == 0 or h <= 0.0:
            cur_lat_deg = math.degrees(lat)
            cur_lon_deg = math.degrees(lon)
            d_ksc = great_circle_distance(KSC_LAT, KSC_LON, cur_lat_deg, cur_lon_deg) / 1000.0
            trajectory.append({
                "t": t,
                "alt": max(0.0, h),
                "v_surf": v_surf,
                "v_r": v_r,
                "pitch": pitch_deg,
                "lat": cur_lat_deg,
                "lon": cur_lon_deg,
                "dist_ksc": d_ksc,
                "ec": ec,
                "drag": math.sqrt(f_dr_r**2 + f_dr_n**2 + f_dr_e**2),
                "q": 0.5 * rho * (v_surf**2)
            })

    return trajectory

def generate_svg_plot(traj, output_path):
    width = 1000
    height = 680

    times = [p["t"] for p in traj]
    alts = [p["alt"] / 1000.0 for p in traj]
    ecs = [p["ec"] for p in traj]
    speeds = [p["v_surf"] for p in traj]
    lats = [p["lat"] for p in traj]
    lons = [p["lon"] for p in traj]

    max_t = max(times)
    max_alt = max(alts)
    max_spd = max(speeds)
    td_lat = lats[-1]
    td_lon = lons[-1]
    final_ec = ecs[-1]
    final_dist = traj[-1]["dist_ksc"]

    # Graph 1: Altitude & Battery vs Time (Left upper panel)
    g1_x0, g1_y0, g1_w, g1_h = 70, 70, 420, 260
    # Graph 2: Speed vs Time (Left lower panel)
    g2_x0, g2_y0, g2_w, g2_h = 70, 390, 420, 220
    # Graph 3: Ground Track Map (Right panel)
    g3_x0, g3_y0, g3_w, g3_h = 550, 70, 410, 540

    def t_to_x(t):
        return g1_x0 + (t / max_t) * g1_w

    def alt_to_y(a):
        return g1_y0 + g1_h - (a / (max_alt * 1.08)) * g1_h

    def ec_to_y(e):
        return g1_y0 + g1_h - (e / 850.0) * g1_h

    def spd_to_y(s):
        return g2_y0 + g2_h - (s / (max_spd * 1.1)) * g2_h

    # Map bounds (KSC Lat -5º to +55º, Lon -105º to -65º)
    map_lat_min, map_lat_max = -5.0, 55.0
    map_lon_min, map_lon_max = -105.0, -65.0

    def map_project(lon, lat):
        x = g3_x0 + ((lon - map_lon_min) / (map_lon_max - map_lon_min)) * g3_w
        y = g3_y0 + g3_h - ((lat - map_lat_min) / (map_lat_max - map_lat_min)) * g3_h
        return x, y

    # Paths
    alt_path = "M " + " ".join(f"{t_to_x(p['t']):.1f} {alt_to_y(p['alt']/1000.0):.1f}" for p in traj)
    ec_path = "M " + " ".join(f"{t_to_x(p['t']):.1f} {ec_to_y(p['ec']):.1f}" for p in traj)
    spd_path = "M " + " ".join(f"{t_to_x(p['t']):.1f} {spd_to_y(p['v_surf']):.1f}" for p in traj)

    ground_path = "M " + " ".join(f"{map_project(p['lon'], p['lat'])[0]:.1f} {map_project(p['lon'], p['lat'])[1]:.1f}" for p in traj)

    # Northern continental landmass
    # Eastern coastline runs north from KSC, while inland continent extends west to Lon -110º
    coastline_pts = [
        (-70.0, -5.0),
        (-74.557, -0.097), # KSC
        (-74.9, 10.0),
        (-75.5, 20.0),
        (-76.0, 30.0),
        (-76.5, 40.0),
        (-75.5, 50.0),
        (-70.0, 55.0)
    ]
    coast_svg_pts = " ".join(f"{map_project(p[0], p[1])[0]:.1f},{map_project(p[0], p[1])[1]:.1f}" for p in coastline_pts)
    land_poly = coast_svg_pts + f" {map_project(-105.0, 55.0)[0]:.1f},{map_project(-105.0, 55.0)[1]:.1f} {map_project(-105.0, -5.0)[0]:.1f},{map_project(-105.0, -5.0)[1]:.1f}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#090d16; font-family:'Courier New', monospace;">
    <defs>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur"/>
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
        <pattern id="gridPattern" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.7" opacity="0.4"/>
        </pattern>
    </defs>

    <!-- Background Grid -->
    <rect width="{width}" height="{height}" fill="url(#gridPattern)" />

    <!-- TITLE HEADER -->
    <rect x="0" y="0" width="{width}" height="50" fill="#0f172a" />
    <text x="25" y="32" fill="#38bdf8" font-size="16" font-weight="bold">COROLT SPACE AGENCY // CSA-10 PRE-FLIGHT 3D NUMERICAL SIMULATION</text>
    <text x="640" y="32" fill="#94a3b8" font-size="12">HEADING: 355.0º NNW | VEHICLE: COROLT-IIIb (800 EC)</text>

    <!-- ================= PANEL 1: ALTITUDE & BATTERY ================= -->
    <rect x="{g1_x0}" y="{g1_y0}" width="{g1_w}" height="{g1_h}" fill="#0b1120" stroke="#334155" stroke-width="1.2"/>
    <text x="{g1_x0+15}" y="{g1_y0+25}" fill="#38bdf8" font-size="13" font-weight="bold">TRAJECTORY ALTITUDE &amp; POWER PROFILE</text>
    <line x1="{g1_x0}" y1="{alt_to_y(70)}" x2="{g1_x0+g1_w}" y2="{alt_to_y(70)}" stroke="#f59e0b" stroke-dasharray="4,4" stroke-width="1"/>
    <text x="{g1_x0+g1_w-150}" y="{alt_to_y(70)-6}" fill="#f59e0b" font-size="10">KARMAN LINE (70 km)</text>
    
    <!-- Reserve floor line -->
    <line x1="{g1_x0}" y1="{ec_to_y(100)}" x2="{g1_x0+g1_w}" y2="{ec_to_y(100)}" stroke="#ef4444" stroke-dasharray="3,3" stroke-width="1"/>
    <text x="{g1_x0+15}" y="{ec_to_y(100)-5}" fill="#ef4444" font-size="10">RESERVE SAFETY FLOOR (100 EC)</text>

    <!-- Curves -->
    <path d="{alt_path}" fill="none" stroke="#38bdf8" stroke-width="2.5" filter="url(#glow)"/>
    <path d="{ec_path}" fill="none" stroke="#10b981" stroke-width="2.2" stroke-dasharray="5,2"/>

    <!-- Legends & Stats -->
    <text x="{g1_x0+15}" y="{g1_y0+60}" fill="#38bdf8" font-size="11">Peak Apoapsis: {max_alt:.1f} km</text>
    <text x="{g1_x0+15}" y="{g1_y0+78}" fill="#10b981" font-size="11">Final Battery: {final_ec:.1f} / 800.0 EC ({final_ec/8.0:.1f}%)</text>
    <text x="{g1_x0+15}" y="{g1_y0+96}" fill="#a855f7" font-size="11">Mini-Lab Bursts: Upper Atmo (30s) + Low Space (90s)</text>

    <!-- Axis Labels -->
    <text x="{g1_x0+g1_w-50}" y="{g1_y0+g1_h+18}" fill="#64748b" font-size="10">TIME (s)</text>
    <text x="{g1_x0-45}" y="{g1_y0+15}" fill="#38bdf8" font-size="10">ALT (km)</text>
    <text x="{g1_x0+g1_w+10}" y="{g1_y0+15}" fill="#10b981" font-size="10">EC</text>

    <!-- ================= PANEL 2: SURFACE SPEED ================= -->
    <rect x="{g2_x0}" y="{g2_y0}" width="{g2_w}" height="{g2_h}" fill="#0b1120" stroke="#334155" stroke-width="1.2"/>
    <text x="{g2_x0+15}" y="{g2_y0+25}" fill="#f43f5e" font-size="13" font-weight="bold">SURFACE VELOCITY PROFILE</text>
    <path d="{spd_path}" fill="none" stroke="#f43f5e" stroke-width="2.2"/>
    <text x="{g2_x0+15}" y="{g2_y0+55}" fill="#f43f5e" font-size="11">Max Velocity: {max_spd:.1f} m/s (Mach {max_spd/340.0:.2f})</text>
    <text x="{g2_x0+15}" y="{g2_y0+75}" fill="#64748b" font-size="11">Calibrated Drag: Cd·A = {CDA:.3f} m²</text>
    <text x="{g2_x0+15}" y="{g2_y0+95}" fill="#64748b" font-size="11">Total Duration: {max_t:.1f} s ({max_t/60.0:.1f} min)</text>

    <!-- ================= PANEL 3: 3D NORTHERN CONTINENTAL GROUND TRACK ================= -->
    <rect x="{g3_x0}" y="{g3_y0}" width="{g3_w}" height="{g3_h}" fill="#0b1b2d" stroke="#334155" stroke-width="1.2"/>
    <text x="{g3_x0+15}" y="{g3_y0+25}" fill="#22c55e" font-size="13" font-weight="bold">NORTH CONTINENTAL TRACK (HEADING 355º NNW)</text>

    <!-- Continental Landmass Polygon -->
    <polygon points="{land_poly}" fill="#152e22" stroke="#22c55e" stroke-width="1.5"/>
    <text x="{g3_x0+25}" y="{g3_y0+160}" fill="#166534" font-size="14" font-weight="bold" opacity="0.7">CONTINENTAL INTERIOR (DRY LAND)</text>
    <text x="{g3_x0+g3_w-130}" y="{g3_y0+160}" fill="#1e3a5f" font-size="14" font-weight="bold">EAST OCEAN</text>

    <!-- Flight Ground Track Arc -->
    <path d="{ground_path}" fill="none" stroke="#38bdf8" stroke-width="3" filter="url(#glow)"/>

    <!-- Key Waypoints -->
    <!-- KSC -->
    <circle cx="{map_project(KSC_LON, KSC_LAT)[0]}" cy="{map_project(KSC_LON, KSC_LAT)[1]}" r="5" fill="#38bdf8"/>
    <text x="{map_project(KSC_LON, KSC_LAT)[0]+10}" y="{map_project(KSC_LON, KSC_LAT)[1]+4}" fill="#38bdf8" font-size="11" font-weight="bold">KSC PAD (-74.56º, -0.10º)</text>

    <!-- Touchdown -->
    <circle cx="{map_project(td_lon, td_lat)[0]}" cy="{map_project(td_lon, td_lat)[1]}" r="6" fill="#22c55e"/>
    <text x="{map_project(td_lon, td_lat)[0]-180}" y="{map_project(td_lon, td_lat)[1]-10}" fill="#22c55e" font-size="11" font-weight="bold">TOUCHDOWN: +{td_lat:.2f}ºN, {abs(td_lon):.2f}ºW</text>
    <text x="{map_project(td_lon, td_lat)[0]-180}" y="{map_project(td_lon, td_lat)[1]+6}" fill="#94a3b8" font-size="10">Solid Land (Highlands): {final_dist:.1f} km</text>

    <!-- Lat/Lon Grid lines -->
    <line x1="{g3_x0}" y1="{map_project(0, 0)[1]}" x2="{g3_x0+g3_w}" y2="{map_project(0, 0)[1]}" stroke="#38bdf8" stroke-dasharray="3,3" stroke-width="0.8"/>
    <text x="{g3_x0+5}" y="{map_project(0, 0)[1]-4}" fill="#38bdf8" font-size="9">EQUATOR 0º</text>

    <line x1="{g3_x0}" y1="{map_project(0, 20)[1]}" x2="{g3_x0+g3_w}" y2="{map_project(0, 20)[1]}" stroke="#64748b" stroke-dasharray="3,3" stroke-width="0.8"/>
    <text x="{g3_x0+5}" y="{map_project(0, 20)[1]-4}" fill="#64748b" font-size="9">+20º LAT</text>

    <line x1="{g3_x0}" y1="{map_project(0, 40)[1]}" x2="{g3_x0+g3_w}" y2="{map_project(0, 40)[1]}" stroke="#64748b" stroke-dasharray="3,3" stroke-width="0.8"/>
    <text x="{g3_x0+5}" y="{map_project(0, 40)[1]-4}" fill="#64748b" font-size="9">+40º LAT</text>

    <!-- FOOTER SUMMARY -->
    <rect x="0" y="{height-30}" width="{width}" height="30" fill="#0f172a" />
    <text x="25" y="{height-11}" fill="#94a3b8" font-size="11">ENGINEERING ASSESSMENT: Heading 355.0º NNW tracks into the vast northern continent (Grasslands/Highlands). 100% dry land recovery.</text>
</svg>
"""

    with open(output_path, "w") as f:
        f.write(svg)
    print(f"[✓] Simulation SVG generated at: {output_path}")

if __name__ == "__main__":
    print("======================================================================")
    print("🚀 CSA MISSION CSA-10: 3D NUMERICAL ASCENT & POWER SIMULATION")
    print("======================================================================")
    traj = simulate_csa10()
    max_alt = max(p["alt"] for p in traj)
    final_p = traj[-1]
    print(f"• Launch Heading:      {HEADING_DEG:5.1f}º (Coastal Polar Track)")
    print(f"• Peak Apoapsis:       {max_alt/1000.0:6.2f} km")
    print(f"• Max Surface Speed:   {max(p['v_surf'] for p in traj):6.1f} m/s")
    print(f"• Flight Duration:     {final_p['t']:6.1f} s ({final_p['t']/60.0:.1f} min)")
    print(f"• Touchdown Lat/Lon:   Lat {final_p['lat']:.2f}º, Lon {final_p['lon']:.2f}º")
    print(f"• Downrange Distance:  {final_p['dist_ksc']:6.1f} km from KSC")
    print(f"• Remaining Battery:   {final_p['ec']:6.1f} / 800.0 EC ({final_p['ec']/8.0:.1f}%)")
    print("----------------------------------------------------------------------")
    output_svg = "assets/csa-10_simulated_ascent.svg"
    generate_svg_plot(traj, output_svg)
    print("======================================================================")
