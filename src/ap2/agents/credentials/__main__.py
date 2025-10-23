"""Credentials Provider entry point"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[3]))

from ap2.agents.credentials.server import app

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    load_dotenv()
    port = int(os.getenv("CREDENTIALS_PROVIDER_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
