# Zara Web Scraping Project

[![GitHub License](https://img.shields.io/github/license/Adithya4code/webscraping-dresses.svg)](https://github.com/Adithya4code/webscraping-dresses/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.52.0-orange.svg)](https://playwright.dev/python/docs/intro)

This repository contains Python scripts for scraping categories, product links, and images from Zara's website, specifically targeting the Indian online store ([Zara India](https://www.zara.com/in/en/)). The project automates the extraction of clothing data for educational and research purposes, producing a dataset available on Kaggle. It uses modern tools like Playwright for robust handling of dynamic content.

**Important**: Before using this project, ensure compliance with Zara's [Terms of Service](https://www.zara.com/in/en/legal-notice.html) and `robots.txt`. Unauthorized scraping may violate legal agreements. This project is intended for non-commercial, educational use only.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Dataset](#dataset)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Project Overview

The Zara Web Scraping Project provides a comprehensive solution for extracting data from Zara's online store. It consists of four Python scripts that work sequentially to:
1. Scrape category URLs from Zara's homepage.
2. Organize categories into a nested JSON structure.
3. Collect product links from each category.
4. Download product images, organized by gender and category.

The project leverages [Playwright](https://playwright.dev/python/docs/intro) for browser automation, handling Zara’s JavaScript-heavy pages, and [Requests](https://requests.readthedocs.io/en/latest/) for efficient image downloads. The output dataset, including images, is hosted on Kaggle for further analysis.

## Features

- **Category Scraping**: Extracts clothing categories (e.g., "woman-tshirts", "man-jeans") from Zara’s homepage.
- **Structured Data**: Organizes categories into a JSON file for easy access.
- **Product Link Extraction**: Scrapes up to 200 product links per category, covering various clothing items.
- **Image Downloading**: Downloads high-quality product images, avoiding placeholders like `transparent-background.png`.
- **Asynchronous Processing**: Uses Playwright’s async API for efficient, concurrent scraping.
- **Error Handling**: Includes robust error handling and logging to manage network issues or DOM changes.
- **Sample Outputs**: Provides sample JSON files (`test_categories.json`, `test_product_links.json`) for reference.

## Project Structure

The repository is organized as follows:

```
webscraping-dresses/
├── LICENSE                    # MIT License file
├── README.md                  # Project documentation
├── requirements.txt           # Required Python dependencies
├── scrape_zara_categories.py  # Script to scrape category URLs
├── create_categories_json.py  # Script to organize categories into JSON
├── scrape_zara_product_links.py  # Script to scrape product links
├── speed_scrap.py             # Script to download product images
├── test_categories.json       # Sample categories JSON
├── test_product_links.json    # Sample product links JSON
├── .gitignore                 # Excludes virtual environments and output files
└── zara_images/               # Directory for downloaded images (created at runtime)
```

- **Scripts**:
  - `scrape_zara_categories.py`: Collects category URLs from Zara’s homepage.
  - `create_categories_json.py`: Structures category URLs into a nested JSON file.
  - `scrape_zara_product_links.py`: Extracts product links from category pages.
  - `speed_scrap.py`: Downloads images from product pages, organizing them by gender and category.
- **Sample Outputs**:
  - `test_categories.json`: Example of organized category URLs (e.g., men’s clothing categories).
  - `test_product_links.json`: Example of scraped product links (e.g., men’s shirts, trousers).
- **Configuration**:
  - `.gitignore`: Excludes `venv/`, `zara_images/`, and other temporary files.
  - `requirements.txt`: Lists essential dependencies like Playwright and Requests.
  - `LICENSE`: Specifies the MIT License for open-source use.

## Prerequisites

To run this project, you need:
- **Python 3.8 or higher**: Download from [Python Downloads](https://www.python.org/downloads/).
- **Playwright**: Installed via `playwright install` for browser automation.
- **Basic Python Knowledge**: Familiarity with Python and web scraping concepts is recommended.
- **Internet Connection**: Required for accessing Zara’s website and downloading images.
- **Compliance Awareness**: Understanding of Zara’s [Terms of Service](https://www.zara.com/in/en/legal-notice.html) to ensure ethical scraping.

## Installation

Follow these steps to set up the project locally:

### Step 1: Clone the Repository
Clone the repository from GitHub:
```bash
git clone https://github.com/Adithya4code/webscraping-dresses.git
cd webscraping-dresses
```

### Step 2: Create a Virtual Environment
Create and activate a virtual environment to isolate dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
Install the required Python packages and Playwright browsers:
```bash
pip install -r requirements.txt
playwright install
```

The `requirements.txt` includes:
- `playwright==1.52.0`: For browser automation.
- `requests==2.32.3`: For image downloads.
- `beautifulsoup4==4.12.3`: Optional, for potential HTML parsing in `speed_scrap.py`.
- Supporting async libraries: `aiohttp`, `yarl`, `multidict`, `frozenlist`, `aiosignal`, `attrs`, `greenlet`, `pyee`.

### Step 4: Verify Setup
Ensure Python and Playwright are installed correctly:
```bash
python --version  # Should output 3.8 or higher
playwright --version  # Should output 1.52.0 or compatible
```

## Usage

The project consists of four scripts that must be run in sequence to scrape data and download images. Activate the virtual environment before running any script:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 1: Scrape Categories
Extract category URLs from Zara’s homepage:
```bash
python scrape_zara_categories.py
```
- **Input**: None (hardcoded URL: `[invalid url, do not cite]).
- **Output**: `zara_urls(unfiltered).txt` containing raw category URLs (e.g., `[invalid url, do not cite]).
- **Details**: Uses Playwright to navigate the homepage, scrape `<a>` tags with `/in/en/`, and save unique URLs.

### Step 2: Organize Categories
Convert raw category URLs into a nested JSON structure:
```bash
python create_categories_json.py
```
- **Input**: `zara_urls(unfiltered).txt`.
- **Output**: `zara_categories(unfiltered).json` with categories organized by gender (e.g., "man", "woman") and subcategory (e.g., "shirts-short").
- **Details**: Uses regex to parse URLs and build a dictionary, saved as JSON.

### Step 3: Scrape Product Links
Collect product links from each category:
```bash
python scrape_zara_product_links.py
```
- **Input**: `zara_categories(unfiltered).json`.
- **Output**: `zara_product_links(unfiltered).json` with product URLs (e.g., `[invalid url, do not cite]).
- **Details**: Scrapes up to 200 links per category, scrolling dynamically to load products, and organizes them by gender and category.

### Step 4: Download Images
Download images from product pages:
```bash
python speed_scrap.py
```
- **Input**: `zara_product_links(unfiltered).json`.
- **Output**: Images saved in `zara_images/`, organized by gender and category (e.g., `zara_images/man/shirts-short/product_1.jpg`).
- **Details**: Uses Playwright to navigate product pages, extract image URLs, and download them, with logging to resume interrupted tasks. For each product page, the script opens the page in a headless browser, finds images in the main gallery (e1, like the big product photo) and the thumbnail carousel (e2, smaller side images), and uses regex (e.g., r"https://static.zara.net/photos/[^?]+\.(jpg|jpeg|png)") to filter valid image URLs while avoiding placeholders like transparent-background.png. It then downloads the images using requests, naming them with the product ID (extracted via regex like r"/p/(\d+)-") and an index (e.g., product_1_0.jpg). A log.txt file tracks progress, helping the script pick up where it left off if interrupted. For beginners: this script acts like a robot that visits Zara’s website, finds all the product pictures, and saves them neatly into folders for you to use later.

**Note**: Run scripts in the above order, as each depends on the output of the previous step. Ensure a stable internet connection and monitor for anti-scraping measures (e.g., CAPTCHAs).

### Temp Folder: Previous Iterations and Testing
The temp/ folder in the repository contains earlier versions of the scripts and test outputs from the development process. These files were used to experiment with different scraping techniques, debug issues, and refine the code before finalizing the main scripts. For example, you might find older versions of speed_scrap.py or sample JSON files used for testing. This folder is included for transparency and learning purposes, but you don’t need it to run the project—just focus on the main scripts outlined above.

## Dataset

The output dataset, including category URLs, product links, and scraped images, is available on Kaggle at [Zara Dresses Dataset](https://www.kaggle.com/datasets/adithya4code/dresses-webscraped). This dataset provides a comprehensive collection of Zara’s clothing data for analysis and research.

**Note**: If the Kaggle dataset link differs, update it in this README. Contact the repository owner if the link is unavailable.

## Troubleshooting

Common issues and solutions:
- **Timeout Errors**:
  - **Cause**: Slow page loading or network issues.
  - **Fix**: Increase wait times in scripts (e.g., change `wait_for_timeout(4000)` to `6000` in `scrape_zara_categories.py`).
- **Selector Failures**:
  - **Cause**: Zara’s HTML structure changed.
  - **Fix**: Inspect the website in Chrome Developer Tools, update selectors in scripts (e.g., `<a>` tags in `scrape_zara_product_links.py`), and test with a single category.
- **Anti-Scraping Blocks**:
  - **Cause**: Zara detects automated requests.
  - **Fix**: Add delays (e.g., `time.sleep(2)` between requests), use proxies, or reduce concurrent tasks in `scrape_zara_product_links.py`.
- **Missing Images**:
  - **Cause**: Lazy-loaded images or incorrect selectors in `speed_scrap.py`.
  - **Fix**: Ensure carousel navigation (e.g., clicking “Next”) is sufficient; check `<img>` or `<source>` tags for URLs.


## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make changes and commit (`git commit -m "Add your feature"`).
4. Push to your branch (`git push origin feature/your-feature`).
5. Open a pull request with a clear description.

**Guidelines**:
- Document changes thoroughly.
- Test scripts before submitting.

Report issues or suggestions via GitHub Issues.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Adithya4code/webscraping-dresses/blob/main/LICENSE) file for details.

## Contact

For questions or support, contact:
- **GitHub**: [Adithya4code](https://github.com/Adithya4code)
- **Email**: s.adithya097@gmail.com.

---

## Key Citations

- [Python Official Downloads](https://www.python.org/downloads/): Official Python download page for installing Python 3.8+.
- [Playwright Python Documentation](https://playwright.dev/python/docs/intro): Documentation for Playwright, used for browser automation.
- [Requests Documentation](https://requests.readthedocs.io/en/latest/): Documentation for the Requests library, used for image downloads.
- [Zara Dresses Dataset on Kaggle](https://www.kaggle.com/datasets/adithya4code/dresses-webscraped): Kaggle dataset containing the project’s output.
- [Zara India Terms of Service](https://www.zara.com/in/en/legal-notice.html): Zara’s legal notice for checking scraping permissions.
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/): Python style guide for contributing to the project.
