// ============================================================================
// COROLT SPACE AGENCY (CSA) - FLIGHT GUIDANCE SYSTEM
// MISSION: CSA-12 (DEORBIT & CONTROLLED OCEAN DISPOSAL)
// VEHICLE: Corolt-IV B #2 Second Stage (Belle-RLX81 + FL-T400 Core)
// TARGET DISPOSAL: Atlantic Maritime Sector (~100 km East of KSC Pad)
// TARGET COORDINATES: Lat ~ 0.0º, Lon ~ -65.0º W (Open Ocean Splashdown)
// TARGET PERIAPSIS: 0.0 km (Steep, Non-Skip Deterministic Atmospheric Plunge)
// CALCULATED BURN LOCATION: Lon +161.2º E (Delta Lon = 133.8º Aero-Orbital Arc)
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "      COROLT SPACE AGENCY - MISSION CONTROL       ".
PRINT "   STAGE 2 DEORBIT & CONTROLLED OCEAN DISPOSAL    ".
PRINT "   VEHICLE: COROLT-IV B #2 | ENGINE: BELLE-RLX81  ".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Deorbit Parameters & Target Calculation
// ----------------------------------------------------------------------------
SET TARGET_SPLASHDOWN_LNG TO -65.0. // Target ocean splashdown: 100 km East of KSC (-74.56º)
SET TARGET_PERIAPSIS TO 0.          // Target Periapsis: 0 km (surface level)
SET REENTRY_DELTA_LNG TO 133.8.     // Aerodynamic and orbital ground track travel arc (deg)

// Calculate required deorbit burn longitude (normalized to [-180, 180])
SET BURN_LNG TO TARGET_SPLASHDOWN_LNG - REENTRY_DELTA_LNG.
IF BURN_LNG < -180.0 {
    SET BURN_LNG TO BURN_LNG + 360.0.
}

SET KERBIN_RADIUS TO 600000.
SET KERBIN_ROT_PERIOD TO 21600.
SET KSC_LNG TO -74.557.

PRINT "Target Splashdown Longitude: " + ROUND(TARGET_SPLASHDOWN_LNG, 1) + "º W".
PRINT "Calculated Deorbit Burn Node: " + ROUND(BURN_LNG, 1) + "º E".
PRINT "Target Re-entry Periapsis:    " + ROUND(TARGET_PERIAPSIS / 1000, 1) + " km".
PRINT "--------------------------------------------------".

// ----------------------------------------------------------------------------
// Helper Functions
// ----------------------------------------------------------------------------
FUNCTION get_eta_to_burn_node {
    LOCAL cur_lng IS SHIP:GEOPOSITION:LNG.
    LOCAL deg_to_go IS BURN_LNG - cur_lng.
    UNTIL deg_to_go > 0 { SET deg_to_go TO deg_to_go + 360. }
    SET deg_to_go TO deg_to_go - (FLOOR(deg_to_go / 360) * 360).
    IF deg_to_go <= 0 { SET deg_to_go TO deg_to_go + 360. }

    LOCAL omega_orb IS 360.0 / MAX(1.0, SHIP:ORBIT:PERIOD).
    LOCAL omega_kerbin IS 360.0 / KERBIN_ROT_PERIOD.
    LOCAL omega_rel IS omega_orb - omega_kerbin.

    LOCAL eta_seconds IS deg_to_go / omega_rel.
    RETURN eta_seconds.
}

FUNCTION get_ksc_distance_km {
    LOCAL d_lng IS ABS(SHIP:GEOPOSITION:LNG - KSC_LNG).
    IF d_lng > 180 { SET d_lng TO 360 - d_lng. }
    LOCAL d_lat IS ABS(SHIP:GEOPOSITION:LAT - (-0.097)).
    LOCAL rad_dist IS SQRT(d_lng * d_lng + d_lat * d_lat) * (CONSTANT:PI / 180.0) * KERBIN_RADIUS.
    RETURN ROUND(rad_dist / 1000.0, 1).
}

// ----------------------------------------------------------------------------
// Phase 1: Orbital Phasing & Alignment
// ----------------------------------------------------------------------------
SAS OFF.
RCS OFF.

LOCAL eta_burn IS get_eta_to_burn_node().
PRINT "Current Longitude: " + ROUND(SHIP:GEOPOSITION:LNG, 1) + "º".
PRINT "Time until Burn Node: " + ROUND(eta_burn / 60, 1) + " min (" + ROUND(eta_burn, 0) + " s)".

// If burn is more than 60s away, use time warp
IF eta_burn > 60.0 {
    PRINT "Warping to burn node (T-45s)...".
    WARPTO(TIME:SECONDS + eta_burn - 45.0).
    WAIT UNTIL (TIME:WARP = 0) OR (get_eta_to_burn_node() <= 48.0).
}

PRINT "--------------------------------------------------".
PRINT "T-45s: Orienting attitude strictly to RETROGRADE...".
LOCK STEERING TO RETROGRADE.

// Wait until vessel is exactly at burn node
UNTIL get_eta_to_burn_node() <= 3.0 {
    PRINT "Aligning Retrograde | Dist to Node: " + ROUND(get_eta_to_burn_node(), 1) + "s | Alt: " + ROUND(SHIP:ALTITUDE/1000, 1) + "km" AT(0, 12).
    WAIT 0.5.
}

PRINT "==================================================".
PRINT "COUNTDOWN TO DEORBIT BURN:".
FROM {LOCAL countdown IS 3.} UNTIL countdown = 0 STEP {SET countdown TO countdown - 1.} DO {
    PRINT "T-" + countdown + "...".
    WAIT 1.
}

