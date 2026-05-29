"""Generate Figure 2: latency distribution bar chart from real Q0 data."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = json.load(open(r'C:\tmp\darkweb-audit\test_results\q00_precheck.json', encoding='utf-8'))
engines = data['result']['engines']
live = [(e['name'], e['latency_ms']) for e in engines if e.get('status') == 'up' and e.get('latency_ms')]
live.sort(key=lambda x: x[1])
names = [n for n, _ in live]
lats  = [l for _, l in live]
colors = ['#1f77b4' if n != 'Ahmia-clearnet' else '#d62728' for n in names]

fig, ax = plt.subplots(figsize=(8.5, 4.6), dpi=160)
ax.barh(range(len(names)), lats, color=colors, edgecolor='black', linewidth=0.4)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=9)
ax.set_xlabel('Q0 round-trip latency (ms)', fontsize=10)
ax.set_title('Q0 engine latencies (live cohort, ascending)', fontsize=11)
ax.invert_yaxis()
ax.grid(axis='x', linestyle='--', alpha=0.4)
for i, v in enumerate(lats):
    ax.text(v + max(lats) * 0.01, i, f'{v} ms', va='center', fontsize=8)

onion_lats = [l for n, l in live if n != 'Ahmia-clearnet']
mean_onion = sum(onion_lats) / len(onion_lats)
n = len(onion_lats)
sample_sd = (sum((x - mean_onion) ** 2 for x in onion_lats) / (n - 1)) ** 0.5
ax.axvline(mean_onion, color='black', linestyle=':', linewidth=1.2,
           label=f'.onion mean = {mean_onion:.0f} ms (sample SD {sample_sd:.0f}, n={n})')

from matplotlib.patches import Patch
legend_items = [
    Patch(facecolor='#1f77b4', edgecolor='black', label='.onion engine'),
    Patch(facecolor='#d62728', edgecolor='black', label='Ahmia-clearnet (HTTPS)'),
]
ax.legend(handles=legend_items + [ax.lines[0]], loc='lower right', fontsize=8)

plt.tight_layout()
out = r'E:\Bildiri\01-darkweb-search-engine-benchmark\figures\fig2_latency_distribution.png'
plt.savefig(out, bbox_inches='tight', dpi=160)
print(f'mean={mean_onion:.1f}, sample_sd={sample_sd:.1f}, n={n}, saved={out}')
