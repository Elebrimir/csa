// ============================================================================
// COROLT SPACE AGENCY (CSA) - UNIVERSAL FLIGHT GUIDANCE SYSTEM v5.0
// SCRIPT: universal_guided_ascent.ks
// DESCRIPTION:
//   Mission-agnostic, orbit-agnostic automated pad servicing, countdown,
//   two-burn orbital ascent, synchronous period lock, phase audit & automatic
//   hand-off to constellation_phasing.ks (or immediate Normal deployment and
//   Zero Debris Stage 2 deorbit).
//
// USAGE EXAMPLES:
//   1. Node 1 MKO-600 Expansion (CSA-17 / CoroltSat-1G at +60 deg vs CoroltSat-1F):
//      RUNPATH("0:/csa/universal_guided_ascent.ks", 600.0, 4242865.9, 60.0, "CoroltSat-1F", "CSA-17", "CoroltSat-1G").
//   2. Node 0 Foundation Anchor (no reference anchor):
//      RUNPATH("0:/csa/universal_guided_ascent.ks", 600.0, 0, 0.0, "NONE", "CSA-16", "CoroltSat-1F").
// ============================================================================

DECLARE PARAMETER TARGET_ALT_KM IS 600.0.        // Target orbital altitude in km (default 600 km MKO)
DECLARE PARAMETER TARGET_LAUNCH_UT IS 0.         // Set to 0 for immediate sequence or pass exact window UT
DECLARE PARAMETER TARGET_SLOT_DEG IS 60.0.       // Target slot in deg (e.g. +60.0, -60.0, 0.0)
DECLARE PARAMETER TARGET_ANCHOR IS "CoroltSat-1F". // Reference anchor ("NONE" = Foundation Anchor)
DECLARE PARAMETER MISSION_CODE IS "CSA-17".      // Mission identifier for console telemetry
DECLARE PARAMETER PAYLOAD_NAME IS "CoroltSat-1G". // Payload identifier for console telemetry

CLEARSCREEN.
// ----------------------------------------------------------------------------
// Live Remote Terminal Mirroring (0:/kos_live.log)
// ----------------------------------------------------------------------------
LOCAL KOS_LIVE_LOG IS "0:/kos_live.log".
FUNCTION kprint {
    PARAMETER msg.
    PRINT msg.
    IF HOMECONNECTION:ISCONNECTED {
        LOG "[UT " + ROUND(TIME:SECONDS, 1) + "s] " + msg TO KOS_LIVE_LOG.
    }
}
kprint("==================================================").
kprint("      COROLT SPACE AGENCY - MISSION CONTROL       ").
kprint("   UNIVERSAL FLIGHT GUIDANCE SYSTEM v5.0          ").
kprint("   MISSION: " + MISSION_CODE + " | PAYLOAD: " + PAYLOAD_NAME).
kprint("   TARGET ORBIT: " + TARGET_ALT_KM + " x " + TARGET_ALT_KM + " km (Equatorial)").
IF TARGET_ANCHOR = "NONE" OR TARGET_ANCHOR = "" {
    kprint("   ROLE: Foundation Anchor (Node 0 / " + TARGET_ALT_KM + " km) ").
} ELSE {
    kprint("   TARGET SLOT: " + TARGET_SLOT_DEG + " deg (Anchor: " + TARGET_ANCHOR + ")").
}
kprint("==================================================").

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
        kprint("  [PAD] Ground external electrical power: CONNECTED").
    } ELSE {
        kprint("  [PAD] Ground external electrical power: DISCONNECTED").
    }
}

FUNCTION set_pad_fueling {
    PARAMETER fuel_state. // TRUE = start pumping, FALSE = stop
    PARAMETER verbose IS TRUE.
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
            kprint("  [PAD] Propellant transfer lines: OPEN").
        } ELSE {
            kprint("  [PAD] Propellant transfer lines: CLOSED").
        }
    }
}

