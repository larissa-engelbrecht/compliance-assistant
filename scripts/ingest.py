import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import Config
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.readers.file import PyMuPDFReader

# Validate config
Config.validate()

# Configure Gemini
print("Initializing Gemini...")
Settings.embed_model = GeminiEmbedding(
    model_name="models/text-embedding-004",
    api_key=Config.GOOGLE_API_KEY
)
Settings.llm = None

# Connect to Postgres
print("Connecting to Postgres...")
vector_store = PGVectorStore.from_params(
    database=Config.DB_NAME,
    host=Config.DB_HOST,
    password=Config.DB_PASSWORD,
    port=Config.DB_PORT,
    user=Config.DB_USER,
    table_name=Config.TABLE_NAME,
    embed_dim=Config.EMBED_DIM
)

# Read PDF
print("Reading documents...")
file_extractor = {".pdf": PyMuPDFReader()}
documents = SimpleDirectoryReader(
    "./data", 
    file_extractor=file_extractor
).load_data()

print(f"Loaded {len(documents)} pages.")

# Ingest into Vector Store
print("Ingesting data...(This may take a while)")
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    show_progress=True
)

print("Successfully ingested PDF!")