"""
Command-line interface for running the LaTeX compilation server.
"""

import argparse
import logging
import sys

import uvicorn

from latex_server import __version__
from latex_server.config import settings

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="LaTeX Compilation Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--host",
        default=settings.host,
        help="Host to bind the server to",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help="Port to bind the server to",
    )

    parser.add_argument(
        "--log-level",
        default=settings.log_level,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development mode)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the CLI.
    """
    args = parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info(f"Starting LaTeX Compilation Server v{__version__}")
    logger.info(f"Server will be available at http://{args.host}:{args.port}")

    try:
        uvicorn.run(
            "latex_server.app:app",
            host=args.host,
            port=args.port,
            log_level=args.log_level.lower(),
            reload=args.reload,
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
