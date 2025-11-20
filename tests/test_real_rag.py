"""Test real RAG retrieval with ChromaDB."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adk.rag.retriever import Retriever

async def test_real_rag():
    print("Testing Real RAG Retriever...")
    
    # Initialize
    retriever = Retriever()
    
    # Test Query
    query = "How should I handle user requests to delete their data?"
    print(f"\nQuery: '{query}'")
    
    # Retrieve
    results = await retriever.retrieve(query, top_k=2)
    
    print(f"\nFound {len(results)} relevant regulations:")
    for res in results:
        print(f"- {res['metadata']['name']} {res['metadata']['article']} (Distance: {res['distance']:.4f})")
        print(f"  Text: {res['text'][:100]}...")
        
    # Assertions
    # Should find GDPR Article 17 (Right to Erasure)
    found_erasure = any("17(1)" in r['metadata']['article'] for r in results)
    
    if found_erasure:
        print("\nSUCCESS: Found GDPR Right to Erasure!")
    else:
        print("\nFAILURE: Did not find relevant regulation.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_real_rag())
