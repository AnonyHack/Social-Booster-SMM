# adpanel.py
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from functions import (get_all_users,
    delete_user, lock_service, unlock_service, get_locked_services, isExists, getData,
    set_bonus_amount, set_bonus_interval, toggle_bonus, get_top_balances,
    get_top_affiliate_earners, get_suspicious_users, get_panel_balance, users_collection
)
import time
import requests
import logging
from config import MEGAHUB_PANEL_API, MEGAHUB_PANEL_API_URL, SUPPORT_BOT

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================= SHARED FUNCTIONS ======================= #
def format_timespan(seconds):
    intervals = (
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1)
    )
    result = []
    for name, count in intervals:
        value = int(seconds // count)
        if value:
            seconds -= value * count
            result.append(f"{value} {name}")
    return ', '.join(result[:2])

def delete_after_delay(bot, chat_id, message_id, delay):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Could not delete message: {e}")

# ======================= LOCK/UNLOCK SERVICES ======================= #
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from functions import lock_service, unlock_service, get_locked_services, get_all_users
import time

def register_lock_handlers(bot, admin_markup, admin_user_ids):
    lock_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    lock_markup.row(KeyboardButton("🔒 Lock Service"))
    lock_markup.row(KeyboardButton("🔓 Unlock Service"))
    lock_markup.row(KeyboardButton("📋 List Locked Services"))
    lock_markup.row(KeyboardButton("🔙 Admin Panel"))

    def lock_service_menu(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        bot.reply_to(message, "🔒 Service Lock Management:", reply_markup=lock_markup)

    def handle_lock_service(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        bot.reply_to(message, "📝 ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ *ꜱᴇʀᴠɪᴄᴇ ɪᴅ* ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʟᴏᴄᴋ:", parse_mode="Markdown")
        bot.register_next_step_handler(message, process_lock_service)

    def process_lock_service(message):
        if message.text.lower() == 'cancel':
            bot.reply_to(message, "❌ Oᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=admin_markup)
            return

        service_id = message.text.strip()
        if lock_service(service_id):
            bot.reply_to(
                message,
                f"✅ *Sᴇʀᴠɪᴄᴇ {service_id} ʜᴀꜱ ʙᴇᴇɴ ʟᴏᴄᴋᴇᴅ ꜰᴏʀ ʀᴇɢᴜʟᴀʀ ᴜꜱᴇʀꜱ.*\n"
                f"Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɴᴏᴛɪꜰʏ ᴜꜱᴇʀꜱ? *(yes/no)*",
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(message, lambda m: process_notify_lock(m, service_id))
        else:
            bot.reply_to(message, f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ʟᴏᴄᴋ ꜱᴇʀᴠɪᴄᴇ `{service_id}`.", parse_mode="Markdown", reply_markup=admin_markup)

    def process_notify_lock(message, service_id):
        choice = message.text.lower()
        if choice == 'yes':
            notify_users_about_service(service_id, action="lock")
            bot.reply_to(message, "📢 Nᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ ꜱᴇɴᴛ ᴛᴏ ᴜꜱᴇʀꜱ.", reply_markup=admin_markup)
        else:
            bot.reply_to(message, "👍 Nᴏ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ ᴡᴇʀᴇ ꜱᴇɴᴛ.", reply_markup=admin_markup)

    def handle_unlock_service(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        bot.reply_to(message, "📝 ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ *ꜱᴇʀᴠɪᴄᴇ ɪᴅ* ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜɴʟᴏᴄᴋ:", parse_mode="Markdown")
        bot.register_next_step_handler(message, process_unlock_service)

    def process_unlock_service(message):
        if message.text.lower() == 'cancel':
            bot.reply_to(message, "❌ Oᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=admin_markup)
            return

        service_id = message.text.strip()
        if unlock_service(service_id):
            bot.reply_to(
                message,
                f"✅ *Sᴇʀᴠɪᴄᴇ {service_id} ʜᴀꜱ ʙᴇᴇɴ ᴜɴʟᴏᴄᴋᴇᴅ ꜰᴏʀ ᴀʟʟ ᴜꜱᴇʀꜱ.*\n"
                f"Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɴᴏᴛɪꜰʏ ᴜꜱᴇʀꜱ? *(yes/no)*",
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(message, lambda m: process_notify_unlock(m, service_id))
        else:
            bot.reply_to(message, f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴜɴʟᴏᴄᴋ ꜱᴇʀᴠɪᴄᴇ `{service_id}`.", parse_mode="Markdown", reply_markup=admin_markup)

    def process_notify_unlock(message, service_id):
        choice = message.text.lower()
        if choice == 'yes':
            notify_users_about_service(service_id, action="unlock")
            bot.reply_to(message, "📢 Nᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ ꜱᴇɴᴛ ᴛᴏ ᴜꜱᴇʀꜱ.", reply_markup=admin_markup)
        else:
            bot.reply_to(message, "👍 Nᴏ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ ᴡᴇʀᴇ ꜱᴇɴᴛ.", reply_markup=admin_markup)

    def notify_users_about_service(service_id, action):
        users = get_all_users()

        if action == "lock":
            text = (
                f"🚫 *Sᴇʀᴠɪᴄᴇ Uᴘᴅᴀᴛᴇ*\n\n"
                f"📌 *Service ID:* `{service_id}`\n"
                f"✅ *Status:* Lᴏᴄᴋᴇᴅ 🔒\n\n"
                f"Tʜᴇ sᴇʀᴠɪᴄᴇ ʜᴀs ʙᴇᴇɴ ᴛᴇᴍᴘᴏʀᴀʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴏᴜʀ Aᴅᴍɪɴ Tᴇᴀᴍ.\n"
                f"Yᴏᴜ ᴡɪʟʟ ɴᴏᴛ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴏʀᴅᴇʀ ᴛʜɪs sᴇʀᴠɪᴄᴇ ᴜɴᴛɪʟ ꜰᴜʀᴛʜᴇʀ ɴᴏᴛɪᴄᴇ.\n\n"            )
        else:
            text = (
                f"✅ *Sᴇʀᴠɪᴄᴇ Uᴘᴅᴀᴛᴇ*\n\n"
                f"📌 *Service ID:* `{service_id}`\n"
                f"✅ *Status:* Uɴʟᴏᴄᴋᴇᴅ 🔓\n\n"
                f"Tʜᴇ sᴇʀᴠɪᴄᴇ ɪs ɴᴏᴡ ᴀᴠᴀɪʟᴀʙʟᴇ ꜰᴏʀ ᴏʀᴅᴇʀɪɴɢ.\n\n"
            )

        for user_id in users:
            try:
                bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="Markdown"
                )
                time.sleep(0.05)  # Throttle
            except Exception as e:
                print(f"Failed to notify user {user_id}: {e}")

    def list_locked_services(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        locked_services = get_locked_services()
        if not locked_services:
            bot.reply_to(message, "🔓 ɴᴏ ꜱᴇʀᴠɪᴄᴇꜱ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ.", reply_markup=admin_markup)
            return

        services_list = "\n".join([f"• `{service_id}`" for service_id in locked_services])
        bot.reply_to(message, f"🔒 *Lᴏᴄᴋᴇᴅ Sᴇʀᴠɪᴄᴇꜱ:*\n{services_list}", parse_mode="Markdown", reply_markup=admin_markup)

    # Register buttons
    bot.register_message_handler(lock_service_menu, func=lambda m: m.text == "🔐 Lock/Unlock")
    bot.register_message_handler(handle_lock_service, func=lambda m: m.text == "🔒 Lock Service")
    bot.register_message_handler(handle_unlock_service, func=lambda m: m.text == "🔓 Unlock Service")
    bot.register_message_handler(list_locked_services, func=lambda m: m.text == "📋 List Locked Services")

# ======================= DELETE USER ======================= #
def register_delete_user_handlers(bot, admin_markup):
    def handle_delete_user(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        
        # Create cancel button
        cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        cancel_markup.add(KeyboardButton("⌧ ᴄᴀɴᴄᴇʟ ᴅᴇʟᴇᴛᴇ ⌧"))
            
        bot.reply_to(message, 
                    "🗑 <b>Dᴇʟᴇᴛᴇ Uꜱᴇʀ Aᴄᴄᴏᴜɴᴛ</b>\n\n"
                    "Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ ᴜꜱᴇʀ ID ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ:\n\n"
                    "⚠️ <b>Note:</b> Oɴʟʏ ɴᴜᴍᴇʀɪᴄ ᴜꜱᴇʀ IDs ᴀʀᴇ ᴀᴄᴄᴇᴘᴛᴇᴅ\n"
                    "📝 <b>Example:</b> <code>123456789</code>\n\n"
                    "❌ Click the button below to cancel:",
                    parse_mode="HTML",
                    reply_markup=cancel_markup)
        bot.register_next_step_handler(message, process_delete_user)

    def process_delete_user(message):
        # Check if user cancelled
        if message.text and message.text.strip() == "⌧ ᴄᴀɴᴄᴇʟ ᴅᴇʟᴇᴛᴇ ⌧":
            bot.reply_to(message, "❌ Dᴇʟᴇᴛᴇ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=admin_markup)
            return
            
        user_input = message.text.strip()
        
        # Validate if input is numeric (user ID)
        if not user_input.isdigit():
            bot.reply_to(message, 
                        "❌ <b>Iɴᴠᴀʟɪᴅ Uꜱᴇʀ ID</b>\n\n"
                        "Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍᴇʀɪᴄ ᴜꜱᴇʀ ID.\n"
                        "📝 <b>Example:</b> <code>123456789</code>\n\n"
                        "Try again or use the cancel button:",
                        parse_mode="HTML",
                        reply_markup=admin_markup)
            return
            
        user_id = user_input
        
        # Show checking animation
        checking_msg = bot.reply_to(message,
                    f"🔍 <b>Cʜᴇᴄᴋɪɴɢ Uꜱᴇʀ Dᴀᴛᴀʙᴀꜱᴇ...</b>\n\n"
                    f"🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"
                    f"⏳ Sᴇᴀʀᴄʜɪɴɢ ꜰᴏʀ ᴜꜱᴇʀ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ...\n\n"
                    f"[░░░░░░░░░░] 0%",
                    parse_mode="HTML")
        
        # Simulate checking progress
        for progress in [25, 50, 75, 100]:
            time.sleep(0.5)
            progress_bar = '█' * (progress // 10) + '░' * (10 - progress // 10)
            bot.edit_message_text(
                f"🔍 <b>Cʜᴇᴄᴋɪɴɢ Uꜱᴇʀ Dᴀᴛᴀʙᴀꜱᴇ...</b>\n\n"
                f"🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"
                f"⏳ Sᴇᴀʀᴄʜɪɴɢ ꜰᴏʀ ᴜꜱᴇʀ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ...\n\n"
                f"[{progress_bar}] {progress}%",
                message.chat.id,
                checking_msg.message_id,
                parse_mode="HTML"
            )
        
        # Check if user exists in database
        user_exists = isExists(user_id)
        
        if not user_exists:
            bot.edit_message_text(
                f"❌ <b>Uꜱᴇʀ Nᴏᴛ Fᴏᴜɴᴅ</b>\n\n"
                f"🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"
                f"🔍 <b>Dᴀᴛᴀʙᴀꜱᴇ Sᴇᴀʀᴄʜ Rᴇꜱᴜʟᴛ:</b> Uꜱᴇʀ ɴᴏᴛ ꜰᴏᴜɴᴅ\n"
                f"📊 <b>Status:</b> Nᴏ ᴜꜱᴇʀ ᴡɪᴛʜ ᴛʜɪꜱ ID ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ\n\n"
                f"⚠️ <i>Pʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ᴜꜱᴇʀ ID ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</i>",
                message.chat.id,
                checking_msg.message_id,
                parse_mode="HTML"
            )
            # Send back to admin panel
            bot.send_message(message.chat.id, "🔙 <b>Rᴇᴛᴜʀɴᴇᴅ ᴛᴏ Aᴅᴍɪɴ Pᴀɴᴇʟ</b>", parse_mode="HTML", reply_markup=admin_markup)
            return
        
        # User exists - show confirmation
        confirm_markup = InlineKeyboardMarkup()
        confirm_markup.row(
            InlineKeyboardButton("✅ Cᴏɴꜰɪʀᴍ Dᴇʟᴇᴛᴇ", callback_data=f"confirm_delete_{user_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")
        )
        
        # Get user data for confirmation
        user_data = getData(user_id) or {}
        username = f"@{user_data.get('username', 'N/A')}" if user_data.get('username') else "No Username"
        balance = user_data.get('balance', 0)
        orders_count = user_data.get('orders_count', 0)
        
        bot.edit_message_text(
            f"⚠️ <b>Cᴏɴꜰɪʀᴍ Uꜱᴇʀ Dᴇʟᴇᴛɪᴏɴ</b>\n\n"
            f"👤 <b>User Details:</b>\n"
            f"├ 🆔 ID: <code>{user_id}</code>\n"
            f"├ 📛 Username: {username}\n"
            f"├ 💰 Balance: {balance} coins\n"
            f"└ 📦 Orders: {orders_count}\n\n"
            f"🔴 <b>Tʜɪꜱ ᴀᴄᴛɪᴏɴ ᴡɪʟʟ:</b>\n"
            f"• Dᴇʟᴇᴛᴇ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀꜱᴇ\n"
            f"• Rᴇᴍᴏᴠᴇ ᴀʟʟ ᴜꜱᴇʀ ᴏʀᴅᴇʀꜱ\n"
            f"• Nᴏᴛɪꜰʏ ᴛʜᴇ ᴜꜱᴇʀ\n"
            f"• Cᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ!\n\n"
            f"Aʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛʜɪꜱ ᴜꜱᴇʀ?",
            message.chat.id,
            checking_msg.message_id,
            parse_mode="HTML",
            reply_markup=confirm_markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_") or call.data == "cancel_delete")
    def handle_delete_confirmation(call):
        if call.data == "cancel_delete":
            bot.answer_callback_query(call.id, "❌ Dᴇʟᴇᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ")
            
            bot.edit_message_text(
                "❌ <b>Dᴇʟᴇᴛɪᴏɴ Cᴀɴᴄᴇʟʟᴇᴅ</b>\n\n"
                "Uꜱᴇʀ ᴅᴇʟᴇᴛɪᴏɴ ʜᴀꜱ ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )
            # Send the admin panel markup
            bot.send_message(call.message.chat.id, "🔙 <b>Rᴇᴛᴜʀɴᴇᴅ ᴛᴏ Aᴅᴍɪɴ Pᴀɴᴇʟ</b>", parse_mode="HTML", reply_markup=admin_markup)
            return
            
        # Extract user ID from callback data
        user_id = call.data.replace("confirm_delete_", "")
        
        # Show deleting animation with progress bar
        for progress in [0, 25, 50, 75, 100]:
            progress_bar = '█' * (progress // 10) + '░' * (10 - progress // 10)
            bot.edit_message_text(
                f"🗑️ <b>Dᴇʟᴇᴛɪɴɢ Uꜱᴇʀ...</b>\n\n"
                f"🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"
                f"⏳ Rᴇᴍᴏᴠɪɴɢ ᴜꜱᴇʀ ᴅᴀᴛᴀ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀꜱᴇ...\n\n"
                f"[{progress_bar}] {progress}%",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )
            if progress < 100:
                time.sleep(0.5)
        
        # Perform deletion
        if delete_user(user_id):
            try:
                # Create support button for user notification
                support_markup = InlineKeyboardMarkup()
                support_markup.add(InlineKeyboardButton("📞 Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ", url=SUPPORT_BOT))
                
                bot.send_message(
                    user_id, 
                    "⚠️ <b>Aᴄᴄᴏᴜɴᴛ Dᴇʟᴇᴛɪᴏɴ Nᴏᴛɪᴄᴇ</b>\n\n"
                    "Yᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ ʙʏ ᴀᴅᴍɪɴ. Yᴏᴜ ᴄᴀɴ ɴᴏ ʟᴏɴɢᴇʀ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ.\n\n"
                    "Iꜰ ʏᴏᴜ ʙᴇʟɪᴇᴠᴇ ᴛʜɪꜱ ᴡᴀꜱ ᴀ ᴍɪꜱᴛᴀᴋᴇ ᴏʀ ʜᴀᴠᴇ ᴀɴʏ ǫᴜᴇꜱᴛɪᴏɴꜱ:",
                    parse_mode="HTML",
                    reply_markup=support_markup
                )
                notified = "Yes"
            except:
                notified = "No"
            
            # Success message with close button
            success_markup = InlineKeyboardMarkup()
            success_markup.add(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_delete_success"))
            
            bot.edit_message_text(
                f"✅ <b>Uꜱᴇʀ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ</b>\n\n"
                f"👤 <b>User Details:</b>\n"
                f"├ 🆔 ID: <code>{user_id}</code>\n"
                f"├ 🗑️ Status: Dᴀᴛᴀʙᴀꜱᴇ ᴇɴᴛʀʏ ʀᴇᴍᴏᴠᴇᴅ\n"
                f"├ 📊 Orders: Aʟʟ ᴏʀᴅᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ\n"
                f"└ 👤 Uꜱᴇʀ Nᴏᴛɪꜰɪᴇᴅ: {notified}\n\n"
                f"✨ <i>Uꜱᴇʀ ᴀᴄᴄᴏᴜɴᴛ ʜᴀꜱ ʙᴇᴇɴ ᴄᴏᴍᴘʟᴇᴛᴇʟʏ ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ꜱʏꜱᴛᴇᴍ.</i>",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=success_markup
            )
            bot.answer_callback_query(call.id, "✅ Uꜱᴇʀ ᴅᴇʟᴇᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ")
        else:
            bot.answer_callback_query(call.id, "❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴜꜱᴇʀ", show_alert=True)
            
            bot.edit_message_text(
                f"❌ <b>Dᴇʟᴇᴛɪᴏɴ Fᴀɪʟᴇᴅ</b>\n\n"
                f"🆔 <b>User ID:</b> <code>{user_id}</code>\n\n"
                f"Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀꜱᴇ.\n"
                f"Uꜱᴇʀ ᴍᴀʏ ɴᴏᴛ ᴇxɪꜱᴛ ᴏʀ ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀ ᴅᴀᴛᴀʙᴀꜱᴇ ᴇʀʀᴏʀ.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )
            # Send the admin panel markup
            bot.send_message(call.message.chat.id, "🔙 <b>Rᴇᴛᴜʀɴᴇᴅ ᴛᴏ Aᴅᴍɪɴ Pᴀɴᴇʟ</b>", parse_mode="HTML", reply_markup=admin_markup)

    @bot.callback_query_handler(func=lambda call: call.data == "close_delete_success")
    def handle_close_delete_success(call):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.answer_callback_query(call.id, "Mᴇꜱꜱᴀɢᴇ ᴄʟᴏꜱᴇᴅ")
        # Send back to admin panel
        bot.send_message(call.message.chat.id, "🔙 <b>Rᴇᴛᴜʀɴᴇᴅ ᴛᴏ Aᴅᴍɪɴ Pᴀɴᴇʟ</b>", parse_mode="HTML", reply_markup=admin_markup)

    bot.register_message_handler(handle_delete_user, func=lambda m: m.text == "🗑 Delete User")

# ======================= ADMIN PANEL ======================= #
def register_admin_handlers(bot, admin_markup, main_markup, admin_user_ids):
    @bot.message_handler(commands=['adminpanel'])
    def admin_panel(message):
        user_id = str(message.from_user.id)
        if user_id not in map(str, admin_user_ids):
            bot.reply_to(
                message,
                "🔒 *Rᴇꜱᴛʀɪᴄᴛᴇᴅ Aʀᴇᴀ*\n\n"
                "Tʜɪꜱ Pᴀɴᴇʟ ɪꜱ ꜰᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ Aᴅᴍɪɴɪꜱᴛʀᴀᴛᴏʀꜱ ᴏɴʟʏ\n\n"
                "⚠️ Yᴏᴜʀ ᴀᴄᴄᴇꜱꜱ ᴀᴛᴛᴇᴍᴘᴛ ʜᴀꜱ ʙᴇᴇɴ ʟᴏɢɢᴇᴅ",
                parse_mode="Markdown"
            )
            return
        
        bot.reply_to(
            message,
            "⚡ *SMM Bᴏᴏꜱᴛᴇʀ Aᴅᴍɪɴ Cᴇɴᴛᴇʀ*\n\n"
            "▸ Uꜱᴇʀ Mᴀɴᴀɢᴇᴍᴇɴᴛ\n"
            "▸ Cᴏɪɴ Tʀᴀɴꜱᴀᴄᴛɪᴏɴꜱ\n"
            "▸ Sʏꜱᴛᴇᴍ Cᴏɴᴛʀᴏʟꜱ\n\n"
            "Sᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ:",
            parse_mode="Markdown",
            reply_markup=admin_markup
        )

    # Register all admin handlers
    register_lock_handlers(bot, admin_markup, admin_user_ids)
    register_delete_user_handlers(bot, admin_markup)

    @bot.message_handler(func=lambda m: m.text == "🔙 Main Menu")
    def return_to_main(message):
        bot.reply_to(message, "Returning to main menu...", reply_markup=main_markup)
        
# ======================= BONUS CONFIGURATION ======================= #
def register_bonus_config_handlers(bot, admin_markup, admin_user_ids):
    bonus_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    bonus_markup.row(KeyboardButton("💰 Coins"), KeyboardButton("⏰ Time"))
    bonus_markup.row(KeyboardButton("🔄 Switch"))
    bonus_markup.row(KeyboardButton("🔙 Admin Panel"))

    @bot.message_handler(func=lambda m: m.text == "🪙 Bonus")
    def bonus_menu(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        bot.reply_to(message, "🎛 *Bᴏɴᴜꜱ Cᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ:*", parse_mode="Markdown", reply_markup=bonus_markup)

    @bot.message_handler(func=lambda m: m.text == "💰 Coins")
    def bonus_coins(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        bot.reply_to(message, "🔢 Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ɴᴇᴡ ʙᴏɴᴜꜱ ᴄᴏɪɴꜱ ᴀᴍᴏᴜɴᴛ:")
        bot.register_next_step_handler(message, process_bonus_coins)

    def process_bonus_coins(message):
        if message.text.lower() == "cancel":
            bot.reply_to(message, "❌ Oᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=bonus_markup)
            return
        try:
            amount = int(message.text)
            if amount < 0:
                raise ValueError
            set_bonus_amount(amount)
            bot.reply_to(message, f"✅ Bᴏɴᴜꜱ ᴄᴏɪɴꜱ ꜱᴇᴛ ᴛᴏ {amount}.", reply_markup=bonus_markup)
        except:
            bot.reply_to(message, "❌ Iɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ. Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴘᴏꜱɪᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ.", reply_markup=bonus_markup)


    @bot.message_handler(func=lambda m: m.text == "⏰ Time")
    def bonus_time(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        bot.reply_to(message, "🕑 Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ʙᴏɴᴜꜱ ɪɴᴛᴇʀᴠᴀʟ ɪɴ *ᴍɪɴᴜᴛᴇꜱ*:", parse_mode="Markdown")
        bot.register_next_step_handler(message, process_bonus_time)

    def process_bonus_time(message):
        if message.text.lower() == "cancel":
            bot.reply_to(message, "❌ Oᴘᴇʀᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=bonus_markup)
            return
        try:
            minutes = int(message.text)
            if minutes <= 0:
                raise ValueError
            set_bonus_interval(minutes * 60)
            bot.reply_to(message, f"✅ Bᴏɴᴜꜱ ɪɴᴛᴇʀᴠᴀʟ ꜱᴇᴛ ᴛᴏ {minutes} ᴍɪɴᴜᴛᴇꜱ.", reply_markup=bonus_markup)
        except:
            bot.reply_to(message, "❌ Iɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ. Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴘᴏꜱɪᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ.", reply_markup=bonus_markup)


    @bot.message_handler(func=lambda m: m.text == "🔄 Switch")
    def bonus_switch(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        status = toggle_bonus()
        bot.reply_to(message, f"🔄 Bᴏɴᴜꜱ ʙᴜᴛᴛᴏɴ ɪꜱ ɴᴏᴡ {'ᴇɴᴀʙʟᴇᴅ ✅' if status else 'ᴅɪꜱᴀʙʟᴇᴅ ❌'}.", reply_markup=bonus_markup)

    @bot.message_handler(func=lambda m: m.text == "🔙 Admin Panel")
    def return_to_admin_panel(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        bot.reply_to(message, "🔧 Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ Aᴅᴍɪɴ Pᴀɴᴇʟ...", reply_markup=admin_markup)

# ======================= TOP RICH USERS ======================= #
def register_top_rich_handler(bot, admin_user_ids):
    PAGE_SIZE = 10

    def build_rich_page(users, page=0):
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_users = users[start:end]

        inner_list = ""
        for i, user in enumerate(page_users, start + 1):
            username = f"@{user.get('username')}" if user.get('username') else f"ID:{user['user_id']}"
            balance = round(float(user.get('balance', 0)), 2)
            inner_list += f"{i}. {username} — <code>{balance}</code> ᴄᴏɪɴꜱ\n"

        quoted_content = f"<blockquote><b>{inner_list}</b></blockquote>"

        msg = f"🏆 <b>Top 10 Rɪᴄʜᴇꜱᴛ Uꜱᴇʀꜱ</b>\n\n{quoted_content}"

        # Pagination + Close
        markup = InlineKeyboardMarkup()
        nav_row = []

        if page > 0:
            nav_row.append(InlineKeyboardButton("⌫ Back", callback_data=f"rich_page_{page-1}"))
        if end < len(users):
            nav_row.append(InlineKeyboardButton("Next ⌦", callback_data=f"rich_page_{page+1}"))

        if nav_row:
            markup.row(*nav_row)

        markup.add(InlineKeyboardButton("⌧ Close ⌧", callback_data="close_rich"))

        return msg, markup

    def show_top_rich(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        users = get_top_balances()
        if not users:
            bot.reply_to(message, "Nᴏ ᴜꜱᴇʀ ᴅᴀᴛᴀ ꜰᴏᴜɴᴅ.")
            return

        text, reply_markup = build_rich_page(users, page=0)
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=reply_markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("rich_page_") or call.data == "close_rich")
    def handle_rich_pagination(call):
        if str(call.from_user.id) not in map(str, admin_user_ids):
            bot.answer_callback_query(call.id, text="Aᴄᴄᴇꜱꜱ Dᴇɴɪᴇᴅ", show_alert=True)
            return

        users = get_top_balances()
        if not users:
            bot.answer_callback_query(call.id)
            return

        if call.data == "close_rich":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.answer_callback_query(call.id)
            return

        try:
            page = int(call.data.split("_")[-1])
            text, reply_markup = build_rich_page(users, page)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            bot.answer_callback_query(call.id)
        except:
            bot.answer_callback_query(call.id, text="Eʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴘᴀɢᴇ")

    # Register button — EMOJI PRESERVED
    bot.register_message_handler(show_top_rich, func=lambda m: m.text == "💰 Top Rich")

# ======================= TOP AFFILIATES ======================= #
def register_top_affiliates_handler(bot, admin_user_ids):
    PAGE_SIZE = 10

    def build_affiliates_page(users, page=0):
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_users = users[start:end]

        inner_list = ""
        for i, user in enumerate(page_users, start + 1):
            username = f"@{user.get('username')}" if user.get('username') else f"ID:{user['user_id']}"
            earnings = round(float(user.get('affiliate_earnings', 0)), 2)
            inner_list += f"{i}. {username} — <code>{earnings}</code> ᴄᴏɪɴꜱ\n"

        quoted_content = f"<blockquote><b>{inner_list}</b></blockquote>"

        msg = f"👥 <b>Top 10 Aꜰꜰɪʟɪᴀᴛᴇꜱ</b>\n\n{quoted_content}"

        # Pagination + Close
        markup = InlineKeyboardMarkup()
        nav_row = []

        if page > 0:
            nav_row.append(InlineKeyboardButton("⌫ Bᴀᴄᴋ", callback_data=f"affiliates_page_{page-1}"))
        if end < len(users):
            nav_row.append(InlineKeyboardButton("Nᴇxᴛ ⌦", callback_data=f"affiliates_page_{page+1}"))

        if nav_row:
            markup.row(*nav_row)

        markup.add(InlineKeyboardButton("⌧ Cʟᴏꜱᴇ ⌧", callback_data="close_affiliates"))

        return msg, markup

    def show_top_affiliates(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        users = get_top_affiliate_earners()
        if not users:
            bot.reply_to(message, "Nᴏ Aꜰꜰɪʟɪᴀᴛᴇ Eᴀʀɴɪɴɢꜱ Dᴀᴛᴀ ᴏᴜɴᴅ.")
            return

        text, reply_markup = build_affiliates_page(users, page=0)
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=reply_markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("affiliates_page_") or call.data == "close_affiliates")
    def handle_affiliates_pagination(call):
        if str(call.from_user.id) not in map(str, admin_user_ids):
            bot.answer_callback_query(call.id, text="Aᴄᴄᴇꜱꜱ Dᴇɴɪᴇᴅ", show_alert=True)
            return

        users = get_top_affiliate_earners()
        if not users:
            bot.answer_callback_query(call.id)
            return

        if call.data == "close_affiliates":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.answer_callback_query(call.id)
            return

        try:
            page = int(call.data.split("_")[-1])
            text, reply_markup = build_affiliates_page(users, page)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            bot.answer_callback_query(call.id)
        except:
            bot.answer_callback_query(call.id, text="Eʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴘᴀɢᴇ")

    # Register button
    bot.register_message_handler(show_top_affiliates, func=lambda m: m.text == "👥 Top Affiliates")

# ======================= ANTI-FRAUD ======================= #
def register_anti_fraud_handler(bot, admin_user_ids):
    PAGE_SIZE = 10

    def build_fraud_page(suspects, page=0):
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_suspects = suspects[start:end]

        inner_list = ""
        for i, s in enumerate(page_suspects, start + 1):
            username = f"@{s['username']}" if s.get("username") else f"ID:{s['user_id']}"
            line = f"{i}. Uꜱᴇʀ: {username}"

            if "balance" in s:
                line += f" | 💰 {float(s['balance']):.2f}"
            if "bonus" in s:
                line += f" | 🎁 {float(s['bonus']):.2f}"
            if "deposits" in s:
                line += f" | 💳 {float(s['deposits']):.2f}"

            inner_list += line + "\n"

        quoted_content = f"<blockquote><b>{inner_list}</b></blockquote>"

        msg = f"<b>🛡️ Sᴜꜱᴘɪᴄɪᴏᴜꜱ Uꜱᴇʀꜱ Dᴇᴛᴇᴄᴛᴇᴅ:</b>\n\n{quoted_content}"

        # Buttons
        markup = InlineKeyboardMarkup()
        nav_row = []

        if page > 0:
            nav_row.append(InlineKeyboardButton("⌫ Bᴀᴄᴋ", callback_data=f"fraud_page_{page-1}"))
        if end < len(suspects):
            nav_row.append(InlineKeyboardButton("Nᴇxᴛ ⌦", callback_data=f"fraud_page_{page+1}"))

        if nav_row:
            markup.row(*nav_row)

        action_row = []
        action_row.append(InlineKeyboardButton("⥁ Cʟᴇᴀʀ Uꜱᴇʀꜱ ⥁", callback_data="clear_suspicious"))
        action_row.append(InlineKeyboardButton("⌧ Cʟᴏꜱᴇ ⌧", callback_data="close_fraud"))
        markup.row(*action_row)

        return msg, markup

    def show_anti_fraud(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        suspects = get_suspicious_users()

        if not suspects:
            bot.reply_to(message, "Nᴏ sᴜꜱᴘɪᴄɪᴏᴜꜱ uꜱᴇʀꜱ ꜰᴏᴜɴᴅ.")
            return

        text, reply_markup = build_fraud_page(suspects, page=0)
        bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=reply_markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("fraud_page_") or call.data in ["close_fraud", "clear_suspicious"])
    def handle_fraud_actions(call):
        if str(call.from_user.id) not in map(str, admin_user_ids):
            bot.answer_callback_query(call.id, text="Aᴄᴄᴇꜱꜱ Dᴇɴɪᴇᴅ", show_alert=True)
            return

        if call.data == "close_fraud":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.answer_callback_query(call.id)
            return

        if call.data == "clear_suspicious":
            # === MODIFIED CLEAR LOGIC: Only clear bonus coins, don't deduct from balance ===
            suspects = get_suspicious_users()
            cleared_count = 0

            for s in suspects:
                user_id = s['user_id']
                user = users_collection.find_one({"user_id": user_id})
                if user:
                    bonus = float(user.get("bonus_coins", 0))
                    if bonus > 0:
                        users_collection.update_one(
                            {"user_id": user_id},
                            {"$set": {"bonus_coins": 0}}
                        )
                        cleared_count += 1

            bot.answer_callback_query(call.id, text=f"Cʟᴇᴀʀᴇᴅ ʙᴏɴᴜꜱ ᴄᴏɪɴꜱ ꜰʀᴏᴍ {cleared_count} uꜱᴇʀꜱ!", show_alert=True)

            suspects = get_suspicious_users()
            if not suspects:
                try:
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="Nᴏ sᴜꜱᴘɪᴄɪᴏᴜꜱ uꜱᴇʀꜱ ꜰᴏᴜɴᴅ.",
                        parse_mode="HTML"
                    )
                except:
                    pass
                return

            text, reply_markup = build_fraud_page(suspects, page=0)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            return

        # Pagination
        try:
            page = int(call.data.split("_")[-1])
            suspects = get_suspicious_users()
            text, reply_markup = build_fraud_page(suspects, page)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            bot.answer_callback_query(call.id)
        except:
            bot.answer_callback_query(call.id, text="Eʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴘᴀɢᴇ")

    # EMOJI PRESERVED — NEVER TOUCHED
    bot.register_message_handler(show_anti_fraud, func=lambda m: m.text == "🛡️ Anti-Fraud")

# ======================= PANEL BALANCE ======================= #
def register_panel_balance_handler(bot, admin_user_ids, admin_markup=None, main_markup=None):
    def get_megahub_balance():
        """Fetch balance from Megahub API"""
        try:
            payload = {
                "key": MEGAHUB_PANEL_API,
                "action": "balance"
            }
            
            resp = requests.post(MEGAHUB_PANEL_API_URL, data=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            balance = data.get("balance")
            currency = data.get("currency", "USD")
            
            if balance is not None:
                return f"{balance} {currency}"
            else:
                logger.warning(f"Megahub balance missing in response: {data}")
                return "❌ Failed to fetch"
                
        except Exception as e:
            logger.error(f"Megahub API error: {e}")
            return "❌ API Error"

    def show_panel_balance(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        # Get balances from both APIs
        shakerg_balance = get_panel_balance()  # Your existing function
        megahub_balance = get_megahub_balance()

        from datetime import datetime
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        current_date = now.strftime("%Y-%m-%d")

        admin_id = message.from_user.id
        admin_username = f"@{message.from_user.username}" if message.from_user.username else "N/A"

        panel_text = (
            "<b>⍟──[ ᴘᴀɴᴇʟ ʙᴀʟᴀɴᴄᴇ ]──⍟</b>\n\n"
            "<blockquote>"
            "🆔 ᴀᴅᴍɪɴ Iᴅ: <code>{admin_id}</code>\n"
            "👤 Uꜱᴇʀɴᴀᴍᴇ: <code>{admin_username}</code>\n\n"
            "💵 <b>Sʜᴀᴋᴇʀɢ :</b> <code>{shakerg_balance}</code>\n"
            "💵 <b>Mᴇɢᴀʜᴜʙ :</b> <code>{megahub_balance}</code>\n\n"
            "⏰ Tɪᴍᴇ: <b>{current_time}</b>\n"
            "📅 Dᴀᴛᴇ: <b>{current_date}</b>"
            "</blockquote>\n\n"
            "⍟────────────────────⍟"
        ).format(
            admin_id=admin_id,
            admin_username=admin_username,
            shakerg_balance=shakerg_balance,
            megahub_balance=megahub_balance,
            current_time=current_time,
            current_date=current_date
        )

        close_button = InlineKeyboardMarkup()
        close_button.add(InlineKeyboardButton("⌧ Close ⌧", callback_data="close_panel_balance"))

        bot.send_message(
            chat_id=message.chat.id,
            text=panel_text,
            parse_mode="HTML",
            reply_markup=close_button
        )

    bot.register_message_handler(show_panel_balance, func=lambda m: m.text == "📟 Panel Balance")

    @bot.callback_query_handler(func=lambda call: call.data == "close_panel_balance")
    def close_panel_balance_callback(call):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.answer_callback_query(call.id)

# ======================= UPDATE USERS BUTTON ======================= #
def register_update_users_handler(bot, admin_user_ids, admin_markup=None, main_markup=None):
    def update_users_start(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("⟳ Start Update", callback_data="start_user_update"),
            InlineKeyboardButton("☒ Cancel ☒", callback_data="cancel_user_update")
        )
        
        bot.reply_to(message,
            "🔄 <b>Uᴘᴅᴀᴛᴇ Usᴇʀ Dᴀᴛᴀʙᴀꜱᴇ</b>\n\n"
            "Tʜɪꜱ ᴡɪʟʟ ᴄʜᴇᴄᴋ ᴀʟʟ ᴜꜱᴇʀꜱ ᴀɴᴅ ʀᴇᴍᴏᴠᴇ ᴛʜᴏꜱᴇ ᴡʜᴏ ʜᴀᴠᴇɴ'ᴛ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ ɴᴇᴡ ʙᴏᴛ.\n\n"
            "📊 <b>Current Users:</b> <code>{}</code>\n\n"
            "⚠️ <b>This action cannot be undone!</b>".format(len(get_all_users())),
            parse_mode="HTML",
            reply_markup=markup
        )

    def perform_user_cleanup(message):
        """Remove users who haven't started the new bot"""
        from functions import get_all_users, delete_user
        
        all_users = get_all_users()
        total_users = len(all_users)
        active_users = 0
        removed_users = 0
        
        progress_msg = bot.send_message(message.chat.id, 
            "🔄 <b>Uᴘᴅᴀᴛɪɴɢ Usᴇʀꜱ...</b>\n\n"
            "📊 Pʀᴏɢʀᴇꜱꜱ: <code>0%</code>\n"
            "✅ Aᴄᴛɪᴠᴇ: <code>0</code>\n"
            "🗑️ Rᴇᴍᴏᴠᴇᴅ: <code>0</code>\n"
            "👥 Tᴏᴛᴀʟ: <code>{}</code>".format(total_users),
            parse_mode="HTML"
        )
        
        for index, user_id in enumerate(all_users):
            try:
                # Try to send a hidden message to check if user exists
                bot.send_chat_action(user_id, 'typing')
                active_users += 1
            except:
                # User blocked/deleted bot - remove from database
                delete_user(user_id)
                removed_users += 1
            
            # Update progress every 10 users or at the end
            if (index + 1) % 10 == 0 or (index + 1) == total_users:
                progress = int((index + 1) / total_users * 100)
                progress_bar = '█' * (progress // 10) + '░' * (10 - progress // 10)
                
                bot.edit_message_text(
                    "🔄 <b>Uᴘᴅᴀᴛɪɴɢ Usᴇʀꜱ...</b>\n\n"
                    "📊 Pʀᴏɢʀᴇꜱꜱ: <code>{}%</code>\n"
                    "[{}]\n\n"
                    "✅ Aᴄᴛɪᴠᴇ: <code>{}</code>\n"
                    "🗑️ Rᴇᴍᴏᴠᴇᴅ: <code>{}</code>\n"
                    "👥 Tᴏᴛᴀʟ: <code>{}</code>".format(progress, progress_bar, active_users, removed_users, total_users),
                    message.chat.id,
                    progress_msg.message_id,
                    parse_mode="HTML"
                )
        
        # Final result
        bot.edit_message_text(
            "✅ <b>Uᴘᴅᴀᴛᴇ Cᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"
            "📊 <b>Fɪɴᴀʟ Rᴇꜱᴜʟᴛꜱ:</b>\n"
            "├ ✅ Aᴄᴛɪᴠᴇ Usᴇʀꜱ: <code>{}</code>\n"
            "├ 🗑️ Rᴇᴍᴏᴠᴇᴅ Usᴇʀꜱ: <code>{}</code>\n"
            "└ 📈 Sᴜᴄᴄᴇꜱꜱ Rᴀᴛᴇ: <code>{}%</code>\n\n"
            "✨ <b>Dᴀᴛᴀʙᴀꜱᴇ ɪꜱ ɴᴏᴡ ᴜᴘ ᴛᴏ ᴅᴀᴛᴇ!</b>".format(
                active_users, 
                removed_users, 
                int(active_users / total_users * 100) if total_users > 0 else 0
            ),
            message.chat.id,
            progress_msg.message_id,
            parse_mode="HTML"
        )

    @bot.callback_query_handler(func=lambda call: call.data in ["start_user_update", "cancel_user_update"])
    def handle_user_update(call):
        if call.data == "cancel_user_update":
            bot.answer_callback_query(call.id, "Update cancelled")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            return
        
        # Start the update process
        bot.answer_callback_query(call.id, "Starting user update...")
        perform_user_cleanup(call.message)

    bot.register_message_handler(update_users_start, func=lambda m: m.text == "🔄 Update Users")

# ======================= REGISTER ALL ADMIN FEATURES ======================= #
def register_admin_features(bot, admin_markup, main_markup, admin_user_ids_list):
    global admin_user_ids
    admin_user_ids = admin_user_ids_list

#========================= Register Admin Handlers =========================#
    # Pass admin_user_ids to register_admin_handlers
    register_admin_handlers(bot, admin_markup, main_markup, admin_user_ids)
    # Register Top Affiliates handler
    register_top_affiliates_handler(bot, admin_user_ids)
    # Register Top Rich handler
    register_top_rich_handler(bot, admin_user_ids)
    # Register Lock/Unlock handlers
    register_lock_handlers(bot, admin_markup, admin_user_ids)
    # Register Bonus Configuration handlers
    register_bonus_config_handlers(bot, admin_markup, admin_user_ids)
    # Register Delete User handler
    register_delete_user_handlers(bot, admin_markup)
    # Register Anti-Fraud handler
    register_anti_fraud_handler(bot, admin_user_ids)
    # Register Panel Balance handler
    register_panel_balance_handler(bot, admin_user_ids)
    # Register other handlers as needed
    register_anti_fraud_handler(bot, admin_user_ids)
    # Register Update Users handler
    register_update_users_handler(bot, admin_user_ids)
    # Register other handlers as needed
