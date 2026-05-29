"""Verify Faizan & Khan (2019) engine list against current Tor network.
Each engine probed via SOCKS5 (127.0.0.1:9050). Records HTTP status, elapsed time, and a short
content-truthiness check (title detected vs. timeout vs. 404).
"""
import requests, time, sys, json
from datetime import datetime, timezone

PROXIES = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}

ENGINES = [
    # (id, canonical name, URL)
    ("1", "Ahmia",
     "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/"),
    ("2", "Torch",
     "http://torchpoaolafho6ycwo7lzfg7p7okjbplowxhqixyhguvifmplnybnyd.onion/"),
    ("3", "NotEvil (alias 'not Evil')",
     "http://hss3uro2hsxfogfq.onion/"),
    ("4", "Candle",
     "http://gjobqjj7wyczbqie.onion/"),
    ("5", "Haystak",
     "http://haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion/"),
    ("6", "OnionLand Search",
     "http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/"),
]

results = []
print(f"Probe date (UTC): {datetime.now(timezone.utc).isoformat()}")
print(f"Tor SOCKS: 127.0.0.1:9050")
print()
for eid, name, url in ENGINES:
    t0 = time.time()
    record = {"id": eid, "name": name, "url": url, "resolved": False, "http_status": None,
              "elapsed_sec": None, "title": None, "error": None}
    try:
        r = requests.get(url, proxies=PROXIES, timeout=90, allow_redirects=True,
                         headers={'User-Agent': 'Mozilla/5.0 (academic-replication)'})
        record["http_status"] = r.status_code
        record["elapsed_sec"] = round(time.time() - t0, 2)
        if r.status_code == 200:
            record["resolved"] = True
            # First 60 chars of <title> if present
            import re as _re
            m = _re.search(r"<title[^>]*>([^<]+)</title>", r.text, _re.I)
            if m:
                record["title"] = m.group(1).strip()[:60]
        else:
            record["error"] = f"HTTP {r.status_code}"
    except requests.exceptions.ConnectTimeout:
        record["elapsed_sec"] = round(time.time() - t0, 2)
        record["error"] = "ConnectTimeout"
    except requests.exceptions.ReadTimeout:
        record["elapsed_sec"] = round(time.time() - t0, 2)
        record["error"] = "ReadTimeout"
    except Exception as e:
        record["elapsed_sec"] = round(time.time() - t0, 2)
        msg = str(e)[:120]
        record["error"] = f"{type(e).__name__}: {msg}"
    results.append(record)
    status = "UP   " if record["resolved"] else "DOWN "
    sys.stdout.buffer.write(
        f"  [{eid}] {status} {name:30s}  http={record['http_status']!s:<4}  t={record['elapsed_sec']!s:<5}s  err={record['error']!s:<22}  title={record['title'] or ''}\n".encode('utf-8')
    )

resolved = sum(1 for r in results if r["resolved"])
print()
print(f"Resolved: {resolved} / {len(results)}")
print(f"Down:     {len(results) - resolved} / {len(results)}")

# Save full JSON for the supplementary
import os
out = r"E:\Bildiri\01-darkweb-search-engine-benchmark\supplementary\legacy_check.json"
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    json.dump({
        "probe_utc": datetime.now(timezone.utc).isoformat(),
        "proxy": "socks5h://127.0.0.1:9050",
        "summary": {"resolved": resolved, "total": len(results)},
        "results": results,
    }, f, indent=2, ensure_ascii=False)
print(f"\nSaved JSON: {out}")
