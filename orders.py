from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import re, os
import requests
import time
from functions import getData, cutBalance, add_order, updateUser, get_affiliate_earnings, add_affiliate_earning, get_locked_services
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from io import BytesIO
import os

from notification_image import create_order_notification, cleanup_image

def send_order_notification(bot, PAYMENT_CHANNEL, message, service, quantity, cost, link, order_id):
    """Send order notification"""
    try:
        image_path = create_order_notification(
            bot=bot,
            user_id=message.from_user.id,
            user_name=message.from_user.first_name,
            service_name=service['name']
        )
        
        if image_path:
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("🔗 View Order Link", url=link),
                InlineKeyboardButton("🤖 Visit Bot", url=f"https://t.me/{bot.get_me().username}")
            )
            
            caption = f"""⭐️ ｢ɴᴇᴡ {service['name']} ᴏʀᴅᴇʀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
👤 <b>Uꜱᴇʀ:</b> {message.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━━
🕵🏻‍♂️ <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Uꜱᴇʀ Iᴅ:</b> {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']} {service.get('icon', '')}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Qᴜᴀɴᴛɪᴛʏ:</b> {quantity}
💰 <b>Cᴏꜱᴛ:</b> {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Oʀᴅᴇʀ Iᴅ:</b> <code>{order_id}</code>
━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Sᴛᴀᴛᴜꜱ:</b> <code>PENDING</code>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━"""
            
            with open(image_path, 'rb') as photo:
                bot.send_photo(
                    PAYMENT_CHANNEL,
                    photo,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=markup
                )
            
            os.remove(image_path)
        else:
            bot.send_message(
                PAYMENT_CHANNEL,
                caption,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"Error sending notification: {e}")
        bot.send_message(
            PAYMENT_CHANNEL,
            f"New order: {service['name']} by {message.from_user.first_name}",
            disable_web_page_preview=True
        )

