// ============================================================================
// COROLT SPACE AGENCY (CSA) - REMOTE COMMAND LISTENER DAEMON v1.0
// SCRIPT: remote.ks
// DESCRIPTION:
//   Crash-proof alternative to kOS Telnet on Linux (avoids Mono libKernel32 bug).
//   Polls 0:/remote_cmd.ks every 1.0s, executes incoming commands from external
//   SSH / laptop terminals (tools/csa_remote_terminal.py), and deletes the file.
// ============================================================================

CLEARSCREEN.
PRINT "==================================================".
PRINT "   COROLT SPACE AGENCY - REMOTE COMMAND BRIDGE    ".
PRINT "   STATUS: ONLINE (Listening on 0:/remote_cmd.ks) ".
PRINT "   VESSEL: " + SHIP:NAME.
PRINT "==================================================".
PRINT "Ready to receive commands from laptop SSH terminal!".
PRINT "To exit listener on vessel, send: EXIT_REMOTE".
PRINT "--------------------------------------------------".

SET STOP_REMOTE_BRIDGE TO FALSE.
LOCAL cmd_file IS "0:/remote_cmd.ks".
LOCAL ack_file IS "0:/remote_ack.txt".

IF EXISTS(cmd_file) {
    DELETEPATH(cmd_file).
}

UNTIL STOP_REMOTE_BRIDGE {
    IF HOMECONNECTION:ISCONNECTED AND EXISTS(cmd_file) {
        PRINT "--------------------------------------------------".
        PRINT "[REMOTE UT " + ROUND(TIME:SECONDS, 1) + "s] Executing command from laptop...".
        LOG "START|" + ROUND(TIME:SECONDS, 2) + "|" + SHIP:NAME TO ack_file.
        LOCAL local_cmd IS "1:/exec_remote.ks".
        COPYPATH(cmd_file, local_cmd).
        DELETEPATH(cmd_file).
        RUNPATH(local_cmd).
        IF EXISTS(local_cmd) {
            DELETEPATH(local_cmd).
        }
        IF HOMECONNECTION:ISCONNECTED {
            LOG "DONE|" + ROUND(TIME:SECONDS, 2) + "|Ap=" + ROUND(SHIP:APOAPSIS/1000, 2) + "km|Pe=" + ROUND(SHIP:PERIAPSIS/1000, 2) + "km" TO ack_file.
        }
        PRINT "[REMOTE UT " + ROUND(TIME:SECONDS, 1) + "s] Command execution finished.".
        PRINT "--------------------------------------------------".
    }
    WAIT 1.0.
}

PRINT "CSA Remote Command Bridge stopped.".
