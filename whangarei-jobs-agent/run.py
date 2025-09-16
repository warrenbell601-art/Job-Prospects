import csv, os, time, traceback, yaml
from datetime import datetime
from zoneinfo import ZoneInfo
from utils import NZT, compile_region, in_region, match_keywords, parse_deadline, today_str
from sources.seek import fetch_seek
from sources.trademe import fetch_trademe

DATA_DIR = "data"

def write_csv(rows, out_path):
    cols = ["Role","Company","Location","Date Listed","Deadline"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})

def write_audit(run_info, audit_path):
    cols = ["run_at_NZT","schedule","region_filter","industry_filter","keywords","sources_hit","items_found","errors","duration_seconds"]
    exists = os.path.exists(audit_path)
    with open(audit_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if not exists:
            w.writeheader()
        w.writerow(run_info)

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    region_rx = compile_region(cfg["region_regex"])
    keywords = cfg["keywords"]
    max_results = int(cfg.get("max_results", 25))

    t0 = time.time()
    sources_hit = 0
    errors = []

    items = []
    for collector in (fetch_seek, fetch_trademe):
        try:
            new_items = collector()
            sources_hit += 1
            for it in new_items:
                loc = it.get("Location","")
                text = f"{it.get('Role','')} {it.get('Desc','')}"
                if in_region(loc, region_rx) and match_keywords(text, keywords):
                    if not it.get("Deadline"):
                        it["Deadline"] = parse_deadline(it.get("Desc",""))
                    items.append({
                        "Role": it.get("Role",""),
                        "Company": it.get("Company",""),
                        "Location": loc,
                        "Date Listed": it.get("Date Listed",""),
                        "Deadline": it.get("Deadline","") or ""
                    })
        except Exception as e:
            errors.append(f"{collector.__name__}: {e}")

    # dedupe
    seen = set()
    dedup = []
    for it in items:
        key = (it["Role"].lower(), it["Company"].lower(), it["Location"].lower())
        if key not in seen:
            seen.add(key); dedup.append(it)

    # sort by deadline (empty last)
    from datetime import date
    def dkey(x):
        try:
            return datetime.fromisoformat((x.get("Deadline","") or "9999-12-31")+"T00:00:00").date()
        except Exception:
            return date.max
    dedup.sort(key=dkey)
    dedup = dedup[:max_results]

    # write outputs
    today = today_str()
    out_csv = os.path.join(DATA_DIR, f"Job_Search_{today}.csv")
    write_csv(dedup, out_csv)

    audit_csv = os.path.join(DATA_DIR, f"Job_Search_audit_log_{today}.csv")
    run_info = {
        "run_at_NZT": datetime.now(NZT).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "schedule": "Weekly Sat 06:00 NZT",
        "region_filter": "Greater Whangārei only",
        "industry_filter": "None",
        "keywords": " | ".join(keywords),
        "sources_hit": sources_hit,
        "items_found": len(dedup),
        "errors": "; ".join(errors),
        "duration_seconds": round(time.time()-t0,2)
    }
    write_audit(run_info, audit_csv)

    print("Wrote:", out_csv)
    print("Audit:", audit_csv)
    if errors:
        print("Errors:", errors)

if __name__ == "__main__":
    main()
