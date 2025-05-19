import os
from dotenv import load_dotenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

TRANSLATOR_CONFIG = {
    "MODEL": os.environ.get("TRANSLATOR_MODEL"),
    "API_URL": os.environ.get("TRANSLATOR_API_URL"),
    "API_KEY": os.environ.get("TRANSLATOR_API_KEY"),
}   
