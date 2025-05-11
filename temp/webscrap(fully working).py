import asyncio
import re
from playwright.async_api import async_playwright

async def scrape_filtered_zara_images(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)

        # Scroll to trigger lazy loading
        for i in range(0, 3000, 500):
            await page.evaluate(f"window.scrollTo(0, {i})")
            await page.wait_for_timeout(1000)

        images = await page.query_selector_all("img")
        print(f"Total <img> tags found: {len(images)}")

        image_links = []
        pattern_alt = re.compile(r"Image\s+\d+", re.IGNORECASE)
        pattern_ult = re.compile(r"ult\d+\.(jpg|jpeg|png|webp)$", re.IGNORECASE)
        pattern_e = re.compile(r"e\d+\.(jpg|jpeg|png|webp)$", re.IGNORECASE)

        for img in images:
            src = await img.get_attribute("src") or await img.get_attribute("data-src") or await img.get_attribute("srcset")
            alt = await img.get_attribute("alt") or ""
            if src:
                if pattern_alt.search(alt):
                    print(f"ALT OK: {alt} | SRC: {src}")
                    clean_src = src.split("?")[0]
                    if pattern_e.search(clean_src) or pattern_ult.search(clean_src):
                        image_links.append(src)

        # Fallback if not enough alt-pattern matches
        if len(image_links) < 2:
            print("Fewer than 2 'Image <number>' matches found. Checking fallback rules...")
            for img in images:
                src = await img.get_attribute("src") or await img.get_attribute("data-src") or await img.get_attribute("srcset")
                if not src:
                    continue
                if pattern_ult.search(src):
                    image_links.append(src)
                # elif len(image_links) >= 2 and pattern_e.search(src):
                #     image_links.append(src)

        print("\n🎯 Filtered Image Links:")
        for i, link in enumerate(set(image_links)):
            print(f"[{i+1}] {link}")

        await browser.close()

# Run it with your dress product URL
url = "https://www.zara.com/in/en/faux-suede-jacket-p04344622.html?v1=427538567&v2=2417772"
asyncio.run(scrape_filtered_zara_images(url))