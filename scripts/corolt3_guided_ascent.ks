// ============================================================================
// Corolt Space Agency (CSA) — Pla d'Ascens i Gir Gravitatori Parametritzat
// Vehicle: Corolt-III
// ============================================================================

DECLARE PARAMETER PITCH_INICIAL IS 82, ALT_KICK IS 1200, RUMB IS 90.

CLEARSCREEN.
PRINT "==================================================".
PRINT "        COROLT SPACE AGENCY - FLIGHT OS           ".
PRINT "       Pla d'Ascens Guiat i Gir Gravitatori       ".
PRINT "==================================================".
PRINT "Configuracio:".
PRINT "  - Inclinacio Kick: " + PITCH_INICIAL + " graus".
PRINT "  - Cota del Kick:   " + ALT_KICK + " m".
PRINT "  - Rumb d'Ascens:   " + RUMB + " graus (Est)".
PRINT "==================================================".

// 1. Enlairament Vertical
LOCK THROTTLE TO 1.0.
LOCK STEERING TO HEADING(RUMB, 90).

PRINT "Iniciant compte enrere...".
FROM {LOCAL c IS 3.} UNTIL c = 0 STEP {SET c TO c - 1.} DO {
    PRINT "T-" + c.
    WAIT 1.
}

PRINT "T+0.0s: IGNICIO ETAPA 1 (RT-10 «Hammer»)!".
STAGE.

// 2. Ascens vertical fins a cota de Kick
WAIT UNTIL SHIP:ALTITUDE > ALT_KICK.
PRINT "T+" + ROUND(MISSIONTIME,1) + "s: INICIANT PITCH KICK A " + PITCH_INICIAL + "º!".
LOCK STEERING TO HEADING(RUMB, PITCH_INICIAL).

// 3. Esgotament Etapa 1 i Separacio
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME,1) + "s: Esgotament Etapa 1. Separacio...".
WAIT 0.5.
STAGE. // Desacoblament

// 4. Ignicio Etapa 2 i Perfil Progressiu
WAIT 1.0.
PRINT "T+" + ROUND(MISSIONTIME,1) + "s: IGNICIO ETAPA 2 (SRM-XL)!".
STAGE. // Ignicio 2a etapa

// Formula de perfil continu: a mes altitud, anem aplanant suaument cap a 30 graus
// A 1.200m -> PITCH_INICIAL (~82º). A 35.000m -> 30º.
LOCK targetPitch TO MAX(30, PITCH_INICIAL - ((SHIP:ALTITUDE - ALT_KICK) / (35000 - ALT_KICK)) * (PITCH_INICIAL - 30)).
LOCK STEERING TO HEADING(RUMB, targetPitch).

// 5. Fi de Propulsio
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME,1) + "s: Esgotament Etapa 2. Fi de propulsio activa.".
PRINT "Apoapsi estimada: " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km.".
UNLOCK STEERING.
SAS ON.

// 6. Vol Balistic a l'Espai i Alliberament de Cobertes
WHEN SHIP:ALTITUDE > 60000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME,1) + "s: Atmosfera residual creuada (>60 km). Alliberant cobertes i separador...".
    STAGE. // Etapa 1: Desplegament de fairings i separador de càrrega
}

WHEN SHIP:ALTITUDE > 70000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME,1) + "s: Travessant la linia de Karman (>70 km)!".
}

WAIT UNTIL SHIP:VERTICALSPEED < 0.
PRINT "T+" + ROUND(MISSIONTIME,1) + "s: APOGEU ASSOLIT (" + ROUND(SHIP:ALTITUDE / 1000, 2) + " km).".

// 7. Reentrada Atmosferica
WAIT UNTIL SHIP:ALTITUDE < 70000.
PRINT "T+" + ROUND(MISSIONTIME,1) + "s: Reentrant a l'atmosfera (70 km).".

// 8. Obertura Segura de Paracaigudes
PRINT "Monitoritzant condicions per al paracaigudes...".
WAIT UNTIL (ALT:RADAR < 2500) AND (SHIP:AIRSPEED < 250).

PRINT "T+" + ROUND(MISSIONTIME,1) + "s: Condicions segures detectades!".
PRINT "DESPLEGANT PARACAIGUDES...".
CHUTES ON.
STAGE.

// 9. Contacte final
WAIT UNTIL SHIP:STATUS = "LANDED" OR SHIP:STATUS = "SPLASHED".
PRINT "==================================================".
PRINT "   T+" + ROUND(MISSIONTIME,1) + "s: CONTACTE CONFIRMAT AMB EL TERRENY! ".
PRINT "           MISSIO RECUPERADA AMB EXIT!            ".
PRINT "==================================================".
