# ung-vol-surface

**Builds and fits an implied-volatility surface for UNG (United States Natural
Gas Fund) options using the SVI parameterization, then flags options that look
mispriced relative to the fitted surface.**

> ⚠️ Local Claude: verify every command, path, and claim below against the
> actual code before publishing — see `NOTES_FOR_LOCAL_CLAUDE.md`. Replace the
> `TODO` markers with the real entry points.

## What it does

- Pulls UNG option chains <!-- TODO: name the data source (yfinance? broker API? CSV?) -->
- Computes implied volatilities across strikes and expiries.
- Fits the **SVI (Stochastic Volatility Inspired)** parameterization to each
  expiry slice, producing a smooth, arbitrage-aware volatility smile.
- Assembles the per-expiry slices into a full implied-volatility **surface**.
- Detects **mispricings**: options whose market IV deviates materially from the
  fitted surface, surfacing candidate rich/cheap contracts.

## Why SVI

SVI fits the volatility smile with five interpretable parameters per slice and,
with the right constraints, avoids static arbitrage. That makes it a standard,
defensible choice for turning a noisy set of quoted option prices into a clean,
queryable surface.

## Install

```bash
git clone https://github.com/Keyan-sm/ung-vol-surface.git
cd ung-vol-surface
pip install -r requirements.txt        # TODO: confirm requirements file exists
```

## Usage

```bash
# TODO: replace with the real entry point(s), e.g.:
python -m ung_vol_surface fit --expiry 2026-07-17
python -m ung_vol_surface mispricing --threshold 0.05
```

```python
# TODO: confirm the public API and show a minimal example that actually runs.
```

## How it works

1. **Data ingestion** – <!-- TODO -->
2. **IV computation** – invert Black-76 / Black-Scholes per contract.
3. **SVI calibration** – least-squares fit of the five SVI params per expiry,
   with no-arbitrage constraints.
4. **Surface assembly** – interpolate across expiries.
5. **Mispricing scan** – compare market IV vs fitted IV; rank by deviation.

## Limitations & disclaimer

Research/educational tool, **not investment advice**. Fits are only as good as
the input quotes; illiquid strikes can distort the surface.

## License

MIT
