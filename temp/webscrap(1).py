# To run this code, install Playwright:
# pip install playwright
# playwright install
#
# This script scrapes dress images from a Zara product page using Playwright for
# browser automation and Requests for downloading images. It handles dynamic content,
# lazy loading, and placeholder images (e.g., transparent-background.png) by checking
# multiple attributes (src, data-src, srcset, <source> tags).

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


def scrape_zara_dress_images(url, save_dir="zara_dresses"):
    """Scrape dress images from a Zara product page.

    Args:
        url (str): The URL of the Zara dress product page.
        save_dir (str): The directory to save downloaded images.
    """
    with sync_playwright() as p:
        # Launch Chromium browser in non-headless mode for visibility
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to the product page and wait for network activity to settle
        page.goto(url)
        page.wait_for_load_state('networkidle')

        # Scroll to the bottom to trigger lazy loading of images
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(5000)  # Wait 5 seconds for images to load

        # Attempt to click the carousel's "Next" button to load all images
        for _ in range(3):  # Try clicking up to 3 times
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

        # Find all <img> elements within the carousel
        # Selector based on Zara's carousel structure; adjust if needed
        img_elements = page.query_selector_all('div.carousel__viewport img')
        if not img_elements:
            print("No images found in carousel. Inspect page to update selector.")
            # Save page source for debugging
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            page.screenshot(path="page_screenshot.png")
            browser.close()
            return

        # Loop through each image element to extract URLs
        for i, img in enumerate(img_elements, start=1):
            # Get potential image URL attributes
            src = img.get_attribute('src')
            data_src = img.get_attribute('data-src')
            srcset = img.get_attribute('srcset')

            # Select the most likely image URL
            if src and "transparent-background.png" not in src:
                img_url = src
            elif data_src:
                img_url = data_src
            elif srcset:
                # Take the first URL from srcset (often highest quality)
                img_url = srcset.split(',')[0].split()[0].strip()
            else:
                # Check <picture> for <source> tags
                try:
                    picture = img.query_selector('xpath=..')  # Get parent <picture>
                    if picture:
                        sources = picture.query_selector_all('source')
                        if sources:
                            img_url = sources[0].get_attribute('srcset')
                        else:
                            img_url = None
                    else:
                        img_url = None
                except:
                    img_url = None

            if img_url:
                # Ensure the URL is complete
                if not img_url.startswith('http'):
                    img_url = f"https://www.zara.com{img_url}"
                # Download the image with a unique filename
                filename = os.path.join(save_dir, f"{title}_{i}.jpg")
                download_image(img_url, filename)
            else:
                print(f"No valid URL found for image {i}")

        # Close the browser
        browser.close()


# Example usage
if __name__ == "__main__":
    # Use a valid Zara dress product page URL
    # Example: Find a dress URL from https://www.zara.com/us/en/woman-dresses-l1066.html
    product_url = "https://www.zara.com/us/en/printed-dress-p03167109.html"
    scrape_zara_dress_images(product_url)