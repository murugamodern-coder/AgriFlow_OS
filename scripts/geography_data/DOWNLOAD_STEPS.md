# Tamil Nadu Geography Data — Download Steps

## Automated (recommended)

From WSL or any Python 3.10+ environment:

```bash
cd /mnt/c/AgriFlow_OS/AgriFlow_Main/scripts/geography_data
python3 prepare_tn_csv.py
```

This pulls the **LGD mirror** from GitHub (`planemad/india-local-government-directory`), filters `state_code = 33` (Tamil Nadu), and writes:

| File | Expected rows |
|------|----------------|
| `tn_districts.csv` | 38 |
| `tn_blocks.csv` | ~385–600 (LGD development blocks) |
| `tn_villages.csv` | ~17,000 |

## Primary source — LGD portal

- URL: https://lgdirectory.gov.in
- Tamil Nadu state code: **33**
- Public CSV exports may require browser interaction (captcha / session).

If the portal blocks automation, use the GitHub mirror above (same LGD schema).

## Manual LGD portal steps

1. Open https://lgdirectory.gov.in → Reports / Download
2. Select **State: Tamil Nadu (33)**
3. Export District, Block, Village CSVs
4. Rename to `tn_districts.csv`, `tn_blocks.csv`, `tn_villages.csv`
5. Ensure UTF-8 encoding and columns: code, English name, parent code

## Verification

```bash
wc -l tn_*.csv
head -3 tn_districts.csv
python3 -c "import csv; print(list(csv.DictReader(open('tn_villages.csv',encoding='utf-8')))[0])"
```

Expected district count: **38**. Village file should contain Tamil Unicode names.
