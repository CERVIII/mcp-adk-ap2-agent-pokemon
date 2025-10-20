"""Credentials Provider entry point"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.credentials_provider.server import app

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    load_dotenv()
    port = int(os.getenv("CREDENTIALS_PROVIDER_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
