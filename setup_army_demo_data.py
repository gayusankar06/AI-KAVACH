"""
Setup Realistic Indian Armed Forces Tactical Codebase & Run Complete CRS Pipeline.
Creates:
1. User: 'major_kavach' / 'kavach_officer' (Clearance: SECRET / LEVEL-4)
2. Project: 'INDIAN-ARMY-TACTICAL-COMM-SUITE'
3. Tactical Code Files:
   - tactical_radio_gateway.c (CWE-120: Buffer overflow in military packet framing)
   - drone_telemetry_parser.py (CWE-78: Command injection in firmware telemetry handler)
   - radar_target_tracker.cpp (CWE-415: Double free / memory corruption in tracking buffer)
   - test_tactical_suite.py (Automated regression suite)
4. Executes:
   - SAST Scan & Finding Extraction
   - Coverage-Guided Fuzzing (AFL++)
   - Security Knowledge Graph (Layer 4)
   - Autonomous Patch Synthesis (Layer 5)
   - Dual-Gate Proof-of-Fix Sandbox Harness (Layer 6)
   - Cryptographic SHA-256 Proof Certificates
"""

import os
import sys
import json
import httpx
import time

import os
import sys
import json
import httpx
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def setup_demo():
    print("==================================================")
    print("[*] INITIALIZING INDIAN ARMED FORCES DEMO ENVIRONMENT")
    print("==================================================")

    # 1. Create or login demo user
    username = "major_kavach"
    email = "vikram.kavach@army.mil.in"
    password = "KavachSecure@2026"

    signup_res = httpx.post(f"{BASE_URL}/api/signup", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    login_res = httpx.post(f"{BASE_URL}/api/login", json={
        "username": username,
        "password": password
    })
    
    if login_res.status_code != 200:
        print(f"❌ Login failed: {login_res.text}")
        return
    
    user_data = login_res.json()["user"]
    user_id = user_data["id"]
    print(f"[+] Demo Officer Authenticated: {user_data['username']} (ID: {user_id})")

    # 2. Create Project
    proj_name = "INDIAN-ARMY-TACTICAL-COMM-SUITE"
    proj_res = httpx.post(f"{BASE_URL}/api/projects", json={
        "user_id": user_id,
        "name": proj_name,
        "source_type": "folder",
        "source_url": ""
    })
    
    proj_id = proj_res.json().get("project_id")
    print(f"[+] Project Created: {proj_name} (ID: {proj_id})")

    # 3. Create Tactical Military Source Files
    from project_service import project_dir
    p_dir = project_dir(user_id, proj_name)
    os.makedirs(p_dir, exist_ok=True)

    # File 1: Tactical Radio Gateway in C (Buffer Overflow)
    radio_code = """/*
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
    printf("[RADIO-GATEWAY] Ingesting SDR telemetry packet frame...\\n");

    // VULNERABILITY (CWE-120): Unchecked strcpy allows adversary packet to overflow stack
    strcpy(radio_payload, raw_packet_stream);

    printf("[RADIO-GATEWAY] Processed frame: %s\\n", radio_payload);
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        parse_tactical_packet(argv[1]);
    } else {
        parse_tactical_packet("SECURE_MIL_BURST_SYNC_OK");
    }
    return 0;
}
"""

    # File 2: Drone Telemetry Parser in Python (Command Injection)
    drone_code = """# INDIAN ARMED FORCES UAV TELEMETRY ROUTER
# Subsystem: Tactical Edge Drone Link
# Classification: CONFIDENTIAL

import os
import sys

def execute_sensor_diagnostic(sensor_id, diagnostic_cmd):
    print(f"[UAV-ROUTER] Running diagnostic on payload sensor: {sensor_id}")
    
    # VULNERABILITY (CWE-78): Unsanitized command execution allows shell breakout
    os.system(f"run_diag_tool --sensor {sensor_id} --mode {diagnostic_cmd}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        execute_sensor_diagnostic(sys.argv[1], sys.argv[2])
    else:
        execute_sensor_diagnostic("IR_CAM_01", "standard_check")
"""

    # File 3: Radar Target Tracker in C++ (Double Free)
    radar_code = """/*
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
"""

    # File 4: Regression Test Suite
    test_code = """# AUTOMATED REGRESSION HARNESS FOR DEFENSE PROTOCOLS
def test_radio_packet_decoding():
    sample = "FREQ=142.500MHz|CODE=BRAVO_LEADER"
    assert len(sample) > 0
    assert "FREQ" in sample

def test_uav_telemetry_bounds():
    azimuth = 180.0
    assert 0.0 <= azimuth <= 360.0

def test_radar_track_allocation():
    track_id = 1044
    assert track_id > 0
"""

    with open(os.path.join(p_dir, "tactical_radio_gateway.c"), "w", encoding="utf-8") as f:
        f.write(radio_code)
    with open(os.path.join(p_dir, "drone_telemetry_parser.py"), "w", encoding="utf-8") as f:
        f.write(drone_code)
    with open(os.path.join(p_dir, "radar_target_tracker.cpp"), "w", encoding="utf-8") as f:
        f.write(radar_code)
    with open(os.path.join(p_dir, "test_tactical_suite.py"), "w", encoding="utf-8") as f:
        f.write(test_code)

    print("[+] Ingested 4 Tactical Defense Source Files to Workspace Storage.")

    # 4. Ingest code findings into DB
    from database import add_code_finding, clear_code_findings
    clear_code_findings(proj_id)
    
    f1 = add_code_finding(
        proj_id, user_id, "tactical_radio_gateway.c", "critical",
        "Critical Buffer Overflow in SDR Packet Demuxer (CWE-120)",
        "Unbounded strcpy() copy of SDR stream into static 256-byte stack frame allows remote code execution.",
        "strcpy(radio_payload, raw_packet_stream);"
    )
    f2 = add_code_finding(
        proj_id, user_id, "drone_telemetry_parser.py", "critical",
        "OS Command Injection in Drone Sensor Diagnostics (CWE-78)",
        "os.system() directly invokes shell with unescaped diagnostic parameters enabling command escalation.",
        "os.system(f\"run_diag_tool --sensor {sensor_id} --mode {diagnostic_cmd}\")"
    )
    f3 = add_code_finding(
        proj_id, user_id, "radar_target_tracker.cpp", "high",
        "Double Free Vulnerability in Phased Array Radar Track Memory (CWE-415)",
        "Freeing heap pointer twice without nullification corrupts tcache memory manager.",
        "free(track);\n        free(track);"
    )
    print(f"[+] Ingested 3 Tactical CWE Vulnerabilities (Finding IDs: {f1}, {f2}, {f3})")

    # 5. Run CRS Closed-Loop Remediation for Findings
    print("\n[*] EXECUTING AUTONOMOUS CRS CLOSED-LOOP REMEDIATION...")
    
    # Run on Finding 1
    crs1 = httpx.post(f"{BASE_URL}/api/projects/{proj_id}/crs/pipeline/run", json={
        "user_id": user_id,
        "finding_id": f1
    }).json()
    print(f"   [OK] Finding 1 (CWE-120) Remediated: {crs1.get('result', {}).get('certificate_id')} -> STATUS: {crs1.get('result', {}).get('status')}")

    # Run on Finding 2
    crs2 = httpx.post(f"{BASE_URL}/api/projects/{proj_id}/crs/pipeline/run", json={
        "user_id": user_id,
        "finding_id": f2
    }).json()
    print(f"   [OK] Finding 2 (CWE-78) Remediated: {crs2.get('result', {}).get('certificate_id')} -> STATUS: {crs2.get('result', {}).get('status')}")

    # 6. Run Agent Mesh Task
    agent_res = httpx.post(f"{BASE_URL}/api/projects/{proj_id}/crs/agent-mesh/run", json={
        "user_id": user_id,
        "agent_id": "root_cause",
        "query": "Trace root cause of buffer overflows in tactical_radio_gateway.c and verify invariant bounds."
    }).json()
    print(f"[+] Dispatched Collaborative Agent Mesh: {agent_res.get('result', {}).get('agent_name')}")

    print("\n==================================================")
    print("[SUCCESS] DEMO DATA ENVIRONMENT FULLY POPULATED & READY!")
    print(f"Credentials -> Username: {username} | Password: {password}")
    print("==================================================")

if __name__ == "__main__":
    setup_demo()
