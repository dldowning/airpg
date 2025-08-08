from playwright.sync_api import sync_playwright

def run(playwright):
    # Windows PC emulation
    try:
        print("Testing on Windows PC...")
        browser_pc = playwright.chromium.launch(headless=True)
        context_pc = browser_pc.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page_pc = context_pc.new_page()
        page_pc.goto("http://localhost:4001")
        page_pc.wait_for_load_state("networkidle")
        page_pc.wait_for_timeout(2000) # wait for 2 seconds
        page_pc.wait_for_selector("#inputfield")
        voice_toggle_pc = page_pc.locator("#voice-toggle")
        mic_button_pc = page_pc.locator("#mic-button")
        if not voice_toggle_pc.is_visible():
            raise Exception("Voice toggle switch not found on Windows PC")
        if not mic_button_pc.is_visible():
            raise Exception("Microphone button not found on Windows PC")
        page_pc.screenshot(path="jules-scratch/verification/verification_windows.png")
        print("Windows PC verification successful!")
        browser_pc.close()
    except Exception as e:
        print(f"An error occurred during Windows PC verification: {e}")
        page_pc.screenshot(path="jules-scratch/verification/error_windows.png")
        browser_pc.close()


    # Android device emulation
    try:
        print("\nTesting on Android device...")
        pixel_5 = playwright.devices['Pixel 5']
        browser_android = playwright.chromium.launch(headless=True)
        context_android = browser_android.new_context(**pixel_5)
        page_android = context_android.new_page()
        page_android.goto("http://localhost:4001")
        page_android.wait_for_load_state("networkidle")
        page_android.wait_for_timeout(2000) # wait for 2 seconds
        page_android.wait_for_selector("#inputfield")
        voice_toggle_android = page_android.locator("#voice-toggle")
        mic_button_android = page_android.locator("#mic-button")
        if not voice_toggle_android.is_visible():
            raise Exception("Voice toggle switch not found on Android")
        if not mic_button_android.is_visible():
            raise Exception("Microphone button not found on Android")
        page_android.screenshot(path="jules-scratch/verification/verification_android.png")
        print("Android verification successful!")
        browser_android.close()
    except Exception as e:
        print(f"An error occurred during Android verification: {e}")
        page_android.screenshot(path="jules-scratch/verification/error_android.png")
        browser_android.close()


with sync_playwright() as playwright:
    run(playwright)
