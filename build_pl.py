"""Turn the Corporate P&L workbook into pl.json for the P&L dashboard.

Usage: python3 build_pl.py "<Corporate P&L 2026-27.xlsx>" <out/pl.json>

The workbook must have cached values (save it in Excel / Google Sheets, or
recalculate it with LibreOffice) because formulas are read as their values.
All money is in Rs. lakh, as in the workbook.
"""
import json
import sys
from datetime import datetime, timezone, timedelta

import openpyxl

ACT_COLS = list("FGHIJKM")          # Apr..Sep actual + Oct estimate (Unit Conso)
FC_COLS = list("EFGHIJ")            # Oct..Mar (Estimated P&L)
CORP_COLS = list("BCDEFGI")         # Apr..Sep + Oct estimate (Corporate P&L)

LEASED = [  # name in workbook row, short name, first row
    ("Haldwani", 6), ("Ranchi", 9), ("Gwalior", 12), ("Delhi", 15), ("Gurugram", 18)]
MANAGED = [("Chakrata", 27), ("Dhanbad", 31), ("Goa", 35)]


def v(ws, ref):
    x = ws[ref].value
    if isinstance(x, (int, float)):
        return round(float(x), 4)
    return None


def row(ws, cols, r):
    return [v(ws, f"{c}{r}") for c in cols]


def main():
    wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
    u = wb["Unit Conso Actual 26-27"]
    e = wb["Estimated P&L for 6 Months"]
    c = wb["Corporate P&L"]

    units = []
    for short, r in LEASED:
        units.append({
            "short": short, "name": u[f"B{r}"].value, "rooms": v(u, f"C{r}"),
            "status": u[f"D{r}"].value, "model": "Leased",
            "rev": row(u, ACT_COLS, r), "exp": row(u, ACT_COLS, r + 1), "fee": None,
            "f_rev": row(e, FC_COLS, r), "f_exp": row(e, FC_COLS, r + 1), "f_fee": None,
        })
    for short, r in MANAGED:
        units.append({
            "short": short, "name": u[f"B{r}"].value, "rooms": v(u, f"C{r}"),
            "status": u[f"D{r}"].value, "model": "Managed",
            "rev": row(u, ACT_COLS, r), "exp": row(u, ACT_COLS, r + 1), "fee": row(u, ACT_COLS, r + 2),
            "f_rev": row(e, FC_COLS, r), "f_exp": row(e, FC_COLS, r + 1), "f_fee": row(e, FC_COLS, r + 2),
        })

    corp = {
        "income": {
            "Management fees, hotels": row(c, CORP_COLS, 8),
            "Management fees, clubs": row(c, CORP_COLS, 9),
            "Manpower supply (ATS)": row(c, CORP_COLS, 10),
        },
        "expense": {
            "Corporate staff salary": row(c, CORP_COLS, 13),
            "ATS manpower": row(c, CORP_COLS, 14),
            "Sales & marketing": row(c, CORP_COLS, 15),
            "Travelling": row(c, CORP_COLS, 16),
            "Other office expenses": row(c, CORP_COLS, 17),
            "Professional fees": row(c, CORP_COLS, 18),
            "Laptop & computer rental": row(c, CORP_COLS, 19),
        },
        "preopening": {
            "Claire, Gurugram": row(c, CORP_COLS, 25),
            "Ranchi": row(c, CORP_COLS, 26),
            "Gwalior": row(c, CORP_COLS, 27),
        },
    }
    forecast = {
        "other_fees": row(e, FC_COLS, 45),
        "corp_exp": row(e, FC_COLS, 47),
    }
    ist = timezone(timedelta(hours=5, minutes=30))
    data = {
        "generated_at": datetime.now(ist).strftime("%Y-%m-%d %H:%M IST"),
        "source": "Corporate P&L 2026-27.xlsx",
        "months": ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"],
        "estimate_from": 6,
        "f_months": ["2026-10", "2026-11", "2026-12", "2027-01", "2027-02", "2027-03"],
        "units": units, "corp": corp, "forecast": forecast,
    }
    json.dump(data, open(sys.argv[2], "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {len(units)} units to {sys.argv[2]}")


if __name__ == "__main__":
    main()
