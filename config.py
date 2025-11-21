# ==============================================
# 📝 Configuration (Environment Variables)
# ==============================================
# This file reads configuration from environment variables.
# For local development: use .env file
# For production (Render): set environment variables in dashboard

import os
from dotenv import load_dotenv

# Load environment variables from .env (only for local development)
load_dotenv()

def get_required_env(key: str) -> str:
    """Get required environment variable"""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"환경 변수 '{key}'가 설정되지 않았습니다. Render 대시보드에서 환경변수를 확인하세요.")
    return value

# ==============================================
# 1. OpenAI Settings
# ==============================================
OPENAI_API_KEY = get_required_env("OPENAI_API_KEY")

# ==============================================
# 2. Supabase Settings
# ==============================================
SUPABASE_URL = get_required_env("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = get_required_env("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_TABLE_NAME = "mysql_data_embeddings"
SUPABASE_QUERY_NAME = "match_mysql_embeddings"

# Supabase tables config (for compatibility)
SUPABASE_TABLES = {
    "embeddings": SUPABASE_TABLE_NAME,
    "match_function": SUPABASE_QUERY_NAME
}

# ==============================================
# 3. Cafe24 MySQL Database Settings
# ==============================================
CAFE24_DB_CONFIG = {
    "host": os.getenv("CAFE24_DB_HOST"),
    "port": int(os.getenv("CAFE24_DB_PORT", "3306")),
    "user": os.getenv("CAFE24_DB_USER"),
    "password": os.getenv("CAFE24_DB_PASSWORD"),
    "database": os.getenv("CAFE24_DB_DATABASE"),
    "charset": os.getenv("CAFE24_DB_CHARSET", "utf8mb4")
}

# MySQL connection toggle
USE_MYSQL_CONNECTION = os.getenv("USE_MYSQL_CONNECTION", "True").lower() == "true"

# ==============================================
# 4. Data Extraction Config (JSON files)
# ==============================================
DATA_EXTRACTION_CONFIG = {
    "processed_data": {
        "json_file": "data/processed_data.json",
        "table": "processed_data",
        "columns": ["id", "content", "metadata"],
        "text_columns": ["content"],
        "metadata_columns": ["id", "metadata"]
    }
}

# ==============================================
# 5. Embedding Config
# ==============================================
EMBEDDING_CONFIG = {
    "model": "text-embedding-3-small",
    "chunk_size": 500,
    "chunk_overlap": 50
}

# ==============================================
# 6. LLM Config
# ==============================================
LLM_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 1000
}

# ==============================================
# 7. Retrieval Config
# ==============================================
RETRIEVAL_CONFIG = {
    "k": 5,
    "hybrid_weight": 0.7
}

# ==============================================
# 8. Chatbot Config (for web interface)
# ==============================================
CHATBOT_CONFIG = {
    "model": LLM_CONFIG["model"],
    "temperature": LLM_CONFIG["temperature"],
    "max_tokens": LLM_CONFIG["max_tokens"],
    "search_results_count": RETRIEVAL_CONFIG["k"]
}

# ==============================================
# 9. Logging Config
# ==============================================
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s"
}
