"""Pull cardiology papers from PubMed and open-access journals."""
import time
import requests
from config import PUBMED_BASE, PUBMED_EMAIL, load_keywords

OPEN_ACCESS_JOURNALS = [
    "PLoS One[journal]",
    "BMC Cardiovasc Disord[journal]",
    "Frontiers in Cardiovascular Medicine[journal]",
    "Int J Mol Sci[journal]",
    "J Clin Med[journal]",
]

def search_pubmed(term, max_results=10, days_back=2):
    """Search PubMed for recent papers matching a term."""
    params = {
        "db": "pubmed",
        "term": f"({term}) AND (\"{days_back} days\"[dp])",
        "retmax": max_results,
        "retmode": "json",
        "email": PUBMED_EMAIL,
        "sort": "relevance",
    }
    r = requests.get(f"{PUBMED_BASE}/esearch.fcgi", params=params, timeout=30)
    r.raise_for_status()
    ids = r.json()["esearchresult"]["idlist"]
    if not ids:
        return []
    # fetch summaries
    params2 = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json",
        "rettype": "abstract",
    }
    r2 = requests.get(f"{PUBMED_BASE}/efetch.fcgi", params=params2, timeout=30)
    r2.raise_for_status()
    return r2.json()["result"]

def search_open_access(term, max_results=5):
    """Search open-access journals via PubMed with journal filters."""
    results = []
    for journal in OPEN_ACCESS_JOURNALS:
        try:
            data = search_pubmed(f"{term} AND {journal}", max_results=max_results)
            for uid, paper in data.items():
                if uid == "uids":
                    continue
                results.append(paper)
            time.sleep(0.35)  # NCBI rate limit
        except Exception as e:
            print(f"Open-access search failed for {journal}: {e}")
    return results

def discover_all(days_back=2):
    """Run discovery across all keyword categories."""
    kw = load_keywords()
    seen = set()
    papers = []
    all_terms = kw["primary"] + kw["drugs"] + kw["topics"]
    for term in all_terms:
        try:
            data = search_pubmed(term, days_back=days_back)
            for uid, paper in data.items():
                if uid == "uids" or uid in seen:
                    continue
                seen.add(uid)
                paper["_search_term"] = term
                papers.append(paper)
            time.sleep(0.35)
        except Exception as e:
            print(f"Discovery failed for '{term}': {e}")
    # supplement with open-access journal hits
    for term in kw["primary"][:5]:
        for paper in search_open_access(term):
            uid = paper.get("uid")
            if uid and uid not in seen:
                seen.add(uid)
                paper["_search_term"] = term
                papers.append(paper)
    return papers