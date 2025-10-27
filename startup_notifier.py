import pytz
from datetime import datetime
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PAYMENT_CHANNEL, WELCOME_IMAGE_URL  # image fallback


def get_formatted_datetime():
    """Get current datetime in East Africa Time (EAT) timezone"""
    tz = pytz.timezone('Africa/Nairobi')
    now = datetime.now(tz)
    return {
        'date': now.strftime('%Y-%m-%d'),
        'time': now.strftime('%I:%M:%S %p'),
        'timezone': now.strftime('%Z')  # 'EAT'
    }


def send_startup_message(bot: TeleBot, is_restart: bool = False):
    """Send bot startup or restart message (with image & button) to the logs channel."""
    try:
        dt = get_formatted_datetime()
        status = "Rᴇꜱᴛᴀʀᴛᴇᴅ" if is_restart else "Sᴛᴀʀᴛᴇᴅ"

        bot_info = bot.get_me()
        bot_username = bot_info.username
        bot_url = f"https://t.me/{bot_username}"

        # Try to get bot's profile picture
        try:
            photos = bot.get_user_profile_photos(bot_info.id, limit=1)
            if photos.total_count > 0:
                file_id = photos.photos[0][0].file_id  # smallest size
                image_source = file_id
            else:
                image_source = WELCOME_IMAGE_URL  # fallback
        except Exception:
            image_source = WELCOME_IMAGE_URL  # fallback if no photo

        message = f"""
<blockquote>
🚀 <b>Bᴏᴛ {status}</b> !

📅 Dᴀᴛᴇ : {dt['date']}
⏰ Tɪᴍᴇ : {dt['time']}
🌐 Tɪᴍᴇᴢᴏɴᴇ : {dt['timezone']}
🛠️ Bᴜɪʟᴅ Sᴛᴀᴛᴜꜱ: v2 [Sᴛᴀʙʟᴇ]
</blockquote>
"""

        # Inline button to open bot
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Oᴘᴇɴ Bᴏᴛ", url=bot_url)]
        ])

        # Send as photo (uses bot profile or fallback image)
        bot.send_photo(
            chat_id=PAYMENT_CHANNEL,
            photo=image_source,
            caption=message,
            parse_mode='HTML',
            reply_markup=markup
        )

    except Exception as e:
        print(f"[StartupNotifier] Error sending startup message: {e}")
