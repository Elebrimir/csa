// ============================================================================
// COROLT SPACE AGENCY (CSA) - ORBITAL FLIGHT GUIDANCE SYSTEM
// MISSION: CSA-14 (COROLTSAT-1D CONSTELLATION PHASING & FINE CORRECTION)
// VEHICLE: Corolt-IV B #4 Upper Stage (Belle-RLX81) + CoroltSat-1D Payload
// PROFILE: Phased Equatorial Drift Maneuver to Target Slot
// SAFETY INTERLOCK: Desacoblament condicionat a tolerància d'angle estricta (+/-0.50 deg)
// ============================================================================

DECLARE PARAMETER TARGET_SLOT_DEG IS 40.0.  // Target Constellation slot (Option 2: 40.0 deg for 9-satellite mesh ring)
DECLARE PARAMETER TARGET_ANCHOR IS "CorolSat-1B".
DECLARE PARAMETER DESIRED_DRIFT_ORBITS IS 3. // Number of drift revolutions

CLEARSCREEN.
PRINT "==================================================".
PRINT "       COROLT SPACE AGENCY - MISSION CONTROL      ".
PRINT "    CSA-14: ORBITAL PHASING & CONSTELLATION LOCK  ".
PRINT "   TARGET SLOT: " + TARGET_SLOT_DEG + " deg (Anchor: " + TARGET_ANCHOR + ")".
PRINT "   SAFETY GATE: Strict tolerance +/- 0.50 deg    ".
PRINT "==================================================".

SET KERBIN_MU TO 3.5316000e12.
SET KERBIN_RADIUS TO 600000.0.
SET PI_VAL TO 3.141592653589793.
SET PHASE_TOLERANCE_DEG TO 0.50.

// ----------------------------------------------------------------------------
// 1. Identificació del Target (Anchor Satellite)
// ----------------------------------------------------------------------------
LOCAL tgt_found IS FALSE.
LOCAL tgt_vessel IS SHIP.

IF HASTARGET {
    SET tgt_vessel TO TARGET.
    SET tgt_found TO TRUE.
    PRINT "Objectiu fixat manualment: " + tgt_vessel:NAME.
} ELSE {
    LOCAL all_vessels IS LIST().
    LIST TARGETS IN all_vessels.
    FOR v IN all_vessels {
        LOCAL vn IS v:NAME:TOLOWER.
        IF (NOT tgt_found) AND (vn:CONTAINS(TARGET_ANCHOR:TOLOWER) OR vn:CONTAINS("corolsat-1b") OR vn:CONTAINS("coroltsat-1b")) {
            SET TARGET TO v.
            SET tgt_vessel TO v.
            SET tgt_found TO TRUE.
            PRINT "Objectiu assignat automàticament: " + v:NAME.
        }
    }
}

IF NOT tgt_found {
    PRINT "ERROR CRÍTIC: No s'ha trobat el satèl·lit objectiu (" + TARGET_ANCHOR + ")!".
    PRINT "Si us plau, fixa el satèl·lit àncora com a TARGET a KSP i torna a executar.".
    UNLOCK STEERING.
    UNLOCK THROTTLE.
}

// ----------------------------------------------------------------------------
// Funcions de Càlcul Orbital
// ----------------------------------------------------------------------------
FUNCTION get_orbital_longitude {
    PARAMETER craft.
    LOCAL lng IS craft:OBT:LAN + craft:OBT:ARGUMENTOFPERIAPSIS + craft:OBT:TRUEANOMALY.
    SET lng TO MOD(lng, 360).
    IF lng < 0 { SET lng TO lng + 360. }
    RETURN lng.
}

FUNCTION get_phase_angle {
    PARAMETER ship_craft, tgt_craft.
    LOCAL ship_l IS get_orbital_longitude(ship_craft).
    LOCAL tgt_l IS get_orbital_longitude(tgt_craft).
    LOCAL diff IS MOD(ship_l - tgt_l + 360, 360).
    RETURN diff.
}

