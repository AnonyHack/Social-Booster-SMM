# adpanel.py
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from functions import (get_all_users,
    delete_user, lock_service, unlock_service, get_locked_services,
    set_bonus_amount, set_bonus_interval, toggle_bonus, get_top_balances,
    get_top_affiliate_earners, get_suspicious_users, get_panel_balance
)
import time

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

        bot.reply_to(message, "📝 Please send the *Service ID* you want to lock:", parse_mode="Markdown")
        bot.register_next_step_handler(message, process_lock_service)

    def process_lock_service(message):
        if message.text.lower() == 'cancel':
            bot.reply_to(message, "❌ Operation cancelled.", reply_markup=admin_markup)
            return

        service_id = message.text.strip()
        if lock_service(service_id):
            bot.reply_to(
                message,
                f"✅ *Service {service_id} has been locked for regular users.*\n"
                f"Do you want to notify users? *(yes/no)*",
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(message, lambda m: process_notify_lock(m, service_id))
        else:
            bot.reply_to(message, f"❌ Failed to lock service `{service_id}`.", parse_mode="Markdown", reply_markup=admin_markup)

    def process_notify_lock(message, service_id):
        choice = message.text.lower()
        if choice == 'yes':
            notify_users_about_service(service_id, action="lock")
            bot.reply_to(message, "📢 Notification sent to users.", reply_markup=admin_markup)
        else:
            bot.reply_to(message, "👍 No notifications were sent.", reply_markup=admin_markup)

    def handle_unlock_service(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        bot.reply_to(message, "📝 Please send the *Service ID* you want to unlock:", parse_mode="Markdown")
        bot.register_next_step_handler(message, process_unlock_service)

    def process_unlock_service(message):
        if message.text.lower() == 'cancel':
            bot.reply_to(message, "❌ Operation cancelled.", reply_markup=admin_markup)
            return

        service_id = message.text.strip()
        if unlock_service(service_id):
            bot.reply_to(
                message,
                f"✅ *Service {service_id} has been unlocked for all users.*\n"
                f"Do you want to notify users? *(yes/no)*",
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(message, lambda m: process_notify_unlock(m, service_id))
        else:
            bot.reply_to(message, f"❌ Failed to unlock service `{service_id}`.", parse_mode="Markdown", reply_markup=admin_markup)

    def process_notify_unlock(message, service_id):
        choice = message.text.lower()
        if choice == 'yes':
            notify_users_about_service(service_id, action="unlock")
            bot.reply_to(message, "📢 Notification sent to users.", reply_markup=admin_markup)
        else:
            bot.reply_to(message, "👍 No notifications were sent.", reply_markup=admin_markup)

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
            bot.reply_to(message, "🔓 No services are currently locked.", reply_markup=admin_markup)
            return

        services_list = "\n".join([f"• `{service_id}`" for service_id in locked_services])
        bot.reply_to(message, f"🔒 *Locked Services:*\n{services_list}", parse_mode="Markdown", reply_markup=admin_markup)

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
            
        bot.reply_to(message, "🗑 Please send the user ID you want to delete:")
        bot.register_next_step_handler(message, process_delete_user)

    def process_delete_user(message):
        if message.text.lower() == 'cancel':
            bot.reply_to(message, "❌ Operation cancelled.", reply_markup=admin_markup)
            return
            
        user_id = message.text.strip()
        if delete_user(user_id):
            try:
                bot.send_message(user_id, "⚠️ Your account has been deleted by admin. You can no longer use this bot.")
            except:
                pass
            bot.reply_to(message, f"✅ User {user_id} has been deleted from the database.", reply_markup=admin_markup)
        else:
            bot.reply_to(message, f"❌ Failed to delete user {user_id}.", reply_markup=admin_markup)

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

def register_bonus_config_handlers(bot, admin_markup, admin_user_ids):
    bonus_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    bonus_markup.row(KeyboardButton("💰 Coins"), KeyboardButton("⏰ Time"))
    bonus_markup.row(KeyboardButton("🔄 Switch"))
    bonus_markup.row(KeyboardButton("🔙 Admin Panel"))

    @bot.message_handler(func=lambda m: m.text == "🪙 Bonus")
    def bonus_menu(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        bot.reply_to(message, "🎛 *Bonus Configuration:*", parse_mode="Markdown", reply_markup=bonus_markup)

    @bot.message_handler(func=lambda m: m.text == "💰 Coins")
    def bonus_coins(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        bot.reply_to(message, "🔢 Please enter the new bonus coins amount:")
        bot.register_next_step_handler(message, process_bonus_coins)

    def process_bonus_coins(message):
        if message.text.lower() == "cancel":
            bot.reply_to(message, "❌ Operation cancelled.", reply_markup=bonus_markup)
            return
        try:
            amount = int(message.text)
            if amount < 0:
                raise ValueError
            set_bonus_amount(amount)
            bot.reply_to(message, f"✅ Bonus coins set to {amount}.", reply_markup=bonus_markup)
        except:
            bot.reply_to(message, "❌ Invalid input. Please enter a valid positive integer.", reply_markup=bonus_markup)


    @bot.message_handler(func=lambda m: m.text == "⏰ Time")
    def bonus_time(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        bot.reply_to(message, "🕑 Please enter the bonus interval in *minutes*:", parse_mode="Markdown")
        bot.register_next_step_handler(message, process_bonus_time)

    def process_bonus_time(message):
        if message.text.lower() == "cancel":
            bot.reply_to(message, "❌ Operation cancelled.", reply_markup=bonus_markup)
            return
        try:
            minutes = int(message.text)
            if minutes <= 0:
                raise ValueError
            set_bonus_interval(minutes * 60)
            bot.reply_to(message, f"✅ Bonus interval set to {minutes} minutes.", reply_markup=bonus_markup)
        except:
            bot.reply_to(message, "❌ Invalid input. Please enter a valid positive integer.", reply_markup=bonus_markup)


    @bot.message_handler(func=lambda m: m.text == "🔄 Switch")
    def bonus_switch(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        status = toggle_bonus()
        bot.reply_to(message, f"🔄 Bonus button is now {'enabled ✅' if status else 'disabled ❌'}.", reply_markup=bonus_markup)

    @bot.message_handler(func=lambda m: m.text == "🔙 Admin Panel")
    def return_to_admin_panel(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return
        bot.reply_to(message, "🔧 Returning to Admin Panel...", reply_markup=admin_markup)

# ======================= TOP RICH USERS ======================= #
def register_top_rich_handler(bot, admin_user_ids):
    def handle_top_rich(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        users = get_top_balances()
        if not users:
            bot.reply_to(message, "❌ No user data found.")
            return

        msg = "🏆 <b>Top 10 Richest Users</b>\n\n"
        for i, user in enumerate(users, 1):
            username = f"@{user.get('username')}" if user.get('username') else f"ID:{user['user_id']}"
            balance = round(float(user.get('balance', 0)), 2)
            msg += f"{i}. {username} — <code>{balance}</code> coins\n"

        bot.send_message(message.chat.id, msg, parse_mode="HTML")

    bot.register_message_handler(handle_top_rich, func=lambda m: m.text == "💰 Top Rich")

def register_top_affiliates_handler(bot, admin_user_ids):
    def handle_top_affiliates(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        users = get_top_affiliate_earners()
        if not users:
            bot.reply_to(message, "❌ No affiliate earnings data found.")
            return

        msg = "👥 <b>Top 10 Affiliates</b>\n\n"
        for i, user in enumerate(users, 1):
            username = f"@{user.get('username')}" if user.get('username') else f"ID:{user['user_id']}"
            earnings = round(float(user.get('affiliate_earnings', 0)), 2)
            msg += f"{i}. {username} — <code>{earnings}</code> coins\n"

        bot.send_message(message.chat.id, msg, parse_mode="HTML")

    bot.register_message_handler(handle_top_affiliates, func=lambda m: m.text == "👥 Top Affiliates")

def register_anti_fraud_handler(bot, admin_user_ids):
    def handle_anti_fraud(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        suspects = get_suspicious_users()

        if not suspects:
            bot.reply_to(message, "✅ No suspicious users found.")
            return

        msg = "<b>🛡️ Suspicious Users Detected:</b>\n\n"
        for s in suspects[:20]:  # Show up to 20
            username = f"@{s['username']}" if s.get("username") else f"ID:{s['user_id']}"
            line = f"{s['type']} — {username}"

            if "balance" in s:
                line += f" | 💰 {float(s['balance']):.2f}"

            if "bonus" in s:
                line += f" | 🎁 {float(s['bonus']):.2f}"

            if "deposits" in s:
                line += f" | 💳 {float(s['deposits']):.2f}"

            msg += line + "\n"

        bot.send_message(message.chat.id, msg, parse_mode="HTML")

    bot.register_message_handler(handle_anti_fraud, func=lambda m: m.text == "🛡️ Anti-Fraud")


# ======================= PANEL BALANCE ======================= #
def register_panel_balance_handler(bot, admin_user_ids):
    def show_panel_balance(message):
        if str(message.from_user.id) not in map(str, admin_user_ids):
            return

        balance = get_panel_balance()

        if balance:
            bot.reply_to(message,
                f"📟 Yᴏᴜʀ Pᴀɴᴇʟ Bᴀʟᴀɴᴄᴇ:\n\n💰 <b>{balance}</b>",
                parse_mode="HTML"
            )
        else:
            bot.reply_to(message, "❌ Fᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ʙᴀʟᴀɴᴄᴇ. Cʜᴇᴄᴋ ᴀᴘɪ ᴋᴇʏ / ᴜʀʟ.")

    bot.register_message_handler(show_panel_balance, func=lambda m: m.text == "📟 Panel Balance")
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
    # Register other handlers as needed