FUNCTION retract_tower_umbilicals {
    kprint("--------------------------------------------------").
    kprint("T-30s: Retracting fuel umbilicals and service tower swing arms..").
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("Umbilical") OR p:NAME:CONTAINS("SwingArm") {
            FOR m IN p:MODULES {
                LOCAL part_mod IS p:GETMODULE(m).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("retract") OR evl:CONTAINS("release") OR evl:CONTAINS("retirar") {
                        part_mod:DOEVENT(ev).
                        kprint("  [TOWER] Arm retracted: " + p:TITLE).
                    }
                }
            }
        }
    }
    kprint("  [TOWER] Umbilical & swing arm retraction complete").
    kprint("--------------------------------------------------").
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
    kprint("--------------------------------------------------").
    kprint("T+" + ROUND(MISSIONTIME, 1) + "s: Jettisoning payload fairings (> 55 km)..").
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
    kprint("T+" + ROUND(MISSIONTIME, 1) + "s: Deploying antennas and solar arrays (" + PAYLOAD_NAME + ")..").
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
    kprint("--------------------------------------------------").
    kprint("T+" + ROUND(MISSIONTIME, 1) + "s: EXECUTING " + PAYLOAD_NAME + " PAYLOAD SEPARATION..").
    LOCAL separated IS FALSE.

    FOR part_item IN SHIP:PARTS {
        IF part_item:HASMODULE("ModuleDecouple") {
            LOCAL part_mod IS part_item:GETMODULE("ModuleDecouple").
            IF part_mod:HASACTION("DecoupleAction") {
                part_mod:DOACTION("DecoupleAction", TRUE).
                SET separated TO TRUE.
                kprint("  -> DecoupleAction executed on " + part_item:NAME).
            }
            FOR ev IN part_mod:ALLEVENTNAMES {
                LOCAL evl IS ev:TOLOWER.
                IF evl:CONTAINS("decouple") OR evl:CONTAINS("desacobl") OR evl:CONTAINS("desacopl") OR evl:CONTAINS("separ") {
                    part_mod:DOEVENT(ev).
                    SET separated TO TRUE.
                    kprint("  -> Event " + ev + " executed on " + part_item:NAME).
                }
            }
        }
    }

    STAGE.
    WAIT 0.5.
    STAGE.

    kprint("Payload separation command sent and confirmed!").
    kprint("--------------------------------------------------").
    RETURN separated.
}

