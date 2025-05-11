import json
import re

def extract_keys(url):
    """
    Extracts the top-level key (kid/man/woman) and subcategory (e.g., girl-tshirts) from the URL.
    """
    match = re.search(r"zara\.com/.+?/([a-z]+)-([a-z]+-[a-z]+)", url)
    if match:
        top_level, sub_category = match.groups()
        return top_level, sub_category
    return None, None

def build_nested_dict(urls):
    nested_dict = {}

    for url in urls:
        url = url.strip().strip('"').strip("'")
        top_level, sub_category = extract_keys(url)
        if top_level and sub_category:
            if top_level not in nested_dict:
                nested_dict[top_level] = {}
            nested_dict[top_level][sub_category] = url
    return nested_dict

if __name__ == "__main__":
    with open("zara_urls.txt", "r") as file:
        content = file.read()
        urls = [url.strip() for url in content.split(",") if url.strip()]

    result = build_nested_dict(urls)

    with open("zara_categories.json", "w") as f:
        json.dump(result, f, indent=4)

    print("Saved as zara_categories.json")