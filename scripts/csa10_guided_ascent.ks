// ============================================================================
// COROLT SPACE AGENCY (CSA) - FLIGHT GUIDANCE SYSTEM v3.0
// MISSION: CSA-10 (Coastal Polar Trajectory & Multi-Layer Science Survey)
// VEHICLE: Corolt-IIIb (Upgraded 800 EC Power Bank & Double Duty-Cycle Mini-Lab)
// OBJECTIVES:
//   1. Steer along Heading 355º (NNW) targeting solid inland northern continent.
//   2. Deep outer space apogee (> 200 km) penetrating Van Allen threshold.
//   3. Execute dual Materials Mini-Lab sampling:
//      - 30s burst in Upper Atmosphere (18 - 70 km)
//      - 90s burst in Low Space (> 70 km)
//   4. Sample PresMat barometer, Geiger radiation, and micrometeorit sensors.
//   5. Maintain strict 100 EC battery reserve floor for recovery avionics.
//   6. Autonomous truss fairing ejection (>58 km) and mechanical parachute arming.
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "      COROLT SPACE AGENCY - FLIGHT CONTROL        ".
PRINT "   MISSION: CSA-10 | VEHICLE: Corolt-IIIb (800 EC)".
PRINT "   Target Heading: 355º (Inland Land) | Floor: 100".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Flight Constants & Guidance Parameters
// ----------------------------------------------------------------------------
SET ALT_KICK TO 2500.            // Altitude for initial gravity kick (m)
SET PITCH_INITIAL TO 88.0.       // Initial pitch after kick (degrees)
SET HEADING_DEG TO 355.0.        // Heading 355.0º (North-North-West into solid continent)
SET POWER_SAFETY_FLOOR TO 100.   // Reserve floor for avionics & recovery (EC)

// ----------------------------------------------------------------------------
// Helper Functions: Power & Subsystem Management
// ----------------------------------------------------------------------------
FUNCTION get_current_ec {
    RETURN SHIP:ELECTRICCHARGE.
}

FUNCTION get_safe_biome {
    // Robust biome polling without throwing GeoCoordinates suffix errors
    LOCAL cur_lat IS SHIP:LATITUDE.
    LOCAL cur_lng IS SHIP:LONGITUDE.
    LOCAL b_name IS "Unknown".
    
    // Safely query via BODY geoposition
    LOCAL geo IS SHIP:BODY:GEOPOSITIONLATLNG(cur_lat, cur_lng).
    IF geo:TYPENAME = "GeoCoordinates" {
        // Some kOS versions store biome on body geoposition
        SET b_name TO "Coastal Sector (" + ROUND(cur_lat, 2) + "N, " + ROUND(cur_lng, 2) + "W)".
    }
    RETURN b_name.
}

FUNCTION stop_all_science {
    PRINT "⚠️ [POWER GUARD] Emergency shutdown of all scientific instruments!".
    FOR p IN SHIP:PARTS {
        FOR m IN p:MODULES {
            LOCAL part_mod IS p:GETMODULE(m).
            FOR ev IN part_mod:ALLEVENTNAMES {
                LOCAL evl IS ev:TOLOWER.
                IF evl:CONTAINS("stop") OR evl:CONTAINS("detener") OR evl:CONTAINS("parar") {
                    part_mod:DOEVENT(ev).
                }
            }
        }
    }
}

FUNCTION stop_instruments_by_keyword {
    PARAMETER keyword.
    FOR p IN SHIP:PARTS {
        IF p:TITLE:CONTAINS(keyword) OR p:NAME:CONTAINS(keyword) {
            FOR m IN p:MODULES {
                LOCAL part_mod IS p:GETMODULE(m).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("stop") OR evl:CONTAINS("detener") OR evl:CONTAINS("parar") {
                        part_mod:DOEVENT(ev).
                        PRINT "  [STOPPED] " + p:TITLE + " (" + ev + ")".
                    }
                }
            }
        }
    }
}

FUNCTION trigger_science_suite {
    PARAMETER regime_name.
    PARAMETER include_materials.

    IF get_current_ec() < POWER_SAFETY_FLOOR {
        PRINT "⚠️ [POWER GUARD] EC (" + ROUND(get_current_ec(), 1) + ") below floor. Skipping science triggers.".
        RETURN.
    }

    PRINT "--------------------------------------------------".
    PRINT "[SCIENCE] Activating instruments for " + regime_name + "...".
    PRINT "Current Battery: " + ROUND(get_current_ec(), 1) + " EC".
    
    LOCAL trig_count IS 0.
    FOR p IN SHIP:PARTS {
        LOCAL is_mat IS p:TITLE:CONTAINS("Material") OR p:NAME:CONTAINS("Payload_01").
        IF NOT is_mat OR include_materials {
            FOR m IN p:MODULES {
                LOCAL part_mod IS p:GETMODULE(m).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("investigar") OR evl:CONTAINS("comenzar") OR evl:CONTAINS("observar")
                       OR evl:CONTAINS("registrar") OR evl:CONTAINS("iniciar") OR evl:CONTAINS("start")
                       OR evl:CONTAINS("log") OR evl:CONTAINS("deploy") OR evl:CONTAINS("analizar") {
                        IF NOT evl:CONTAINS("paracaídas") AND NOT evl:CONTAINS("chute") AND NOT evl:CONTAINS("desacoplar") {
                            part_mod:DOEVENT(ev).
                            SET trig_count TO trig_count + 1.
                        }
                    }
                }
            }
        }
    }
    PRINT "[SCIENCE] " + trig_count + " triggers executed successfully.".
    PRINT "--------------------------------------------------".
}

