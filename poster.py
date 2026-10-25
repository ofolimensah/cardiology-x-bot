"""X posting with a mandatory draft-and-approve step."""
import tweepy
from config import (
    X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET, DRY_RUN
)

def get_client():
    return tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_SECRET,
    )

def show_draft(draft, index, total):
    print("\n" + "=" * 60)
    print(f"DRAFT {index} of {total}")
    print("=" * 60)
    print(f"Source: {draft['journal']} | PMID {draft['pmid']} | DOI {draft['doi']}")
    print(f"Triggered by keyword: {draft['search_term']}")
    print("-" * 60)
    for i, part in enumerate(draft["text"].split("\n---\n")):
        print(f"[Post {i+1}] {part}")
        print("-" * 40)

def approve(draft):
    """Ask the human to approve, edit, or skip."""
    while True:
        choice = input("[A]pprove / [E]dit / [S]kip? ").strip().lower()
        if choice == "a":
            return "approve"
        if choice == "e":
            print("Enter revised text (end with a blank line):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            draft["text"] = "\n".join(lines)
            return "edit"
        if choice == "s":
            return "skip"
        print("Please choose A, E, or S.")

def post_draft(draft):
    """Publish an approved draft to X."""
    parts = [p.strip() for p in draft["text"].split("\n---\n") if p.strip()]
    if DRY_RUN:
        print("[DRY RUN] Would post:")
        for p in parts:
            print(f"  -> {p[:80]}...")
        return True
    client = get_client()
    try:
        if len(parts) == 1:
            client.create_tweet(text=parts[0])
        else:
            # post thread: first tweet, then reply chain
            prev_id = None
            for p in parts:
                if prev_id is None:
                    resp = client.create_tweet(text=p)
                else:
                    resp = client.create_tweet(text=p, in_reply_to_tweet_id=prev_id)
                prev_id = resp.data["id"]
        return True
    except tweepy.TweepyException as e:
        print(f"Post failed: {e}")
        return False