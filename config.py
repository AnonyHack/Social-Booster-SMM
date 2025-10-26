from os import getenv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ───── Bot Configuration ───── #
BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")
SMM_PANEL_API = getenv("SMM_PANEL_API_KEY")
SMM_PANEL_API_URL = getenv("SMM_PANEL_API_URL")

# Admins (comma-separated list in .env)
ADMIN_USER_IDS = [int(id.strip()) for id in getenv("ADMIN_USER_IDS", "").split(",") if id.strip()]

# Bonuses
WELCOME_BONUS = int(getenv("WELCOME_BONUS", 30))
REF_BONUS = int(getenv("REF_BONUS", 50))

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/XPTOOLSTEAM")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/nextgenroom")
UPDATES_CHANNEL_LINK = getenv("UPDATES_CHANNEL_LINK", "https://t.me/XPTOOLSTEAM")
WELCOME_IMAGE_URL = getenv("WELCOME_IMAGE_URL", "https://i.ibb.co/1JYDJ34S/smmlogo.jpg")
PAYMENT_CHANNEL = getenv("PAYMENT_CHANNEL", "@xptoolslogs")
WHATSAPP_CHANNEL = getenv("WHATSAPP_CHANNEL", "https://whatsapp.com/channel/0029VaDnY2y0rGiPV41aSX0l")

# ───── Force Join Channels ───── #
REQUIRED_CHANNELS = getenv("REQUIRED_CHANNELS", "XPTOOLSTEAM").split(",")  # Comma-separated channel usernames
CHANNEL_BUTTONS = {
    #"Freenethubz": {"name": "📢 PROMOTER CHANNEL", "url": "https://t.me/Freenethubz"},
    "WHATSAPP_CHANNEL": {"name": "📱 WHATSAPP", "url": "https://whatsapp.com/channel/0029VaDnY2y0rGiPV41aSX0l"},
    "BOTS_UPDATE_CHANNEL": {"name": "🤖 BOTS UPDATE", "url": "https://t.me/XPTOOLSTEAM"},
    #"BACKUP_CHANNEL": {"name": "🔙 BACKUP CHANNEL", "url": "https://t.me/Freenethubchannel"},
    #"COINS_STORE_CHANNEL": {"name": "🪙 COINS STORE CHANNEL", "url": "https://t.me/iCoinStores"}
}