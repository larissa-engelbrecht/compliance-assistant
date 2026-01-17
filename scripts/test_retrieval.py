import os
import sys

# 1. Setup Path (So we can import from 'app')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Import the Config (The "Best Practice" way)
from app.config import Config
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding

# 3. Validate Config
Config.validate()

# 4. Configure Gemini
print("Initializing Gemini...")
Settings.embed_model = GeminiEmbedding(
    model_name="models/text-embedding-004", 
    api_key=Config.GOOGLE_API_KEY
)
Settings.llm = None 

# 5. Connect to DB (Using the clean Config object)
print(f"Connecting to DB at {Config.DB_HOST}...")
vector_store = PGVectorStore.from_params(
    database=Config.DB_NAME,
    host=Config.DB_HOST,
    password=Config.DB_PASSWORD,
    port=Config.DB_PORT,
    user=Config.DB_USER,
    table_name=Config.TABLE_NAME,
    embed_dim=Config.EMBED_DIM
)

# 6. Search Logic
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

query = "What are the prohibited AI practices?"
print(f"\nQuerying: '{query}'")
print("-" * 50)

# Retrieve top 3 matches
retriever = index.as_retriever(similarity_top_k=3)
nodes = retriever.retrieve(query)

for node in nodes:
    print(f"\n[Score: {node.score:.4f}]")
    # Clean up newlines for display
    clean_text = node.text.replace("\n", " ")[:250] 
    print(f"{clean_text}...")

print("-" * 50)