# Style notes — dark-web / Tor measurement literature

Derived from close reading of the six downloaded references (Christin 2012 / arXiv:1207.7139; Biryukov, Pustogarov, Thill & Weinmann 2014 / arXiv:1308.6768; Avarikioti, Brunner, Kiayias, Wattenhofer & Zindros 2018 / arXiv:1811.01348; Al-Nabki, Fidalgo, Alegre & Chaves 2019 / arXiv:1910.02332; Fidalgo, Vasco-Carofilis, Jáñez-Martino & Blanco-Medina 2020 / arXiv:2005.10086; Thakur, Reimers, Rücklé, Srivastava & Gurevych 2021 / arXiv:2104.08663).

## 1. Opening sentence patterns

The field consistently opens with a one-sentence framing of the anonymity layer, followed by a tension between legitimate use and abuse.

- "Tor hidden services allow running Internet services while protecting the location of the servers" (Biryukov et al.).
- "The Onion Router (Tor) network ... gives the end-users a high level of privacy and anonymity" (Al-Nabki et al.).
- "We perform a comprehensive measurement analysis of Silk Road, an anonymous, international online marketplace" (Christin).

The tension sentence almost always follows: "However, providing location privacy ... also makes Tor hidden services an attractive platform for every kind of imaginable shady service" (Biryukov). Pattern: definition → "However" → abuse vector → measurement motivation.

## 2. Methodology section structure

Measurement-style papers follow a tight order:

1. Tor setup paragraph (relay/circuit configuration; named software versions; bootstrap behaviour).
2. Seed / sampling description, with explicit count of starting addresses.
3. Crawling or probing module decomposition (Avarikioti uses a four-module list: Conductor, Network, Parser, Database).
4. Per-engine or per-service descriptor of what was recorded.
5. Subsection on filtering, deduplication, and ethical exclusions.

Avarikioti et al. is the cleanest template — section 2 ("Crawling the Darknet") opens with a one-line goal, then enumerates modules in bold, then narrates the encountered problems. We follow that template in §3.

## 3. Hedging and modal vocabulary

Hedges are used aggressively because ground truth is unavailable on Tor. Common phrasings:

- "To the best of our knowledge..." (Al-Nabki, Thakur).
- "Our results suggest..." (Fidalgo).
- "Within the scope of this snapshot..." / "at the time of writing" (Biryukov uses footnote dates explicitly).
- "We were able to..." instead of "we proved" (Avarikioti).
- "The most plausible explanation..." (Christin uses this when interpreting vendor churn).
- "We make no claim about the population of all hidden services..." (Avarikioti, Section 3).

Strong claims appear only when supported by a number; weak claims are wrapped in "appears", "suggests", "is consistent with".

## 4. Domain-specific vocabulary

| Term | Use |
|---|---|
| hidden service / onion service | Interchangeable; "onion service" is post-2017 Tor Project terminology, "hidden service" is the pre-v3 legacy term. Papers use both. |
| descriptor / HSDir | Used when discussing service discovery internals. |
| clearnet | Always lower-case, no hyphen. Contrasted with "darknet" or "Tor network". |
| crawl / probe | "Probe" is liveness only; "crawl" implies recursive link-following. |
| reachability / liveness | "Reachable" = TCP/SOCKS handshake; "live" = full HTTP 200 + parseable body. |
| circuit hygiene | Avoiding cross-query contamination via `NEWNYM`. |
| churn | Used both for vendors and for services going off-line. |
| seed list | Curated bootstrap set of .onion URLs. |
| SERP | Search engine results page — used informally. |
| recall / precision | Standard IR terms; recall is rarely measurable in darknet IR because there is no ground-truth corpus. |

## 5. How they handle limitations and ethics

Every paper ends with an explicit "Limitations" or "Discussion" paragraph naming the boundary of the claim. Common pattern:

- N is small; replication needed across larger samples.
- Single observation window; longitudinal study needed.
- Tor exit selection biases timing measurements (Christin and Avarikioti both note this).
- No human-in-the-loop relevance judgements; we rely on automated proxies.

Ethics paragraphs are short but explicit. Christin opens his ethics paragraph with: "We discuss economic and policy implications of our analysis and results, including ethical considerations for future research in this area." Biryukov hedges around deanonymisation by claiming the attack is "opportunistic", framing it as a measurement side-effect rather than an offensive tool. Avarikioti explicitly excludes CSAM-related categories from the published classifier outputs.

The common move is: (1) state the pre-registered ethical boundary; (2) name what was *not* done; (3) cite IRB or institutional process when applicable.

## 6. Citation patterns

- Inline citation style: numbered brackets [1], [2] in the IEEE/ACM venues; (Author Year) in the SAGE / Tandfonline policy venues.
- First-cite-after-claim discipline: claims like "the number of v3 onion addresses has grown from 30K to 90K between April 2015 and October 2019" (Al-Nabki) are always immediately followed by a footnote URL or a citation to Tor metrics.
- Self-citation is common when one research group has multiple iterations on a DUTA-like dataset; Al-Nabki cites his own 2017 DUTA paper to introduce DUTA-10K.

## 7. Phrases to avoid

The downloaded papers do **not** use:

- "delve into", "leverage" (used only in BEIR; rare in measurement work), "robust" (used cautiously, only with numeric backing), "comprehensive" (used by Christin but only with explicit corpus count), "this paper aims to..."
- Em-dashes as sentence breaks (n-dashes appear in numeric ranges only).
- First-person singular ("I") — even Christin's single-author paper uses "we" throughout.
- Marketing-style adverbs ("seamlessly", "elegantly", "powerfully").

## 8. Title patterns

The titles are concrete and noun-heavy:

- "Content and popularity analysis of Tor hidden services"
- "Traveling the Silk Road: A measurement analysis of a large anonymous online marketplace"
- "Structure and content of the visible Darknet"
- "Content-based features to rank influential hidden services of the Tor darknet"
- "Classifying suspicious content in Tor darknet"

Pattern: <noun phrase describing the artefact studied>: <method or framing>. Our title — "A Reproducible Benchmark of 18 Tor Search Engines: Liveness, Latency, and Silent Failure Modes" — follows that pattern.
