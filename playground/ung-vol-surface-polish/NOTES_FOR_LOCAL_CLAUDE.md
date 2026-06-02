# Notes for local Claude: polishing `ung-vol-surface`

This folder holds a **draft** README for the existing public repo
`Keyan-sm/ung-vol-surface`. It was written from the repo *description* only —
the sandbox that produced it could not read that repo (out of session scope), so
**everything must be verified against the real code.**

## Tasks
1. Read the actual `ung-vol-surface` source. Replace every `TODO` / HTML comment
   in `README.md` with the real data source, install steps, entry points, and a
   runnable example. Delete claims the code doesn't support.
2. Add the polished `README.md` to the repo root (it currently has only a
   one-line description). Keep a `LICENSE` (MIT) if missing.
3. Add repo **topics** on GitHub: `options`, `volatility-surface`, `svi`,
   `quantitative-finance`, `derivatives`, `python`.
4. If there are no tests, add at least one smoke test (e.g. SVI fit on a tiny
   synthetic slice returns finite params) so the repo shows a green check.
5. Confirm the default branch is `main` and the repo is **public**.

## Why
`ung-vol-surface` is the strongest *existing, genuinely useful* project for the
OpenAI Codex-for-OSS application (see `../HANDOFF.md`). A clear README + topics +
a passing test materially strengthen it with ~10 minutes of work.
