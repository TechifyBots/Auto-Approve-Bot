import os
import requests
from typing import List

API_ID = os.environ.get("API_ID", "")
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN = int(os.environ.get("ADMIN", "1255023013"))
PICS: List[str] = requests.get("https://raw.githubusercontent.com/TechifyBots/TechifyBots/main/assets/pics.txt").text.split()
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002686843200"))
NEW_REQ_MODE = os.environ.get("NEW_REQ_MODE", "True").lower() == "true"
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "approve")
PING_URL = os.environ.get("PING_URL", "") # Service URL for Keep-Alive
VERSION = os.environ.get("VERSION", "3.0")
SOURCE_CODE = os.environ.get("SOURCE_CODE", "https://github.com/TechifyBots/Auto-Approve-Bot")
