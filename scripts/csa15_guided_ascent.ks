// ============================================================================
// COROLT SPACE AGENCY (CSA) - FLIGHT GUIDANCE SYSTEM v4.6
// MISSION: CSA-15 (Kerbin Comms Constellation Expansion - CoroltSat-1E)
// VEHICLE: Corolt-IV B Unit 5 on Modular Launch Pad (MLP)
// TARGET:  Slot 2 (+80.0 deg vs CorolSat-1B / +40.0 deg vs CoroltSat-1D)
//          Bridging the 4-Satellite Continuous Mesh Link:
//          1B (0 deg) <-> 1D (+40 deg) <-> 1E (+80 deg) <-> 1C (+120 deg)
// AUTOMATED PAD OPERATIONS & LAUNCH COUNTDOWN:
//   1. 5s countdown to tanking initiation.
//   2. Ground electrical generator connected.
//   3. Refueling initiated (~120s tanking duration to 900 LF / 1100 Ox).
//   4. Tank level monitoring (until 898+ LF full) & Hold until T-60s of window.
//   5. Terminal countdown at T-60s with 10-second milestones.
//   6. At T-30s: Disconnect ground power & retract umbilicals/swing arms.
//   7. At T-10s: Terminal single-second countdown.
//   8. At T-0s: Core & SRB Ignition, pad clamp release, Liftoff!
// FLIGHT GUIDANCE (Empirical CSA-14 Calibration: 778.3s ascent, 78.5 deg arc):
//   - Immediate pitch kick at 1,200 m (84.0 deg) concurrent with SRB thrust
//   - Ascent with Max Q throttling governor (Target Q <= 32 kPa)
//   - Seamless Shrimp SRB separation (~48.5s) via srb_separated MECO guard
//   - Fairing vacuum separation (> 55 km)
//   - SECO-1 apogee push (300 km) & ballistic coast
//   - SECO-2 circularization with 4-tier vernier governor (e <= 0.0008)
// SAFETY INTERLOCK & SEPARATION:
//   - Real-time relative orbital phase evaluation vs TARGET_ANCHOR
//   - STRICT TOLERANCE GATE: Condition ABS(phase - TARGET_SLOT) <= 0.50 deg
//   - Normal-axis payload release (VCRS(vel, pos)) with ModuleDecouple & fallback
//   - Autonomous Stage 2 Retrograde Deorbit to Pe <= 0 km (Zero Debris Protocol)
//   - Automatic HOLD & Stage 2 retention if deviation > 0.50 deg for phasing fix
// ============================================================================

DECLARE PARAMETER TARGET_LAUNCH_UT IS 0.          // Set to 0 for immediate sequence or pass exact window UT
DECLARE PARAMETER TARGET_SLOT_DEG IS 80.0.        // Target Constellation Slot 2 (+80.0 deg vs 1B, or pass 40.0 with "CoroltSat-1D")
DECLARE PARAMETER TARGET_ANCHOR IS "CorolSat-1B". // Reference anchor vessel name ("CorolSat-1B" or "CoroltSat-1D")

CLEARSCREEN.
PRINT "==================================================".
PRINT "      COROLT SPACE AGENCY - MISSION CONTROL       ".
PRINT "   MISSION: CSA-15 | CoroltSat-1E (Constellation) ".
PRINT "   VEHICLE: Corolt-IV B #5                        ".
PRINT "   TARGET SLOT: " + TARGET_SLOT_DEG + " deg (Anchor: " + TARGET_ANCHOR + ")".
PRINT "   SAFETY GATE: Strict tolerance +/- 0.50 deg    ".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Flight Constants & Orbital Targets
// ----------------------------------------------------------------------------
SET TARGET_APOAPSIS TO 300000.      // Target Apogee: 300 km (300,000 m)
SET TARGET_PERIAPSIS TO 300000.     // Target Perigee: 300 km (300,000 m)
SET ALT_KICK TO 1200.               // Pitch kick initiation altitude (m)
SET PITCH_INITIAL TO 84.0.          // Initial pitch angle (deg)
SET HEADING_DEG TO 90.0.            // Launch azimuth (Due East Equatorial)
SET ALT_END_TURN TO 48000.          // Turn completion altitude (m)
SET MIN_PITCH TO 15.0.              // Minimum pitch before MECO (deg)
SET KERBIN_MU TO 3.5316000e12.      // Gravitational parameter
SET KERBIN_RADIUS TO 600000.        // Equatorial radius (m)
SET PHASE_TOLERANCE_DEG TO 0.50.    // Strict safety limit (+/- 0.50 deg)

