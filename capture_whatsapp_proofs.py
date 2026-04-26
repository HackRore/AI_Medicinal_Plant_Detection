import asyncio
import os
from playwright.async_api import async_playwright

async def capture_proofs():
    IMAGE_DIR = r"C:\Users\HackRore\OneDrive\Desktop\Temp testing Leaf Images"
    OUT_DIR = r"d:\PROJECT FINAL\screenshots"
    os.makedirs(OUT_DIR, exist_ok=True)
    
    images = [
        {"file": "WhatsApp Image 2026-04-27 at 00.09.18.jpeg", "name": "whatsapp_guava"},
        {"file": "WhatsApp Image 2026-04-27 at 00.09.43.jpeg", "name": "whatsapp_ganike"},
        {"file": "WhatsApp Image 2026-04-27 at 00.09.8.jpeg", "name": "whatsapp_bamboo"},
        {"file": "WhatsApp Image 2026-04-27 at 00.10.37.jpeg", "name": "whatsapp_tulsi"}
    ]
    
    async with async_playwright() as p:
        print("Launching Neural Monitor...")
        browser = await p.chromium.launch(headless=True)
        # Use a realistic desktop user agent
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()
        
        for img in images:
            path = os.path.join(IMAGE_DIR, img["file"])
            if not os.path.exists(path):
                print(f"Skipping {img['file']} - Not found")
                continue
                
            print(f"Testing {img['file']} on Live Monolith...")
            await page.goto("https://plantoai.vercel.app/predict", wait_until="networkidle")
            
            # Target the hidden file input
            await page.set_input_files('input[type="file"]', path)
            
            print("  Analyzing Neural Features...")
            try:
                # Wait for the plant name header in PredictResult.tsx
                # It uses <h2 className="text-4xl sm:text-6xl font-black text-white uppercase tracking-tighter leading-none">
                await page.wait_for_selector("h2.text-4xl", timeout=60000)
                await asyncio.sleep(5) # Wait for animations and high-res image load
                
                screenshot_path = os.path.join(OUT_DIR, f"{img['name']}.png")
                # Scroll to the result section
                await page.evaluate("document.querySelector('h2.text-4xl').scrollIntoView()")
                await asyncio.sleep(1)
                
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"  SUCCESS Captured: {screenshot_path}")
            except Exception as e:
                print(f"  FAILED to capture {img['file']}: {e}")
                
        await browser.close()
        print("\nAll proofs captured.")

if __name__ == "__main__":
    asyncio.run(capture_proofs())
