import asyncio
import json
from playwright.async_api import async_playwright

CONCURRENT_TASKS = 4  # Adjust based on system/network

async def scrape_links_from_category(sem, url, gender, category, browser):
    async with sem:
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(4000)

            for i in range(0, 1000000, 1000):
                await page.evaluate(f"window.scrollTo(0, {i})")

            anchors = await page.query_selector_all("a[href*='/in/en/'][href*='p0']")
            links = set()

            for a in anchors:
                if len(links) >= 200:
                    print(f"🔢 Reached link cap (200) for {gender} → {category}")
                    break
                href = await a.get_attribute("href")
                if href and href.startswith("https://www.zara.com/in/en/") and "p0" in href:
                    full_link = href.split("?")[0]
                    links.add(full_link)

            print(f"✅ {len(links)} links found for {gender} → {category}")
            return gender, category, list(links)
        except Exception as e:
            print(f"⚠️ Failed {gender} → {category}: {e}")
            return gender, category, []
        finally:
            await page.close()

async def main(categories_file="zara_categories.json", output_file="zara_product_links(unfiltered"").json"):
    with open(categories_file, "r") as f:
        categories = json.load(f)

    results = {gender: {} for gender in categories}
    sem = asyncio.Semaphore(CONCURRENT_TASKS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        tasks = []

        for gender, cat_map in categories.items():
            for category, url in cat_map.items():
                tasks.append(scrape_links_from_category(sem, url, gender, category, browser))

        all_results = await asyncio.gather(*tasks)

        for gender, category, links in all_results:
            results[gender][category] = links

        await browser.close()

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n🎉 All product links saved to {output_file}")

# Run the scraper
asyncio.run(main())
