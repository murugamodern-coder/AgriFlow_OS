import json

with open("/mnt/c/AgriFlow_OS/AgriFlow_Main/mobile/agriflow_mobile/lib/l10n/app_en.arb") as f:
    en = json.load(f)
with open("/mnt/c/AgriFlow_OS/AgriFlow_Main/mobile/agriflow_mobile/lib/l10n/app_ta.arb") as f:
    ta = json.load(f)

en_keys = set(en.keys()) - {"@@locale", "@@last_modified"}
ta_keys = set(ta.keys()) - {"@@locale", "@@last_modified"}
missing = en_keys - ta_keys
extra = ta_keys - en_keys
common = len(ta_keys & en_keys)

print(f"EN keys: {len(en_keys)}")
print(f"TA keys: {len(ta_keys)}")
print(f"Coverage: {common}/{len(en_keys)} = {100*common/len(en_keys):.1f}%")
if missing:
    print(f"Missing in TA ({len(missing)}): {sorted(missing)}")
if extra:
    print(f"Extra in TA ({len(extra)}): {sorted(extra)}")