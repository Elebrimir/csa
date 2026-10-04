// ============================================================================
// Corolt Space Agency (CSA) — Emergency Protocol & Autonomous Recovery
// Script: emergency_recovery.ks
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "  ⚠️ COROLT SPACE AGENCY - EMERGENCY PROTOCOL     ".
PRINT "   Autonomous Capsule Recovery & Safeguarding     ".
PRINT "==================================================".

// 1. Immediate Stabilization
UNLOCK STEERING.
LOCK THROTTLE TO 0.
SAS ON.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Systems stabilized in SAS mode.".

// 2. Safety Activation of Scientific Sensors
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Forcing collection of onboard experiments...".
LOCAL activated IS 0.
FOR p IN SHIP:PARTS {
    FOR m_name IN p:MODULES {
        IF m_name = "Experiment" OR m_name = "ModuleScienceExperiment" {
            LOCAL m_part IS p:GETMODULE(m_name).
            FOR act_name IN m_part:ALLACTIONNAMES {
                IF act_name:TOLOWER:CONTAINS("start") OR act_name:TOLOWER:CONTAINS("inici") {
                    m_part:DOACTION(act_name, TRUE).
                    SET activated TO activated + 1.
                }
            }
            FOR ev_name IN m_part:ALLEVENTNAMES {
                IF ev_name:TOLOWER:CONTAINS("start") OR ev_name:TOLOWER:CONTAINS("deploy") OR ev_name:TOLOWER:CONTAINS("inici") OR ev_name:TOLOWER:CONTAINS("observ") {
                    m_part:DOEVENT(ev_name).
                    SET activated TO activated + 1.
                }
            }
        }
    }
}
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: " + activated + " sensors activated!".

// 3. Reentry Monitoring
IF SHIP:ALTITUDE > 70000 {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: In outer space (" + ROUND(SHIP:ALTITUDE/1000, 1) + " km). Awaiting reentry (70 km)...".
    WAIT UNTIL SHIP:ALTITUDE < 70000.
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Crossing atmosphere (70 km).".
}

// 4. Safe Parachute Deployment
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Monitoring safe recovery parameters...".
WAIT UNTIL (ALT:RADAR < 2500) AND (SHIP:AIRSPEED < 250).

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Safe conditions detected!".
PRINT "DEPLOYING PARACHUTES...".
CHUTES ON.
STAGE.

// 5. Touchdown
WAIT UNTIL SHIP:STATUS = "LANDED" OR SHIP:STATUS = "SPLASHED".
PRINT "==================================================".
PRINT "   T+" + ROUND(MISSIONTIME, 1) + "s: CONTACT CONFIRMED WITH SURFACE!    ".
PRINT "           MISSION SAVED SUCCESSFULLY!            ".
PRINT "==================================================".