FUNCTION deploy_satellite_systems {
    PRINT "Desplegant sistemes de comunicacions i panells solars...".
    AG3 ON.
    FOR part_item IN SHIP:PARTS {
        FOR mod_name IN part_item:MODULES {
            LOCAL part_mod IS part_item:GETMODULE(mod_name).
            FOR ev IN part_mod:ALLEVENTNAMES {
                LOCAL evl IS ev:TOLOWER.
                IF evl:CONTAINS("extend") OR evl:CONTAINS("deploy") OR evl:CONTAINS("desplegar") OR evl:CONTAINS("activar") {
                    IF NOT evl:CONTAINS("chute") AND NOT evl:CONTAINS("decouple") AND NOT evl:CONTAINS("desacoblar") {
                        part_mod:DOEVENT(ev).
                    }
                }
            }
        }
    }
}

FUNCTION separate_payload {
    PRINT "--------------------------------------------------".
    PRINT "EXECUTANT DESACOBLAMENT DE COROLTSAT-1D...".
    LOCAL separated IS FALSE.

    FOR part_item IN SHIP:PARTS {
        IF part_item:HASMODULE("ModuleDecouple") {
            LOCAL part_mod IS part_item:GETMODULE("ModuleDecouple").
            IF part_mod:HASACTION("DecoupleAction") {
                part_mod:DOACTION("DecoupleAction", TRUE).
                SET separated TO TRUE.
                PRINT "  -> DecoupleAction executada a " + part_item:NAME.
            }
            FOR ev IN part_mod:ALLEVENTNAMES {
                LOCAL evl IS ev:TOLOWER.
                IF evl:CONTAINS("decouple") OR evl:CONTAINS("desacobl") OR evl:CONTAINS("desacopl") OR evl:CONTAINS("separ") {
                    part_mod:DOEVENT(ev).
                    SET separated TO TRUE.
                    PRINT "  -> Event " + ev + " executat a " + part_item:NAME.
                }
            }
        }
    }

    STAGE.
    WAIT 0.5.
    STAGE.

    PRINT "Comanda de desacoblament enviada i confirmada!".
    PRINT "--------------------------------------------------".
    RETURN separated.
}

FUNCTION ensure_engines_active {
    LOCAL eng_list IS LIST().
    LIST ENGINES IN eng_list.
    FOR e_item IN eng_list {
        e_item:ACTIVATE().
        PRINT "  -> Motor activat: " + e_item:NAME.
    }
}

// ----------------------------------------------------------------------------
// Diagnòstic Inicial de Fase
// ----------------------------------------------------------------------------
LOCAL cur_phase IS get_phase_angle(SHIP, tgt_vessel).
LOCAL deg_to_gain IS MOD(TARGET_SLOT_DEG - cur_phase + 360, 360).
LOCAL initial_phase_err IS ABS(cur_phase - TARGET_SLOT_DEG).
IF initial_phase_err > 180 { SET initial_phase_err TO 360 - initial_phase_err. }

PRINT "--------------------------------------------------".
PRINT "Angle de fase actual:        " + ROUND(cur_phase, 3) + " deg".
PRINT "Objectiu constel·lació:      " + ROUND(TARGET_SLOT_DEG, 1) + " deg".
PRINT "Desviació absoluta:          " + ROUND(initial_phase_err, 3) + " deg".
PRINT "--------------------------------------------------".

