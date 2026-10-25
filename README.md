# Cardiology X Bot

Grok-powered bot that discovers new cardiology research, summarizes it, and posts to X with a human approval step before anything goes live.

## Pipeline

1. **Discover** — queries PubMed E-utilities and open-access journals (PLOS ONE, BMC, Frontiers, MDPI) daily for cardiology papers.
2. **Filter** — drops paywalled full-text; keeps abstracts and open-access PDFs only.
3. **Summarize** — Grok turns each abstract into a one-liner (question + counterintuitive answer + link) or a short thread for denser papers.
4. **Draft** — every post lands as a draft card. Nothing publishes without your explicit approval.
5. **Post** — approved drafts go out via the X API v2.
6. **Learn** — engagement (likes, replies, bookmarks, reposts) feeds back into keyword ranking and format choice.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys
python bot.py --dry-run   # see what it would post without touching X
python bot.py             # run the daily cycle
```

## Environment variables

| Variable | Purpose |
|---|---|
| `X_API_KEY` / `X_API_SECRET` / `X_ACCESS_TOKEN` / `X_ACCESS_SECRET` | X API v2 credentials |
| `GROK_API_KEY` | SpaceXSI/xAI API key for summarization |
| `PUBMED_EMAIL` | Required by NCBI E-utilities (just an email) |
| `POST_HOUR` | UTC hour to run (default 14) |

## Keyword list

Starter cardiology terms live in `keywords.json`. The bot ranks them by which surface the highest-engagement posts and demotes quiet ones after 30 days.

## Guardrails

- Abstracts and open-access full text only. No paywalled PDFs.
- Every post cites the source DOI or PubMed ID.
- Dry-run mode for testing without posting.
- Rate-limited to 3 posts per day max.

## License

MIT