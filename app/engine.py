from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from app.config import Config

# 1. Setup Models
Settings.embed_model = GeminiEmbedding(
    model_name="models/text-embedding-004", 
    api_key=Config.GOOGLE_API_KEY
)
Settings.llm = Gemini(
    model="models/gemini-flash-latest", 
    api_key=Config.GOOGLE_API_KEY
)

def get_chat_engine():
    """
    Connects to the DB and returns a Chat Engine that knows the EU AI Act.
    """
    # Connect to your existing Postgres DB
    vector_store = PGVectorStore.from_params(
        database=Config.DB_NAME,
        host=Config.DB_HOST,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        table_name=Config.TABLE_NAME,
        embed_dim=Config.EMBED_DIM
    )

    # Load the Index
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Create the Chat Engine (Context Chat Mode)
    # "context" mode means: "Retrieve data first, then answer"
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        system_prompt=(
            "You are a Senior EU AI Act Compliance Consultant. "
            "Use the provided context to answer questions accurately. "
            "If the answer is not in the context, say you don't know. "
            "Cite the specific Article numbers if possible."
        )
    )
    
    return chat_engine