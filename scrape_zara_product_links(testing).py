import asyncio
import json
import os
from playwright.async_api import async_playwright

def save_nested_links(gender, category, new_links, filename="clothes.json"):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Warning: JSON file is corrupted or empty. Starting fresh.")
                data = {}
    else:
        data = {}

    if gender not in data:
        data[gender] = {}
    data[gender][category] = list(set(new_links))  # ensure no duplicates

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved {len(new_links)} links under {gender} → {category}")

async def scrape_zara_product_links(category_url, gender, category, output_file="clothes.json"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(category_url)
        await page.wait_for_timeout(2000)

        # Scroll to load all products
        for i in range(0, 1000000, 1000):
            await page.evaluate(f"window.scrollTo(0, {i})")
            #await page.wait_for_timeout(1000)

        anchors = await page.query_selector_all("a[href*='/in/en/'][href*='p0']")
        links = []

        print(f"Found {len(anchors)} anchor tags matching pattern...")

        for a in anchors:
            href = await a.get_attribute("href")
            if href and href.startswith("https://www.zara.com/in/en/") and "p0" in href:
                full_link = href.split("?")[0]
                links.append(full_link)

        links = list(set(links))  # remove duplicates
        save_nested_links(gender, category, links, output_file)
        await browser.close()

# Example usage
category_page_url = "https://www.zara.com/in/en/woman-dresses-l1066.html"
asyncio.run(scrape_zara_product_links(category_page_url, gender="women", category="dresses"))
