// ============================================================================
// COROLT SPACE AGENCY (CSA) - FLIGHT GUIDANCE SYSTEM v4.0
// MISSION: CSA-11 (Kerbin Comms Constellation Anchor - CoroltSat-1A)
// VEHICLE: Corolt-IV B (Etoh-140-TU Core + 2x Shrimp SRB + Belle-RLX81 Upper Stage)
// PAYLOAD: CoroltSat-1A (248 kg, 0.625m Payload Truss, Stayputnik, Codac-A23 1Mm)
// OBJECTIVES:
//   1. Autonomous liftoff and umbilical tower clearance.
//   2. Dual solid booster jettison upon burnout (T+11s).
//   3. Pitch-kick at 1,200m towards Heading 90.0º (Equatorial East).
//   4. Stage 1 core MECO and interstage separation at ~48 km.
//   5. Belle-RLX81 upper stage ignition and fairing jettison (> 55 km).
//   6. Apoapsis insertion at 300.0 km (SECO-1).
//   7. Exospheric coast to apogee with active prograde attitude lock.
//   8. Symmetric circularization burn (SECO-2) targeting e < 0.002 (300x300 km).
//   9. Autonomous payload separation and constellation deployment.
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "      COROLT SPACE AGENCY - MISSION CONTROL       ".
PRINT "   MISSION: CSA-11 | CoroltSat-1A (Constellation) ".
PRINT "   VEHICLE: Corolt-IV B | TARGET ORBIT: 300x300 km".
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

// ----------------------------------------------------------------------------
// Subsystem Helper Functions
// ----------------------------------------------------------------------------
FUNCTION jettison_fairings {
    PRINT "--------------------------------------------------".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Jettisoning payload fairings (> 55 km)...".
    LOCAL fairing_jettisoned IS FALSE.
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("Fairing") OR p:NAME:CONTAINS("Juno4") {
            FOR m IN p:MODULES {
                LOCAL part_mod IS p:GETMODULE(m).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("deploy") OR evl:CONTAINS("jettison") OR evl:CONTAINS("desplegar") OR evl:CONTAINS("soltar") {
                        part_mod:DOEVENT(ev).
                        SET fairing_jettisoned TO TRUE.
                        PRINT "  [FAIRING] Event fired: " + ev + " on " + p:TITLE.
                    }
                }
            }
        }
    }
    RETURN fairing_jettisoned.
}

FUNCTION separate_payload {
    PRINT "--------------------------------------------------".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SEPARATING PAYLOAD (CoroltSat-1A)...".
    LOCAL separated IS FALSE.
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("Decoupler") OR p:NAME:CONTAINS("Adapter") OR p:NAME:CONTAINS("OGO") {
            FOR m IN p:MODULES {
                LOCAL part_mod IS p:GETMODULE(m).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("decouple") OR evl:CONTAINS("desacoplar") OR evl:CONTAINS("separate") {
                        part_mod:DOEVENT(ev).
                        SET separated TO TRUE.
                        PRINT "  [PAYLOAD] Decoupler triggered: " + ev + " on " + p:TITLE.
                    }
                }
            }
        }
    }
    // If no specific decoupler event was matched, fire standard stage
    IF NOT separated {
        PRINT "  [PAYLOAD] Triggering active stage for payload release...".
        STAGE.
    }
    PRINT "==================================================".
}