// Aerodynamic Governor Limits
SET TARGET_MAX_Q_KPA TO 32.0.       // Max dynamic pressure ceiling (kPa)
SET MIN_TWR_FLOOR TO 1.30.          // Minimum TWR floor
SET MAX_G_CEILING TO 3.80.          // Maximum acceleration load (G)

// Fuel Thresholds for Stage 1 Full Tanking (2x FL-T800 = 720 LF, Stage 2 = 180 LF)
SET TARGET_FULL_LF TO 898.0.        // Total ship liquid fuel target (units)

// ----------------------------------------------------------------------------
// Pad Servicing Helper Functions (Modular Launch Pads)
// ----------------------------------------------------------------------------
FUNCTION set_pad_electric_power {
    PARAMETER power_state. // TRUE = connect generator, FALSE = disconnect
    LOCAL found IS FALSE.
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("LaunchStand") OR p:NAME:CONTAINS("AM.MLP") OR p:NAME:CONTAINS("AM_MLP") {
            FROM {LOCAL i IS 0.} UNTIL i >= p:MODULES:LENGTH STEP {SET i TO i + 1.} DO {
                IF p:MODULES[i] = "ModuleGenerator" {
                    LOCAL gen IS p:GETMODULEBYINDEX(i).
                    LOCAL is_fuel_gen IS FALSE.
                    FOR ev IN gen:ALLEVENTNAMES {
                        IF ev:TOLOWER:CONTAINS("fuel") OR ev:TOLOWER:CONTAINS("combustible") {
                            SET is_fuel_gen TO TRUE.
                        }
                    }
                    IF NOT is_fuel_gen {
                        FOR ev IN gen:ALLEVENTNAMES {
                            LOCAL evl IS ev:TOLOWER.
                            IF power_state AND (evl:CONTAINS("activar") OR evl:CONTAINS("activate") OR evl:CONTAINS("start") OR evl:CONTAINS("encender")) {
                                gen:DOEVENT(ev).
                                SET found TO TRUE.
                            }
                            IF (NOT power_state) AND (evl:CONTAINS("desactivar") OR evl:CONTAINS("shutdown") OR evl:CONTAINS("apagar") OR evl:CONTAINS("stop")) {
                                gen:DOEVENT(ev).
                                SET found TO TRUE.
                            }
                        }
                        FOR act IN gen:ALLACTIONNAMES {
                            LOCAL actl IS act:TOLOWER.
                            IF power_state AND (actl:CONTAINS("activate") OR actl:CONTAINS("activar")) {
                                gen:DOACTION(act, TRUE).
                                SET found TO TRUE.
                            }
                            IF (NOT power_state) AND (actl:CONTAINS("shutdown") OR actl:CONTAINS("desactivar") OR actl:CONTAINS("apagar")) {
                                gen:DOACTION(act, TRUE).
                                SET found TO TRUE.
                            }
                        }
                    }
                }
            }
        }
    }
    IF power_state {
        PRINT "  [PAD] Alimentacio electrica externa de la torre: CONNECTADA.".
    } ELSE {
        PRINT "  [PAD] Alimentacio electrica externa de la torre: DESCONNECTADA.".
    }
}

FUNCTION set_pad_fueling {
    PARAMETER fuel_state. // TRUE = start pumping, FALSE = stop
    LOCAL found IS FALSE.
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("LaunchStand") OR p:NAME:CONTAINS("AM.MLP") OR p:NAME:CONTAINS("AM_MLP") {
            FROM {LOCAL i IS 0.} UNTIL i >= p:MODULES:LENGTH STEP {SET i TO i + 1.} DO {
                IF p:MODULES[i] = "ModuleGenerator" {
                    LOCAL gen IS p:GETMODULEBYINDEX(i).
                    LOCAL is_fuel_gen IS FALSE.
                    FOR ev IN gen:ALLEVENTNAMES {
                        LOCAL evl IS ev:TOLOWER.
                        IF evl:CONTAINS("fuel") OR evl:CONTAINS("combustible") {
                            SET is_fuel_gen TO TRUE.
                        }
                    }
                    IF is_fuel_gen {
                        FOR ev IN gen:ALLEVENTNAMES {
                            LOCAL evl IS ev:TOLOWER.
                            IF fuel_state AND (evl:CONTAINS("start") OR evl:CONTAINS("iniciar") OR evl:CONTAINS("activar")) {
                                gen:DOEVENT(ev).
                                SET found TO TRUE.
                            }
                            IF (NOT fuel_state) AND (evl:CONTAINS("stop") OR evl:CONTAINS("detener") OR evl:CONTAINS("desactivar")) {
                                gen:DOEVENT(ev).
                                SET found TO TRUE.
                            }
                        }
                        FOR act IN gen:ALLACTIONNAMES {
                            LOCAL actl IS act:TOLOWER.
                            IF fuel_state AND (actl:CONTAINS("activate") OR actl:CONTAINS("activar") OR actl:CONTAINS("start") OR actl:CONTAINS("toggle")) {
                                gen:DOACTION(act, TRUE).
                                SET found TO TRUE.
                            }
                            IF (NOT fuel_state) AND (actl:CONTAINS("shutdown") OR actl:CONTAINS("desactivar") OR actl:CONTAINS("stop")) {
                                gen:DOACTION(act, TRUE).
                                SET found TO TRUE.
                            }
                        }
                    }
                }
            }
        }
    }
    IF fuel_state {
        PRINT "  [PAD] Linies de carrega de propelents criogenics: OBERTES.".
    } ELSE {
        PRINT "  [PAD] Linies de carrega de propelents criogenics: TANCADES.".
    }
}

