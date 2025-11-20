"""Seed RAG with regulation data."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adk.rag.vector_store import get_vector_store

REGULATIONS = [
    {
        "text": "GDPR Article 5(1)(f): Personal data shall be processed in a manner that ensures appropriate security of the personal data, including protection against unauthorised or unlawful processing and against accidental loss, destruction or damage, using appropriate technical or organisational measures ('integrity and confidentiality').",
        "metadata": {"name": "GDPR", "article": "5(1)(f)", "topic": "security"}
    },
    {
        "text": "GDPR Article 17(1): The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her without undue delay and the controller shall have the obligation to erase personal data without undue delay where one of the following grounds applies...",
        "metadata": {"name": "GDPR", "article": "17(1)", "topic": "right_to_erasure"}
    },
    {
        "text": "HIPAA Security Rule 45 CFR 164.312(a)(1): Implement technical policies and procedures for electronic information systems that maintain electronic protected health information to allow access only to those persons or software programs that have been granted access rights as specified in § 164.308(a)(4).",
        "metadata": {"name": "HIPAA", "article": "164.312(a)(1)", "topic": "access_control"}
    },
    {
        "text": "HIPAA Privacy Rule 45 CFR 164.502(a): A covered entity or business associate may not use or disclose protected health information, except as permitted or required by this subpart or by subpart C of part 160 of this subchapter.",
        "metadata": {"name": "HIPAA", "article": "164.502(a)", "topic": "privacy"}
    }
]

async def seed_rag():
    print("Seeding RAG with regulations...")
    
    try:
        vector_store = get_vector_store()
        
        texts = [r["text"] for r in REGULATIONS]
        metadatas = [r["metadata"] for r in REGULATIONS]
        ids = [f"{r['metadata']['name']}_{r['metadata']['article']}" for r in REGULATIONS]
        
        await vector_store.add_documents(texts, metadatas, ids)
        
        print(f"Successfully added {len(texts)} regulations to ChromaDB.")
        
    except Exception as e:
        print(f"Error seeding RAG: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(seed_rag())
