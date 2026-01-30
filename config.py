import os
from typing import List

API_ID = os.environ.get("API_ID", "27806628")
API_HASH = os.environ.get("API_HASH", "25d88301e886b82826a525b7cf52e090")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8554483339:AAG7hUH9R7EtDjuk9kECoxNikeUEIx6Qs90")
ADMIN = int(os.environ.get("ADMIN", "1255023013"))
PICS = (os.environ.get("PICS", "https://i.ibb.co/MDssddJp/pic.jpg https://i.ibb.co/n8fQ2xcx/pic.jpg https://i.ibb.co/LDxwffYv/pic.jpg https://i.ibb.co/m5BN0XPD/pic.jpg")).split()
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002686843200"))
NEW_REQ_MODE = os.environ.get("NEW_REQ_MODE", "True").lower() == "true"
DB_URI = os.environ.get("DB_URI", "mongodb+srv://Bosshub:JMaff0WvazwNxKky@cluster0.l0xcoc1.mongodb.net/?appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "approve")
IS_FSUB = os.environ.get("IS_FSUB", "False").lower() == "true"  # Set "True" For Enable Force Subscribe
AUTH_CHANNELS = list(map(int, os.environ.get("AUTH_CHANNEL", "").split())) # Add Multiple channel ids
AUTH_REQ_CHANNELS = list(map(int, os.environ.get("AUTH_REQ_CHANNEL", "").split())) # Add Multiple channel ids
FSUB_EXPIRE = int(os.environ.get("FSUB_EXPIRE", 0))  # minutes, 0 = no expiry