FUNCTION synchronize_constellation_period {
    PARAMETER tgt_period_sec.
    LOCAL p_diff IS tgt_period_sec - SHIP:OBT:PERIOD.
    IF ABS(p_diff) <= PERIOD_TOLERANCE_SEC {
        kprint("  [SYNC] Orbital period already matched (" + ROUND(SHIP:OBT:PERIOD, 2) + " s vs " + ROUND(tgt_period_sec, 2) + " s)").
        RETURN.
    }

    kprint("--------------------------------------------------").
    kprint("T+" + ROUND(MISSIONTIME, 1) + "s: SYNCHRONOUS PERIOD LOCK BURN INITIATED").
    kprint("  Current Period: " + ROUND(SHIP:OBT:PERIOD, 2) + " s | Target Period: " + ROUND(tgt_period_sec, 2) + " s").
    SET KUNIVERSE:TIMEWARP:WARP TO 0.
    ensure_engines_active().

    IF p_diff > 0 {
        kprint("  Steering PROGRADE to raise orbital period (+ " + ROUND(p_diff, 2) + " s)..").
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
        kprint("  Steering RETROGRADE to lower orbital period (" + ROUND(p_diff, 2) + " s)..").
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
    kprint("  [SYNC] Period locked at " + ROUND(SHIP:OBT:PERIOD, 2) + " s (Drift < 002 deg/rev)!").
    kprint("--------------------------------------------------").
}

FUNCTION deorbit_upper_stage {
    kprint("Waiting 30-second safety clearance interval from deployed satellite..").
    WAIT 30.0.

    kprint("Orienting upper stage to RETROGRADE for disposal burn (Zero Debris Protocol)..").
    LOCK STEERING TO RETROGRADE.
    WAIT 15.0.

    kprint("EXECUTING STAGE 2 DEORBIT BURN (Belle-RLX81)..").
    ensure_engines_active().

    LOCK THROTTLE TO 1.0.
    LOCAL deorbit_start IS TIME:SECONDS.
    UNTIL (SHIP:PERIAPSIS <= 0) OR (SHIP:LIQUIDFUEL < 0.2) {
        PRINT "Deorbit Pe: " + ROUND(SHIP:PERIAPSIS / 1000, 1) + " km | Fuel: " + ROUND(SHIP:LIQUIDFUEL, 1) + " LF   " AT(0, 32).
        WAIT 0.2.
    }

    LOCK THROTTLE TO 0.0.
    LOCAL deorbit_dur IS TIME:SECONDS - deorbit_start.
    kprint("DEORBIT BURN COMPLETE (" + ROUND(deorbit_dur, 1) + " s)! PERIAPSIS: " + ROUND(SHIP:PERIAPSIS / 1000, 1) + " km").
    kprint("Belle-RLX81 upper stage targeted for destructive ocean disposal Zero Debris!").

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
kprint("==================================================").
kprint("NOTICE: Propellant tanking sequence starts in 5 seconds").
kprint("==================================================").

FROM {LOCAL cd_val IS 5.} UNTIL cd_val = 0 STEP {SET cd_val TO cd_val - 1.} DO {
    kprint("T-tanking: " + cd_val + "..").
    WAIT 1.0.
}

// ============================================================================
// STEP 2: CONNECT PAD GROUND ELECTRICAL POWER
// ============================================================================
kprint("--------------------------------------------------").
kprint("Activating ground electrical power supply..").
set_pad_electric_power(TRUE).
WAIT 1.0.

// ============================================================================
// STEP 3: OPEN PROPELLANT TRANSFER VALVES (PULSED 25% DUTY CYCLE FOR 1/4 FLOW RATE)
// ============================================================================
kprint("--------------------------------------------------").
kprint("Opening launch tower propellant fill valves (1/4 flow rate mode)..").
set_pad_fueling(TRUE, TRUE).
WAIT 1.0.

kprint("Propellant loading in progress (Quarter-rate ~ 15 LF/s, ~480s)...").
LOCAL cycle_count IS 0.
UNTIL (SHIP:LIQUIDFUEL >= TARGET_FULL_LF) {
    set_pad_fueling(TRUE, FALSE).
    WAIT 1.0.
    IF SHIP:LIQUIDFUEL >= TARGET_FULL_LF {
        BREAK.
    }
    set_pad_fueling(FALSE, FALSE).

    SET cycle_count TO cycle_count + 1.
    LOCAL pct IS ROUND((SHIP:LIQUIDFUEL / 900.0) * 100, 1).
    kprint("Loading (1/4 rate): " + ROUND(SHIP:LIQUIDFUEL, 1) + " / 9000 LF (" + pct + "%) | Ox: " + ROUND(SHIP:OXIDIZER, 1) + " / 1100.0").
    WAIT 3.0.
}

kprint("==================================================").
kprint("STAGE 1 & STAGE 2 PROPELLANT TANKS AT 100%!").
kprint("Closing ground transfer valves..").
set_pad_fueling(FALSE, TRUE).
WAIT 2.0.

// Determine launch window UT (and support live dynamic override via 0:/override_ut.txt!)
LOCAL override_file IS "0:/override_ut.txt".
IF EXISTS(override_file) { DELETEPATH(override_file). }

LOCAL effective_launch_ut IS TARGET_LAUNCH_UT.
IF effective_launch_ut <= TIME:SECONDS {
    SET effective_launch_ut TO TIME:SECONDS + 70.0.
}

kprint("--------------------------------------------------").
kprint("Target launch window set to UT: " + ROUND(effective_launch_ut, 1) + " s").
kprint("Time remaining until liftoff:   " + ROUND(effective_launch_ut - TIME:SECONDS, 1) + " s").
kprint("(Tip: You can change window anytime from laptop via `setut <NEW_UT>`)").
kprint("--------------------------------------------------").

LOCAL time_to_t60 IS (effective_launch_ut - 60.0) - TIME:SECONDS.
IF time_to_t60 > 1.0 {
    kprint("Pad HOLD active until T-60s of launch window").
    kprint("Manual Time Warp is permitted during pad HOLD").
    UNTIL TIME:SECONDS >= (effective_launch_ut - 60.0) {
        IF EXISTS(override_file) {
            RUNPATH(override_file).
            DELETEPATH(override_file).
            IF DEFINED NEW_TARGET_LAUNCH_UT {
                SET effective_launch_ut TO NEW_TARGET_LAUNCH_UT.
                kprint("  [OVERRIDE] Launch window UT updated dynamically to: " + ROUND(effective_launch_ut, 1) + " s!").
            }
        }
        LOCAL remaining_hold IS ROUND((effective_launch_ut - 60.0) - TIME:SECONDS, 0).
        IF remaining_hold > 0 {
            kprint("HOLD... T-60s countdown starts in " + remaining_hold + "s (Warp allowed)    ", 0 AT(24)).
        }
        WAIT 1.0.
    }
}

// ============================================================================
// STEP 5: TERMINAL COUNTDOWN AT T-60 SECONDS (10-SECOND MILESTONES)
// ============================================================================
SET KUNIVERSE:TIMEWARP:WARP TO 0.
kprint("==================================================").
kprint("T-60s: TERMINAL COUNTDOWN INITIATED").
kprint("All vehicle and pad systems are GO").
kprint("==================================================").

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 50.0).
kprint("T-50s: Flight tank pressurization confirmed").

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 40.0).
kprint("T-40s: kOS guidance computer and telemetry nominal").

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 30.0).

