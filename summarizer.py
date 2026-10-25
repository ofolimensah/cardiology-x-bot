"""Turn paper metadata into X-ready copy using Grok."""
import json
import requests
from config import GROK_API_KEY, GROK_BASE

SYSTEM_PROMPT = """You are a medical science communicator writing for clinicians on X.
Given a paper's title, abstract, journal, and DOI, produce ONE of two formats:

FORMAT A (one-liner, default): A single post of 240 chars or fewer.
Structure: a short question or hook, then the counterintuitive or headline finding,
then the source. Example: "Can maternal diet affect infant food allergies? Peanut and egg
consumption during pregnancy neither caused nor protected against it. Read the PrEggNut
study: https://doi.org/10.xxxx"

FORMAT B (thread): 3-5 short posts for methodologically rich or clinically dense papers.
Post 1 is the hook. Later posts cover methods, key numbers, and the takeaway.
Each post under 240 chars. Separate posts with \n---\n.

Rules:
- Lead with the surprise or the number, never "New study shows".
- Cite the DOI or PubMed ID in the final post.
- No medical advice. No hype. State what the paper found.
- If the abstract is too thin to say anything specific, reply with SKIP.
- Output only the post text. No markdown, no commentary."""

def summarize_paper(paper):
    """Return drafted post text for one paper, or None to skip."""
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    journal = ", ".join(paper.get("source", [""]))
    doi = "".join(paper.get("articleids", []))
    # articleids is a list of dicts; find doi
    for aid in paper.get("articleids", []):
        if aid.get("idtype") == "doi":
            doi = aid["value"]
            break
    uid = paper.get("uid", "")

    user_msg = (
        f"Title: {title}\nJournal: {journal}\n"
        f"PubMed ID: {uid}\nDOI: {doi}\n\nAbstract:\n{abstract[:3000]}"
    )
    payload = {
        "model": "grok-4-fast",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "temperature": 0.4,
        "max_tokens": 600,
    }
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }
    r = requests.post(f"{GROK_BASE}/chat/completions", json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"].strip()
    if text.upper().startswith("SKIP"):
        return None
    return {
        "text": text,
        "pmid": uid,
        "doi": doi,
        "title": title,
        "journal": journal,
        "search_term": paper.get("_search_term", ""),
    }