// ============================================================================
// Corolt Space Agency (CSA) — Flight OS v2.1
// Mission: CSA-08 «Inland High-Altitude Science & Biome Sampling»
// Vehicle: Corolt-IIIb (Active Control Surfaces & Advanced Science Package)
// Target Heading: 315º (North-West inland towards Grasslands / Highlands)
// Target Apogee:  > 250 km (High Space & Van Allen Belt Sampling)
// ============================================================================

DECLARE PARAMETER PITCH_INITIAL IS 87.5, ALT_KICK IS 2400, HEADING_DEG IS 315.

CLEARSCREEN.
PRINT "==================================================".
PRINT "        COROLT SPACE AGENCY - FLIGHT OS v2.1      ".
PRINT "   Mission CSA-08: Inland Suborbital & High Space ".
PRINT "==================================================".
PRINT "Mission Parameters:".
PRINT "  - Initial Pitch Kick : " + PITCH_INITIAL + " deg".
PRINT "  - Kick Initiation Alt: " + ALT_KICK + " m".
PRINT "  - Launch Heading     : " + HEADING_DEG + " deg (North-West Inland)".
PRINT "  - Target Apogee      : > 250.0 km (Van Allen Belt)".
PRINT "  - Target Biome (Lnd) : Grasslands / Highlands".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Science Trigger Subroutine (Kerbalism & Stock compatible)
// ----------------------------------------------------------------------------
FUNCTION trigger_science_suite {
    PARAMETER stage_label IS "CURRENT REGIME".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [SCIENCE] Triggering instruments for " + stage_label + "...".
    LOCAL count IS 0.
    FOR p IN SHIP:PARTS {
        FOR m_name IN p:MODULES {
            IF m_name = "Experiment" OR m_name = "ModuleScienceExperiment" {
                LOCAL m_part IS p:GETMODULE(m_name).
                // Trigger actions via ALLACTIONNAMES (100% safe, non-throwing)
                FOR act_name IN m_part:ALLACTIONNAMES {
                    LOCAL act_l IS act_name:TOLOWER.
                    IF act_l:CONTAINS("start") OR act_l:CONTAINS("inici") OR act_l:CONTAINS("sample") OR act_l:CONTAINS("deploy") {
                        m_part:DOACTION(act_name, TRUE).
                        SET count TO count + 1.
                    }
                }
            }
        }
    }
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [SCIENCE] " + count + " triggers executed (" + stage_label + ")!".
}

// ----------------------------------------------------------------------------
// Phase 1: Vertical Ignition & Liftoff
// ----------------------------------------------------------------------------
LOCK THROTTLE TO 1.0.
LOCK STEERING TO HEADING(HEADING_DEG, 90).

PRINT "Initiating ignition countdown sequence...".
FROM {LOCAL c IS 3.} UNTIL c = 0 STEP {SET c TO c - 1.} DO {
    PRINT "T-" + c.
    WAIT 1.
}

PRINT "T+0.0s: IGNITION STAGE 1 (RT-10 «Hammer»)!".
STAGE.
LOCAL t_liftoff IS TIME:SECONDS.

// Automated low-atmosphere science activation
WHEN TIME:SECONDS >= t_liftoff + 3.5 THEN {
    trigger_science_suite("LOW ATMOSPHERE (0-18 km)").
}

// Upper atmosphere science activation trigger
WHEN SHIP:ALTITUDE > 18000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [SCIENCE] Entering UPPER ATMOSPHERE (> 18 km).".
    trigger_science_suite("UPPER ATMOSPHERE (18-70 km)").
}

// ----------------------------------------------------------------------------
// Phase 2: Pitch Kick Maneuver
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:ALTITUDE >= ALT_KICK.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: PITCH KICK EXECUTED AT " + PITCH_INITIAL + "º (HDG " + HEADING_DEG + "º)!".
LOCK STEERING TO HEADING(HEADING_DEG, PITCH_INITIAL).

// ----------------------------------------------------------------------------
// Phase 3: Stage 1 Burnout & Interstage Separation
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 1 Burnout. Staging decoupler...".
WAIT 0.5.
STAGE. // Decouple Stage 1

