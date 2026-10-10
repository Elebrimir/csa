// ============================================================================
// COROLT SPACE AGENCY (CSA) - FLIGHT GUIDANCE SYSTEM v4.1 (CALIBRATED)
// MISSION: CSA-12 (Kerbin Comms Constellation Anchor - CoroltSat-1B)
// VEHICLE: Corolt-IV B Unit 2 (Etoh-140-TU Core + 2x Shrimp SRB + Belle-RLX81)
// PAYLOAD: CoroltSat-1B (248 kg, 0.625m Payload Truss, Stayputnik, Codac-A23 1Mm)
// EMPIRICAL CALIBRATION: Post-CSA-11 Telemetry (Ap 269.1 km, Max Q 17.8 kPa)
// IMPROVEMENTS INTRODUCED:
//   1. Full Shrimp SRB propellant burn via SHIP:SOLIDFUEL exhaustion (~45s).
//   2. Calibrated dynamic throttle governor (tuned for higher booster velocity).
//   3. In-flight engine breakdown fail-safe with emergency satellite safeing.
//   4. Precision apogee taper (25% throttle at Ap-5km) for exact 300.0 km insertion.
//   5. Symmetrical half-burn circularization at apogee (SECO-2) targeting e < 0.002.
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "      COROLT SPACE AGENCY - MISSION CONTROL       ".
PRINT "   MISSION: CSA-12 | CoroltSat-1B (Constellation) ".
PRINT "   VEHICLE: Corolt-IV B #2 | TARGET: 300x300 km   ".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Flight Constants & Target Orbital Parameters
// ----------------------------------------------------------------------------
SET TARGET_APOAPSIS TO 300000.      // Target Apogee: 300 km (300,000 m)
SET TARGET_PERIAPSIS TO 300000.     // Target Perigee: 300 km (300,000 m)
SET ALT_KICK TO 1200.               // Altitude for pitch kick initiation (m)
SET PITCH_INITIAL TO 84.0.          // Initial pitch angle after kick (degrees)
SET HEADING_DEG TO 90.0.            // Equatorial East launch azimuth (0.0º inc)
SET ALT_END_TURN TO 48000.          // Altitude where gravity turn flattens (m)
SET MIN_PITCH TO 15.0.              // Minimum pitch angle before MECO (degrees)
SET KERBIN_MU TO 3.5316000e12.      // Kerbin standard gravitational parameter
SET KERBIN_RADIUS TO 600000.        // Kerbin equatorial radius (m)

// Aerodynamic & Load Limits (Dynamic Atmospheric Throttle Governor)
SET TARGET_MAX_Q_KPA TO 32.0.       // Maximum Dynamic Pressure ceiling (kPa)
SET MIN_TWR_FLOOR TO 1.30.          // Minimum TWR floor to avoid gravity drag penalty
SET MAX_G_CEILING TO 3.80.          // Maximum acceleration load (G) to protect payload

// ----------------------------------------------------------------------------
// Subsystem Helper Functions
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
                        PRINT "  [FAIRING] Event fired: " + ev + " on " + part_item:TITLE.
                    }
                }
            }
        }
    }
    // Fail-safe fallback if no part module event was found
    IF NOT fairing_jettisoned {
        IF STAGE:NUMBER >= 1 {
            STAGE.
            SET fairing_jettisoned TO TRUE.
            PRINT "  [FAIRING] Staged via active stage.".
        }
    }
    RETURN fairing_jettisoned.
}

FUNCTION separate_payload {
    PRINT "--------------------------------------------------".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SEPARATING PAYLOAD (CoroltSat-1B)...".
    LOCAL separated IS FALSE.
    FOR part_item IN SHIP:PARTS {
        IF part_item:NAME:CONTAINS("Decoupler") OR part_item:NAME:CONTAINS("Adapter") OR part_item:NAME:CONTAINS("OGO") {
            FOR mod_name IN part_item:MODULES {
                LOCAL part_mod IS part_item:GETMODULE(mod_name).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("decouple") OR evl:CONTAINS("desacoplar") OR evl:CONTAINS("separate") {
                        part_mod:DOEVENT(ev).
                        SET separated TO TRUE.
                        PRINT "  [PAYLOAD] Decoupler triggered: " + ev + " on " + part_item:TITLE.
                    }
                }
            }
        }
    }
    // Fail-safe fallback: trigger active stage if part event was not found
    IF NOT separated {
        PRINT "  [PAYLOAD] Triggering active stage for payload release...".
        STAGE.
        SET separated TO TRUE.
    }
    PRINT "==================================================".
}

