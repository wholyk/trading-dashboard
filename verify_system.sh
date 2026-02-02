#!/bin/bash
echo "=================================================="
echo "ShortsFactory System Verification"
echo "=================================================="
echo ""

echo "1. Checking directory structure..."
for dir in INBOX/long_videos INBOX/clips storage/originals storage/intermediate storage/finals storage/captions storage/metadata logs database config shortsfactory/core shortsfactory/workers shortsfactory/dashboard; do
    if [ -d "$dir" ]; then
        echo "   ✓ $dir"
    else
        echo "   ✗ $dir (missing)"
    fi
done
echo ""

echo "2. Checking key files..."
for file in README.md ARCHITECTURE.md QUICKSTART.md SAFETY.md IMPLEMENTATION_SUMMARY.md requirements.txt config/settings.yaml database/shortsfactory.db INBOX/ideas.txt; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file (missing)"
    fi
done
echo ""

echo "3. Checking Python modules..."
python3 -c "
import sys
sys.path.insert(0, '.')

modules = [
    'shortsfactory',
    'shortsfactory.core.database',
    'shortsfactory.core.config',
    'shortsfactory.core.logger',
    'shortsfactory.workers.base',
    'shortsfactory.workers.cutting',
    'shortsfactory.workers.formatting',
    'shortsfactory.workers.caption',
    'shortsfactory.workers.metadata',
    'shortsfactory.workers.rendering',
    'shortsfactory.workers.upload',
    'shortsfactory.workers.manager',
    'shortsfactory.watcher',
    'shortsfactory.init',
    'shortsfactory.main',
]

for module in modules:
    try:
        __import__(module)
        print(f'   ✓ {module}')
    except Exception as e:
        print(f'   ✗ {module}: {e}')
"
echo ""

echo "4. System stats..."
python3 -c "
import sys
sys.path.insert(0, '.')
from shortsfactory.core.database import Database
from shortsfactory.core.config import get_config

db = Database()
config = get_config()
stats = db.get_stats()

print(f'   Database: {stats[\"total_jobs\"]} total jobs')
print(f'   Video format: {config.video.target_width}x{config.video.target_height}')
print(f'   Upload enabled: {config.upload.enabled}')
print(f'   Max retries: {config.worker.max_retries}')
"
echo ""

echo "=================================================="
echo "✓ System Verification Complete"
echo "=================================================="
echo ""
echo "To start the system:"
echo "  python -m shortsfactory.main all"
echo ""
echo "Dashboard will be available at:"
echo "  http://localhost:8501"
echo ""
