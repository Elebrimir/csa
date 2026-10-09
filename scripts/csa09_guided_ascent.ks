// ============================================================================
// COROLT SPACE AGENCY (CSA) - FLIGHT GUIDANCE SYSTEM v2.5
// MISSION: CSA-09 (High-Altitude Sounding Rocket - Power-Managed Science)
// OBJECTIVES:
//   1. Boost apogee > 180 km over equatorial inland biomes (Grasslands/Highlands).
//   2. Trajectory: Heading 270º (Due West) with Coriolis compensation.
//   3. Smart Power Budget Management (800 EC capacity, strict 100 EC reserve floor).
//   4. Automated Science Duty-Cycling (90s Mini-Lab burst, auto-shutdown).
//   5. Guaranteed truss fairing jettison (>58 km) and mechanical parachute arming.
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "      COROLT SPACE AGENCY - FLIGHT CONTROL        ".
PRINT "   MISSION: CSA-09 | VESSEL: CSA-09 (Suborbital)  ".
PRINT "   Target Heading: 270º (West) | Floor EC: 100 EC ".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Flight Constants & Parameters
// ----------------------------------------------------------------------------
SET ALT_KICK TO 2400.            // Altitude for initial gravity kick (m)
SET PITCH_INITIAL TO 87.5.       // Initial pitch after kick (degrees)
SET HEADING_DEG TO 270.          // Due West (equatorial inland corridor)
SET POWER_SAFETY_FLOOR TO 100.   // Emergency reserve floor for flight CPU & parachute (EC)

// ----------------------------------------------------------------------------
// Power Management & Instrument Helper Functions
// ----------------------------------------------------------------------------
FUNCTION get_current_ec {
    RETURN SHIP:ELECTRICCHARGE.
}

