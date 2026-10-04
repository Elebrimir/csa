// ============================================================================
// Corolt Space Agency (CSA) — Protocol d'Emergència i Recuperació Autònoma
// Script: emergency_recovery.ks
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "  ⚠️ COROLT SPACE AGENCY - PROTOCOL D'EMERGÈNCIA  ".
PRINT "   Recuperació i Salvament Autònom de Càpsula    ".
PRINT "==================================================".

// 1. Estabilització Immediata
UNLOCK STEERING.
LOCK THROTTLE TO 0.
SAS ON.
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Sistemes estabilitzats en mode SAS.".

// 2. Activació de Seguretat de Sensors Científics
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Forçant recollida d'experiments a bord...".
LOCAL activats IS 0.
FOR p IN SHIP:PARTS {
    FOR m_nom IN p:MODULES {
        IF m_nom = "Experiment" OR m_nom = "ModuleScienceExperiment" {
            LOCAL m_part IS p:GETMODULE(m_nom).
            FOR act_nom IN m_part:ALLACTIONNAMES {
                IF act_nom:TOLOWER:CONTAINS("start") OR act_nom:TOLOWER:CONTAINS("inici") {
                    m_part:DOACTION(act_nom, TRUE).
                    SET activats TO activats + 1.
                }
            }
            FOR ev_nom IN m_part:ALLEVENTNAMES {
                IF ev_nom:TOLOWER:CONTAINS("start") OR ev_nom:TOLOWER:CONTAINS("deploy") OR ev_nom:TOLOWER:CONTAINS("inici") OR ev_nom:TOLOWER:CONTAINS("observ") {
                    m_part:DOEVENT(ev_nom).
                    SET activats TO activats + 1.
                }
            }
        }
    }
}
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: " + activats + " sensors activats!".

// 3. Monitorització de Reentrada
IF SHIP:ALTITUDE > 70000 {
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: A l'espai exterior (" + ROUND(SHIP:ALTITUDE/1000, 1) + " km). Esperant reentrada (70 km)...".
    WAIT UNTIL SHIP:ALTITUDE < 70000.
    PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Travessant atmosfera (70 km).".
}

// 4. Desplegament Segur de Paracaigudes
PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Monitoritzant condicions per al paracaigudes...".
WAIT UNTIL (ALT:RADAR < 2500) AND (SHIP:AIRSPEED < 250).

PRINT "T+" + ROUND(MISSIONTIME, 1) + "s: Condicions segures detectades!".
PRINT "DESPLEGANT PARACAIGUDES...".
CHUTES ON.
STAGE.

// 5. Contacte final
WAIT UNTIL SHIP:STATUS = "LANDED" OR SHIP:STATUS = "SPLASHED".
PRINT "==================================================".
PRINT "   T+" + ROUND(MISSIONTIME, 1) + "s: CONTACTE CONFIRMAT AMB EL TERRENY! ".
PRINT "           MISSIO SALVADA AMB EXIT!               ".
PRINT "==================================================".
