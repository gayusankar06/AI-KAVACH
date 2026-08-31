/*
 * AIR DEFENSE RADAR TARGET TRACKER
 * Subsystem: Phased Array Track Initiator
 */
#include <iostream>
#include <cstdlib>

struct TrackObject {
    int target_id;
    double azimuth;
    double elevation;
};

void cleanup_track(TrackObject* track) {
    if (track != nullptr) {
        free(track);
        // VULNERABILITY (CWE-415): Missing null assignment causes double-free on abort
        free(track);
    }
}

int main() {
    TrackObject* t = (TrackObject*)malloc(sizeof(TrackObject));
    t->target_id = 901;
    t->azimuth = 45.2;
    t->elevation = 12.8;
    cleanup_track(t);
    return 0;
}
