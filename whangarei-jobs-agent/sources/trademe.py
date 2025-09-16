# Basic Trade Me Jobs collector (fragile: selectors subject to change)
from playwright.sync_api import sync_playwright

SEARCH_URL = "https://www.trademe.co.nz/a/jobs/search?region=15"  # 15 = Northland; we will filter to Whangārei by text

def fetch_trademe():
    items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SEARCH_URL, wait_until="load", timeout=60000)
        page.wait_for_timeout(3000)
        cards = page.query_selector_all("tm-job-search-card, div.o-card")
        for c in cards[:60]:
            try:
                title = (c.query_selector("a[href*='/a/jobs/listing/']") or c.query_selector("a")).inner_text()
                company = (c.query_selector('[data-test="company"]') or c.query_selector(".t-is-medium")).inner_text() if c else ""
                loc = (c.query_selector('[data-test="region"]') or c.query_selector("tm-location")).inner_text() if c else ""
                date_listed = (c.query_selector('[data-test="date-listed"]') or c.query_selector("time"))
                date_listed = date_listed.inner_text() if date_listed else ""
                href_el = c.query_selector("a[href*='/a/jobs/listing/']")
                desc = ""
                deadline = ""
                if href_el:
                    href = href_el.get_attribute("href")
                    if href and href.startswith("/"):
                        href = "https://www.trademe.co.nz" + href
                    try:
                        detail = browser.new_page()
                        detail.goto(href, wait_until="load", timeout=60000)
                        detail.wait_for_timeout(2000)
                        jd = detail.query_selector("tm-markdown, article") or detail.query_selector("main")
                        desc = jd.inner_text()[:5000] if jd else ""
                        close_el = detail.query_selector("text=/close|closing|applications close/i")
                        if close_el:
                            deadline = close_el.inner_text()
                        detail.close()
                    except Exception:
                        pass
                items.append({
                    "Role": title.strip(),
                    "Company": company.strip(),
                    "Location": loc.strip(),
                    "Date Listed": date_listed.strip(),
                    "Deadline": deadline.strip(),
                    "Desc": desc
                })
            except Exception:
                continue
        browser.close()
    return items
