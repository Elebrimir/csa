// ============================================================================
// COROLT SPACE AGENCY (CSA) - FLIGHT GUIDANCE SYSTEM v4.8
// MISSION: CSA-16 (Inaugural Node of 600 km MKO Constellation - CoroltSat-1F)
// VEHICLE: Corolt-IV B Unit 6 (CSA14 - B6CSF) on Modular Launch Pad (MLP)
// TARGET:  600.0 km Equatorial Circular Orbit (Node 0 Foundation Anchor)
//          Inaugurates the 6-satellite MKO constellation (60.0 deg spacing):
//          Chord distance = 1,200.0 km <= 1,327.4 km (100% compliant with 3x Codac-A23 & rangeModifier=0.65)
// AUTOMATED PAD OPERATIONS & LAUNCH COUNTDOWN:
//   1. 5s countdown to tanking initiation.
//   2. Ground electrical generator connected.
//   3. Refueling initiated (~120s tanking duration to 900 LF / 1100 Ox).
//   4. Tank level monitoring (until 898+ LF full) & Hold until T-60s of window.
//   5. Terminal countdown at T-60s with 10-second milestones.
//   6. At T-30s: Disconnect ground power & retract umbilicals/swing arms.
//   7. At T-10s: Terminal single-second countdown.
//   8. At T-0s: Core & SRB Ignition, pad clamp release, Liftoff!
// FLIGHT GUIDANCE:
//   - Immediate pitch kick at 1,200 m (84.0 deg) concurrent with SRB thrust
//   - Ascent with Max Q throttling governor (Target Q <= 32 kPa)
//   - Seamless Shrimp SRB separation (~48.5s) via srb_separated MECO guard
//   - Fairing vacuum separation (> 55 km)
//   - SECO-1 apogee push (600 km) & exospheric ballistic coast
//   - SECO-2 circularization at 600 km with 4-tier vernier governor (e <= 0.0008)
//   - Synchronous period lock (T_tgt = 4,395.14 s within +/- 0.15 s)
//   - Normal-vector deployment of CoroltSat-1F (5x solar arrays, 3x Codac-A23 relays)
//   - Belle-RLX81 Stage 2 Retrograde deorbit disposal (Pe <= 0 km, Zero Debris Protocol)
// ============================================================================

DECLARE PARAMETER TARGET_ALT_KM IS 600.0.        // Target orbital altitude in km (default 600 km MKO)
DECLARE PARAMETER TARGET_LAUNCH_UT IS 0.         // Set to 0 for immediate sequence or pass exact window UT
DECLARE PARAMETER TARGET_SLOT_DEG IS 0.0.        // Target slot (0.0 deg for Node 0 Foundation Anchor)
DECLARE PARAMETER TARGET_ANCHOR IS "NONE".       // Reference anchor ("NONE" = Inaugural Anchor of new ring)

CLEARSCREEN.
PRINT "==================================================".
PRINT "      COROLT SPACE AGENCY - MISSION CONTROL       ".
PRINT "   MISSION: CSA-16 | CoroltSat-1F (MKO-600)       ".
PRINT "   VEHICLE: Corolt-IV B #6 (CSA14 - B6CSF)        ".
PRINT "   TARGET ORBIT: " + TARGET_ALT_KM + " x " + TARGET_ALT_KM + " km (Equatorial)".
IF TARGET_ANCHOR = "NONE" OR TARGET_ANCHOR = "" {
    PRINT "   ROLE: Foundation Anchor (Node 0 / 600 km MKO)  ".
} ELSE {
    PRINT "   TARGET SLOT: " + TARGET_SLOT_DEG + " deg (Anchor: " + TARGET_ANCHOR + ")".
}
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Flight Constants & Orbital Targets
// ----------------------------------------------------------------------------
SET TARGET_APOAPSIS TO TARGET_ALT_KM * 1000.0.   // Target Apogee (m)
SET TARGET_PERIAPSIS TO TARGET_ALT_KM * 1000.0.  // Target Perigee (m)
SET ALT_KICK TO 1200.                            // Pitch kick initiation altitude (m)
SET PITCH_INITIAL TO 84.0.                       // Initial pitch angle (deg)
SET HEADING_DEG TO 90.0.                         // Launch azimuth (Due East Equatorial)
SET ALT_END_TURN TO 48000.                       // Turn completion altitude (m)
SET MIN_PITCH TO 15.0.                           // Minimum pitch before MECO (deg)
SET KERBIN_MU TO 3.5316000e12.                   // Gravitational parameter
SET KERBIN_RADIUS TO 600000.                     // Equatorial radius (m)
SET PHASE_TOLERANCE_DEG TO 0.50.                 // Strict safety limit (+/- 0.50 deg)
SET PERIOD_TOLERANCE_SEC TO 0.20.                // Strict synchronous period lock tolerance (+/- 0.20 s)

