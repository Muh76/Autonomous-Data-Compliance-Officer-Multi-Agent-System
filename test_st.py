
import sys
try:
    print("Importing sentence_transformers...")
    from sentence_transformers import SentenceTransformer
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully.")
    emb = model.encode("test")
    print(f"Embedding shape: {emb.shape}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
