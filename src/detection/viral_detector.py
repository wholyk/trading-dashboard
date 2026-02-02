#!/usr/bin/env python3
"""
Viral Pattern Detector

Scans YouTube Shorts in target niche to identify viral patterns.
Outputs pattern dictionary with frequency scores.
"""

import os
import sys
import json
import yaml
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def load_config():
    """Load system configuration"""
    with open('config/system_config.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_youtube_client():
    """Initialize YouTube API client"""
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing YouTube API credentials")
    
    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    
    return build('youtube', 'v3', credentials=credentials)

def search_viral_shorts(youtube, config):
    """Search for viral Shorts in niche"""
    niche = config['detection']['niche']
    keywords = config['detection']['keywords']
    max_results = config['detection']['youtube']['max_results_per_query']
    min_views = config['detection']['min_views_threshold']
    
    # Calculate date range
    lookback_days = config['detection']['lookback_days']
    published_after = (datetime.now() - timedelta(days=lookback_days)).isoformat() + 'Z'
    
    all_videos = []
    
    for keyword in keywords:
        try:
            # Search for Shorts
            request = youtube.search().list(
                part='id,snippet',
                q=f"{keyword} #shorts",
                type='video',
                videoDuration='short',  # Under 4 minutes
                order='viewCount',
                maxResults=max_results,
                publishedAfter=published_after
            )
            response = request.execute()
            
            # Get video statistics
            video_ids = [item['id']['videoId'] for item in response.get('items', [])]
            
            if video_ids:
                stats_request = youtube.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(video_ids)
                )
                stats_response = stats_request.execute()
                
                for video in stats_response.get('items', []):
                    view_count = int(video['statistics'].get('viewCount', 0))
                    
                    if view_count >= min_views:
                        all_videos.append({
                            'video_id': video['id'],
                            'views': view_count,
                            'likes': int(video['statistics'].get('likeCount', 0)),
                            'comments': int(video['statistics'].get('commentCount', 0)),
                            'duration': video['contentDetails']['duration']
                        })
        
        except Exception as e:
            print(f"Error searching for keyword '{keyword}': {e}", file=sys.stderr)
            continue
    
    return all_videos

def extract_patterns(videos, config):
    """Extract viral patterns from videos"""
    patterns = {}
    
    # For this stub implementation, we create basic patterns
    # In production, this would analyze titles, thumbnails, hooks, etc.
    
    for video in videos:
        # Calculate engagement rate
        engagement = (video['likes'] + video['comments']) / video['views'] if video['views'] > 0 else 0
        
        # Create pattern based on view ranges
        if video['views'] > 1000000:
            pattern_key = "mega_viral"
        elif video['views'] > 500000:
            pattern_key = "high_viral"
        elif video['views'] > 100000:
            pattern_key = "medium_viral"
        else:
            pattern_key = "low_viral"
        
        if pattern_key not in patterns:
            patterns[pattern_key] = {
                'frequency': 0,
                'avg_views': 0,
                'avg_engagement': 0,
                'examples': []
            }
        
        patterns[pattern_key]['frequency'] += 1
        patterns[pattern_key]['avg_views'] += video['views']
        patterns[pattern_key]['avg_engagement'] += engagement
        patterns[pattern_key]['examples'].append(video['video_id'])
    
    # Calculate averages
    for pattern in patterns.values():
        if pattern['frequency'] > 0:
            pattern['avg_views'] /= pattern['frequency']
            pattern['avg_engagement'] /= pattern['frequency']
    
    return patterns

def generate_ideas_from_patterns(patterns, config):
    """Generate content ideas from patterns"""
    ideas = []
    
    niche = config['detection']['niche']
    
    for pattern_name, pattern_data in patterns.items():
        # Only generate ideas from patterns that appear frequently enough
        min_frequency = config['detection']['min_pattern_frequency']
        
        if pattern_data['frequency'] >= min_frequency:
            # Generate idea
            idea = {
                'pattern': pattern_name,
                'niche': niche,
                'pattern_frequency': pattern_data['frequency'],
                'avg_views': pattern_data['avg_views'],
                'avg_engagement': pattern_data['avg_engagement'],
                'reference_examples': pattern_data['examples'][:3],  # Top 3
                'timestamp': datetime.now().isoformat()
            }
            ideas.append(idea)
    
    return ideas

def main():
    """Main execution"""
    try:
        # Load configuration
        config = load_config()
        
        print("Initializing YouTube API client...")
        youtube = get_youtube_client()
        
        print(f"Searching for viral Shorts in niche: {config['detection']['niche']}")
        videos = search_viral_shorts(youtube, config)
        print(f"Found {len(videos)} viral videos")
        
        print("Extracting patterns...")
        patterns = extract_patterns(videos, config)
        print(f"Extracted {len(patterns)} patterns")
        
        print("Generating ideas from patterns...")
        ideas = generate_ideas_from_patterns(patterns, config)
        print(f"Generated {len(ideas)} content ideas")
        
        # Save outputs
        os.makedirs('data', exist_ok=True)
        
        with open('data/patterns_detected.json', 'w') as f:
            json.dump(patterns, f, indent=2)
        
        with open('data/ideas_generated.json', 'w') as f:
            json.dump(ideas, f, indent=2)
        
        print("✓ Viral detection complete")
        return 0
    
    except Exception as e:
        print(f"✗ Viral detection failed: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
