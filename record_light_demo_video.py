"""
High-Resolution Light Mode 60-Second Demo Video Recorder for AI-KAVACH Hackathon.
Operates in pristine Light Mode, executing a rapid, high-impact walkthrough of:
1. Sovereign Login (major_kavach)
2. Tactical Dashboard Overview
3. Kavach CRS 5-Stage Autonomous Execution
4. Unified Git Diff & Dual-Gate Proof Verification
5. Security Knowledge Graph & Agent Mesh
6. Cryptographic Certificate Vault
Target Length: ~45-50 Seconds (Under 1 Minute).
"""

import os
import time
import cv2
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "e:/CyberLens/CYBERLENS--main/demo_video_recordings"
FINAL_MP4_PATH = "e:/CyberLens/CYBERLENS--main/AI_KAVACH_Demo_Walkthrough.mp4"
FINAL_WEBM_PATH = "e:/CyberLens/CYBERLENS--main/AI_KAVACH_Demo_Walkthrough.webm"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def record_light_demo():
    print("[*] Launching Light-Mode Video Capture Session (< 60s target)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=OUTPUT_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        # Pre-set light theme in localStorage
        page.add_init_script("""
            localStorage.setItem('cyberlens_theme', 'light');
            document.documentElement.dataset.theme = 'light';
        """)

        # 1. Login Screen (0 - 6s)
        print("[1/6] Navigating to Login Page (Light Mode)...")
        page.goto("http://127.0.0.1:5173/login", wait_until="networkidle")
        page.evaluate("document.documentElement.dataset.theme = 'light'")
        page.wait_for_timeout(1000)

        # Type credentials with smooth pacing
        page.fill("input[name='username'], input[type='text']", "major_kavach")
        page.wait_for_timeout(600)
        page.fill("input[name='password'], input[type='password']", "KavachSecure@2026")
        page.wait_for_timeout(800)
        page.click("button[type='submit']")
        page.wait_for_timeout(2000)

        # 2. Dashboard Screen (6 - 12s)
        print("[2/6] Inspecting Tactical Dashboard...")
        page.evaluate("document.documentElement.dataset.theme = 'light'")
        page.wait_for_timeout(1500)
        page.mouse.wheel(0, 350)
        page.wait_for_timeout(1200)
        page.mouse.wheel(0, -350)
        page.wait_for_timeout(800)

        # 3. Kavach CRS Flagship Studio (12 - 32s)
        print("[3/6] Navigating to Kavach CRS...")
        crs_link = page.locator("a:has-text('Kavach CRS')").first
        if crs_link.count() > 0:
            crs_link.click()
        else:
            page.goto("http://127.0.0.1:5173/kavach-crs", wait_until="networkidle")
        page.wait_for_timeout(1500)

        # Trigger Autonomous Run
        print("   -> Executing Autonomous CRS Run...")
        execute_btn = page.locator("button:has-text('EXECUTE AUTONOMOUS CRS RUN')").first
        if execute_btn.count() > 0:
            execute_btn.click()
            # Fast-forward wait through 5 stages
            for _ in range(8):
                page.wait_for_timeout(1000)

        # Scroll to inspect Git Diff and Proof Cards
        page.mouse.wheel(0, 450)
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, 450)
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, -900)
        page.wait_for_timeout(1000)

        # 4. Security Knowledge Graph Tab (32 - 38s)
        print("[4/6] Demonstrating Security Knowledge Graph...")
        kg_tab = page.locator("button:has-text('Security Knowledge Graph')").first
        if kg_tab.count() > 0:
            kg_tab.click()
            page.wait_for_timeout(2500)

        # 5. Agent Mesh Tab (38 - 44s)
        print("[5/6] Demonstrating Collaborative Agent Mesh...")
        mesh_tab = page.locator("button:has-text('Collaborative Agent Mesh')").first
        if mesh_tab.count() > 0:
            mesh_tab.click()
            page.wait_for_timeout(2500)

        # 6. Proof-of-Fix Certificate Vault Tab (44 - 50s)
        print("[6/6] Demonstrating Certificate Vault...")
        vault_tab = page.locator("button:has-text('Proof-of-Fix Certificate Vault')").first
        if vault_tab.count() > 0:
            vault_tab.click()
            page.wait_for_timeout(3000)

        print("[*] Recording complete. Finalizing video file...")
        page.close()
        video_path = page.video.path()
        context.close()
        browser.close()

        # Copy / Transcode Video
        if os.path.exists(video_path):
            import shutil
            shutil.copy2(video_path, FINAL_WEBM_PATH)
            print(f"[SUCCESS] Saved Light-Mode WebM to: {FINAL_WEBM_PATH}")

            print("[*] Transcoding to MP4...")
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1920
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1080
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(FINAL_MP4_PATH, fourcc, fps, (width, height))

            frameCount = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
                frameCount += 1

            cap.release()
            out.release()
            duration_sec = frameCount / fps if fps > 0 else 0
            print(f"[SUCCESS] Light-Mode MP4 Video Generated ({frameCount} frames, ~{duration_sec:.1f}s) at: {FINAL_MP4_PATH}")

if __name__ == "__main__":
    record_light_demo()
