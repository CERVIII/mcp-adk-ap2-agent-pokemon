"""Shopping Agent entry point"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))

from ap2.agents.shopping.agent import main
import asyncio

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main())
