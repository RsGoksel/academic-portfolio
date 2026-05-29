import sys, os, json, time, traceback
sys.path.insert(0, r'C:\tmp\darkweb-audit\repos\OnionClaw-genuine')
os.environ['TOR_SOCKS_HOST'] = '127.0.0.1'
os.environ['TOR_SOCKS_PORT'] = '9050'
os.environ['TOR_CONTROL_PORT'] = '9051'

import sicry

RESULTS_DIR = r'C:\tmp\darkweb-audit\test_results'

def save(qid, name, payload):
    p = os.path.join(RESULTS_DIR, f'{qid}_{name}.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
    sz = os.path.getsize(p)
    print(f"  -> saved {p} ({sz} bytes)")
    return sz

def run(label, fn):
    print(f"\n{'='*70}\n{label}\n{'='*70}", flush=True)
    t0 = time.time()
    try:
        result = fn()
        return {'ok': True, 'elapsed_sec': round(time.time()-t0, 2), 'result': result}
    except Exception as e:
        return {'ok': False, 'elapsed_sec': round(time.time()-t0, 2),
                'error': f'{type(e).__name__}: {e}',
                'trace': traceback.format_exc()}

# Q1: Ahmia search "machine learning"
out = run('Q1: Ahmia search "machine learning"',
          lambda: sicry.dispatch('sicry_search', {
              'query': 'machine learning',
              'engines': ['Ahmia', 'Ahmia-clearnet'],
              'max_results': 10
          }))
save('q01', 'ahmia_machine_learning', out)
print(f"  Q1 status: ok={out['ok']} elapsed={out['elapsed_sec']}s")

# Q2: Ahmia search "academic papers"
out = run('Q2: Ahmia search "academic papers"',
          lambda: sicry.dispatch('sicry_search', {
              'query': 'academic papers',
              'engines': ['Ahmia', 'Ahmia-clearnet'],
              'max_results': 10
          }))
save('q02', 'ahmia_academic_papers', out)
print(f"  Q2 status: ok={out['ok']} elapsed={out['elapsed_sec']}s")

# Q3: Fetch Tor Project hidden service homepage
TOR_PROJECT_ONION = 'http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion/'
out = run('Q3: Fetch Tor Project .onion homepage',
          lambda: sicry.dispatch('sicry_fetch', {'url': TOR_PROJECT_ONION}))
# truncate content to 4 KB if huge
if out.get('ok') and isinstance(out['result'], dict):
    for k, v in list(out['result'].items()):
        if isinstance(v, str) and len(v) > 4096:
            out['result'][k] = v[:4096] + f'\n...[truncated, full len {len(v)}]'
save('q03', 'fetch_torproject_onion', out)
print(f"  Q3 status: ok={out['ok']} elapsed={out['elapsed_sec']}s")

# Q4: Fetch DuckDuckGo onion homepage
DDG_ONION = 'https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/'
out = run('Q4: Fetch DuckDuckGo onion homepage',
          lambda: sicry.dispatch('sicry_fetch', {'url': DDG_ONION}))
if out.get('ok') and isinstance(out['result'], dict):
    for k, v in list(out['result'].items()):
        if isinstance(v, str) and len(v) > 4096:
            out['result'][k] = v[:4096] + f'\n...[truncated, full len {len(v)}]'
save('q04', 'fetch_ddg_onion', out)
print(f"  Q4 status: ok={out['ok']} elapsed={out['elapsed_sec']}s")

# Q5: Multi-engine search "open source intelligence"
out = run('Q5: Multi-engine search "open source intelligence"',
          lambda: sicry.dispatch('sicry_search', {
              'query': 'open source intelligence',
              'max_results': 10
          }))
save('q05', 'multi_engine_osint', out)
print(f"  Q5 status: ok={out['ok']} elapsed={out['elapsed_sec']}s")

print("\nALL 5 SAFE QUERIES COMPLETE.")
