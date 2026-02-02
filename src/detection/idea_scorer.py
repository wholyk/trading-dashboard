#!/usr/bin/env python3
"""
Idea Scorer

Assigns confidence scores (0-100) to content ideas.
Uses weighted scoring algorithm based on multiple factors.
"""

import os
import sys
import json
import yaml
from datetime import datetime

def load_config():
    """Load system configuration"""
    with open('config/system_config.yaml', 'r') as f:
        return yaml.safe_load(f)

def load_ideas():
    """Load generated ideas"""
    with open('data/ideas_generated.json', 'r') as f:
        return json.load(f)

def calculate_recency_score(idea):
    """Calculate score based on pattern recency"""
    timestamp = datetime.fromisoformat(idea['timestamp'])
    age_hours = (datetime.now() - timestamp).total_seconds() / 3600
    
    # Newer patterns score higher
    if age_hours < 6:
        return 100
    elif age_hours < 24:
        return 80
    elif age_hours < 72:
        return 60
    elif age_hours < 168:  # 1 week
        return 40
    else:
        return 20

def calculate_engagement_score(idea):
    """Calculate score based on average engagement"""
    engagement = idea.get('avg_engagement', 0)
    
    # Normalize to 0-100 scale
    # Typical engagement rate for Shorts: 0.01-0.05
    normalized = min(engagement / 0.05 * 100, 100)
    return normalized

def calculate_competition_score(idea):
    """Calculate score based on market saturation (inverse)"""
    frequency = idea.get('pattern_frequency', 0)
    
    # Less competition is better
    # If pattern appears 3-10 times, good balance
    # If > 20 times, oversaturated
    if frequency < 3:
        return 40  # Too niche, might not work
    elif frequency <= 10:
        return 100  # Sweet spot
    elif frequency <= 20:
        return 70  # Still good
    else:
        return 30  # Oversaturated

def calculate_audience_fit_score(idea, config):
    """Calculate score based on fit with channel's niche"""
    # For now, simple check if niche matches
    if idea['niche'] == config['detection']['niche']:
        return 100
    else:
        return 50  # Partial match

def score_idea(idea, config):
    """Calculate overall score for an idea"""
    weights = config['scoring']['weights']
    
    # Calculate individual scores
    pattern_frequency_score = min(idea.get('pattern_frequency', 0) / 20 * 100, 100)
    recency_score = calculate_recency_score(idea)
    engagement_score = calculate_engagement_score(idea)
    competition_score = calculate_competition_score(idea)
    audience_fit_score = calculate_audience_fit_score(idea, config)
    
    # Weighted sum
    total_score = (
        pattern_frequency_score * weights['pattern_frequency'] +
        recency_score * weights['recency'] +
        engagement_score * weights['engagement_rate'] +
        competition_score * weights['competition'] +
        audience_fit_score * weights['audience_fit']
    )
    
    # Round to integer
    total_score = int(round(total_score))
    
    # Add score breakdown for transparency
    idea['score'] = total_score
    idea['score_breakdown'] = {
        'pattern_frequency': round(pattern_frequency_score, 1),
        'recency': round(recency_score, 1),
        'engagement': round(engagement_score, 1),
        'competition': round(competition_score, 1),
        'audience_fit': round(audience_fit_score, 1)
    }
    
    return idea

def main():
    """Main execution"""
    try:
        # Load configuration and ideas
        config = load_config()
        ideas = load_ideas()
        
        print(f"Scoring {len(ideas)} ideas...")
        
        # Score each idea
        scored_ideas = []
        for idea in ideas:
            scored_idea = score_idea(idea, config)
            scored_ideas.append(scored_idea)
        
        # Sort by score (highest first)
        scored_ideas.sort(key=lambda x: x['score'], reverse=True)
        
        # Save scored ideas
        os.makedirs('data', exist_ok=True)
        with open('data/ideas_scored.json', 'w') as f:
            json.dump(scored_ideas, f, indent=2)
        
        # Print summary
        scores = [idea['score'] for idea in scored_ideas]
        print(f"Score range: {min(scores)}-{max(scores)}")
        print(f"Average score: {sum(scores) / len(scores):.1f}")
        print(f"✓ Scoring complete")
        
        return 0
    
    except Exception as e:
        print(f"✗ Scoring failed: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
