# Research grounding — the papers these projects implement

Each project implements mechanisms from **specific, verifiable, peer-known
papers**. Every citation below was confirmed to exist with its stated method and
numbers (via search — direct PDF access is blocked by this environment's network
allowlist, so the full texts were not read end-to-end; claims are taken from the
abstracts and widely-reproduced summaries).

> Earlier drafts cited several 2026 arXiv IDs that could not be opened or
> verified. Those were removed. Only the four papers below are cited, and only
> for claims they actually make.

## frugal-cascade
| Paper | Verified | Method we implement | Their reported result |
| --- | --- | --- | --- |
| **FrugalGPT** — Chen, Zaharia, Zou (Stanford, 2023), [2305.05176](https://arxiv.org/abs/2305.05176) | ✅ title/authors/year/abstract | LLM **cascade**: cheap→expensive with a scorer that accepts or escalates | up to **98%** cost cut matching GPT-4; +4% acc at equal cost |
| **RouteLLM** — Ong et al. (Berkeley/LMSYS, 2024), [2406.18665](https://arxiv.org/abs/2406.18665) | ✅ title/authors/year/abstract | Single-shot **router** predicting whether a query needs the strong model | 95% GPT-4 quality at ~26% of GPT-4 calls; up to 85% cheaper on MT-Bench |

**Our additions (not from these papers):** the accept/escalate scorer is a
confidence heuristic (FrugalGPT trains a DistilBERT scorer); the router is
rule-based (RouteLLM trains on preference data); the anti-collapse cost penalty
is ours. We implement the *mechanisms*; the learned components are future work.

## virtual-context
| Paper | Verified | Method we implement | Core idea |
| --- | --- | --- | --- |
| **MemGPT** — Packer et al. (Berkeley, 2023), [2310.08560](https://arxiv.org/abs/2310.08560) | ✅ title/authors/year/abstract | **External context** outside the prompt + memory edited via **function/tool calls** | OS virtual memory analogy: main context (RAM) ↔ external context (disk) |
| **Generative Agents** — Park et al. (Stanford, 2023), [2304.03442](https://arxiv.org/abs/2304.03442) | ✅ title/authors/year/abstract | Retrieval score = **relevance + recency + importance** | memory stream; relevance=cosine, recency=exp decay, importance=1–10 |

**Our additions (not from these papers):** `supersede()` + `as_of` time-travel
recall (handling facts that change over time); markdown import/export. We do not
implement MemGPT's autonomous paging loop, and importance is set explicitly
rather than LLM-scored.

## Honest summary
- The papers are real and the mechanisms are implemented faithfully.
- The **learned/trained** parts of FrugalGPT, RouteLLM, and Generative Agents are
  replaced with transparent heuristics — clearly labeled as such in each README.
- The headline cost/quality numbers belong to the papers' own benchmarks, not to
  this code. The only number these repos measure is an illustrative synthetic
  eval, labeled as synthetic.