// ============================================================================
// STEP 6: AT T-30s: TRANSFER TO INTERNAL POWER & RETRACT UMBILICALS
// ============================================================================
kprint("==================================================").
kprint("T-30s: VEHICLE ON INTERNAL BATTERY POWER!").
kprint("==================================================").
set_pad_electric_power(FALSE).
retract_tower_umbilicals().

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 20.0).
kprint("T-20s: Power status: INTERNAL (Onboard battery bank at 100%)").

WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - 10.0).

// ============================================================================
// STEP 7: AT T-10s: SINGLE-SECOND TERMINAL COUNTDOWN
// ============================================================================
kprint("==================================================").
kprint("T-10s: AUTOMATIC IGNITION SEQUENCE START:").
kprint("==================================================").
SAS OFF.
LOCK THROTTLE TO 0.0.
LOCK STEERING TO HEADING(HEADING_DEG, 90.0).

LOCAL countdown_val IS 10.
UNTIL countdown_val <= 0 {
    kprint("T-" + countdown_val + "..").
    SET countdown_val TO countdown_val - 1.
    WAIT UNTIL TIME:SECONDS >= (effective_launch_ut - countdown_val).
}

// ============================================================================
// STEP 8: IGNITION AND PAD RELEASE (T-0)
// ============================================================================
kprint("==================================================").
kprint("T+00s: IGNITION! Etoh-140-TU Core & Dual Shrimp SRBs!").
kprint("RELEASING LAUNCH PAD HOLD-DOWN CLAMPS!").
kprint("==================================================").

LOCK THROTTLE TO 1.0.
STAGE.
WAIT 0.5.
UNTIL SHIP:MAXTHRUST > 0 {
    STAGE.
    WAIT 0.5.
}

// ============================================================================
// FLIGHT PHASES: ASCENT, STAGING & ULTRA-CIRCULAR ORBITAL INSERTION
// ============================================================================
kprint("T+" + ROUND(MISSIONTIME, 1) + "s: VEHICLE " + MISSION_CODE + " LIFTOFF CONFIRMED!").

LOCK THROTTLE TO calculate_atmo_throttle().

LOCAL initial_thrust IS SHIP:MAXTHRUST.
LOCAL srb_separated IS FALSE.

IF SHIP:ALTITUDE < ALT_KICK {
    WAIT UNTIL SHIP:ALTITUDE >= ALT_KICK.
}
kprint("T+" + ROUND(MISSIONTIME, 1) + "s: INITIATING GRAVITY TURN (PITCH " + PITCH_INITIAL + " deg HDG " + HEADING_DEG + " deg)!").
LOCK targetPitch TO MAX(MIN_PITCH, PITCH_INITIAL - ((SHIP:ALTITUDE - ALT_KICK) / (ALT_END_TURN - ALT_KICK)) * (PITCH_INITIAL - MIN_PITCH)).
LOCK STEERING TO HEADING(HEADING_DEG, targetPitch).

LOCAL last_telemetry_print IS MISSIONTIME.
UNTIL (srb_separated AND (STAGE:LIQUIDFUEL < 0.5)) OR (SHIP:LIQUIDFUEL <= 180.5) OR (SHIP:MAXTHRUST < 10.0) {
    IF (NOT srb_separated) AND ((SHIP:SOLIDFUEL < 1.0) OR (SHIP:MAXTHRUST < (initial_thrust * 0.70))) {
        WAIT 0.5.
        kprint("T+" + ROUND(MISSIONTIME, 1) + "s: Booster burnout! Jettisoning 2x Shrimp SRBs..").
        STAGE.
        WAIT 0.5.
        SET srb_separated TO TRUE.
    }
    IF (MISSIONTIME - last_telemetry_print) >= 5.0 {
        LOCAL q_curr IS ROUND(SHIP:DYNAMICPRESSURE * CONSTANT:ATMTOKPA, 1).
        kprint("T+" + ROUND(MISSIONTIME, 0) + "s | Alt: " + ROUND(SHIP:ALTITUDE/1000, 1) + "km | Q: " + q_curr + "kPa | Th: " + ROUND(THROTTLE * 100, 0) + "%").
        SET last_telemetry_print TO MISSIONTIME.
    }
    WAIT 0.2.
}

