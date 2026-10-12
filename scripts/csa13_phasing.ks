// ============================================================================
// COROLT SPACE AGENCY (CSA) - ORBITAL FLIGHT GUIDANCE SYSTEM
// MISSION: CSA-13 (COROLTSAT-1C CONSTELLATION PHASING & SEPARATION)
// VEHICLE: Corolt-IV B #3 Upper Stage (Belle-RLX81) + CoroltSat-1C Payload
// PROFILE: 4-Orbit Equatorial Drift Maneuver to 120º Constellation Slot
// SAFETY INTERLOCK: Desacoblament condicionat a tolerància d'angle [115º, 125º]
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "       COROLT SPACE AGENCY - MISSION CONTROL      ".
PRINT "    CSA-13: ORBITAL PHASING & CONSTELLATION LOCK  ".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// Constel·lació & Objectius
// ----------------------------------------------------------------------------
SET TARGET_PHASE_ANGLE TO 120.0.    // Slot objectiu: +120º per davant de CorolSat-1B
SET MIN_ACCEPTABLE_PHASE TO 115.0.  // Límit inferior de seguretat per desacoblar
SET MAX_ACCEPTABLE_PHASE TO 125.0.  // Límit superior de seguretat per desacoblar
SET NUM_PHASING_ORBITS TO 4.        // Número de voltes de drift
SET KERBIN_MU TO 3.5316000e12.
SET KERBIN_RADIUS TO 600000.0.
SET PI_VAL TO 3.141592653589793.

// ----------------------------------------------------------------------------
// 1. Identificació del Target (CorolSat-1B)
// ----------------------------------------------------------------------------
LOCAL tgt_found IS FALSE.
LOCAL tgt_vessel IS SHIP.

IF HASTARGET {
    SET tgt_vessel TO TARGET.
    SET tgt_found TO TRUE.
    PRINT "Objectiu fixat manualment: " + tgt_vessel:NAME.
} ELSE {
    // Intentar seleccionar automàticament per nom
    SET TARGET TO VESSEL("CorolSat-1B").
    IF HASTARGET {
        SET tgt_vessel TO TARGET.
        SET tgt_found TO TRUE.
        PRINT "Objectiu assignat automàticament: CorolSat-1B".
    }
}

IF NOT tgt_found {
    PRINT "ERROR CRÍTIC: No s'ha trobat el satèl·lit objectiu!".
    PRINT "Si us plau, fixa CorolSat-1B com a TARGET a KSP i torna a executar.".
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
    // Angle de fase: quants graus va SHIP per davant de TGT en direcció prograda
    LOCAL diff IS MOD(ship_l - tgt_l + 360, 360).
    RETURN diff.
}

// ----------------------------------------------------------------------------
// Càlcul de la Maniobra de Phasing (4 Voltes)
// ----------------------------------------------------------------------------
LOCAL cur_phase IS get_phase_angle(SHIP, tgt_vessel).
LOCAL deg_to_gain IS MOD(TARGET_PHASE_ANGLE - cur_phase + 360, 360).
LOCAL drift_per_orb IS deg_to_gain / NUM_PHASING_ORBITS.

LOCAL tgt_period IS tgt_vessel:OBT:PERIOD.
LOCAL phasing_period IS tgt_period * (1.0 - (drift_per_orb / 360.0)).
LOCAL phasing_sma IS (KERBIN_MU * ((phasing_period / (2 * PI_VAL))^2))^(1/3).

// Calculem el Periapsis requerit mantenint l'Apoapsis actual com a r_ap
LOCAL r_ap IS SHIP:APOAPSIS + KERBIN_RADIUS.
LOCAL r_pe_target IS (2 * phasing_sma) - r_ap.
LOCAL target_pe_alt IS r_pe_target - KERBIN_RADIUS.

PRINT "--------------------------------------------------".
PRINT "Angle de fase actual:        " + ROUND(cur_phase, 2) + "º".
PRINT "Objectiu constel·lació:      " + ROUND(TARGET_PHASE_ANGLE, 1) + "º".
PRINT "Graus a guanyar:             +" + ROUND(deg_to_gain, 2) + "º".
PRINT "Drift requerit per volta:    +" + ROUND(drift_per_orb, 2) + "º / volta".
PRINT "Període de fase objectiu:    " + ROUND(phasing_period, 1) + " s (" + ROUND(phasing_period/60, 2) + " min)".
PRINT "Periapsis de fase objectiu:  " + ROUND(target_pe_alt / 1000, 2) + " km".
PRINT "--------------------------------------------------".

