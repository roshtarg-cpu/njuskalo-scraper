"""Main entry point for running as module."""
from .main import main
import asyncio

if __name__ == '__main__':
    asyncio.run(main())
