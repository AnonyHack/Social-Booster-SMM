from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import re
import requests
import time
from datetime import datetime
import pytz
from functions import getData, updateUser, add_order, is_banned, get_locked_services
from config import MEGAHUB_PANEL_API, MEGAHUB_PANEL_API_URL, PAYMENT_CHANNEL, FREE_ORDERS_DAILY_LIMIT, ADMIN_USER_IDS
from orders import send_order_notification  # Reuse notification function
from notification_image import create_order_notification, cleanup_image  # For image generation

def process_free_quantity(bot, message, service, service_markup, main_markup, next_step_handler):
    """Process quantity for free orders (no balance check)"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    elif message.text == "⌫ ɢᴏ ʙᴀᴄᴋ":
        bot.reply_to(message, "↩️ Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ Sᴇʀᴠɪᴄᴇꜱ...", reply_markup=service_markup)
        return
    
    try:
        quantity = int(message.text)
        if quantity < service['min']:
            bot.reply_to(message, f"❌ Mɪɴɪᴍᴜᴍ Oʀᴅᴇʀ ɪꜱ {service['min']}", reply_markup=service_markup)
            return
        if quantity > service['max']:
            bot.reply_to(message, f"❌ Mᴀxɪᴍᴜᴍ Oʀᴅᴇʀ ɪꜱ {service['max']}", reply_markup=service_markup)
            return
            
        cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_markup.add(KeyboardButton("✘ Cancel"))
        
        bot.reply_to(message, f"🔗 Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ {service['link_hint']}:", reply_markup=cancel_markup)
        bot.register_next_step_handler(
            message, 
            next_step_handler,
            service,
            quantity
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ", reply_markup=service_markup)

def process_free_link(bot, message, service, quantity, link_pattern, service_markup, service_type, PAYMENT_CHANNEL, main_markup):
    """Process link for free orders (no balance deduction, uses Megahub API)"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
        
    link = message.text.strip()
    
    if not re.match(link_pattern, link):
        bot.reply_to(message, f"❌ Iɴᴠᴀʟɪᴅ {service_type} ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ", reply_markup=service_markup)
        return
    
    user_id = str(message.from_user.id)
    try:
        response = requests.post(
            MEGAHUB_PANEL_API_URL,
            data={
                'key': MEGAHUB_PANEL_API,
                'action': 'add',
                'service': service['service_id'],
                'link': link,
                'quantity': quantity
            },
            timeout=30
        )
        result = response.json()
        
        if result and result.get('order'):
            order_id = str(result['order'])
            order_data = {
                'service': service['name'],
                'service_type': service_type,
                'service_id': service['service_id'],
                'quantity': quantity,
                'cost': '0.00',  # Free for users
                'order_id': order_id,
                'status': 'pending',
                'timestamp': time.time(),
                'username': message.from_user.username or str(message.from_user.id)
            }
            
            add_order(user_id, order_data)
            
            # Update free order count
            data = getData(user_id)
            data['free_orders_today'] = data.get('free_orders_today', 0) + 1
            data['last_free_order_date'] = datetime.now(pytz.timezone('Africa/Harare')).strftime('%Y-%m-%d')
            if 'orders_count' not in data:
                data['orders_count'] = 0
            data['orders_count'] += 1
            updateUser(user_id, data)
            
            # Send notification with generated image
            send_order_notification(
                bot, PAYMENT_CHANNEL, message, service, quantity, '0.00', link, order_id
            )

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                text="📊 Cʜᴇᴄᴋ Oʀᴅᴇʀ Sᴛᴀᴛᴜꜱ",
                url=f"https://t.me/{PAYMENT_CHANNEL.lstrip('@')}"
            ))
            
            bot.reply_to(
                message,
                f"""✅ <b>{service['name']} Oʀᴅᴇʀ Sᴜʙᴍɪᴛᴛᴇᴅ!</b>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Qᴜᴀɴᴛɪᴛʏ:</b> {quantity}
💰 <b>Cᴏꜱᴛ:</b> Free
━━━━━━━━━━━━━━━━━━━━━━━
📎 <b>Lɪɴᴋ:</b> {link}
🆔 <b>Oʀᴅᴇʀ ID:</b> {order_id}
━━━━━━━━━━━━━━━━━━━━━━━
😊 <b>Tʜᴀɴᴋꜱ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ꜰʀᴇᴇ ꜱᴇʀᴠɪᴄᴇ!</b>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
⚠️ <b>Wᴀʀɴɪɴɢ:</b> Dᴏ ɴᴏᴛ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴀᴍᴇ ᴏʀᴅᴇʀ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ʟɪɴᴋ ʙᴇꜰᴏʀᴇ ᴛʜᴇ ꜰɪʀꜱᴆ ᴏɴᴇ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!""",
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )

            go_back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            go_back_markup.add(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))
            bot.send_message(
                message.chat.id,
                "🔙 Yᴏᴜ ᴄᴀɴ ɢᴏ ʙᴀᴄᴋ ᴛᴏ ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇꜱ ᴍᴇɴᴜ ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ.",
                reply_markup=go_back_markup
            )

        else:
            error_msg = result.get('error', 'Uɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ ꜰʀᴏᴍ Mᴇɢᴀʜᴜʙ ᴘᴀɴᴇʟ')
            raise Exception(error_msg)
            
    except requests.Timeout:
        bot.reply_to(
            message,
            "⚠️ Tʜᴇ ᴏʀᴅᴇʀ ɪꜱ ᴛᴀᴋɪɴɢ ʟᴏɴɢᴇʀ ᴛʜᴀɴ ᴇxᴘᴇᴄᴛᴇᴅ. Pʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴏʀᴅᴇʀ ꜱᴛᴀᴛᴜꜱ ʟᴀᴛᴇʀ.",
            reply_markup=main_markup
        )
    except Exception as e:
        print(f"Eʀʀᴏʀ ꜱᴜʙᴍɪᴛᴛɪɴɢ {service['name']} ᴏʀᴅᴇʀ: {str(e)}")
        bot.reply_to(
            message,
            f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ꜱᴜʙᴍɪᴛ {service['name']} ᴏʀᴅᴇʀ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
            reply_markup=main_markup
        )

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def register_free_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL):
    # --- Free Main Menu ---
    free_send_orders_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    free_send_orders_markup.row(
        KeyboardButton("📱 Free Telegram"),
        KeyboardButton("🌐 Free Instagram")
    )
    free_send_orders_markup.row(
        KeyboardButton("🎵 Free TikTok"),
        KeyboardButton("📘 Free Facebook")
    )
    free_send_orders_markup.add(KeyboardButton("⌫ ᴍᴀɪɴ ᴍᴇɴᴜ"))

    # --- Free Telegram Services ---
    free_telegram_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    free_telegram_services_markup.row(
        KeyboardButton("👀 Free TG Views"),
        KeyboardButton("❤️ Free TG Reactions")
    )
    free_telegram_services_markup.row(
        KeyboardButton("👥 Free TG Members")
    )
    free_telegram_services_markup.add(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

    # --- Free Instagram Services ---
    free_instagram_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    free_instagram_services_markup.row(
        KeyboardButton("🎥 Free Insta Views")
    )
    # Uncomment below if you want to include more buttons later
    # free_instagram_services_markup.row(
    #     KeyboardButton("❤️ Insta Likes"),
    #     KeyboardButton("👥 Insta Followers")
    # )
    free_instagram_services_markup.add(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

    # --- Free Tiktok Services ---
    free_tiktok_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    free_tiktok_services_markup.row(
        KeyboardButton("👀 Free Tiktok Views"),
    )
    free_tiktok_services_markup.add(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

    # --- Free Facebook Services ---
    free_facebook_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    free_facebook_services_markup.row(
        #KeyboardButton("👀 Free FB Views"),
        KeyboardButton("👀 Free FB Followers")

    )
    free_facebook_services_markup.add(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))


    # Telegram free services dictionary
    telegram_free_services = {
        "👀 Free TG Views": {
            "name": "TG Views",
            "quality": "High Quality",
            "min": 10,
            "max": 100,  # Strict limit for free service
            "price": 0,  # Free for users
            "unit": "1k views",
            "service_id": "357",  # TODO: Replace with actual Megahub service ID
            "link_hint": "TG post link",
            "icon": "👀"
        },
        "❤️ Free TG Reactions": {
            "name": "TG Reactions",
            "quality": "High Quality",
            "min": 40,
            "max": 40,  # Strict limit for free service
            "price": 0,  # Free for users
            "unit": "1k reactions",
            "service_id": "312",  # TODO: Replace with actual Megahub service ID
            "link_hint": "TG post link",
            "icon": "❤️"
        },
        "👥 Free TG Members": {
            "name": "TG Members",
            "quality": "High Quality",
            "min": 10,
            "max": 10,  # Strict limit for free service
            "price": 0,  # Free for users
            "unit": "1k members",
            "service_id": "480",  # TODO: Replace with actual Megahub service ID
            "link_hint": "TG group/channel link",
            "icon": "👥"
        }

    }

    # Instagram free services dictionary
    instagram_free_services = {
        "🎥 Free Insta Views": {
            "name": "Insta Views",
            "quality": "High Quality",
            "min": 10,
            "max": 100,  # Strict limit for free service
            "price": 0,  # Free for users
            "unit": "1k views",
            "service_id": "671",  # TODO: Replace with actual Megahub service ID
            "link_hint": "Insta reel link",
            "icon": "🎥"
        },
       # "❤️ Free Insta Likes": {
       #     "name": "Free Instagram Likes",
       #     "quality": "High Quality",
       #     "min": 10,
       #     "max": 100,  # Strict limit for free service
       #     "price": 0,  # Free for users
       #     "unit": "1k likes",
       #     "service_id": "0",  # TODO: Replace with actual Megahub service ID
       #     "link_hint": "Instagram post link",
       #     "icon": "❤️"
       # },
       # "❤️ Free Insta Followers": {
       #     "name": "Free Instagram Followers",
       #     "quality": "High Quality",
       #     "min": 10,
       #     "max": 100,  # Strict limit for free service
       #     "price": 0,  # Free for users
       #     "unit": "1k followers",
       #     "service_id": "0",  # TODO: Replace with actual Megahub service ID
       #     "link_hint": "Instagram post link",
       #     "icon": "❤️"
    }
        # Tiktok free services dictionary
    tiktok_free_services = {
            "👀 Free Tiktok Views": {
            "name": "Tiktok Video Views",
            "quality": "High Quality",
            "min": 10,
            "max": 100,  # Strict limit for free service
            "price": 0,  # Free for users
            "unit": "1k views",
            "service_id": "678",  # TODO: Replace with actual Megahub service ID
            "link_hint": "TikTok video link",
            "icon": "👀"
        },
    }
            # Facebook free services dictionary
    facebook_free_services = {
           # "👀 Free FB Views": {
           # "name": "FB Views",
           # "quality": "High Quality",
           # "min": 10,
           # "max": 100,  # Strict limit for free service
           # "price": 0,  # Free for users
           # "unit": "1k views",
           # "service_id": "0",  # TODO: Replace with actual Megahub service ID
           # "link_hint": "Facebook video link",
           # "icon": "👀"
           #},
            "👀 Free FB Followers": {
            "name": "FB Followers",
            "quality": "No Refill",
            "min": 10,
            "max": 10,  # Strict limit for free service
            "price": 0,  # Free for users
            "unit": "1k views",
            "service_id": "674",  # TODO: Replace with actual Megahub service ID
            "link_hint": "Facebook profile link",
            "icon": "👀"
        },
    }
        
    def order_free_menu(message):
        user_id = str(message.from_user.id)
        if is_banned(user_id):
            bot.reply_to(message, "⛔ Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ.")
            return
        
        # Update user activity (matching orders.py)
        data = getData(user_id)
        data['last_activity'] = time.time()
        data['username'] = message.from_user.username or str(message.from_user.id)
        
        # Check daily free order limit
        current_date = datetime.now(pytz.timezone('Africa/Harare')).strftime('%Y-%m-%d')
        last_free_order_date = data.get('last_free_order_date', '')
        free_orders_today = data.get('free_orders_today', 0)
        
        if last_free_order_date != current_date:
            # Reset count for new day
            data['free_orders_today'] = 0
            data['last_free_order_date'] = current_date
            free_orders_today = 0
        
        if free_orders_today >= FREE_ORDERS_DAILY_LIMIT:
            bot.reply_to(message, f"❌ Yᴏᴜ ʜᴀᴠᴇ ʀᴇᴀᴄʜᴇᴅ ᴛʜᴇ ᴅᴀɪʟʏ ʟɪᴍɪᴛ ᴏꜱ {FREE_ORDERS_DAILY_LIMIT} ꜰʀᴇᴇ ᴏʀᴅᴇʀ(ꜱ). Tʀʏ ᴀɢᴀɪɴ ᴛᴏᴍᴏʀʀᴏᴡ.")
            return
        
        updateUser(user_id, data)

        bot.reply_to(message, "🆓 Fʀᴇᴇ Sᴇʀᴠɪᴄᴇꜱ:", reply_markup=free_send_orders_markup)

    def order_free_telegram_menu(message):
        bot.reply_to(message, "📱 Fʀᴇᴇ Tᴇʟᴇɢʀᴀᴍ Sᴇʀᴠɪᴄᴇꜱ:", reply_markup=free_telegram_services_markup)

    def order_free_instagram_menu(message):
        bot.reply_to(message, "🌐 Fʀᴇᴇ Iɴꜱᴛᴀɢʀᴀᴍ Sᴇʀᴠɪᴄᴇꜱ:", reply_markup=free_instagram_services_markup)

    def order_free_tiktok_menu(message):
        bot.reply_to(message, "🎵 Fʀᴇᴇ TɪᴋTᴏᴋ Sᴇʀᴠɪᴄᴇꜱ:", reply_markup=free_tiktok_services_markup)

    def order_free_facebook_menu(message):
        bot.reply_to(message, "📘 Fʀᴇᴇ Fᴀᴄᴇʙᴏᴏᴋ Sᴇʀᴠɪᴄᴇꜱ:", reply_markup=free_facebook_services_markup)

    def handle_free_telegram_order(message):
        if message.text not in telegram_free_services:
            return
        
        service = telegram_free_services[message.text]
        user_id = str(message.from_user.id)

        # Check if the service is locked for non-admins (matching orders.py)
        admin_user_ids = [int(uid) if isinstance(uid, str) else uid for uid in ADMIN_USER_IDS if str(uid).isdigit()]
        locked_services = get_locked_services()
        if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
            bot.reply_to(message, "🚫 Tʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
            return

        # Create cancel/back markup (matching orders.py)
        cancel_back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_back_markup.row(
            KeyboardButton("✘ Cancel"),
            KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ")
        )

        msg = f"""⭐️ ｢{service['name']} Dᴇᴛᴀɪʟꜱ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
📌 Oʀᴅᴇʀ ID: {service['service_id']}
━━━━━━━━━━━━━━━━━━━━━━━
📉 Mɪɴɪᴍᴜᴍ: {service['min']}
📈 Mᴀxɪᴍᴜᴍ: {service['max']}
━━━━━━━━━━━━━━━━━━━━━━━
💰 Pʀɪᴄᴇ: Free
━━━━━━━━━━━━━━━━━━━━━━━
🔗 Lɪɴᴋ Hɪɴᴛ: {service['link_hint']}
━━━━━━━━━━━━━━━━━━━━━━━
💎 Qᴜᴀʟɪᴛʏ: {service['quality']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 Eɴᴛᴇʀ Qᴜᴀɴᴛɪᴛʏ:
━━━━━━━━━━━━━━━━━━━━━━━"""
        
        bot.reply_to(message, msg, reply_markup=cancel_back_markup)
        bot.register_next_step_handler(
            message,
            lambda msg: process_free_quantity(
                bot, msg, service, free_telegram_services_markup, main_markup,
                lambda m, s, q: process_free_link(
                    bot, m, s, q, r'^https?://(t\.me|telegram\.me)/',
                    free_telegram_services_markup, 'telegram', PAYMENT_CHANNEL, main_markup
                )
            )
        )

    def handle_free_tiktok_order(message):
        if message.text not in tiktok_free_services:
            return

        service = tiktok_free_services[message.text]
        user_id = str(message.from_user.id)

        # Check if the service is locked for non-admins (matching orders.py)
        admin_user_ids = [int(uid) if isinstance(uid, str) else uid for uid in ADMIN_USER_IDS if str(uid).isdigit()]
        locked_services = get_locked_services()
        if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
            bot.reply_to(message, "🚫 Tʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
            return

        # Create cancel/back markup (matching orders.py)
        cancel_back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_back_markup.row(
            KeyboardButton("✘ Cancel"),
            KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ")
        )

        msg = f"""⭐️ ｢{service['name']} Dᴇᴛᴀɪʟꜱ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
📌 Oʀᴅᴇʀ ID: {service['service_id']}
━━━━━━━━━━━━━━━━━━━━━━━
📉 Mɪɴɪᴍᴜᴍ: {service['min']}
📈 Mᴀxɪᴍᴜᴍ: {service['max']}
━━━━━━━━━━━━━━━━━━━━━━━
💰 Pʀɪᴄᴇ: Free
━━━━━━━━━━━━━━━━━━━━━━━
🔗 Lɪɴᴋ Hɪɴᴛ: {service['link_hint']}
━━━━━━━━━━━━━━━━━━━━━━━
💎 Qᴜᴀʟɪᴛʏ: {service['quality']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 Eɴᴛᴇʀ Qᴜᴀɴᴛɪᴛʏ:
━━━━━━━━━━━━━━━━━━━━━━━"""
        
        bot.reply_to(message, msg, reply_markup=cancel_back_markup)
        bot.register_next_step_handler(
            message,
            lambda msg: process_free_quantity(
                bot, msg, service, free_tiktok_services_markup, main_markup,
                lambda m, s, q: process_free_link(
                    bot, m, s, q, r'^https?://(www\.tiktok\.com|tiktok\.com)/',
                    free_tiktok_services_markup, 'tiktok', PAYMENT_CHANNEL, main_markup
                )
            )
        )

    def handle_free_instagram_order(message):
        if message.text not in instagram_free_services:  # FIXED: Changed from facebook_free_services to instagram_free_services
            return

        service = instagram_free_services[message.text]  # FIXED: Changed from facebook_free_services to instagram_free_services
        user_id = str(message.from_user.id)

        # Check if the service is locked for non-admins (matching orders.py)
        admin_user_ids = [int(uid) if isinstance(uid, str) else uid for uid in ADMIN_USER_IDS if str(uid).isdigit()]
        locked_services = get_locked_services()
        if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
            bot.reply_to(message, "🚫 Tʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
            return

        # Create cancel/back markup (matching orders.py)
        cancel_back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_back_markup.row(
            KeyboardButton("✘ Cancel"),
            KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ")
        )

        msg = f"""⭐️ ｢{service['name']} Dᴇᴛᴀɪʟꜱ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
📌 Oʀᴅᴇʀ ID: {service['service_id']}
━━━━━━━━━━━━━━━━━━━━━━━
📉 Mɪɴɪᴍᴜᴍ: {service['min']}
📈 Mᴀxɪᴍᴜᴍ: {service['max']}
━━━━━━━━━━━━━━━━━━━━━━━
💰 Pʀɪᴄᴇ: Free
━━━━━━━━━━━━━━━━━━━━━━━
🔗 Lɪɴᴋ Hɪɴᴛ: {service['link_hint']}
━━━━━━━━━━━━━━━━━━━━━━━
💎 Qᴜᴀʟɪᴛʏ: {service['quality']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 Eɴᴛᴇʀ Qᴜᴀɴᴛɪᴛʏ:
━━━━━━━━━━━━━━━━━━━━━━━"""
        
        bot.reply_to(message, msg, reply_markup=cancel_back_markup)
        bot.register_next_step_handler(
            message,
            lambda msg: process_free_quantity(
                bot, msg, service, free_instagram_services_markup, main_markup,
                lambda m, s, q: process_free_link(
                    bot, m, s, q, r'^https?://(www\.instagram\.com|instagram\.com)/',
                    free_instagram_services_markup, 'instagram', PAYMENT_CHANNEL, main_markup
                )
            )
        )

    def handle_free_facebook_order(message):
        if message.text not in facebook_free_services:
            return
        
        service = facebook_free_services[message.text]
        user_id = str(message.from_user.id)

        # Check if the service is locked for non-admins (matching orders.py)
        admin_user_ids = [int(uid) if isinstance(uid, str) else uid for uid in ADMIN_USER_IDS if str(uid).isdigit()]
        locked_services = get_locked_services()
        if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
            bot.reply_to(message, "🚫 Tʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
            return

        # Create cancel/back markup (matching orders.py)
        cancel_back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_back_markup.row(
            KeyboardButton("✘ Cancel"),
            KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ")
        )

        msg = f"""⭐️ ｢{service['name']} Dᴇᴛᴀɪʟꜱ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
📌 Oʀᴅᴇʀ ID: {service['service_id']}
━━━━━━━━━━━━━━━━━━━━━━━
📉 Mɪɴɪᴍᴜᴍ: {service['min']}
📈 Mᴀxɪᴍᴜᴍ: {service['max']}
━━━━━━━━━━━━━━━━━━━━━━━
💰 Pʀɪᴄᴇ: Free
━━━━━━━━━━━━━━━━━━━━━━━
🔗 Lɪɴᴋ Hɪɴᴛ: {service['link_hint']}
━━━━━━━━━━━━━━━━━━━━━━━
💎 Qᴜᴀʟɪᴛʏ: {service['quality']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 Eɴᴛᴇʀ Qᴜᴀɴᴛɪᴛʏ:
━━━━━━━━━━━━━━━━━━━━━━━"""
        
        bot.reply_to(message, msg, reply_markup=cancel_back_markup)
        bot.register_next_step_handler(
            message,
            lambda msg: process_free_quantity(
                bot, msg, service, free_facebook_services_markup, main_markup,
                lambda m, s, q: process_free_link(
                    bot, m, s, q, r'^https?://(www\.facebook\.com|facebook\.com)/',
                    free_facebook_services_markup, 'facebook', PAYMENT_CHANNEL, main_markup
                )
            )
        )

    # Register handlers
    bot.register_message_handler(order_free_menu, func=lambda m: m.text == "🆓 Free Services")
    bot.register_message_handler(order_free_telegram_menu, func=lambda m: m.text == "📱 Free Telegram")
    bot.register_message_handler(order_free_instagram_menu, func=lambda m: m.text == "🌐 Free Instagram")
    bot.register_message_handler(order_free_tiktok_menu, func=lambda m: m.text == "🎵 Free TikTok")
    bot.register_message_handler(order_free_facebook_menu, func=lambda m: m.text == "📘 Free Facebook")
    bot.register_message_handler(handle_free_telegram_order, func=lambda m: m.text in telegram_free_services)
    bot.register_message_handler(handle_free_instagram_order, func=lambda m: m.text in instagram_free_services)
    bot.register_message_handler(handle_free_tiktok_order, func=lambda m: m.text in tiktok_free_services)
    bot.register_message_handler(handle_free_facebook_order, func=lambda m: m.text in facebook_free_services)
    bot.register_message_handler(
        lambda m: bot.reply_to(m, "↩️ Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ Fʀᴇᴇ Sᴇʀᴠɪᴄᴇꜱ...", reply_markup=free_send_orders_markup),
        func=lambda m: m.text == "⌫ ɢᴏ ʙᴀᴄᴋ"
    )
    bot.register_message_handler(
        lambda m: bot.reply_to(m, "🔙 Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ Mᴀɪɴ Mᴇɴᴜ...", reply_markup=main_markup),
        func=lambda m: m.text == "⌫ ᴍᴀɪɴ ᴍᴇɴᴜ"
    )