IF target_pe_alt < 80000 {
    PRINT "ALERTA: Periapsis de fase massa baix (< 80 km)!".
    PRINT "Operació cancel·lada per seguretat atmosfèrica.".
    UNLOCK STEERING.
    UNLOCK THROTTLE.
}

// ----------------------------------------------------------------------------
// FASE 1: Cremada Retrògrada a l'Apoapsi (Baixar Periapsis a Òrbita de Fase)
// ----------------------------------------------------------------------------
PRINT "FASE 1: Preparant inserció en òrbita de drift a l'Apoapsi...".
PRINT "Pots accelerar el temps (timewarp) manualment.".

// Esperar a aproximar-se a l'Apoapsi
UNTIL (ETA:APOAPSIS < 90) OR (ETA:APOAPSIS > (SHIP:OBT:PERIOD - 15)) {
    LOCAL cur_p IS get_phase_angle(SHIP, tgt_vessel).
    PRINT "Apropant-se a l'Apoapsi | ETA Ap: " + ROUND(ETA:APOAPSIS, 0) + " s | Fase: " + ROUND(cur_p, 1) + "º   " AT(0, 16).
    WAIT 0.5.
}

// Dropar timewarp a 0 si l'usuari tenia warp actiu
SET KUNIVERSE:TIMEWARP:WARP TO 0.
PRINT "Alineant actitud en RETRÒGRAD...                                     " AT(0, 16).
LOCK STEERING TO RETROGRADE.
WAIT 15.0.

UNTIL (ETA:APOAPSIS < 10) OR (ETA:APOAPSIS > (SHIP:OBT:PERIOD - 5)) {
    PRINT "Comptador per a l'ignició retrògrada: T-" + ROUND(ETA:APOAPSIS, 0) + " s   " AT(0, 17).
    WAIT 0.2.
}

PRINT "IGNICIÓ RETRÒGRADA EN MARXA! Baixant Periapsis a " + ROUND(target_pe_alt/1000, 1) + " km...".
ensure_engines_active().
LOCAL burn_phase1 IS TRUE.
UNTIL NOT burn_phase1 {
    LOCAL pe_diff IS SHIP:PERIAPSIS - target_pe_alt.
    IF pe_diff <= 0 {
        SET burn_phase1 TO FALSE.
        LOCK THROTTLE TO 0.0.
    } ELSE IF pe_diff < 1500 {
        LOCK THROTTLE TO 0.05. // Ajust fi
    } ELSE IF pe_diff < 5000 {
        LOCK THROTTLE TO 0.20.
    } ELSE {
        LOCK THROTTLE TO 0.60.
    }
    PRINT "Burn Fase 1 | Pe actual: " + ROUND(SHIP:PERIAPSIS/1000, 2) + " km | Obj: " + ROUND(target_pe_alt/1000, 2) + " km | Th: " + ROUND(THROTTLE*100, 0) + "%   " AT(0, 19).
    WAIT 0.05.
}

LOCK THROTTLE TO 0.0.
PRINT "==================================================".
PRINT "ÒRBITA DE DRIFT ASSOLIDA!".
PRINT "  Periapsis: " + ROUND(SHIP:PERIAPSIS / 1000, 2) + " km".
PRINT "  Període:   " + ROUND(SHIP:OBT:PERIOD, 1) + " s".
PRINT "==================================================".

// ----------------------------------------------------------------------------
// FASE 2: Monitorització del Drift de 4 Voltes
// ----------------------------------------------------------------------------
PRINT "FASE 2: Executant les 4 voltes de drift.".
PRINT "El satèl·lit guanyarà ~" + ROUND(drift_per_orb, 1) + "º per cada volta.".
PRINT "Pots usar TIMEWARP manualment. kOS avisarà i frenarà el warp a la volta 4.".

LOCAL orbits_completed IS 0.
LOCAL last_eta_ap IS ETA:APOAPSIS.