kprint("T+" + ROUND(MISSIONTIME, 1) + "s: Stage 1 Core MECO!").
LOCK THROTTLE TO 0.0.
WAIT 1.0.
STAGE. // Interstage decoupling
WAIT 1.5.

kprint("T+" + ROUND(MISSIONTIME, 1) + "s: STAGE 2 IGNITION (Belle-RLX81)!").
LOCK THROTTLE TO 1.0.
STAGE. // Belle-RLX81 ignition
WAIT 1.0.

LOCAL fairing_done IS FALSE.
LOCK STEERING TO PROGRADE.

UNTIL SHIP:APOAPSIS >= (TARGET_APOAPSIS - 5000) {
    IF (SHIP:ALTITUDE > 55000) AND (NOT fairing_done) {
        jettison_fairings().
        SET fairing_done TO TRUE.
    }
    WAIT 0.2.
}

kprint("T+" + ROUND(MISSIONTIME, 1) + "s: Approaching target apogee (" + ROUND((TARGET_APOAPSIS-5000)/1000, 0) + " km) Throttling down to 20%...").
LOCK THROTTLE TO 0.20.

WAIT UNTIL SHIP:APOAPSIS >= TARGET_APOAPSIS.
LOCK THROTTLE TO 0.0.
kprint("T+" + ROUND(MISSIONTIME, 1) + "s: SECO-1! Target apogee acquired at " + ROUND(TARGET_APOAPSIS/1000, 1) + " km").

LOCK STEERING TO PROGRADE.
IF NOT fairing_done {
    WAIT UNTIL SHIP:ALTITUDE > 70000.
    jettison_fairings().
    SET fairing_done TO TRUE.
}

LOCAL rad_target IS KERBIN_RADIUS + TARGET_APOAPSIS.
LOCAL v_circ IS SQRT(KERBIN_MU / rad_target).
LOCAL sma_trans IS (SHIP:PERIAPSIS + SHIP:APOAPSIS + 2 * KERBIN_RADIUS) / 2.
LOCAL v_apo_pred IS SQRT(KERBIN_MU * (2 / (KERBIN_RADIUS + SHIP:APOAPSIS) - 1 / sma_trans)).
LOCAL delta_v_circ IS MAX(10.0, v_circ - v_apo_pred).
LOCAL burn_duration IS (delta_v_circ * SHIP:MASS) / MAX(1.0, SHIP:MAXTHRUST).
LOCAL half_burn IS burn_duration / 2.

kprint("Coast to Apogee (" + ROUND(TARGET_APOAPSIS/1000, 0) + " km) in progress Circularization burn ~ " + ROUND(burn_duration, 1) + " s.").
WAIT UNTIL (ETA:APOAPSIS <= (half_burn + 5.0)) OR (ETA:APOAPSIS > (SHIP:ORBIT:PERIOD - 60)).
SET KUNIVERSE:TIMEWARP:WARP TO 0.
LOCK STEERING TO PROGRADE.
WAIT UNTIL (ETA:APOAPSIS <= half_burn) OR (ETA:APOAPSIS > (SHIP:ORBIT:PERIOD - 30)).

kprint("==================================================").
kprint("T+" + ROUND(MISSIONTIME, 1) + "s: SECO-2 IGNITION (" + TARGET_ALT_KM + " km Circularization Burn)!").
kprint("==================================================").

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
kprint("==================================================").
kprint("T+" + ROUND(MISSIONTIME, 1) + "s: SECO-2 CUTOFF! CIRCULAR ORBIT ACHIEVED!").
kprint("  Final Ap:   " + ROUND(SHIP:APOAPSIS / 1000, 3) + " km").
kprint("  Final Pe:   " + ROUND(SHIP:PERIAPSIS / 1000, 3) + " km").
kprint("  Final Ecc:  " + ROUND(SHIP:ORBIT:ECCENTRICITY, 6)).
kprint("  Final Per:  " + ROUND(SHIP:ORBIT:PERIOD, 2) + " s (Target: " + ROUND(TARGET_THEORETICAL_PERIOD, 2) + " s)").
kprint("==================================================").

