# Trevon Hotels sales dashboard

Static page (index.html) that reads data.json. data.json is rebuilt every day at 12:00 IST from the "Trevon Group – Daily Sales (all properties)" Google Sheet with `python3 build_data.py <sheet_values.json> data.json`.

## P&L dashboard

`pl-c02c931ae5/` holds the P&L dashboard (not linked from the sales page). Rebuild its data from the Corporate P&L workbook ("Corporate P&L 2026-27.xlsx" in Google Drive, file id 1VUBg-ZDf-6rrGkjJQiTB4al21KLeblzf; download it with the Drive connector) with
`python3 build_pl.py "<Corporate P&L 2026-27.xlsx>" pl-c02c931ae5/pl.json --fallback <copy of the previous pl.json>` (the workbook needs saved values, so save it in Excel or Sheets first; `--fallback` keeps the last good plan for units whose plan cells show #REF!).

The sales page's "Revenue vs expenditure by property" section reads the same figures: `build_data.py` copies each unit's revenue and expenditure from `pl-c02c931ae5/pl.json` into data.json.