FUNCTION deploy_satellite_systems {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Deploying communications and solar arrays...".
    AG3 ON. // Trigger Action Group 3 standard
    FOR part_item IN SHIP:PARTS {
        FOR mod_name IN part_item:MODULES {
            LOCAL part_mod IS part_item:GETMODULE(mod_name).
            FOR ev IN part_mod:ALLEVENTNAMES {
                LOCAL evl IS ev:TOLOWER.
                IF evl:CONTAINS("extend") OR evl:CONTAINS("deploy") OR evl:CONTAINS("desplegar") OR evl:CONTAINS("activar") {
                    IF NOT evl:CONTAINS("chute") AND NOT evl:CONTAINS("decouple") {
                        part_mod:DOEVENT(ev).
                    }
                }
            }
        }
    }
}

FUNCTION calculate_atmo_throttle {
    // 1. Dynamic pressure in kPa (kOS SHIP:DYNAMICPRESSURE is in atm; 1 atm = 101.325 kPa)
    LOCAL q_kpa IS SHIP:DYNAMICPRESSURE * 101.325.

    // 2. Local gravitational acceleration & maximum available TWR
    LOCAL rad_local IS KERBIN_RADIUS + SHIP:ALTITUDE.
    LOCAL g_local IS KERBIN_MU / (rad_local * rad_local).
    LOCAL max_twr IS 0.
    IF (SHIP:MASS > 0) AND (g_local > 0) {
        SET max_twr TO SHIP:AVAILABLETHRUST / (SHIP:MASS * g_local).
    }

    LOCAL target_th IS 1.0.

    // 3. Max Q Governor: Smoothly throttle back if dynamic pressure exceeds 20 kPa
    IF q_kpa > 20.0 {
        LOCAL q_excess IS (q_kpa - 20.0) / (TARGET_MAX_Q_KPA - 20.0).
        SET target_th TO 1.0 - (q_excess * 0.50). // Taper down to ~50%
    }

    // 4. TWR Safety Floor: Ensure we never drop below MIN_TWR_FLOOR to avoid gravity stall
    IF max_twr > 0 {
        LOCAL min_th_for_twr IS MIN_TWR_FLOOR / max_twr.
        SET target_th TO MAX(target_th, min_th_for_twr).
    }

    // 5. G-Force Safety Ceiling: Throttle back as propellant burns off and vessel gets light
    IF max_twr > 0 {
        LOCAL max_th_for_g IS MAX_G_CEILING / max_twr.
        SET target_th TO MIN(target_th, max_th_for_g).
    }

    // Clamp throttle within physical engine limits (25% to 100%)
    RETURN MIN(1.0, MAX(0.25, target_th)).
}

// ----------------------------------------------------------------------------
// Phase 1: Pre-Launch Countdown & Ignition Sequence
// ----------------------------------------------------------------------------
PRINT "Initiating terminal countdown sequence...".
SAS OFF.
LOCK THROTTLE TO 1.0.
LOCK STEERING TO HEADING(HEADING_DEG, 90.0).

FROM {LOCAL countdown IS 3.} UNTIL countdown = 0 STEP {SET countdown TO countdown - 1.} DO {
    PRINT "T-" + countdown + "...".
    WAIT 1.
}

PRINT "==================================================".
PRINT "T+0.0s: LIFTOFF! Core Engine & Boosters Ignited!".
PRINT "==================================================".

// Release launch clamps / umbilicals and ignite propulsion
UNTIL SHIP:MAXTHRUST > 0 {
    STAGE.
    WAIT 0.5.
}

// ----------------------------------------------------------------------------
// Phase 2: Booster Burn & Staging (2x Shrimp SRB - Full Propellant Burn)
// ----------------------------------------------------------------------------
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 0 + Stage 1 climbing vertically...".
LOCAL initial_thrust IS SHIP:MAXTHRUST.

// Wait for full solid booster burnout via resource depletion (180 SolidFuel -> 0)
WAIT UNTIL (SHIP:SOLIDFUEL < 1.0) OR (SHIP:MAXTHRUST < (initial_thrust * 0.70)).
WAIT 0.5. // Allow chamber pressure to decay completely before release
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Booster burnout! Decoupling 2x Shrimp SRBs...".
STAGE. // Jettison radial solid boosters
WAIT 1.0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Radial boosters separated cleanly.".

// ----------------------------------------------------------------------------
// Phase 3: Pitch Kick & Guided Atmospheric Ascent (Heading 90º)
// ----------------------------------------------------------------------------
IF SHIP:ALTITUDE < ALT_KICK {
    PRINT "Climbing to pitch-kick altitude (" + ALT_KICK + " m)...".
    WAIT UNTIL SHIP:ALTITUDE >= ALT_KICK.
}

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: EXECUTING PITCH KICK TO " + PITCH_INITIAL + "º (HDG " + HEADING_DEG + "º)!".
LOCK targetPitch TO MAX(MIN_PITCH, PITCH_INITIAL - ((SHIP:ALTITUDE - ALT_KICK) / (ALT_END_TURN - ALT_KICK)) * (PITCH_INITIAL - MIN_PITCH)).
LOCK STEERING TO HEADING(HEADING_DEG, targetPitch).

