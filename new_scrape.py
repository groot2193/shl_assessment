import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import time

# Base SHL product catalog page (change start param to paginate)
BASE_URL = "https://www.shl.com/solutions/products/product-catalog/?start={}&type=2"

# Directory to save PDFs
folder_name = "shl_job_pdfs"
os.makedirs(folder_name, exist_ok=True)

# User-Agent header to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Store errors or no-pdf cases
no_pdf_list = []

# Loop through pages (12 pages = 0 to 264 by 24s)
for start in range(0, 288, 24):  # Adjust this if needed
    url = BASE_URL.format(start)
    print(f"Scraping listing page: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to load page: {url}\n  Error: {e}")
        continue

    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.select("td.custom_table-heading_title a")

    for a in links:
        test_page = urljoin("https://www.shl.com", a['href'])
        test_name = a.text.strip().replace(" ", "_").replace("/", "_")
        print(f"→ Visiting: {test_page}")

        try:
            detail_resp = requests.get(test_page, headers=HEADERS, timeout=10)
            detail_resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"   ✗ Failed to load detail page: {e}")
            continue

        detail_soup = BeautifulSoup(detail_resp.content, "html.parser")
        pdf_tag = detail_soup.select_one("ul.product-catalogue__downloads a[href$='.pdf']")

        if pdf_tag:
            pdf_url = pdf_tag["href"]
            print(f"   ↳ Found PDF: {pdf_url}")

            try:
                pdf_response = requests.get(pdf_url, headers=HEADERS, timeout=10)
                pdf_response.raise_for_status()

                with open(os.path.join(folder_name, f"{test_name}.pdf"), "wb") as f:
                    f.write(pdf_response.content)
                print(f"   ↳ Saved: {test_name}.pdf")

            except Exception as e:
                print(f"   ✗ Error downloading PDF: {e}")
        else:
            print("   ↳ No PDF found.")
            no_pdf_list.append(test_name)

        time.sleep(1)

    print("=== Page complete ===\n")
    time.sleep(2)

print("✅ All done!")
if no_pdf_list:
    print(f"📝 Assessments with no PDFs found: {no_pdf_list}")

mereko koi psnd aayi ladki mtlb sundar hai