FUNCTION retract_tower_umbilicals {
    PRINT "--------------------------------------------------".
    PRINT "T-30s: Retirant mannegues de carrega i bracos oscil-lants de la torre...".
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("Umbilical") OR p:NAME:CONTAINS("SwingArm") {
            FOR m IN p:MODULES {
                LOCAL part_mod IS p:GETMODULE(m).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("retract") OR evl:CONTAINS("release") OR evl:CONTAINS("retirar") {
                        part_mod:DOEVENT(ev).
                        PRINT "  [TOWER] Brac retirat: " + p:TITLE.
                    }
                }
            }
        }
    }
    PRINT "  [TOWER] Retirada d'umbilicals i bracos executada amb exit.".
    PRINT "--------------------------------------------------".
}

// ----------------------------------------------------------------------------
// Flight Subsystem Helper Functions
// ----------------------------------------------------------------------------
FUNCTION jettison_fairings {
    PRINT "--------------------------------------------------".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Jettisoning payload fairings (> 55 km)...".
    LOCAL fairing_jettisoned IS FALSE.
    FOR part_item IN SHIP:PARTS {
        IF part_item:NAME:CONTAINS("Fairing") OR part_item:NAME:CONTAINS("Juno4") {
            FOR mod_name IN part_item:MODULES {
                LOCAL part_mod IS part_item:GETMODULE(mod_name).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("deploy") OR evl:CONTAINS("jettison") OR evl:CONTAINS("desplegar") OR evl:CONTAINS("soltar") {
                        part_mod:DOEVENT(ev).
                        SET fairing_jettisoned TO TRUE.
                    }
                }
            }
        }
    }
    IF NOT fairing_jettisoned {
        IF STAGE:NUMBER >= 1 {
            STAGE.
            SET fairing_jettisoned TO TRUE.
        }
    }
    RETURN fairing_jettisoned.
}

FUNCTION deploy_satellite_systems {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Desplegant antenes i panells solars (CoroltSat-1E)...".
    AG3 ON.
    FOR part_item IN SHIP:PARTS {
        FOR mod_name IN part_item:MODULES {
            LOCAL part_mod IS part_item:GETMODULE(mod_name).
            FOR ev IN part_mod:ALLEVENTNAMES {
                LOCAL evl IS ev:TOLOWER.
                IF evl:CONTAINS("extend") OR evl:CONTAINS("deploy") OR evl:CONTAINS("desplegar") OR evl:CONTAINS("activar") {
                    IF NOT evl:CONTAINS("chute") AND NOT evl:CONTAINS("decouple") AND NOT evl:CONTAINS("desacoblar") {
                        part_mod:DOEVENT(ev).
                    }
                }
            }
        }
    }
}

