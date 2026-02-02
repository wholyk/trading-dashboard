"""
Main entry point for ShortsFactory.
Provides commands to run different components.
"""

import sys
import argparse
import subprocess
from shortsfactory.core.logger import get_logger


def run_init():
    """Initialize the system"""
    from shortsfactory.init import init_system
    init_system()


def run_watcher():
    """Run the inbox watcher"""
    from shortsfactory.watcher import main
    main()


def run_workers():
    """Run the worker manager"""
    from shortsfactory.workers.manager import main
    main()


def run_dashboard():
    """Run the dashboard"""
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "shortsfactory/dashboard/app.py",
        "--server.port=8501",
        "--server.address=localhost"
    ])


def run_all():
    """Run all components (for development/testing)"""
    import threading
    
    logger = get_logger("main")
    logger.info("Starting all components")
    
    print("=" * 60)
    print("Starting ShortsFactory - All Components")
    print("=" * 60)
    print()
    print("Starting:")
    print("  - Inbox Watcher")
    print("  - Worker Manager")
    print("  - Dashboard (http://localhost:8501)")
    print()
    print("Press CTRL+C to stop all components")
    print("=" * 60)
    print()
    
    # Start watcher in thread
    watcher_thread = threading.Thread(target=run_watcher, daemon=True)
    watcher_thread.start()
    
    # Start workers in thread
    workers_thread = threading.Thread(target=run_workers, daemon=True)
    workers_thread.start()
    
    # Run dashboard in main thread (blocks)
    try:
        run_dashboard()
    except KeyboardInterrupt:
        print("\nShutting down all components...")
        logger.info("Shutdown requested")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ShortsFactory - YouTube Shorts Production System"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Init command
    subparsers.add_parser("init", help="Initialize the system")
    
    # Watcher command
    subparsers.add_parser("watcher", help="Run the inbox watcher")
    
    # Workers command
    subparsers.add_parser("workers", help="Run the worker manager")
    
    # Dashboard command
    subparsers.add_parser("dashboard", help="Run the dashboard")
    
    # All command
    subparsers.add_parser("all", help="Run all components (watcher, workers, dashboard)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate function
    if args.command == "init":
        run_init()
    elif args.command == "watcher":
        run_watcher()
    elif args.command == "workers":
        run_workers()
    elif args.command == "dashboard":
        run_dashboard()
    elif args.command == "all":
        run_all()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
