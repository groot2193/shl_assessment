import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# Set up headless Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Load SHL catalog
BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
driver.get(BASE_URL)
time.sleep(5)  # Wait for page to load

# Parse catalog page
soup = BeautifulSoup(driver.page_source, "html.parser")

# Find all valid assessment links
assessment_links = []
for a_tag in soup.find_all("a", href=True):
    href = a_tag["href"]
    text = a_tag.get_text(strip=True)
    if "/solutions/products/product-catalog/" in href and len(text) > 3:
        full_url = href if href.startswith("http") else f"https://www.shl.com{href}"
        assessment_links.append((text, full_url))

# Remove duplicates
assessment_links = list(set(assessment_links))

print(f"Found {len(assessment_links)} assessments.")

# Final scraped data
data = []

# Scrape individual pages
for name, url in assessment_links:
    print(f"Scraping: {name}")
    try:
        driver.get(url)
        time.sleep(3)
        page_soup = BeautifulSoup(driver.page_source, "html.parser")

        # Description (fallback if multiple)
        desc_tag = page_soup.find("div", class_="content") or page_soup.find("div", class_="description")
        description = desc_tag.get_text(strip=True) if desc_tag else "N/A"

        # Remote Testing Support
        remote_testing = "Yes" if page_soup.find("span", class_="green-dot") else "No"

        # Adaptive/IRT Support
        adaptive_irt = "Yes" if "Adaptive/IRT" in driver.page_source else "No"

        # Duration
        duration = "N/A"
        for el in page_soup.find_all(text=True):
            if "Approximate Completion Time" in el:
                duration = el.split(":")[-1].strip()
                break

        # Test Type
        test_types = page_soup.find_all("span", class_="test-type")
        test_type_texts = [t.get_text(strip=True) for t in test_types]
        test_type = ", ".join(test_type_texts) if test_type_texts else "N/A"

        # Save result
        data.append([name, url, remote_testing, adaptive_irt, duration, test_type, description])

    except Exception as e:
        print(f"Failed to scrape {name}: {e}")
        continue

# Convert to DataFrame
df = pd.DataFrame(data, columns=[
    "Assessment Name", "URL", "Remote Testing", "Adaptive/IRT",
    "Duration", "Test Type", "Description"
])

# Save to CSV
df.to_csv("shl.csv", index=False)
print("\n✅ Scraping complete. Data saved to `shl_assessments_full.csv`.")

# Close browser
driver.quit()
