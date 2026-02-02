#!/usr/bin/env python3
"""
YouTube API Quota Checker

Checks current quota usage and determines if operations can proceed.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Quota costs
QUOTA_COSTS = {
    'search': 100,
    'video_list': 1,
    'upload': 1600,
    'analytics': 200
}

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

def load_quota_state():
    """Load quota usage state from file"""
    state_file = 'data/quota_state.json'
    
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)
            
            # Check if state is from today
            state_date = datetime.fromisoformat(state['date']).date()
            if state_date == datetime.now().date():
                return state
    
    # Return fresh state for today
    return {
        'date': datetime.now().date().isoformat(),
        'used': 0,
        'limit': 10000,
        'reserve': 1500,  # Reserve for analytics and buffer
        'operations': []
    }

def save_quota_state(state):
    """Save quota usage state to file"""
    os.makedirs('data', exist_ok=True)
    with open('data/quota_state.json', 'w') as f:
        json.dump(state, f, indent=2)

def check_quota(operation='generic', count=1):
    """Check if quota is available for operation"""
    state = load_quota_state()
    
    cost = QUOTA_COSTS.get(operation, 100) * count
    available = state['limit'] - state['reserve'] - state['used']
    
    print(f"Quota check for operation: {operation}")
    print(f"  Cost: {cost} units")
    print(f"  Used: {state['used']}/{state['limit']} units")
    print(f"  Available: {available} units")
    print(f"  Reserved: {state['reserve']} units")
    
    if cost > available:
        print(f"✗ Insufficient quota (need {cost}, have {available})")
        return False
    else:
        print(f"✓ Quota available")
        
        # Record this check (actual usage will be recorded by the operation)
        state['operations'].append({
            'type': 'check',
            'operation': operation,
            'cost': cost,
            'timestamp': datetime.now().isoformat()
        })
        save_quota_state(state)
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Check YouTube API quota')
    parser.add_argument('--operation', default='generic',
                       choices=['search', 'video_list', 'upload', 'analytics'],
                       help='Type of operation to check quota for')
    parser.add_argument('--count', type=int, default=1,
                       help='Number of operations')
    
    args = parser.parse_args()
    
    try:
        if check_quota(args.operation, args.count):
            return 0
        else:
            return 1
    except Exception as e:
        print(f"✗ Quota check failed: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
