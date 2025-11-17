"""Main entry point for ADCO system."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.main import app
import uvicorn
from adk.config import get_config

if __name__ == "__main__":
    config = get_config()
    api_config = config.get("api", {})
    
    uvicorn.run(
        app,
        host=api_config.get("host", "0.0.0.0"),
        port=api_config.get("port", 8000),
        reload=config.get("app", {}).get("debug", False),
    )

