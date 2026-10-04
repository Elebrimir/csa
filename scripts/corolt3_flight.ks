// ============================================================================
// Corolt Space Agency (CSA) — Autopilot & Flight Control System
// Vehicle: Corolt-III (Tandem Architecture)
// Mission: Suborbital Flight & Autonomous Recovery (100% free of CommNet)
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "        COROLT SPACE AGENCY - FLIGHT OS           ".
PRINT "   Vehicle: Corolt-III | Mission: Suborbital      ".
PRINT "==================================================".

// 1. Liftoff Sequence
PRINT "Starting countdown...".
FROM {LOCAL c IS 3.} UNTIL c = 0 STEP {SET c TO c - 1.} DO {
    PRINT "T-" + c.
    WAIT 1.
}

PRINT "STAGE 1 IGNITION: RT-10 «Hammer»!".
STAGE.

// 2. Stage 1 Monitoring
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 1 Burnout. Separation...".
WAIT 0.5.
STAGE. // Decoupling

WAIT 1.0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: STAGE 2 IGNITION: SRM-XL!".
STAGE. // Stage 2 ignition

// 3. Stage 2 Monitoring
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Stage 2 Burnout. Propulsion complete.".
PRINT "Estimated Apoapsis: " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km.".

// 4. Ballistic Flight and Space Crossing
WHEN SHIP:ALTITUDE > 70000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: ENTERING OUTER SPACE (>70 km)!".
}

WAIT UNTIL SHIP:VERTICALSPEED < 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: APOAPSIS REACHED (" + ROUND(SHIP:ALTITUDE / 1000, 2) + " km). Beginning descent.".

// 5. Atmospheric Reentry
WAIT UNTIL SHIP:ALTITUDE < 70000.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Reentering atmosphere (70 km).".

// 6. Safe Parachute Deployment
// Conditions: Radar altitude < 2,500 m and safe subsonic airspeed (< 250 m/s)
PRINT "Monitoring safe recovery parameters...".
WAIT UNTIL (ALT:RADAR < 2500) AND (SHIP:AIRSPEED < 250).

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Safe conditions detected!".
PRINT "DEPLOYING PARACHUTES...".
CHUTES ON.
STAGE. // Triggers stage 0 parachute deployment

// 7. Touchdown / Surface Contact
WAIT UNTIL SHIP:STATUS = "LANDED" OR SHIP:STATUS = "SPLASHED".
PRINT "==================================================".
PRINT "   T+" + ROUND(MISSIONTIME, 1) + "s: CONTACT CONFIRMED WITH SURFACE!    ".
PRINT "           MISSION RECOVERED SUCCESSFULLY!        ".
PRINT "==================================================".
