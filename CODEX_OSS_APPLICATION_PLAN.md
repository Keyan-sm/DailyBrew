# Plan: Get approved for OpenAI "Codex for Open Source" (6 months ChatGPT Pro free)

> Goal: Free 6 months of ChatGPT Pro + Codex (~$1,200 value) to use as extra
> agentic-coding capacity alongside Claude Pro.

> **Status update:** The two flagship projects below are now built and live in
> `playground/`, each implementing a verified published method:
> **`frugal-cascade`** (FrugalGPT cascade + RouteLLM routing) and
> **`virtual-context`** (MemGPT external memory + Generative-Agents retrieval).
> See `playground/HANDOFF.md` for promoting them to standalone repos and
> `playground/RESEARCH_NOTES.md` for the citations. Where this doc says
> "llm-router"/"LLM memory layer" below, read `frugal-cascade`/`virtual-context`.

---

## 0. Reality check on that tweet (read this first)

The offer is **real**, but the tweet oversells it.

- **What's real:** OpenAI is giving **6 months of ChatGPT Pro (~$1,200) + Codex
  access** to open-source maintainers. No credit card, global, apply via a form.
  Official program: **Codex for Open Source** → `https://openai.com/form/codex-for-oss/`
  (docs: `https://developers.openai.com/community/codex-for-oss`).
- **What's hype:** "They approve everyone with an active GitHub" / "vibe-code 3
  throwaway projects tonight." The form explicitly asks for your repo's **stars,
  monthly downloads, and *why the project matters*.** It's aimed at people who
  *maintain something useful*, not at freshly-spawned AI repos. Ten obviously-
  generated toy repos created the night before the application is the **weakest**
  possible signal and can read as gaming it.
- **Note:** The tweet links only to the **form**, not to any "guy's GitHub" — so
  there was no profile to reverse-engineer. The plan below is built from the
  actual program eligibility instead.

**Bottom line:** quality over quantity. The bar is *"at least one genuinely
useful public project + a credibly active profile."* You're already most of the
way there — this is polish + one real flagship, not a farm of junk.

---

## 1. Your starting position (audit)

GitHub: `Keyan-sm` — account since 2023, 14 repos (5 public), real quant/ML work.

**Genuine assets already public:**
- `ung-vol-surface` — UNG options vol surface, SVI fitting + mispricing. *Real,
  useful, nicely scoped. This is your current best application candidate.*
- `COINS_Trade_Analysis`, `Image-Recognition-CNN` — real, show range.

**Quick wins sitting private** (flip to public after a cleanup pass):
- `LLMToClipboard`, `KCW`, others — make presentable, then publish.

**Gaps to close:** no profile README, nothing pinned, no stars/traction, thin
READMEs, no license/`pyproject` on most repos. All cheap to fix.

---

## 2. Strategy

Make the profile read as *"an active dev who ships and maintains useful tools,"*
then apply on the strength of **one flagship**. Your two real interests are
*perfect* flagship material — so they're not "for later," they're the centerpiece:

1. **LLM router** (OpenRouter-style: route a request to the best-fit model per
   task/cost/latency). Hot, obviously useful, demoable quickly.
2. **LLM memory layer** (durable, structured memory for agents — beyond a pile
   of markdown files).

Pick **#1 as the flagship** (tighter scope, easy to demo, easy "why it matters")
and keep **#2 as the strong second repo**. The "bullshit" repos become a small
set of *small-but-real* utilities — not garbage, just modest.

---

## 3. Execution plan

### Phase A — Profile credibility (≈1 evening)
- [ ] Create `Keyan-sm/Keyan-sm` profile README (who you are: quant/ML, what you
      build, links to flagship).
- [ ] Add to every public repo you keep: clear README (what/why/install/usage/
      example), `LICENSE` (MIT), topics/tags.
- [ ] Pin 6 best repos (flagship first).
- [ ] Clean + publish 1–2 of the private repos that are genuinely useful.

### Phase B — Flagship: LLM router (the real one) (≈1–2 evenings)
Working name e.g. `llm-router` / `smart-route`.
- [ ] MVP: config-driven router that picks a model per request using simple,
      explainable rules (task type, prompt length/cost, latency budget,
      fallback chain) across ≥2 providers (OpenAI + Anthropic, OpenRouter-compatible).
- [ ] Real usability: pip-installable, CLI + tiny Python API, `.env` keys,
      example configs, a benchmark/eval script showing routing decisions.
- [ ] **Excellent README** with a diagram, quickstart, and a "why" section.
- [ ] Tests + GitHub Actions CI badge (cheap credibility).
- [ ] Tag a `v0.1.0` release.

### Phase C — Second repo: LLM memory layer (optional before applying)
- [ ] MVP: structured memory store for agents (e.g., SQLite/vector-backed,
      write/recall/summarize API) with a Claude/Codex adapter. Even a focused
      MVP strengthens the "I work in this space" story.

### Phase D — Modest supporting repos (the acceptable "filler", still real)
Pick 1–2, keep them small but honest and documented:
- [ ] Polish + publish `LLMToClipboard`.
- [ ] One small CLI you'd actually use.

### Phase E — Apply
- [ ] Fill `https://openai.com/form/codex-for-oss/`.
- [ ] Lead with the **flagship** repo link.
- [ ] "Why it matters" draft: *"An open, self-hostable LLM router that picks the
      cheapest/best model per task — cutting cost and lock-in for devs building
      agentic apps. Actively maintained, pip-installable, with evals."*
- [ ] Stars: ask a few people / relevant communities to star honestly (don't
      fake). Even single-digit stars + good README beats 0 + empty repo.

---

## 4. Honest timeline
- **Minimum viable application:** Phase A + B = ~2–3 focused evenings. Apply.
- **Stronger application:** add Phase C/D over the following week.
- Don't wait for perfection — the program may close; ship MVP, apply, keep iterating.

---

## 5. What I (Claude) can do for you

Confirmed capabilities in this environment:
- **Create new repos directly on your account** (`Keyan-sm`) — yes, I have repo-
  creation access, not just this one repo. I can also create branches, push
  files, open PRs.
- Scaffold the flagship router (code, tests, CI, README, examples) and push it.
- Write the profile README and clean up / document existing repos.
- Draft the application form answers.

**Caveat:** creating public repos and pushing code to your account is outward-
facing and permanent, so I'll confirm names/visibility with you before creating
anything public. I won't fake stars/traction — that's on real merit only.

### Suggested first action when you're ready
Say the word and I'll: (1) create `llm-router` (private first), (2) scaffold the
MVP + README + CI, (3) create your `Keyan-sm/Keyan-sm` profile README — then you
review before anything goes public.