UNTIL orbits_completed >= NUM_PHASING_ORBITS {
    LOCAL cur_eta_ap IS ETA:APOAPSIS.
    LOCAL cur_p IS get_phase_angle(SHIP, tgt_vessel).

    // Detectem pas per Apoapsi quan ETA:APOAPSIS fa el salt de 0 a SHIP:OBT:PERIOD
    IF (last_eta_ap < 60) AND (cur_eta_ap > (SHIP:OBT:PERIOD - 120)) {
        SET orbits_completed TO orbits_completed + 1.
        PRINT ">>> VOLTA DE DRIFT " + orbits_completed + " DE " + NUM_PHASING_ORBITS + " COMPLETADA! Fase actual: " + ROUND(cur_p, 2) + "º <<<".
    }
    SET last_eta_ap TO cur_eta_ap.

    // A l'última volta (quan falten menys de 90s per a l'Apoapsi final de la volta 4), aturem el timewarp
    IF (orbits_completed = (NUM_PHASING_ORBITS - 1)) AND (cur_eta_ap < 90) {
        SET KUNIVERSE:TIMEWARP:WARP TO 0.
        BREAK.
    }

    PRINT "Drift Actiu | Voltes: " + orbits_completed + "/" + NUM_PHASING_ORBITS + " | Fase: " + ROUND(cur_p, 2) + "º (Obj: 120º) | ETA Ap: " + ROUND(cur_eta_ap, 0) + " s   " AT(0, 25).
    WAIT 0.5.
}

// ----------------------------------------------------------------------------
// FASE 3: Circularització Final a l'Apoapsi 4 (Bloqueig de la Constel·lació)
// ----------------------------------------------------------------------------
SET KUNIVERSE:TIMEWARP:WARP TO 0.
PRINT "--------------------------------------------------".
PRINT "FASE 3: Sincronització final de constel·lació a l'Apoapsi!".
PRINT "Alineant actitud en PROGRADE...".
LOCK STEERING TO PROGRADE.
WAIT 15.0.

UNTIL (ETA:APOAPSIS < 10) OR (ETA:APOAPSIS > (SHIP:OBT:PERIOD - 5)) {
    PRINT "Comptador per a la circularització final: T-" + ROUND(ETA:APOAPSIS, 0) + " s   " AT(0, 28).
    WAIT 0.2.
}

PRINT "IGNICIÓ PROGRADA EN MARXA! Igualant període orbital amb CorolSat-1B...".
ensure_engines_active().
LOCAL burn_phase3 IS TRUE.
UNTIL NOT burn_phase3 {
    LOCAL period_diff IS tgt_period - SHIP:OBT:PERIOD.
    IF period_diff <= 0.2 {
        SET burn_phase3 TO FALSE.
        LOCK THROTTLE TO 0.0.
    } ELSE IF period_diff < 5.0 {
        LOCK THROTTLE TO 0.05. // Ajust mil·limètric del període
    } ELSE IF period_diff < 20.0 {
        LOCK THROTTLE TO 0.25.
    } ELSE {
        LOCK THROTTLE TO 0.70.
    }
    PRINT "Circ Burn | Període: " + ROUND(SHIP:OBT:PERIOD, 1) + "s | Obj: " + ROUND(tgt_period, 1) + "s | Diff: " + ROUND(period_diff, 1) + "s   " AT(0, 30).
    WAIT 0.05.
}

LOCK THROTTLE TO 0.0.
WAIT 3.0.

// ----------------------------------------------------------------------------
// FASE 4: Verificació de Seguretat i Desacoblament Condicional [115º, 125º]
// ----------------------------------------------------------------------------
LOCAL final_phase IS get_phase_angle(SHIP, tgt_vessel).
PRINT "==================================================".
PRINT "     AUDITORIA DE FASE FINAL DE CONSTEL·LACIÓ     ".
PRINT "  Angle assolit: " + ROUND(final_phase, 2) + "º".
PRINT "  Finestra permesa per a desacoblar: [" + MIN_ACCEPTABLE_PHASE + "º, " + MAX_ACCEPTABLE_PHASE + "º]".
PRINT "==================================================".

