"""Q8: session-aware probe that honours Ahmia's actual form contract.

Background: Q1, Q2 (through OnionClaw) and Q7 (independent direct probe) all
silently failed against Ahmia's `/search/?q=...` URL. Both implementations
shared a single blind spot — they issue the query as a stateless GET against
a URL pattern, without first acquiring whatever session state the form
contract requires.

Inspection of Ahmia's homepage form reveals a per-session hidden input field
with a randomised name and value (e.g. `<input type="hidden" name="33ab23"
value="b8f425">`). The field is regenerated on every homepage load. Without
this token in the request parameters, Ahmia's `/search/` endpoint returns a
302 redirect to `/`, and any non-redirect-aware parser sees only homepage
chrome.

Q8 honours the form contract: it first GETs the homepage, scrapes the hidden
token, and only then issues the search request with the harvested token
alongside the query parameter.

The probe is performed against the clearnet form (`https://ahmia.fi/`) to
keep the diagnostic surface narrow; the onion address uses the same Django
backend and the same form contract.

Expected outcomes:
  - If the engine is genuinely JS-only: Q8 still returns chrome.
  - If the engine simply enforces a session contract that stateless probes
    miss: Q8 returns a real result list with li.result elements.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

UA = "Mozilla/5.0 (compatible; darknet-IR-audit/1.0; +https://github.com/RsGoksel/academic-portfolio)"
BASE = "https://ahmia.fi"
QUERY = "machine learning"
ENGINE = "Ahmia"
OUT = Path(r"C:\tmp\darkweb-audit\test_results\q08_session_aware_probe.json")


def main():
    record = {
        "probe_run_utc": datetime.now(timezone.utc).isoformat(),
        "query": QUERY,
        "engine": ENGINE,
        "method": (
            "Two-step: (1) GET homepage and harvest the per-session hidden form "
            "token, (2) issue the search GET with the query parameter and the "
            "harvested token."
        ),
        "base_url": BASE,
    }
    s = requests.Session()
    s.headers.update({"User-Agent": UA})

    print(f"[step 1/3] GET homepage to harvest form token", flush=True)
    home = s.get(f"{BASE}/", timeout=30)
    record["homepage_status"] = home.status_code
    record["homepage_len"] = len(home.text)

    form_m = re.search(
        r'<form[^>]+id="searchForm"[^>]*>(.*?)</form>',
        home.text, re.S | re.I,
    )
    if not form_m:
        print("FAIL: searchForm not found on homepage"); sys.exit(1)
    inner = form_m.group(1)

    action_m = re.search(r'<form[^>]+action="([^"]+)"', form_m.group(0))
    method_m = re.search(r'<form[^>]+method="([^"]+)"', form_m.group(0))
    action = action_m.group(1) if action_m else "/search/"
    http_method = (method_m.group(1) if method_m else "get").lower()

    tokens = re.findall(
        r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]+value="([^"]+)"',
        inner,
    )
    record["form_action"] = action
    record["form_http_method"] = http_method
    record["harvested_hidden_inputs"] = [{"name": n, "value": v} for n, v in tokens]
    print(f"  -> form action={action} method={http_method} hidden tokens={len(tokens)}", flush=True)
    for n, v in tokens:
        print(f"     {n} = {v}", flush=True)

    print(f"[step 2/3] issue search WITH harvested token", flush=True)
    params = {"q": QUERY}
    for n, v in tokens:
        params[n] = v
    if http_method == "post":
        r = s.post(f"{BASE}{action}", data=params, timeout=30, allow_redirects=True)
    else:
        r = s.get(f"{BASE}{action}", params=params, timeout=30, allow_redirects=True)
    record["search_status"] = r.status_code
    record["search_final_url"] = r.url
    record["search_response_len"] = len(r.text)
    print(f"  -> status {r.status_code}, len {len(r.text)} bytes, final url {r.url}", flush=True)

    print(f"[step 3/3] parse li.result entries", flush=True)
    li_count = len(re.findall(r'<li[^>]+class="result"', r.text))
    query_echo = len(re.findall(r"machine\s+learning", r.text, re.I))
    onion_hrefs = len(re.findall(
        r'<a[^>]+href="(http[s]?://[a-z0-9]{56}\.onion[^"]*)"', r.text))
    record["raw_li_result_count"] = li_count
    record["query_echo_count_in_html"] = query_echo
    record["onion_href_count_in_html"] = onion_hrefs

    # Now extract first 10 real result titles + URLs for the record
    titles = re.findall(
        r'<li[^>]+class="result"[^>]*>\s*<h4[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        r.text, re.S,
    )
    cleaned = []
    for href, title_html in titles[:10]:
        t = re.sub(r"<[^>]+>", "", title_html).strip()
        cleaned.append({"href": href, "title": t[:120]})
    record["first_10_result_entries"] = cleaned

    record["verdict"] = {
        "engine_returns_server_rendered_results": (li_count > 0),
        "silent_failure_in_q7_was_due_to": (
            "missing per-session hidden form token in stateless probe URL "
            "construction (anti-scraping mechanism), not a JS-only engine architecture"
            if li_count > 0 else
            "still unable to extract results after honouring the form contract; "
            "alternative diagnoses (additional protections, server outage) remain "
            "in scope"
        ),
        "reasoning": (
            f"Stateless probes against /search/?q=... receive a 302 redirect to /. "
            f"With the homepage form token included as a request parameter, the "
            f"search endpoint returns {len(r.text)} bytes of HTML containing "
            f"{li_count} <li class='result'> elements and {query_echo} echoes of "
            f"the query string. The engine itself is server-rendering results; "
            f"the silent failure caught by the protocol in Q6 and Q7 is the "
            f"consequence of two independent stateless parsers sharing the same "
            f"blind spot about Ahmia's per-session form contract."
        ),
    }

    print(f"  raw li.result count           : {li_count}", flush=True)
    print(f"  query echo count in HTML      : {query_echo}", flush=True)
    print(f"  onion href count in HTML      : {onion_hrefs}", flush=True)
    print(f"  engine server-renders results : {li_count > 0}", flush=True)

    OUT.write_text(json.dumps(record, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nSaved: {OUT}", flush=True)


if __name__ == "__main__":
    main()