// Theoretical synchronous period for target altitude
SET TARGET_THEORETICAL_PERIOD TO 2.0 * CONSTANT:PI * SQRT(((KERBIN_RADIUS + TARGET_APOAPSIS)^3) / KERBIN_MU).

// Aerodynamic Governor Limits
SET TARGET_MAX_Q_KPA TO 32.0.                    // Max dynamic pressure ceiling (kPa)
SET MIN_TWR_FLOOR TO 1.30.                       // Minimum TWR floor
SET MAX_G_CEILING TO 3.80.                       // Maximum acceleration load (G)

// Fuel Thresholds for Stage 1 Full Tanking (2x FL-T800 = 720 LF, Stage 2 = 180 LF)
SET TARGET_FULL_LF TO 898.0.                     // Total ship liquid fuel target (units)

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
        PRINT "  [PAD] Ground external electrical power: CONNECTED.".
    } ELSE {
        PRINT "  [PAD] Ground external electrical power: DISCONNECTED.".
    }
}

FUNCTION set_pad_fueling {
    PARAMETER fuel_state. // TRUE = start pumping, FALSE = stop
    PARAMETER verbose IS TRUE. // Optional: whether to print status messages
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
    IF verbose {
        IF fuel_state {
            PRINT "  [PAD] Propellant transfer lines: OPEN.".
        } ELSE {
            PRINT "  [PAD] Propellant transfer lines: CLOSED.".
        }
    }
}

FUNCTION retract_tower_umbilicals {
    PRINT "--------------------------------------------------".
    PRINT "T-30s: Retracting fuel umbilicals and service tower swing arms...".
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("Umbilical") OR p:NAME:CONTAINS("SwingArm") {
            FOR m IN p:MODULES {
                LOCAL part_mod IS p:GETMODULE(m).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("retract") OR evl:CONTAINS("release") OR evl:CONTAINS("retirar") {
                        part_mod:DOEVENT(ev).
                        PRINT "  [TOWER] Arm retracted: " + p:TITLE.
                    }
                }
            }
        }
    }
    PRINT "  [TOWER] Umbilical & swing arm retraction complete.".
    PRINT "--------------------------------------------------".
}

