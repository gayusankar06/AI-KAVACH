"""
Automated High-Resolution Demo Video Recorder for AI-KAVACH Hackathon Submission.
Logs into the live running web application as 'major_kavach', executes the autonomous CRS run,
demonstrates the Security Knowledge Graph, Agent Mesh, Certificate Vault, and Code Security.
Produces a crisp HD video file (AI_KAVACH_Demo_Walkthrough.webm / .mp4).
"""

import os
import time
import cv2
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "e:/CyberLens/CYBERLENS--main/demo_video_recordings"
FINAL_MP4_PATH = "e:/CyberLens/CYBERLENS--main/AI_KAVACH_Demo_Walkthrough.mp4"
FINAL_WEBM_PATH = "e:/CyberLens/CYBERLENS--main/AI_KAVACH_Demo_Walkthrough.webm"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def record_demo():
    print("[*] Starting Playwright Video Capture Session...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=OUTPUT_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        # Step 1: Open Login Page
        print("[1/8] Navigating to Login Page...")
        page.goto("http://127.0.0.1:5173/login", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Step 2: Fill in Credentials
        print("[2/8] Entering Demo Officer Credentials (major_kavach)...")
        page.fill("input[name='username'], input[type='text']", "major_kavach")
        page.wait_for_timeout(1000)
        page.fill("input[name='password'], input[type='password']", "KavachSecure@2026")
        page.wait_for_timeout(1500)
        
        # Click Sign In
        print("[3/8] Signing In...")
        page.click("button[type='submit']")
        page.wait_for_timeout(3000)

        # Step 3: Dashboard Overview
        print("[4/8] Inspecting Tactical Dashboard...")
        page.wait_for_timeout(3000)
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, -400)
        page.wait_for_timeout(1500)

        # Step 4: Navigate to Kavach CRS Flagship Studio
        print("[5/8] Navigating to Kavach CRS Flagship Studio...")
        crs_link = page.locator("a:has-text('Kavach CRS'), button:has-text('Kavach CRS')").first
        if crs_link.count() > 0:
            crs_link.click()
        else:
            page.goto("http://127.0.0.1:5173/kavach-crs", wait_until="networkidle")
        page.wait_for_timeout(3000)

        # Step 5: Execute Autonomous CRS Run
        print("[6/8] Executing Autonomous Closed-Loop CRS Run...")
        execute_btn = page.locator("button:has-text('EXECUTE AUTONOMOUS CRS RUN')").first
        if execute_btn.count() > 0:
            execute_btn.click()
            print("   -> Triggered CRS Run. Awaiting 5-stage closed loop execution...")
            # Wait for execution stages to animate
            for i in range(12):
                page.wait_for_timeout(1000)
                print(f"      ... Stage progress: {i+1}s")

        # Scroll to inspect Git Diff and Dual-Gate status
        page.mouse.wheel(0, 500)
        page.wait_for_timeout(3000)
        page.mouse.wheel(0, 500)
        page.wait_for_timeout(3000)
        page.mouse.wheel(0, -1000)
        page.wait_for_timeout(1500)

        # Step 6: Security Knowledge Graph Tab
        print("[7/8] Demonstrating Security Knowledge Graph...")
        kg_tab = page.locator("button:has-text('Security Knowledge Graph')").first
        if kg_tab.count() > 0:
            kg_tab.click()
            page.wait_for_timeout(3500)
            page.mouse.wheel(0, 300)
            page.wait_for_timeout(2000)

        # Step 7: Collaborative Agent Mesh Tab
        print("[8/8] Demonstrating Agent Mesh & Certificate Vault...")
        mesh_tab = page.locator("button:has-text('Collaborative Agent Mesh')").first
        if mesh_tab.count() > 0:
            mesh_tab.click()
            page.wait_for_timeout(3000)

        # Step 8: Certificate Vault Tab
        vault_tab = page.locator("button:has-text('Proof-of-Fix Certificate Vault')").first
        if vault_tab.count() > 0:
            vault_tab.click()
            page.wait_for_timeout(3500)

        # Final view: Code Security Console
        page.goto("http://127.0.0.1:5173/code-security", wait_until="networkidle")
        page.wait_for_timeout(4000)

        print("[*] Wrapping up video recording session...")
        page.close()
        video_path = page.video.path()
        context.close()
        browser.close()

        print(f"[+] Raw Playwright Video Saved at: {video_path}")

        # Copy / Convert to Final WebM & MP4
        if os.path.exists(video_path):
            import shutil
            shutil.copy2(video_path, FINAL_WEBM_PATH)
            print(f"[SUCCESS] Copied WebM to: {FINAL_WEBM_PATH}")

            # Transcode to MP4 using OpenCV
            print("[*] Transcoding WebM to High-Compatibility MP4...")
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
            print(f"[SUCCESS] MP4 Video Generated ({frameCount} frames) at: {FINAL_MP4_PATH}")

if __name__ == "__main__":
    record_demo()
