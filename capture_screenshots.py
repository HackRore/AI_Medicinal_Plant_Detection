import asyncio
from playwright.async_api import async_playwright

async def take_screenshots():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        routes = [
            {"path": "/", "name": "home"},
            {"path": "/predict", "name": "predict"},
            {"path": "/about", "name": "about"},
            {"path": "/symptom-search", "name": "symptom_search"},
            {"path": "/plants", "name": "plants"}
        ]
        
        base_url = "https://plantoai.vercel.app"
        
        for route in routes:
            url = base_url + route["path"]
            print(f"Capturing {url} ...")
            await page.goto(url, wait_until="networkidle")
            # Wait a bit for animations
            await asyncio.sleep(2)
            await page.screenshot(path=f"screenshots/{route['name']}.png", full_page=True)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(take_screenshots())
