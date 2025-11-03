from os import getenv
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ───── Bot Configuration ───── #
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
SMM_PANEL_API = os.getenv("SMM_PANEL_API_KEY", "")
SMM_PANEL_API_URL = os.getenv("SMM_PANEL_API_URL", "")
MEGAHUB_PANEL_API = os.getenv("MEGAHUB_PANEL_API", "")
MEGAHUB_PANEL_API_URL = os.getenv("MEGAHUB_PANEL_API_URL", "")

# ───── Database Settings ───── #
MONGODB_URI = getenv("MONGODB_URI", "")
DATABASE_NAME = getenv("DATABASE_NAME", "smmhubbooster") 

# Admins (comma-separated list in .env)
ADMIN_USER_IDS = [int(id.strip()) for id in getenv("ADMIN_USER_IDS", "").split(",") if id.strip()]

# ───── User Settings ───── #
FREE_ORDERS_DAILY_LIMIT = int(getenv("FREE_ORDERS_DAILY_LIMIT", 3))
WELCOME_BONUS = int(getenv("WELCOME_BONUS", 30)) 
REF_BONUS = int(getenv("REF_BONUS", 50)) 

# ───── Maintenance Settings ───── #
MAINTENANCE_AUTO_DISABLE_TIME = int(getenv("MAINTENANCE_AUTO_DISABLE_TIME", "1440"))  # 1 hour in seconds
MAINTENANCE_MODE = getenv("MAINTENANCE_MODE", "False").lower() == "true" # Convert to boolean

# ───── Server Settings ───── #
PORT = int(getenv("PORT", "10000")) # Default port for webhooks
KEEP_ALIVE_ENABLED = getenv("KEEP_ALIVE_ENABLED", "True").lower() == "true" # Convert to boolean

# ───── Links & URLs ───── #
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/XPTOOLSTEAM")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/nextgenroom")
UPDATES_CHANNEL_LINK = getenv("UPDATES_CHANNEL_LINK", "https://t.me/XPTOOLSTEAM")
WELCOME_IMAGE_URL = getenv("WELCOME_IMAGE_URL", "https://i.ibb.co/1JYDJ34S/smmlogo.jpg")
PAYMENT_CHANNEL = getenv("PAYMENT_CHANNEL", "@xptoolslogs")
WHATSAPP_CHANNEL = getenv("WHATSAPP_CHANNEL", "https://whatsapp.com/channel/0029VbB3G3BH5JM0s7gtKA2d")
SUPPORT_BOT = getenv("SUPPORT_BOT", "https://t.me/SocialHubBoosterTMbot")

# ───── Force Join Channels ───── #
REQUIRED_CHANNELS = getenv("REQUIRED_CHANNELS", "XPTOOLSTEAM,Freenethubz,SmmBoosterz,Freenethubchannel").split(",")  # Comma-separated channel usernames
CHANNEL_BUTTONS = {
    "Freenethubz": {"name": "📢 PROMOTER CHANNEL", "url": "https://t.me/Freenethubz"},
    "WHATSAPP_CHANNEL": {"name": "📱 WHATSAPP", "url": "https://whatsapp.com/channel/0029VaDnY2y0rGiPV41aSX0l"},
    "BOTS_UPDATE_CHANNEL": {"name": "🤖 BOTS UPDATE", "url": "https://t.me/XPTOOLSTEAM"},
    "SERVICES_UPDATE": {"name": "🏪 SERVICES UPDATE", "url": "https://t.me/SmmBoosterz"},
    "COINS_CHANNEL": {"name": "🪙 COINS STORE", "url": "https://t.me/Freenethubchannel"}
}