def process_order_quantity(bot, message, service, service_markup, main_markup, next_step_handler):
    """Process order quantity"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Order cancelled.", reply_markup=main_markup)
        return
    elif message.text == "⌫ ɢᴏ ʙᴀᴄᴋ":
        bot.reply_to(message, "Returning to Services...", reply_markup=service_markup)
        return
    
    try:
        quantity = int(message.text)
        if quantity < service['min']:
            bot.reply_to(message, f"❌ Minimum Order is {service['min']}", reply_markup=service_markup)
            return
        if quantity > service['max']:
            bot.reply_to(message, f"❌ Maximum Order is {service['max']}", reply_markup=service_markup)
            return
            
        cost = (quantity * service['price']) // 1000
        user_data = getData(str(message.from_user.id))
        
        if float(user_data['balance']) < cost:
            bot.reply_to(message, f"❌ Insufficient Balance. You need {cost} coins.", reply_markup=service_markup)
            return
            
        cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_markup.add(KeyboardButton("✘ Cancel"))
        
        bot.reply_to(message, f"🔗 Please send the {service['link_hint']}:", reply_markup=cancel_markup)
        bot.register_next_step_handler(
            message, 
            next_step_handler,
            service,
            quantity,
            cost
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Please enter a valid number", reply_markup=service_markup)

        
def process_order_link(bot, message, service, quantity, cost, link_pattern, service_markup, service_type, PAYMENT_CHANNEL, main_markup):
    """Process order link"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
        
    link = message.text.strip()
    
    if not re.match(link_pattern, link):
        bot.reply_to(message, f"❌ Iɴᴠᴀʟɪᴅ {service_type} ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ", reply_markup=service_markup)
        return
    
    try:
        response = requests.post(
            os.getenv("SMM_PANEL_API_URL"),
            data={
                'key': os.getenv("SMM_PANEL_API_KEY"),
                'action': 'add',
                'service': service['service_id'],
                'link': link,
                'quantity': quantity
            },
            timeout=30
        )
        result = response.json()
        
        if result and result.get('order'):
            if not cutBalance(str(message.from_user.id), cost):
                raise Exception("Failed to deduct balance")
            
            order_data = {
                'service': service['name'],
                'service_type': service_type,
                'service_id': service['service_id'],
                'quantity': quantity,
                'cost': cost,
                'order_id': str(result['order']),
                'status': 'pending',
                'timestamp': time.time(),
                'username': message.from_user.username or str(message.from_user.id)
            }
            
            add_order(str(message.from_user.id), order_data)
            
            send_order_notification(
                bot,
                PAYMENT_CHANNEL,
                message,
                service,
                quantity,
                cost,
                link,
                result['order']
            )

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                text="📊 Check Order Status",
                url=f"https://t.me/{PAYMENT_CHANNEL.lstrip('@')}"
            ))
            
            bot.reply_to(
                message,
f"""✅ <b>{service['name']} Oʀᴅᴇʀ Sᴜʙᴍɪᴛᴛᴇᴅ!</b>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Qᴜᴀɴᴛɪᴛʏ:</b> {quantity}
💰 <b>Cᴏꜱᴛ:</b> {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
📎 <b>Lɪɴᴋ:</b> {link}
🆔 <b>Oʀᴅᴇʀ ID:</b> {result['order']}
━━━━━━━━━━━━━━━━━━━━━━━
😊 <b>Tʜᴀɴᴋꜱ ꜰᴏʀ ᴏʀᴅᴇʀɪɴɢ!</b>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
⚠️ <b>𝙒𝙖𝙧𝙣𝙞𝙣𝙜:</b> Dᴏ ɴᴏᴛ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴀᴍᴇ ᴏʀᴅᴇʀ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ʟɪɴᴋ ʙᴇꜰᴏʀᴇ ᴛʜᴇ ꜰɪʀꜱᴛ ᴏɴᴇ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!""",
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )

            go_back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
            go_back_markup.add(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

            bot.send_message(
    message.chat.id,
    "✅ Your order was submitted! Use the button below to go back and place another order.",
    reply_markup=go_back_markup
)

            # Update user data with order count
            user_id = str(message.from_user.id)
            data = getData(user_id)
            if 'orders_count' not in data:
                data['orders_count'] = 0
            data['orders_count'] += 1
            updateUser(user_id, data)

            if data.get('ref_by') and data['ref_by'] != "none":
                try:
                    commission = cost * 0.05
                    add_affiliate_earning(data['ref_by'], commission)

                    bot.send_message(
                        data['ref_by'],
                        f"🎉 <b>Aꜰꜰɪʟɪᴀᴛᴇ Cᴏᴍᴍɪꜱꜱɪᴏɴ Rᴇᴄᴇɪᴠᴇᴅ!</b>\n\n"
                        f"💸 <b>Yᴏᴜ'ᴠᴇ �ᴇᴀʀɴᴇᴅ:</b> <code>{commission:.2f} ᴄᴏɪɴꜱ</code>\n"
                        f"👤 <b>Fʀᴏᴍ:</b> {message.from_user.first_name}\n"
                        f"📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']}\n"
                        f"💵 <b>Oʀᴅᴇʀ Vᴀʟᴜᴇ:</b> {cost} ᴄᴏɪɴꜱ\n"
                        f"🆔 <b>Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ID:</b> <code>{int(time.time())}</code>\n\n"
                        f"🚀 <i>Kᴇᴇᴘ sʜᴀʀɪɴɢ ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟ ʟɪɴᴋ ᴛᴏ ᴇᴀʀɴ ᴍᴏʀᴇ!</i>",
                        parse_mode='HTML'
                    )
                except Exception as e:
                    print(f"Failed to send affiliate notification: {e}")

        else:
            error_msg = result.get('error', 'Uɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ ꜰʀᴏᴍ SMM ᴘᴀɴᴇʟ')
            raise Exception(error_msg)
            
    except requests.Timeout:
        bot.reply_to(
            message,
            "⚠️ Tʜᴇ ᴏʀᴅᴇʀ ɪꜱ ᴛᴀᴋɪɴɢ ʟᴏɴɢᴇʀ ᴛʜᴀɴ ᴇxᴘᴇᴄᴛᴇᴅ. Pʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ ᴀɴᴅ ᴏʀᴅᴇʀ ꜱᴛᴀᴛᴜꜱ ʟᴀᴛᴇʀ.",
            reply_markup=main_markup
        )
    except Exception as e:
        print(f"Eʀʀᴏʀ ꜱᴜʙᴍɪᴛᴛɪɴɢ {service['name']} ᴏʀᴅᴇʀ: {str(e)}")
        bot.reply_to(
            message,
            f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ꜱᴜʙᴍɪᴛ {service['name']} ᴏʀᴅᴇʀ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
            reply_markup=main_markup
        )

# ======================= TWITTER HANDLERS ======================= #
def register_twitter_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL):
    twitter_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    twitter_services_markup.row(
        KeyboardButton("🔼 X Views"),
        KeyboardButton("❤️ X Likes")
    )
    twitter_services_markup.row(
        KeyboardButton("🔁 X Retweets"),
        KeyboardButton("👤 X Followers")
    )
    twitter_services_markup.row(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

    twitter_services = {
        "🔼 X Views": {
            "name": "Tweet Views",
            "quality": "Fast Delivery",
            "min": 1000,
            "max": 100000,
            "price": 200,
            "unit": "1k views",
            "service_id": "21477",
            "link_hint": "X Video link",
            "icon": "👀"
        },
        "❤️ X Likes": {
            "name": "Tweet Likes",
            "quality": "Real & Active",
            "min": 100,
            "max": 10000,
            "price": 3000,
            "unit": "1k likes",
            "service_id": "11741",
            "link_hint": "Tweet link",
            "icon": "❤️"
        },
        "🔁 X Retweets": {
            "name": "Tweet Retweets",
            "quality": "No Refill",
            "min": 100,
            "max": 10000,
            "price": 4500,
            "unit": "1k retweets",
            "service_id": "20478",
            "link_hint": "Tweet link",
            "icon": "🔄"
        },
        "👤 X Followers": {
            "name": "Twitter Followers",
            "quality": "No Refill",
            "min": 200,
            "max": 1000000,
            "price": 20000,
            "unit": "1k followers",
            "service_id": "20399",
            "link_hint": "Twitter profile link",
            "icon": "👥"
        }
    }

    def order_twitter_menu(message):
        bot.reply_to(message, "🐦 Twitter/X Services:", reply_markup=twitter_services_markup)

    def handle_twitter_order(message):
        service = twitter_services[message.text]

                # Check if the service is locked for non-admins
        locked_services = get_locked_services()
        admin_ids_env = os.getenv("ADMIN_USER_IDS", "")
        admin_user_ids = [int(uid.strip()) for uid in admin_ids_env.split(",") if uid.strip().isdigit()]
        if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
            bot.reply_to(message, "🚫 ᴛʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
            return
        
        # Create a cancel and back button markup
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
💰 Pʀɪᴄᴇ: {service['price']} ᴄᴏɪɴꜱ / {service['unit']}
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
            lambda msg: process_order_quantity(
                bot,
                msg,
                service,
                twitter_services_markup,
                main_markup,
                lambda m, s, q, c: process_twitter_link(m, s, q, c)
            )

        )

    def process_twitter_link(message, service, quantity, cost):
        process_order_link(
            bot, message, service, quantity, cost,
            r'^https?://(www\.)?(tiktok\.com|vm\.tiktok\.com)/',
            twitter_services_markup,
            'twitter',
            PAYMENT_CHANNEL,
            main_markup
        )

    bot.register_message_handler(order_twitter_menu, func=lambda m: m.text == "🐦 Order Twitter/X")
    bot.register_message_handler(handle_twitter_order, func=lambda m: m.text in twitter_services)

# ======================= SPOTIFY HANDLERS ======================= #
def register_spotify_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL):
    spotify_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    spotify_services_markup.row(
        KeyboardButton("👥 Spotify Followers"),
        KeyboardButton("💾 Spotify Saves")
    )
    spotify_services_markup.row(
        KeyboardButton("▶️ Spotify Plays"),
        KeyboardButton("📈 Monthly Listeners")
    )
    spotify_services_markup.row(
        KeyboardButton("🎙 Podcast Plays"),
        KeyboardButton("📻 Radio Plays")
    )
    spotify_services_markup.row(
        KeyboardButton("🏆 Chart-Top 50"),
        KeyboardButton("⚡ Algorithmic Plays")
    )
    spotify_services_markup.row(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

    spotify_services = {
        "👥 Spotify Followers": {
            "name": "Spotify Followers",
            "quality": "Refill 90Days",
            "min": 100,
            "max": 100000,
            "price": 3000,
            "unit": "1k followers",
            "service_id": "19304",
            "link_hint": "Profile link",
            "icon": "👥"
        },
        "💾 Spotify Saves": {
            "name": "Spotify Saves",
            "quality": "No Refill",
            "min": 100,
            "max": 1000000,
            "price": 1800,
            "unit": "1k saves",
            "service_id": "19331",
            "link_hint": "Track link",
            "icon": "💾"
        },
        "▶️ Spotify Plays": {
            "name": "Spotify Plays",
            "quality": "Refill 365Days",
            "min": 1000,
            "max": 100000,
            "price": 800,
            "unit": "1k plays",
            "service_id": "19450",
            "link_hint": "Track link",
            "icon": "▶️"
        },
        "📈 Monthly Listeners": {
            "name": "Monthly Listeners",
            "quality": "Refill 30Days",
            "min": 500,
            "max": 1000000,
            "price": 12000,
            "unit": "1k listeners",
            "service_id": "19385",
            "link_hint": "Profile link",
            "icon": "📈"
        },
            "🎙 Podcast Plays": {
                "name": "Podcast Plays",
                "quality": "Refill 365Days",
                "min": 500,
                "max": 20000000,
                "price": 2500,
                "unit": "1k plays",
                "service_id": "19402",
                "link_hint": "Podcast link"
            },
            "📻 Radio Plays": {
                "name": "Radio Plays",
                "quality": "Mixed Premium",
                "min": 500,
                "max": 20000000,
                "price": 5200,
                "unit": "1k plays",
                "service_id": "15682",
                "link_hint": "Track Link(To place an order, insert your track link in the \"link\" field. Only track links in the https://open.spotify.com/track/xxx format are accepted. Please avoid using https://spotify.link/xxxx)."
            },
            "🏆 Chart-Top 50": {
                "name": "Chart-Top 50",
                "quality": "Premium Mix",
                "min": 2000,
                "max": 5000000,
                "price": 20000,
                "unit": "1k placements",
                "service_id": "19408",
                "link_hint": "Track Link: To place an order, insert your track link in the \"link\" field. Only track or album links in the https://open.spotify.com/track/xxx or https://open.spotify.com/album/xxx format are accepted. Please avoid using https://spotify.link/xxxx."
            },
            "⚡ Algorithmic Plays": {
                "name": "Algorithmic Plays",
                "quality": "Mix Premium",
                "min": 500,
                "max": 2000000,
                "price": 5200,
                "unit": "1k plays",
                "service_id": "15586",
                "link_hint": "Track Link(To place an order, insert your track link in the \"link\" field. Only track links in the https://open.spotify.com/track/xxx format are accepted. Please avoid using https://spotify.link/xxxx.)"
            }
        }

    def order_spotify_menu(message):
        bot.reply_to(message, "🎶 Spotify Services:", reply_markup=spotify_services_markup)

    def handle_spotify_order(message):
        service = spotify_services[message.text]

                        # Check if the service is locked for non-admins
        locked_services = get_locked_services()
        admin_ids_env = os.getenv("ADMIN_USER_IDS", "")
        admin_user_ids = [int(uid.strip()) for uid in admin_ids_env.split(",") if uid.strip().isdigit()]
        if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
            bot.reply_to(message, "🚫 ᴛʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
            return
        
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
💰 Pʀɪᴄᴇ: {service['price']} ᴄᴏɪɴꜱ / {service['unit']}
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
            lambda msg: process_order_quantity(
                bot,
                msg,
                service,
                spotify_services_markup,
                main_markup,
                lambda m, s, q, c: process_spotify_link(m, s, q, c)
            )

        )

    def process_spotify_link(message, service, quantity, cost):
        process_order_link(
            bot, message, service, quantity, cost,
            r'^https?://(open\.spotify\.com)/',
            spotify_services_markup,
            'spotify',
            PAYMENT_CHANNEL,
            main_markup
        )

    bot.register_message_handler(order_spotify_menu, func=lambda m: m.text == "🎶 Order Spotify")
    bot.register_message_handler(handle_spotify_order, func=lambda m: m.text in spotify_services)

# ======================= PINTEREST HANDLERS ======================= #
def register_pinterest_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL):
    pinterest_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    pinterest_services_markup.row(
        KeyboardButton("📌 Pinterest Followers"),
        KeyboardButton("❤️ Pinterest Likes")
    )
    pinterest_services_markup.row(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

    pinterest_services = {
        "📌 Pinterest Followers": {
            "name": "Pinterest Followers",
            "quality": "High Quality",
            "min": 200,
            "max": 10000,
            "price": 23000,  # Adjust price as needed
            "unit": "1k followers",
            "service_id": "21597",
            "link_hint": "Profile link",
            "icon": "👥"
        },
        "❤️ Pinterest Likes": {
            "name": "Pinterest Likes",
            "quality": "Real & Active",
            "min": 100,
            "max": 50000,
            "price": 21000,  # Adjust price as needed
            "unit": "1k likes",
            "service_id": "21599",
            "link_hint": "Pin link",
            "icon": "❤️"
        }
    }

    def order_pinterest_menu(message):
        bot.reply_to(message, "📛 Pinterest Services:", reply_markup=pinterest_services_markup)

    def handle_pinterest_order(message):
        service = pinterest_services[message.text]

                        # Check if the service is locked for non-admins
        locked_services = get_locked_services()
        admin_ids_env = os.getenv("ADMIN_USER_IDS", "")
        admin_user_ids = [int(uid.strip()) for uid in admin_ids_env.split(",") if uid.strip().isdigit()]
        if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
            bot.reply_to(message, "🚫 ᴛʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
            return
        
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
💰 Pʀɪᴄᴇ: {service['price']} ᴄᴏɪɴꜱ / {service['unit']}
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
            lambda msg: process_order_quantity(
                bot,
                msg,
                service,
                pinterest_services_markup,
                main_markup,
                lambda m, s, q, c: process_pinterest_link(m, s, q, c)
            )
        )

    def process_pinterest_link(message, service, quantity, cost):
        process_order_link(
            bot, message, service, quantity, cost,
            r'^https?://(www\.)?pinterest\.(com|ru|fr|de|it|es|co\.uk|ca|com\.au|com\.mx|co\.jp|pt|pl|nl|co\.nz|co\.in|com\.br)/',
            pinterest_services_markup,
            'pinterest',
            PAYMENT_CHANNEL,
            main_markup
        )

    bot.register_message_handler(order_pinterest_menu, func=lambda m: m.text == "📛 Order Pinterest")
    bot.register_message_handler(handle_pinterest_order, func=lambda m: m.text in pinterest_services)

# ======================= SNAPCHAT HANDLERS ======================= #
def register_snapchat_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL):
    snapchat_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    snapchat_services_markup.row(
        KeyboardButton("👥 Snapchat Followers"),
        KeyboardButton("❤️ Snapchat Likes")
    )
    snapchat_services_markup.row(
        KeyboardButton("👀 Snapchat Views"),
    )

    snapchat_services_markup.row(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

    snapchat_services = {
        "👥 Snapchat Followers": {
            "name": "Snapchat Followers",
            "quality": "Real & NonDrop",
            "min": 100,
            "max": 15000,
            "price": 97000,  # Adjust price as needed
            "unit": "1k followers",
            "service_id": "19584",
            "link_hint": "Profile username",
            "icon": "👥"
        },
        "❤️ Snapchat Likes": {
            "name": "Snapchat Likes+Views",
            "quality": "Real & NonDrop",
            "min": 100,
            "max": 10000,
            "price": 215000,  # Adjust price as needed
            "unit": "1k likes",
            "service_id": "21779",
            "link_hint": "Snap link",
            "icon": "❤️"
        },
        "👀 Snapchat Views": {
            "name": "Snapchat Views+Likes",
            "quality": "Real & NonDrop",
            "min": 10,
            "max": 10000,
            "price": 173000,  # Adjust price as needed
            "unit": "1k views",
            "service_id": "19583",
            "link_hint": "Snap link",
            "icon": "👀"
        }
    }


    def order_snapchat_menu(message):
        bot.reply_to(message, "👻 Snapchat Services:", reply_markup=snapchat_services_markup)

    def handle_snapchat_order(message):
        service = snapchat_services[message.text]

                        # Check if the service is locked for non-admins
        locked_services = get_locked_services()
        admin_ids_env = os.getenv("ADMIN_USER_IDS", "")
        admin_user_ids = [int(uid.strip()) for uid in admin_ids_env.split(",") if uid.strip().isdigit()]
        if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
            bot.reply_to(message, "🚫 ᴛʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
            return
        
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
💰 Pʀɪᴄᴇ: {service['price']} ᴄᴏɪɴꜱ / {service['unit']}
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
            lambda msg: process_order_quantity(
                bot,
                msg,
                service,
                snapchat_services_markup,
                main_markup,
                lambda m, s, q, c: process_snapchat_link(m, s, q, c)
            )
        )

    def process_snapchat_link(message, service, quantity, cost):
        # Snapchat doesn't use traditional URLs, so we'll validate the format
        link = message.text.strip()
        valid = True
        
        # Basic validation - adjust as needed
        if "snapchat.com" in link or "snapchat.com/add" in link:
            # Profile link format
            pass
        elif len(link) > 3 and not " " in link:
            # Username format
            pass
        else:
            valid = False
            
        if not valid:
            bot.reply_to(message, "❌ Invalid Snapchat format. Please provide a valid username or profile link", 
                        reply_markup=snapchat_services_markup)
            return
            
        process_order_link(
            bot, message, service, quantity, cost,
            r'.+',  # Basic pattern since Snapchat doesn't use standard URLs
            snapchat_services_markup,
            'snapchat',
            PAYMENT_CHANNEL,
            main_markup
        )

    bot.register_message_handler(order_snapchat_menu, func=lambda m: m.text == "👻 Order Snapchat")
    bot.register_message_handler(handle_snapchat_order, func=lambda m: m.text in snapchat_services)

# ======================= MAIN REGISTRATION ======================= #
def register_order_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL):
    register_twitter_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL)
    register_spotify_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL)
    register_pinterest_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL)
    register_snapchat_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL)
    # Add more service registrations here as needed

