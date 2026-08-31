/*
 * INDIAN ARMED FORCES TACTICAL COMMUNICATIONS GATEWAY
 * Subsystem: VHF/UHF SDR Packet Demuxer
 * Classification: RESTRICTED
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_BUFFER 256

void parse_tactical_packet(const char *raw_packet_stream) {
    char radio_payload[MAX_BUFFER];
    printf("[RADIO-GATEWAY] Ingesting SDR telemetry packet frame...\n");

    // VULNERABILITY (CWE-120): Unchecked strcpy allows adversary packet to overflow stack
    strcpy(radio_payload, raw_packet_stream);

    printf("[RADIO-GATEWAY] Processed frame: %s\n", radio_payload);
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        parse_tactical_packet(argv[1]);
    } else {
        parse_tactical_packet("SECURE_MIL_BURST_SYNC_OK");
    }
    return 0;
}
