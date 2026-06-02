# Context — why this branch exists

Single source of truth for the goal, the plan, the constraints, and the
decisions behind everything on the `claude/token-increase-plan-*` branch. Read
this first if you're picking the work up cold.

## High-level goal
Keyan is on Claude Pro and wants **more agentic-coding capacity**. A tweet
pointed at OpenAI's **"Codex for Open Source"** program
(`https://openai.com/form/codex-for-oss/`): ~6 months of free ChatGPT Pro +
Codex (~$1,200) for developers with an **active GitHub and ≥1 genuinely useful
public project**. The goal is to get approved by strengthening Keyan's GitHub
with **real, paper-grounded OSS projects** — not filler.

Two domains Keyan actually cares about, chosen so nothing is contrived:
1. **LLM routing** (route a request to the best-fit model by cost/quality).
2. **Better-than-markdown LLM memory** for agents/harnesses.

## The plan Keyan gave (his directives)
- Use **DailyBrew as a temporary playground**: build the projects as subfolders
  here, because this session's GitHub access is locked to this one repo.
- Write a **handoff doc** so a future local Claude (with full GitHub access) can
  split each folder into its **own standalone repo** and then remove it from
  DailyBrew.
- **Two projects, not one** — plus **polish the existing `ung-vol-surface`** repo.
- **Ground each project in a published paper/method.** The README must say what
  we implement and **what we did differently**, honestly.
- Repos must be **legible at a glance** and not blend into the bulk. Names should
  be **technical (named after the method)** — not slop/brand words, not generic.
- **No contrivance.** Anti-slop writing.

## Constraints discovered (the real limits this session ran into)
- **GitHub scope** is locked to `keyan-sm/dailybrew`; creating new repos is
  blocked (`POST /user/repos` → 403). Hence the playground-then-extract approach.
- **Network allowlist** blocks arXiv / Hugging Face / ar5iv / Semantic Scholar
  (`curl` → "Host not in allowlist"; the page-fetcher → 403). Papers were
  therefore **verified via web search, not read in full**. Local Claude can open
  them directly to double-check.
- The "stop slop" writing skill is **not installed** in this session; prose was
  written to that standard by hand instead.

## Key decisions & rationale
- **Quality over quantity.** The tweet oversells ("they approve everyone / vibe-
  code 10 repos tonight"). The form actually weighs *usefulness* (it asks "why
  does this project matter"). So: two real, paper-grounded projects + one polished
  existing repo beats a pile of throwaways.
- **Correction made mid-effort.** The first build pass over-claimed paper
  fidelity and cited unverifiable 2026 arXiv IDs from search snippets. Those were
  **removed** and the projects **re-anchored on four verified canonical papers**,
  with honest "faithful vs. our extension" tables and the synthetic eval labeled
  as synthetic. (See `playground/RESEARCH_NOTES.md`.)
- **Names** are method-derived: `frugal-cascade` (FrugalGPT) and
  `virtual-context` (MemGPT) — chosen over generic (`llm-router`) and brandable
  (`ballast`/`engram`).

## Current state
| Path | What it is | Status |
| --- | --- | --- |
| `playground/frugal-cascade/` | FrugalGPT cascade + RouteLLM routing | MVP, 6 tests pass, offline |
| `playground/virtual-context/` | MemGPT external context + Generative-Agents retrieval | MVP, 6 tests pass, offline |
| `playground/ung-vol-surface-polish/` | Draft README + notes for the existing repo | Needs verifying against real code |
| `CODEX_OSS_APPLICATION_PLAN.md` | Strategy + reality check | Partly superseded by this file |
| `playground/HANDOFF.md` | Extraction steps + form answers | Operative |
| `playground/RESEARCH_NOTES.md` | The four verified papers + provenance | Operative |

## Next steps
1. **Local Claude:** follow `playground/HANDOFF.md` — publish `frugal-cascade`
   and `virtual-context` as standalone repos, polish `ung-vol-surface`, clean the
   playground out of DailyBrew.
2. **Keyan:** submit `https://openai.com/form/codex-for-oss/`, leading with
   `frugal-cascade`. Don't fabricate stars/usage; answer truthfully.
