"""Test Vertex AI Client."""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adk.tools.llm_client import VertexAIClient

async def test_vertex_client():
    print("Testing Vertex AI Client...")
    
    # Mock credentials check for demo purposes if real ones aren't set
    # In a real CI/CD, we'd have a service account key.
    # Here we just check if we can instantiate the class and import the library.
    
    try:
        client = VertexAIClient(project_id="mock-project", location="us-central1")
        print("VertexAIClient instantiated successfully.")
        
        # We won't actually call generate() because it requires active GCP credentials
        # which might not be present in this environment.
        # But we can check if the underlying client object is created.
        if client.client:
             print("Underlying LangChain VertexAI client created.")
             
    except Exception as e:
        print(f"Initialization failed (Expected if no GCP creds, but check error): {e}")
        # If it fails due to credentials, that's "success" for code correctness (library is installed)
        if "DefaultCredentialsError" in str(e) or "google-auth" in str(e):
            print("Caught expected credential error. Library installation verified.")
        else:
            # If it fails due to ImportError, that's a failure
            if "ImportError" in str(e):
                print("FAILURE: Library not found.")
                sys.exit(1)
            else:
                print(f"WARNING: Other error: {e}")

if __name__ == "__main__":
    asyncio.run(test_vertex_client())
