// ============================================================================
// Corolt Space Agency (CSA) — Guided Ascent & Gravity Turn Flight Plan
// Vehicle: Corolt-III
// ============================================================================

DECLARE PARAMETER PITCH_INITIAL IS 82, ALT_KICK IS 1200, HEADING_DEG IS 90.

CLEARSCREEN.
PRINT "==================================================".
PRINT "        COROLT SPACE AGENCY - FLIGHT OS           ".
PRINT "       Guided Ascent & Gravity Turn Profile       ".
PRINT "==================================================".
PRINT "Configuration:".
PRINT "  - Kick Pitch Angle: " + PITCH_INITIAL + " deg".
PRINT "  - Kick Altitude:    " + ALT_KICK + " m".
PRINT "  - Ascent Heading:   " + HEADING_DEG + " deg (East)".
PRINT "==================================================".

// Function to activate all scientific experiments onboard
FUNCTION activate_experiments {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [SCIENCE] Activating onboard scientific instruments...".
    LOCAL count IS 0.
    FOR p IN SHIP:PARTS {
        FOR m_name IN p:MODULES {
            IF m_name = "Experiment" OR m_name = "ModuleScienceExperiment" {
                LOCAL m_part IS p:GETMODULE(m_name).
                // Actions (Kerbalism StartAction / Start)
                FOR act_name IN m_part:ALLACTIONNAMES {
                    IF act_name:TOLOWER:CONTAINS("start") OR act_name:TOLOWER:CONTAINS("inici") {
                        m_part:DOACTION(act_name, TRUE).
                        SET count TO count + 1.
                    }
                }
                // Events (KSP GUI / Deploy / Observe)
                FOR ev_name IN m_part:ALLEVENTNAMES {
                    IF ev_name:TOLOWER:CONTAINS("start") OR ev_name:TOLOWER:CONTAINS("deploy") OR ev_name:TOLOWER:CONTAINS("inici") OR ev_name:TOLOWER:CONTAINS("observ") {
                        m_part:DOEVENT(ev_name).
                        SET count TO count + 1.
                    }
                }
            }
        }
    }
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [SCIENCE] " + count + " commands sent to sensors!".
}

// 1. Vertical Liftoff
LOCK THROTTLE TO 1.0.
LOCK STEERING TO HEADING(HEADING_DEG, 90).

PRINT "Starting countdown...".
FROM {LOCAL c IS 3.} UNTIL c = 0 STEP {SET c TO c - 1.} DO {
    PRINT "T-" + c.
    WAIT 1.
}

PRINT "T+0.0s: STAGE 1 IGNITION (RT-10 «Hammer»)!".
STAGE.
LOCAL t_liftoff IS TIME:SECONDS.

// Activation of science experiments 3.5 seconds after liftoff
WHEN TIME:SECONDS >= t_liftoff + 3.5 THEN {
    activate_experiments().
}

// 2. Vertical ascent until kick altitude
WAIT UNTIL SHIP:ALTITUDE > ALT_KICK.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: INITIATING PITCH KICK AT " + PITCH_INITIAL + "º!".
LOCK STEERING TO HEADING(HEADING_DEG, PITCH_INITIAL).

// 3. Stage 1 Burnout and Separation
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 1 Burnout. Separation...".
WAIT 0.5.
STAGE. // Decoupling

// 4. Stage 2 Ignition and Progressive Turn Profile
WAIT 1.0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: STAGE 2 IGNITION (SRM-XL)!".
STAGE. // Stage 2 ignition

// Continuous profile formula: as altitude increases, smoothly flatten toward 30 degrees
// At 1,200m -> PITCH_INITIAL (~82º). At 35,000m -> 30º.
LOCK targetPitch TO MAX(30, PITCH_INITIAL - ((SHIP:ALTITUDE - ALT_KICK) / (35000 - ALT_KICK)) * (PITCH_INITIAL - 30)).
LOCK STEERING TO HEADING(HEADING_DEG, targetPitch).

// 5. End of Active Propulsion
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 2 Burnout. Active propulsion complete.".
PRINT "Estimated Apoapsis: " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km.".
UNLOCK STEERING.
SAS ON.

// 6. Ballistic Spaceflight and Fairing Jettison
WHEN SHIP:ALTITUDE > 60000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Residual atmosphere cleared (>60 km). Jettisoning fairings and payload decoupler...".
    STAGE. // Stage 1: Deploy fairings and payload decoupler
}

WHEN SHIP:ALTITUDE > 70000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Crossing the Karman line (>70 km)!".
}

WAIT UNTIL SHIP:VERTICALSPEED < 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: APOAPSIS REACHED (" + ROUND(SHIP:ALTITUDE / 1000, 2) + " km).".

// 7. Atmospheric Reentry
WAIT UNTIL SHIP:ALTITUDE < 70000.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Reentering atmosphere (70 km).".

// 8. Safe Parachute Deployment
PRINT "Monitoring safe recovery parameters...".
WAIT UNTIL (ALT:RADAR < 2500) AND (SHIP:AIRSPEED < 250).

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Safe conditions detected!".
PRINT "DEPLOYING PARACHUTES...".
CHUTES ON.
STAGE.

// 9. Touchdown
WAIT UNTIL SHIP:STATUS = "LANDED" OR SHIP:STATUS = "SPLASHED".
PRINT "==================================================".
PRINT "   T+" + ROUND(MISSIONTIME, 1) + "s: CONTACT CONFIRMED WITH SURFACE!    ".
PRINT "           MISSION RECOVERED SUCCESSFULLY!        ".
PRINT "==================================================".