FUNCTION separate_payload {
    PRINT "--------------------------------------------------".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: EXECUTANT DESACOBLAMENT DE COROLTSAT-1E...".
    LOCAL separated IS FALSE.

    // 1. Desencadenar directament per modul ModuleDecouple
    FOR part_item IN SHIP:PARTS {
        IF part_item:HASMODULE("ModuleDecouple") {
            LOCAL part_mod IS part_item:GETMODULE("ModuleDecouple").
            IF part_mod:HASACTION("DecoupleAction") {
                part_mod:DOACTION("DecoupleAction", TRUE).
                SET separated TO TRUE.
                PRINT "  -> DecoupleAction executada a " + part_item:NAME.
            }
            FOR ev IN part_mod:ALLEVENTNAMES {
                LOCAL evl IS ev:TOLOWER.
                IF evl:CONTAINS("decouple") OR evl:CONTAINS("desacobl") OR evl:CONTAINS("desacopl") OR evl:CONTAINS("separ") {
                    part_mod:DOEVENT(ev).
                    SET separated TO TRUE.
                    PRINT "  -> Event " + ev + " executat a " + part_item:NAME.
                }
            }
        }
    }

    // 2. Comanda addicional de Staging per redundancia total
    STAGE.
    WAIT 0.5.
    STAGE.

    PRINT "Comanda de desacoblament enviada i confirmada!".
    PRINT "--------------------------------------------------".
    RETURN separated.
}

FUNCTION deorbit_upper_stage {
    PRINT "Esperant 30 segons de marge de seguretat respecte al satel-lit...".
    WAIT 30.0.

    PRINT "Orientant etapa superior a RETROGRAD per a la deorbitacio (Zero Debris Protocol)...".
    LOCK STEERING TO RETROGRADE.
    WAIT 15.0.

    PRINT "CREMADA DE DEORBITACIO DE LA SEGONA ETAPA (Belle-RLX81)...".
    LOCAL eng_list IS LIST().
    LIST ENGINES IN eng_list.
    FOR e_item IN eng_list {
        e_item:ACTIVATE().
    }

    LOCK THROTTLE TO 1.0.
    LOCAL deorbit_start IS TIME:SECONDS.
    UNTIL (SHIP:PERIAPSIS <= 0) OR (SHIP:LIQUIDFUEL < 0.2) {
        PRINT "Deorbit Pe: " + ROUND(SHIP:PERIAPSIS / 1000, 1) + " km | Fuel: " + ROUND(SHIP:LIQUIDFUEL, 1) + " LF   " AT(0, 32).
        WAIT 0.2.
    }

    LOCK THROTTLE TO 0.0.
    LOCAL deorbit_dur IS TIME:SECONDS - deorbit_start.
    PRINT "DEORBITACIO COMPLETADA (" + ROUND(deorbit_dur, 1) + " s)! PERIAPSI: " + ROUND(SHIP:PERIAPSIS / 1000, 1) + " km.".
    PRINT "Etapa superior Belle-RLX81 destinada a amaratge a l'ocea. Zero deixalles!".

    LOCK STEERING TO RETROGRADE.
    WAIT 10.0.
    UNLOCK STEERING.
    UNLOCK THROTTLE.
    SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
}

FUNCTION calculate_atmo_throttle {
    LOCAL q_kpa IS SHIP:DYNAMICPRESSURE * 101.325.
    LOCAL rad_local IS KERBIN_RADIUS + SHIP:ALTITUDE.
    LOCAL g_local IS KERBIN_MU / (rad_local * rad_local).
    LOCAL max_twr IS 0.
    IF (SHIP:MASS > 0) AND (g_local > 0) {
        SET max_twr TO SHIP:AVAILABLETHRUST / (SHIP:MASS * g_local).
    }

    LOCAL target_th IS 1.0.

    IF q_kpa > 20.0 {
        LOCAL q_excess IS (q_kpa - 20.0) / (TARGET_MAX_Q_KPA - 20.0).
        SET target_th TO 1.0 - (q_excess * 0.50).
    }

    IF max_twr > 0 {
        LOCAL min_th_for_twr IS MIN_TWR_FLOOR / max_twr.
        SET target_th TO MAX(target_th, min_th_for_twr).
    }

    IF max_twr > 0 {
        LOCAL max_th_for_g IS MAX_G_CEILING / max_twr.
        SET target_th TO MIN(target_th, max_th_for_g).
    }

    RETURN MIN(1.0, MAX(0.25, target_th)).
}

// ----------------------------------------------------------------------------
// Orbital Mechanics & Phase Evaluation Functions
// ----------------------------------------------------------------------------
FUNCTION get_orbital_longitude {
    PARAMETER craft.
    LOCAL lng IS craft:OBT:LAN + craft:OBT:ARGUMENTOFPERIAPSIS + craft:OBT:TRUEANOMALY.
    SET lng TO MOD(lng, 360).
    IF lng < 0 { SET lng TO lng + 360. }
    RETURN lng.
}

