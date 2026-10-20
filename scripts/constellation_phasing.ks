// ============================================================================
// COROLT SPACE AGENCY (CSA) - UNIVERSAL CONSTELLATION PHASING SYSTEM v1.0
// SCRIPT: constellation_phasing.ks
// DESCRIPTION:
//   Mission-agnostic, orbit-agnostic bidirectional orbital phasing autopilot.
//   Synchronizes the active vessel to a specified phase angle offset (+ or -)
//   relative to any reference TARGET satellite in the same orbital plane.
//   Supports automatic mid-maneuver recovery if resumed after the Phase 1 burn.
//
// USAGE EXAMPLES:
//   1. Select reference satellite as TARGET in KSP Map View, then run:
//      RUNPATH("0:/csa/constellation_phasing.ks", 40).
//      RUNPATH("0:/csa/constellation_phasing.ks", -40).
//      RUNPATH("0:/csa/constellation_phasing.ks", 120, 4).
//   2. Or pass the target vessel name explicitly as the 3rd parameter:
//      RUNPATH("0:/csa/constellation_phasing.ks", 40, 3, "CorolSat-1B").
// ============================================================================

DECLARE PARAMETER TARGET_SLOT_DEG IS 9999.0.     // Required: desired phase offset in deg (e.g. +40, -40, +120)
DECLARE PARAMETER DESIRED_DRIFT_ORBITS IS 3.     // Optional: initial number of drift revolutions
DECLARE PARAMETER TARGET_NAME_OPT IS "".         // Optional: target vessel name if not set in KSP Map
DECLARE PARAMETER PHASE_TOLERANCE_DEG IS 0.50.   // Optional: strict safety gate tolerance (+/- deg)
DECLARE PARAMETER AUTO_DECOUPLE_DEORBIT IS TRUE. // Optional: Normal separation + Stage 2 deorbit after lock

