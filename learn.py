"""Feedback loop: rank keywords by engagement, demote quiet ones."""
import tweepy
from datetime import datetime, timezone
from config import load_keywords, save_keywords, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET

SCORE_WEIGHTS = {"like_count": 1, "retweet_count": 2, "reply_count": 3, "bookmark_count": 2}
DEMOTE_DAYS = 30

def score_recent_posts(days=7):
    """Fetch the bot's recent posts and score them by engagement."""
    client = tweepy.Client(
        consumer_key=X_API_KEY,
        consumer_secret=X_API_SECRET,
        access_token=X_ACCESS_TOKEN,
        access_token_secret=X_ACCESS_SECRET,
    )
    me = client.get_me().data
    tweets = client.get_users_tweets(
        me.id,
        max_results=20,
        tweet_fields=["created_at", "public_metrics", "conversation_id"],
    )
    if not tweets.data:
        return []
    scored = []
    for t in tweets.data:
        metrics = t.public_metrics
        score = sum(metrics.get(k, 0) * w for k, w in SCORE_WEIGHTS.items())
        scored.append({"id": t.id, "score": score, "metrics": metrics, "created_at": t.created_at})
    return scored

def update_keyword_scores(posted_keywords):
    """Bump scores for keywords that produced posted content."""
    kw = load_keywords()
    scores = kw.get("engagement_scores", {})
    for term in posted_keywords:
        scores[term] = scores.get(term, 0) + 1
    kw["engagement_scores"] = scores
    kw["last_updated"] = datetime.now(timezone.utc).isoformat()
    # demote terms untouched for DEMOTE_DAYS
    save_keywords(kw)
    return kw