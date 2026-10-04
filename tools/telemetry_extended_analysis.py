import sys
import os
import pandas as pd
import numpy as np

def analyze_flight(mission_id):
    csv_file = f"/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/{mission_id}_telemetry.csv"
    if not os.path.exists(csv_file):
        print(f"Error: No s'ha trobat el fitxer {csv_file}")
        sys.exit(1)
        
    df = pd.read_csv(csv_file)
    print(f"==================================================")
    print(f"📊 ANÀLISI TELEMÈTRICA EXTESA: {mission_id}")
    print(f"==================================================")
    print(f"• Mostres totals enregistrades: {len(df):,}")
    print(f"• Durada total telemètrica (MET): {df['MET'].max():.1f} s ({df['MET'].max()/60:.2f} min)")
    
    # Cinemàtica i cotes
    ap_idx = df['altitude'].idxmax()
    ap_row = df.loc[ap_idx]
    print(f"\n🚀 ALTITUD I APOGEU:")
    print(f"• Altitud Màxima: {ap_row['altitude']:,.2f} m ({ap_row['altitude']/1000:.2f} km) a T+{ap_row['MET']:.1f} s")
    print(f"• Apoapsi Teòrica Màxima: {df['apoapsis'].max():,.2f} m ({df['apoapsis'].max()/1000:.2f} km)")
    
    # Temps a l'espai
    space_df = df[df['altitude'] >= 70000]
    if not space_df.empty:
        t_space = space_df['MET'].max() - space_df['MET'].min()
        print(f"• Temps a l'Espai Exterior (≥70 km): {t_space:.1f} s ({t_space/60:.2f} min)")
    else:
        print(f"• Temps a l'Espai: 0 s (vol endoatmosfèric)")
        
    # Dinàmica i Velocitat
    v_s_max_idx = df['surface_vel'].idxmax()
    v_s_max = df.loc[v_s_max_idx]
    print(f"\n💨 DINÀMICA I VELOCITAT:")
    print(f"• Velocitat Superfície Màx: {v_s_max['surface_vel']:.1f} m/s ({v_s_max['surface_vel']*3.6:.1f} km/h, Mach ~{v_s_max['surface_vel']/310:.2f}) a T+{v_s_max['MET']:.1f} s")
    print(f"• Velocitat Orbital Màx: {df['orbital_vel'].max():.1f} m/s")
    print(f"• Pressió Dinàmica Màx (Max Q): {df['dynamic_pressure'].max():.1f} Pa ({df['dynamic_pressure'].max()/1000:.2f} kPa)")
    print(f"• Força G Màxima: {df['g_force'].max():.2f} G")
    
    # Fase d'aterratge / recuperació
    # Busquem el punt d'obertura del paracaigudes o descens terminal
    terminal = df[(df['MET'] > 1300) & (df['altitude'] < 5000)]
    if not terminal.empty:
        avg_descent_vel = terminal[terminal['vert_speed'] < 0]['vert_speed'].mean()
        print(f"\n🪂 REENTRADA I ATERRATGE:")
        print(f"• Velocitat mitjana de descens sota paracaigudes: {abs(avg_descent_vel):.2f} m/s")
        td = df[(df['MET'] > 1300) & (df['radar_alt'] < 1.0)]
        if not td.empty:
            td_row = td.iloc[0]
            print(f"• Aterratge registrat a T+{td_row['MET']:.1f} s a cota {td_row['altitude']:.1f} m (radar {td_row['radar_alt']:.1f} m)")
    print(f"==================================================\n")

if __name__ == '__main__':
    mid = sys.argv[1] if len(sys.argv) > 1 else 'CSA-06'
    analyze_flight(mid)
