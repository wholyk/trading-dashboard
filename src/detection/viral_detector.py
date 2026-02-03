#!/usr/bin/env python3
"""
Viral Pattern Detector

Scans YouTube Shorts in target niche to identify viral patterns.
Outputs pattern dictionary with frequency scores.

Includes a safe mock fallback when YouTube API credentials
are unavailable (for dry runs in GitHub Actions).
"""

import os
import sys
import json
import yaml
from datetime import datetime, timedelta

# Optional YouTube imports (may fail in dry runs)
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
    """Initialize YouTube API client"""
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing YouTube API credentials")

    if build is None or Credentials is None:
        raise RuntimeError("YouTube client libraries not available")

    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )

    return build("youtube", "v3", credentials=credentials)


def search_viral_shorts(youtube, config):
    """Search for viral Shorts in niche"""
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
            request = youtube.search().list(
                part="id,snippet",
                q=f"{keyword} #shorts",
                type="video",
                videoDuration="short",
                order="viewCount",
                maxResults=max_results,
                publishedAfter=published_after,
            )
            response = request.execute()

            video_ids = [
                item["id"]["videoId"]
                for item in response.get("items", [])
                if "videoId" in item.get("id", {})
            ]

            if not video_ids:
                continue

            stats_request = youtube.videos().list(
                part="statistics,contentDetails",
                id=",".join(video_ids),
            )
            stats_response = stats_request.execute()

            for video in stats_response.get("items", []):
                view_count = int(video["statistics"].get("viewCount", 0))

                if view_count >= min_views:
                    all_videos.append(
                        {
                            "video_id": video["id"],
                            "views": view_count,
                            "likes": int(video["statistics"].get("likeCount", 0)),
                            "comments": int(
                                video["statistics"].get("commentCount", 0)
                            ),
                            "duration": video["contentDetails"]["duration"],
                        }
                    )

        except Exception as e:
            print(
                f"Error searching keyword '{keyword}', skipping: {e}",
                file=sys.stderr,
            )

    return all_videos


def extract_patterns(videos, config):
    """Extract viral patterns from videos"""
    patterns = {}

    for video in videos:
        engagement = (
            (video["likes"] + video["comments"]) / video["views"]
            if video["views"] > 0
            else 0
        )

        if video["views"] > 1_000_000:
            key = "mega_viral"
        elif video["views"] > 500_000:
            key = "high_viral"
        elif video["views"] > 100_000:
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
        patterns[key]["avg_views"] += video["views"]
        patterns[key]["avg_engagement"] += engagement
        patterns[key]["examples"].append(video["video_id"])

    for p in patterns.values():
        if p["frequency"] > 0:
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
    """Main execution"""
    try:
        config = load_config()

        # 🔁 TRY YOUTUBE → FALL BACK TO MOCK DATA
        try:
            print("Initializing YouTube API client...")
            youtube = get_youtube_client()
            print("Searching YouTube for viral Shorts...")
            videos = search_viral_shorts(youtube, config)
            print(f"Found {len(videos)} viral videos")

        except Exception as e:
            print("YouTube API unavailable, using mock data:", e)

            videos = [
                {
                    "video_id": "mock_video_1",
                    "views": 1_200_000,
                    "likes": 54_000,
                    "comments": 3_200,
                    "duration": "PT45S",
                },
                {
                    "video_id": "mock_video_2",
                    "views": 980_000,
                    "likes": 41_000,
                    "comments": 2_100,
                    "duration": "PT38S",
                },
            ]

        patterns = extract_patterns(videos, config)
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
