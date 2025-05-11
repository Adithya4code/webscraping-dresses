import asyncio
import json
from playwright.async_api import async_playwright

CONCURRENT_TASKS = 4  # Adjust based on system/network


async def scrape_links_from_category(sem, url, gender, category, browser, output_file, results):
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

            # Update the results dictionary with the new links
            results[gender][category] = list(links)

            # Write the updated results to the JSON file immediately
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            print(f"📝 Updated {output_file} with links for {gender} → {category}")

            return gender, category, list(links)
        except Exception as e:
            print(f"⚠️ Failed {gender} → {category}: {e}")
            return gender, category, []
        finally:
            await page.close()


async def main(categories_file="zara_categories.json", output_file="zara_product_links.json"):
    # Load the categories JSON file
    with open(categories_file, "r") as f:
        categories = json.load(f)

    # Initialize the results dictionary
    results = {gender: {} for gender in categories}

    # Check if output file already exists; if so, load its contents to resume
    try:
        with open(output_file, "r") as f:
            existing_results = json.load(f)
            for gender in results:
                if gender in existing_results:
                    results[gender] = existing_results[gender]
    except FileNotFoundError:
        pass  # File doesn't exist yet, start fresh

    sem = asyncio.Semaphore(CONCURRENT_TASKS)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        tasks = []

        for gender, cat_map in categories.items():
            for category, url in cat_map.items():
                # Skip if this category was already fully processed
                if gender in results and category in results[gender] and results[gender][category]:
                    print(f"⏭️ Skipping {gender} → {category} (already processed)")
                    continue
                tasks.append(scrape_links_from_category(sem, url, gender, category, browser, output_file, results))

        if tasks:
            await asyncio.gather(*tasks)
        else:
            print("ℹ️ No new categories to process.")

        await browser.close()

    print(f"\n🎉 All product links saved to {output_file}")


# Run the scraper
asyncio.run(main())