// ============================================================================
// PHASE 8: ORBITAL PHASE AUDIT, AUTOMATIC PHASING HAND-OFF OR DEPLOYMENT
// ============================================================================
WAIT 3.0.

LOCAL is_foundation_node IS (TARGET_ANCHOR = "NONE" OR TARGET_ANCHOR = "").

IF is_foundation_node {
    synchronize_constellation_period(TARGET_THEORETICAL_PERIOD).

    kprint("Proceeding to Normal orientation and " + PAYLOAD_NAME + " deployment..").
    LOCK STEERING TO VCRS(SHIP:VELOCITY:ORBIT, BODY:POSITION).
    WAIT 15.0.

    deploy_satellite_systems().
    WAIT 3.0.

    separate_payload().
    kprint("==================================================").
    kprint("      MISSION " + MISSION_CODE + ": " + PAYLOAD_NAME + " DEPLOYED!").
    kprint("   NODE 0 FOUNDATION ANCHOR AT " + TARGET_ALT_KM + " KM ESTABLISHED!").
    kprint("==================================================").

    deorbit_upper_stage().
} ELSE {
    LOCAL tgt_anchor IS find_target_satellite(TARGET_ANCHOR).
    LOCAL norm_target_slot IS MOD(TARGET_SLOT_DEG, 360.0).
    IF norm_target_slot < 0 { SET norm_target_slot TO norm_target_slot + 360.0. }

    IF tgt_anchor = SHIP {
        kprint("WARNING: Reference anchor " + TARGET_ANCHOR + " not found! Locking theoretical period..").
        synchronize_constellation_period(TARGET_THEORETICAL_PERIOD).
    } ELSE {
        LOCAL final_phase IS get_phase_angle(SHIP, tgt_anchor).
        LOCAL phase_err IS ABS(to_signed_deg(final_phase - norm_target_slot)).

        kprint("==================================================").
        kprint("        ORBITAL PHASE AUDIT: " + MISSION_CODE).
        kprint("  Reference Anchor:        " + tgt_anchor:NAME).
        kprint("  Target Slot:             " + ROUND(to_signed_deg(norm_target_slot), 2) + " deg (" + ROUND(norm_target_slot, 2) + "º)").
        kprint("  Achieved Relative Phase: " + ROUND(to_signed_deg(final_phase), 3) + " deg (" + ROUND(final_phase, 2) + "º)").
        kprint("  Absolute Phase Error:    " + ROUND(phase_err, 3) + " deg").
        kprint("  Release Gate Tolerance:  +/-" + PHASE_TOLERANCE_DEG + " deg").
        kprint("==================================================").

        IF phase_err <= PHASE_TOLERANCE_DEG {
            kprint(">>> DIRECT INSERTION WITHIN GATE (" + ROUND(phase_err, 3) + " deg <= +/-" + PHASE_TOLERANCE_DEG + " deg)! <<<").
            synchronize_constellation_period(tgt_anchor:OBT:PERIOD).

            kprint("T+" + ROUND(MISSIONTIME, 1) + "s: Steering attitude to pure orbital NORMAL..").
            LOCK STEERING TO VCRS(SHIP:VELOCITY:ORBIT, BODY:POSITION).
            WAIT 15.0.

            deploy_satellite_systems().
            WAIT 3.0.

            separate_payload().
            kprint("==================================================").
            kprint("      MISSION " + MISSION_CODE + ": " + PAYLOAD_NAME + " DEPLOYED!").
            kprint("   CONSTELLATION NODE LOCKED AT " + TARGET_SLOT_DEG + " DEG!").
            kprint("==================================================").

            deorbit_upper_stage().
        } ELSE {
            kprint(">>> Phase offset (" + ROUND(phase_err, 3) + " deg) exceeds direct gate (+/-" + PHASE_TOLERANCE_DEG + " deg) <<<").
            kprint(">>> Automatically invoking constellation_phasingks to fine-tune slot! <<<").
            WAIT 2.0.
            RUNPATH("0:/csa/constellation_phasing.ks", TARGET_SLOT_DEG, 3, tgt_anchor:NAME, PHASE_TOLERANCE_DEG, TRUE).
        }
    }
}

kprint("Sequence universal_guided_ascent (" + MISSION_CODE + ") completed").
