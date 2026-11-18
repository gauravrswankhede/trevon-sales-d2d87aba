"""Read each property's Daily Revenue Report and write report_mtd.json.

Usage: python3 build_mtd.py <folder> [report_mtd.json]

<folder> holds one file per property, named <Property>.json (e.g. Haldwani.json),
each the JSON result of Google Sheets get_values on that property's report tab
(range A1:G45). Figures are read by their row label, so shifted or re-pasted
layouts still work: FTD is column A, MTD actual is the cell right after the
label, MTD budget the one after that.

The website uses these month-to-date figures for the scorecard and the group
totals, so a day a hotel skipped is still counted once a later report includes it.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

# normalised label -> key
LABELS = {
    "netroomrevenue": "room",
    "inroomdining": "ird",
    "restaurant": "restaurant", "restaurent": "restaurant",
    "plansale": "plans", "plansales": "plans",
    "bar": "bar", "beveragesale": "bar",
    "banquet": "banquet",
    "venuecharges": "venue", "vanuecharges": "venue",
    "totalfbrevenue": "fnb",
    "totalotherrevenue": "other",
    "totalrevenueabc": "total",
    "totalrooms": "avail",
    "outoforderrooms": "ooo",
    "occupiedrooms": "sold",
    "complimentaryroomshouseuse": "comp",
}
BUDGET_KEYS = {"room": "b_room", "fnb": "b_fnb", "other": "b_other", "total": "b_total", "sold": "b_sold", "avail": "b_avail"}
DATE_RE = re.compile(r"^\s*(\d{1,2})[-/.](\d{1,2})[-/.](\d{2}|\d{4})\s*$")


def norm(s):
    return re.sub(r"[^a-z]", "", str(s).lower())


def num(v):
    if v is None:
        return 0.0
    s = str(v).replace("₹", "").replace(",", "").replace("%", "").strip()
    if s in ("", "-"):
        return 0.0
    s = s.lstrip("+")
    try:
        return float(s)
    except ValueError:
        return 0.0


def report_date(values):
    """The report date: a dd-mm-yyyy (or / .) cell in the first six rows."""
    for row in values[:6]:
        for cell in row:
            m = DATE_RE.match(str(cell))
            if m:
                d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if y < 100:
                    y += 2000
                try:
                    return datetime(y, mo, d).strftime("%Y-%m-%d")
                except ValueError:
                    continue
    return None


def parse(values):
    out = {"date": report_date(values)}
    for row in values:
        for i, cell in enumerate(row[:4]):
            key = LABELS.get(norm(cell))
            if not key or key in out:
                continue
            ftd = row[0] if i > 0 else ""
            mtd = row[i + 1] if i + 1 < len(row) else ""
            bud = row[i + 2] if i + 2 < len(row) else ""
            out[key] = num(mtd)
            out["day_" + key] = num(ftd)
            if key in BUDGET_KEYS:
                out[BUDGET_KEYS[key]] = num(bud)
            break
    return out


def main():
    folder = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "report_mtd.json"
    props = {}
    dates = {}
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".json"):
            continue
        prop = name[:-5]
        src = json.load(open(os.path.join(folder, name)))
        values = src.get("values") or []
        if not values:
            print(f"{prop}: no rows, skipped")
            continue
        r = parse(values)
        dates[prop] = r.get("date")
        if not r.get("date") or not r.get("total"):
            print(f"{prop}: report date {r.get('date')} with no month-to-date revenue, skipped")
            continue
        props[prop] = r
        print(f"{prop}: report {r['date']}, MTD revenue {r['total']:,.0f}, budget {r.get('b_total', 0):,.0f}")
    data = {"generated_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"), "properties": props, "report_dates": dates}
    json.dump(data, open(out_path, "w"), ensure_ascii=False, indent=1)
    print(f"wrote {len(props)} properties to {out_path}")


if __name__ == "__main__":
    main()