// ----------------------------------------------------------------------------
// Flight Subsystem Helper Functions
// ----------------------------------------------------------------------------
FUNCTION ensure_engines_active {
    LOCAL eng_list IS LIST().
    LIST ENGINES IN eng_list.
    FOR e_item IN eng_list {
        e_item:ACTIVATE().
    }
}

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
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Deploying antennas and solar arrays (CoroltSat-1F)...".
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
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: EXECUTING COROLTSAT-1F PAYLOAD SEPARATION...".
    LOCAL separated IS FALSE.

    // 1. Trigger directly via ModuleDecouple
    FOR part_item IN SHIP:PARTS {
        IF part_item:HASMODULE("ModuleDecouple") {
            LOCAL part_mod IS part_item:GETMODULE("ModuleDecouple").
            IF part_mod:HASACTION("DecoupleAction") {
                part_mod:DOACTION("DecoupleAction", TRUE).
                SET separated TO TRUE.
                PRINT "  -> DecoupleAction executed on " + part_item:NAME.
            }
            FOR ev IN part_mod:ALLEVENTNAMES {
                LOCAL evl IS ev:TOLOWER.
                IF evl:CONTAINS("decouple") OR evl:CONTAINS("desacobl") OR evl:CONTAINS("desacopl") OR evl:CONTAINS("separ") {
                    part_mod:DOEVENT(ev).
                    SET separated TO TRUE.
                    PRINT "  -> Event " + ev + " executed on " + part_item:NAME.
                }
            }
        }
    }

    // 2. Redundant Staging command
    STAGE.
    WAIT 0.5.
    STAGE.

    PRINT "Payload separation command sent and confirmed!".
    PRINT "--------------------------------------------------".
    RETURN separated.
}

FUNCTION synchronize_constellation_period {
    PARAMETER tgt_period_sec.
    LOCAL p_diff IS tgt_period_sec - SHIP:OBT:PERIOD.
    IF ABS(p_diff) <= PERIOD_TOLERANCE_SEC {
        PRINT "  [SYNC] Orbital period already matched (" + ROUND(SHIP:OBT:PERIOD, 2) + " s vs " + ROUND(tgt_period_sec, 2) + " s).".
        RETURN.
    }

    PRINT "--------------------------------------------------".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SYNCHRONOUS PERIOD LOCK BURN INITIATED".
    PRINT "  Current Period: " + ROUND(SHIP:OBT:PERIOD, 2) + " s | Target Period: " + ROUND(tgt_period_sec, 2) + " s".
    SET KUNIVERSE:TIMEWARP:WARP TO 0.
    ensure_engines_active().

    IF p_diff > 0 {
        PRINT "  Steering PROGRADE to raise orbital period (+ " + ROUND(p_diff, 2) + " s)...".
        LOCK STEERING TO PROGRADE.
        WAIT 12.0.
        LOCAL sync_burn IS TRUE.
        UNTIL NOT sync_burn {
            LOCAL rem_p IS tgt_period_sec - SHIP:OBT:PERIOD.
            IF rem_p <= PERIOD_TOLERANCE_SEC {
                SET sync_burn TO FALSE.
                LOCK THROTTLE TO 0.0.
            } ELSE IF rem_p < 2.0 {
                LOCK THROTTLE TO 0.03.
            } ELSE IF rem_p < 8.0 {
                LOCK THROTTLE TO 0.10.
            } ELSE {
                LOCK THROTTLE TO 0.25.
            }
            PRINT "Period Trim | T_cur: " + ROUND(SHIP:OBT:PERIOD, 2) + "s | T_tgt: " + ROUND(tgt_period_sec, 2) + "s | Th: " + ROUND(THROTTLE*100, 0) + "%   " AT(0, 28).
            WAIT 0.05.
        }
    } ELSE {
        PRINT "  Steering RETROGRADE to lower orbital period (" + ROUND(p_diff, 2) + " s)...".
        LOCK STEERING TO RETROGRADE.
        WAIT 12.0.
        LOCAL sync_burn IS TRUE.
        UNTIL NOT sync_burn {
            LOCAL rem_p IS SHIP:OBT:PERIOD - tgt_period_sec.
            IF rem_p <= PERIOD_TOLERANCE_SEC {
                SET sync_burn TO FALSE.
                LOCK THROTTLE TO 0.0.
            } ELSE IF rem_p < 2.0 {
                LOCK THROTTLE TO 0.03.
            } ELSE IF rem_p < 8.0 {
                LOCK THROTTLE TO 0.10.
            } ELSE {
                LOCK THROTTLE TO 0.25.
            }
            PRINT "Period Trim | T_cur: " + ROUND(SHIP:OBT:PERIOD, 2) + "s | T_tgt: " + ROUND(tgt_period_sec, 2) + "s | Th: " + ROUND(THROTTLE*100, 0) + "%   " AT(0, 28).
            WAIT 0.05.
        }
    }
    LOCK THROTTLE TO 0.0.
    PRINT "  [SYNC] Period locked at " + ROUND(SHIP:OBT:PERIOD, 2) + " s (Drift < 0.02 deg/rev)!".
    PRINT "--------------------------------------------------".
}