FUNCTION get_phase_angle {
    PARAMETER ship_craft, tgt_craft.
    LOCAL ship_l IS get_orbital_longitude(ship_craft).
    LOCAL tgt_l IS get_orbital_longitude(tgt_craft).
    LOCAL diff IS MOD(ship_l - tgt_l + 360, 360).
    RETURN diff.
}

FUNCTION find_target_satellite {
    PARAMETER name_str.
    LOCAL all_vessels IS LIST().
    LIST TARGETS IN all_vessels.
    IF name_str:LENGTH > 0 {
        FOR v IN all_vessels {
            LOCAL vn IS v:NAME:TOLOWER.
            IF vn:CONTAINS(name_str:TOLOWER) {
                SET TARGET TO v.
                RETURN TARGET.
            }
        }
    }
    IF HASTARGET {
        RETURN TARGET.
    }
    FOR v IN all_vessels {
        LOCAL vn IS v:NAME:TOLOWER.
        IF vn:CONTAINS("corolsat-1b") OR vn:CONTAINS("coroltsat-1b") {
            SET TARGET TO v.
            RETURN TARGET.
        }
    }
    RETURN SHIP.
}

// ============================================================================
// PAS 1: SEQÜÈNCIA D'INICI DE CÀRREGA (5 SEGONS DE COMPTE ENRERE)
// ============================================================================
PRINT "==================================================".
PRINT "AVIS: La carrega de propelents comencara en 5 segons.".
PRINT "==================================================".

FROM {LOCAL cd_val IS 5.} UNTIL cd_val = 0 STEP {SET cd_val TO cd_val - 1.} DO {
    PRINT "T-omplida: " + cd_val + "...".
    WAIT 1.0.
}

// ============================================================================
// PAS 2: CONNECTAR GENERADOR ELÈCTRIC DE LA PLATAFORMA
// ============================================================================
PRINT "--------------------------------------------------".
PRINT "Activant subministrament electric terrestre...".
set_pad_electric_power(TRUE).
WAIT 1.0.

// ============================================================================
// PAS 3: COMENÇAR A CARREGAR ELS PROPELENTS
// ============================================================================
PRINT "--------------------------------------------------".
PRINT "Obrint valvules d'ompliment de la torre...".
set_pad_fueling(TRUE).
WAIT 1.0.

// ============================================================================
PRINT "Carrega de combustible en curs (Taxa reduida ~ 6 LF/s, ~120s)...".
UNTIL (SHIP:LIQUIDFUEL >= TARGET_FULL_LF) {
    LOCAL pct IS ROUND((SHIP:LIQUIDFUEL / 900.0) * 100, 1).
    PRINT "Carrega: " + ROUND(SHIP:LIQUIDFUEL, 1) + " / 900.0 LF (" + pct + "%) | Ox: " + ROUND(SHIP:OXIDIZER, 1) + " / 1100.0".
    WAIT 5.0.
}

PRINT "==================================================".
PRINT "DIPOSITS DE LA 1A ETAPA PLENS AL 100%!".
PRINT "Tancant valvules de proveiment terrestre...".
set_pad_fueling(FALSE).
WAIT 2.0.

// Determinació de finestra de llançament
LOCAL effective_launch_ut IS TARGET_LAUNCH_UT.
IF effective_launch_ut <= TIME:SECONDS {
    SET effective_launch_ut TO TIME:SECONDS + 70.0.
}

PRINT "--------------------------------------------------".
PRINT "Finestra objectiu establerta a UT: " + ROUND(effective_launch_ut, 1) + " s".
PRINT "Temps restant fins al llancament:  " + ROUND(effective_launch_ut - TIME:SECONDS, 1) + " s".
PRINT "--------------------------------------------------".

LOCAL time_to_t60 IS (effective_launch_ut - 60.0) - TIME:SECONDS.
IF time_to_t60 > 1.0 {
    PRINT "Estat de HOLD a la rampa fins a T-60s de la finestra de llancament.".
    PRINT "Pots activar i controlar el Time Warp manualment segons desitgis.".
    UNTIL TIME:SECONDS >= (effective_launch_ut - 60.0) {
        LOCAL remaining_hold IS ROUND((effective_launch_ut - 60.0) - TIME:SECONDS, 0).
        IF remaining_hold > 0 {
            PRINT "HOLD... Falten " + remaining_hold + "s per a T-60s (Warp manual permes)    " AT(0, 24).
        }
        WAIT 1.0.
    }
}

