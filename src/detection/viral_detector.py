#!/usr/bin/env python3
"""
Viral Pattern Detector

Scans YouTube Shorts in a target niche to identify viral patterns.
Outputs pattern statistics and generates content ideas.

SAFE FOR GITHUB ACTIONS:
- Automatically disables YouTube API in CI
- Falls back to mock data
- Never throws HttpError in Actions
"""

import os
import sys
import json
import yaml
from datetime import datetime, timedelta

# Detect GitHub Actions
CI_MODE = os.getenv("GITHUB_ACTIONS") == "true"

# Optional YouTube imports (will fail safely in CI)
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
except Exception:
    build = None
    Credentials = None


def load_config():
    """Load system configuration"""
    with open("config/system_config.yaml", "r") as f:
        return yaml.safe_load(f)


def get_youtube_client():
    """Initialize YouTube API client (DISABLED IN CI)"""
    if CI_MODE:
        print("CI detected — YouTube API disabled")
        return None

    if build is None or Credentials is None:
        raise RuntimeError("YouTube client libraries unavailable")

    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing YouTube API credentials")

    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )

    return build("youtube", "v3", credentials=credentials)


def search_viral_shorts(youtube, config):
    """Search for viral Shorts OR use mock data in CI"""

    # 🔒 CI-safe mock data
    if youtube is None:
        print("Using mock viral data")
        return [
            {
                "video_id": "mock_video_1",
                "views": 1_200_000,
                "likes": 54000,
                "comments": 3200,
                "duration": "PT45S",
            },
            {
                "video_id": "mock_video_2",
                "views": 980000,
                "likes": 41000,
                "comments": 2100,
                "duration": "PT38S",
            },
        ]

    keywords = config["detection"]["keywords"]
    max_results = config["detection"]["youtube"]["max_results_per_query"]
    min_views = config["detection"]["min_views_threshold"]
    lookback_days = config["detection"]["lookback_days"]

    published_after = (
        datetime.now() - timedelta(days=lookback_days)
    ).isoformat() + "Z"

    all_videos = []

    for keyword in keywords:
        try:
            search = youtube.search().list(
                part="id",
                q=f"{keyword} #shorts",
                type="video",
                videoDuration="short",
                order="viewCount",
                maxResults=max_results,
                publishedAfter=published_after,
            )
            response = search.execute()

            video_ids = [
                item["id"]["videoId"]
                for item in response.get("items", [])
                if "videoId" in item.get("id", {})
            ]

            if not video_ids:
                continue

            stats = youtube.videos().list(
                part="statistics,contentDetails",
                id=",".join(video_ids),
            ).execute()

            for video in stats.get("items", []):
                views = int(video["statistics"].get("viewCount", 0))
                if views < min_views:
                    continue

                all_videos.append(
                    {
                        "video_id": video["id"],
                        "views": views,
                        "likes": int(video["statistics"].get("likeCount", 0)),
                        "comments": int(video["statistics"].get("commentCount", 0)),
                        "duration": video["contentDetails"]["duration"],
                    }
                )

        except Exception as e:
            print(f"Skipping keyword '{keyword}': {e}", file=sys.stderr)

    return all_videos


def extract_patterns(videos):
    """Extract viral patterns from videos"""
    patterns = {}

    for v in videos:
        engagement = (
            (v["likes"] + v["comments"]) / v["views"]
            if v["views"] > 0
            else 0
        )

        if v["views"] > 1_000_000:
            key = "mega_viral"
        elif v["views"] > 500_000:
            key = "high_viral"
        elif v["views"] > 100_000:
            key = "medium_viral"
        else:
            key = "low_viral"

        if key not in patterns:
            patterns[key] = {
                "frequency": 0,
                "avg_views": 0,
                "avg_engagement": 0,
                "examples": [],
            }

        patterns[key]["frequency"] += 1
        patterns[key]["avg_views"] += v["views"]
        patterns[key]["avg_engagement"] += engagement
        patterns[key]["examples"].append(v["video_id"])

    for p in patterns.values():
        p["avg_views"] /= p["frequency"]
        p["avg_engagement"] /= p["frequency"]

    return patterns


def generate_ideas_from_patterns(patterns, config):
    """Generate content ideas from patterns"""
    ideas = []
    niche = config["detection"]["niche"]
    min_frequency = config["detection"]["min_pattern_frequency"]

    for name, data in patterns.items():
        if data["frequency"] >= min_frequency:
            ideas.append(
                {
                    "pattern": name,
                    "niche": niche,
                    "pattern_frequency": data["frequency"],
                    "avg_views": data["avg_views"],
                    "avg_engagement": data["avg_engagement"],
                    "reference_examples": data["examples"][:3],
                    "timestamp": datetime.now().isoformat(),
                }
            )

    return ideas


def main():
    try:
        config = load_config()

        youtube = get_youtube_client()
        videos = search_viral_shorts(youtube, config)

        patterns = extract_patterns(videos)
        ideas = generate_ideas_from_patterns(patterns, config)

        os.makedirs("data", exist_ok=True)

        with open("data/patterns_detected.json", "w") as f:
            json.dump(patterns, f, indent=2)

        with open("data/ideas_generated.json", "w") as f:
            json.dump(ideas, f, indent=2)

        print("✓ Viral detection complete")
        return 0

    except Exception as e:
        print(f"✗ Viral detection failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
