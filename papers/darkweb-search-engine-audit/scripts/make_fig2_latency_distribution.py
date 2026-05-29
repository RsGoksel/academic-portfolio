"""Generate Figure 2: latency distribution bar chart.

v2 fix:
  - Legend moved outside the plot area (lower right was overlapping
    the longest bars).
  - x-axis extended +12% past the max bar so the value label "6307 ms"
    is not clipped at the right edge.
  - Slightly wider figure to leave room for the legend below.
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

data = json.load(open(r"C:\tmp\darkweb-audit\test_results\q00_precheck.json", encoding="utf-8"))
engines = data["result"]["engines"]
live = [(e["name"], e["latency_ms"]) for e in engines if e.get("status") == "up" and e.get("latency_ms")]
live.sort(key=lambda x: x[1])
names = [n for n, _ in live]
lats = [l for _, l in live]
colors = ["#1f77b4" if n != "Ahmia-clearnet" else "#d62728" for n in names]

fig, ax = plt.subplots(figsize=(9.0, 5.0), dpi=160)
ax.barh(range(len(names)), lats, color=colors, edgecolor="black", linewidth=0.4)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=9)
ax.set_xlabel("Q0 round-trip latency (ms)", fontsize=10)
ax.set_title("Q0 engine latencies (live cohort, ascending)", fontsize=11)
ax.invert_yaxis()
ax.grid(axis="x", linestyle="--", alpha=0.4)

# Extend x-axis to leave room for the value labels at the right edge
xmax_val = max(lats)
ax.set_xlim(0, xmax_val * 1.12)

# Value labels
for i, v in enumerate(lats):
    ax.text(v + xmax_val * 0.012, i, f"{v} ms", va="center", fontsize=8)

# Compute sample SD line
onion_lats = [l for n, l in live if n != "Ahmia-clearnet"]
mean_onion = sum(onion_lats) / len(onion_lats)
n = len(onion_lats)
sample_sd = (sum((x - mean_onion) ** 2 for x in onion_lats) / (n - 1)) ** 0.5
ax.axvline(mean_onion, color="black", linestyle=":", linewidth=1.2)

# Build legend outside the plot (bottom)
legend_items = [
    Patch(facecolor="#1f77b4", edgecolor="black", label=".onion engine"),
    Patch(facecolor="#d62728", edgecolor="black", label="Ahmia-clearnet (HTTPS)"),
    plt.Line2D([0], [0], color="black", linestyle=":", linewidth=1.2,
               label=f".onion mean = {mean_onion:.0f} ms (sample SD {sample_sd:.0f}, n={n})"),
]
ax.legend(handles=legend_items, loc="upper center", bbox_to_anchor=(0.5, -0.10),
          ncol=3, fontsize=8, frameon=False)

plt.tight_layout()
out = r"E:\Bildiri\01-darkweb-search-engine-benchmark\figures\fig2_latency_distribution.png"
plt.savefig(out, bbox_inches="tight", dpi=160)
print(f"mean={mean_onion:.1f}, sample_sd={sample_sd:.1f}, n={n}, saved={out}")
