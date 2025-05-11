import asyncio
from playwright.async_api import async_playwright

async def scrape_zara_images_smart(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)  # Wait a bit for JS

        # Scroll slowly to load all lazy images
        for i in range(0, 3000, 500):
            await page.evaluate(f"window.scrollTo(0, {i})")
            await page.wait_for_timeout(1000)

        # Grab all image elements
        image_elements = await page.query_selector_all("img")
        print(f"Found {len(image_elements)} images after scrolling.\n")

        for i, img in enumerate(image_elements):
            src = await img.get_attribute("src") or await img.get_attribute("data-src") or await img.get_attribute("srcset")
            alt = await img.get_attribute("alt")
            if src:
                print(f"[{i+1}] src: {src}\n     alt: {alt}")

        await browser.close()

# Test with your URL
asyncio.run(scrape_zara_images_smart("https://www.zara.com/in/en/zw-collection-crochet-shirt-p04786042.html"))