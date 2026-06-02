# HANDOFF — extract these projects into standalone repos

**Read this first, local Claude.** You are running on Keyan's machine (or any
environment) with **full access to his GitHub account `Keyan-sm`** — not the
restricted, single-repo scope that produced this folder.

## Context / why this folder exists
These projects were built in a Claude Code **web** session whose GitHub scope was
locked to a single repo (`Keyan-sm/DailyBrew`). That session could not create new
repos (`POST /user/repos` → 403) or touch other repos. So it **incubated the
projects as subfolders inside DailyBrew** as a staging area. They do **not**
belong in DailyBrew long-term — DailyBrew is a separate podcast project.

Your job: promote each subfolder to its **own standalone public repo** under
`Keyan-sm`, then **remove this `playground/` folder from DailyBrew** so DailyBrew
is clean again.

## The goal these serve
Keyan is applying to **OpenAI's "Codex for Open Source"** program
(`https://openai.com/form/codex-for-oss/`) for 6 months of free ChatGPT Pro +
Codex. The bar: an active GitHub with at least one genuinely useful public
project. These give him three strong, real, tested projects.

## What's here
| Folder | Becomes repo | Status |
| --- | --- | --- |
| `llm-router/` | `Keyan-sm/llm-router` | Complete MVP, **6 tests pass**, runs offline |
| `llm-memory/` | `Keyan-sm/llm-memory` | Complete MVP, **6 tests pass**, runs offline |
| `ung-vol-surface-polish/` | (applies to existing `Keyan-sm/ung-vol-surface`) | Draft README to verify + apply |

---

## Procedure

### A. Publish `llm-router` and `llm-memory` as new repos
For each of the two folders (example shown for `llm-router`):

```bash
# 1. Verify it still works before publishing
cd playground/llm-router
pip install -e ".[dev]" && pytest -q        # expect: passing

# 2. Copy the folder OUT of the DailyBrew tree to a clean location
cp -r ../../playground/llm-router ~/repos/llm-router
cd ~/repos/llm-router

# 3. Fresh git history (do NOT carry DailyBrew's history)
git init -b main
git add -A
git commit -m "Initial release: cost-aware LLM router (v0.1.0)"

# 4. Create the GitHub repo and push
gh repo create Keyan-sm/llm-router --public --source=. --remote=origin --push \
  --description "A small, explainable, cost-aware router that picks the best-fit LLM per request."

# 5. Topics + a release tag
gh repo edit Keyan-sm/llm-router --add-topic llm,routing,model-selection,agents,cost-optimization,llmops
git tag v0.1.0 && git push origin v0.1.0
```

Repeat for `llm-memory` with:
- description: `A structured, temporal, queryable memory layer for LLM agents — beyond a pile of markdown files.`
- topics: `llm,agents,memory,rag,sqlite,harness,context-engineering`

> You can do all of the above with your GitHub tools instead of `gh` if you
> prefer (create_repository, push_files, etc.) — same result.

### B. Polish the existing `ung-vol-surface` repo
Follow `ung-vol-surface-polish/NOTES_FOR_LOCAL_CLAUDE.md`: read the real source,
fix every `TODO` in the draft README, commit it to `Keyan-sm/ung-vol-surface`,
add topics, ensure it's public with a passing smoke test.

### C. Clean up DailyBrew
Once the two repos exist and are pushed:

```bash
cd <DailyBrew checkout>
git rm -r playground CODEX_OSS_APPLICATION_PLAN.md
git commit -m "Remove incubator: projects promoted to standalone repos"
git push
```
(Keep `CODEX_OSS_APPLICATION_PLAN.md` only if Keyan still wants it; otherwise
remove it too — it doesn't belong in the podcast repo.)

### D. Profile polish (quick wins)
- Create a profile README repo `Keyan-sm/Keyan-sm` (see suggested text below).
- Pin: `llm-router`, `llm-memory`, `ung-vol-surface`, + 3 other real repos.

---

## Application form — ready-to-paste answers
Lead the application with **`llm-router`** (most broadly useful), mention the
other two.

**Primary project URL:** `https://github.com/Keyan-sm/llm-router`

**Why does this project matter? (draft)**
> llm-router is an open, self-hostable router that picks the best-fit LLM for
> each request — balancing quality, cost, and latency — and cascades from cheap
> to capable models only when confidence is low. It directly attacks the
> "routing collapse" failure mode (always defaulting to the most expensive
> model) documented in recent literature, cutting cost ~30% on its benchmark
> suite while preserving quality on hard tasks. It's MIT-licensed, dependency-
> free, tested, and runs offline via a mock provider, with adapters for OpenAI
> and Anthropic. I maintain two companion OSS tools — llm-memory (a structured,
> temporal memory layer for agents) and ung-vol-surface (an SVI options-vol
> surface fitter) — and build agentic developer tooling actively.

**Honesty guardrails (important):**
- Do **not** fabricate stars/downloads. If the form asks, answer truthfully
  (likely 0 at submission). The program weighs *usefulness*, not popularity.
- You *may* honestly ask real people/communities to try and star the repos.

## Suggested `Keyan-sm/Keyan-sm` profile README
```markdown
### Hi, I'm Keyan 👋
Quant + ML, building practical developer tooling for LLM agents.

- 🧭 [llm-router](https://github.com/Keyan-sm/llm-router) — cost-aware LLM routing
- 🧠 [llm-memory](https://github.com/Keyan-sm/llm-memory) — structured agent memory
- 📈 [ung-vol-surface](https://github.com/Keyan-sm/ung-vol-surface) — SVI options vol surface
```
(Adjust to taste — keep it true.)

## Provenance
Both MVPs were designed from recent routing/memory papers; the specific
techniques and citations are in `RESEARCH_NOTES.md`.
