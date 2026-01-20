import json
import os

STATS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'stats.json')

def load_stats():
    try:
        with open(STATS_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}
