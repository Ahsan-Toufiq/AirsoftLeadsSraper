import re

def find_contact_page_link(page):
    try:
        contact_keywords = [
            "contact", "contact us", "contact-us", "get in touch", "getintouch",
            "reach us", "reachout", "talk to us", "say hello", "get support", "customer care", "Email"
        ]

        def normalize(text):
            return re.sub(r"[\\s\\-_]+", "", text.lower())

        normalized_keywords = [normalize(k) for k in contact_keywords]

        links = page.locator("a")
        count = links.count()

        for i in range(count):
            try:
                link = links.nth(i)
                text = link.text_content() or ""
                href = link.get_attribute("href") or ""

                if not href or href.startswith("javascript"):
                    continue

                norm_text = normalize(text)
                if any(keyword in norm_text for keyword in normalized_keywords):
                    print(f"🔗 Found contact link: \"{text.strip()}\" → {href}")
                    return href
            except:
                continue

        print("❌ No contact link found.")
        return False

    except Exception as e:
        print(f"⚠️ Error while searching for contact link: {e}")
        return False


import re

def extract_email_from_page(page):
    try:
        # Get all visible text from the page
        body_text = page.locator("body").inner_text(timeout=10000)

        # Email regex (simple + general)
        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        # Find all matches
        matches = re.findall(email_regex, body_text)

        if matches:
            print(f"📧 Found email: {matches[0]}")
            return matches[0]

        print("❌ No email found on this page.")
        return False

    except Exception as e:
        print(f"⚠️ Error while extracting email: {e}")
        return False



import csv
from playwright.sync_api import Page

def process_csv_and_extract_emails(csv_file, output_file, page: Page):
    with open(csv_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        if len(header) < 5:
            header += ["Email"]
        writer.writerow(header)

        for index, row in enumerate(reader, 1):
            try:
                if len(row) < 3:
                    print(f"⚠️ Row {index} skipped (no 3rd column): {row}")
                    continue

                url = row[2].strip()
                if not url.startswith("http"):
                    url = "https://" + url

                print(f"🔗 [{index}] Visiting: {url}")
                page.goto(url, timeout=30000, wait_until="domcontentloaded")

                contact_link = find_contact_page_link(page)
                if not contact_link:
                    print(f"❌ No contact page found for {url}")
                    # continue
                    email = extract_email_from_page(page)
                    if email:
                        row_with_email = row[:4] + [email]
                        writer.writerow(row_with_email)
                        print(f"✅ Email extracted: {email}")
                        continue
                    else:
                        print(f"❌ No email found on contact page of {url}")
                        continue

                # Navigate to contact page
                if not contact_link.startswith("http"):
                    # Resolve relative links
                    from urllib.parse import urljoin
                    contact_link = urljoin(url, contact_link)

                print(f"➡ Navigating to contact page: {contact_link}")
                page.goto(contact_link, timeout=30000, wait_until="domcontentloaded")

                email = extract_email_from_page(page)
                if email:
                    row_with_email = row[:4] + [email]
                    writer.writerow(row_with_email)
                    print(f"✅ Email extracted: {email}")
                else:
                    print(f"❌ No email found on contact page of {url}")

            except Exception as e:
                print(f"❌ Error on row {index}: {e}")


from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    process_csv_and_extract_emails("airsoft_stores_sites_deduped.csv", "output_with_emails.csv", page)
    browser.close()