IF (final_phase >= MIN_ACCEPTABLE_PHASE) AND (final_phase <= MAX_ACCEPTABLE_PHASE) {
    PRINT ">>> VALIDACIÓ EXITOSA! L'angle està dins dels paràmetres correctes. <<<".
    PRINT "Preparant procediment de desplegament i separació...".
    
    // Desplegar sistemes del satèl·lit (antenes i panells)
    deploy_satellite_systems().
    WAIT 3.0.

    // Orientar a eix NORMAL per evitar absolutament cap impuls en l'eix orbital prograda/retrograda
    PRINT "Orientant actitud a NORMAL orbital pur per a separació neta...".
    LOCAL normal_vec IS VCRS(SHIP:VELOCITY:ORBIT, BODY:POSITION).
    LOCK STEERING TO normal_vec.
    WAIT 15.0.

    // Desacoblar
    separate_payload().

    PRINT "==================================================".
    PRINT "   MISSIÓ CSA-13: COROLTSAT-1C DESACOBLAT AMB ÈXIT!  ".
    PRINT "   LA CONSTEL·LACIÓ ESTÀ FIXADA A " + ROUND(final_phase, 2) + "º!".
    PRINT "==================================================".

    // Esperar marge abans de maniobra de deorbitació de la 2a etapa
    PRINT "Esperant 30s de marge de seguretat abans de la deorbitació de l'etapa buida...".
    WAIT 30.0.

    PRINT "Orientant etapa superior a RETRÒGRAD per a desorbitar...".
    LOCK STEERING TO RETROGRADE.
    WAIT 15.0.

    PRINT "CREMADA DE DEORBITACIÓ DE LA SEGONA ETAPA (Zero Debris Protocol)...".
    ensure_engines_active().
    LOCK THROTTLE TO 1.0.
    UNTIL (SHIP:PERIAPSIS <= 0) OR (STAGE:LIQUIDFUEL < 0.2) {
        PRINT "Deorbit Pe: " + ROUND(SHIP:PERIAPSIS / 1000, 1) + " km | Fuel: " + ROUND(STAGE:LIQUIDFUEL, 1) + " LF   " AT(0, 42).
        WAIT 0.2.
    }
    LOCK THROTTLE TO 0.0.
    PRINT "Etapa superior desorbitada! Amaratge segur a l'oceà.".

} ELSE {
    PRINT "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".
    PRINT "ALERTA DE SEGURETAT DE MISSIONS CSA:".
    PRINT "L'angle de fase (" + ROUND(final_phase, 2) + "º) NO ESTÀ entre " + MIN_ACCEPTABLE_PHASE + "º i " + MAX_ACCEPTABLE_PHASE + "º!".
    PRINT "DESACOBLAMENT CANCEL·LAT PER EVITAR DEIXAR EL SATÈL·LIT EN ÒRBITA INCORRECTA.".
    PRINT "El satèl·lit es manté acoblat a l'etapa superior per a poder fer un reajust posterior.".
    PRINT "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!".
}

UNLOCK STEERING.
UNLOCK THROTTLE.
SET SHIP:CONTROL:PILOTMAINTHROTTLE TO 0.
PRINT "Programa csa13_phasing finalitzat.".

// ----------------------------------------------------------------------------
// Funcions de Suport
// ----------------------------------------------------------------------------
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
    PRINT "EXECUTANT DESACOBLAMENT DE COROLTSAT-1C...".
    LOCAL separated IS FALSE.

    // 1. Desencadenar directament per mòdul ModuleDecouple
    FOR part_item IN SHIP:PARTS {
        IF part_item:HASMODULE("ModuleDecouple") {
            LOCAL part_mod IS part_item:GETMODULE("ModuleDecouple").
            // Execució directa d'acció d'enginyeria
            IF part_mod:HASACTION("DecoupleAction") {
                part_mod:DOACTION("DecoupleAction", TRUE).
                SET separated TO TRUE.
                PRINT "  -> DecoupleAction executada a " + part_item:NAME.
            }
            // Execució d'esdeveniments en qualsevol idioma (anglès/català/castellà)
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

    // 2. Comanda addicional de Staging per redundància total
    STAGE.
    WAIT 0.5.
    STAGE.

    PRINT "Comanda de desacoblament enviada i confirmada!".
    PRINT "--------------------------------------------------".
}

FUNCTION ensure_engines_active {
    LOCAL eng_list IS LIST().
    LIST ENGINES IN eng_list.
    FOR e_item IN eng_list {
        e_item:ACTIVATE().
        PRINT "  -> Motor activat i armat: " + e_item:NAME.
    }
}
