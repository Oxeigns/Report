# config.py
# Developed by @oxeign
import os

API_ID = int(os.environ.get("24090342") or 0)      # set env var API_ID to avoid editing file
API_HASH = os.environ.get("b1bc1341aac0d5cea8da11872969142f") or ""     # set env var API_HASH
DEVELOPER = "@oxeign"

if API_ID == 0 or API_HASH == "":
    # fallback to manual edit if env not set
    # replace below values if you prefer editing file directly
    API_ID = 123456
    API_HASH = "your_api_hash_here"