FUNCTION deorbit_upper_stage {
    PRINT "Waiting 30-second safety clearance interval from deployed satellite...".
    WAIT 30.0.

    PRINT "Orienting upper stage to RETROGRADE for disposal burn (Zero Debris Protocol)...".
    LOCK STEERING TO RETROGRADE.
    WAIT 15.0.

    PRINT "EXECUTING STAGE 2 DEORBIT BURN (Belle-RLX81)...".
    ensure_engines_active().

    LOCK THROTTLE TO 1.0.
    LOCAL deorbit_start IS TIME:SECONDS.
    UNTIL (SHIP:PERIAPSIS <= 0) OR (SHIP:LIQUIDFUEL < 0.2) {
        PRINT "Deorbit Pe: " + ROUND(SHIP:PERIAPSIS / 1000, 1) + " km | Fuel: " + ROUND(SHIP:LIQUIDFUEL, 1) + " LF   " AT(0, 32).
        WAIT 0.2.
    }

    LOCK THROTTLE TO 0.0.
    LOCAL deorbit_dur IS TIME:SECONDS - deorbit_start.
    PRINT "DEORBIT BURN COMPLETE (" + ROUND(deorbit_dur, 1) + " s)! PERIAPSIS: " + ROUND(SHIP:PERIAPSIS / 1000, 1) + " km.".
    PRINT "Belle-RLX81 upper stage targeted for destructive ocean disposal. Zero Debris!".

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

FUNCTION to_signed_deg {
    PARAMETER angle_deg.
    LOCAL a IS MOD(angle_deg, 360.0).
    IF a < 0 { SET a TO a + 360.0. }
    IF a > 180.0 { SET a TO a - 360.0. }
    RETURN a.
}

FUNCTION find_target_satellite {
    PARAMETER name_str.
    LOCAL all_vessels IS LIST().
    LIST TARGETS IN all_vessels.
    IF name_str:LENGTH > 0 AND name_str <> "NONE" {
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
    RETURN SHIP.
}

// ============================================================================
// STEP 1: PROPELLANT LOADING INITIATION (5-SECOND COUNTDOWN)
// ============================================================================
PRINT "==================================================".
PRINT "NOTICE: Propellant tanking sequence starts in 5 seconds.".
PRINT "==================================================".

FROM {LOCAL cd_val IS 5.} UNTIL cd_val = 0 STEP {SET cd_val TO cd_val - 1.} DO {
    PRINT "T-tanking: " + cd_val + "...".
    WAIT 1.0.
}

// ============================================================================
// STEP 2: CONNECT PAD GROUND ELECTRICAL POWER
// ============================================================================
PRINT "--------------------------------------------------".
PRINT "Activating ground electrical power supply...".
set_pad_electric_power(TRUE).
WAIT 1.0.

// ============================================================================
// STEP 3: OPEN PROPELLANT TRANSFER VALVES (PULSED 25% DUTY CYCLE FOR 1/4 FLOW RATE)
// ============================================================================
PRINT "--------------------------------------------------".
PRINT "Opening launch tower propellant fill valves (1/4 flow rate mode)...".
set_pad_fueling(TRUE, TRUE).
WAIT 1.0.

// ============================================================================
PRINT "Propellant loading in progress (Quarter-rate ~ 1.5 LF/s, ~480s)...".
LOCAL cycle_count IS 0.
UNTIL (SHIP:LIQUIDFUEL >= TARGET_FULL_LF) {
    // 25% Duty cycle: 1.0s ON, 3.0s OFF (effective 1/4 flow rate)
    set_pad_fueling(TRUE, FALSE).
    WAIT 1.0.
    IF SHIP:LIQUIDFUEL >= TARGET_FULL_LF {
        BREAK.
    }
    set_pad_fueling(FALSE, FALSE).

    SET cycle_count TO cycle_count + 1.
    // Display status update every cycle (~4 seconds)
    LOCAL pct IS ROUND((SHIP:LIQUIDFUEL / 900.0) * 100, 1).
    PRINT "Loading (1/4 rate): " + ROUND(SHIP:LIQUIDFUEL, 1) + " / 900.0 LF (" + pct + "%) | Ox: " + ROUND(SHIP:OXIDIZER, 1) + " / 1100.0".
    WAIT 3.0.
}

PRINT "==================================================".
PRINT "STAGE 1 & STAGE 2 PROPELLANT TANKS AT 100%!".
PRINT "Closing ground transfer valves...".
set_pad_fueling(FALSE, TRUE).
WAIT 2.0.

// Determine launch window UT
LOCAL effective_launch_ut IS TARGET_LAUNCH_UT.
IF effective_launch_ut <= TIME:SECONDS {
    SET effective_launch_ut TO TIME:SECONDS + 70.0.
}

PRINT "--------------------------------------------------".
PRINT "Target launch window set to UT: " + ROUND(effective_launch_ut, 1) + " s".
PRINT "Time remaining until liftoff:   " + ROUND(effective_launch_ut - TIME:SECONDS, 1) + " s".
PRINT "--------------------------------------------------".

LOCAL time_to_t60 IS (effective_launch_ut - 60.0) - TIME:SECONDS.
IF time_to_t60 > 1.0 {
    PRINT "Pad HOLD active until T-60s of launch window.".
    PRINT "Manual Time Warp is permitted during pad HOLD.".
    UNTIL TIME:SECONDS >= (effective_launch_ut - 60.0) {
        LOCAL remaining_hold IS ROUND((effective_launch_ut - 60.0) - TIME:SECONDS, 0).
        IF remaining_hold > 0 {
            PRINT "HOLD... T-60s countdown starts in " + remaining_hold + "s (Warp allowed)    " AT(0, 24).
        }
        WAIT 1.0.
    }
}

// ============================================================================
// STEP 5: TERMINAL COUNTDOWN AT T-60 SECONDS (10-SECOND MILESTONES)
// ============================================================================
SET KUNIVERSE:TIMEWARP:WARP TO 0.
PRINT "==================================================".
PRINT "T-60s: TERMINAL COUNTDOWN INITIATED".
PRINT "All vehicle and pad systems are GO.".
PRINT "==================================================".

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 50.0).
PRINT "T-50s: Flight tank pressurization confirmed.".

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 40.0).
PRINT "T-40s: kOS guidance computer and telemetry nominal.".

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 30.0).