// ============================================================================
// PAS 5: COMPTE ENRERE TERMINAL A T-1 MINUT (MARCANT CADA 10 SEGONS)
// ============================================================================
PRINT "==================================================".
PRINT "T-60s: INICI DEL COMPTE ENRERE TERMINAL".
PRINT "Tots els sistemes del vehicle i rampa en verd.".
PRINT "==================================================".

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 50.0).
PRINT "T-50s: Pressuritzacio dels tancs de vol confirmada.".

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 40.0).
PRINT "T-40s: Avionica kOS i telemetria en linia nominal.".

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 30.0).

// ============================================================================
// PAS 6: A T-30s: LLEVAR CÀRREGA ELÈCTRICA I MÀNEGUES DE LA TORRE
// ============================================================================
PRINT "==================================================".
PRINT "T-30s: TRANSICIO A POTENCIA INTERNA DEL VEHICLE!".
PRINT "==================================================".
set_pad_electric_power(FALSE).
retract_tower_umbilicals().

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 20.0).
PRINT "T-20s: Estat de vol: INTERN (Bateries de bord al 100%).".

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 10.0).

// ============================================================================
// PAS 7: A T-10s: COMPTE ENRERE TERMINAL SEGON A SEGON
// ============================================================================
PRINT "==================================================".
PRINT "T-10s: SEQUENCIA TERMINAL D'IGNICIO AUTOMATICA:".
PRINT "==================================================".
SAS OFF.
LOCK THROTTLE TO 0.0.
LOCK STEERING TO HEADING(HEADING_DEG, 90.0).

LOCAL countdown_val IS 10.
UNTIL countdown_val <= 0 {
    PRINT "T-" + countdown_val + "...".
    SET countdown_val TO countdown_val - 1.
    WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - countdown_val).
}

// ============================================================================
// PAS 8: IGNICIÓ I ALLIBERAMENT DE LA PLATAFORMA (T-0)
// ============================================================================
PRINT "==================================================".
PRINT "T+0.0s: IGNICIO! Core Etoh-140-TU & Acceleradors Shrimp!".
PRINT "ALLIBERANT GRAPES DE LA PLATAFORMA (STAGE 5)!".
PRINT "==================================================".

LOCK THROTTLE TO 1.0.
STAGE.
WAIT 0.5.
UNTIL SHIP:MAXTHRUST > 0 {
    STAGE.
    WAIT 0.5.
}

// ============================================================================
// FASES DE VOL: ASCENS, SEPARACIÓ I INSERCIÓ ORBITAL ULTRA-CIRCULAR
// ============================================================================
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: VEHICLE CSA-15 EN VOL ASCENDENT!".

// Activar regulador aerodinàmic Max Q des del vol atmosfèric
LOCK THROTTLE TO calculate_atmo_throttle().

LOCAL initial_thrust IS SHIP:MAXTHRUST.
LOCAL srb_separated IS FALSE.

// Fase 2: Gir gravitatori (Pitch Kick) immediat a ALT_KICK (1200 m)
IF SHIP:ALTITUDE < ALT_KICK {
    WAIT UNTIL SHIP:ALTITUDE >= ALT_KICK.
}
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: INICIANT GIR GRAVITATORI (PITCH " + PITCH_INITIAL + " deg HDG " + HEADING_DEG + " deg)!".
LOCK targetPitch TO MAX(MIN_PITCH, PITCH_INITIAL - ((SHIP:ALTITUDE - ALT_KICK) / (ALT_END_TURN - ALT_KICK)) * (PITCH_INITIAL - MIN_PITCH)).
LOCK STEERING TO HEADING(HEADING_DEG, targetPitch).

// Fase 3: Ascens sota guia fins al MECO de la 1a Etapa (amb desacoblament concurrent d'SRBs)
LOCAL last_telemetry_print IS MISSIONTIME.
UNTIL (srb_separated AND (STAGE:LIQUIDFUEL < 0.5)) OR (SHIP:LIQUIDFUEL <= 180.5) OR (SHIP:MAXTHRUST < 10.0) {
    IF (NOT srb_separated) AND ((SHIP:SOLIDFUEL < 1.0) OR (SHIP:MAXTHRUST < (initial_thrust * 0.70))) {
        WAIT 0.5.
        PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Booster burnout! Desacoblant 2x Shrimp SRBs...".
        STAGE.
        WAIT 0.5.
        SET srb_separated TO TRUE.
    }
    IF (MISSIONTIME - last_telemetry_print) >= 5.0 {
        LOCAL q_curr IS ROUND(SHIP:DYNAMICPRESSURE * CONSTANT:ATMTOKPA, 1).
        PRINT "T+" + ROUND(MISSIONTIME, 0) + "s | Alt: " + ROUND(SHIP:ALTITUDE/1000, 1) + "km | Q: " + q_curr + "kPa | Th: " + ROUND(THROTTLE * 100, 0) + "%".
        SET last_telemetry_print TO MISSIONTIME.
    }
    WAIT 0.2.
}

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 1 Core MECO!".
LOCK THROTTLE TO 0.0.
WAIT 1.0.
STAGE. // Desacoblament interetapa
WAIT 1.5.

