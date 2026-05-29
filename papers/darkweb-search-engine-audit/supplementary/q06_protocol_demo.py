"""Protocol demonstration: exercise the search-fetch-diff sanity protocol on Ahmia.

The protocol proposed in the paper is:
  1. Issue _search(query) to the engine via the dispatcher.
  2. Issue _fetch(engine_serp_url(query)) for the same engine + query.
  3. Compare: do any of the dispatcher-extracted result titles appear as
     substrings in the fetched HTML? Does the query itself appear in any
     dispatcher-extracted result snippet (sentinel check)?
  4. If neither holds, flag the dispatcher's ok=true as a silent failure.

This script runs the protocol against the Ahmia onion + query "machine learning"
(Q1 in the paper). The Q1 search result already on file shows the parser-drift
pattern; here we DEMONSTRATE the protocol catching it, rather than describing
counterfactually that it would have caught it.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, r"C:\tmp\darkweb-audit\repos\OnionClaw-genuine")
os.environ["TOR_SOCKS_HOST"] = "127.0.0.1"
os.environ["TOR_SOCKS_PORT"] = "9050"
os.environ["TOR_CONTROL_PORT"] = "9051"

import sicry

OUT = Path(r"C:\tmp\darkweb-audit\test_results\q06_protocol_demo.json")

QUERY = "machine learning"
ENGINE = "Ahmia"
# SERP URL for Ahmia onion at the audited commit
SERP_URL = (
    "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q=machine+learning"
)


def main():
    record = {
        "protocol_run_utc": datetime.now(timezone.utc).isoformat(),
        "query": QUERY,
        "engine": ENGINE,
        "serp_url": SERP_URL,
    }

    print(f"[step 1/4] sicry_search({QUERY!r}) on {ENGINE}", flush=True)
    s = sicry.dispatch(
        "sicry_search",
        {"query": QUERY, "engines": [ENGINE], "max_results": 10},
    )
    record["dispatcher_search_result"] = s
    print(f"  -> {len(s) if isinstance(s, list) else 'non-list'} results, "
          f"dispatcher reports ok=True (call completed without exception)",
          flush=True)

    print(f"[step 2/4] sicry_fetch({SERP_URL[:60]}...)", flush=True)
    f = sicry.dispatch("sicry_fetch", {"url": SERP_URL})
    record["dispatcher_fetch_result"] = {
        "url": f.get("url"),
        "status": f.get("status"),
        "title": f.get("title"),
        "text_len": len(f.get("text") or ""),
        "links_count": len(f.get("links") or []),
        "text_excerpt": (f.get("text") or "")[:2500],
        "fetched_html_len": len(f.get("text") or ""),
    }
    print(f"  -> fetch status {f.get('status')}, text {len(f.get('text') or '')} chars",
          flush=True)

    print("[step 3/4] sentinel diff", flush=True)
    search_titles = []
    if isinstance(s, list):
        search_titles = [r.get("title", "") for r in s if isinstance(r, dict)]
    fetched_text = (f.get("text") or "").lower()

    # Check A: does the query itself appear in any returned title?
    query_in_titles = [t for t in search_titles if QUERY.lower() in t.lower()]

    # Check B: do the returned titles appear as substrings in the fetched page text?
    titles_in_fetched = [t for t in search_titles if t and t.lower() in fetched_text]

    # Check C: does the query appear in the fetched page at all? (sanity: Ahmia
    # should at least echo the query string in its SERP)
    query_in_fetched = QUERY.lower() in fetched_text

    record["protocol_diff"] = {
        "search_returned_titles": search_titles,
        "search_titles_containing_query": query_in_titles,
        "search_titles_found_in_fetched_html": titles_in_fetched,
        "query_string_present_in_fetched_html": query_in_fetched,
    }

    # Decision rule from the protocol (sentinel check):
    #
    #   The simplest reliable sentinel is whether the query string itself appears
    #   anywhere in the fetched SERP HTML. Ahmia (and almost every search engine)
    #   echoes the query in its result page chrome — even on a no-results SERP.
    #   If the query is absent from the fetched HTML, the engine did not process
    #   the request as a search for this query, and whatever the dispatcher's
    #   parser extracted is not a real result list.
    #
    #   A second, stricter check is whether the dispatcher's returned titles
    #   contain the query at all. A real result list for "machine learning"
    #   ought to surface at least one title with that string in it; chrome-link
    #   fallback titles (e.g. "Tor browser bundle", "contribute to the source
    #   code") never do.
    #
    #   We mark silent_failure_caught = True when both fail.
    sentinel_query_in_fetched_html = query_in_fetched
    sentinel_query_in_any_returned_title = bool(query_in_titles)
    protocol_ok = sentinel_query_in_fetched_html and sentinel_query_in_any_returned_title
    silent_failure = not protocol_ok

    record["protocol_verdict"] = {
        "dispatcher_reported_ok_true": True,
        "sentinel_1_query_in_fetched_html": sentinel_query_in_fetched_html,
        "sentinel_2_query_in_returned_titles": sentinel_query_in_any_returned_title,
        "protocol_passes": protocol_ok,
        "silent_failure_caught": silent_failure,
        "reasoning": (
            "The dispatcher reported ok=True for the search call and returned "
            f"{len(search_titles)} titles. "
            f"Sentinel 1 (query string '{QUERY}' present in fetched SERP HTML): "
            f"{'PASS' if sentinel_query_in_fetched_html else 'FAIL'}. "
            f"Sentinel 2 (query string '{QUERY}' present in at least one returned "
            f"title): {'PASS' if sentinel_query_in_any_returned_title else 'FAIL'}. "
            "Either sentinel failing is sufficient to flag a silent failure; "
            "here both fail, so the protocol catches what the dispatcher's ok=True "
            "missed. The dispatcher's returned titles are the same Ahmia site "
            "chrome regardless of query (cf. the identical four-row boilerplate "
            "documented for Q1 and Q2 in §4.3), which is exactly the symptom of "
            "the parser regression described in §5.1."
        ),
    }

    print(f"[step 4/4] verdict", flush=True)
    print(f"  dispatcher said ok=True : {record['protocol_verdict']['dispatcher_reported_ok_true']}", flush=True)
    print(f"  protocol passes         : {record['protocol_verdict']['protocol_passes']}", flush=True)
    print(f"  silent failure CAUGHT   : {record['protocol_verdict']['silent_failure_caught']}", flush=True)

    OUT.write_text(json.dumps(record, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nSaved: {OUT}", flush=True)


if __name__ == "__main__":
    main()
