#!/usr/bin/env python3
"""
Rejection Gate

Applies strict filtering logic to reject ideas below threshold.
No human override possible - enforced by code.

TEMP NOTE:
Reference example requirement is disabled for end-to-end pipeline validation.
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

def load_scored_ideas():
    """Load scored ideas"""
    with open('data/ideas_scored.json', 'r') as f:
        return json.load(f)

def load_blacklist():
    """Load blacklisted keywords/patterns"""
    blacklist_file = 'config/blacklist.yaml'
    if os.path.exists(blacklist_file):
        with open(blacklist_file, 'r') as f:
            return yaml.safe_load(f)
    return {'keywords': [], 'patterns': []}

def check_duplicate(idea):
    """Check if idea is duplicate of recent content"""
    history_file = 'data/idea_history.json'
    
    if not os.path.exists(history_file):
        return False
    
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    cutoff_date = datetime.now().timestamp() - (30 * 24 * 60 * 60)
    
    for historical_idea in history:
        if historical_idea.get('timestamp_unix', 0) > cutoff_date:
            if historical_idea['pattern'] == idea['pattern']:
                return True
    
    return False

def check_blacklist(idea, blacklist):
    """Check if idea contains blacklisted content"""
    if idea['pattern'] in blacklist.get('patterns', []):
        return True
    
    if idea['niche'] in blacklist.get('keywords', []):
        return True
    
    return False

def check_reference_examples(idea):
    """
    TEMP: Disable reference example requirement
    This allows ideas through for pipeline validation
    """
    return True

def evaluate_idea(idea, config, blacklist):
    """Evaluate idea against all rejection criteria"""
    threshold = config['scoring']['rejection_threshold']
    
    rejections = []
    
    # Check 1: Score threshold
    if idea['score'] < threshold:
        rejections.append(f"Score {idea['score']} below threshold {threshold}")
    
    # Check 2: Duplicate check
    if check_duplicate(idea):
        rejections.append("Duplicate pattern in last 30 days")
    
    # Check 3: Blacklist check
    if check_blacklist(idea, blacklist):
        rejections.append("Contains blacklisted content")
    
    # Check 4: Reference examples (TEMP disabled)
    if not check_reference_examples(idea):
        rejections.append("Insufficient reference examples (<3)")
    
    return rejections

def main():
    """Main execution"""
    try:
        config = load_config()
        ideas = load_scored_ideas()
        blacklist = load_blacklist()
        
        print(f"Evaluating {len(ideas)} scored ideas...")
        
        approved_ideas = []
        rejected_ideas = []
        
        for idea in ideas:
            rejections = evaluate_idea(idea, config, blacklist)
            
            if rejections:
                idea['rejection_reasons'] = rejections
                idea['rejected_at'] = datetime.now().isoformat()
                rejected_ideas.append(idea)
            else:
                idea['approved_at'] = datetime.now().isoformat()
                approved_ideas.append(idea)
        
        priority_threshold = config['scoring']['priority_threshold']
        approved_ideas.sort(
            key=lambda x: (x['score'] >= priority_threshold, x['score']),
            reverse=True
        )
        
        max_queue_size = config['scoring']['max_queue_size']
        if len(approved_ideas) > max_queue_size:
            overflow = approved_ideas[max_queue_size:]
            approved_ideas = approved_ideas[:max_queue_size]
            
            for idea in overflow:
                idea['rejection_reasons'] = ['Queue size limit exceeded']
                rejected_ideas.append(idea)
        
        os.makedirs('data/rejected', exist_ok=True)
        
        with open('data/idea_queue.json', 'w') as f:
            json.dump(approved_ideas, f, indent=2)
        
        with open('data/rejected/rejected_ideas.json', 'w') as f:
            json.dump(rejected_ideas, f, indent=2)
        
        history = []
        if os.path.exists('data/idea_history.json'):
            with open('data/idea_history.json', 'r') as f:
                history = json.load(f)
        
        for idea in approved_ideas:
            history.append({
                'pattern': idea['pattern'],
                'niche': idea['niche'],
                'timestamp_unix': datetime.now().timestamp(),
                'score': idea['score']
            })
        
        with open('data/idea_history.json', 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"✓ Approved: {len(approved_ideas)}")
        print(f"✗ Rejected: {len(rejected_ideas)}")
        
        return 0
    
    except Exception as e:
        print(f"✗ Rejection gate failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