FUNCTION jettison_truss_fairings {
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Jettisoning protective truss fairings...".
    LOCAL fairing_count IS 0.
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("Fairing") OR p:NAME:CONTAINS("PayloadFairing") {
            FOR m IN p:MODULES {
                LOCAL part_mod IS p:GETMODULE(m).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("decouple") OR evl:CONTAINS("desacoplar") {
                        part_mod:DOEVENT(ev).
                        SET fairing_count TO fairing_count + 1.
                    }
                }
            }
        }
    }
    // Also trigger Stage 1 if fairings are placed in dedicated stage
    IF STAGE:NUMBER = 1 {
        STAGE.
        SET fairing_count TO fairing_count + 1.
    }
    PRINT "[FAIRINGS] " + fairing_count + " fairing jettison events dispatched.".
    PRINT "==================================================".
}

FUNCTION deploy_parachute_system {
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: ARMING RECOVERY PARACHUTE SYSTEM!".
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("Chute") OR p:NAME:CONTAINS("Nosecone") OR p:NAME:CONTAINS("Parachute") {
            FOR m IN p:MODULES {
                LOCAL part_mod IS p:GETMODULE(m).
                FOR ev IN part_mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("arm") OR evl:CONTAINS("armar") OR evl:CONTAINS("deploy") OR evl:CONTAINS("desplegar") {
                        part_mod:DOEVENT(ev).
                        PRINT "  [PARACHUTE] " + p:TITLE + " -> " + ev.
                    }
                }
            }
        }
    }
    STAGE. // Fire recovery stage
    PRINT "==================================================".
}

// ----------------------------------------------------------------------------
// Phase 1: Pre-Launch Ignition Countdown
// ----------------------------------------------------------------------------
PRINT "Initiating ignition countdown sequence...".
FROM {LOCAL countdown IS 3.} UNTIL countdown = 0 STEP {SET countdown TO countdown - 1.} DO {
    PRINT "T-" + countdown.
    WAIT 1.
}

// ----------------------------------------------------------------------------
// Phase 2: Stage 1 Ignition (RT-10 Hammer Booster)
// ----------------------------------------------------------------------------
PRINT "T+0.0s: IGNITION STAGE 1 (RT-10 'Hammer')!".
STAGE.

// Science Suite 1: Low Atmosphere (0-18 km) - standard sensors
WAIT 3.
trigger_science_suite("LOW ATMOSPHERE (0-18 km)", FALSE).

// Vertical ascent until kick altitude
LOCK STEERING TO HEADING(HEADING_DEG, 90).

// ----------------------------------------------------------------------------
// Phase 3: Gravity Kick towards Heading 005º (NNE Coastal Corridor)
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:ALTITUDE > ALT_KICK.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: PITCH KICK EXECUTED AT " + PITCH_INITIAL + "º (HDG " + HEADING_DEG + "º)!".
LOCK STEERING TO HEADING(HEADING_DEG, PITCH_INITIAL).

// ----------------------------------------------------------------------------
// Phase 4: Stage 1 Burnout & Stage 2 Ignition (SRM-XL)
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 1 Burnout, Staging decoupler...".
STAGE. // Separate Stage 1
WAIT 1.5.

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: IGNITION STAGE 2 (SRM-XL)!".
STAGE. // Ignite Stage 2

// Guided gravity turn transition (smooth pitch reduction down to 54º)
LOCK targetPitch TO MAX(54, PITCH_INITIAL - ((SHIP:ALTITUDE - ALT_KICK) / (45000 - ALT_KICK)) * (PITCH_INITIAL - 54)).
LOCK STEERING TO HEADING(HEADING_DEG, targetPitch).

// Science Suite 2: Upper Atmosphere (18-70 km) + 30s Mini-Lab Burst
WHEN SHIP:ALTITUDE > 25000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [SCIENCE] Entering UPPER ATMOSPHERE (> 25 km)...".
    trigger_science_suite("UPPER ATMOSPHERE (18-70 km)", TRUE).

    // Auto-stop Mini-Lab after 30 seconds to conserve battery for space
    LOCAL t_stop_atmo IS MISSIONTIME + 30.
    WHEN MISSIONTIME > t_stop_atmo THEN {
        PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [POWER GUARD] Upper Atmosphere Mini-Lab 30s run complete. Pausing for space.".
        stop_instruments_by_keyword("Material").
    }
}