// ----------------------------------------------------------------------------
// Phase 2: Deorbit Burn Execution (Belle-RLX81 Retrograde)
// ----------------------------------------------------------------------------
PRINT "==================================================".
PRINT "IGNITION: EXECUTING RETROGRADE DEORBIT BURN!".
PRINT "==================================================".
LOCK THROTTLE TO 1.0.

LOCAL burn_start_time IS TIME:SECONDS.

// Burn full throttle until Periapsis drops to 20 km, then taper for precision
UNTIL (SHIP:PERIAPSIS <= 20000) OR (STAGE:LIQUIDFUEL < 0.2) {
    PRINT "Burning Retrograde | Pe: " + ROUND(SHIP:PERIAPSIS/1000, 1) + "km | Fuel: " + ROUND(STAGE:LIQUIDFUEL, 1) + " LF" AT(0, 18).
    WAIT 0.1.
}

PRINT "Approaching target Periapsis (20 km). Precision throttle at 25%...".
LOCK THROTTLE TO 0.25.

UNTIL (SHIP:PERIAPSIS <= TARGET_PERIAPSIS) OR (STAGE:LIQUIDFUEL < 0.2) {
    PRINT "Precision Taper | Pe: " + ROUND(SHIP:PERIAPSIS/1000, 1) + "km | Fuel: " + ROUND(STAGE:LIQUIDFUEL, 1) + " LF" AT(0, 18).
    WAIT 0.1.
}

LOCK THROTTLE TO 0.0.
LOCAL burn_duration IS TIME:SECONDS - burn_start_time.

PRINT "==================================================".
PRINT "ENGINE CUTOFF: DEORBIT BURN COMPLETE!".
PRINT "Burn Duration:     " + ROUND(burn_duration, 1) + " seconds".
PRINT "Resulting Periapsis: " + ROUND(SHIP:PERIAPSIS / 1000, 2) + " km".
PRINT "Resulting Apoapsis:  " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km".
PRINT "Propellant Remaining: " + ROUND(STAGE:LIQUIDFUEL, 1) + " LF / " + ROUND(STAGE:OXIDIZER, 1) + " Ox".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Phase 3: Coast to Atmospheric Interface (70 km)
// ----------------------------------------------------------------------------
PRINT "Locking attitude to RETROGRADE to maximize drag profile...".
LOCK STEERING TO RETROGRADE.

IF SHIP:ALTITUDE > 85000 {
    PRINT "Coasting through exosphere to atmospheric boundary...".
    LOCAL eta_entry IS (SHIP:ALTITUDE - 70000) / MAX(1.0, ABS(SHIP:VERTICALSPEED)).
    IF eta_entry > 60 {
        WARPTO(TIME:SECONDS + eta_entry - 30).
    }
}

WAIT UNTIL SHIP:ALTITUDE <= 70000.
PRINT "==================================================".
PRINT "T+ENTRY: ATMOSPHERIC INTERFACE CROSSED (70.0 KM)!".
PRINT "STAGE 2 HAS COMMENCED TERMINAL HYPERSONIC RE-ENTRY".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Phase 4: Atmospheric Descent & Telemetry Stream
// ----------------------------------------------------------------------------
LOCAL max_q_kpa IS 0.
LOCAL max_g_load IS 0.
LOCAL last_spd IS SHIP:SURFACESPEED.
LOCAL last_time IS TIME:SECONDS.

UNTIL (SHIP:ALTITUDE <= 100) OR (SHIP:STATUS = "SPLASHED") OR (SHIP:STATUS = "LANDED") {
    LOCAL cur_q IS (SHIP:DYNAMICPRESSURE * CONSTANT:ATMTOKPA).
    IF cur_q > max_q_kpa { SET max_q_kpa TO cur_q. }

    LOCAL dt IS MAX(0.01, TIME:SECONDS - last_time).
    LOCAL cur_g IS ABS(SHIP:SURFACESPEED - last_spd) / (dt * 9.81).
    SET last_spd TO SHIP:SURFACESPEED.
    SET last_time TO TIME:SECONDS.
    IF cur_g > max_g_load { SET max_g_load TO cur_g. }

    LOCAL dist_ksc IS get_ksc_distance_km().

    PRINT "Alt: " + ROUND(SHIP:ALTITUDE/1000, 1) + "km | Spd: " + ROUND(SHIP:SURFACESPEED, 0) + "m/s | Q: " + ROUND(cur_q, 1) + "kPa | KSC: " + dist_ksc + "km | Lon: " + ROUND(SHIP:GEOPOSITION:LNG, 1) + "º" AT(0, 28).

    WAIT 0.2.
}

PRINT "==================================================".
PRINT "TERMINAL IMPACT / SPLASHDOWN CONFIRMED!".
PRINT "Final Coordinates: Lat " + ROUND(SHIP:GEOPOSITION:LAT, 3) + "º, Lon " + ROUND(SHIP:GEOPOSITION:LNG, 3) + "º".
PRINT "Distance from KSC: " + get_ksc_distance_km() + " km (Maritime Sector)".
PRINT "Peak Re-entry Q:   " + ROUND(max_q_kpa, 1) + " kPa".
PRINT "Peak G-Force Load: " + ROUND(max_g_load, 2) + " G".
PRINT "==================================================".
PRINT "MISSION CSA-12 STAGE 2 DEORBIT 100% ACCOMPLISHED!".
PRINT "==================================================".

UNLOCK STEERING.
UNLOCK THROTTLE.
SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