// Activate Real-time Dynamic Atmospheric Throttle Governor (Max Q & TWR Protection)
LOCK THROTTLE TO calculate_atmo_throttle().
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [GOVERNOR] Active Dynamic Throttle Engaged (Max Q: " + TARGET_MAX_Q_KPA + " kPa, Min TWR: " + MIN_TWR_FLOOR + ")".

// ----------------------------------------------------------------------------
// Phase 4: Stage 1 MECO & Upper Stage (Belle-RLX81) Ignition
// ----------------------------------------------------------------------------
// Monitor ascent telemetry while waiting for core liquid fuel depletion or engine flameout
LOCAL last_telemetry_print IS MISSIONTIME.
UNTIL (STAGE:LIQUIDFUEL < 0.5) OR (SHIP:MAXTHRUST < 10.0) {
    IF (MISSIONTIME - last_telemetry_print) >= 5.0 {
        LOCAL q_curr IS ROUND(SHIP:DYNAMICPRESSURE * CONSTANT:ATMTOKPA, 1).
        LOCAL rad_c IS KERBIN_RADIUS + SHIP:ALTITUDE.
        LOCAL g_c IS KERBIN_MU / (rad_c * rad_c).
        LOCAL cur_twr IS ROUND(SHIP:THRUST / MAX(0.001, (SHIP:MASS * g_c)), 2).
        PRINT "T+" + ROUND(MISSIONTIME, 0) + "s | Alt: " + ROUND(SHIP:ALTITUDE/1000, 1) + "km | Q: " + q_curr + "kPa | TWR: " + cur_twr + " | Throttle: " + ROUND(THROTTLE * 100, 0) + "%".
        SET last_telemetry_print TO MISSIONTIME.
    }
    WAIT 0.2.
}
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 1 Core MECO (Main Engine Cutoff)!".
LOCK THROTTLE TO 0.0.
WAIT 1.0.

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Decoupling Stage 1 Booster Core...".
STAGE. // Separate core stage via interstage
WAIT 1.5.

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: IGNITION STAGE 2 (Belle-RLX81 Upper Stage)!".
LOCK THROTTLE TO 1.0.
STAGE. // Ignite XLR81 / Belle-RLX81
WAIT 1.0.

// ----------------------------------------------------------------------------
// Phase 5: Fairing Jettison & Apoapsis Acquisition (Target: 300 km)
// ----------------------------------------------------------------------------
LOCAL fairing_done IS FALSE.
LOCAL engine_failed IS FALSE.

// Upper stage burns along prograde / shallow ascent until Apoapsis reaches 300 km
PRINT "Pushing Apoapsis to target altitude (300 km)...".
LOCK STEERING TO PROGRADE.

// Active loop pushing Ap and checking fairing release altitude deterministically
UNTIL SHIP:APOAPSIS >= (TARGET_APOAPSIS - 5000) {
    IF (SHIP:ALTITUDE > 55000) AND (NOT fairing_done) {
        jettison_fairings().
        SET fairing_done TO TRUE.
    }
    // Fail-safe check for engine breakdown / flameout
    IF (SHIP:MAXTHRUST < 1.0) AND (STAGE:LIQUIDFUEL > 5.0) {
        PRINT "--------------------------------------------------".
        PRINT "[EMERGENCY] Upper stage engine flameout/breakdown detected!".
        PRINT "Current Apoapsis: " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km".
        PRINT "Deploying solar arrays and communications bus immediately...".
        deploy_satellite_systems().
        SET engine_failed TO TRUE.
        BREAK.
    }
    WAIT 0.2.
}

