// ============================================================================
// COROLT SPACE AGENCY (CSA) - UNIVERSAL STAGE 2 DEORBIT PROTOCOL v2.0
// SCRIPT: stage2_deorbit.ks
// DESCRIPTION:
//   Orients the spent Belle-RLX81 upper stage to pure RETROGRADE and executes
//   a full disposal burn until Periapsis <= 0 km (Zero Debris Protocol).
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "   CSA ZERO DEBRIS PROTOCOL - STAGE 2 DEORBIT     ".
PRINT "   VESSEL: " + SHIP:NAME.
PRINT "==================================================".

SET KUNIVERSE:TIMEWARP:WARP TO 0.
SAS OFF.

LOCAL eng_list IS LIST().
LIST ENGINES IN eng_list.
FOR e_item IN eng_list {
    e_item:ACTIVATE().
}

PRINT "Orienting upper stage to RETROGRADE...".
LOCK STEERING TO RETROGRADE.
WAIT 12.0.

PRINT "EXECUTING STAGE 2 DEORBIT BURN (Belle-RLX81)...".
LOCK THROTTLE TO 1.0.
LOCAL deorbit_start IS TIME:SECONDS.

UNTIL (SHIP:PERIAPSIS <= 0) OR (SHIP:LIQUIDFUEL < 0.2) {
    PRINT "Deorbit Pe: " + ROUND(SHIP:PERIAPSIS / 1000, 1) + " km | Fuel: " + ROUND(SHIP:LIQUIDFUEL, 1) + " LF   " AT(0, 14).
    WAIT 0.2.
}

LOCK THROTTLE TO 0.0.
LOCAL deorbit_dur IS TIME:SECONDS - deorbit_start.
PRINT "==================================================".
PRINT "DEORBIT BURN COMPLETE (" + ROUND(deorbit_dur, 1) + " s)!".
PRINT "FINAL PERIAPSIS: " + ROUND(SHIP:PERIAPSIS / 1000, 2) + " km.".
PRINT "Belle-RLX81 upper stage targeted for ocean disposal!".
PRINT "==================================================".

LOCK STEERING TO RETROGRADE.
WAIT 5.0.
UNLOCK STEERING.
UNLOCK THROTTLE.
SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
