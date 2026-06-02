# HANDOFF — extract these projects into standalone repos

**Read this first, local Claude.** You are running on Keyan's machine (or any
environment) with **full access to his GitHub account `Keyan-sm`** — not the
restricted, single-repo scope that produced this folder.

## Context / why this folder exists
These projects were built in a Claude Code **web** session whose GitHub scope was
locked to a single repo (`Keyan-sm/DailyBrew`). That session could not create new
repos (`POST /user/repos` → 403) or touch other repos, and its network allowlist
blocked arXiv/Hugging Face, so papers were verified via web search rather than
read in full. The projects were **incubated as subfolders inside DailyBrew** as a
staging area. They do **not** belong in DailyBrew long-term.

Your job: promote each subfolder to its **own standalone public repo** under
`Keyan-sm`, then **remove this `playground/` folder from DailyBrew**.

## The goal these serve
Keyan is applying to **OpenAI's "Codex for Open Source"** program
(`https://openai.com/form/codex-for-oss/`) for 6 months of free ChatGPT Pro +
Codex. The bar: an active GitHub with at least one genuinely useful public
project. Each project here faithfully implements published methods (see
`RESEARCH_NOTES.md`) and is honestly scoped.

## What's here
| Folder | Becomes repo | Implements | Status |
| --- | --- | --- | --- |
| `frugal-cascade/` | `Keyan-sm/frugal-cascade` | FrugalGPT cascade + RouteLLM routing | MVP, **6 tests pass**, offline |
| `virtual-context/` | `Keyan-sm/virtual-context` | MemGPT external context + Generative-Agents retrieval | MVP, **6 tests pass**, offline |
| `ung-vol-surface-polish/` | (applies to existing `Keyan-sm/ung-vol-surface`) | — | Draft README to verify + apply |

---

## Procedure

### A. Publish `frugal-cascade` and `virtual-context` as new repos
For each folder (example shown for `frugal-cascade`):

```bash
# 1. Verify it still works before publishing
cd playground/frugal-cascade
pip install -e ".[dev]" && pytest -q        # expect: 6 passed

# 2. Copy OUT of the DailyBrew tree to a clean location
cp -r ../../playground/frugal-cascade ~/repos/frugal-cascade
cd ~/repos/frugal-cascade

# 3. Fresh git history (do NOT carry DailyBrew's history)
git init -b main && git add -A
git commit -m "Initial release: FrugalGPT-style LLM cascade (v0.1.0)"

# 4. Create the repo and push
gh repo create Keyan-sm/frugal-cascade --public --source=. --remote=origin --push \
  --description "FrugalGPT-style LLM cascade + RouteLLM-style routing: cheap model first, escalate on low confidence."

# 5. Topics + release tag
gh repo edit Keyan-sm/frugal-cascade --add-topic llm,llm-cascade,frugalgpt,routellm,llm-routing,cost-optimization,llmops
git tag v0.1.0 && git push origin v0.1.0
```

Repeat for `virtual-context`:
- description: `MemGPT-style external memory for LLM agents, with Generative-Agents retrieval (relevance + recency + importance).`
- topics: `llm,agents,memory,memgpt,generative-agents,context-window,sqlite`
- commit: `Initial release: MemGPT-style virtual context memory (v0.1.0)`

> You may use your GitHub tools (create_repository, push_files, …) instead of
> `gh` — same result.

### B. Polish the existing `ung-vol-surface` repo
Follow `ung-vol-surface-polish/NOTES_FOR_LOCAL_CLAUDE.md`: read the real source,
fix every `TODO` in the draft README, commit it, add topics, ensure it's public
with a passing smoke test.

### C. Clean up DailyBrew
Once the two repos exist and are pushed:
```bash
cd <DailyBrew checkout>
git rm -r playground CODEX_OSS_APPLICATION_PLAN.md
git commit -m "Remove incubator: projects promoted to standalone repos"
git push
```

### D. Profile polish
- Create `Keyan-sm/Keyan-sm` profile README (text below).
- Pin: `frugal-cascade`, `virtual-context`, `ung-vol-surface`, + 3 other real repos.

---

## Application form — ready-to-paste answers
Lead with **`frugal-cascade`** (clearest paper grounding + broad usefulness).

**Primary project URL:** `https://github.com/Keyan-sm/frugal-cascade`

**Why does this project matter? (draft — edit to taste, keep it true)**
> frugal-cascade is an open implementation of the FrugalGPT cascade (Chen,
> Zaharia & Zou, 2023): it sends each request to a cheap model first and
> escalates to a stronger one only when the answer scores poorly, cutting LLM
> cost without giving up quality on hard prompts. It also includes a
> RouteLLM-style single-shot router. It's MIT-licensed, dependency-free, tested,
> and runs offline via a mock provider, with OpenAI/Anthropic adapters. I keep
> two companion tools: virtual-context (MemGPT-style external memory for agents)
> and ung-vol-surface (an SVI options-vol-surface fitter).

**Honesty guardrails (important):**
- The READMEs already separate "faithful to the paper" from "our heuristic
  extension," and label the synthetic eval as synthetic. Keep that. Do not
  upgrade the synthetic 32% number into a benchmark claim.
- Do **not** fabricate stars/downloads. Answer truthfully (likely 0 at submit).
- You may honestly ask real people to try and star the repos.

## Suggested `Keyan-sm/Keyan-sm` profile README
```markdown
### Hi, I'm Keyan 👋
Quant + ML, building practical tooling for LLM agents — usually by implementing
a paper and keeping it honest.

- ⚡ [frugal-cascade](https://github.com/Keyan-sm/frugal-cascade) — FrugalGPT-style LLM cascade
- 🧠 [virtual-context](https://github.com/Keyan-sm/virtual-context) — MemGPT-style agent memory
- 📈 [ung-vol-surface](https://github.com/Keyan-sm/ung-vol-surface) — SVI options vol surface
```

## Provenance
Verified papers + the faithful-vs-extension breakdown are in `RESEARCH_NOTES.md`
and in each repo's README.
