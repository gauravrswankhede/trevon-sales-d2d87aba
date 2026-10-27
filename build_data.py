"""Turn the 'All properties' tab of the Trevon Group combined sheet into data.json.

Usage: python3 build_data.py <get_values_result.json> [data.json]

The input is the JSON returned by the Google Sheets get_values call on
'All properties'!A1:W (displayed values, e.g. "₹761,942", "24-Oct-2026").
"""
import json
import sys
from datetime import datetime, timezone, timedelta

FIELDS = {
    "Date": "date", "Entry type": "type", "Rooms available": "avail",
    "Rooms out of order": "ooo", "Rooms sold": "sold", "Room revenue": "room",
    "Restaurant": "restaurant", "In-room dining": "ird", "Meal plans": "plans",
    "Banquet": "banquet", "Bar & beverage": "bar", "Venue charges": "venue",
    "Other revenue": "other", "F&B revenue": "fnb", "Total revenue": "total",
    "Property": "property", "Room revenue budget": "b_room", "F&B budget": "b_fnb",
    "Other revenue budget": "b_other", "Total budget": "b_total",
    "Rooms sold budget": "b_sold",
}
TEXT = {"date", "type", "property"}


def num(v):
    if v is None:
        return 0.0
    s = str(v).replace("₹", "").replace(",", "").strip()
    if s in ("", "-"):
        return 0.0
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        x = float(s)
    except ValueError:
        return 0.0
    return -x if neg else x


def parse_date(s):
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def main():
    src = json.load(open(sys.argv[1]))
    out_path = sys.argv[2] if len(sys.argv) > 2 else "data.json"
    values = src.get("values") or []
    if not values:
        sys.exit("No rows in the sheet result; data.json left unchanged.")
    header = values[0]
    rows = []
    for raw in values[1:]:
        rec = {}
        for i, h in enumerate(header):
            key = FIELDS.get(h)
            if not key:
                continue
            v = raw[i] if i < len(raw) else ""
            rec[key] = v.strip() if key in TEXT else num(v)
        d = parse_date(rec.get("date", ""))
        if not d or not rec.get("property"):
            continue
        rec["date"] = d
        rec["type"] = rec.get("type") or "Daily"
        rows.append(rec)
    rows.sort(key=lambda r: (r["property"], r["date"]))
    ist = timezone(timedelta(hours=5, minutes=30))
    data = {"generated_at": datetime.now(ist).strftime("%Y-%m-%d %H:%M IST"), "rows": rows}
    json.dump(data, open(out_path, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