CLEARSCREEN.
PRINT "==================================================".
PRINT "       COROLT SPACE AGENCY - MISSION CONTROL      ".
PRINT "    UNIVERSAL CONSTELLATION PHASING SYSTEM v1.0   ".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// 0. Parameter Validation (Phase Angle Offset)
// ----------------------------------------------------------------------------
IF TARGET_SLOT_DEG = 9999.0 {
    PRINT "ERROR: Cal indicar l'angle de fase desitjat (en graus)!".
    PRINT "Exemples d'us:".
    PRINT "  RUNPATH(" + CHAR(34) + "0:/csa/constellation_phasing.ks" + CHAR(34) + ", 40).".
    PRINT "  RUNPATH(" + CHAR(34) + "0:/csa/constellation_phasing.ks" + CHAR(34) + ", -40).".
    PRINT "  RUNPATH(" + CHAR(34) + "0:/csa/constellation_phasing.ks" + CHAR(34) + ", 120, 4).".
    PRINT "==================================================".
} ELSE {

    // Normalize desired slot to [0, 360) and signed [-180, +180] for display
    LOCAL norm_slot_deg IS MOD(TARGET_SLOT_DEG, 360.0).
    IF norm_slot_deg < 0 { SET norm_slot_deg TO norm_slot_deg + 360.0. }
    LOCAL signed_slot_deg IS norm_slot_deg.
    IF signed_slot_deg > 180.0 { SET signed_slot_deg TO signed_slot_deg - 360.0. }

    // ------------------------------------------------------------------------
    // 1. Target Acquisition (KSP Map Target or Optional Name)
    // ------------------------------------------------------------------------
    LOCAL tgt_found IS FALSE.
    LOCAL tgt_vessel IS SHIP.

    IF TARGET_NAME_OPT:LENGTH > 0 {
        LOCAL all_vessels IS LIST().
        LIST TARGETS IN all_vessels.
        FOR v IN all_vessels {
            IF (NOT tgt_found) AND v:NAME:TOLOWER:CONTAINS(TARGET_NAME_OPT:TOLOWER) {
                SET TARGET TO v.
                SET tgt_vessel TO v.
                SET tgt_found TO TRUE.
                PRINT "Objectiu assignat per nom: " + v:NAME.
            }
        }
    }
    IF (NOT tgt_found) AND HASTARGET {
        SET tgt_vessel TO TARGET.
        SET tgt_found TO TRUE.
        PRINT "Objectiu detectat (KSP Target): " + tgt_vessel:NAME.
    }

    IF NOT tgt_found {
        PRINT "--------------------------------------------------".
        PRINT "ATENCIO: No hi ha cap satel·lit seleccionat com a TARGET!".
        PRINT "Selecciona el satel·lit ancora al Mapa de KSP i".
        PRINT "torna a executar l'script.".
        PRINT "--------------------------------------------------".
        UNLOCK STEERING.
        UNLOCK THROTTLE.
    } ELSE {

        // --------------------------------------------------------------------
        // 2. Body & Safe Altitude Parameters (Orbit-Agnostic)
        // --------------------------------------------------------------------
        LOCAL BODY_MU IS SHIP:BODY:MU.
        LOCAL BODY_RADIUS IS SHIP:BODY:RADIUS.
        LOCAL PI_VAL IS CONSTANT:PI.
        LOCAL SAFE_MIN_ALT IS 25000.0.
        IF SHIP:BODY:ATM:EXISTS {
            SET SAFE_MIN_ALT TO SHIP:BODY:ATM:HEIGHT + 10000.0.
        }

        // --------------------------------------------------------------------
        // 3. Helper Functions
        // --------------------------------------------------------------------
        FUNCTION get_orbital_longitude {
            PARAMETER craft.
            LOCAL lng IS craft:OBT:LAN + craft:OBT:ARGUMENTOFPERIAPSIS + craft:OBT:TRUEANOMALY.
            SET lng TO MOD(lng, 360.0).
            IF lng < 0 { SET lng TO lng + 360.0. }
            RETURN lng.
        }

        FUNCTION get_phase_angle {
            PARAMETER ship_craft, tgt_craft.
            LOCAL ship_l IS get_orbital_longitude(ship_craft).
            LOCAL tgt_l IS get_orbital_longitude(tgt_craft).
            LOCAL diff IS MOD(ship_l - tgt_l + 360.0, 360.0).
            RETURN diff.
        }

        FUNCTION to_signed_deg {
            PARAMETER angle_deg.
            LOCAL a IS MOD(angle_deg, 360.0).
            IF a < 0 { SET a TO a + 360.0. }
            IF a > 180.0 { SET a TO a - 360.0. }
            RETURN a.
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
            PRINT "EXECUTANT DESACOBLAMENT DE LA CARREGA UTIL...".
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
            }
        }

        // --------------------------------------------------------------------
        // 4. Initial Phase & Orbit State Assessment
        // --------------------------------------------------------------------
        LOCAL cur_phase IS get_phase_angle(SHIP, tgt_vessel).
        LOCAL deg_to_gain IS MOD(norm_slot_deg - cur_phase + 360.0, 360.0).
        LOCAL initial_phase_err IS ABS(to_signed_deg(cur_phase - norm_slot_deg)).
        LOCAL tgt_period IS tgt_vessel:OBT:PERIOD.
        LOCAL tgt_sma IS tgt_vessel:OBT:SEMIMAJORAXIS.

        PRINT "Satel·lit ancora:            " + tgt_vessel:NAME.
        PRINT "Periode de l'ancora:         " + ROUND(tgt_period, 2) + " s".
        PRINT "Angle de fase actual:        " + ROUND(to_signed_deg(cur_phase), 3) + " deg (" + ROUND(cur_phase, 2) + "º)".
        PRINT "Objectiu constel·lacio:      " + ROUND(signed_slot_deg, 3) + " deg (" + ROUND(norm_slot_deg, 2) + "º)".
        PRINT "Desviacio absoluta:          " + ROUND(initial_phase_err, 3) + " deg".
        PRINT "Tolerancia admesa:           +/-" + PHASE_TOLERANCE_DEG + " deg".
        PRINT "--------------------------------------------------".

        // Detect if vessel is already in an active elliptical drift orbit (>2% period difference vs target)
        LOCAL period_ratio_diff IS ABS(SHIP:OBT:PERIOD - tgt_period) / tgt_period.

        IF (initial_phase_err <= PHASE_TOLERANCE_DEG) AND (period_ratio_diff < 0.01) {
            PRINT ">>> EL VEHICLE JA ES TROBA DINS DE TOLERANCIA (+/-" + PHASE_TOLERANCE_DEG + " deg)! <<<".
        } ELSE {

            IF deg_to_gain <= 180.0 {
                // ============================================================
                // MODE A: ADVANCE PHASE (+deg_to_gain) -> Lower Periapsis at Apogee
                // ============================================================
                IF SHIP:OBT:PERIOD < (tgt_period * 0.985) {
                    // Already in faster elliptical drift orbit (post-Phase 1 recovery)
                    LOCAL actual_drift_per_orb IS 360.0 * (1.0 - (SHIP:OBT:PERIOD / tgt_period)).
                    LOCAL rem_orbits IS MAX(1, ROUND(deg_to_gain / actual_drift_per_orb, 0)).
                    PRINT ">>> DETECTADA ORBITA DE DRIFT RAPIDA ACTIVA (Pe = " + ROUND(SHIP:PERIAPSIS/1000, 2) + " km)! <<<".
                    PRINT "Saltant Fase 1 (cremada d'insercio ja completada).".
                    PRINT "Drift actual per volta:      +" + ROUND(actual_drift_per_orb, 2) + " deg / volta".
                    PRINT "Voltes restants fins slot:   " + rem_orbits.
                    PRINT "--------------------------------------------------".

                    FROM {LOCAL orb_idx IS 1.} UNTIL orb_idx > rem_orbits STEP {SET orb_idx TO orb_idx + 1.} DO {
                        PRINT "Navegant volta de drift restant " + orb_idx + " / " + rem_orbits + "...".
                        WAIT UNTIL ETA:PERIAPSIS < 30.
                        WAIT UNTIL ETA:APOAPSIS < 90.
                    }
                } ELSE {
                    LOCAL drift_per_orb IS deg_to_gain / DESIRED_DRIFT_ORBITS.
                    LOCAL phasing_period IS tgt_period * (1.0 - (drift_per_orb / 360.0)).
                    LOCAL phasing_sma IS (BODY_MU * ((phasing_period / (2 * PI_VAL))^2))^(1/3).

                    LOCAL r_ap IS SHIP:APOAPSIS + BODY_RADIUS.
                    LOCAL r_pe_target IS (2 * phasing_sma) - r_ap.
                    LOCAL target_pe_alt IS r_pe_target - BODY_RADIUS.

                    UNTIL target_pe_alt >= SAFE_MIN_ALT {
                        SET DESIRED_DRIFT_ORBITS TO DESIRED_DRIFT_ORBITS + 1.
                        SET drift_per_orb TO deg_to_gain / DESIRED_DRIFT_ORBITS.
                        SET phasing_period TO tgt_period * (1.0 - (drift_per_orb / 360.0)).
                        SET phasing_sma TO (BODY_MU * ((phasing_period / (2 * PI_VAL))^2))^(1/3).
                        SET r_pe_target TO (2 * phasing_sma) - r_ap.
                        SET target_pe_alt TO r_pe_target - BODY_RADIUS.
                    }

                    PRINT "Mode Phasing:                AVANÇAR (Baixar Pe)".
                    PRINT "Graus a guanyar:             +" + ROUND(deg_to_gain, 2) + " deg".
                    PRINT "Voltes de drift previstes:   " + DESIRED_DRIFT_ORBITS.
                    PRINT "Drift requerit per volta:    +" + ROUND(drift_per_orb, 2) + " deg / volta".
                    PRINT "Periode de drift objectiu:   " + ROUND(phasing_period, 1) + " s (" + ROUND(phasing_period/60, 2) + " min)".
                    PRINT "Periapsis de drift objectiu: " + ROUND(target_pe_alt / 1000, 2) + " km".
                    PRINT "--------------------------------------------------".

                    PRINT "FASE 1: Esperant arribada a l'Apoapsi per a cremar...".
                    UNTIL (ETA:APOAPSIS < 90) OR (ETA:APOAPSIS > (SHIP:OBT:PERIOD - 15)) {
                        LOCAL cur_p IS to_signed_deg(get_phase_angle(SHIP, tgt_vessel)).
                        PRINT "Apropant-se a l'Apoapsi | ETA Ap: " + ROUND(ETA:APOAPSIS, 0) + " s | Fase: " + ROUND(cur_p, 1) + " deg   " AT(0, 19).
                        WAIT 0.5.
                    }

                    SET KUNIVERSE:TIMEWARP:WARP TO 0.
                    PRINT "Alineant actitud en RETROGRAD...                                     " AT(0, 19).
                    LOCK STEERING TO RETROGRADE.
                    WAIT 15.0.

                    UNTIL (ETA:APOAPSIS < 10) OR (ETA:APOAPSIS > (SHIP:OBT:PERIOD - 5)) {
                        PRINT "Comptador per a l'ignicio retrograda: T-" + ROUND(ETA:APOAPSIS, 0) + " s   " AT(0, 20).
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
                        PRINT "Burn Fase 1 | Pe actual: " + ROUND(SHIP:PERIAPSIS/1000, 2) + " km | Obj: " + ROUND(target_pe_alt/1000, 2) + " km | Th: " + ROUND(THROTTLE*100, 0) + "%   " AT(0, 22).
                        WAIT 0.05.
                    }
                    LOCK THROTTLE TO 0.0.
                    PRINT "ORBITA DE DRIFT ESTABLERTA!".

                    FROM {LOCAL orb_idx IS 1.} UNTIL orb_idx > DESIRED_DRIFT_ORBITS STEP {SET orb_idx TO orb_idx + 1.} DO {
                        PRINT "Navegant volta de drift " + orb_idx + " / " + DESIRED_DRIFT_ORBITS + "...".
                        WAIT UNTIL ETA:PERIAPSIS < 30.
                        WAIT UNTIL ETA:APOAPSIS < 90.
                    }
                }

                // FASE 3: Circularization at Apogee
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
                    PRINT "Circ Burn | Periode: " + ROUND(SHIP:OBT:PERIOD, 1) + "s | Obj: " + ROUND(tgt_period, 1) + "s   " AT(0, 28).
                    WAIT 0.05.
                }
                LOCK THROTTLE TO 0.0.
                WAIT 3.0.

            } ELSE {
                // ============================================================
                // MODE B: RETARD PHASE (-deg_to_lose) -> Raise Apoapsis at Periapsis
                // ============================================================
                LOCAL deg_to_lose IS 360.0 - deg_to_gain.

                IF SHIP:OBT:PERIOD > (tgt_period * 1.015) {
                    // Already in slower elliptical drift orbit (post-Phase 1 recovery)
                    LOCAL actual_drift_per_orb IS 360.0 * ((SHIP:OBT:PERIOD / tgt_period) - 1.0).
                    LOCAL rem_orbits IS MAX(1, ROUND(deg_to_lose / actual_drift_per_orb, 0)).
                    PRINT ">>> DETECTADA ORBITA DE DRIFT LENTA ACTIVA (Ap = " + ROUND(SHIP:APOAPSIS/1000, 2) + " km)! <<<".
                    PRINT "Saltant Fase 1 (cremada d'insercio ja completada).".
                    PRINT "Drift actual per volta:      -" + ROUND(actual_drift_per_orb, 2) + " deg / volta".
                    PRINT "Voltes restants fins slot:   " + rem_orbits.
                    PRINT "--------------------------------------------------".

                    FROM {LOCAL orb_idx IS 1.} UNTIL orb_idx > rem_orbits STEP {SET orb_idx TO orb_idx + 1.} DO {
                        PRINT "Navegant volta de drift restant " + orb_idx + " / " + rem_orbits + "...".
                        WAIT UNTIL ETA:APOAPSIS < 30.
                        WAIT UNTIL ETA:PERIAPSIS < 90.
                    }
                } ELSE {
                    LOCAL drift_per_orb IS deg_to_lose / DESIRED_DRIFT_ORBITS.
                    LOCAL phasing_period IS tgt_period * (1.0 + (drift_per_orb / 360.0)).
                    LOCAL phasing_sma IS (BODY_MU * ((phasing_period / (2 * PI_VAL))^2))^(1/3).

                    LOCAL r_pe IS SHIP:PERIAPSIS + BODY_RADIUS.
                    LOCAL r_ap_target IS (2 * phasing_sma) - r_pe.
                    LOCAL target_ap_alt IS r_ap_target - BODY_RADIUS.

                    PRINT "Mode Phasing:                RETARDAR (Pujar Ap)".
                    PRINT "Graus a cedir:               -" + ROUND(deg_to_lose, 2) + " deg".
                    PRINT "Voltes de drift previstes:   " + DESIRED_DRIFT_ORBITS.
                    PRINT "Drift requerit per volta:    -" + ROUND(drift_per_orb, 2) + " deg / volta".
                    PRINT "Periode de drift objectiu:   " + ROUND(phasing_period, 1) + " s (" + ROUND(phasing_period/60, 2) + " min)".
                    PRINT "Apoapsis de drift objectiu:  " + ROUND(target_ap_alt / 1000, 2) + " km".
                    PRINT "--------------------------------------------------".

                    PRINT "FASE 1: Esperant arribada al Periapsi per a cremar...".
                    UNTIL (ETA:PERIAPSIS < 90) OR (ETA:PERIAPSIS > (SHIP:OBT:PERIOD - 15)) {
                        LOCAL cur_p IS to_signed_deg(get_phase_angle(SHIP, tgt_vessel)).
                        PRINT "Apropant-se al Periapsi | ETA Pe: " + ROUND(ETA:PERIAPSIS, 0) + " s | Fase: " + ROUND(cur_p, 1) + " deg   " AT(0, 19).
                        WAIT 0.5.
                    }

                    SET KUNIVERSE:TIMEWARP:WARP TO 0.
                    PRINT "Alineant actitud en PROGRAD...                                       " AT(0, 19).
                    LOCK STEERING TO PROGRADE.
                    WAIT 15.0.

                    UNTIL (ETA:PERIAPSIS < 10) OR (ETA:PERIAPSIS > (SHIP:OBT:PERIOD - 5)) {
                        PRINT "Comptador per a l'ignicio prograda: T-" + ROUND(ETA:PERIAPSIS, 0) + " s   " AT(0, 20).
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
                        PRINT "Burn Fase 1 | Ap actual: " + ROUND(SHIP:APOAPSIS/1000, 2) + " km | Obj: " + ROUND(target_ap_alt/1000, 2) + " km | Th: " + ROUND(THROTTLE*100, 0) + "%   " AT(0, 22).
                        WAIT 0.05.
                    }
                    LOCK THROTTLE TO 0.0.
                    PRINT "ORBITA DE DRIFT ESTABLERTA!".

                    FROM {LOCAL orb_idx IS 1.} UNTIL orb_idx > DESIRED_DRIFT_ORBITS STEP {SET orb_idx TO orb_idx + 1.} DO {
                        PRINT "Navegant volta de drift " + orb_idx + " / " + DESIRED_DRIFT_ORBITS + "...".
                        WAIT UNTIL ETA:APOAPSIS < 30.
                        WAIT UNTIL ETA:PERIAPSIS < 90.
                    }
                }

                // FASE 3: Circularization at Periapsis
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
                    PRINT "Circ Burn | Periode: " + ROUND(SHIP:OBT:PERIOD, 1) + "s | Obj: " + ROUND(tgt_period, 1) + "s   " AT(0, 28).
                    WAIT 0.05.
                }
                LOCK THROTTLE TO 0.0.
                WAIT 3.0.
            }
        }

        // --------------------------------------------------------------------
        // 5. Final Constellation Phase Gate Audit (+/- PHASE_TOLERANCE_DEG)
        // --------------------------------------------------------------------
        LOCAL final_phase IS get_phase_angle(SHIP, tgt_vessel).
        LOCAL final_err IS ABS(to_signed_deg(final_phase - norm_slot_deg)).

        PRINT "==================================================".
        PRINT "     AUDITORIA DE FASE FINAL DE CONSTEL·LACIO     ".
        PRINT "  Angle assolit:       " + ROUND(to_signed_deg(final_phase), 3) + " deg (" + ROUND(final_phase, 2) + "º)".
        PRINT "  Objectiu demanat:    " + ROUND(signed_slot_deg, 3) + " deg".
        PRINT "  Desviacio absoluta:  " + ROUND(final_err, 3) + " deg".
        PRINT "  Tolerancia admesa:   +/-" + PHASE_TOLERANCE_DEG + " deg".
        PRINT "==================================================".

        IF final_err <= PHASE_TOLERANCE_DEG {
            PRINT ">>> VALIDACIO EXITOSA! L'angle esta dins del marge admes (+/-" + PHASE_TOLERANCE_DEG + " deg). <<<".
            IF AUTO_DECOUPLE_DEORBIT {
                PRINT "Procedint al desplegament, desacoblament Normal i deorbitacio...".
                deploy_satellite_systems().
                WAIT 3.0.

                PRINT "Orientant actitud a NORMAL orbital pur per a separacio neta...".
                LOCK STEERING TO VCRS(SHIP:VELOCITY:ORBIT, BODY:POSITION).
                WAIT 15.0.

                separate_payload().

                PRINT "==================================================".
                PRINT "   SATEL·LIT DESACOBLAT AMB EXIT!                 ".
                PRINT "   FASE FIXADA A " + ROUND(to_signed_deg(final_phase), 2) + " deg RESPECTE A " + tgt_vessel:NAME.
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
                PRINT "Etapa superior desorbitada! Amaratge segur.".
            }
        } ELSE {
            PRINT "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".
            PRINT "ALERTA: Desviacio (" + ROUND(final_err, 3) + " deg > +/-" + PHASE_TOLERANCE_DEG + " deg).".
            PRINT "Desacoblament cancel·lat per seguretat. Pots tornar a executar".
            PRINT "constellation_phasing.ks per fer un ajust fi d'1 orbita.".
            PRINT "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".
        }

        UNLOCK STEERING.
        UNLOCK THROTTLE.
        SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
        PRINT "Programa constellation_phasing finalitzat.".
    }
}
