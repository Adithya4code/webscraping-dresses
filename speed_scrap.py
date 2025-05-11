import asyncio
import json
import os
import re
from urllib.parse import urlparse
from urllib.parse import urljoin
import aiohttp
from playwright.async_api import async_playwright

SCRAPED_LOG_FILE = "scraped_log.json"
CONCURRENT_TASKS = 8  # Tune based on CPU/network

# Helper functions
def extract_base_name(alt_text):
    alt_clean = re.sub(r"(?i)\s*by\s+Zara", "", alt_text)
    alt_clean = re.sub(r"(?i)\s*Image\s*\d+", "", alt_text)
    alt_clean = alt_clean.strip().replace("-", "").replace(" ", "_")
    if not alt_clean.endswith("_"):
        alt_clean += "_"
    return f"{alt_clean}"

def extract_filename_from_src(src):
    clean_src = src.split("?")[0]
    return os.path.basename(urlparse(clean_src).path)

async def download_image(session, url, folder, filename):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        print(f"⏩ Skipped (already exists): {filename}")
        return
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.zara.com/",
        }
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                with open(filepath, 'wb') as f:
                    f.write(await response.read())
                print(f"✅ Saved: {filename}")
            else:
                print(f"❌ Failed to download ({response.status}): {url}")
    except Exception as e:
        print(f"🚫 Error downloading {url}: {e}")

async def scrape_filtered_zara_images(url, folder, browser):
    page = await browser.new_page()

    await page.route("**/*", lambda route, request: asyncio.create_task(
        route.continue_() if request.resource_type in ["document", "image", "script", "xhr"] else route.abort()
    ))

    try:
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")

        for i in range(0, 20000, 2000):
            await page.evaluate(f"window.scrollTo(0, {i})")
            await page.wait_for_timeout(200)

        images = await page.query_selector_all("img")
        print(f"🔍 Found {len(images)} <img> tags on: {url}")

        image_links = []
        image_filenames = set()

        pattern_alt = re.compile(r"Image\s+\d+", re.IGNORECASE)
        pattern_ult = re.compile(r"ult\d+\.(jpg|jpeg|png|webp)$", re.IGNORECASE)
        pattern_e = re.compile(r"e[12]\.(jpg|jpeg|png|webp)$", re.IGNORECASE)

        for img in images:
            src = await img.get_attribute("src") or await img.get_attribute("data-src") or await img.get_attribute("srcset")
            alt = await img.get_attribute("alt") or ""
            if not src:
                continue
            if "," in src:  # handle srcset
                src = src.split(",")[0].split()[0]
            src = urljoin(url, src)
            clean_src = src.split("?")[0]

            if pattern_alt.search(alt) and (pattern_e.search(clean_src) or pattern_ult.search(clean_src)):
                base = extract_base_name(alt)
                file = extract_filename_from_src(src)
                filename = f"{base}_{file}"
                if filename not in image_filenames:
                    print(f"⬇️ Trying to download: {src}")
                    image_links.append((src, filename))
                    image_filenames.add(filename)

        # Fallback logic if too few images
        if len(image_links) < 2:
            for img in images:
                src = await img.get_attribute("src") or await img.get_attribute("data-src") or await img.get_attribute("srcset")
                if not src:
                    continue
                if "," in src:
                    src = src.split(",")[0].split()[0]
                src = urljoin(url, src)
                clean_src = src.split("?")[0]
                if pattern_ult.search(clean_src):
                    file = extract_filename_from_src(src)
                    if file not in image_filenames:
                        print(f"⬇️ Fallback download: {src}")
                        image_links.append((src, file))
                        image_filenames.add(file)

        async with aiohttp.ClientSession() as session:
            for src, filename in image_links:
                await download_image(session, src, folder, filename)

    finally:
        await page.close()

# Resume support: load & save scraped log
def load_scraped_log():
    if os.path.exists(SCRAPED_LOG_FILE):
        with open(SCRAPED_LOG_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_scraped_log(scraped_set):
    with open(SCRAPED_LOG_FILE, "w") as f:
        json.dump(list(scraped_set), f, indent=2)

async def scrape_with_semaphore(sem, url, folder, browser, scraped_log):
    async with sem:
        print(f"📥 Scraping: {url}")
        try:
            await scrape_filtered_zara_images(url, folder, browser)
            scraped_log.add(url)
        except Exception as e:
            print(f"⚠️ Failed {url}: {e}")

async def scrape_all(data):
    scraped_log = load_scraped_log()
    sem = asyncio.Semaphore(CONCURRENT_TASKS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        tasks = []

        for gender, cat_map in data.items():
            for category, links in cat_map.items():
                folder_path = os.path.join("downloaded_images", gender, category)
                os.makedirs(folder_path, exist_ok=True)

                for url in links:
                    if url in scraped_log:
                        continue
                    tasks.append(
                        scrape_with_semaphore(sem, url, folder_path, browser, scraped_log)
                    )

        await asyncio.gather(*tasks)
        await browser.close()
        save_scraped_log(scraped_log)

async def main(json_file="zara_product_links.json"):
    with open(json_file, "r") as f:
        data = json.load(f)
    await scrape_all(data)

# Run the image scraper
asyncio.run(main())