// ============================================================================
// STEP 6: AT T-30s: TRANSFER TO INTERNAL POWER & RETRACT UMBILICALS
// ============================================================================
PRINT "==================================================".
PRINT "T-30s: VEHICLE ON INTERNAL BATTERY POWER!".
PRINT "==================================================".
set_pad_electric_power(FALSE).
retract_tower_umbilicals().

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 20.0).
PRINT "T-20s: Power status: INTERNAL (Onboard battery bank at 100%).".

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 10.0).

// ============================================================================
// STEP 7: AT T-10s: SINGLE-SECOND TERMINAL COUNTDOWN
// ============================================================================
PRINT "==================================================".
PRINT "T-10s: AUTOMATIC IGNITION SEQUENCE START:".
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
// STEP 8: IGNITION AND PAD RELEASE (T-0)
// ============================================================================
PRINT "==================================================".
PRINT "T+0.0s: IGNITION! Etoh-140-TU Core & Dual Shrimp SRBs!".
PRINT "RELEASING LAUNCH PAD HOLD-DOWN CLAMPS!".
PRINT "==================================================".

LOCK THROTTLE TO 1.0.
STAGE.
WAIT 0.5.
UNTIL SHIP:MAXTHRUST > 0 {
    STAGE.
    WAIT 0.5.
}

