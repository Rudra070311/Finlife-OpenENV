"""
FinLife-OpenEnv Server Entry Point
Can be launched via: python -m server.app or via uv run server
"""

import sys
import os
import argparse
import logging

# Add root directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.insert(0, root_dir)

import uvicorn
from app.config import EnvConfig

# Import the FastAPI app from api_server
from api_server import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the server"""
    parser = argparse.ArgumentParser(description="FinLife-OpenEnv API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on file changes")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers (default: 1)")
    
    args = parser.parse_args()
    
    logger.info(f"Starting FinLife-OpenEnv API Server...")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Reload: {args.reload}")
    logger.info(f"Workers: {args.workers}")
    
    # Run the FastAPI app
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level="info",
    )


if __name__ == "__main__":
    main()