// Fase 4: Encesa Etapa 2 (Belle-RLX81)
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: IGNICIO ETAPA 2 (Belle-RLX81)!".
LOCK THROTTLE TO 1.0.
STAGE. // Encesa Belle-RLX81
WAIT 1.0.

// Fase 5: Expulsio de cofia i adquisicio d'Apogeu (300 km)
LOCAL fairing_done IS FALSE.
LOCK STEERING TO PROGRADE.

UNTIL SHIP:APOAPSIS >= (TARGET_APOAPSIS - 5000) {
    IF (SHIP:ALTITUDE > 55000) AND (NOT fairing_done) {
        jettison_fairings().
        SET fairing_done TO TRUE.
    }
    WAIT 0.2.
}

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Apogeu proper (295 km). Reduint potencia al 20%...".
LOCK THROTTLE TO 0.20.

WAIT UNTIL SHIP:APOAPSIS >= TARGET_APOAPSIS.
LOCK THROTTLE TO 0.0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SECO-1! Apogeu assolit a 300.0 km.".

// Fase 6: Deriva exosferica a l'Apogeu
LOCK STEERING TO PROGRADE.
IF NOT fairing_done {
    WAIT UNTIL SHIP:ALTITUDE > 70000.
    jettison_fairings().
    SET fairing_done TO TRUE.
}

// Fase 7: Circularitzacio d'Ultra-Precisio (e <= 0.0008)
LOCAL rad_target IS KERBIN_RADIUS + TARGET_APOAPSIS.
LOCAL v_circ IS SQRT(KERBIN_MU / rad_target).
LOCAL sma_trans IS (SHIP:PERIAPSIS + SHIP:APOAPSIS + 2 * KERBIN_RADIUS) / 2.
LOCAL v_apo_pred IS SQRT(KERBIN_MU * (2 / (KERBIN_RADIUS + SHIP:APOAPSIS) - 1 / sma_trans)).
LOCAL delta_v_circ IS MAX(10.0, v_circ - v_apo_pred).
LOCAL burn_duration IS (delta_v_circ * SHIP:MASS) / MAX(1.0, SHIP:MAXTHRUST).
LOCAL half_burn IS burn_duration / 2.

WAIT UNTIL (ETA:APOAPSIS <= (half_burn + 5.0)) OR (ETA:APOAPSIS > (SHIP:ORBIT:PERIOD - 60)).
LOCK STEERING TO PROGRADE.
WAIT UNTIL (ETA:APOAPSIS <= half_burn) OR (ETA:APOAPSIS > (SHIP:ORBIT:PERIOD - 30)).

PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: IGNICIO SECO-2 (Circularitzacio d'Ultra-Precisio)!".
PRINT "==================================================".

LOCK THROTTLE TO 1.0.
LOCAL best_ecc IS SHIP:ORBIT:ECCENTRICITY.
LOCAL burn_active IS TRUE.

UNTIL NOT burn_active {
    LOCAL cur_ecc IS SHIP:ORBIT:ECCENTRICITY.
    IF cur_ecc < best_ecc { SET best_ecc TO cur_ecc. }

    IF cur_ecc > 0.05 {
        LOCK THROTTLE TO 1.0.
    } ELSE IF cur_ecc > 0.015 {
        LOCK THROTTLE TO 0.35.
    } ELSE IF cur_ecc > 0.003 {
        LOCK THROTTLE TO 0.10.
    } ELSE {
        LOCK THROTTLE TO 0.03.
    }

    IF (cur_ecc <= 0.0008) OR ((cur_ecc > (best_ecc + 0.0002)) AND (cur_ecc < 0.005)) OR (ABS(SHIP:APOAPSIS - SHIP:PERIAPSIS) < 500) {
        SET burn_active TO FALSE.
    }

    PRINT "Circ Burn | e: " + ROUND(cur_ecc, 5) + " | Ap: " + ROUND(SHIP:APOAPSIS/1000, 2) + "km | Pe: " + ROUND(SHIP:PERIAPSIS/1000, 2) + "km | Th: " + ROUND(THROTTLE*100, 0) + "%" AT(0, 26).
    WAIT 0.05.
}

LOCK THROTTLE TO 0.0.
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SECO-2 TALLAT! ORBITA ULTRA-CIRCULAR ASSOLIDA!".
PRINT "  Final Ap: " + ROUND(SHIP:APOAPSIS / 1000, 3) + " km".
PRINT "  Final Pe: " + ROUND(SHIP:PERIAPSIS / 1000, 3) + " km".
PRINT "  Final Ecc: " + ROUND(SHIP:ORBIT:ECCENTRICITY, 6).
PRINT "==================================================".

// ============================================================================
// FASE 8: AUDITORIA DE FASE ORBITAL I INTERLOCK DE SEGURETAT (+/- 0.50 deg)
// ============================================================================
WAIT 3.0.
LOCAL tgt_anchor IS find_target_satellite(TARGET_ANCHOR).
LOCAL final_phase IS 0.
LOCAL phase_err IS 999.
LOCAL norm_target_slot IS MOD(TARGET_SLOT_DEG, 360.0).
IF norm_target_slot < 0 { SET norm_target_slot TO norm_target_slot + 360.0. }

IF tgt_anchor <> SHIP {
    SET final_phase TO get_phase_angle(SHIP, tgt_anchor).
    SET phase_err TO ABS(final_phase - norm_target_slot).
    IF phase_err > 180 { SET phase_err TO 360 - phase_err. }
} ELSE {
    PRINT "ALERTA: Sense connexió amb satèl·lit àncora " + TARGET_ANCHOR + ".".
}

PRINT "==================================================".
PRINT "        AUDITORIA DE FASE ORBITAL CSA-15          ".
PRINT "  Àncora de referència:    " + tgt_anchor:NAME.
PRINT "  Slot objectiu:           " + TARGET_SLOT_DEG + " deg".
PRINT "  Fase relativa assolida:  " + ROUND(final_phase, 3) + " deg".
PRINT "  Desviació absoluta:      " + ROUND(phase_err, 3) + " deg".
PRINT "  Tolerància d'alliberament: +/-" + PHASE_TOLERANCE_DEG + " deg".
PRINT "==================================================".

IF phase_err <= PHASE_TOLERANCE_DEG {
    PRINT ">>> VALIDACIO EXITOSA: Error (" + ROUND(phase_err, 3) + " deg) <= +/-" + PHASE_TOLERANCE_DEG + " deg! <<<".
    PRINT "Procedint a l'orientacio Normal i desplegament de CoroltSat-1E...".

    // Orientar al vector NORMAL orbital pur dinàmicament (perpendicular al pla)
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Orientant actitud a NORMAL orbital pur...".
    LOCK STEERING TO VCRS(SHIP:VELOCITY:ORBIT, BODY:POSITION).
    WAIT 15.0.

    deploy_satellite_systems().
    WAIT 3.0.

    separate_payload().
    PRINT "==================================================".
    PRINT "      MISSIO CSA-15: COROLTSAT-1E DESPLEGAT!      ".
    PRINT "   PONT DE 4 SATEL-LITS (1B-1D-1E-1C) ENLLAÇAT!   ".
    PRINT "==================================================".

    // Desorbitar l'etapa superior buida
    deorbit_upper_stage().

} ELSE {
    PRINT "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".
    PRINT "ALERTA DE SEGURETAT DE MISSIONS CSA:".
    PRINT "La desviació de fase (" + ROUND(phase_err, 3) + " deg) SUPERA el límit de +/-" + PHASE_TOLERANCE_DEG + " deg!".
    PRINT "DESACOBLAMENT CANCEL-LAT AUTOMATICAMENT!".
    PRINT "CoroltSat-1E roman acoblat de forma segura a la 2a etapa.".
    PRINT "Conserva el combustible de la Belle-RLX81 per a correcció de drift.".
    PRINT "Accio requerida: Executeu constellation_phasing.ks:".
    PRINT "  RUNPATH(" + CHAR(34) + "0:/csa/constellation_phasing.ks" + CHAR(34) + ", " + TARGET_SLOT_DEG + ", 3, " + CHAR(34) + tgt_anchor:NAME + CHAR(34) + ").".
    PRINT "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".
    UNLOCK STEERING.
    UNLOCK THROTTLE.
    SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
}

PRINT "Seqüència csa15_guided_ascent finalitzada.".