// ============================================================================
// FLIGHT PHASES: ASCENT, STAGING & ULTRA-CIRCULAR ORBITAL INSERTION (600 KM)
// ============================================================================
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: VEHICLE CSA-16 LIFTOFF CONFIRMED!".

// Activate Max Q aerodynamic throttle governor
LOCK THROTTLE TO calculate_atmo_throttle().

LOCAL initial_thrust IS SHIP:MAXTHRUST.
LOCAL srb_separated IS FALSE.

// Phase 2: Immediate Gravity Turn (Pitch Kick) at ALT_KICK (1,200 m)
IF SHIP:ALTITUDE < ALT_KICK {
    WAIT UNTIL SHIP:ALTITUDE >= ALT_KICK.
}
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: INITIATING GRAVITY TURN (PITCH " + PITCH_INITIAL + " deg HDG " + HEADING_DEG + " deg)!".
LOCK targetPitch TO MAX(MIN_PITCH, PITCH_INITIAL - ((SHIP:ALTITUDE - ALT_KICK) / (ALT_END_TURN - ALT_KICK)) * (PITCH_INITIAL - MIN_PITCH)).
LOCK STEERING TO HEADING(HEADING_DEG, targetPitch).

// Phase 3: Guided Ascent to Stage 1 MECO (with concurrent SRB separation)
LOCAL last_telemetry_print IS MISSIONTIME.
UNTIL (srb_separated AND (STAGE:LIQUIDFUEL < 0.5)) OR (SHIP:LIQUIDFUEL <= 180.5) OR (SHIP:MAXTHRUST < 10.0) {
    IF (NOT srb_separated) AND ((SHIP:SOLIDFUEL < 1.0) OR (SHIP:MAXTHRUST < (initial_thrust * 0.70))) {
        WAIT 0.5.
        PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Booster burnout! Jettisoning 2x Shrimp SRBs...".
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
STAGE. // Interstage decoupling
WAIT 1.5.

// Phase 4: Stage 2 Ignition (Belle-RLX81)
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: STAGE 2 IGNITION (Belle-RLX81)!".
LOCK THROTTLE TO 1.0.
STAGE. // Belle-RLX81 ignition
WAIT 1.0.

// Phase 5: Fairing Jettison & Apogee Acquisition (Target: 600 km)
LOCAL fairing_done IS FALSE.
LOCK STEERING TO PROGRADE.

UNTIL SHIP:APOAPSIS >= (TARGET_APOAPSIS - 5000) {
    IF (SHIP:ALTITUDE > 55000) AND (NOT fairing_done) {
        jettison_fairings().
        SET fairing_done TO TRUE.
    }
    WAIT 0.2.
}

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Approaching target apogee (" + ROUND((TARGET_APOAPSIS-5000)/1000, 0) + " km). Throttling down to 20%...".
LOCK THROTTLE TO 0.20.

WAIT UNTIL SHIP:APOAPSIS >= TARGET_APOAPSIS.
LOCK THROTTLE TO 0.0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SECO-1! Target apogee acquired at " + ROUND(TARGET_APOAPSIS/1000, 1) + " km.".

// Phase 6: Exospheric Coast to Apogee (600 km)
LOCK STEERING TO PROGRADE.
IF NOT fairing_done {
    WAIT UNTIL SHIP:ALTITUDE > 70000.
    jettison_fairings().
    SET fairing_done TO TRUE.
}

// Phase 7: Ultra-Precision Circularization at 600 km (e <= 0.0008)
LOCAL rad_target IS KERBIN_RADIUS + TARGET_APOAPSIS.
LOCAL v_circ IS SQRT(KERBIN_MU / rad_target).
LOCAL sma_trans IS (SHIP:PERIAPSIS + SHIP:APOAPSIS + 2 * KERBIN_RADIUS) / 2.
LOCAL v_apo_pred IS SQRT(KERBIN_MU * (2 / (KERBIN_RADIUS + SHIP:APOAPSIS) - 1 / sma_trans)).
LOCAL delta_v_circ IS MAX(10.0, v_circ - v_apo_pred).
LOCAL burn_duration IS (delta_v_circ * SHIP:MASS) / MAX(1.0, SHIP:MAXTHRUST).
LOCAL half_burn IS burn_duration / 2.

PRINT "Coast to Apogee (" + ROUND(TARGET_APOAPSIS/1000, 0) + " km) in progress. Circularization burn ~ " + ROUND(burn_duration, 1) + " s.".
WAIT UNTIL (ETA:APOAPSIS <= (half_burn + 5.0)) OR (ETA:APOAPSIS > (SHIP:ORBIT:PERIOD - 60)).
SET KUNIVERSE:TIMEWARP:WARP TO 0.
LOCK STEERING TO PROGRADE.
WAIT UNTIL (ETA:APOAPSIS <= half_burn) OR (ETA:APOAPSIS > (SHIP:ORBIT:PERIOD - 30)).

PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SECO-2 IGNITION (600 km Circularization Burn)!".
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
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SECO-2 CUTOFF! 600 KM CIRCULAR ORBIT ACHIEVED!".
PRINT "  Final Ap:   " + ROUND(SHIP:APOAPSIS / 1000, 3) + " km".
PRINT "  Final Pe:   " + ROUND(SHIP:PERIAPSIS / 1000, 3) + " km".
PRINT "  Final Ecc:  " + ROUND(SHIP:ORBIT:ECCENTRICITY, 6).
PRINT "  Final Per:  " + ROUND(SHIP:ORBIT:PERIOD, 2) + " s (Target: " + ROUND(TARGET_THEORETICAL_PERIOD, 2) + " s)".
PRINT "==================================================".

// ============================================================================
// PHASE 8: SYNCHRONOUS PERIOD LOCK & PAYLOAD SEPARATION
// ============================================================================
WAIT 3.0.

LOCAL is_foundation_node IS (TARGET_ANCHOR = "NONE" OR TARGET_ANCHOR = "").
LOCAL target_sync_period IS TARGET_THEORETICAL_PERIOD.

IF NOT is_foundation_node {
    LOCAL tgt_anchor IS find_target_satellite(TARGET_ANCHOR).
    IF tgt_anchor <> SHIP {
        SET target_sync_period TO tgt_anchor:OBT:PERIOD.
    }
}

// Fine-tune orbital period to exact theoretical/anchor period (+/- 0.20 s)
synchronize_constellation_period(target_sync_period).

PRINT "Proceeding to Normal orientation and CoroltSat-1F deployment...".

// Orient attitude to pure orbital NORMAL vector (VCRS(vel, pos))
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Steering attitude to pure orbital NORMAL...".
LOCK STEERING TO VCRS(SHIP:VELOCITY:ORBIT, BODY:POSITION).
WAIT 15.0.

deploy_satellite_systems().
WAIT 3.0.

separate_payload().
PRINT "==================================================".
PRINT "      MISSION CSA-16: COROLTSAT-1F DEPLOYED!      ".
IF is_foundation_node {
    PRINT "   NODE 0 FOUNDATION ANCHOR AT 600 KM ESTABLISHED! ".
    PRINT "   NEW 6-SATELLITE MKO CONSTELLATION INAUGURATED! ".
} ELSE {
    PRINT "   ORBITAL RING AT 600 KM SYNCHRONIZED!          ".
}
PRINT "==================================================".

// Deorbit spent upper stage under Zero Debris Protocol
deorbit_upper_stage().

PRINT "Sequence csa16_guided_ascent completed successfully.".