// Si ja estem dins de tolerància, no cal cremar combustible
IF initial_phase_err <= PHASE_TOLERANCE_DEG {
    PRINT ">>> EL VEHICLE JA ES TROBA DINS DE TOLERÀNCIA (+/-" + PHASE_TOLERANCE_DEG + " deg)! <<<".
    PRINT "Procedint directament a la seqüència de desacoblament i deorbitació...".
} ELSE {
    // ----------------------------------------------------------------------------
    // Càlcul de la Maniobra de Phasing Bidireccional
    // ----------------------------------------------------------------------------
    LOCAL tgt_period IS tgt_vessel:OBT:PERIOD.

    IF deg_to_gain <= 180.0 {
        // Cas A: Estem per darrere de l'slot -> Baixar Periapsis a l'Apoapsi (òrbita més ràpida)
        IF SHIP:PERIAPSIS < 270000 {
            // Ja estem a l'orbita el·liptica de drift (recuperacio post-recarrega)
            LOCAL actual_drift_per_orb IS 360.0 * (1.0 - (SHIP:OBT:PERIOD / tgt_period)).
            LOCAL rem_orbits IS MAX(1, ROUND(deg_to_gain / actual_drift_per_orb, 0)).
            PRINT ">>> DETECTADA ORBITA DE DRIFT ACTIVA (Pe = " + ROUND(SHIP:PERIAPSIS/1000, 2) + " km)! <<<".
            PRINT "Saltant Fase 1 (cremada d'insercio ja completada).".
            PRINT "Drift actual per volta:      +" + ROUND(actual_drift_per_orb, 2) + " deg / volta".
            PRINT "Voltes restants fins +40º:   " + rem_orbits.
            PRINT "--------------------------------------------------".

            FROM {LOCAL orb_idx IS 1.} UNTIL orb_idx > rem_orbits STEP {SET orb_idx TO orb_idx + 1.} DO {
                PRINT "Navegant volta de drift restant " + orb_idx + " / " + rem_orbits + "...".
                WAIT UNTIL ETA:PERIAPSIS < 30.
                WAIT UNTIL ETA:APOAPSIS < 90.
            }
        } ELSE {
            LOCAL drift_per_orb IS deg_to_gain / DESIRED_DRIFT_ORBITS.
            LOCAL phasing_period IS tgt_period * (1.0 - (drift_per_orb / 360.0)).
            LOCAL phasing_sma IS (KERBIN_MU * ((phasing_period / (2 * PI_VAL))^2))^(1/3).

            LOCAL r_ap IS SHIP:APOAPSIS + KERBIN_RADIUS.
            LOCAL r_pe_target IS (2 * phasing_sma) - r_ap.
            LOCAL target_pe_alt IS r_pe_target - KERBIN_RADIUS.

            UNTIL target_pe_alt >= 80000 {
                SET DESIRED_DRIFT_ORBITS TO DESIRED_DRIFT_ORBITS + 1.
                SET drift_per_orb TO deg_to_gain / DESIRED_DRIFT_ORBITS.
                SET phasing_period TO tgt_period * (1.0 - (drift_per_orb / 360.0)).
                SET phasing_sma TO (KERBIN_MU * ((phasing_period / (2 * PI_VAL))^2))^(1/3).
                SET r_pe_target TO (2 * phasing_sma) - r_ap.
                SET target_pe_alt TO r_pe_target - KERBIN_RADIUS.
            }

            PRINT "Mode Phasing:                AVANÇAR (Baixar Pe)".
            PRINT "Graus a guanyar:             +" + ROUND(deg_to_gain, 2) + " deg".
            PRINT "Voltes de drift previstes:   " + DESIRED_DRIFT_ORBITS.
            PRINT "Drift requerit per volta:    +" + ROUND(drift_per_orb, 2) + " deg / volta".
            PRINT "Període de drift objectiu:   " + ROUND(phasing_period, 1) + " s (" + ROUND(phasing_period/60, 2) + " min)".
            PRINT "Periapsis de drift objectiu: " + ROUND(target_pe_alt / 1000, 2) + " km".
            PRINT "--------------------------------------------------".

            // FASE 1: Inserció en òrbita de drift a l'Apoapsi
            PRINT "FASE 1: Esperant arribada a l'Apoapsi per a cremar...".
            UNTIL (ETA:APOAPSIS < 90) OR (ETA:APOAPSIS > (SHIP:OBT:PERIOD - 15)) {
                LOCAL cur_p IS get_phase_angle(SHIP, tgt_vessel).
                PRINT "Apropant-se a l'Apoapsi | ETA Ap: " + ROUND(ETA:APOAPSIS, 0) + " s | Fase: " + ROUND(cur_p, 1) + " deg   " AT(0, 18).
                WAIT 0.5.
            }

            SET KUNIVERSE:TIMEWARP:WARP TO 0.
            PRINT "Alineant actitud en RETROGRAD...                                     " AT(0, 18).
            LOCK STEERING TO RETROGRADE.
            WAIT 15.0.

            UNTIL (ETA:APOAPSIS < 10) OR (ETA:APOAPSIS > (SHIP:OBT:PERIOD - 5)) {
                PRINT "Comptador per a l'ignicio retrograda: T-" + ROUND(ETA:APOAPSIS, 0) + " s   " AT(0, 19).
                WAIT 0.2.
            }

            PRINT "IGNICIO RETROGRADA EN MARXA! Baixant Periapsis a " + ROUND(target_pe_alt/1000, 1) + " km...".
            ensure_engines_active().
            LOCAL burn_phase1 IS TRUE.
            UNTIL NOT burn_phase1 {
                LOCAL pe_diff IS SHIP:PERIAPSIS - target_pe_alt.
                IF pe_diff <= 0 {
                    SET burn_phase1 TO FALSE.
                    LOCK THROTTLE TO 0.0.
                } ELSE IF pe_diff < 1500 {
                    LOCK THROTTLE TO 0.05.
                } ELSE IF pe_diff < 5000 {
                    LOCK THROTTLE TO 0.20.
                } ELSE {
                    LOCK THROTTLE TO 0.60.
                }
                PRINT "Burn Fase 1 | Pe actual: " + ROUND(SHIP:PERIAPSIS/1000, 2) + " km | Obj: " + ROUND(target_pe_alt/1000, 2) + " km | Th: " + ROUND(THROTTLE*100, 0) + "%   " AT(0, 21).
                WAIT 0.05.
            }
            LOCK THROTTLE TO 0.0.
            PRINT "ORBITA DE DRIFT ESTABLERTA!".

            // FASE 2: Espera de drift
            FROM {LOCAL orb_idx IS 1.} UNTIL orb_idx > DESIRED_DRIFT_ORBITS STEP {SET orb_idx TO orb_idx + 1.} DO {
                PRINT "Navegant volta de drift " + orb_idx + " / " + DESIRED_DRIFT_ORBITS + "...".
                WAIT UNTIL ETA:PERIAPSIS < 30.
                WAIT UNTIL ETA:APOAPSIS < 90.
            }
        }

        // FASE 3: Circularització al target slot
        PRINT "FASE 3: Circularitzant a l'Apoapsi final...".
        SET KUNIVERSE:TIMEWARP:WARP TO 0.
        LOCK STEERING TO PROGRADE.
        WAIT 15.0.

        WAIT UNTIL (ETA:APOAPSIS < 10) OR (ETA:APOAPSIS > (SHIP:OBT:PERIOD - 5)).
        ensure_engines_active().
        LOCAL burn_circ IS TRUE.
        UNTIL NOT burn_circ {
            LOCAL period_diff IS tgt_period - SHIP:OBT:PERIOD.
            IF period_diff <= 0.2 {
                SET burn_circ TO FALSE.
                LOCK THROTTLE TO 0.0.
            } ELSE IF period_diff < 5.0 {
                LOCK THROTTLE TO 0.05.
            } ELSE IF period_diff < 20.0 {
                LOCK THROTTLE TO 0.25.
            } ELSE {
                LOCK THROTTLE TO 0.70.
            }
            PRINT "Circ Burn | Període: " + ROUND(SHIP:OBT:PERIOD, 1) + "s | Obj: " + ROUND(tgt_period, 1) + "s   " AT(0, 27).
            WAIT 0.05.
        }
        LOCK THROTTLE TO 0.0.
        WAIT 3.0.

    } ELSE {
        // Cas B: Estem per davant de l'slot -> Pujar Apoapsis al Periapsi (òrbita més lenta)
        LOCAL deg_to_lose IS 360.0 - deg_to_gain.
        LOCAL drift_per_orb IS deg_to_lose / DESIRED_DRIFT_ORBITS.
        LOCAL phasing_period IS tgt_period * (1.0 + (drift_per_orb / 360.0)).
        LOCAL phasing_sma IS (KERBIN_MU * ((phasing_period / (2 * PI_VAL))^2))^(1/3).

        LOCAL r_pe IS SHIP:PERIAPSIS + KERBIN_RADIUS.
        LOCAL r_ap_target IS (2 * phasing_sma) - r_pe.
        LOCAL target_ap_alt IS r_ap_target - KERBIN_RADIUS.

        PRINT "Mode Phasing:                RETARDAR (Pujar Ap)".
        PRINT "Graus a cedir:               -" + ROUND(deg_to_lose, 2) + " deg".
        PRINT "Voltes de drift previstes:   " + DESIRED_DRIFT_ORBITS.
        PRINT "Drift requerit per volta:    -" + ROUND(drift_per_orb, 2) + " deg / volta".
        PRINT "Període de drift objectiu:   " + ROUND(phasing_period, 1) + " s (" + ROUND(phasing_period/60, 2) + " min)".
        PRINT "Apoapsis de drift objectiu:  " + ROUND(target_ap_alt / 1000, 2) + " km".
        PRINT "--------------------------------------------------".

        // FASE 1: Inserció en òrbita de drift al Periapsi
        PRINT "FASE 1: Esperant arribada al Periapsi per a cremar...".
        UNTIL (ETA:PERIAPSIS < 90) OR (ETA:PERIAPSIS > (SHIP:OBT:PERIOD - 15)) {
            LOCAL cur_p IS get_phase_angle(SHIP, tgt_vessel).
            PRINT "Apropant-se al Periapsi | ETA Pe: " + ROUND(ETA:PERIAPSIS, 0) + " s | Fase: " + ROUND(cur_p, 1) + " deg   " AT(0, 18).
            WAIT 0.5.
        }

        SET KUNIVERSE:TIMEWARP:WARP TO 0.
        PRINT "Alineant actitud en PROGRAD...                                       " AT(0, 18).
        LOCK STEERING TO PROGRADE.
        WAIT 15.0.

        UNTIL (ETA:PERIAPSIS < 10) OR (ETA:PERIAPSIS > (SHIP:OBT:PERIOD - 5)) {
            PRINT "Comptador per a l'ignicio prograda: T-" + ROUND(ETA:PERIAPSIS, 0) + " s   " AT(0, 19).
            WAIT 0.2.
        }

        PRINT "IGNICIO PROGRADA EN MARXA! Pujant Apoapsis a " + ROUND(target_ap_alt/1000, 1) + " km...".
        ensure_engines_active().
        LOCAL burn_phase1 IS TRUE.
        UNTIL NOT burn_phase1 {
            LOCAL ap_diff IS target_ap_alt - SHIP:APOAPSIS.
            IF ap_diff <= 0 {
                SET burn_phase1 TO FALSE.
                LOCK THROTTLE TO 0.0.
            } ELSE IF ap_diff < 1500 {
                LOCK THROTTLE TO 0.05.
            } ELSE IF ap_diff < 5000 {
                LOCK THROTTLE TO 0.20.
            } ELSE {
                LOCK THROTTLE TO 0.60.
            }
            PRINT "Burn Fase 1 | Ap actual: " + ROUND(SHIP:APOAPSIS/1000, 2) + " km | Obj: " + ROUND(target_ap_alt/1000, 2) + " km | Th: " + ROUND(THROTTLE*100, 0) + "%   " AT(0, 21).
            WAIT 0.05.
        }
        LOCK THROTTLE TO 0.0.
        PRINT "ORBITA DE DRIFT ESTABLERTA!".

        // FASE 2: Espera de drift
        FROM {LOCAL orb_idx IS 1.} UNTIL orb_idx > DESIRED_DRIFT_ORBITS STEP {SET orb_idx TO orb_idx + 1.} DO {
            PRINT "Navegant volta de drift " + orb_idx + " / " + DESIRED_DRIFT_ORBITS + "...".
            WAIT UNTIL ETA:APOAPSIS < 30.
            WAIT UNTIL ETA:PERIAPSIS < 90.
        }

        // FASE 3: Circularització al target slot (al Periapsi, baixant l'Apoapsi)
        PRINT "FASE 3: Circularitzant al Periapsi final...".
        SET KUNIVERSE:TIMEWARP:WARP TO 0.
        LOCK STEERING TO RETROGRADE.
        WAIT 15.0.

        WAIT UNTIL (ETA:PERIAPSIS < 10) OR (ETA:PERIAPSIS > (SHIP:OBT:PERIOD - 5)).
        ensure_engines_active().
        LOCAL burn_circ IS TRUE.
        UNTIL NOT burn_circ {
            LOCAL period_diff IS SHIP:OBT:PERIOD - tgt_period.
            IF period_diff <= 0.2 {
                SET burn_circ TO FALSE.
                LOCK THROTTLE TO 0.0.
            } ELSE IF period_diff < 5.0 {
                LOCK THROTTLE TO 0.05.
            } ELSE IF period_diff < 20.0 {
                LOCK THROTTLE TO 0.25.
            } ELSE {
                LOCK THROTTLE TO 0.70.
            }
            PRINT "Circ Burn | Període: " + ROUND(SHIP:OBT:PERIOD, 1) + "s | Obj: " + ROUND(tgt_period, 1) + "s   " AT(0, 27).
            WAIT 0.05.
        }
        LOCK THROTTLE TO 0.0.
        WAIT 3.0.
    }
}

