// ============================================================================
// Corolt Space Agency (CSA) — Autopilot & Flight Control System
// Vehicle: Corolt-III (Arquitectura Tàndem)
// Missió: Vol Suborbital i Recuperació Autònoma (100% lliure de CommNet)
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "        COROLT SPACE AGENCY - FLIGHT OS           ".
PRINT "   Vehicle: Corolt-III | Missió: Suborbital       ".
PRINT "==================================================".

// 1. Seqüència d'Enlairament
PRINT "Iniciant compte enrere...".
FROM {LOCAL c IS 3.} UNTIL c = 0 STEP {SET c TO c - 1.} DO {
    PRINT "T-" + c.
    WAIT 1.
}

PRINT "IGNICIÓ ETAPA 1: RT-10 «Hammer»!".
STAGE.

// 2. Monitorització d'Etapa 1
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Esgotament Etapa 1. Separació...".
WAIT 0.5.
STAGE. // Desacoblament

WAIT 1.0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: IGNICIÓ ETAPA 2: SRM-XL!".
STAGE. // Ignició 2a etapa

// 3. Monitorització d'Etapa 2
WAIT UNTIL SHIP:MAXTHRUST = 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Esgotament Etapa 2. Fi de propulsió.".
PRINT "Apoapsi estimada: " + ROUND(SHIP:APOAPSIS / 1000, 2) + " km.".

// 4. Vol Balístic i Travessa de l'Espai
WHEN SHIP:ALTITUDE > 70000 THEN {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: ENTRANT A L'ESPAI EXTERIOR (>70 km)!".
}

WAIT UNTIL SHIP:VERTICALSPEED < 0.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: APOGEU ASSOLIT (" + ROUND(SHIP:ALTITUDE / 1000, 2) + " km). Iniciant descens.".

// 5. Reentrada Atmosfèrica
WAIT UNTIL SHIP:ALTITUDE < 70000.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Reentrant a l'atmosfera (70 km).".

// 6. Desplegament Segur del Paracaigudes
// Condicions: Altitud sobre el terreny < 2.500 m i velocitat subsònica segura (< 250 m/s)
PRINT "Esperant paràmetres segurs de salvament...".
WAIT UNTIL (ALT:RADAR < 2500) AND (SHIP:AIRSPEED < 250).

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Condicions segures detectades!".
PRINT "DESPLEGANT PARACAIGUDES...".
CHUTES ON.
STAGE. // Assegura el disparador de l'etapa 0

// 7. Amaratge / Contacte amb Superfície
WAIT UNTIL SHIP:STATUS = "LANDED" OR SHIP:STATUS = "SPLASHED".
PRINT "==================================================".
PRINT "   T+" + ROUND(MISSIONTIME, 1) + "s: CONTACTE CONFIRMAT AMB EL TERRENY! ".
PRINT "           MISSIÓ RECUPERADA AMB ÈXIT!            ".
PRINT "==================================================".