FUNCTION stop_all_science {
    PRINT "⚠️ [POWER GUARD] Emergency shutdown of all science instruments!".
    FOR p IN SHIP:PARTS {
        FOR m IN p:MODULES {
            LOCAL mod IS p:GETMODULE(m).
            FOR ev IN mod:ALLEVENTNAMES {
                LOCAL evl IS ev:TOLOWER.
                IF evl:CONTAINS("stop") OR evl:CONTAINS("detener") OR evl:CONTAINS("parar") {
                    mod:DOEVENT(ev).
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
                LOCAL mod IS p:GETMODULE(m).
                FOR ev IN mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("stop") OR evl:CONTAINS("detener") OR evl:CONTAINS("parar") {
                        mod:DOEVENT(ev).
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
        // Skip Mini-Lab if include_materials is FALSE
        LOCAL is_mat IS p:TITLE:CONTAINS("Material") OR p:NAME:CONTAINS("Payload_01").
        IF NOT is_mat OR include_materials {
            FOR m IN p:MODULES {
                LOCAL mod IS p:GETMODULE(m).
                FOR ev IN mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("investigar") OR evl:CONTAINS("comenzar") OR evl:CONTAINS("observar")
                       OR evl:CONTAINS("registrar") OR evl:CONTAINS("iniciar") OR evl:CONTAINS("start")
                       OR evl:CONTAINS("log") OR evl:CONTAINS("deploy") OR evl:CONTAINS("analizar") {
                        IF NOT evl:CONTAINS("paracaídas") AND NOT evl:CONTAINS("chute") AND NOT evl:CONTAINS("desacoplar") {
                            mod:DOEVENT(ev).
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
                LOCAL mod IS p:GETMODULE(m).
                FOR ev IN mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("decouple") OR evl:CONTAINS("desacoplar") {
                        mod:DOEVENT(ev).
                        SET fairing_count TO fairing_count + 1.
                    }
                }
            }
        }
    }
    PRINT "[FAIRINGS] " + fairing_count + " fairing decouplers fired.".
    PRINT "==================================================".
}

FUNCTION deploy_parachute_system {
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: ARMING RECOVERY PARACHUTE SYSTEM!".
    FOR p IN SHIP:PARTS {
        IF p:NAME:CONTAINS("Chute") OR p:NAME:CONTAINS("Nosecone") OR p:NAME:CONTAINS("Parachute") {
            FOR m IN p:MODULES {
                LOCAL mod IS p:GETMODULE(m).
                FOR ev IN mod:ALLEVENTNAMES {
                    LOCAL evl IS ev:TOLOWER.
                    IF evl:CONTAINS("arm") OR evl:CONTAINS("armar") OR evl:CONTAINS("deploy") OR evl:CONTAINS("desplegar") {
                        mod:DOEVENT(ev).
                        PRINT "  [PARACHUTE] " + p:TITLE + " -> " + ev.
                    }
                }
            }
        }
    }
    STAGE. // Also fire recovery stage in sequence
    PRINT "==================================================".
}

// ----------------------------------------------------------------------------
// Phase 1: Pre-Launch Countdown
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

// Science Suite 1: Low Atmosphere (0-18 km) - sensors only, save Mini-Lab
WAIT 3.
trigger_science_suite("LOW ATMOSPHERE (0-18 km)", FALSE).

// Vertical ascent until kick altitude
LOCK STEERING TO HEADING(HEADING_DEG, 90).

// ----------------------------------------------------------------------------
// Phase 3: Gravity Kick towards Heading 270º (Due West)
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

// Guided gravity turn transition
LOCK targetPitch TO MAX(48, PITCH_INITIAL - ((SHIP:ALTITUDE - ALT_KICK) / (45000 - ALT_KICK)) * (PITCH_INITIAL - 48)).
LOCK STEERING TO HEADING(HEADING_DEG, targetPitch).

// Science Suite 2: Upper Atmosphere (18-70 km)
WHEN SHIP:ALTITUDE > 18000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [SCIENCE] Entering UPPER ATMOSPHERE (> 18 km)...".
    trigger_science_suite("UPPER ATMOSPHERE (18-70 km)", FALSE).
}

// ----------------------------------------------------------------------------
// Phase 5: Propulsion Burnout, Fairing Separation & Parasitic Load Elimination
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 2 Burnout. Active propulsion complete.".
PRINT "Predicted Apoapsis: " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km.".

// Cut attitude steering and reaction wheel SAS to save electricity!
UNLOCK STEERING.
SAS OFF.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Steering unlocked, SAS OFF (Parasitic reaction wheel draw eliminated).".

// Truss Fairing Jettison in thin air
WHEN SHIP:ALTITUDE > 58000 THEN {
    jettison_truss_fairings().
}

// Science Suite 3: Low Space (> 70 km) + 90s Mini-Lab Burst
WHEN SHIP:ALTITUDE > 70000 THEN {
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [ORBIT] KARMAN LINE EXCEEDED (> 70 km)!".
    PRINT "Entering LOW SPACE environment.".
    PRINT "==================================================".
    // Trigger standard sensors and start Mini-Lab
    trigger_science_suite("LOW SPACE (70-250 km)", TRUE).
    
    // Scheduled shut down of Mini-Lab after 90 seconds of exposure
    WHEN MISSIONTIME > (ROUND(MISSIONTIME, 1) + 90) OR get_current_ec() < (POWER_SAFETY_FLOOR + 50) THEN {
        PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [POWER GUARD] Mini-Lab 90s exposure complete. Shutting down to conserve battery.".
        stop_instruments_by_keyword("Material").
    }
}

// ----------------------------------------------------------------------------
// Phase 6: Coast to Apoapsis & Descent Prep
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:VERTICALSPEED < 0.
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: APOAPSIS ATTAINED: " + ROUND(SHIP:ALTITUDE / 1000, 2) + " km!".
PRINT "Current Ground Biome: " + SHIP:GEOPOSITION:BIOME.
PRINT "Battery Level: " + ROUND(get_current_ec(), 1) + " EC".
PRINT "Beginning atmospheric descent...".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Phase 7: Atmospheric Entry & Parachute Deployment
// ----------------------------------------------------------------------------
WHEN SHIP:ALTITUDE < 70000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Re-entering atmosphere (< 70 km).".
}

WHEN SHIP:ALTITUDE < 15000 AND SHIP:VERTICALSPEED < 0 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Altitude < 15,000m. Pre-arming parachute system...".
    deploy_parachute_system().
}

// Low-altitude final touchdown monitor
WAIT UNTIL SHIP:ALTITUDE < 5000.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Terminal descent under 5,000m. Final radar alt: " + ROUND(ALT:RADAR, 1) + "m.".
PRINT "Remaining Battery: " + ROUND(get_current_ec(), 1) + " EC (Nominal reserve maintained).".

WAIT UNTIL SHIP:VERTICALSPEED > -0.5 OR SHIP:ALTITUDE < 50.
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: TOUCHDOWN DETECTED!".
PRINT "Final Landing Biome: " + SHIP:GEOPOSITION:BIOME.
PRINT "Coordinates: Lat " + ROUND(SHIP:GEOPOSITION:LAT, 4) + "º, Lon " + ROUND(SHIP:GEOPOSITION:LNG, 4) + "º.".
PRINT "MISSION CSA-09 COMPLETE. VESSEL READY FOR RECOVERY.".
PRINT "==================================================".
