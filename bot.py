#!/usr/bin/env python3
"""Cardiology X Bot — daily discovery, summarization, draft approval, posting."""
import argparse
import sys
from discover import discover_all
from summarizer import summarize_paper
from poster import show_draft, approve, post_draft
from learn import update_keyword_scores
from config import MAX_POSTS_PER_DAY, DRY_RUN

def run_cycle(dry_run=False):
    global_dry = DRY_RUN
    # allow CLI override
    import config
    config.DRY_RUN = dry_run or global_dry

    print("Discovering cardiology papers...")
    papers = discover_all(days_back=2)
    print(f"Found {len(papers)} candidate papers.")

    drafts = []
    for paper in papers:
        if len(drafts) >= MAX_POSTS_PER_DAY:
            break
        try:
            draft = summarize_paper(paper)
            if draft:
                drafts.append(draft)
        except Exception as e:
            print(f"Summarization failed for PMID {paper.get('uid')}: {e}")

    if not drafts:
        print("Nothing worth posting today.")
        return

    posted_terms = []
    for i, draft in enumerate(drafts, 1):
        show_draft(draft, i, len(drafts))
        decision = approve(draft)
        if decision in ("approve", "edit"):
            ok = post_draft(draft)
            if ok:
                posted_terms.append(draft["search_term"])
                print("Posted.")
        else:
            print("Skipped.")

    if posted_terms:
        update_keyword_scores(posted_terms)
        print(f"Updated engagement scores for: {posted_terms}")

def main():
    parser = argparse.ArgumentParser(description="Cardiology X Bot")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting to X")
    args = parser.parse_args()
    run_cycle(dry_run=args.dry_run)

if __name__ == "__main__":
        main()