IF engine_failed {
    PRINT "Aborting circularization due to engine breakdown.".
    PRINT "Vessel on suborbital ballistic trajectory (Ap " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km).".
    UNLOCK STEERING.
    UNLOCK THROTTLE.
    SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
} ELSE {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Approaching target Apogee (295 km). Throttling down to 25%...".
    LOCK THROTTLE TO 0.25.

    WAIT UNTIL SHIP:APOAPSIS >= TARGET_APOAPSIS.
    LOCK THROTTLE TO 0.0.
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SECO-1 (First Upper Stage Cutoff)!".
    PRINT "Current Apoapsis: " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km".
    PRINT "Current Periapsis: " + ROUND(SHIP:PERIAPSIS / 1000, 2) + " km".
    PRINT "==================================================".

    // ----------------------------------------------------------------------------
    // Phase 6: Exospheric Coast to Apoapsis
    // ----------------------------------------------------------------------------
    PRINT "Coasting through exosphere to Apoapsis...".
    LOCK STEERING TO PROGRADE.

    IF NOT fairing_done {
        WAIT UNTIL SHIP:ALTITUDE > 70000.
        jettison_fairings().
        SET fairing_done TO TRUE.
    }

    // ----------------------------------------------------------------------------
    // Phase 7: Symmetric Circularization Burn Calculation & Execution
    // ----------------------------------------------------------------------------
    LOCAL rad_target IS KERBIN_RADIUS + TARGET_APOAPSIS.
    LOCAL v_circ IS SQRT(KERBIN_MU / rad_target).

    LOCAL sma_trans IS (SHIP:PERIAPSIS + SHIP:APOAPSIS + 2 * KERBIN_RADIUS) / 2.
    LOCAL v_apo_pred IS SQRT(KERBIN_MU * (2 / (KERBIN_RADIUS + SHIP:APOAPSIS) - 1 / sma_trans)).
    LOCAL delta_v_circ IS MAX(10.0, v_circ - v_apo_pred).

    LOCAL engine_thrust IS MAX(1.0, SHIP:MAXTHRUST).
    LOCAL burn_duration IS (delta_v_circ * SHIP:MASS) / engine_thrust.
    LOCAL half_burn IS burn_duration / 2.

    PRINT "--------------------------------------------------".
    PRINT "CIRCULARIZATION BURN PARAMETERS:".
    PRINT "  Target Circular Speed: " + ROUND(v_circ, 1) + " m/s".
    PRINT "  Predicted Speed at Ap: " + ROUND(v_apo_pred, 1) + " m/s".
    PRINT "  Required Delta-v:      " + ROUND(delta_v_circ, 1) + " m/s".
    PRINT "  Estimated Burn Time:   " + ROUND(burn_duration, 1) + " s".
    PRINT "  Ignition Point:        T_Ap - " + ROUND(half_burn, 1) + " s".
    PRINT "--------------------------------------------------".

    WAIT UNTIL (ETA:APOAPSIS <= (half_burn + 5.0)) OR (ETA:APOAPSIS > (SHIP:ORBIT:PERIOD - 60)).
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Aligning strictly with Orbital Prograde...".
    LOCK STEERING TO PROGRADE.

    WAIT UNTIL (ETA:APOAPSIS <= half_burn) OR (ETA:APOAPSIS > (SHIP:ORBIT:PERIOD - 30)).
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: IGNITION SECO-2 (Circularization Burn)!".
    PRINT "==================================================".
    LOCK THROTTLE TO 1.0.

    WAIT UNTIL (SHIP:PERIAPSIS >= 275000) OR ((SHIP:APOAPSIS - SHIP:PERIAPSIS) < 15000).
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Periapsis approaching target. Precision throttle at 15%...".
    LOCK THROTTLE TO 0.15.

    WAIT UNTIL (SHIP:PERIAPSIS >= (TARGET_PERIAPSIS - 300)) OR ((SHIP:APOAPSIS - SHIP:PERIAPSIS) < 300) OR (ETA:PERIAPSIS < ETA:APOAPSIS).
    LOCK THROTTLE TO 0.0.
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SECO-2 CUTOFF! CIRCULAR ORBIT ACHIEVED!".
    PRINT "==================================================".

    // ----------------------------------------------------------------------------
    // Phase 8: Final Orbital Assessment & Payload Release
    // ----------------------------------------------------------------------------
    WAIT 3.0.
    LOCAL final_ecc IS SHIP:ORBIT:ECCENTRICITY.
    LOCAL final_period IS SHIP:ORBIT:PERIOD.

    PRINT "FINAL ORBITAL TELEMETRY:".
    PRINT "  Apoapsis:     " + ROUND(SHIP:APOAPSIS / 1000, 3) + " km".
    PRINT "  Periapsis:    " + ROUND(SHIP:PERIAPSIS / 1000, 3) + " km".
    PRINT "  Eccentricity: " + ROUND(final_ecc, 5).
    PRINT "  Period:       " + ROUND(final_period / 60, 2) + " min (" + ROUND(final_period, 1) + " s)".
    PRINT "  Inclination:  " + ROUND(SHIP:ORBIT:INCLINATION, 3) + "º".
    PRINT "--------------------------------------------------".

    WAIT 5.0.
    deploy_satellite_systems().
    WAIT 3.0.
    separate_payload().

    PRINT "==================================================".
    PRINT "      MISSION CSA-12: COROLTSAT-1B DEPLOYED!      ".
    PRINT "       KERBIN COMMS CONSTELLATION IS ACTIVE!      ".
    PRINT "==================================================".

    UNLOCK STEERING.
    UNLOCK THROTTLE.
    SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
}
