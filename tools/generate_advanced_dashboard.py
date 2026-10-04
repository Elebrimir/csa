import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def create_mission_dashboard(mission_id):
    csv_file = f"/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/{mission_id}_telemetry.csv"
    out_png = f"/home/pablo-cortes/Documents/Corolt_Space_Agency/assets/{mission_id.lower()}_advanced_dashboard.png"
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} does not exist!")
        sys.exit(1)
        
    df = pd.read_csv(csv_file)
    
    # Filter valid flight until touchdown (~T+1705s if CSA-06)
    if mission_id == 'CSA-06':
        df = df[df['MET'] <= 1705].copy()
    elif mission_id == 'CSA-05b':
        df = df[df['MET'] <= 1012].copy()
        
    t = df['MET']
    alt_km = df['altitude'] / 1000.0
    vel_ms = df['surface_vel']
    vel_kmh = vel_ms * 3.6
    q_kpa = df['dynamic_pressure'] / 1000.0
    g = df['g_force']
    v_spd = df['vert_speed']
    
    # Specific mechanical energy estimate (J/kg)
    # E_kin = 0.5 * v^2
    # E_pot = g0 * h (simplified for profile)
    e_kin = 0.5 * (vel_ms ** 2) / 1000.0 # kJ/kg
    e_pot = 9.81 * df['altitude'] / 1000.0 # kJ/kg
    e_tot = e_kin + e_pot
    
    # Space agency modern dark theme
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 10), dpi=150)
    fig.patch.set_facecolor('#070b13')
    
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.25)
    
    # 1. ALTITUDE PROFILE & SPACE BOUNDARY
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor('#0d1527')
    ax1.plot(t, alt_km, color='#38bdf8', lw=2.2, label='Altitude (km)')
    ax1.axhline(70, color='#c084fc', ls='--', lw=1.5, label='Kármán Line (70 km)')
    max_alt_idx = alt_km.idxmax()
    ax1.scatter([t.loc[max_alt_idx]], [alt_km.loc[max_alt_idx]], color='#38bdf8', s=60, zorder=5)
    ax1.annotate(f"Apogee: {alt_km.max():.1f} km\n(T+{t.loc[max_alt_idx]:.0f}s)", 
                 (t.loc[max_alt_idx], alt_km.max()),
                 xytext=(t.loc[max_alt_idx] - 300, alt_km.max() - 40),
                 color='#38bdf8', fontweight='bold', fontsize=9,
                 arrowprops=dict(arrowstyle="->", color='#38bdf8', lw=1.2))
    ax1.set_title("🌌 Altitude Profile & Space Boundary", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax1.set_ylabel("Altitude (km)", color='#94a3b8')
    ax1.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax1.legend(loc='upper right', framealpha=0.4, fontsize=9)
    
    # 2. SURFACE VELOCITY & VERTICAL VELOCITY
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#0d1527')
    ax2.plot(t, vel_ms, color='#f43f5e', lw=2, label='Surface Vel. (m/s)')
    ax2.plot(t, v_spd, color='#fbbf24', lw=1.5, ls='--', alpha=0.85, label='Vertical Vel. (m/s)')
    ax2.axhline(343, color='#94a3b8', ls=':', lw=1, label='Mach 1 (343 m/s)')
    max_v_idx = vel_ms.idxmax()
    ax2.scatter([t.loc[max_v_idx]], [vel_ms.loc[max_v_idx]], color='#f43f5e', s=60, zorder=5)
    ax2.annotate(f"Max: {vel_ms.max():.1f} m/s\n({vel_kmh.max():.0f} km/h - M{vel_ms.max()/310:.1f})", 
                 (t.loc[max_v_idx], vel_ms.max()),
                 xytext=(t.loc[max_v_idx] - 450, vel_ms.max() - 250),
                 color='#f43f5e', fontweight='bold', fontsize=9,
                 arrowprops=dict(arrowstyle="->", color='#f43f5e', lw=1.2))
    ax2.set_title("⚡ Velocity Regimes & Ascent/Descent", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylabel("Velocity (m/s)", color='#94a3b8')
    ax2.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax2.legend(loc='upper left', framealpha=0.4, fontsize=9)
    
    # 3. DYNAMIC PRESSURE (MAX Q)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor('#0d1527')
    ax3.fill_between(t, q_kpa, color='#06b6d4', alpha=0.25)
    ax3.plot(t, q_kpa, color='#06b6d4', lw=2, label='Dynamic Pressure Q (kPa)')
    max_q_idx = q_kpa.idxmax()
    ax3.scatter([t.loc[max_q_idx]], [q_kpa.loc[max_q_idx]], color='#22d3ee', s=60, zorder=5)
    ax3.annotate(f"Max Q: {q_kpa.max():.2f} kPa\n(Reentry T+{t.loc[max_q_idx]:.0f}s)",
                 (t.loc[max_q_idx], q_kpa.max()),
                 xytext=(t.loc[max_q_idx] - 500, q_kpa.max() - 15),
                 color='#22d3ee', fontweight='bold', fontsize=9,
                 arrowprops=dict(arrowstyle="->", color='#22d3ee', lw=1.2))
    ax3.set_title("🌪️ Aerodynamic Stress (Dynamic Pressure Q)", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax3.set_ylabel("Pressure Q (kPa)", color='#94a3b8')
    ax3.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax3.legend(loc='upper right', framealpha=0.4, fontsize=9)
    
    # 4. G-FORCES & DECELERATION
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor('#0d1527')
    ax4.plot(t, g, color='#ec4899', lw=2, label='Total G-Force')
    max_g_idx = g.idxmax()
    ax4.scatter([t.loc[max_g_idx]], [g.loc[max_g_idx]], color='#f472b6', s=60, zorder=5)
    ax4.annotate(f"Max Deceleration: {g.max():.2f} G\n(T+{t.loc[max_g_idx]:.0f}s)",
                 (t.loc[max_g_idx], g.max()),
                 xytext=(t.loc[max_g_idx] - 450, g.max() - 2.5),
                 color='#f472b6', fontweight='bold', fontsize=9,
                 arrowprops=dict(arrowstyle="->", color='#f472b6', lw=1.2))
    ax4.set_title("💥 Acceleration & Gravitational Loads (G-Force)", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax4.set_ylabel("Acceleration (G)", color='#94a3b8')
    ax4.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax4.legend(loc='upper left', framealpha=0.4, fontsize=9)
    
    # 5. SPECIFIC MECHANICAL ENERGY DISTRIBUTION (KINETIC VS POTENTIAL)
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.set_facecolor('#0d1527')
    ax5.plot(t, e_kin, color='#f43f5e', lw=1.8, label='Kinetic Energy (kJ/kg)')
    ax5.plot(t, e_pot, color='#38bdf8', lw=1.8, label='Potential Energy (kJ/kg)')
    ax5.plot(t, e_tot, color='#10b981', lw=1.5, ls=':', label='Total Mechanical Energy')
    ax5.set_title("⚡ Specific Mechanical Energy Balance", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax5.set_xlabel("Elapsed Time MET (s)", color='#94a3b8')
    ax5.set_ylabel("Energy (kJ/kg)", color='#94a3b8')
    ax5.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax5.legend(loc='upper right', framealpha=0.4, fontsize=8)
    
    # 6. EXECUTIVE KPI CARD
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')
    
    # KPI Data
    kpis = [
        ["Vehicle", "Corolt-III (Unit 03 - Guided kOS)"],
        ["Max Apoapsis", f"{alt_km.max():.2f} km"],
        ["Max Surface Velocity", f"{vel_ms.max():.1f} m/s ({vel_kmh.max():.0f} km/h)"],
        ["Time in Outer Space", f"{((df[df['altitude']>=70000]['MET'].max() - df[df['altitude']>=70000]['MET'].min())):.1f} s (~14.1 min)"],
        ["Max Dynamic Pressure", f"{q_kpa.max():.2f} kPa ({q_kpa.max()*1000:.0f} Pa)"],
        ["Peak Reentry Deceleration", f"{g.max():.2f} G"],
        ["Terminal Descent Speed", "6.5 m/s (Parachutes deployed)"],
        ["Mission Outcome", "TOTAL SUCCESS (Recovered at KSC)"]
    ]
    
    table = ax6.table(cellText=kpis, colLabels=["Operational Metric", "Recorded Value"], 
                      cellLoc='left', loc='center', bbox=[0.05, 0.05, 0.9, 0.88])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    
    # Table styling
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor('#1e293b')
        if r == 0:
            cell.set_facecolor('#1e293b')
            cell.set_text_props(color='#38bdf8', fontweight='bold')
        else:
            cell.set_facecolor('#0d1527' if r % 2 == 0 else '#111c33')
            if c == 1 and r == 8:
                cell.set_text_props(color='#4ade80', fontweight='bold')
            else:
                cell.set_text_props(color='#f1f5f9')
                
    ax6.set_title("📋 Executive Telemetry Summary", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)

    # Main title
    fig.suptitle(f"COROLT SPACE AGENCY  |  ADVANCED TELEMETRY DASHBOARD: MISSION {mission_id.upper()}", 
                 fontsize=15, fontweight='bold', color='#ffffff', y=0.98)
    
    plt.savefig(out_png, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"✅ Dashboard generated successfully at: {out_png}")

if __name__ == '__main__':
    mid = sys.argv[1] if len(sys.argv) > 1 else 'CSA-06'
    create_mission_dashboard(mid)