FUNCTION deploy_satellite_systems {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Deploying communications and solar arrays...".
    AG3 ON. // Trigger Action Group 3 standard
    FOR p IN SHIP:PARTS {
        FOR m IN p:MODULES {
            LOCAL part_mod IS p:GETMODULE(m).
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
UNTIL SHIP:MAXTHRUST > 0 DO {
    STAGE.
    WAIT 0.5.
}

// ----------------------------------------------------------------------------
// Phase 2: Booster Burn & Staging (2x Shrimp SRB)
// ----------------------------------------------------------------------------
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 0 + Stage 1 climbing vertically...".
LOCAL initial_thrust IS SHIP:MAXTHRUST.

// Wait for booster burnout (thrust drop or solid fuel exhaustion)
WAIT UNTIL (SHIP:MAXTHRUST < (initial_thrust * 0.85)) OR (STAGE:SOLIDFUEL < 0.1) OR (MISSIONTIME > 12.0).
WAIT 0.5.
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

// ----------------------------------------------------------------------------
// Phase 4: Stage 1 MECO & Upper Stage (Belle-RLX81) Ignition
// ----------------------------------------------------------------------------
// Wait for core liquid fuel depletion
WAIT UNTIL STAGE:LIQUIDFUEL < 0.5.
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
WHEN (SHIP:ALTITUDE > 55000) AND (NOT fairing_done) THEN {
    jettison_fairings().
    SET fairing_done TO TRUE.
}

// Upper stage burns along prograde / shallow ascent until Apoapsis reaches 300 km
PRINT "Pushing Apoapsis to target altitude (300 km)...".
LOCK STEERING TO PROGRADE.

WAIT UNTIL SHIP:APOAPSIS >= (TARGET_APOAPSIS - 5000).
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

// Ensure fairings are gone if not yet deployed
IF NOT fairing_done {
    WAIT UNTIL SHIP:ALTITUDE > 70000.
    jettison_fairings().
    SET fairing_done TO TRUE.
}

// ----------------------------------------------------------------------------
// Phase 7: Symmetric Circularization Burn Calculation & Execution
// ----------------------------------------------------------------------------
// Calculate exact orbital speed required at 300 km
LOCAL r_target IS KERBIN_RADIUS + TARGET_APOAPSIS.
LOCAL v_circ IS SQRT(KERBIN_MU / r_target).

// Estimate velocity at apoapsis from current orbital energy
LOCAL sma_trans IS (SHIP:PERIAPSIS + SHIP:APOAPSIS + 2 * KERBIN_RADIUS) / 2.
LOCAL v_apo_pred IS SQRT(KERBIN_MU * (2 / (KERBIN_RADIUS + SHIP:APOAPSIS) - 1 / sma_trans)).
LOCAL delta_v_circ IS MAX(10, v_circ - v_apo_pred).

// Estimate burn time with Belle-RLX81 (Thrust ~ 17.2 kN, Isp ~ 272 s)
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

// Wait until approaching ignition window
WAIT UNTIL ETA:APOAPSIS <= (half_burn + 5.0).
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Aligning strictly with Orbital Prograde...".
LOCK STEERING TO PROGRADE.

WAIT UNTIL ETA:APOAPSIS <= half_burn.
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: IGNITION SECO-2 (Circularization Burn)!".
PRINT "==================================================".
LOCK THROTTLE TO 1.0.

// Fine throttling as periapsis approaches target
WAIT UNTIL (SHIP:PERIAPSIS >= 275000) OR (SHIP:PERIAPSIS >= (SHIP:APOAPSIS - 5000)).
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Periapsis approaching target. Precision throttle at 15%...".
LOCK THROTTLE TO 0.15.

// Cutoff condition: Pe within 500m of Ap or Ap reached
WAIT UNTIL (SHIP:PERIAPSIS >= (TARGET_PERIAPSIS - 500)) OR (SHIP:PERIAPSIS >= SHIP:APOAPSIS).
LOCK THROTTLE TO 0.0.
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SECO-2 CUTOFF! CIRCULAR ORBIT ACHIEVED!".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Phase 8: Final Orbital Assessment & Payload Release
// ----------------------------------------------------------------------------
WAIT 3.0.
LOCAL final_ecc IS SHIP:OBT:ECCENTRICITY.
LOCAL final_period IS SHIP:OBT:PERIOD.

PRINT "FINAL ORBITAL TELEMETRY:".
PRINT "  Apoapsis:     " + ROUND(SHIP:APOAPSIS / 1000, 3) + " km".
PRINT "  Periapsis:    " + ROUND(SHIP:PERIAPSIS / 1000, 3) + " km".
PRINT "  Eccentricity: " + ROUND(final_ecc, 5).
PRINT "  Period:       " + ROUND(final_period / 60, 2) + " min (" + ROUND(final_period, 1) + " s)".
PRINT "  Inclination:  " + ROUND(SHIP:OBT:INCLINATION, 3) + "º".
PRINT "--------------------------------------------------".

// Payload Deployment
WAIT 5.0.
separate_payload().
WAIT 2.0.
deploy_satellite_systems().

PRINT "==================================================".
PRINT "      MISSION CSA-11: COROLTSAT-1A DEPLOYED!      ".
PRINT "       KERBIN COMMS CONSTELLATION IS ACTIVE!      ".
PRINT "==================================================".

UNLOCK STEERING.
UNLOCK THROTTLE.
SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