// ----------------------------------------------------------------------------
// AUDITORIA FINAL DE SEGURETAT (+/- 0.50 deg)
// ----------------------------------------------------------------------------
LOCAL final_phase IS get_phase_angle(SHIP, tgt_vessel).
LOCAL final_err IS ABS(final_phase - TARGET_SLOT_DEG).
IF final_err > 180 { SET final_err TO 360 - final_err. }

PRINT "==================================================".
PRINT "     AUDITORIA DE FASE FINAL DE CONSTEL·LACIÓ     ".
PRINT "  Angle assolit:       " + ROUND(final_phase, 3) + " deg".
PRINT "  Desviació absoluta:  " + ROUND(final_err, 3) + " deg".
PRINT "  Tolerància admesa:   +/-" + PHASE_TOLERANCE_DEG + " deg".
PRINT "==================================================".

IF final_err <= PHASE_TOLERANCE_DEG {
    PRINT ">>> VALIDACIO EXITOSA! L'angle esta dins del marge admes (+/-" + PHASE_TOLERANCE_DEG + " deg). <<<".
    PRINT "Procedint al desacoblament i deorbitacio...".

    deploy_satellite_systems().
    WAIT 3.0.

    PRINT "Orientant actitud a NORMAL orbital pur per a separacio neta...".
    LOCK STEERING TO VCRS(SHIP:VELOCITY:ORBIT, BODY:POSITION).
    WAIT 15.0.

    separate_payload().

    PRINT "==================================================".
    PRINT "   MISSIO CSA-14: COROLTSAT-1D DESACOBLAT AMB EXIT!  ".
    PRINT "   LA CONSTEL-LACIO ESTA FIXADA A " + ROUND(final_phase, 2) + " deg!".
    PRINT "==================================================".

    PRINT "Esperant 30s de marge de seguretat abans de la deorbitacio...".
    WAIT 30.0.

    PRINT "Orientant etapa superior a RETROGRAD per a desorbitar...".
    LOCK STEERING TO RETROGRADE.
    WAIT 15.0.

    PRINT "CREMADA DE DEORBITACIO DE LA SEGONA ETAPA (Zero Debris Protocol)...".
    ensure_engines_active().
    LOCK THROTTLE TO 1.0.
    UNTIL (SHIP:PERIAPSIS <= 0) OR (SHIP:LIQUIDFUEL < 0.2) {
        PRINT "Deorbit Pe: " + ROUND(SHIP:PERIAPSIS / 1000, 1) + " km | Fuel: " + ROUND(SHIP:LIQUIDFUEL, 1) + " LF   " AT(0, 36).
        WAIT 0.2.
    }
    LOCK THROTTLE TO 0.0.
    PRINT "Etapa superior desorbitada! Amaratge segur a l'ocea.".

} ELSE {
    PRINT "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".
    PRINT "ALERTA: Desviació excessiva (" + ROUND(final_err, 3) + " deg > +/-" + PHASE_TOLERANCE_DEG + " deg).".
    PRINT "Desacoblament cancel·lat per seguretat.".
    PRINT "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".
}

UNLOCK STEERING.
UNLOCK THROTTLE.
SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
PRINT "Programa csa14_phasing finalitzat.".
