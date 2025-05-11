import asyncio
import re
import os
import aiohttp
from urllib.parse import urlparse
from playwright.async_api import async_playwright

# Helper functions
def extract_base_name(alt_text):
    # Remove "by Zara" (case-insensitive) and extra spaces
    alt_clean = re.sub(r"(?i)\s*by\s+Zara", "", alt_text)
    alt_clean = re.sub(r"(?i)\s*Image\s*\d+", "", alt_clean)
    alt_clean = alt_clean.strip().replace("-", " ").replace(" ", "_")
    if not alt_clean.endswith("_"):
        alt_clean += "_"

    return f"{alt_clean}"

def extract_filename_from_src(src):
    clean_src = src.split("?")[0]
    return os.path.basename(urlparse(clean_src).path)

async def download_image(session, url, folder, filename):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    async with session.get(url) as response:
        if response.status == 200:
            with open(filepath, 'wb') as f:
                f.write(await response.read())
            print(f"Saved: {filename}")
        else:
            print(f"Failed to download: {url}")

async def scrape_filtered_zara_images(url, folder="downloaded_images"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)

        # Scroll to trigger lazy loading
        for i in range(0, 5000, 500):
            await page.evaluate(f"window.scrollTo(0, {i})")
            await page.wait_for_timeout(1000)

        images = await page.query_selector_all("img")
        print(f"Total <img> tags found: {len(images)}")

        image_links = []
        image_filenames = set()

        pattern_alt = re.compile(r"Image\s+\d+", re.IGNORECASE)
        pattern_ult = re.compile(r"ult\d+\.(jpg|jpeg|png|webp)$", re.IGNORECASE)
        pattern_e = re.compile(r"e\d+\.(jpg|jpeg|png|webp)$", re.IGNORECASE)

        for img in images:
            src = await img.get_attribute("src") or await img.get_attribute("data-src") or await img.get_attribute("srcset")
            alt = await img.get_attribute("alt") or ""
            if src and pattern_alt.search(alt):
                print(f"ALT OK: {alt} | SRC: {src}")
                clean_src = src.split("?")[0]
                if pattern_e.search(clean_src) or pattern_ult.search(clean_src):
                    base = extract_base_name(alt)
                    file = extract_filename_from_src(src)
                    filename = f"{base}_{file}"
                    if filename not in image_filenames:
                        image_links.append((src, filename))
                        image_filenames.add(filename)

        # Fallback
        if len(image_links) < 2:
            print("Fewer than 2 'Image <number>' matches found. Checking fallback rules...")
            for img in images:
                src = await img.get_attribute("src") or await img.get_attribute("data-src") or await img.get_attribute("srcset")
                if not src:
                    continue
                if pattern_ult.search(src):
                    file = extract_filename_from_src(src)
                    if file not in image_filenames:
                        image_links.append((src, file))
                        image_filenames.add(file)

        # Download
        async with aiohttp.ClientSession() as session:
            for src, filename in image_links:
                await download_image(session, src, folder, filename)

        await browser.close()

# Run the function
asyncio.run(scrape_filtered_zara_images("https://www.zara.com/in/en/z1975-denim-globo-bomber-jacket-p02152576.html?v1=419600672&v2=2417772"))