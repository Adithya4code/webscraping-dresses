# To run this code, install Playwright:
# pip install playwright
# playwright install
#
# This script scrapes dress images from a Zara product page using Playwright for
# browser automation and Requests for downloading images. It handles dynamic content,
# lazy loading, and placeholder images (e.g., transparent-background.png) by checking
# multiple attributes (src, data-src, srcset, <source> tags). The CSS selector is based
# on the provided structure, looping through nth-child indices to fetch all images.

import os
import requests
from playwright.sync_api import sync_playwright


def download_image(url, filename):
    """Download an image from a URL and save it to a file.

    Args:
        url (str): The image URL to download.
        filename (str): The local path to save the image.
    """
    try:
        # Send a GET request to download the image in chunks
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded {filename}")
        else:
            print(f"Failed to download {url}: Status code {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")


def get_best_url(srcset):
    """Extract the best (last) URL from a srcset attribute.

    Args:
        srcset (str): The srcset attribute value.

    Returns:
        str: The best URL or None if not found.
    """
    if not srcset:
        return None
    sources = [s.strip().split(' ') for s in srcset.split(',')]
    urls = [s[0] for s in sources if s]
    return urls[-1] if urls else None


def scrape_zara_dress_images(product_url, save_dir="zara_dresses"):
    """Scrape dress images from a Zara product page.

    Args:
        product_url (str): The URL of the Zara dress product page.
        save_dir (str): The directory to save downloaded images.
    """
    with sync_playwright() as p:
        # Launch Chromium browser in non-headless mode for visibility
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to the product page and wait for network activity to settle
        page.goto(product_url)
        page.wait_for_load_state('networkidle')

        # Scroll to the bottom to trigger lazy loading of images
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(5000)  # Wait 5 seconds for images to load

        # Click the carousel's "Next" button to load all images
        for _ in range(5):  # Try clicking up to 5 times to cycle through carousel
            try:
                next_button = page.query_selector('[aria-label="Next"]')
                if next_button:
                    next_button.click()
                    page.wait_for_timeout(2000)  # Wait for images to load
                    print("Clicked 'Next' button in carousel.")
            except:
                print("No 'Next' button found or not clickable.")
                break

        # Extract product title for naming files (e.g., from <h1> tag)
        title_element = page.query_selector('h1.product-detail-info__header-name')
        if title_element:
            # Clean title to create a valid filename
            title = title_element.inner_text().strip().replace(' ', '_').lower()
            title = ''.join(c for c in title if c.isalnum() or c == '_')
        else:
            title = "dress"

        # Create save directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)

        # Loop through possible nth-child indices to find images
        max_images = 10  # Adjust based on expected number of images
        for i in range(1, max_images + 1):
            # Construct CSS selector for each image
            css_selector = f'#main .product-detail-view-base-mob .carousel__viewport ul li ul li:nth-child({i}) picture img'
            try:
                img_element = page.query_selector(css_selector)
                if not img_element:
                    print(f"No image found for nth-child({i}).")
                    continue

                # Get potential image URL attributes
                src = img_element.get_attribute('src')
                data_src = img_element.get_attribute('data-src')
                srcset = img_element.get_attribute('srcset')

                # Check <picture> for <source> tags
                picture = img_element.query_selector('xpath=..')  # Get parent <picture>
                img_url = None
                if picture:
                    sources = picture.query_selector_all('source')
                    if sources:
                        source_srcset = sources[0].get_attribute('srcset')
                        img_url = get_best_url(source_srcset)

                # Select the best URL
                if not img_url:
                    if src and "transparent-background.png" not in src:
                        img_url = src
                    elif data_src:
                        img_url = data_src
                    elif srcset:
                        img_url = get_best_url(srcset)

                if img_url:
                    # Ensure the URL is complete
                    if not img_url.startswith('http'):
                        img_url = f"{img_url}"
                    # Download the image with a unique filename
                    filename = os.path.join(save_dir, f"{title}_{i}.jpg")
                    download_image(img_url, filename)
                else:
                    print(f"No valid URL found for image {i}")

            except Exception as e:
                print(f"Error processing image {i} with selector {css_selector}: {e}")

        # Save page source and screenshot for debugging if needed
        if not page.query_selector('#main .product-detail-view-base-mob .carousel__viewport'):
            print("Carousel not found. Saving page source for inspection.")
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            page.screenshot(path="page_screenshot.png")

        # Close the browser
        browser.close()


if __name__ == "__main__":
    # Use the Zara dress product page URL
    product_url = "https://www.zara.com/in/en/zw-collection-crochet-shirt-p04786042.html"
    scrape_zara_dress_images(product_url)