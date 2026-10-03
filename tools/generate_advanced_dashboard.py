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
        print(f"Error: {csv_file} no existeix!")
        sys.exit(1)
        
    df = pd.read_csv(csv_file)
    
    # Filtrar vol vàlid fins l'aterratge (~T+1705s si és CSA-06)
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
    
    # Estimació energètica específica (J/kg)
    # E_cin = 0.5 * v^2
    # E_pot = g0 * h (simplificat per perfil)
    e_kin = 0.5 * (vel_ms ** 2) / 1000.0 # kJ/kg
    e_pot = 9.81 * df['altitude'] / 1000.0 # kJ/kg
    e_tot = e_kin + e_pot
    
    # Estil fosc d'agència espacial (modern dark theme)
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 10), dpi=150)
    fig.patch.set_facecolor('#070b13')
    
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.25)
    
    # 1. PERFIL D'ALTITUD I FRONTERA ESPACIAL
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor('#0d1527')
    ax1.plot(t, alt_km, color='#38bdf8', lw=2.2, label='Altitud (km)')
    ax1.axhline(70, color='#c084fc', ls='--', lw=1.5, label='Línia Kármán (70 km)')
    max_alt_idx = alt_km.idxmax()
    ax1.scatter([t.loc[max_alt_idx]], [alt_km.loc[max_alt_idx]], color='#38bdf8', s=60, zorder=5)
    ax1.annotate(f"Apogeu: {alt_km.max():.1f} km\n(T+{t.loc[max_alt_idx]:.0f}s)", 
                 (t.loc[max_alt_idx], alt_km.max()),
                 xytext=(t.loc[max_alt_idx] - 300, alt_km.max() - 40),
                 color='#38bdf8', fontweight='bold', fontsize=9,
                 arrowprops=dict(arrowstyle="->", color='#38bdf8', lw=1.2))
    ax1.set_title("🌌 Perfil d'Altitud i Límit Espacial", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax1.set_ylabel("Altitud (km)", color='#94a3b8')
    ax1.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax1.legend(loc='upper right', framealpha=0.4, fontsize=9)
    
    # 2. VELOCITAT DE SUPERFÍCIE I VELOCITAT VERTICAL
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#0d1527')
    ax2.plot(t, vel_ms, color='#f43f5e', lw=2, label='Vel. Superfície (m/s)')
    ax2.plot(t, v_spd, color='#fbbf24', lw=1.5, ls='--', alpha=0.85, label='Vel. Vertical (m/s)')
    ax2.axhline(343, color='#94a3b8', ls=':', lw=1, label='Mach 1 (343 m/s)')
    max_v_idx = vel_ms.idxmax()
    ax2.scatter([t.loc[max_v_idx]], [vel_ms.loc[max_v_idx]], color='#f43f5e', s=60, zorder=5)
    ax2.annotate(f"Màx: {vel_ms.max():.1f} m/s\n({vel_kmh.max():.0f} km/h - M{vel_ms.max()/310:.1f})", 
                 (t.loc[max_v_idx], vel_ms.max()),
                 xytext=(t.loc[max_v_idx] - 450, vel_ms.max() - 250),
                 color='#f43f5e', fontweight='bold', fontsize=9,
                 arrowprops=dict(arrowstyle="->", color='#f43f5e', lw=1.2))
    ax2.set_title("⚡ Règim de Velocitat i Ascens/Descens", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylabel("Velocitat (m/s)", color='#94a3b8')
    ax2.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax2.legend(loc='upper left', framealpha=0.4, fontsize=9)
    
    # 3. PRESSIÓ DINÀMICA (MAX Q)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor('#0d1527')
    ax3.fill_between(t, q_kpa, color='#06b6d4', alpha=0.25)
    ax3.plot(t, q_kpa, color='#06b6d4', lw=2, label='Pressió Dinàmica Q (kPa)')
    max_q_idx = q_kpa.idxmax()
    ax3.scatter([t.loc[max_q_idx]], [q_kpa.loc[max_q_idx]], color='#22d3ee', s=60, zorder=5)
    ax3.annotate(f"Max Q: {q_kpa.max():.2f} kPa\n(Reentrada T+{t.loc[max_q_idx]:.0f}s)",
                 (t.loc[max_q_idx], q_kpa.max()),
                 xytext=(t.loc[max_q_idx] - 500, q_kpa.max() - 15),
                 color='#22d3ee', fontweight='bold', fontsize=9,
                 arrowprops=dict(arrowstyle="->", color='#22d3ee', lw=1.2))
    ax3.set_title("🌪️ Estrès Aerodinàmic (Pressió Dinàmica Q)", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax3.set_ylabel("Pressió Q (kPa)", color='#94a3b8')
    ax3.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax3.legend(loc='upper right', framealpha=0.4, fontsize=9)
    
    # 4. FORCES G I DECELERACIÓ
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor('#0d1527')
    ax4.plot(t, g, color='#ec4899', lw=2, label='Força G total')
    max_g_idx = g.idxmax()
    ax4.scatter([t.loc[max_g_idx]], [g.loc[max_g_idx]], color='#f472b6', s=60, zorder=5)
    ax4.annotate(f"Màx Deceleració: {g.max():.2f} G\n(T+{t.loc[max_g_idx]:.0f}s)",
                 (t.loc[max_g_idx], g.max()),
                 xytext=(t.loc[max_g_idx] - 450, g.max() - 2.5),
                 color='#f472b6', fontweight='bold', fontsize=9,
                 arrowprops=dict(arrowstyle="->", color='#f472b6', lw=1.2))
    ax4.set_title("💥 Càrregues d'Acceleració i Gravetat (G-Force)", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax4.set_ylabel("Acceleració (G)", color='#94a3b8')
    ax4.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax4.legend(loc='upper left', framealpha=0.4, fontsize=9)
    
    # 5. DISTRIBUCIÓ D'ENERGIA MECÀNICA ESPECÍFICA (CINÈTICA VS POTENCIAL)
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.set_facecolor('#0d1527')
    ax5.plot(t, e_kin, color='#f43f5e', lw=1.8, label='Energia Cinètica (kJ/kg)')
    ax5.plot(t, e_pot, color='#38bdf8', lw=1.8, label='Energia Potencial (kJ/kg)')
    ax5.plot(t, e_tot, color='#10b981', lw=1.5, ls=':', label='Energia Mecànica Total')
    ax5.set_title("⚡ Balanç d'Energia Mecànica Específica", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)
    ax5.set_xlabel("Temps Transcorregut MET (s)", color='#94a3b8')
    ax5.set_ylabel("Energia (kJ/kg)", color='#94a3b8')
    ax5.grid(True, ls=':', color='#1e293b', alpha=0.7)
    ax5.legend(loc='upper right', framealpha=0.4, fontsize=8)
    
    # 6. TAULA D'INDICADORS CLAU (KPIs EXECUTIVE CARD)
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')
    
    # Dades resum
    kpis = [
        ["Vehicle", "Corolt-III (Unitat 03 - kOS)"],
        ["Apogeu Màxim", f"{alt_km.max():.2f} km"],
        ["Velocitat Màx Superfície", f"{vel_ms.max():.1f} m/s ({vel_kmh.max():.0f} km/h)"],
        ["Temps a l'Espai Exterior", f"{((df[df['altitude']>=70000]['MET'].max() - df[df['altitude']>=70000]['MET'].min())):.1f} s (~14,1 min)"],
        ["Màxima Pressió Dinàmica", f"{q_kpa.max():.2f} kPa ({q_kpa.max()*1000:.0f} Pa)"],
        ["Pico d'Acceleració Reentrada", f"{g.max():.2f} G"],
        ["Velocitat de Descens Terminal", "6,5 m/s (Paracaigudes desplegat)"],
        ["Resultat de la Missió", "ÈXIT TOTAL (Recuperat al KSC)"]
    ]
    
    table = ax6.table(cellText=kpis, colLabels=["Mètrica Operativa", "Valor Registrat"], 
                      cellLoc='left', loc='center', bbox=[0.05, 0.05, 0.9, 0.88])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    
    # Estil de la taula
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
                
    ax6.set_title("📋 Quadre de Comandament Executiu", color='#f8fafc', fontsize=12, fontweight='bold', pad=10)

    # Títol principal
    fig.suptitle(f"COROLT SPACE AGENCY  |  QUADRE TELEMÈTRIC AVANÇAT: MISSIÓ {mission_id.upper()}", 
                 fontsize=15, fontweight='bold', color='#ffffff', y=0.98)
    
    plt.savefig(out_png, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"✅ Dashboard generat amb èxit a: {out_png}")

if __name__ == '__main__':
    mid = sys.argv[1] if len(sys.argv) > 1 else 'CSA-06'
    create_mission_dashboard(mid)
