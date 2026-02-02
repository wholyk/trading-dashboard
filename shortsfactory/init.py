"""
Initialization script for ShortsFactory.
Sets up the system for first use.
"""

import os
import sys

from shortsfactory.core.database import Database
from shortsfactory.core.config import save_default_config, get_config
from shortsfactory.core.logger import get_logger


def init_system():
    """Initialize the ShortsFactory system"""
    print("=" * 60)
    print("ShortsFactory Initialization")
    print("=" * 60)
    print()
    
    # Create logger
    logger = get_logger("init")
    logger.info("Starting system initialization")
    
    # Create directory structure
    print("Creating directory structure...")
    directories = [
        "INBOX/long_videos",
        "INBOX/clips",
        "storage/originals",
        "storage/intermediate",
        "storage/finals",
        "storage/captions",
        "storage/metadata",
        "logs",
        "database",
        "config",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ Created: {directory}")
    
    # Create ideas.txt
    ideas_file = "INBOX/ideas.txt"
    if not os.path.exists(ideas_file):
        with open(ideas_file, 'w', encoding='utf-8') as f:
            f.write("# Add your video ideas here, one per line\n")
            f.write("# Lines starting with # are ignored\n")
            f.write("\n")
            f.write("# Example ideas:\n")
            f.write("# Amazing life hack for productivity\n")
            f.write("# Top 5 travel destinations in 2024\n")
            f.write("# Quick recipe for busy people\n")
        print(f"  ✓ Created: {ideas_file}")
    
    # Create default configuration
    print("\nCreating default configuration...")
    config_path = "config/settings.yaml"
    if not os.path.exists(config_path):
        save_default_config(config_path)
        print(f"  ✓ Created: {config_path}")
    else:
        print(f"  ℹ Already exists: {config_path}")
    
    # Initialize database
    print("\nInitializing database...")
    config = get_config(config_path)
    db = Database(config.database_path)
    print(f"  ✓ Database initialized: {config.database_path}")
    
    # Create .gitignore updates
    print("\nUpdating .gitignore...")
    gitignore_additions = [
        "\n# ShortsFactory",
        "INBOX/long_videos/*",
        "INBOX/clips/*",
        "!INBOX/long_videos/.gitkeep",
        "!INBOX/clips/.gitkeep",
        "storage/",
        "database/*.db",
        "logs/*.log",
        "config/credentials.json",
        "config/token.json",
    ]
    
    with open(".gitignore", "a", encoding="utf-8") as f:
        f.write("\n".join(gitignore_additions) + "\n")
    print("  ✓ Updated .gitignore")
    
    # Create .gitkeep files
    for directory in ["INBOX/long_videos", "INBOX/clips"]:
        gitkeep = os.path.join(directory, ".gitkeep")
        if not os.path.exists(gitkeep):
            open(gitkeep, 'a').close()
    
    # Create README in storage
    storage_readme = """# Storage Directory

This directory contains all processed files organized by stage:

- **originals/**: Original uploaded files (backup)
- **intermediate/**: Files during processing (cut, formatted)
- **finals/**: Final rendered videos ready for upload
- **captions/**: Caption text files
- **metadata/**: Metadata JSON files (titles, descriptions, hashtags)

Files are automatically managed by the system. Do not manually modify unless necessary.
"""
    
    with open("storage/README.md", "w", encoding="utf-8") as f:
        f.write(storage_readme)
    
    print("\n" + "=" * 60)
    print("✓ Initialization Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Review configuration: config/settings.yaml")
    print("  2. Start the watcher: python -m shortsfactory.watcher")
    print("  3. Start workers: python -m shortsfactory.workers.manager")
    print("  4. Start dashboard: python -m shortsfactory.dashboard.app")
    print()
    print("Or use the main entry point:")
    print("  python -m shortsfactory.main --help")
    print()
    
    logger.info("System initialization completed successfully")


if __name__ == "__main__":
    try:
        init_system()
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}", file=sys.stderr)
        sys.exit(1)
