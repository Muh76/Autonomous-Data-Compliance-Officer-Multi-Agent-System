
import sys
try:
    print("Importing chromadb...")
    import chromadb
    print("ChromaDB imported.")
    
    print("Importing sentence_transformers...")
    from sentence_transformers import SentenceTransformer
    print("SentenceTransformers imported.")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
