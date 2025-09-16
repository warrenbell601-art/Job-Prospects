# Basic SEEK collector (fragile: selectors subject to change)
from playwright.sync_api import sync_playwright

SEARCH_URL = "https://www.seek.co.nz/jobs?where=Whang%C4%81rei"

def fetch_seek():
    items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SEARCH_URL, wait_until="load", timeout=60000)
        page.wait_for_timeout(3000)  # allow dynamic content
        # Approximate selectors; update if SEEK changes
        cards = page.query_selector_all('[data-automation="searchResults"] article')
        for c in cards[:60]:
            title = (c.query_selector('[data-automation="jobTitle"]') or c.query_selector("a")).inner_text() if c else ""
            company = (c.query_selector('[data-automation="jobCompany"]') or c.query_selector('[data-automation="jobAdvertiser"]'))
            company = company.inner_text() if company else ""
            loc = (c.query_selector('[data-automation="jobLocation"]') or c.query_selector('[data-automation="jobCardLocation"]'))
            loc = loc.inner_text() if loc else ""
            date_listed = (c.query_selector('[data-automation="jobListingDate"]') or c.query_selector('[data-automation="jobCardDatePosted"]'))
            date_listed = date_listed.inner_text() if date_listed else ""
            link_el = c.query_selector("a[href*='/job/']")
            desc = ""
            deadline = ""
            if link_el:
                href = link_el.get_attribute("href")
                if href and href.startswith("/"):
                    href = "https://www.seek.co.nz" + href
                # open detail page
                try:
                    detail = browser.new_page()
                    detail.goto(href, wait_until="load", timeout=60000)
                    detail.wait_for_timeout(2000)
                    jd = detail.query_selector('[data-automation="jobAdDetails"]') or detail.query_selector("article")
                    desc = jd.inner_text()[:5000] if jd else ""
                    # look for closing date text
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
        browser.close()
    return items