// ----------------------------------------------------------------------------
// Phase 4: Stage 2 Ignition & Optimized High-Apogee Gravity Profile
// ----------------------------------------------------------------------------
WAIT 1.0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: IGNITION STAGE 2 (SRM-XL)!".
STAGE. // Ignite Stage 2

// Steep turn profile keeping altitude high (>250 km capable)
// Slowly transition from PITCH_INITIAL (~87.5º) to 48º at 45,000 m
LOCK targetPitch TO MAX(48, PITCH_INITIAL - ((SHIP:ALTITUDE - ALT_KICK) / (45000 - ALT_KICK)) * (PITCH_INITIAL - 48)).
LOCK STEERING TO HEADING(HEADING_DEG, targetPitch).

// ----------------------------------------------------------------------------
// Phase 5: Propulsion Burnout & Space Transition
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 2 Burnout. Active propulsion complete.".
PRINT "Predicted Apoapsis: " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km.".
UNLOCK STEERING.
SAS ON. // SAS stability damping

// Fairing and interstage truss jettison in thin air
WHEN SHIP:ALTITUDE > 58000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Aerodynamic pressure negligible (> 58 km). Jettisoning protective fairings...".
    STAGE. // Release fairings
}

// Low Space science trigger
WHEN SHIP:ALTITUDE > 70000 THEN {
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [ORBIT] KARMAN LINE EXCEEDED (> 70 km)!".
    PRINT "Entering LOW SPACE environment.".
    PRINT "==================================================".
    trigger_science_suite("LOW SPACE (70-250 km)").
}

// High Space (> 250 km) Van Allen Radiation Belt trigger
WHEN SHIP:ALTITUDE > 250000 THEN {
    PRINT "==================================================".
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: [RADIATION] VAN ALLEN BELT PENETRATED (> 250 km)!".
    PRINT "CRITICAL SCIENCE REGIME: HIGH SPACE DETECTED!".
    PRINT "==================================================".
    trigger_science_suite("HIGH SPACE / VAN ALLEN (> 250 km)").
}

// ----------------------------------------------------------------------------
// Phase 6: Coast to Apoapsis & Descent Prep
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:VERTICALSPEED < 0.
PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: APOAPSIS ATTAINED: " + ROUND(SHIP:ALTITUDE / 1000, 2) + " km!".
PRINT "Current Biome Below: " + SHIP:GEOPOSITION:BIOME.
PRINT "Preparing attitude for atmospheric entry...".
PRINT "==================================================".
SAS ON. // Maintain stabilization

// ----------------------------------------------------------------------------
// Phase 7: Atmospheric Entry & Parachute Recovery
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:ALTITUDE < 70000.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Re-entering atmosphere. Holding retrograde attitude...".

// Safe parachute arming and deployment parameters
WAIT UNTIL (ALT:RADAR < 2500) AND (SHIP:AIRSPEED < 250).
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Subsonic aero regime reached (" + ROUND(SHIP:AIRSPEED, 1) + " m/s).".
PRINT "DEPLOYING RECOVERY PARACHUTE CANOPY!".
CHUTES ON.
STAGE.

// ----------------------------------------------------------------------------
// Phase 8: Surface Touchdown & Landed Science Harvesting
// ----------------------------------------------------------------------------
WAIT UNTIL SHIP:STATUS = "LANDED" OR SHIP:STATUS = "SPLASHED".
LOCAL final_biome IS SHIP:GEOPOSITION:BIOME.
LOCAL final_lat IS ROUND(SHIP:GEOPOSITION:LAT, 4).
LOCAL final_lon IS ROUND(SHIP:GEOPOSITION:LNG, 4).

PRINT "==================================================".
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: TOUCHDOWN CONFIRMED!".
PRINT "Landing Coordinates: Lat " + final_lat + "º | Lon " + final_lon + "º".
PRINT "Landing Biome      : " + final_biome.
PRINT "==================================================".

// Final surface science sampling trigger
WAIT 2.0.
PRINT "Harvesting Surface Ground Science (" + final_biome + ")...".
trigger_science_suite("SURFACE GROUND (" + final_biome + ")").

PRINT "==================================================".
PRINT "    MISSION CSA-08 COMPLETED WITH TOTAL SUCCESS!  ".
PRINT "       Hardware ready for Recovery Crew           ".
PRINT "==================================================".
