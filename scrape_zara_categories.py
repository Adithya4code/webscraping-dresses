import asyncio
from playwright.async_api import async_playwright

async def scrape_zara_categories(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(4000)  # Adjust the time for page to load
        count = 0
        # Select all category links (you may need to inspect the HTML structure)
        category_elements = await page.query_selector_all('a[href*="/in/en/"]')

        # Extract the href from each link
        categories = []
        for element in category_elements:
            href = await element.get_attribute('href')
            if href:
                count+=1
                categories.append(href)

        # Filter unique category URLs and exclude duplicates
        categories = list(set(categories))
        print(count)
        await browser.close()
        return categories

# Example usage
url = "https://www.zara.com/in/en"  # Zara homepage URL
categories = asyncio.run(scrape_zara_categories(url))

with open("zara_urls(unfiltered).txt", "w") as f:
    f.write(",\n".join([f'"{cat}"' for cat in categories]))
