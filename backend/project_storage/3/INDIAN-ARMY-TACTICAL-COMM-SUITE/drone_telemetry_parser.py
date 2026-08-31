# INDIAN ARMED FORCES UAV TELEMETRY ROUTER
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