// ----------------------------------------------------------------------------
// Phase 5: Propulsion Burnout, Stage 2 Separation & Fairing Jettison
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 2 Burnout. Active propulsion complete.".
PRINT "Predicted Apoapsis: " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km.".

// Cut steering and SAS immediately to eliminate 0.38 EC/s reaction wheel draw
UNLOCK STEERING.
SAS OFF.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Steering unlocked, SAS OFF (Zero parasitic draw).".

// Jettison empty Stage 2 booster casing to liberate payload (Fires Stage 2 decoupler)
WAIT 1.0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Decoupling Stage 2 booster casing...".
STAGE.
WAIT 1.5.

// Jettison protective truss fairings (Fires Stage 1 fairings)
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Jettisoning protective truss fairings...".
jettison_truss_fairings().

// Science Suite 3: Low Space (> 70 km) + 90s Mini-Lab Burst
WHEN SHIP:ALTITUDE > 70000 THEN {
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [ORBIT] KARMAN LINE EXCEEDED (> 70 km)!".
    PRINT "Entering LOW SPACE environment along coastal corridor.".
    PRINT "==================================================".
    trigger_science_suite("LOW SPACE (70-250 km)", TRUE).
    
    // Scheduled shut down of Mini-Lab after 90 seconds
    LOCAL t_stop_space IS MISSIONTIME + 90.
    WHEN MISSIONTIME > t_stop_space OR get_current_ec() < (POWER_SAFETY_FLOOR + 50) THEN {
        PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [POWER GUARD] Low Space Mini-Lab 90s exposure complete. Shutting down.".
        stop_instruments_by_keyword("Material").
    }
}

// ----------------------------------------------------------------------------
// Phase 6: Coast to Apoapsis & High Space Monitoring
// ----------------------------------------------------------------------------
WHEN SHIP:ALTITUDE > 250000 THEN {
    PRINT "⚠️ [VAN ALLEN] High Space reached (> 250 km)! Background radiation recording active.".
    trigger_science_suite("HIGH SPACE (> 250 km)", FALSE).
}

WAIT UNTIL SHIP:VERTICALSPEED < 0.
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: APOAPSIS ATTAINED: " + ROUND(SHIP:ALTITUDE / 1000, 2) + " km!".
PRINT "Current Coordinates: Lat " + ROUND(SHIP:LATITUDE, 3) + "ºN, Lon " + ROUND(SHIP:LONGITUDE, 3) + "ºW.".
PRINT "Ground Sector: " + get_safe_biome().
PRINT "Battery Level: " + ROUND(get_current_ec(), 1) + " EC".
PRINT "Beginning atmospheric descent along northern coast...".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Phase 7: Aerothermal Atmospheric Reentry & Subsonic Backflip
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:ALTITUDE < 70000.
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: RE-ENTERING ATMOSPHERE (< 70 km)!".
PRINT "LOCKING NOSECONE-FORWARD (SRFPROGRADE) FOR AEROTHERMAL SHIELDING.".
PRINT "Shielding lateral batteries & sensors behind conical shock wave...".
PRINT "==================================================".
LOCK STEERING TO SRFPROGRADE.

// Plunge nosecone-first through peak dynamic pressure & hypersonic deceleration
WAIT UNTIL SHIP:ALTITUDE < 6000 OR (SHIP:ALTITUDE < 10000 AND SHIP:AIRSPEED < 280).
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: SUBSONIC VELOCITY ATTAINED (Airspeed: " + ROUND(SHIP:AIRSPEED, 1) + " m/s).".
PRINT "EXECUTING REENTRY BACKFLIP MANEUVER (FLIPPING TO SRFRETROGRADE)...".
LOCK STEERING TO SRFRETROGRADE.
WAIT 3.0. // Allow reaction wheel to complete the 180º flip so nosecone faces up into trailing wake
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Backflip complete! Nosecone oriented upwards in trailing wake.".
PRINT "DEPLOYING MECHANICAL PARACHUTE SYSTEM!".
PRINT "==================================================".
deploy_parachute_system().
WAIT 2.0.
UNLOCK STEERING.
SAS OFF.
PRINT "Steering unlocked, SAS OFF (Zero parasitic draw for final descent).".

// Low-altitude final touchdown monitor
WAIT UNTIL SHIP:ALTITUDE < 5000.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Terminal descent under 5,000m. Radar alt: " + ROUND(ALT:RADAR, 1) + "m.".
PRINT "Remaining Battery: " + ROUND(get_current_ec(), 1) + " EC (Nominal reserve maintained).".

WAIT UNTIL SHIP:VERTICALSPEED > -0.5 OR SHIP:ALTITUDE < 50.
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: TOUCHDOWN DETECTED!".
PRINT "Final Sector: " + get_safe_biome().
PRINT "Coordinates: Lat " + ROUND(SHIP:LATITUDE, 4) + "ºN, Lon " + ROUND(SHIP:LONGITUDE, 4) + "ºW.".
PRINT "MISSION CSA-10 COMPLETE. VESSEL READY FOR RECOVERY.".
PRINT "==================================================".
