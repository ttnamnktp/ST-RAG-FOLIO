# config.py
from enum import Enum

class LLMProvider(Enum):
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    GROQ = "groq"

# ===== OLLAMA LOCAL - UNLIMITED FREE =====
USE_PROVIDER = LLMProvider.OLLAMA
# LLM_MODEL = "qwen2.5:3b"
LLM_MODEL = "qwen2.5:14b"
LLM_API_KEY = "ollama"
LLM_BASE_URL = "http://localhost:11434/v1"

# ==========================================

# Cấu hình chung
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
TOP_K = 3
MAX_TOKENS = 512
TEMPERATURE = 0.1

# Đường dẫn
TRANSLATION_KB_PATH = "kb/translation_kb"
FIXER_KB_PATH = "kb/fixer_kb"