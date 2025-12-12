import telebot
import re
import requests
import time
import os
import traceback
import logging
import psutil
import threading
from threading import Thread
import datetime
from datetime import datetime
import pytz
from functools import wraps
from flask import Flask, jsonify
from dotenv import load_dotenv
import logging
from telebot import types
from logging.handlers import RotatingFileHandler
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from telebot.types import ForceReply, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from functions import (insertUser, track_exists, addBalance, cutBalance, getData,
                       addRefCount, isExists, setWelcomeStaus, setReferredStatus, updateUser, 
                       ban_user, unban_user, get_all_users, is_banned, get_banned_users, 
                       get_top_users, get_user_count, get_active_users, get_total_orders, 
                       get_total_deposits, get_top_referrer, get_user_orders_stats, get_new_users,
                       get_completed_orders, get_all_users, save_pinned_message, get_all_pinned_messages,
                         clear_all_pinned_messages, orders_collection, get_confirmed_spent, get_pending_spent, 
                         get_affiliate_earnings, add_affiliate_earning, get_affiliate_users, 
                         update_affiliate_earning, get_user_deposits, get_locked_services,
                           addBonusBalance, removeOldBonus, get_bonus_amount, get_bonus_interval,
                           is_bonus_enabled, setup_close_handler, update_order_statuses, status_updater,
                           get_free_orders_cost, get_deleted_users_count, get_free_orders_count, get_total_referrals,
                           get_premium_orders_count, get_premium_orders_cost, send_affiliate_notification, setup_affiliate_handlers)
from startup_notifier import send_startup_message # Import your functions from functions.py
 
# Load environment variables from .env file
load_dotenv()
from config import (SUPPORT_CHAT, UPDATES_CHANNEL_LINK, WELCOME_IMAGE_URL, 
                    REQUIRED_CHANNELS, CHANNEL_BUTTONS, WHATSAPP_CHANNEL, PAYMENT_CHANNEL,
                    MAINTENANCE_AUTO_DISABLE_TIME)
 
# =============== Bot Configuration =============== #
from config import BOT_TOKEN, SMM_PANEL_API, SMM_PANEL_API_URL, MEGAHUB_PANEL_API, MEGAHUB_PANEL_API_URL, FREE_ORDERS_DAILY_LIMIT, ADMIN_USER_IDS, WELCOME_BONUS, REF_BONUS

admin_user_ids = ADMIN_USER_IDS
SmmPanelApiUrl = SMM_PANEL_API_URL
SmmPanelApi = SMM_PANEL_API
MegahubPanelApiUrl = MEGAHUB_PANEL_API_URL
MegahubPanelApi = MEGAHUB_PANEL_API

# After creating your bot instance
bot = telebot.TeleBot(BOT_TOKEN)

# Setup affiliate handlers
setup_affiliate_handlers(bot)

# Welcome and referral bonuses
welcome_bonus = WELCOME_BONUS
ref_bonus = REF_BONUS

# Setup the universal close handler for inline buttons
setup_close_handler(bot)

# Send startup message when bot starts
send_startup_message(bot, is_restart=True)  # or False if you want default

#======================= Keyboards =======================#
# Main keyboard markup
main_markup = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton("🆓 Free Services") 
button2 = KeyboardButton("🛒 Buy Services")
button3 = KeyboardButton("👤 My Account")
button4 = KeyboardButton("💳 Pricing")
button5 = KeyboardButton("📊 Order Stats")
button6 = KeyboardButton("💰 Refer&Earn")
button7 = KeyboardButton("🏆 Leaderboard")  # New Affiliate button
button8 = KeyboardButton("📜 Help")
button9 = KeyboardButton("🎉 Bᴏɴᴜs")

main_markup.add(button1, button2)
main_markup.add(button3, button4)
main_markup.add(button5, button6)
main_markup.add(button7, button8)
main_markup.add(button9)

# Admin keyboard markup
admin_markup = ReplyKeyboardMarkup(resize_keyboard=True)
admin_markup.row("➕ Add", "➖ Remove")
admin_markup.row("📌 Pin Message", "📍 Unpin")
admin_markup.row("🔒 Ban User", "✅ Unban User")
admin_markup.row("📋 List Banned", "👤 User Info")
admin_markup.row("🖥 Server Status", "📤 Export Data")
admin_markup.row("📦 Order Manager", "📊 Analytics")
admin_markup.row("🔧 Maintenance", "📤 Broadcast")
admin_markup.row("🚮 Broadcast Delete", "🔐 Lock/Unlock")  # Added Delete Broadcast here
admin_markup.row("📦 Batch Coins", "🪙 Bonus")
admin_markup.row("🗑 Delete User", "💰 Top Rich")
admin_markup.row("👥 Top Affiliates", "🛡️ Anti-Fraud")
admin_markup.row("📟 Panel Balance", "🔄 Update Users")
admin_markup.row("⌫ ᴍᴀɪɴ ᴍᴇɴᴜ")

#======================= Send Orders main menu =======================#
send_orders_markup = ReplyKeyboardMarkup(resize_keyboard=True)
send_orders_markup.row(
    KeyboardButton("📱 Order Telegram"),
    KeyboardButton("🎵 Order TikTok"),
)

send_orders_markup.row(
    KeyboardButton("📸 Order Instagram"),
    KeyboardButton("▶️ Order YouTube"),
)

send_orders_markup.row(
    KeyboardButton("📘 Order Facebook"),
    KeyboardButton("💬 Order WhatsApp")
)

send_orders_markup.row(
    KeyboardButton("🐦 Order Twitter/X"),
    KeyboardButton("📛 Order Pinterest")
)

send_orders_markup.row(
    KeyboardButton("👻 Order Snapchat"),
    KeyboardButton("🎶 Order Spotify")
)

send_orders_markup.add(KeyboardButton("⌫ ᴍᴀɪɴ ᴍᴇɴᴜ"))

# === Import and register order handlers ===
from orders import register_order_handlers
register_order_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL)

# === Import and register free services handlers ===
from free_services import register_free_handlers
register_free_handlers(bot, send_orders_markup, main_markup, PAYMENT_CHANNEL)

# In bot.py (near other imports)
from adpanel import register_admin_features

# Then where you register handlers (after the admin_markup is defined)
register_admin_features(bot, admin_markup, main_markup, admin_user_ids)

# Telegram services menu
telegram_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
telegram_services_markup.row(
    KeyboardButton("👀 Post Views"),
    KeyboardButton("👀 Story Views")
)
telegram_services_markup.row(
    KeyboardButton("❤️ Cheap Reactions"),
    KeyboardButton("❤️ Premium Reactions"),
)
telegram_services_markup.row(
    KeyboardButton("👥 Channel Members"),
    KeyboardButton("👥 Premium Members")
)
telegram_services_markup.row(
    KeyboardButton("👥 Cheap Members"),
    KeyboardButton("👥 Bot Members")
)
telegram_services_markup.row(
    KeyboardButton("🔄 Post Shares"),
    KeyboardButton("💬 Post Comments")
)
telegram_services_markup.row(
    KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ")
)

# TikTok services menu (placeholder for now)
tiktok_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
tiktok_services_markup.row(
    KeyboardButton("👀 Tiktok Views"),
    KeyboardButton("👁️‍🗨️ Stream Views")
)
tiktok_services_markup.row(
    KeyboardButton("💗 HQ Likes"),
    KeyboardButton("💗 Cheap Likes")
)
tiktok_services_markup.row(
    KeyboardButton("💕 Stream Likes"),
    KeyboardButton("💕 Story Likes")
)
tiktok_services_markup.row(
    KeyboardButton("👥 Cheap Followers"),
    KeyboardButton("👥 Real Followers")
)
tiktok_services_markup.row(
    KeyboardButton("💬 Video Comments"),
    KeyboardButton("💬 Stream Comments")
)
tiktok_services_markup.row(
    KeyboardButton("🔄 Video Shares"),
    KeyboardButton("🔄 Stream Shares")
)
tiktok_services_markup.row(
    KeyboardButton("💾 Add Favorites"),
    KeyboardButton("⚔️ PKBattle Points")
)
tiktok_services_markup.row(
    KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ")
)

# Instagram services menu
instagram_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
instagram_services_markup.row(
    KeyboardButton("🎥 Reel Views"),
    KeyboardButton("👁️‍🗨️ Story Views")
)
instagram_services_markup.row(
    KeyboardButton("👁️‍🗨️ Photo Views"),
    KeyboardButton("👁️‍🗨️ Live Views")
)
instagram_services_markup.row(
    KeyboardButton("💓 Real Likes"),
    KeyboardButton("💓 Cheap Likes")
)
instagram_services_markup.row(
    KeyboardButton("👥 Real Followerss"),
    KeyboardButton("👥 Cheap Followerss")
)
instagram_services_markup.row(
    KeyboardButton("🗨️ Real Comments"),
    KeyboardButton("🗨️ Random Comments")
)
instagram_services_markup.row(
    KeyboardButton("🪪 Profile Visits"),
    KeyboardButton("👥 Channel Memberss")
    
)
instagram_services_markup.row(
    KeyboardButton("🔄 Insta Shares"),
    KeyboardButton("🔂 Insta Reposts")
    
)
instagram_services_markup.row(
    KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ")
)

# YouTube services menu
youtube_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
youtube_services_markup.row(
    KeyboardButton("▶️ YT Views"),
    KeyboardButton("👍 YT Likes")
)
youtube_services_markup.row(
    KeyboardButton("👥 YT Subscribers"),
)
youtube_services_markup.row(
    KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ")
)

# Facebook services menu
facebook_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
facebook_services_markup.row(
    KeyboardButton("👤 Profile Followers"),
    KeyboardButton("📄 Page Followers")
)
facebook_services_markup.row(
    KeyboardButton("🎥 Video/Reel Views"),
    KeyboardButton("❤️ Post Likes")
)
facebook_services_markup.add(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

# WhatsApp services menu
whatsapp_services_markup = ReplyKeyboardMarkup(resize_keyboard=True)
whatsapp_services_markup.row(
    KeyboardButton("👥 Channel Subscribers"),
)
whatsapp_services_markup.row(
    KeyboardButton("😀 Post EmojiReaction")
)
whatsapp_services_markup.add(KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ"))

############################ END OF NEW FEATURES #############################

#==================================== MongoDB Integration =======================#
# Replace the existing add_order function in bot.py with this:
def add_order(user_id, order_data):
    """Add a new order to user's history using MongoDB"""
    try:
        # Ensure the order_data has required fields
        order_data['user_id'] = str(user_id)
        if 'timestamp' not in order_data:
            order_data['timestamp'] = time.time()
        if 'status' not in order_data:
            order_data['status'] = 'pending'
        
        # Add to MongoDB
        from functions import add_order as mongo_add_order
        return mongo_add_order(user_id, order_data)
    except Exception as e:
        print(f"Error adding order to MongoDB: {e}")
        return False

#================================== Force Join Method =======================================#
required_channels = REQUIRED_CHANNELS  # Channel usernames from config
channel_buttons = CHANNEL_BUTTONS  # Button names and URLs from config

def is_user_member(user_id):
    """Check if a user is a member of all required channels."""
    for channel in required_channels:
        try:
            # Remove @ if present and any URL parts
            channel_username = channel.replace('https://t.me/', '').replace('@', '')
            chat_member = bot.get_chat_member(chat_id=f"@{channel_username}", user_id=user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            print(f"Error checking channel membership for {channel}: {e}")
            # If there's an error checking, assume user is not member
            return False
    return True

def check_membership_and_prompt(user_id, message):
    """Check if the user is a member of all required channels and prompt them to join if not."""
    if not is_user_member(user_id):
        # First, check if this is a callback query or regular message
        if hasattr(message, 'message_id'):
            chat_id = message.chat.id
            reply_to_message_id = message.message_id
        else:
            chat_id = message.chat.id
            reply_to_message_id = None
        
        # Create buttons for all channels in CHANNEL_BUTTONS (including WhatsApp)
        buttons = []
        
        # Add all channels from CHANNEL_BUTTONS config
        for channel_key, channel_info in channel_buttons.items():
            buttons.append([InlineKeyboardButton(channel_info['name'], url=channel_info['url'])])
        
        # Add action buttons
        buttons.append([InlineKeyboardButton("✨ ✅ VERIFY MEMBERSHIP", callback_data="verify_membership")])
        buttons.append([InlineKeyboardButton("❓ Why Join These Channels?", callback_data="why_join_info")])
        
        # Send the join message
        bot.send_message(
            chat_id=chat_id,
            reply_to_message_id=reply_to_message_id,
            text="""
<blockquote>
*🚀 Wᴇʟᴄᴏᴍᴇ Tᴏ Sᴍᴍʜᴜʙ Bᴏᴏꜱᴛᴇʀ Bᴏᴛ ! 🚀*

🚨 *Tᴏ Uꜱᴇ Tʜɪꜱ Bᴏᴛ, Yᴏᴜ Mᴜꜱᴛ Jᴏɪɴ Tʜᴇ RᴇQᴜɪʀᴇᴅ Cʜᴀɴɴᴇʟꜱ Fɪʀꜱᴛ!* 🚨

📊 *Cᴏᴍᴘʟᴇᴛᴇ Tʜᴇꜱᴇ Sᴛᴇᴘꜱ Tᴏ Uɴʟᴏᴄᴋ:*
▫️ Jᴏɪɴ Aʟʟ Cʜᴀɴɴᴇʟꜱ Bᴇʟᴏᴡ
▫️ Cʟɪᴄᴋ *'✅ VERIFY MEMBERSHIP'* Bᴜᴛᴛᴏɴ
▫️ Wᴀɪᴛ Fᴏʀ Vᴇʀɪғɪᴄᴀᴛɪᴏɴ


🔐 *Vᴇʀɪғɪᴄᴀᴛɪᴏɴ Sᴛᴀᴛᴜꜱ:* 𝘕𝘰𝘵 𝘝𝘦𝘳𝘪𝘧𝘪𝘦𝘥
⍟────────────────────⍟
</blockquote>""",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return False
    return True

@bot.callback_query_handler(func=lambda call: call.data == "why_join_info")
def handle_why_join(call):
    """Send the privileges info when user clicks 'Why Join?' button"""
    perks_text = """
<blockquote>
🛡️ *𝙋𝙧𝙞𝙫𝙞𝙡𝙚𝙜𝙚𝙨 𝙮𝙤𝙪'𝙡𝙡 𝙜𝙚𝙩:*
✓ Fᴜʟʟ Bᴏᴛ Aᴄᴄᴇꜱꜱ  
✓ Exᴄʟᴜꜱɪᴠᴇ Oғғᴇʀꜱ  
✓ Pʀᴇᴍɪᴜᴍ Sᴜᴘᴘᴏʀᴛ  
✓ Rᴇɢᴜʟᴀʀ Uᴘᴅᴀᴛᴇꜱ
⍟──────────────────⍟
</blockquote>
"""
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, perks_text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "verify_membership")
def verify_membership(call):
    user_id = call.from_user.id
    
    if is_user_member(user_id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
            # Create a mock message with referral data to preserve referral info
            class MockMessage:
                def __init__(self, call, user_id):
                    self.from_user = call.from_user
                    self.chat = call.message.chat
                    self.message_id = call.message.message_id
                    self.text = f"/start {call.message.text.split()[-1] if len(call.message.text.split()) > 1 else ''}"
                    self._json = call.message.json
            
            # Create mock message with preserved referral data
            mock_message = MockMessage(call, user_id)
            send_welcome(mock_message)
            
        except Exception as e:
            print(f"Error in verify_membership: {e}")
            bot.answer_callback_query(
                call.id,
                text="✅ Hᴇʏ! Yᴏᴜ ᴀʀᴇ ᴠᴇʀɪꜰɪᴇᴅ! Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ. Cʟɪᴄᴋ /start ᴀɢᴀɪɴ.",
                show_alert=True
            )
    else:
        bot.answer_callback_query(
            call.id,
            text="❌ Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴛʜᴇ ʀᴇQᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟꜱ ʏᴇᴛ!",
            show_alert=True
        )
#==============================================#

#========================= utility function to check bans =================#
# Enhanced check_ban decorator to include maintenance check
def check_ban(func):
    @wraps(func)
    def wrapped(message, *args, **kwargs):
        user_id = str(message.from_user.id)
        
        # Check maintenance mode
        if maintenance_mode and user_id not in map(str, admin_user_ids):
            bot.reply_to(message, maintenance_message)
            return
            
        # Check ban status
        if is_banned(user_id):
            bot.reply_to(message, "⛔ ❝Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ❞.")
            return
            
        return func(message, *args, **kwargs)
    return wrapped

#================== Send Orders Button ============================#
@bot.message_handler(func=lambda message: message.text == "🛒 Buy Services")
@check_ban
def send_orders_menu(message):
    user_id = message.from_user.id

    # Update last activity and username
    data = getData(user_id)
    data['last_activity'] = time.time()
    data['username'] = message.from_user.username
    updateUser(user_id, data)

    # Check if the user has joined all required channels
    if not check_membership_and_prompt(user_id, message):
        return  # Stop execution until the user joins
    
    # If the user is a member, show the Send Orders menu
    """Handle the main Send Orders menu"""
    bot.reply_to(message, "📤 Sᴇʟᴇᴄᴛ Pʟᴀᴛꜰᴏʀᴍ Tᴏ Sᴇɴᴅ Oʀᴅᴇʀꜱ:", reply_markup=send_orders_markup)


def set_bot_commands():
    commands = [
        BotCommand('start', '⟳ Restart the bot'),
        BotCommand('policy', '📋 View usage policy'),
    ]
    
    # Admin-only commands
    admin_commands = [
        BotCommand('adminpanel', 'Access admin controls'),
    ]
    
    try:
        # Set basic commands for all users
        bot.set_my_commands(commands)
        
        # Set admin commands specifically for admin users
        for admin_id in admin_user_ids:
            try:
                bot.set_chat_menu_button(
                    chat_id=admin_id,
                    menu_button=types.MenuButtonCommands()
                )
                bot.set_my_commands(admin_commands + commands, scope=types.BotCommandScopeChat(admin_id))
            except Exception as e:
                print(f"Error setting admin commands for {admin_id}: {e}")
        
        print("Bot commands set successfully")
    except Exception as e:
        print(f"Error setting bot commands: {e}")
  
#======================= Start Command =======================#
@bot.message_handler(commands=['start'])
@check_ban
def send_welcome(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

    ref_by = None
    is_affiliate = False

    # Parse referral parameter FIRST - before force join check
    if len(message.text.split()) > 1:
        ref_param = message.text.split()[1]
        if ref_param.startswith('aff_'):
            ref_by = ref_param.replace('aff_', '')
            is_affiliate = True
        elif ref_param.isdigit():
            ref_by = ref_param
            is_affiliate = False

    # Store referral data in user session before force join check
    if ref_by and int(ref_by) != int(user_id) and track_exists(ref_by):
        if not isExists(user_id):
            initial_data = {
                "user_id": user_id,
                "balance": "0.00",
                "ref_by": ref_by,
                "is_affiliate": is_affiliate,
                "referred": 0,
                "welcome_bonus": 0,
                "total_refs": 0,
            }
            insertUser(user_id, initial_data)
            addRefCount(ref_by)

    # Check channel membership AFTER storing referral data
    if not check_membership_and_prompt(user_id, message):
        return

    # If new user and not referred (but passed force join)
    if not isExists(user_id):
        initial_data = {
            "user_id": user_id,
                "balance": "0.00",
                "ref_by": ref_by if ref_by and int(ref_by) != int(user_id) and track_exists(ref_by) else "none",
                "is_affiliate": is_affiliate if ref_by and ref_by.startswith('aff_') else False,
                "referred": 0,
                "welcome_bonus": 0,
                "total_refs": 0,
        }
        insertUser(user_id, initial_data)

    # Welcome bonus logic
    userData = getData(user_id)
    if userData.get('welcome_bonus', 0) == 0:
        addBalance(user_id, welcome_bonus)
        setWelcomeStaus(user_id)

    # Referral bonus logic - NOW THIS WILL WORK AFTER VERIFICATION
    data = getData(user_id)
    if data['ref_by'] != "none" and data.get('referred') == 0:
        referrer_data = getData(data['ref_by'])
        referral_message = f"""
<blockquote>
🎉 <b>Rᴇꜰᴇʀʀᴀʟ Rᴇᴡᴀʀᴅ Nᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ</b> 🎉

Wᴇ'ʀᴇ ᴘʟᴇᴀꜱᴇᴅ ᴛᴏ ɪɴꜰᴏʀᴍ ʏᴏᴜ ᴛʜᴀᴛ ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟ <b>{first_name}</b> ʜᴀꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴊᴏɪɴᴇᴅ ᴜꜱɪɴɢ ʏᴏᴜʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ʟɪɴᴋ.

💰 <b>Rᴇᴡᴀʀᴅ Cʀᴇᴅɪᴛᴇᴅ:</b> +{ref_bonus} ᴄᴏɪɴꜱ
📈 <b>Yᴏᴜʀ Tᴏᴛᴀʟ Rᴇᴡᴀʀᴅꜱ:</b> {int(referrer_data.get('total_refs', 0)) + 1}
💎 <b>Cᴜʀʀᴇɴᴛ Bᴀʟᴀɴᴄᴇ:</b> {float(referrer_data.get('balance', 0)) + float(ref_bonus):.2f} ᴄᴏɪɴꜱ

Kᴇᴇᴘ ꜱʜᴀʀɪɴɢ ʏᴏᴜʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ʟɪɴᴋ ᴛᴏ ᴇᴀʀɴ ᴍᴏʀᴇ ʀᴇᴡᴀʀᴅꜱ & ᴄᴀꜱʜ!
Yᴏᴜʀ ᴜɴɪQᴜᴇ ʟɪɴᴋ: https://t.me/{bot.get_me().username}?start=aff_{data['ref_by']}

Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʜᴇʟᴘɪɴɢ ɢʀᴏᴡ ᴏᴜʀ ᴄᴏᴍᴍᴜɴɪᴛʏ!
</blockquote>
"""
        close_btn = InlineKeyboardMarkup().add(
            InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")
        )
        bot.send_message(
            data['ref_by'],
            referral_message,
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=close_btn
        )
        addBalance(data['ref_by'], ref_bonus)
        setReferredStatus(user_id)

    # Rest of your welcome message code remains the same...
    # [Your existing welcome message code here]

    # Inline buttons for welcome message
    welcome_buttons = InlineKeyboardMarkup()
    welcome_buttons.row(
        InlineKeyboardButton("📱 Wʜᴀᴛꜱᴀᴘᴘ", url=WHATSAPP_CHANNEL),
        InlineKeyboardButton("💬 Sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)
    )
    welcome_buttons.row(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button"))

    # Welcome message with image
    welcome_caption = f"""
<blockquote>
🎉 <b>Wᴇʟᴄᴏᴍᴇ {first_name}!</b> 🎉

👤 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> {username}

Wɪᴛʜ ᴏᴜʀ ʙᴏᴛ, ʏᴏᴜ ᴄᴀɴ ʙᴏᴏꜱᴛ ʏᴏᴜʀ ꜱᴏᴄɪᴀʟ ᴍᴇᴅɪᴀ ᴀᴄᴄᴏᴜɴᴛꜱ & ᴘᴏꜱᴛꜱ ᴡɪᴛʜ ᴊᴜꜱᴛ ᴀ ꜰᴇᴡ ꜱɪᴍᴘʟᴇ ꜱᴛᴇᴘꜱ!

👇 <b>Cʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ꜱᴛᴀʀᴛᴇᴅ:</b>
</blockquote>

🔗 <b>Join our channels:</b>
• 📢 <a href="{UPDATES_CHANNEL_LINK}">Updates Channel</a> - Stay updated  
• 💬 <a href="{SUPPORT_CHAT}">Support Chat</a> - Get help
"""

    try:
        bot.send_photo(
            chat_id=user_id,
            photo=WELCOME_IMAGE_URL,
            caption=welcome_caption,
            parse_mode='HTML',
            reply_markup=welcome_buttons
        )

        bot.send_message(
            user_id,
            "⟱ Cʜᴏᴏꜱᴇ Aɴ Oᴘᴛɪᴏɴ Bᴇʟᴏᴡ ⟱",
            reply_markup=main_markup
        )

        # ==================================
        # Welcome bonus message with close button
        if userData.get('welcome_bonus', 0) == 0:
            welcome_bonus_message = f"""
<blockquote>
🎉 <b>Wᴇʟᴄᴏᴍᴇ Bᴏɴᴜꜱ Cʀᴇᴅɪᴛᴇᴅ!</b>

🪙 <b>+{welcome_bonus} Coins</b> have been added to your wallet.

💎 <b>Cᴜʀʀᴇɴᴛ Bᴀʟᴀɴᴄᴇ:</b> {float(getData(user_id).get('balance', 0)):.2f} ᴄᴏɪɴꜱ

Sᴛᴀʀᴛ ᴜꜱɪɴɢ ʏᴏᴜʀ ʙᴏɴᴜꜱ ᴛᴏ ᴘʟᴀᴄᴇ ʏᴏᴜʀ ꜰɪʀꜱᴛ ᴏʀᴅᴇʀ ɴᴏᴡ!
</blockquote>
"""
            close_button = InlineKeyboardMarkup().add(
                InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")
            )
            bot.send_message(
                user_id,
                welcome_bonus_message,
                parse_mode='HTML',
                reply_markup=close_button
            )

        # Notify about pending orders
        stats = get_user_orders_stats(user_id)
        if stats['pending'] > 0:
            pending_msg = f"""
<blockquote>
⏳ <b>Pᴇɴᴅɪɴɢ Oʀᴅᴇʀꜱ Nᴏᴛɪᴄᴇ</b>

Yᴏᴜ ᴄᴜʀʀᴇɴᴛʟʏ ʜᴀᴠᴇ <b>{stats['pending']}</b> ᴏʀᴅᴇʀ(ꜱ) ᴘᴇɴᴅɪɴɢ ᴄᴏᴍᴘʟᴇᴛɪᴏɴ.  
Yᴏᴜ ᴄᴀɴ ᴠɪᴇᴡ ᴛʜᴇɪʀ ᴘʀᴏɢʀᴇꜱꜱ ᴀɴʏᴛɪᴍᴇ ʙᴇʟᴏᴡ.
</blockquote>
"""
            pending_buttons = InlineKeyboardMarkup()
            pending_buttons.row(
                InlineKeyboardButton("📋 ᴠɪᴇᴡ ᴏʀᴅᴇʀꜱ", callback_data="order_history")
            )
            pending_buttons.row(
                InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")
            )
            bot.send_message(
                user_id,
                pending_msg,
                parse_mode='HTML',
                reply_markup=pending_buttons
            )

    except Exception as e:
        print(f"Error in send_welcome: {e}")

#====================== My Account =====================#
@bot.message_handler(func=lambda message: message.text == "👤 My Account")
def my_account(message):
    user_id = str(message.chat.id)

    # Always re-fetch the freshest data from the DB
    data = getData(user_id)
    
    if not data:
        bot.reply_to(message, "❌ Aᴄᴄᴏᴜɴᴛ ɴᴏᴛ ꜰᴏᴜɴᴅ. Pʟᴇᴀꜱᴇ /start ᴀɢᴀɪɴ.")
        return
    
    # Update last activity and username in DB
    data['last_activity'] = time.time()
    data['username'] = message.from_user.username
    updateUser(user_id, data)
    
    # Get up-to-date stats
    confirmed_spent = get_confirmed_spent(user_id)
    pending_spent = get_pending_spent(user_id)
    total_deposits = get_user_deposits(user_id)

    # Get current time/date
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%Y-%m-%d")

    # Prepare profile photo if exists
    photos = bot.get_user_profile_photos(message.from_user.id, limit=1)

    # Format the message
    caption = f"""
<blockquote>
<b><u>𝗠𝘆 𝗔𝗰𝗰𝗼𝘂𝗻𝘁</u></b>

🪪 Uꜱᴇʀ Iᴅ: <code>{user_id}</code>
👤 Uꜱᴇʀɴᴀᴍᴇ: @{message.from_user.username if message.from_user.username else "N/A"}
🗣 Iɴᴠɪᴛᴇᴅ Uꜱᴇʀꜱ: {data.get('total_refs', 0)}
⏰ Tɪᴍᴇ: {current_time}
📅 Dᴀᴛᴇ: {current_date}

💰 Tᴏᴛᴀʟ Dᴇᴘᴏꜱɪᴛꜱ: <code>{total_deposits:.2f}</code> Cᴏɪɴꜱ
🪙 Cᴜʀʀᴇɴᴛ Bᴀʟᴀɴᴄᴇ: <code>{float(data.get('balance', 0)):.2f}</code> Cᴏɪɴꜱ
💸 Cᴏɴꜰɪʀᴍᴇᴅ Sᴘᴇɴᴛ: <code>{confirmed_spent:.2f}</code> Cᴏɪɴꜱ
⏳ Pᴇɴᴅɪɴɢ Sᴘᴇɴᴅɪɴɢ: <code>{pending_spent:.2f}</code> Cᴏɪɴꜱ
</blockquote>
"""

    # Create close button
    close_button = InlineKeyboardMarkup()
    close_button.add(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button"))

    try:
        if photos.total_count > 0:
            # Send profile photo with caption and close button
            photo_file_id = photos.photos[0][-1].file_id
            bot.send_photo(
                chat_id=user_id,
                photo=photo_file_id,
                caption=caption,
                parse_mode='HTML',
                reply_markup=close_button
            )
        else:
            # Fallback no photo
            bot.send_message(
                chat_id=user_id,
                text=caption,
                parse_mode='HTML',
                reply_markup=close_button
            )
    except Exception as e:
        print(f"Error sending profile photo: {e}")
        # Fallback if sending photo fails
        bot.send_message(
            chat_id=user_id,
            text=caption,
            parse_mode='HTML',
            reply_markup=close_button
        )

#======================= Affiliate Program =======================#
@bot.message_handler(func=lambda message: message.text == "💰 Refer&Earn")
@check_ban
def affiliate_program(message):
    user_id = str(message.chat.id)
    bot_username = bot.get_me().username
    affiliate_link = f"https://t.me/{bot_username}?start=aff_{user_id}"
    data = getData(user_id)
    
    if not data:
        bot.reply_to(message, "Aᴄᴄᴏᴜɴᴛ ɴᴏᴛ ꜰᴏᴜɴᴅ. Pʟᴇᴀꜱᴇ /start ᴀɢᴀɪɴ")
        return
        
    total_refs = data.get('total_refs', 0)
    affiliate_earnings = data.get('affiliate_earnings', 0)

    affiliate_message = f"""
<blockquote>
🏆 <b>Uɴʟᴏᴄᴋ Eɴᴅʟᴇꜱꜱ Eᴀʀɴɪɴɢꜱ ᴡɪᴛʜ Sᴏᴄɪᴀʟʜᴜʙ Bᴏᴏꜱᴛᴇʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ᴘʀᴏɢʀᴀᴍ!</b>  

🌐 <b>Wʜᴀᴛ'ꜱ ᴛʜᴇ ᴀꜰꜰɪʟɪᴀᴛᴇ ᴘʀᴏɢʀᴀᴍ?</b>  
ᴛʜᴇ ꜱᴏᴄɪᴀʟʜᴜʙ ʙᴏᴏꜱᴛᴇʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ᴘʀᴏɢʀᴀᴍ ɪꜱ ʏᴏᴜʀ ᴄʜᴀɴᴄᴇ ᴛᴏ ᴇᴀʀɴ ᴍᴏɴᴇʏ ᴇꜰꜰᴏʀᴛʟᴇꜱꜱʟʏ ʙʏ ᴘʀᴏᴍᴏᴛɪɴɢ ᴏᴜʀ ᴘᴏᴡᴇʀꜰᴜʟ ꜱᴏᴄɪᴀʟ ᴍᴇᴅɪᴀ ᴍᴀʀᴋᴇᴛɪɴɢ ʙᴏᴛ.  

💰 <b>Yᴏᴜʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ꜱᴛᴀᴛꜱ:</b>
├ 👥 Tᴏᴛᴀʟ ʀᴇꜰᴇʀʀᴀʟꜱ: <code>{total_refs}</code>
└ 💰 Tᴏᴛᴀʟ ᴇᴀʀɴɪɴɢꜱ: <code>ᴜɢx {affiliate_earnings:.2f}</code>

🎁 <b>Exᴛʀᴀ ʙᴏɴᴜꜱ:</b> Yᴏᴜ ᴀʟꜱᴏ ᴇᴀʀɴ <code>{welcome_bonus}</code> ᴄᴏɪɴꜱ ᴡʜᴇɴ ꜱᴏᴍᴇᴏɴᴇ ꜱɪɢɴꜱ ᴜᴘ ᴜꜱɪɴɢ ʏᴏᴜʀ ʟɪɴᴋ!

🔗 <b>Yᴏᴜʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ʟɪɴᴋ:</b>  
<code>{affiliate_link}</code>
</blockquote>
"""

    # Inline buttons
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 ꜱʜᴀʀᴇ ʟɪɴᴋ",
                url=f"https://t.me/share/url?url={affiliate_link}&text=🚀 Earn money with this amazing SMM bot! Get social media growth services and earn 5% commission on all orders!"
            ),
            InlineKeyboardButton("📊 ᴠɪᴇᴡ ꜱᴛᴀᴛꜱ", callback_data="affiliate_stats"),
        ],
        [InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")]
    ])
    
    bot.reply_to(
        message,
        affiliate_message,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "affiliate_stats")
def show_affiliate_stats(call):
    user_id = str(call.from_user.id)
    data = getData(user_id)
    
    total_refs = data.get('total_refs', 0)
    affiliate_earnings = data.get('affiliate_earnings', 0)
    
    stats_message = f"""
<blockquote>
📊 <b>Yᴏᴜʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ꜱᴛᴀᴛꜱ</b>

👥 <b>Tᴏᴛᴀʟ ʀᴇꜰᴇʀʀᴀʟꜱ:</b> {total_refs}
💰 <b>Tᴏᴛᴀʟ ᴇᴀʀɴɪɴɢꜱ:</b> ᴜɢx {affiliate_earnings:.2f}

⚠️ <b>Wɪᴛʜᴅʀᴀᴡ ʀᴜʟᴇꜱ:</b>
ʏᴏᴜ ᴄᴀɴ ᴡɪᴛʜᴅʀᴀᴡ ʏᴏᴜʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ᴇᴀʀɴɪɴɢꜱ ᴛᴏ ʏᴏᴜʀ ʀᴇᴀʟ ᴡᴀʟʟᴇᴛ. ᴡɪᴛʜᴅʀᴀᴡᴀʟꜱ ᴀʀᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ᴍᴀɴᴜᴀʟʟʏ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴꜱ. <b>ɴᴏᴛᴇ:</b> ᴇɴꜱᴜʀᴇ ʏᴏᴜ ʜᴀᴠᴇ ᴀᴛ ʟᴇᴀꜱᴛ ᴜɢx 1000 ɪɴ ᴇᴀʀɴɪɴɢꜱ ᴛᴏ ᴡɪᴛʜᴅʀᴀᴡ.
</blockquote>
"""
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=stats_message,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_to_affiliate"),
            InlineKeyboardButton("📤 ᴡɪᴛʜᴅʀᴀᴡ ᴄᴀꜱʜ", url=f"https://t.me/SOCIALBOOSTERADMIN"),
            InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")
        )
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_affiliate")
def back_to_affiliate(call):
    user_id = str(call.from_user.id)
    bot_username = bot.get_me().username
    affiliate_link = f"https://t.me/{bot_username}?start=aff_{user_id}"
    data = getData(user_id)

    if not data:
        bot.answer_callback_query(call.id, "❌ Account not found.")
        return

    total_refs = data.get('total_refs', 0)
    affiliate_earnings = data.get('affiliate_earnings', 0)

    affiliate_message = f"""
<blockquote>
🏆 <b>Uɴʟᴏᴄᴋ ᴇɴᴅʟᴇꜱꜱ ᴇᴀʀɴɪɴɢꜱ ᴡɪᴛʜ ꜱᴍᴍ ᴍᴇɴᴜ ᴀꜰꜰɪʟɪᴀᴛᴇ ᴘʀᴏɢʀᴀᴍ!</b>  

🌐 <b>Wʜᴀᴛ'ꜱ ᴛʜᴇ ᴀꜰꜰɪʟɪᴀᴛᴇ ᴘʀᴏɢʀᴀᴍ?</b>  
Tʜᴇ SMMHUB Booster ᴀꜰꜰɪʟɪᴀᴛᴇ ᴘʀᴏɢʀᴀᴍ ɪꜱ ʏᴏᴜʀ ᴄʜᴀɴᴄᴇ ᴛᴏ ᴇᴀʀɴ ᴍᴏɴᴇʏ ᴇꜰꜰᴏʀᴛʟᴇꜱꜱʟʏ ʙʏ ᴘʀᴏᴍᴏᴛɪɴɢ ᴏᴜʀ ᴘᴏᴡᴇʀꜰᴜʟ ꜱᴏᴄɪᴀʟ ᴍᴇᴅɪᴀ ᴍᴀʀᴋᴇᴛɪɴɢ ʙᴏᴛ. ᴡʜᴇᴛʜᴇʀ ʏᴏᴜ'ʀᴇ ᴀ ᴄᴏɴᴛᴇɴᴛ ᴄʀᴇᴀᴛᴏʀ, ɪɴꜰʟᴜᴇɴᴄᴇʀ, ᴏʀ ᴊᴜꜱᴛ ꜱᴏᴍᴇᴏɴᴇ ᴡɪᴛʜ ᴀ ɴᴇᴛᴡᴏʀᴋ, ᴛʜɪꜱ ɪꜱ ʏᴏᴜʀ ᴏᴘᴘᴏʀᴛᴜɴɪᴛʏ ᴛᴏ ᴛᴜʀɴ ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ ɪɴᴛᴏ ᴄᴀꜱʜ – ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ʜᴀʀᴅ ᴡᴏʀᴋ!  !    

🔍 <b>Hᴏᴡ ᴅᴏᴇꜱ ɪᴛ ᴡᴏʀᴋ?</b>  
1️⃣ <b>Gᴇᴛ Yᴏᴜʀ Lɪɴᴋ</b> - Uꜱᴇ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟɪᴢᴇᴅ ᴀꜰꜰɪʟɪᴀᴛᴇ ʟɪɴᴋ ʙᴇʟᴏᴡ  
2️⃣ <b>Sᴘʀᴇᴀᴅ ᴛʜᴇ Wᴏʀᴅ</b> - Sʜᴀʀᴇ ɪᴛ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘꜱ, ꜱᴏᴄɪᴀʟ ᴍᴇᴅɪᴀ, ᴡʜᴀᴛꜱᴀᴘᴘ, ᴏʀ ᴀɴʏᴡʜᴇʀᴇ ʏᴏᴜʀ ᴀᴜᴅɪᴇɴᴄᴇ ʜᴀɴɢꜱ ᴏᴜᴛ.  
3️⃣ <b>Eᴀʀɴ ꜰᴏʀᴇᴠᴇʀ</b> - Gᴇᴛ 5% ᴏꜰ ᴇᴠᴇʀʏ ᴏʀᴅᴇʀ ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴀʟꜱ ᴍᴀᴋᴇ - ꜰᴏʀ ʟɪꜰᴇ!  

💰 <b>Yᴏᴜʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ꜱᴛᴀᴛꜱ:</b>
├ 👥 Tᴏᴛᴀʟ ʀᴇꜰᴇʀʀᴀʟꜱ: <code>{total_refs}</code>
└ 💰 Tᴏᴛᴀʟ ᴇᴀʀɴɪɴɢꜱ: <code>ᴜɢx {affiliate_earnings:.2f}</code>

📈 <b>Eᴀʀɴɪɴɢꜱ ʙʀᴇᴀᴋᴅᴏᴡɴ:</b>  
- A ʀᴇꜰᴇʀʀᴀʟ ᴏʀᴅᴇʀꜱ $50 ᴡᴏʀᴛʜ ᴏꜰ ꜱᴇʀᴠɪᴄᴇꜱ → Yᴏᴜ ᴇᴀʀɴ $2.50 / ~9,100 ᴜɢx
- Tʜᴇʏ ᴏʀᴅᴇʀ $500 ᴏᴠᴇʀ ᴀ ᴍᴏɴᴛʜ → Yᴏᴜ ᴘᴏᴄᴋᴇᴛ $25.00 / ~91,008 ᴜɢx
- Iᴍᴀɢɪɴᴇ 20 ᴀᴄᴛɪᴠᴇ ʀᴇꜰᴇʀʀᴀʟꜱ sᴘᴇɴᴅɪɴɢ $200 ᴇᴀᴄʜ → ᴛʜᴀᴛ'ꜱ $200.00 / ~728,064 ᴜɢx ɪɴ ʏᴏᴜʀ ᴡᴀʟʟᴇᴛ!

🎁 <b>Exᴛʀᴀ ʙᴏɴᴜꜱ:</b> Yᴏᴜ ᴀʟꜱᴏ ᴇᴀʀɴ <code>{welcome_bonus}</code> ᴄᴏɪɴꜱ ᴡʜᴇɴ ꜱᴏᴍᴇᴏɴᴇ ꜱɪɢɴꜱ ᴜᴘ ᴜꜱɪɴɢ ʏᴏᴜʀ ʟɪɴᴋ!

🔗 <b>Yᴏᴜʀ ᴜɴɪqᴜᴇ ᴀꜰꜰɪʟɪᴀᴛᴇ ʟɪɴᴋ:</b>  
<code>{affiliate_link}</code>

📌 <b>Pʀᴏ ᴛɪᴘ:</b> Sʜᴀʀᴇ ᴛᴏ ᴘᴇᴏᴘʟᴇ ᴡʜᴏ ᴡᴀɴᴛ ꜱᴏᴄɪᴀʟ ᴍᴇᴅɪᴀ ɢʀᴏᴡᴛʜ ꜰᴏʀ ʙᴇꜱᴛ ʀᴇꜱᴜʟᴛꜱ!
</blockquote>
"""

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📤 ꜱʜᴀʀᴇ ʟɪɴᴋ", url=f"https://t.me/share/url?url={affiliate_link}&text=🚀 Earn money with this amazing SMM bot! Get social media growth services and earn 5% commission on all orders!"),
        InlineKeyboardButton("📊 ᴠɪᴇᴡ ꜱᴛᴀᴛꜱ", callback_data="affiliate_stats"),
        InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")
    )

    # EDIT the current message instead of sending a new one
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=affiliate_message,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=markup
    )
    
    bot.answer_callback_query(call.id)

#======================= Help =======================#
@bot.message_handler(func=lambda message: message.text == "📜 Help")
def help_command(message):
    user_id = message.chat.id
    msg = f"""
<blockquote>
<b>FʀᴇQᴜᴇɴᴛʟʏ Aꜱᴋᴇᴅ Qᴜᴇꜱᴛɪᴏɴꜱ</b>

<b>• Aʀᴇ ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇꜱ ʀᴇᴀʟ?</b>
ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇꜱ ᴀʀᴇ ʀᴀɴᴅᴏᴍʟʏ ꜱᴇʟᴇᴄᴛᴇᴅ ꜰʀᴏᴍ ᴏᴜʀ ᴘᴀɴᴇʟ ʙᴜᴛ ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴏɴʟʏ ʀᴇᴀʟ ᴏɴᴇꜱ ᴏɴʟʏ, ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ ᴄᴏɴᴛᴀᴄᴛ ᴜꜱ ꜰᴏʀ ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇ.

<b>• Wʜᴀᴛ'ꜱ ᴛʜᴇ ᴀᴠᴇʀᴀɢᴇ ꜱᴇʀᴠɪᴄᴇ ꜱᴘᴇᴇᴅ?</b>
Dᴇʟɪᴠᴇʀʏ ꜱᴘᴇᴇᴅ ᴠᴀʀɪᴇꜱ ʙᴀꜱᴇᴅ ᴏɴ ɴᴇᴛᴡᴏʀᴋ ᴄᴏɴᴅɪᴛɪᴏɴꜱ ᴀɴᴅ ᴏʀᴅᴇʀ ᴠᴏʟᴜᴍᴇ, ʙᴜᴛ ᴡᴇ ᴇɴꜱᴜʀᴇ ꜰᴀꜱᴛ ᴅᴇʟɪᴠᴇʀʏ.

<b>• Wɪʟʟ ɪ ʀᴇᴄᴇɪᴠᴇ ʀᴇᴀʟ ᴍᴏɴᴇʏ ꜰʀᴏᴍ ᴀꜰꜰɪʟɪᴀᴛᴇ ᴍᴀʀᴋᴇᴛɪɴɢ?</b>
Yᴇꜱ, ᴀꜰᴛᴇʀ ʀᴇᴀᴄʜɪɴɢ 1000 ᴜɢx, ʏᴏᴜ ᴄᴀɴ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴛʜᴇ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴏꜰ ʏᴏᴜʀ ᴀꜰꜰɪʟɪᴀᴛᴇ ʙᴀʟᴀɴᴄᴇ ᴀɴᴅ ʏᴏᴜ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ʏᴏᴜʀ ᴍᴏɴᴇʏ.

<b>• Hᴏᴡ ᴛᴏ ɪɴᴄʀᴇᴀꜱᴇ ʏᴏᴜʀ ᴄᴏɪɴꜱ?</b>
1️⃣ Iɴᴠɪᴛᴇ ꜰʀɪᴇɴᴅꜱ - Eᴀʀɴ {ref_bonus} ᴄᴏɪɴꜱ ᴘᴇʀ ʀᴇꜰᴇʀʀᴀʟ
2️⃣ Bᴜʏ ᴄᴏɪɴ ᴘᴀᴄᴋᴀɢᴇꜱ - Aᴄᴄᴇᴘᴛᴇᴅ ᴘᴀʏᴍᴇɴᴛꜱ:
   • Mᴏʙɪʟᴇ Mᴏɴᴇʏ
   • Cʀʏᴘᴛᴏᴄᴜʀʀᴇɴᴄɪᴇꜱ (BTC, USDT, ᴇᴛᴄ.)
   • WᴇʙMᴏɴᴇʏ & Pᴇʀꜰᴇᴄᴛ Mᴏɴᴇʏ
   
<b>• Bᴜɢꜱ Rᴇᴘᴏʀᴛ Rᴇᴡᴀʀᴅ:</b>
Wᴇ ʀᴇᴡᴀʀᴅ ᴏᴜʀ Uꜱᴇʀꜱ Fʀᴇᴇ 100 ᴄᴏɪɴꜱ ꜰᴏʀ ᴇᴀᴄʜ Bᴜɢ ᴏʀ Eʀʀᴏʀ ᴛʜᴇʏ Rᴇᴘᴏʀᴛ ᴛᴏ Uꜱ. Jᴜꜱᴛ ᴄʟɪᴄᴋ ᴛʜᴇ Bᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ.

<b>• Cᴀɴ I ᴛʀᴀɴꜱꜰᴇʀ ᴍʏ ʙᴀʟᴀɴᴄᴇ?</b>
Yᴇꜱ! Fᴏʀ ʙᴀʟᴀɴᴄᴇꜱ ᴏᴠᴇʀ 10,000 ᴄᴏɪɴꜱ, ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ.
</blockquote>
"""

    # Inline buttons (aligned left & right)
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🆘 ꜱᴜᴘᴘᴏʀᴛ", url="https://t.me/SocialHubBoosterTMbot"),
            InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button"),
        ]
    ])

    bot.reply_to(
        message,
        msg,
        parse_mode="HTML",
        reply_markup=markup
    )

# ======================== Bonus Command ======================= #
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.message_handler(func=lambda message: message.text == "🎉 Bᴏɴᴜs")
@check_ban
def handle_bonus(message):
    user_id = str(message.chat.id)
    data = getData(user_id)

    if not is_bonus_enabled():
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button"))
        bot.reply_to(
            message,
            (
                "<blockquote>"
                "⚠️ <b>Dᴀɪʟʏ ʙᴏɴᴜꜱ ɪꜱ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ.</b>\n"
                "📆 Pʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʙᴀᴄᴋ ʟᴀᴛᴇʀ."
                "</blockquote>"
            ),
            parse_mode='HTML',
            reply_markup=markup
        )
        return

    now = time.time()
    last_claim = data.get('last_bonus_claim', 0)
    interval = get_bonus_interval()

    if now - last_claim < interval:
        remaining = interval - (now - last_claim)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_bonus"))
        bot.reply_to(
            message,
            (
                f"<blockquote>"
                f"🕑 <b>Yᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ʏᴏᴜʀ ʙᴏɴᴜꜱ.</b>\n\n"
                f"⏳ Cᴏᴍᴇ ʙᴀᴄᴋ ɪɴ <b>{hours}ʜ {minutes}ᴍ {seconds}s</b> ᴛᴏ ᴄʟᴀɪᴍ ᴀɢᴀɪɴ."
                f"</blockquote>"
            ),
            parse_mode='HTML',
            reply_markup=markup
        )
        return

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎁 ᴄʟᴀɪᴍ ʙᴏɴᴜꜱ", callback_data="claim_daily_bonus"))
    markup.add(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button"))

    bot.reply_to(
        message,
        (
            "<blockquote>"
            "<b>🔥 Cʟᴀɪᴍ Yᴏᴜʀ Dᴀɪʟʏ Bᴏɴᴜꜱ!</b>\n\n"
            "💡 <b>Yᴏᴜ ᴄᴀɴ ᴄʟᴀɪᴍ ᴀɢᴀɪɴ ᴀꜰᴛᴇʀ ʏᴏᴜʀ ɪɴᴛᴇʀᴠᴀʟ.</b>\n\n"
            "⚠️ <i>Uɴᴜꜱᴇᴅ ʙᴏɴᴜꜱ ᴄᴏɪɴꜱ ᴡɪʟʟ ʙᴇ ʀᴇᴍᴏᴠᴇᴅ ᴡʜᴇɴ ʏᴏᴜ ᴄʟᴀɪᴍ ᴀɢᴀɪɴ.</i>"
            "</blockquote>"
        ),
        parse_mode='HTML',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "claim_daily_bonus")
def claim_daily_bonus(call):
    user_id = str(call.from_user.id)
    data = getData(user_id)

    now = time.time()
    last_claim = data.get('last_bonus_claim', 0)
    interval = get_bonus_interval()
    amount = get_bonus_amount()

    if now - last_claim < interval:
        remaining = interval - (now - last_claim)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        bot.answer_callback_query(
            call.id,
            f"❗ Yᴏᴜ'ᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ. Cᴏᴍᴇ ʙᴀᴄᴋ ɪɴ {hours}ʜ {minutes}ᴍ {seconds}s!",
            show_alert=True
        )
        return

    # Remove old unused bonus (if any)
    old_removed = removeOldBonus(user_id)

    # Add new bonus
    addBonusBalance(user_id, amount)

    msg = (
        f"<blockquote>"
        f"🎉 <b>Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ!</b>\n\n"
        f"💎 Yᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ <b>{amount} Cᴏɪɴꜱ</b> ᴀꜱ ʏᴏᴜʀ Dᴀɪʟʏ Bᴏɴᴜꜱ.\n"
        f"⏳ Cᴏᴍᴇ ʙᴀᴄᴋ ᴀꜰᴛᴇʀ <b>{interval // 60} ᴍɪɴᴜᴛᴇꜱ</b> ᴛᴏ ᴄʟᴀɪᴍ ᴀɢᴀɪɴ."
        f"</blockquote>"
    )

    if old_removed:
        msg = (
            "<blockquote>"
            "⚠️ <i>Yᴏᴜʀ ᴜɴᴜꜱᴇᴅ ʙᴏɴᴜꜱ ᴄᴏɪɴꜱ ꜰʀᴏᴍ ʟᴀꜱᴛ ᴄʟᴀɪᴍ ᴡᴇʀᴇ ʀᴇᴍᴏᴠᴇᴅ.</i>\n\n"
            f"{msg}"
            "</blockquote>"
        )

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button"))

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=msg,
        parse_mode='HTML',
        reply_markup=markup
    )

#======================== Pricing Command =======================#
@bot.message_handler(func=lambda message: message.text == "💳 Pricing")
def pricing_command(message):
    user_id = message.chat.id
    msg = f"""<b><u>💎 Pricing 💎</u></b>

<i> Cʜᴏᴏꜱᴇ Oɴᴇ Oꜰ Tʜᴇ Cᴏɪɴꜱ Pᴀᴄᴋᴀɢᴇꜱ Aɴᴅ Pᴀʏ Iᴛꜱ Cᴏꜱᴛ Vɪᴀ Pʀᴏᴠɪᴅᴇᴅ Pᴀʏᴍᴇɴᴛ Mᴇᴛʜᴏᴅꜱ.</i>
<blockquote>
<b><u>📜 𝐍𝐨𝐫𝐦𝐚𝐥 𝐏𝐚𝐜𝐤𝐚𝐠𝐞𝐬:</u></b>
<b>➊ 📦 1K coins – 1k ᴜɢx
➋ 📦 2K coins – 2k ᴜɢx
➌ 📦 3K coins – 3k ᴜɢx
➍ 📦 4K coins – 4k ᴜɢx
➎ 📦 5K coins – 5k ᴜɢx </b>
</blockquote>

<blockquote>
<b><u>👑 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐏𝐚𝐜𝐤𝐚𝐠𝐞𝐬:</u></b>
<b>➊ 📦 10K coins – $2.8 - 10k ᴜɢx
➋ 📦 20K coins – $5.5 - 20k ᴜɢx
➌ 📦 40K coins – $11 - 40k ᴜɢx
➍ 📦 60K coins – $17 - 60k ᴜɢx
➎ 📦 100K coins – $28 - 100k ᴜɢx </b>
</blockquote>

<b>💡NOTE: 𝘙𝘦𝘮𝘦𝘮𝘣𝘦𝘳 𝘵𝘰 𝘴𝘦𝘯𝘥 𝘺𝘰𝘶𝘳 𝘈𝘤𝘤𝘰𝘶𝘯𝘵 𝘐𝘋 𝘵𝘰 𝘳𝘦𝘤𝘦𝘪𝘷𝘦 𝘤𝘰𝘪𝘯𝘜</b>

<b>🆔 Your id:</b> <code>{user_id}</code>
"""

    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("💳 ᴍᴏʙɪʟᴇ ᴍᴏɴᴇʏ", url="https://t.me/SocialBoosterAdmin")
    button2 = InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")

    markup.add(button1, button2)

    bot.reply_to(message, msg, parse_mode="html", reply_markup=markup)

# ============================= Enhanced Order Statistics with Auto-Clean ============================= #
@bot.message_handler(func=lambda message: message.text == "📊 Order Stats")
@check_ban
def show_order_stats(message):
    """Show performance overview only. Hide completed/failed orders immediately."""
    user_id = str(message.from_user.id)

    try:
        stats = get_user_orders_stats(user_id)

        # Immediately hide completed and failed orders
        orders_collection.update_many(
            {
                "user_id": user_id,
                "status": {"$in": ["completed", "Completed", "failed", "Failed"]},
                "hidden": {"$ne": True}
            },
            {"$set": {"hidden": True}}
        )

        completion_rate = (stats['completed'] / stats['total']) * 100 if stats['total'] > 0 else 0

        msg = f"""
<blockquote>
📦 <b>Yᴏᴜʀ SMM Oʀᴅᴇʀ Pᴏʀᴛꜰᴏʟɪᴏ</b>
━━━━━━━━━━━━━━━━━━━━

📊 <b>Pᴇʀꜰᴏʀᴍᴀɴᴄᴇ Oᴠᴇʀᴠɪᴇᴡ</b>
├ 🔄 Tᴏᴛᴀʟ Oʀᴅᴇʀꜱ: <code>{stats['total']}</code>
├ ✅ Cᴏᴍᴘʟᴇᴛɪᴏɴ Rᴀᴛᴇ: <code>{completion_rate:.1f}%</code>
├ ⏳ Pᴇɴᴅɪɴɢ: <code>{stats['pending']}</code>
└ ❌ Fᴀɪʟᴇᴅ: <code>{stats['failed']}</code>

📌 <b>NOTE:</b> Iꜰ ʏᴏᴜ ʜᴀᴠᴇ ᴀ Fᴀɪʟᴇᴅ Oʀᴅᴇʀ ᴀɴᴅ ʏᴏᴜʀ Cᴏɪɴꜱ ᴡᴇʀᴇ Dᴇᴅᴜᴄᴛᴇᴅ, 
Vɪꜱɪᴛ ᴛʜᴇ @xptoolslogs ᴀɴᴅ ɢᴇᴛ ʏᴏᴜʀ Oʀᴅᴇʀ Iᴅ. 
Tʜᴇɴ ꜱᴇɴᴅ ɪᴛ ᴛᴏ ᴛʜᴇ Aᴅᴍɪɴ ꜰᴏʀ Aꜱꜱɪꜱᴛᴀɴᴄᴇ @SocialHubBoosterTMbot.
</blockquote>
"""

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("📜 ᴄʜᴇᴄᴋ ᴏʀᴅᴇʀꜱ", callback_data="order_history"),
            InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")
        )

        if hasattr(message, 'is_callback'):
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=msg,
                parse_mode='HTML',
                reply_markup=markup
            )
        else:
            sent_msg = bot.send_message(
                message.chat.id,
                msg,
                parse_mode='HTML',
                reply_markup=markup
            )
            threading.Thread(target=delete_after_delay, args=(message.chat.id, sent_msg.message_id, 120)).start()

    except Exception as e:
        print(f"Order stats error: {e}")
        bot.reply_to(message,
            "⚠️ <b>Oʀᴅᴇʀ Sᴛᴀᴛɪꜱᴛɪᴄꜱ Uɴᴀᴠᴀɪʟᴀʙʟᴇ</b>\n\n"
            "ᴡWᴇ ᴄᴏᴜʟᴅɴ'ᴛ ʀᴇᴛʀɪᴇᴠᴇ ʏᴏᴜʀ Oʀᴅᴇʀ Dᴀᴛᴀ ᴀᴛ ᴛʜɪꜱ ᴛɪᴍᴇ\n"
            "Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ",
            parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "order_history")
def show_recent_orders(call):
    """Show pending orders from the last 24h only"""
    user_id = str(call.from_user.id)

    try:
        recent_orders = list(orders_collection.find(
            {
                "user_id": user_id,
                "status": {"$in": ["pending", "processing"]},
                "hidden": {"$ne": True}
            },
            {"service": 1, "quantity": 1, "status": 1, "timestamp": 1, "_id": 0}
        ).sort("timestamp", -1))

        msg = "🕒 <b>Pᴇɴᴅɪɴɢ Oʀᴅᴇʀꜱ (Lᴀꜱᴛ 24ʜ)</b>\n"

        if recent_orders:
            for i, order in enumerate(recent_orders, 1):
                time_ago = format_timespan(time.time() - order.get('timestamp', time.time()))
                msg += f"\n{i}. ⏳ {order.get('service', 'N/A')[:15]}... x{order.get('quantity', '?')} (<i>{time_ago} ᴀɢᴏ</i>)"
        else:
            msg += "\n└ 🌟 Nᴏ ᴘᴇɴᴅɪɴɢ ᴏʀᴅᴇʀꜱ ꜰᴏᴜɴᴅ"

        msg += "\n\n📌 <i>Oɴʟʏ ᴘᴇɴᴅɪɴɢ ᴏʀᴅᴇʀꜱ ᴀʀᴇ ꜱʜᴏᴡɴ ʜᴇʀᴇ</i>"

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🔙 Back", callback_data="show_order_stats"),
            InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")
        )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=msg,
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        print(f"Recent orders error: {e}")
        bot.answer_callback_query(call.id, "❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ʟᴏᴀᴅ ᴘᴇɴᴅɪɴɢ ᴏʀᴅᴇʀꜱ", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "show_order_stats")
@check_ban
def callback_show_order_stats(call):
    """Back to stats page from order list"""
    try:
        from types import SimpleNamespace
        message = SimpleNamespace()
        message.chat = call.message.chat
        message.message_id = call.message.message_id
        message.from_user = call.from_user
        message.is_callback = True
        show_order_stats(message)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Callback show_order_stats error: {e}")
        bot.answer_callback_query(call.id, "⚠️ Failed to go back", show_alert=True)
      
def delete_after_delay(chat_id, message_id, delay):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Could not delete message: {e}")

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

#======================= Send Orders for Telegram =======================#
@bot.message_handler(func=lambda message: message.text == "📱 Order Telegram")
def order_telegram_menu(message):
    """Show Telegram service options"""
    bot.reply_to(message, "📱 Telegram Services:", reply_markup=telegram_services_markup)

@bot.message_handler(func=lambda message: message.text in ["👀 Post Views", "❤️ Cheap Reactions", "❤️ Premium Reactions", "👀 Story Views", "👥 Channel Members", "👥 Premium Members", "👥 Cheap Members", "👥 Bot Members", "🔄 Post Shares", "💬 Post Comments"])
def handle_telegram_order(message):
    """Handle Telegram service selection"""
    user_id = str(message.from_user.id)

    # Store service details in a dictionary
    services = {
        "👀 Post Views": {
            "name": "Post Views",
            "quality": "Super Fast",
            "min": 1000,
            "max": 100000,
            "price": 200,
            "unit": "1k views",
            "service_id": "10576",  # Your SMM panel service ID for views
            "link_hint": "Telegram post link"
        },
            "👀 Story Views": {
            "name": "Story Views",
            "quality": "Super Fast",
            "min": 100,
            "max": 100000,
            "price": 2000,
            "unit": "1k views",
            "service_id": "22852",  # Your SMM panel service ID for views
            "link_hint": "Telegram story link"
        },
        "❤️ Cheap Reactions": {
            "name": "Positive Reactions",
            "quality": "No Refil",
            "min": 100,
            "max": 1000,
            "price": 700,
            "unit": "1k reactions",
            "service_id": "22171",  # Replace with actual service ID
            "link_hint": "Telegram post link"
            
        },
            "❤️ Premium Reactions": {
            "name": "Positive Reactions",
            "quality": "NonDrop-NR",
            "min": 50,
            "max": 1000,
            "price": 700,
            "unit": "1k reactions",
            "service_id": "14498",  # Replace with actual service ID
            "link_hint": "Telegram post link"
            
        },
        "👥 Channel Members": {
            "name": "Members [Mixed]",
            "quality": "Refill 90 Days",
            "min": 500,
            "max": 10000,
            "price": 9560,
            "unit": "1k members",
            "service_id": "18578", # Replace with actual service ID
            "link_hint": "Telegram channel link"  # Replace with actual service ID
        },
            "👥 Premium Members": {
            "name": "Members [Premium]",
            "quality": "No Refill",
            "min": 100,
            "max": 100000,
            "price": 12000,
            "unit": "1k members",
            "service_id": "17400", # Replace with actual service ID
            "link_hint": "Telegram channel link"  # Replace with actual service ID
        },
            "👥 Cheap Members": {
            "name": "Members [Cheap]",
            "quality": "No Refill",
            "min": 500,
            "max": 350000,
            "price": 500,
            "unit": "1k members",
            "service_id": "22809", # Replace with actual service ID
            "link_hint": "Telegram channel link"  # Replace with actual service ID
        },
            "👥 Bot Members": {
            "name": "Bot Members",
            "quality": "Mixed - NR",
            "min": 500,
            "max": 60000,
            "price": 1000,
            "unit": "1k members",
            "service_id": "21200", # Replace with actual service ID
            "link_hint": "Telegram channel link"  # Replace with actual service ID
        },
            "🔄 Post Shares": {
            "name": "Post Shares",
            "quality": "No Refill",
            "min": 50,
            "max": 500000,
            "price": 150,
            "unit": "1k shares",
            "service_id": "21448", # Replace with actual service ID
            "link_hint": "Telegram post link"  # Replace with actual service ID
        },
            "💬 Post Comments": {
            "name": "Post Comments",
            "quality": "Random - NR",
            "min": 100,
            "max": 4500,
            "price": 78000,
            "unit": "1k commments",
            "service_id": "21451", # Replace with actual service ID
            "link_hint": "Telegram post link"  # Replace with actual service ID
        }
    }
    
    service = services[message.text]

    # Check if the service is locked for non-admins
    locked_services = get_locked_services()
    if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
        bot.reply_to(message, "🚫 ᴛʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
        return
    
    # Create cancel markup
    cancel_back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_back_markup.row(
        KeyboardButton("✘ Cancel"),
        KeyboardButton("⌫ ɢᴏ ʙᴀᴄᴋ")
    )
    
    # Store service data in user session (you may need a session system)
    # Here we'll just pass it through the register_next_step_handler
    
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
        process_telegram_quantity, 
        service
    )

def process_telegram_quantity(message, service):
    """Process the quantity input for Telegram orders"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    elif message.text == "⌫ ɢᴏ ʙᴀᴄᴋ":
        bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ Tᴇʟᴇɢʀᴀᴍ Sᴇʀᴠɪᴄᴇꜱ...", reply_markup=telegram_services_markup)
        return
    
    try:
        quantity = int(message.text)
        if quantity < service['min']:
            bot.reply_to(message, f"❌ Mɪɴɪᴍᴜᴍ Oʀᴅᴇʀ ɪꜱ {service['min']}", reply_markup=telegram_services_markup)
            return
        if quantity > service['max']:
            bot.reply_to(message, f"❌ Mᴀxɪᴍᴜᴍ Oʀᴅᴇʀ ɪꜱ {service['max']}", reply_markup=telegram_services_markup)
            return
            
        # Calculate cost
        cost = (quantity * service['price']) // 1000
        user_data = getData(str(message.from_user.id))
        
        if float(user_data['balance']) < cost:
            bot.reply_to(message, f"❌ Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ Bᴀʟᴀɴᴄᴇ. Yᴏᴜ ɴᴇᴇᴅ {cost} ᴄᴏɪɴꜱ.", reply_markup=telegram_services_markup)
            return
            
        # Ask for link
        cancel_back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_back_markup.row(
            KeyboardButton("✘ Cancel")
        )
        
        bot.reply_to(message, "🔗 Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ Tᴇʟᴇɢʀᴀᴍ Pᴏꜱᴛ Lɪɴᴋ:", reply_markup=cancel_back_markup)
        bot.register_next_step_handler(
            message, 
            process_telegram_link, 
            service,
            quantity,
            cost
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ", reply_markup=telegram_services_markup)

def process_telegram_link(message, service, quantity, cost):
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    
    link = message.text.strip()
    
    # Validate link format (basic check)
    if not re.match(r'^https?://t\.me/', link):
        bot.reply_to(message, "❌ Iɴᴠᴀʟɪᴅ Tᴇʟᴇɢʀᴀᴍ ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ", reply_markup=telegram_services_markup)
        return
    
    try:
        response = requests.post(
            SmmPanelApiUrl,
            data={
                'key': SmmPanelApi,
                'action': 'add',
                'service': service['service_id'],
                'link': link,
                'quantity': quantity
            },
            timeout=30
        )
        result = response.json()
        print(f"SMM Panel Response: {result}")  # Debug print
        
        if result and result.get('order'):
            # Deduct balance
            if not cutBalance(str(message.from_user.id), cost):
                raise Exception("Failed to deduct balance")
            
            # Prepare complete order data
            order_data = {
                'service': service['name'],
                'service_type': 'telegram',
                'service_id': service['service_id'],
                'quantity': quantity,
                'cost': cost,
                'link': link,
                'order_id': str(result['order']),
                'status': 'pending',
                'timestamp': time.time(),
                'username': message.from_user.username or str(message.from_user.id)
            }
            
            # Add to order history
            add_order(str(message.from_user.id), order_data)
            
            # Generate notification image
            try:
                image_path = create_order_notification(
                    bot=bot,
                    user_id=message.from_user.id,
                    user_name=message.from_user.first_name,
                    service_name=service['name']
                )

                if image_path:
                    # Create buttons
                    markup = InlineKeyboardMarkup()
                    markup.row(
                        InlineKeyboardButton("🔗 View Order Link", url=link),
                        InlineKeyboardButton("🤖 Visit Bot", url=f"https://t.me/{bot.get_me().username}")
                    )
                    
                    # Stylish notification to payment channel
                    caption = f"""⭐️ ｢ɴᴇᴡ ᴏʀᴅᴇʀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
➠ 🕵🏻‍♂️ Uꜱᴇʀɴᴀᴍᴇ: @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Uꜱᴇʀ Iᴅ: {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 📦 Sᴇʀᴠɪᴄᴇ: {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🔢 Qᴜᴀɴᴛɪᴛʏ: {quantity}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 💰 Cᴏꜱᴛ: {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Oʀᴅᴇʀ Iᴅ: <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
➠ ⚡ Sᴛᴀᴛᴜꜱ: <code>{result.get('status', 'pending').capitalize()}</code>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━"""
                    
                    with open(image_path, 'rb') as photo:
                        bot.send_photo(
                            PAYMENT_CHANNEL,
                            photo,
                            caption=caption,
                            parse_mode='HTML',
                            reply_markup=markup
                        )
                    
                    # Clean up
                    os.remove(image_path)
                    
            except Exception as e:
                print(f"Error generating notification image: {e}")
                # Fallback to text message if image generation fails
                bot.send_message(
                    PAYMENT_CHANNEL,
f"""⭐️ ｢Nᴇᴡ {service['name'].upper()} Oʀᴅᴇʀ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
👤 <b>Uꜱᴇʀ:</b> {message.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━━
🕵🏻‍♂️ <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Uꜱᴇʀ Iᴅ:</b> {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Qᴜᴀɴᴛɪᴛʏ:</b> {quantity}
💰 <b>Cᴏꜱᴛ:</b> {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
📎 <b>Lɪɴᴋ:</b> {link}
🆔 <b>Oʀᴅᴇʀ ID:</b> <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Sᴛᴀᴛᴜꜱ:</b> <code>{result.get('status', 'pending').capitalize()}</code>
🤖 <b>Bᴏᴛ:</b> @{bot.get_me().username}
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━""",
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )

            # Create "Check Order Status" button for user
            markup = InlineKeyboardMarkup()
            check_status_button = InlineKeyboardButton(
                text="📊 Check Order Status",
                url=f"https://t.me/{PAYMENT_CHANNEL.lstrip('@')}"
            )
            markup.add(check_status_button)

            # Stylish confirmation message
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
⚠️ <b>𝙒𝙖𝙧𝙣𝙞𝙣𝙜:</b> Dᴏ ɴᴏᴛ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴀᴍᴇ ᴏʀᴅᴇʀ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ʟɪɴᴋ ʙᴇꜰᴏʀᴇ ᴛʜᴇ ꜰɪʀꜱᴛ ᴏɴᴇ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴏʀ ʏᴏᴜ ᴍɪɢʜᴛ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇ!""",
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )

            # Update orders count
            user_id = str(message.from_user.id)
            data = getData(user_id)
            if 'orders_count' not in data:
                data['orders_count'] = 0
            data['orders_count'] += 1
            updateUser(user_id, data)

            # ✅ Affiliate Commission Tracking - USING GLOBAL FUNCTION
            if data.get('ref_by') and data['ref_by'] != "none":
                try:
                    commission = cost * 0.05  # 5% commission
                    add_affiliate_earning(data['ref_by'], commission)

                    # Use the global affiliate notification function
                    send_affiliate_notification(
                        bot=bot,
                        ref_by_user_id=data['ref_by'],
                        commission=commission,
                        customer_name=message.from_user.first_name,
                        service_name=service['name'],
                        order_cost=cost
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
        if 'result' not in locals() or not result.get('order'):
            bot.reply_to(
                message,
                f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ꜱᴜʙᴍɪᴛ {service['name']} ᴏʀᴅᴇʀ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
                reply_markup=main_markup
            )
        else:
            bot.reply_to(
                message,
                f"⚠️ Oʀᴅᴇʀ ᴡᴀꜱ ꜱᴜʙᴍɪᴛᴛᴇᴅ (ID: {result['order']}) ʙᴜᴛ ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪꜱꜱᴜᴇ ᴡɪᴛʜ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ.",
                reply_markup=main_markup
            )
#========================= Telegram Orders End =========================#

#========================= Order for Tiktok =========================#
@bot.message_handler(func=lambda message: message.text == "🎵 Order TikTok")
def order_tiktok_menu(message):
    """Show TikTok service options"""
    bot.reply_to(message, "🎵 TikTok Services:", reply_markup=tiktok_services_markup)


@bot.message_handler(func=lambda message: message.text in ["👀 Tiktok Views", "👁️‍🗨️ Stream Views", "💗 HQ Likes", "💗 Cheap Likes", "💕 Stream Likes", "💕 Story Likes",
                                                            "👥 Cheap Followers", "👥 Real Followers", "💬 Video Comments", "💬 Stream Comments", 
                                                           "🔄 Video Shares", "🔄 Stream Shares", "💾 Add Favorites", "⚔️ PKBattle Points"])
def handle_tiktok_order(message):
    """Handle TikTok service selection"""
    user_id = str(message.from_user.id)
    
    # TikTok service configurations
    services = {
        "👀 Tiktok Views": {
            "name": "TikTok Views",
            "quality": "Fast&NR",
            "link_hint": "Tiktok Post Link",
            "min": 1000,
            "max": 100000,
            "price": 200,
            "unit": "1k views",
            "service_id": "24748"
        },
            "👁️‍🗨️ Stream Views": {
            "name": "Live Stream Views",
            "quality": "15 Minutes",
            "link_hint": "Tiktok Stream Link",
            "min": 300,
            "max": 10000,
            "price": 4000,
            "unit": "1k views",
            "service_id": "21428"
        },
        "💗 HQ Likes": {
            "name": "Non Drop Likes",
            "quality": "Refill 365D",
            "link_hint": "Tiktok Video Link",
            "min": 500,
            "max": 10000,
            "price": 3000,
            "unit": "1k likes",
            "service_id": "26143"
        },
            "💗 Cheap Likes": {
            "name": "Cheap Likes",
            "quality": "Refill 365D",
            "link_hint": "Tiktok Video Link",
            "min": 500,
            "max": 100000,
            "price": 500,
            "unit": "1k likes",
            "service_id": "24730"
        },
            "💕 Stream Likes": {
            "name": "Live Stream Likes",
            "quality": "NO Refill",
            "link_hint": "Tiktok Stream Link",
            "min": 500,
            "max": 1000000,
            "price": 200,
            "unit": "1k likes",
            "service_id": "23687"
        },
            "💕 Story Likes": {
            "name": "Story Likes",
            "quality": "Real Quality",
            "link_hint": "Tiktok Story Link",
            "min": 500,
            "max": 1000000,
            "price": 1500,
            "unit": "1k likes",
            "service_id": "15793"
        },
        "👥 Cheap Followers": {
            "name": "TikTok Cheap Followers",
            "quality": "HQ ~ Refill 30D",
            "link_hint": "Tiktok Profile Link",
            "min": 100,
            "max": 10000,
            "price": 10000,
            "unit": "1k followers",
            "service_id": "23923"
        },
            "👥 Real Followers": {
            "name": "TikTok Real Followers",
            "quality": "No Refill",
            "link_hint": "Tiktok Profile Link",
            "min": 100,
            "max": 1000000,
            "price": 14000,
            "unit": "1k followers",
            "service_id": "24763"
        },
            "💬 Video Comments": {
            "name": "TikTok Video Comments",
            "quality": "Mixed Quality",
            "link_hint": "Tiktok Video Link",
            "min": 1000,
            "max": 1000,
            "price": 3500,
            "unit": "1k comments",
            "service_id": "23923"
        },
            "💬 Stream Comments": {
            "name": "Stream Emoji Comments",
            "quality": "No Refill",
            "link_hint": "Tiktok Stream Link",
            "min": 100,
            "max": 1000000,
            "price": 42000,
            "unit": "1k comments",
            "service_id": "11607"
        },
            "🔄 Video Shares": {
            "name": "TikTok Video shares",
            "quality": "No Refill",
            "link_hint": "Tiktok Video Link",
            "min": 500,
            "max": 1000000,
            "price": 200,
            "unit": "1k shares",
            "service_id": "18622"
        },
            "🔄 Stream Shares": {
            "name": "Stream shares",
            "quality": "No Refill",
            "link_hint": "Tiktok Stream Link",
            "min": 100,
            "max": 1000000,
            "price": 1500,
            "unit": "1k shares",
            "service_id": "11604"
        },
            "💾 Add Favorites": {
            "name": "TikTok Save Favorites",
            "quality": "No Refill",
            "link_hint": "Tiktok Video Link",
            "min": 100,
            "max": 1000000,
            "price": 500,
            "unit": "1k favorites",
            "service_id": "22288"
        },
            "⚔️ PKBattle Points": {
            "name": "PKBattle Points",
            "quality": "No Refill",
            "link_hint": "Tiktok Stream Link",
            "min": 200,
            "max": 50000,
            "price": 1500,
            "unit": "1k points",
            "service_id": "17564"
        }
    }
    
    service = services[message.text]

        # Check if the service is locked for non-admins
    locked_services = get_locked_services()
    if service['service_id'] in locked_services and message.from_user.id not in admin_user_ids:
        bot.reply_to(message, "🚫 ᴛʜɪꜱ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴀᴅᴍɪɴ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
        return
    
    # Create cancel markup
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
        process_tiktok_quantity, 
        service
    )

def process_tiktok_quantity(message, service):
    """Process the quantity input for TikTok orders"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    elif message.text == "⌫ ɢᴏ ʙᴀᴄᴋ":
        bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ TɪᴋTᴏᴋ ꜱᴇʀᴠɪᴄᴇꜱ...", reply_markup=tiktok_services_markup)
        return
    
    try:
        quantity = int(message.text)
        if quantity < service['min']:
            bot.reply_to(message, f"❌ Mɪɴɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['min']}", reply_markup=tiktok_services_markup)
            return
        if quantity > service['max']:
            bot.reply_to(message, f"❌ Mᴀxɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['max']}", reply_markup=tiktok_services_markup)
            return
            
        # Calculate cost (price is per 1k, so divide quantity by 1000)
        cost = (quantity * service['price']) // 1000
        user_data = getData(str(message.from_user.id))
        
        if float(user_data['balance']) < cost:
            bot.reply_to(message, f"❌ Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ. Yᴏᴜ ɴᴇᴇᴅ {cost} ᴄᴏɪɴꜱ.", reply_markup=tiktok_services_markup)
            return
            
        # Ask for TikTok link
        cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_markup.add(KeyboardButton("✘ Cancel"))
        
        bot.reply_to(message, "🔗 Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ TɪᴋTᴏᴋ ᴠɪᴅᴇᴏ ʟɪɴᴋ:", reply_markup=cancel_markup)
        bot.register_next_step_handler(
            message, 
            process_tiktok_link, 
            service,
            quantity,
            cost
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ", reply_markup=tiktok_services_markup)

def process_tiktok_link(message, service, quantity, cost):
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    
    link = message.text.strip()
    
    # Validate TikTok link format
    if not re.match(r'^https?://(www\.)?(tiktok\.com|vm\.tiktok\.com)/', link):
        bot.reply_to(message, "❌ Iɴᴠᴀʟɪᴅ TɪᴋTᴏᴋ ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ", reply_markup=tiktok_services_markup)
        return
    
    try:
        response = requests.post(
            SmmPanelApiUrl,
            data={
                'key': SmmPanelApi,
                'action': 'add',
                'service': service['service_id'],
                'link': link,
                'quantity': quantity
            },
            timeout=30
        )
        result = response.json()
        print(f"SMM Panel Response: {result}")  # Debug print
        
        if result and result.get('order'):
            # Deduct balance
            if not cutBalance(str(message.from_user.id), cost):
                raise Exception("Failed to deduct balance")
            
            # Prepare complete order data
            order_data = {
                'service': service['name'],
                'service_type': 'tiktok',
                'service_id': service['service_id'],
                'quantity': quantity,
                'cost': cost,
                'link': link,
                'order_id': str(result['order']),
                'status': 'pending',
                'timestamp': time.time(),
                'username': message.from_user.username or str(message.from_user.id)
            }
            
            # Add to order history
            add_order(str(message.from_user.id), order_data)
            
            # Generate notification image
            try:
                image_path = create_order_notification(
                    bot=bot,
                    user_id=message.from_user.id,
                    user_name=message.from_user.first_name,
                    service_name=service['name']
                )
                
                if image_path:
                    # Create buttons
                    markup = InlineKeyboardMarkup()
                    markup.row(
                        InlineKeyboardButton("🔗 View Order Link", url=link),
                        InlineKeyboardButton("🤖 Visit Bot", url=f"https://t.me/{bot.get_me().username}")
                    )
                    
                    # Stylish notification to payment channel
                    caption = f"""⭐️ ｢ɴᴇᴡ ᴏʀᴅᴇʀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
➠ 🕵🏻‍♂️ Uꜱᴇʀɴᴀᴍᴇ: @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Uꜱᴇʀ Iᴅ: {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 📦 Sᴇʀᴠɪᴄᴇ: {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🔢 Qᴜᴀɴᴛɪᴛʏ: {quantity}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 💰 Cᴏꜱᴛ: {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Oʀᴅᴇʀ Iᴅ: <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
➠ ⚡ Sᴛᴀᴛᴜꜱ: <code>{result.get('status', 'pending').capitalize()}</code>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━"""
                    
                    with open(image_path, 'rb') as photo:
                        bot.send_photo(
                            PAYMENT_CHANNEL,
                            photo,
                            caption=caption,
                            parse_mode='HTML',
                            reply_markup=markup
                        )
                    
                    # Clean up
                    os.remove(image_path)
                    
            except Exception as e:
                print(f"Error generating notification image: {e}")
                # Fallback to text message if image generation fails
                bot.send_message(
                    PAYMENT_CHANNEL,
f"""⭐️ ｢Nᴇᴡ {service['name'].upper()} Oʀᴅᴇʀ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
👤 <b>Uꜱᴇʀ:</b> {message.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━━
🕵🏻‍♂️ <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Uꜱᴇʀ Iᴅ:</b> {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Qᴜᴀɴᴛɪᴛʏ:</b> {quantity}
💰 <b>Cᴏꜱᴛ:</b> {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
📎 <b>Lɪɴᴋ:</b> {link}
🆔 <b>Oʀᴅᴇʀ ID:</b> <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Sᴛᴀᴛᴜꜱ:</b> <code>{result.get('status', 'pending').capitalize()}</code>
🤖 <b>Bᴏᴛ:</b> @{bot.get_me().username}
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━""",
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )

            # Create "Check Order Status" button for user
            markup = InlineKeyboardMarkup()
            check_status_button = InlineKeyboardButton(
                text="📊 Check Order Status",
                url=f"https://t.me/{PAYMENT_CHANNEL.lstrip('@')}"
            )
            markup.add(check_status_button)
            
            # Stylish confirmation message
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
⚠️ <b>𝙒𝙖𝙧𝙣𝙞𝙣𝙜:</b> Dᴏ ɴᴏᴛ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴀᴍᴇ ᴏʀᴅᴇʀ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ʟɪɴᴋ ʙᴇꜰᴏʀᴇ ᴛʜᴇ ꜰɪʀꜱᴛ ᴏɴᴇ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴏʀ ʏᴏᴜ ᴍɪɡʜᴛ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇ!""",
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )
            
            # Update orders count
            user_id = str(message.from_user.id)
            data = getData(user_id)
            if 'orders_count' not in data:
                data['orders_count'] = 0
            data['orders_count'] += 1
            updateUser(user_id, data)

            # ✅ Affiliate Commission Tracking - USING GLOBAL FUNCTION
            if data.get('ref_by') and data['ref_by'] != "none":
                try:
                    commission = cost * 0.05  # 5% commission
                    add_affiliate_earning(data['ref_by'], commission)

                    # Use the global affiliate notification function
                    send_affiliate_notification(
                        bot=bot,
                        ref_by_user_id=data['ref_by'],
                        commission=commission,
                        customer_name=message.from_user.first_name,
                        service_name=service['name'],
                        order_cost=cost
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
        if 'result' not in locals() or not result.get('order'):
            bot.reply_to(
                message,
                f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ꜱᴜʙᴍɪᴛ {service['name']} ᴏʀᴅᴇʀ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
                reply_markup=main_markup
            )
        else:
            bot.reply_to(
                message,
                f"⚠️ Oʀᴅᴇʀ ᴡᴀꜱ ꜱᴜʙᴍɪᴛᴛᴇᴅ (ID: {result['order']}) ʙᴜᴛ ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪꜱꜱᴜᴇ ᴡɪᴛʜ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ.",
                reply_markup=main_markup
            )
    
#======================== End of TikTok Orders ========================#

#======================== Send Orders for Instagram =====================#
@bot.message_handler(func=lambda message: message.text == "📸 Order Instagram")
def order_instagram_menu(message):
    """Show Instagram service options"""
    bot.reply_to(message, "📸 Instagram Services:", reply_markup=instagram_services_markup)

@bot.message_handler(func=lambda message: message.text in ["🎥 Reel Views", "👁️‍🗨️ Story Views", "👁️‍🗨️ Photo Views", "👁️‍🗨️ Live Views",
                                                           "💓 Real Likes", "💓 Cheap Likes", "👥 Cheap Followerss", "👥 Real Followerss",
                                                           "🗨️ Real Comments", "🗨️ Random Comments", "🪪 Profile Visits", "👥 Channel Memberss",
                                                           "🔄 Insta Shares", "🔂 Insta Reposts"])
def handle_instagram_order(message):
    """Handle Instagram service selection"""
    user_id = str(message.from_user.id)
    
    services = {
        "🎥 Reel Views": {
            "name": "Instagram Reel Views",
            "quality": "Fast ~ NR",
            "min": 1000,
            "max": 100000,
            "price": 10,
            "unit": "1k views",
            "service_id": "24117",
            "link_hint": "Instagram Reel link"
        },
            "👁️‍🗨️ Story Views": {
            "name": "Instagram Story Views",
            "quality": "Fast ~ NR",
            "min": 200,
            "max": 1000000,
            "price": 600,
            "unit": "1k views",
            "service_id": "23566",
            "link_hint": "Instagram Story link"
        },
            "👁️‍🗨️ Photo Views": {
            "name": "Instagram Photo Views",
            "quality": "Only for Post",
            "min": 100,
            "max": 1000000,
            "price": 150,
            "unit": "1k views",
            "service_id": "24073",
            "link_hint": "Instagram Photo link"
        },
            "👁️‍🗨️ Live Views": {
            "name": "Instagram Live Views",
            "quality": "15 Minutes",
            "min": 200,
            "max": 1000,
            "price": 5000,
            "unit": "1k views",
            "service_id": "23938",
            "link_hint": "Instagram live link"
        },
            "💓 Real Likes": {
            "name": "Instagram Real Likes",
            "quality": "Fast - Refill 30D",
            "min": 100,
            "max": 1000000,
            "price": 5000,
            "unit": "1k likes",
            "service_id": "24375",
            "link_hint": "Instagram post link"
        },
            "💓 Cheap Likes": {
            "name": "Instagram Cheap Likes",
            "quality": "Fast Working",
            "min": 100,
            "max": 1000000,
            "price": 1500,
            "unit": "1k likes",
            "service_id": "24790",
            "link_hint": "Instagram post link"
        },
            "👥 Real Followerss": {
            "name": "Insta Real Followers",
            "quality": "Refill 365D",
            "min": 100,
            "max": 100000,
            "price": 17000,
            "unit": "1k followers",
            "service_id": "24768",
            "link_hint": "Instagram profile link and Disable The Flag for Review from Settings"
        },
            "👥 Cheap Followerss": {
            "name": "Insta Cheap Followers",
            "quality": "Refill 30D",
            "min": 200,
            "max": 10000,
            "price": 10000,
            "unit": "1k followers",
            "service_id": "24670",
            "link_hint": "Instagram profile link and Disable The Flag for Review from Settings"
        },
            "🗨️ Real Comments": {
            "name": "Insta Real Comments",
            "quality": "Real Users",
            "min": 1000,
            "max": 1000,
            "price": 9000,
            "unit": "1k comments",
            "service_id": "24471",
            "link_hint": "Instagram post link"
        },
            "🗨️ Random Comments": {
            "name": "Insta Random Comments",
            "quality": "No Refill",
            "min": 100,
            "max": 5000,
            "price": 6000,
            "unit": "1k comments",
            "service_id": "24692",
            "link_hint": "Instagram post link"
        },
            "🪪 Profile Visits": {
            "name": "Insta Profile Visits",
            "quality": "Instant",
            "min": 200,
            "max": 1000000,
            "price": 400,
            "unit": "1k visits",
            "service_id": "12187",
            "link_hint": "Instagram profile link"
        },
        "👥 Channel Memberss": {
            "name": "Insta Channel Members",
            "quality": "High Quality",
            "min": 200,
            "max": 1000000,
            "price": 5000,
            "unit": "1k members",
            "service_id": "24320",
            "link_hint": "Instagram channel link"
        },
            "🔄 Insta Shares": {
            "name": "Insta post shares",
            "quality": "Instant",
            "min": 100,
            "max": 1000000,
            "price": 150,
            "unit": "1k shares",
            "service_id": "15569",
            "link_hint": "Instagram post link"
        },
            "🔂 Insta Reposts": {
            "name": "Insta Reposts",
            "quality": "High Quality",
            "min": 100,
            "max": 1000000,
            "price": 4000,
            "unit": "1k reposts",
            "service_id": "24382",
            "link_hint": "Instagram post link"
        },
    }
    
    service = services[message.text]

        # Check if the service is locked for non-admins
    locked_services = get_locked_services()
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
        process_instagram_quantity, 
        service
    )

def process_instagram_quantity(message, service):
    """Process Instagram order quantity"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    elif message.text == "⌫ ɢᴏ ʙᴀᴄᴋ":
        bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ Iɴꜱᴛᴀɢʀᴀᴍ ꜱᴇʀᴠɪᴄᴇꜱ...", reply_markup=instagram_services_markup)
        return
    
    try:
        quantity = int(message.text)
        if quantity < service['min']:
            bot.reply_to(message, f"❌ Mɪɴɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['min']}", reply_markup=instagram_services_markup)
            return
        if quantity > service['max']:
            bot.reply_to(message, f"❌ Mᴀxɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['max']}", reply_markup=instagram_services_markup)
            return
            
        cost = (quantity * service['price']) // 1000
        user_data = getData(str(message.from_user.id))
        
        if float(user_data['balance']) < cost:
            bot.reply_to(message, f"❌ Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ. Yᴏᴜ ɴᴇᴇᴅ {cost} ᴄᴏɪɴꜱ.", reply_markup=instagram_services_markup)
            return
            
        cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_markup.add(KeyboardButton("✘ Cancel"))
        
        bot.reply_to(message, f"🔗 Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ {service['link_hint']}:", reply_markup=cancel_markup)
        bot.register_next_step_handler(
            message, 
            process_instagram_link, 
            service,
            quantity,
            cost
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ", reply_markup=instagram_services_markup)

def process_instagram_link(message, service, quantity, cost):
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    
    link = message.text.strip()
    
    # Validate Instagram link format
    if not re.match(r'^https?://(www\.)?instagram\.com/[\w./-]+', link):
        bot.reply_to(message, "❌ Iɴᴠᴀʟɪᴅ Iɴꜱᴛᴀɢʀᴀᴍ ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ", reply_markup=instagram_services_markup)
        return
    
    try:
        response = requests.post(
            SmmPanelApiUrl,
            data={
                'key': SmmPanelApi,
                'action': 'add',
                'service': service['service_id'],
                'link': link,
                'quantity': quantity
            },
            timeout=30
        )
        result = response.json()
        print(f"SMM Panel Response: {result}")  # Debug print
        
        if result and result.get('order'):
            # Deduct balance
            if not cutBalance(str(message.from_user.id), cost):
                raise Exception("Failed to deduct balance")
            
            # Prepare complete order data
            order_data = {
                'service': service['name'],
                'service_type': 'instagram',
                'service_id': service['service_id'],
                'quantity': quantity,
                'cost': cost,
                'link': link,
                'order_id': str(result['order']),
                'status': 'pending',
                'timestamp': time.time(),
                'username': message.from_user.username or str(message.from_user.id)
            }
            
            # Add to order history
            add_order(str(message.from_user.id), order_data)
            
            # Generate notification image
            try:
                image_path = create_order_notification(
                    bot=bot,
                    user_id=message.from_user.id,
                    user_name=message.from_user.first_name,
                    service_name=service['name']
                )
                
                if image_path:
                    # Create buttons
                    markup = InlineKeyboardMarkup()
                    markup.row(
                        InlineKeyboardButton("🔗 View Order Link", url=link),
                        InlineKeyboardButton("🤖 Visit Bot", url=f"https://t.me/{bot.get_me().username}")
                    )
                    
                    # Stylish notification to payment channel
                    caption = f"""⭐️ ｢ɴᴇᴡ ᴏʀᴅᴇʀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
➠ 🕵🏻‍♂️ Uꜱᴇʀɴᴀᴍᴇ: @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Uꜱᴇʀ Iᴅ: {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 📦 Sᴇʀᴠɪᴄᴇ: {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🔢 Qᴜᴀɴᴛɪᴛʏ: {quantity}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 💰 Cᴏꜱᴛ: {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Oʀᴅᴇʀ Iᴅ: <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
➠ ⚡ Sᴛᴀᴛᴜꜱ: <code>{result.get('status', 'pending').capitalize()}</code>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━"""
                    
                    with open(image_path, 'rb') as photo:
                        bot.send_photo(
                            PAYMENT_CHANNEL,
                            photo,
                            caption=caption,
                            parse_mode='HTML',
                            reply_markup=markup
                        )
                    
                    # Clean up
                    os.remove(image_path)
                    
            except Exception as e:
                print(f"Error generating notification image: {e}")
                # Fallback to text message if image generation fails
                bot.send_message(
                    PAYMENT_CHANNEL,
f"""⭐️ ｢Nᴇᴡ {service['name'].upper()} Oʀᴅᴇʀ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
👤 <b>Uꜱᴇʀ:</b> {message.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━━
🕵🏻‍♂️ <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Uꜱᴇʀ Iᴅ:</b> {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Qᴜᴀɴᴛɪᴛʏ:</b> {quantity}
💰 <b>Cᴏꜱᴛ:</b> {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
📎 <b>Lɪɴᴋ:</b> {link}
🆔 <b>Oʀᴅᴇʀ ID:</b> <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Sᴛᴀᴛᴜꜱ:</b> <code>{result.get('status', 'pending').capitalize()}</code>
🤖 <b>Bᴏᴛ:</b> @{bot.get_me().username}
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━""",
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )

            # Create "Check Order Status" button for user
            markup = InlineKeyboardMarkup()
            check_status_button = InlineKeyboardButton(
                text="📊 Check Order Status",
                url=f"https://t.me/{PAYMENT_CHANNEL.lstrip('@')}"
            )
            markup.add(check_status_button)
            
            # Stylish confirmation message
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
⚠️ <b>𝙒𝙖𝙧𝙣𝙞𝙣𝙜:</b> Dᴏ ɴᴏᴛ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴀᴍᴇ ᴏʀᴅᴇʀ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ʟɪɴᴋ ʙᴇꜰᴏʀᴇ ᴛʜᴇ ꜰɪʀꜱᴛ ᴏɴᴇ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴏʀ ʏᴏᴜ ᴍɪɡʜᴛ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇ!""",
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )
            
            # Update orders count
            user_id = str(message.from_user.id)
            data = getData(user_id)
            if 'orders_count' not in data:
                data['orders_count'] = 0
            data['orders_count'] += 1
            updateUser(user_id, data)

            # ✅ Affiliate Commission Tracking - USING GLOBAL FUNCTION
            if data.get('ref_by') and data['ref_by'] != "none":
                try:
                    commission = cost * 0.05  # 5% commission
                    add_affiliate_earning(data['ref_by'], commission)

                    # Use the global affiliate notification function
                    send_affiliate_notification(
                        bot=bot,
                        ref_by_user_id=data['ref_by'],
                        commission=commission,
                        customer_name=message.from_user.first_name,
                        service_name=service['name'],
                        order_cost=cost
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
        if 'result' not in locals() or not result.get('order'):
            bot.reply_to(
                message,
                f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ꜱᴜʙᴍɪᴛ {service['name']} ᴏʀᴅᴇʀ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
                reply_markup=main_markup
            )
        else:
            bot.reply_to(
                message,
                f"⚠️ Oʀᴅᴇʀ ᴡᴀꜱ ꜱᴜʙᴍɪᴛᴛᴇᴅ (ID: {result['order']}) ʙᴜᴛ ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪꜱꜱᴜᴇ ᴡɪᴛʜ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ.",
                reply_markup=main_markup
            )
#======================== End of Instagram Orders ===========================#

#======================== Send Orders for Youtube =====================#
@bot.message_handler(func=lambda message: message.text == "▶️ Order YouTube")
def order_youtube_menu(message):
    """Show YouTube service options"""
    bot.reply_to(message, "▶️ YouTube Services:", reply_markup=youtube_services_markup)

@bot.message_handler(func=lambda message: message.text in ["▶️ YT Views", "👍 YT Likes", "👥 YT Subscribers"])
def handle_youtube_order(message):
    """Handle YouTube service selection"""
    user_id = str(message.from_user.id)
    
    services = {
        "▶️ YT Views": {
            "name": "YouTube Views",
            "quality": "Non Drop",
            "min": 500,
            "max": 1000000,
            "price": 8000,
            "unit": "1k views",
            "service_id": "22299",
            "link_hint": "YouTube video link"
        },
        "👍 YT Likes": {
            "name": "YouTube Likes [Real]",
            "quality": "Refill 90D",
            "min": 50,
            "max": 10000,
            "price": 1500,
            "unit": "1k likes",
            "service_id": "8464",
            "link_hint": "YouTube video link"
        },
        "👥 YT Subscribers": {
            "name": "YouTube Subscribers [Cheapest]",
            "quality": "Refill 30 days",
            "min": 200,
            "max": 10000,
            "price": 178000,
            "unit": "1k subscribers",
            "service_id": "24017",
            "link_hint": "YouTube channel link"
        }
    }
    
    service = services[message.text]

        # Check if the service is locked for non-admins
    locked_services = get_locked_services()
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
        process_youtube_quantity, 
        service
    )

def process_youtube_quantity(message, service):
    """Process YouTube order quantity"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    elif message.text == "⌫ ɢᴏ ʙᴀᴄᴋ":
        bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ YᴏᴜTᴜʙᴇ ꜱᴇʀᴠɪᴄᴇꜱ...", reply_markup=youtube_services_markup)
        return
    
    try:
        quantity = int(message.text)
        if quantity < service['min']:
            bot.reply_to(message, f"❌ Mɪɴɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['min']}", reply_markup=youtube_services_markup)
            return
        if quantity > service['max']:
            bot.reply_to(message, f"❌ Mᴀxɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['max']}", reply_markup=youtube_services_markup)
            return
            
        cost = (quantity * service['price']) // 1000
        user_data = getData(str(message.from_user.id))
        
        if float(user_data['balance']) < cost:
            bot.reply_to(message, f"❌ Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ. Yᴏᴜ ɴᴇᴇᴅ {cost} ᴄᴏɪɴꜱ.", reply_markup=youtube_services_markup)
            return
            
        cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_markup.add(KeyboardButton("✘ Cancel"))
        
        bot.reply_to(message, f"🔗 Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ {service['link_hint']}:", reply_markup=cancel_markup)
        bot.register_next_step_handler(
            message, 
            process_youtube_link, 
            service,
            quantity,
            cost
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ", reply_markup=youtube_services_markup)

def process_youtube_link(message, service, quantity, cost):
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    
    link = message.text.strip()
    
    if not re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/', link):
        bot.reply_to(message, "❌ Iɴᴠᴀʟɪᴅ YᴏᴜTᴜʙᴇ ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ", reply_markup=youtube_services_markup)
        return
    
    try:
        response = requests.post(
            SmmPanelApiUrl,
            data={
                'key': SmmPanelApi,
                'action': 'add',
                'service': service['service_id'],
                'link': link,
                'quantity': quantity
            },
            timeout=30
        )
        result = response.json()
        print(f"SMM Panel Response: {result}")  # Debug print
        
        if result and result.get('order'):
            # Deduct balance
            if not cutBalance(str(message.from_user.id), cost):
                raise Exception("Failed to deduct balance")
            
            # Prepare complete order data
            order_data = {
                'service': service['name'],
                'service_type': 'youtube',
                'service_id': service['service_id'],
                'quantity': quantity,
                'cost': cost,
                'link': link,
                'order_id': str(result['order']),
                'status': 'pending',
                'timestamp': time.time(),
                'username': message.from_user.username or str(message.from_user.id)
            }
            
            # Add to order history
            add_order(str(message.from_user.id), order_data)
            
            # Generate notification image
            try:
                image_path = create_order_notification(
                    bot=bot,
                    user_id=message.from_user.id,
                    user_name=message.from_user.first_name,
                    service_name=service['name']
                )
                
                if image_path:
                    # Create buttons
                    markup = InlineKeyboardMarkup()
                    markup.row(
                        InlineKeyboardButton("🔗 View Order Link", url=link),
                        InlineKeyboardButton("🤖 Visit Bot", url=f"https://t.me/{bot.get_me().username}")
                    )
                    
                    # Stylish notification to payment channel
                    caption = f"""⭐️ ｢ɴᴇᴡ ᴏʀᴅᴇʀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
➠ 🕵🏻‍♂️ Uꜱᴇʀɴᴀᴍᴇ: @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Uꜱᴇʀ Iᴅ: {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 📦 Sᴇʀᴠɪᴄᴇ: {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🔢 Qᴜᴀɴᴛɪᴛʏ: {quantity}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 💰 Cᴏꜱᴛ: {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Oʀᴅᴇʀ Iᴅ: <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
➠ ⚡ Sᴛᴀᴛᴜꜱ: <code>{result.get('status', 'pending').capitalize()}</code>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━"""
                    
                    with open(image_path, 'rb') as photo:
                        bot.send_photo(
                            PAYMENT_CHANNEL,
                            photo,
                            caption=caption,
                            parse_mode='HTML',
                            reply_markup=markup
                        )
                    
                    # Clean up
                    os.remove(image_path)
                    
            except Exception as e:
                print(f"Error generating notification image: {e}")
                # Fallback to text message if image generation fails
                bot.send_message(
                    PAYMENT_CHANNEL,
f"""⭐️ ｢Nᴇᴡ {service['name'].upper()} Oʀᴅᴇʀ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
👤 <b>Uꜱᴇʀ:</b> {message.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━━
🕵🏻‍♂️ <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Uꜱᴇʀ Iᴅ:</b> {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Qᴜᴀɴᴛɪᴛʏ:</b> {quantity}
💰 <b>Cᴏꜱᴛ:</b> {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
📎 <b>Lɪɴᴋ:</b> {link}
🆔 <b>Oʀᴅᴇʀ ID:</b> <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Sᴛᴀᴛᴜꜱ:</b> <code>{result.get('status', 'pending').capitalize()}</code>
🤖 <b>Bᴏᴛ:</b> @{bot.get_me().username}
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━""",
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )

            # Create "Check Order Status" button for user
            markup = InlineKeyboardMarkup()
            check_status_button = InlineKeyboardButton(
                text="📊 Check Order Status",
                url=f"https://t.me/{PAYMENT_CHANNEL.lstrip('@')}"
            )
            markup.add(check_status_button)
            
            # Stylish confirmation message
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
⚠️ <b>𝙒𝙖𝙧𝙣𝙞𝙣𝙜:</b> Dᴏ ɴᴏᴛ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴀᴍᴇ ᴏʀᴅᴇʀ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ʟɪɴᴋ ʙᴇꜰᴏʀᴇ ᴛʜᴇ ꜰɪʀꜱᴛ ᴏɴᴇ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴏʀ ʏᴏᴜ ᴍɪɡʜᴛ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇ!""",
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )
            
            # Update orders count
            user_id = str(message.from_user.id)
            data = getData(user_id)
            if 'orders_count' not in data:
                data['orders_count'] = 0
            data['orders_count'] += 1
            updateUser(user_id, data)

            # ✅ Affiliate Commission Tracking - USING GLOBAL FUNCTION
            if data.get('ref_by') and data['ref_by'] != "none":
                try:
                    commission = cost * 0.05  # 5% commission
                    add_affiliate_earning(data['ref_by'], commission)

                    # Use the global affiliate notification function
                    send_affiliate_notification(
                        bot=bot,
                        ref_by_user_id=data['ref_by'],
                        commission=commission,
                        customer_name=message.from_user.first_name,
                        service_name=service['name'],
                        order_cost=cost
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
        if 'result' not in locals() or not result.get('order'):
            bot.reply_to(
                message,
                f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ꜱᴜʙᴍɪᴛ {service['name']} ᴏʀᴅᴇʀ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
                reply_markup=main_markup
            )
        else:
            bot.reply_to(
                message,
                f"⚠️ Oʀᴅᴇʀ ᴡᴀꜱ ꜱᴜʙᴍɪᴛᴛᴇᴅ (ID: {result['order']}) ʙᴜᴛ ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪꜱꜱᴜᴇ ᴡɪᴛʜ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ.",
                reply_markup=main_markup
            )
#======================== End of Youtube Orders =====================#

#======================== Send Orders for Facebook =====================#
@bot.message_handler(func=lambda message: message.text == "📘 Order Facebook")
def order_facebook_menu(message):
    """Show Facebook service options"""
    bot.reply_to(message, "📘 Facebook Services:", reply_markup=facebook_services_markup)

@bot.message_handler(func=lambda message: message.text in ["👤 Profile Followers", "📄 Page Followers", "🎥 Video/Reel Views", "❤️ Post Likes"])
def handle_facebook_order(message):
    """Handle Facebook service selection"""
    user_id = str(message.from_user.id)
    
    services = {
        "👤 Profile Followers": {
            "name": "FB Profile Followers",
            "quality": "High Quality",
            "min": 500,
            "max": 1000000,
            "price": 4000,
            "unit": "1k followers",
            "service_id": "18974",
            "link_hint": "Facebook profile link"
        },
        "📄 Page Followers": {
            "name": "FB Page Followers",
            "quality": "Refill 30 Days",
            "min": 500,
            "max": 1000000,
            "price": 4000,
            "unit": "1k followers",
            "service_id": "18974",
            "link_hint": "Facebook page link"
        },
        "🎥 Video/Reel Views": {
            "name": "FB Video/Reel Views",
            "quality": "Non Drop",
            "min": 500,
            "max": 1000000,
            "price": 679,
            "unit": "1k views",
            "service_id": "18457",
            "link_hint": "Facebook video/reel link"
        },
        "❤️ Post Likes": {
            "name": "FB Post Likes",
            "quality": "No Refill",
            "min": 100,
            "max": 10000,
            "price": 1500,
            "unit": "1k likes",
            "service_id": "18990",
            "link_hint": "Facebook post link"
        }
    }
    
    service = services[message.text]

        # Check if the service is locked for non-admins
    locked_services = get_locked_services()
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
        process_facebook_quantity, 
        service
    )

def process_facebook_quantity(message, service):
    """Process Facebook order quantity"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    elif message.text == "⌫ ɢᴏ ʙᴀᴄᴋ":
        bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ Fᴀᴄᴇʙᴏᴏᴋ ꜱᴇʀᴠɪᴄᴇꜱ...", reply_markup=facebook_services_markup)
        return
    
    try:
        quantity = int(message.text)
        if quantity < service['min']:
            bot.reply_to(message, f"❌ Mɪɴɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['min']}", reply_markup=facebook_services_markup)
            return
        if quantity > service['max']:
            bot.reply_to(message, f"❌ Mᴀxɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['max']}", reply_markup=facebook_services_markup)
            return
            
        cost = (quantity * service['price']) // 1000
        user_data = getData(str(message.from_user.id))
        
        if float(user_data['balance']) < cost:
            bot.reply_to(message, f"❌ Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ. Yᴏᴜ ɴᴇᴇᴅ {cost} ᴄᴏɪɴꜱ.", reply_markup=facebook_services_markup)
            return
            
        cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_markup.add(KeyboardButton("✘ Cancel"))
        
        bot.reply_to(message, f"🔗 Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ {service['link_hint']}:", reply_markup=cancel_markup)
        bot.register_next_step_handler(
            message, 
            process_facebook_link, 
            service,
            quantity,
            cost
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ", reply_markup=facebook_services_markup)

def process_facebook_link(message, service, quantity, cost):
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    
    link = message.text.strip()
    
    if not re.match(r'^https?://(www\.|m\.)?(facebook\.com|fb\.watch)/', link):
        bot.reply_to(message, "❌ Iɴᴠᴀʟɪᴅ Fᴀᴄᴇʙᴏᴏᴋ ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ", reply_markup=facebook_services_markup)
        return
    
    try:
        response = requests.post(
            SmmPanelApiUrl,
            data={
                'key': SmmPanelApi,
                'action': 'add',
                'service': service['service_id'],
                'link': link,
                'quantity': quantity
            },
            timeout=30
        )
        result = response.json()
        print(f"SMM Panel Response: {result}")  # Debug print
        
        if result and result.get('order'):
            # Deduct balance
            if not cutBalance(str(message.from_user.id), cost):
                raise Exception("Failed to deduct balance")
            
            # Prepare complete order data
            order_data = {
                'service': service['name'],
                'service_type': 'facebook',
                'service_id': service['service_id'],
                'quantity': quantity,
                'cost': cost,
                'link': link,
                'order_id': str(result['order']),
                'status': 'pending',
                'timestamp': time.time(),
                'username': message.from_user.username or str(message.from_user.id)
            }
            
            # Add to order history
            add_order(str(message.from_user.id), order_data)
            
            # Generate notification image
            try:
                image_path = create_order_notification(
                    bot=bot,
                    user_id=message.from_user.id,
                    user_name=message.from_user.first_name,
                    service_name=service['name']
                )
                
                if image_path:
                    # Create buttons
                    markup = InlineKeyboardMarkup()
                    markup.row(
                        InlineKeyboardButton("🔗 View Order Link", url=link),
                        InlineKeyboardButton("🤖 Visit Bot", url=f"https://t.me/{bot.get_me().username}")
                    )
                    
                    # Stylish notification to payment channel
                    caption = f"""⭐️ ｢ɴᴇᴡ ᴏʀᴅᴇʀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
➠ 🕵🏻‍♂️ Uꜱᴇʀɴᴀᴍᴇ: @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Uꜱᴇʀ Iᴅ: {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 📦 Sᴇʀᴠɪᴄᴇ: {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🔢 Qᴜᴀɴᴛɪᴛʏ: {quantity}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 💰 Cᴏꜱᴛ: {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Oʀᴅᴇʀ Iᴅ: <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
➠ ⚡ Sᴛᴀᴛᴜꜱ: <code>{result.get('status', 'pending').capitalize()}</code>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━"""
                    
                    with open(image_path, 'rb') as photo:
                        bot.send_photo(
                            PAYMENT_CHANNEL,
                            photo,
                            caption=caption,
                            parse_mode='HTML',
                            reply_markup=markup
                        )
                    
                    # Clean up
                    os.remove(image_path)
                    
            except Exception as e:
                print(f"Error generating notification image: {e}")
                # Fallback to text message if image generation fails
                bot.send_message(
                    PAYMENT_CHANNEL,
f"""⭐️ ｢Nᴇᴡ {service['name'].upper()} Oʀᴅᴇʀ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
👤 <b>Uꜱᴇʀ:</b> {message.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━━
🕵🏻‍♂️ <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Uꜱᴇʀ Iᴅ:</b> {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Qᴜᴀɴᴛɪᴛʏ:</b> {quantity}
💰 <b>Cᴏꜱᴛ:</b> {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
📎 <b>Lɪɴᴋ:</b> {link}
🆔 <b>Oʀᴅᴇʀ ID:</b> <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Sᴛᴀᴛᴜꜱ:</b> <code>{result.get('status', 'pending').capitalize()}</code>
🤖 <b>Bᴏᴛ:</b> @{bot.get_me().username}
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━""",
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )

            # Create "Check Order Status" button for user
            markup = InlineKeyboardMarkup()
            check_status_button = InlineKeyboardButton(
                text="📊 Check Order Status",
                url=f"https://t.me/{PAYMENT_CHANNEL.lstrip('@')}"
            )
            markup.add(check_status_button)
            
            # Stylish confirmation message
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
⚠️ <b>𝙒𝙖𝙧𝙣𝙞𝙣𝙜:</b> Dᴏ ɴᴏᴛ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴀᴍᴇ ᴏʀᴅᴇʀ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ʟɪɴᴋ ʙᴇꜰᴏʀᴇ ᴛʜᴇ ꜰɪʀꜱᴛ ᴏɴᴇ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴏʀ ʏᴏᴜ ᴍɪɡʜᴛ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇ!""",
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )
            
            # Update orders count
            user_id = str(message.from_user.id)
            data = getData(user_id)
            if 'orders_count' not in data:
                data['orders_count'] = 0
            data['orders_count'] += 1
            updateUser(user_id, data)

            # ✅ Affiliate Commission Tracking - USING GLOBAL FUNCTION
            if data.get('ref_by') and data['ref_by'] != "none":
                try:
                    commission = cost * 0.05  # 5% commission
                    add_affiliate_earning(data['ref_by'], commission)

                    # Use the global affiliate notification function
                    send_affiliate_notification(
                        bot=bot,
                        ref_by_user_id=data['ref_by'],
                        commission=commission,
                        customer_name=message.from_user.first_name,
                        service_name=service['name'],
                        order_cost=cost
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
        if 'result' not in locals() or not result.get('order'):
            bot.reply_to(
                message,
                f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ꜱᴜʙᴍɪᴛ {service['name']} ᴏʀᴅᴇʀ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
                reply_markup=main_markup
            )
        else:
            bot.reply_to(
                message,
                f"⚠️ Oʀᴅᴇʀ ᴡᴀꜱ ꜱᴜʙᴍɪᴛᴛᴇᴅ (ID: {result['order']}) ʙᴜᴛ ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪꜱꜱᴜᴇ ᴡɪᴛʜ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ.",
                reply_markup=main_markup
            )
#======================== End of Facebook Orders =====================# 

#======================== Send Orders for Whastapp =====================#
@bot.message_handler(func=lambda message: message.text == "💬 Order WhatsApp")
def order_whatsapp_menu(message):
    """Show WhatsApp service options"""
    bot.reply_to(message, "💬 WhatsApp Services:", reply_markup=whatsapp_services_markup)

@bot.message_handler(func=lambda message: message.text in ["👥 Channel Subscribers", "😀 Post EmojiReaction"])
def handle_whatsapp_order(message):
    """Handle WhatsApp service selection"""
    user_id = str(message.from_user.id)
    
    services = {
        "👥 Channel Subscribers": {
            "name": "WhatsApp Channel Members",
            "quality": "No Refill",
            "min": 100,
            "max": 50000,
            "price": 15000,
            "unit": "1k members",
            "service_id": "24362",
            "link_hint": "WhatsApp channel invite link"
        },
        "😀 Post EmojiReaction": {
            "name": "WhatsApp Channel EmojiReaction",
            "quality": "Mixed",
            "min": 10,
            "max": 50000,
            "price": 7000,
            "unit": "1k reactions",
            "service_id": "18840",
            "link_hint": "WhatsApp channel message link"
        }
    }
    
    service = services[message.text]

        # Check if the service is locked for non-admins
    locked_services = get_locked_services()
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
        process_whatsapp_quantity, 
        service
    )

def process_whatsapp_quantity(message, service):
    """Process WhatsApp order quantity"""
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    elif message.text == "⌫ ɢᴏ ʙᴀᴄᴋ":
        bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ WʜᴀᴛꜱAᴘᴘ ꜱᴇʀᴠɪᴄᴇꜱ...", reply_markup=whatsapp_services_markup)
        return
    
    try:
        quantity = int(message.text)
        if quantity < service['min']:
            bot.reply_to(message, f"❌ Mɪɴɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['min']}", reply_markup=whatsapp_services_markup)
            return
        if quantity > service['max']:
            bot.reply_to(message, f"❌ Mᴀxɪᴍᴜᴍ ᴏʀᴅᴇʀ ɪꜱ {service['max']}", reply_markup=whatsapp_services_markup)
            return
            
        cost = (quantity * service['price']) // 1000
        user_data = getData(str(message.from_user.id))
        
        if float(user_data['balance']) < cost:
            bot.reply_to(message, f"❌ Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ. Yᴏᴜ ɴᴇᴇᴅ {cost} ᴄᴏɪɴꜱ.", reply_markup=whatsapp_services_markup)
            return
            
        cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel_markup.add(KeyboardButton("✘ Cancel"))
        
        bot.reply_to(message, f"🔗 Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ {service['link_hint']}:", reply_markup=cancel_markup)
        bot.register_next_step_handler(
            message, 
            process_whatsapp_link, 
            service,
            quantity,
            cost
        )
        
    except ValueError:
        bot.reply_to(message, "❌ Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ", reply_markup=whatsapp_services_markup)

def process_whatsapp_link(message, service, quantity, cost):
    if message.text == "✘ Cancel":
        bot.reply_to(message, "❌ Oʀᴅᴇʀ ᴄᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)
        return
    
    link = message.text.strip()
    
    if not re.match(r'^https?://(chat\.whatsapp\.com|wa\.me)/', link):
        bot.reply_to(message, "❌ Iɴᴠᴀʟɪᴅ WʜᴀᴛꜱAᴘᴘ ʟɪɴᴋ ꜰᴏʀᴍᴀᴛ", reply_markup=whatsapp_services_markup)
    
    try:
        response = requests.post(
            SmmPanelApiUrl,
            data={
                'key': SmmPanelApi,
                'action': 'add',
                'service': service['service_id'],
                'link': link,
                'quantity': quantity
            },
            timeout=30
        )
        result = response.json()
        print(f"SMM Panel Response: {result}")  # Debug print
        
        if result and result.get('order'):
            # Deduct balance
            if not cutBalance(str(message.from_user.id), cost):
                raise Exception("Failed to deduct balance")
            
            # Prepare complete order data
            order_data = {
                'service': service['name'],
                'service_type': 'whatsapp',
                'service_id': service['service_id'],
                'quantity': quantity,
                'cost': cost,
                'link': link,
                'order_id': str(result['order']),
                'status': 'pending',
                'timestamp': time.time(),
                'username': message.from_user.username or str(message.from_user.id)
            }
            
            # Add to order history
            add_order(str(message.from_user.id), order_data)
            
            # Generate notification image
            try:
                image_path = create_order_notification(
                    bot=bot,
                    user_id=message.from_user.id,
                    user_name=message.from_user.first_name,
                    service_name=service['name']
                )
                
                if image_path:
                    # Create buttons
                    markup = InlineKeyboardMarkup()
                    markup.row(
                        InlineKeyboardButton("🔗 View Order Link", url=link),
                        InlineKeyboardButton("🤖 Visit Bot", url=f"https://t.me/{bot.get_me().username}")
                    )
                    
                    # Stylish notification to payment channel
                    caption = f"""⭐️ ｢ɴᴇᴡ ᴏʀᴅᴇʀ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
➠ 🕵🏻‍♂️ Uꜱᴇʀɴᴀᴍᴇ: @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Uꜱᴇʀ Iᴅ: {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 📦 Sᴇʀᴠɪᴄᴇ: {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🔢 Qᴜᴀɴᴛɪᴛʏ: {quantity}
━━━━━━━━━━━━━━━━━━━━━━━
➠ 💰 Cᴏꜱᴛ: {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
➠ 🆔 Oʀᴅᴇʀ Iᴅ: <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
➠ ⚡ Sᴛᴀᴛᴜꜱ: <code>{result.get('status', 'pending').capitalize()}</code>
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━"""
                    
                    with open(image_path, 'rb') as photo:
                        bot.send_photo(
                            PAYMENT_CHANNEL,
                            photo,
                            caption=caption,
                            parse_mode='HTML',
                            reply_markup=markup
                        )
                    
                    # Clean up
                    os.remove(image_path)
                    
            except Exception as e:
                print(f"Error generating notification image: {e}")
                # Fallback to text message if image generation fails
                bot.send_message(
                    PAYMENT_CHANNEL,
f"""⭐️ ｢Nᴇᴡ {service['name'].upper()} Oʀᴅᴇʀ 」⭐️
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━
👤 <b>Uꜱᴇʀ:</b> {message.from_user.first_name}
━━━━━━━━━━━━━━━━━━━━━━━
🕵🏻‍♂️ <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username or 'Not set'}
━━━━━━━━━━━━━━━━━━━━━━━
🆔 <b>Uꜱᴇʀ Iᴅ:</b> {message.from_user.id}
━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>Sᴇʀᴠɪᴄᴇ:</b> {service['name']}
━━━━━━━━━━━━━━━━━━━━━━━
🔢 <b>Qᴜᴀɴᴛɪᴛʏ:</b> {quantity}
💰 <b>Cᴏꜱᴛ:</b> {cost} ᴄᴏɪɴꜱ
━━━━━━━━━━━━━━━━━━━━━━━
📎 <b>Lɪɴᴋ:</b> {link}
🆔 <b>Oʀᴅᴇʀ ID:</b> <code>{result['order']}</code>
━━━━━━━━━━━━━━━━━━━━━━━
⚡ <b>Sᴛᴀᴛᴜꜱ:</b> <code>{result.get('status', 'pending').capitalize()}</code>
🤖 <b>Bᴏᴛ:</b> @{bot.get_me().username}
━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━""",
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )

            # Create "Check Order Status" button for user
            markup = InlineKeyboardMarkup()
            check_status_button = InlineKeyboardButton(
                text="📊 Check Order Status",
                url=f"https://t.me/{PAYMENT_CHANNEL.lstrip('@')}"
            )
            markup.add(check_status_button)
            
            # Stylish confirmation message
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
⚠️ <b>𝙒𝙖𝙧𝙣𝙞𝙣𝙜:</b> Dᴏ ɴᴏᴛ ꜱᴇɴᴅ ᴛʜᴇ ꜱᴀᴍᴇ ᴏʀᴅᴇʀ ᴏɴ ᴛʜᴇ ꜱᴀᴍᴇ ʟɪɴᴋ ʙᴇꜰᴏʀᴇ ᴛʜᴇ ꜰɪʀꜱᴛ ᴏɴᴇ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴏʀ ʏᴏᴜ ᴍɪɡʜᴛ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ꜱᴇʀᴠɪᴄᴇ!""",
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )
            
            # Update orders count
            user_id = str(message.from_user.id)
            data = getData(user_id)
            if 'orders_count' not in data:
                data['orders_count'] = 0
            data['orders_count'] += 1
            updateUser(user_id, data)

            # ✅ Affiliate Commission Tracking - USING GLOBAL FUNCTION
            if data.get('ref_by') and data['ref_by'] != "none":
                try:
                    commission = cost * 0.05  # 5% commission
                    add_affiliate_earning(data['ref_by'], commission)

                    # Use the global affiliate notification function
                    send_affiliate_notification(
                        bot=bot,
                        ref_by_user_id=data['ref_by'],
                        commission=commission,
                        customer_name=message.from_user.first_name,
                        service_name=service['name'],
                        order_cost=cost
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
        if 'result' not in locals() or not result.get('order'):
            bot.reply_to(
                message,
                f"❌ Fᴀɪʟᴇᴅ ᴛᴏ ꜱᴜʙᴍɪᴛ {service['name']} ᴏʀᴅᴇʀ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
                reply_markup=main_markup
            )
        else:
            bot.reply_to(
                message,
                f"⚠️ Oʀᴅᴇʀ ᴡᴀꜱ ꜱᴜʙᴍɪᴛᴛᴇᴅ (ID: {result['order']}) ʙᴜᴛ ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪꜱꜱᴜᴇ ᴡɪᴛʜ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ.",
                reply_markup=main_markup
            )
#======================== End of Whastapp Orders =====================#

#=================== The back button handler =========================================
@bot.message_handler(func=lambda message: message.text in ["⌫ ɢᴏ ʙᴀᴄᴋ", "✘ Cancel"])
def handle_back_buttons(message):
    """Handle all back/cancel buttons"""
    if message.text == "⌫ ɢᴏ ʙᴀᴄᴋ":
        # Determine where to go back based on context
        if message.text in ["👀 Order Views", "❤️ Order Reactions", "👥 Order Members"]:
            bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ Tᴏ Tᴇʟᴇɢʀᴀᴍ Sᴇʀᴠɪᴄᴇꜱ...", reply_markup=telegram_services_markup)
        elif message.text in ["👀 TikTok Views", "❤️ TikTok Likes", "👥 TikTok Followers"]:
            bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ Tᴏ Tɪᴋᴛᴏᴋ Sᴇʀᴠɪᴄᴇꜱ...", reply_markup=tiktok_services_markup)
        elif message.text in ["🎥 Insta Vid Views", "❤️ Insta Likes", "👥 Insta Followers"]:
            bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ Tᴏ Iɴꜱᴛᴀɢʀᴀᴍ Sᴇʀᴠɪᴄᴇꜱ...", reply_markup=instagram_services_markup)
        elif message.text in ["▶️ YT Views", "👍 YT Likes", "👥 YT Subscribers"]:
            bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ Tᴏ Yᴏᴜᴛᴜʙᴇ Sᴇʀᴠɪᴄᴇꜱ...", reply_markup=youtube_services_markup)
        elif message.text in ["👤 Profile Followers", "📄 Page Followers", "🎥 Video/Reel Views", "❤️ Post Likes"]:
            bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ Tᴏ Fᴀᴄᴇʙᴏᴏᴋ Sᴇʀᴠɪᴄᴇꜱ...", reply_markup=facebook_services_markup)
        elif message.text in ["👥 Channel Members", "😀 Channel EmojiReaction"]:
            bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ Tᴏ Wʜᴀꜱᴛᴀᴘᴘ Sᴇʀᴠɪᴄᴇꜱ...", reply_markup=whatsapp_services_markup)
        else:
            # Default back to Send Orders menu
            bot.reply_to(message, "Rᴇᴛᴜʀɴɪɴɢ Tᴏ Oʀᴅᴇʀ Oᴘᴛɪᴏɴꜱ...", reply_markup=send_orders_markup)
    else:
        # Cancel goes straight to main menu
        bot.reply_to(message, "Oᴘᴇʀᴀᴛɪᴏɴ Cᴀɴᴄᴇʟʟᴇᴅ.", reply_markup=main_markup)


#=================== The back button handler =========================================#
@bot.message_handler(func=lambda message: message.text == "⌫ ᴍᴀɪɴ ᴍᴇɴᴜ")
def back_to_main(message):
    if message.from_user.id in admin_user_ids:
        # For admins, show both admin and user keyboards
        combined_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        combined_markup.row("🆓 Free Services", "🛒 Buy Services")
        combined_markup.row("👤 My Account", "💳 Pricing")
        combined_markup.row("📊 Order Stats", "💰 Refer&Earn")
        combined_markup.row("🏆 Leaderboard", "🎉 Bᴏɴᴜs")
        combined_markup.row("📜 Help")

        bot.reply_to(message,
            "🔄 *Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ Mᴀɪɴ Mᴇɴᴜ*\n\n",
            parse_mode="Markdown",
            reply_markup=combined_markup)
    else:
        # For regular users, show normal keyboard
        bot.reply_to(message,
            "🔄 *Rᴇᴛᴜʀɴɪɴɢ ᴛᴏ Mᴀɪɴ Mᴇɴᴜ*",
            parse_mode="Markdown",
            reply_markup=main_markup)

#============================= Add and Remove Coins ==============================================#
@bot.message_handler(func=lambda message: message.text in ["➕ Add", "➖ Remove"] and message.from_user.id in admin_user_ids)
def admin_actions(message):
    """Enhanced admin command guidance for coins and affiliate cash"""
    if "Add" in message.text:
        bot.reply_to(message,
            "💎 *Aᴅᴅ Cᴏɪɴꜱ & Cᴀꜱʜ Gᴜɪᴅᴇ*\n\n"
            "📌 *To Add Coins:*\n"
            "▸ `/addcoins <user_id> <amount>`\n"
            "🧪 Example: `/addcoins 123456789 500.00`\n\n"
            "📌 *To Add Affiliate Cash:*\n"
            "▸ `/addcash <user_id> <amount>`\n"
            "🧪 Example: `/addcash 123456789 5.00`\n\n"
            "⚠️ Coins affect user balance. Cash affects affiliate earnings.",
            parse_mode="Markdown",
            reply_markup=ForceReply(selective=True))

    elif "Remove" in message.text:
        bot.reply_to(message,
            "⚡ *Rᴇᴍᴏᴠᴇ Cᴏɪɴꜱ & Cᴀꜱʜ Gᴜɪᴅᴇ*\n\n"
            "📌 *To Remove Coins:*\n"
            "▸ `/removecoins <user_id> <amount>`\n"
            "🧪 Example: `/removecoins 123456789 250.50`\n\n"
            "📌 *To Remove Affiliate Cash:*\n"
            "▸ `/removecash <user_id> <amount>`\n"
            "🧪 Example: `/removecash 123456789 3.00`\n\n"
            "⚠️ Use `/removecash` after a withdrawal is completed.",
            parse_mode="Markdown",
            reply_markup=ForceReply(selective=True))
        
    elif "Add Cash" in message.text:
        bot.reply_to(message,
            "💵 *Aᴅᴅ Aꜰꜰɪʟɪᴀᴛᴇ Cᴀꜱʜ Gᴜɪᴅᴇ*\n\n"
            "Cᴏᴍᴍᴀɴᴅ: `/addcash <user_id> <amount>`\n\n"
            "Exᴀᴍᴘʟᴇ:\n"
            "`/addcash 123456789 5.00`\n\n"
            "⚠️ Fᴏʀ ᴀᴅᴊᴜꜱᴛɪɴɢ ᴀꜰꜰɪʟɪᴀᴛᴇ ᴄᴏᴍᴍɪꜱꜱɪᴏɴꜱ",
            parse_mode="Markdown",
            reply_markup=ForceReply(selective=True))
    elif "Remove Cash" in message.text:
        bot.reply_to(message,
            "💸 *Rᴇᴍᴏᴠᴇ Aꜰꜰɪʟɪᴀᴛᴇ Cᴀꜱʜ Gᴜɪᴅᴇ*\n\n"
            "Cᴏᴍᴍᴀɴᴅ: `/removecash <user_id> <amount>`\n\n"
            "Exᴀᴍᴘʟᴇ:\n"
            "`/removecash 123456789 3.00`\n\n"
            "⚠️ Uꜱᴇ ᴛʜɪꜱ ᴀꜰᴛᴇʀ ᴡɪᴛʜᴅʀᴀᴡᴀʟ ᴄᴏɴꜰɪʀᴍᴀᴛɪᴏɴ",
            parse_mode="Markdown",
            reply_markup=ForceReply(selective=True))

@bot.message_handler(commands=['addcoins', 'removecoins'])
def handle_admin_commands(message):
    if message.from_user.id not in admin_user_ids:
        bot.reply_to(message, 
            "⛔ *Aᴅᴍɪɴ Aᴄᴄᴇꜱꜱ Dᴇɴɪᴇᴅ*\n\n"
            "Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ ᴛᴏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ꜱᴛᴀꜰꜰ ᴏɴʟʏ\n"
            "Uɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴀᴛᴛᴇᴍᴘᴛꜱ ᴀʀᴇ ʟᴏɢɢᴇᴅ",
            parse_mode="Markdown")
        return
    
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.reply_to(message,
"⚡ *Uꜱᴀɢᴇ Gᴜɪᴅᴇ*\n\n"
"▸ Aᴅᴅ ᴄᴏɪɴꜱ: `/addcoins <user_id> <amount>`\n"
"▸ Rᴇᴍᴏᴠᴇ ᴄᴏɪɴꜱ: `/removecoins <user_id> <amount>`\n\n"
"💡 Exᴀᴍᴘʟᴇ: `/addcoins 123456789 100.50`",
parse_mode="Markdown")
            return
            
        user_id = args[1]
        try:
            # Handle both integer and float inputs
            amount = float(args[2]) if '.' in args[2] else int(args[2])
            if amount <= 0:
                raise ValueError
        except ValueError:
            bot.reply_to(message,
"⚠️ *Iɴᴠᴀʟɪᴅ Aᴍᴏᴜɴᴛ*\n\n"
"Amount must be:\n"
"▸ A ᴘᴏꜱɪᴛɪᴠᴇ ɴᴜᴍʙᴇʀ\n"
"▸ Dᴇᴄɪᴍᴀʟ ᴠᴀʟᴜᴇꜱ ᴀʟʟᴏᴡᴇᴅ\n"
"▸ Mɪɴɪᴍᴜᴍ: 0.01",
parse_mode="Markdown")
            return
            
        if args[0] == '/addcoins':
            if not isExists(user_id):
                initial_data = {
                    "user_id": user_id,
                    "balance": 0.00,  # Changed from string to float
                    "ref_by": "none",
                    "referred": 0,
                    "welcome_bonus": 0,
                    "total_refs": 0,
                }
                insertUser(user_id, initial_data)
                
            if addBalance(user_id, amount):
                user_data = getData(user_id)
                new_balance = user_data.get('balance', 0) if user_data else 0
                
                bot.reply_to(message,
f"💎 *Cᴏɪɴꜱ Aᴅᴅᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ*\n\n"
f"▸ Uꜱᴇʀ ID: `{user_id}`\n"
f"▸ Aᴍᴏᴜɴᴛ: +{amount:.2f} ᴄᴏɪɴꜱ\n"
f"▸ Nᴇᴡ Bᴀʟᴀɴᴄᴇ: {new_balance:.2f}\n\n"
"📝 _Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ʟᴏɢɢᴇᴅ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ_",
parse_mode="Markdown")
                
                # Premium user notification
                try:
                    bot.send_message(
                        user_id,
f"🎉 *Aᴄᴄᴏᴜɴᴛ Cʀᴇᴅɪᴛᴇᴅ*\n\n"
f"Yᴏᴜʀ SMM Bᴏᴏꜱᴛᴇʀ ᴡᴀʟʟᴇᴛ ʜᴀꜱ ʙᴇᴇɴ ᴛᴏᴘᴘᴇᴅ ᴜᴘ!\n\n"
f"▸ Aᴍᴏᴜɴᴛ: +{amount:.2f} ᴄᴏɪɴꜱ\n"
f"▸ Nᴇᴡ Bᴀʟᴀɴᴄᴇ: {new_balance:.2f}\n"
f"▸ Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ID: {int(time.time())}\n\n"
"💎 Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʙᴇɪɴɢ ᴀ ᴠᴀʟᴜᴇᴅ ᴄᴜꜱᴛᴏᴍᴇʀ!",
parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton("🛍️ Shop Now", callback_data="show_send_orders")
                        )
                    )
                except Exception as e:
                    print(f"Credit notification failed: {e}")
            else:
                bot.reply_to(message,
"❌ *Tʀᴀɴꜱᴀᴄᴛɪᴏɴ Fᴀɪʟᴇᴅ*\n\n"
"Cᴏᴜʟᴅ ɴᴏᴛ ᴀᴅᴅ ᴄᴏɪɴꜱ ᴛᴏ ᴜꜱᴇʀ ᴀᴄᴄᴏᴜɴᴛ\n"
"Pᴏꜱꜱɪʙʟᴇ ʀᴇᴀꜱᴏɴꜱ:\n"
"▸ Dᴀᴛᴀʙᴀꜱᴇ ᴇʀʀᴏʀ\n"
"▸ Iɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ID",
parse_mode="Markdown")
                
        elif args[0] == '/removecoins':
            if cutBalance(user_id, amount):
                user_data = getData(user_id)
                new_balance = user_data.get('balance', 0) if user_data else 0
                
                bot.reply_to(message,
f"⚡ *Cᴏɪɴꜱ Dᴇᴅᴜᴄᴛᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ*\n\n"
f"▸ Uꜱᴇʀ ID: `{user_id}`\n"
f"▸ Aᴍᴏᴜɴᴛ: -{amount:.2f} ᴄᴏɪɴꜱ\n"
f"▸ Nᴇᴡ Bᴀʟᴀɴᴄᴇ: {new_balance:.2f}\n\n"
"📝 _Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ʟᴏɢɢᴇᴅ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ_",
parse_mode="Markdown")
                
                # Premium user notification
                try:
                    bot.send_message(
                        user_id,
f"🔔 *Aᴄᴄᴏᴜɴᴛ Dᴇʙɪᴛᴇᴅ*\n\n"
f"Cᴏɪɴꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴅᴇᴅᴜᴄᴛᴇᴅ ꜰʀᴏᴍ ʏᴏᴜʀ SMM Bᴏᴏꜱᴛᴇʀ ᴡᴀʟʟᴇᴛ\n\n"
f"▸ Aᴍᴏᴜɴᴛ: -{amount:.2f} ᴄᴏɪɴꜱ\n"
f"▸ Nᴇᴡ Bᴀʟᴀɴᴄᴇ: {new_balance:.2f}\n"
f"▸ Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ID: {int(time.time())}\n\n"
"⚠️ Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ ɪꜰ ᴛʜɪꜱ ᴡᴀꜱ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ",
parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton("📩 Contact Support", url="https://t.me/SocialHubBoosterTMbot")
                        )
                    )
                except Exception as e:
                    print(f"Debit notification failed: {e}")
            else:
                bot.reply_to(message,
"❌ *Tʀᴀɴꜱᴀᴄᴛɪᴏɴ Fᴀɪʟᴇᴅ*\n\n"
"Cᴏᴜʟᴅ ɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴄᴏɪɴꜱ ꜰʀᴏᴍ ᴜꜱᴇʀ ᴀᴄᴄᴏᴜɴᴛ\n"
"Pᴏꜱꜱɪʙʟᴇ ʀᴇᴀꜱᴏɴꜱ:\n"
"▸ Iɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ\n"
"▸ Iɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ID\n"
"▸ Dᴀᴛᴀʙᴀꜱᴇ ᴇʀʀᴏʀ",
parse_mode="Markdown")
                
    except Exception as e:
        bot.reply_to(message,
            f"⚠️ *System Error*\n\n"
            f"Command failed: {str(e)}\n\n"
            "Please try again or contact developer",
            parse_mode="Markdown")
        print(f"Admin command error: {traceback.format_exc()}")

@bot.message_handler(commands=['addcash', 'removecash'])
def handle_cash_commands(message):
    if message.from_user.id not in admin_user_ids:
        return bot.reply_to(message, "⛔ *Aᴅᴍɪɴ Aᴄᴄᴇꜱꜱ Dᴇɴɪᴇᴅ*", parse_mode="Markdown")

    try:
        args = message.text.split()
        if len(args) != 3:
            return bot.reply_to(message,
                "💡 *Uꜱᴀɢᴇ:*\n"
                "`/addcash <user_id> <amount>`\n"
                "`/removecash <user_id> <amount>`",
                parse_mode="Markdown")

        user_id = args[1]
        amount = float(args[2])

        if amount <= 0:
            return bot.reply_to(message, "⚠️ Aᴍᴏᴜɴᴛ ᴍᴜꜱᴛ ʙᴇ ᴀ ᴘᴏꜱɪᴛɪᴠᴇ ɴᴜᴍʙᴇʀ", parse_mode="Markdown")

        is_removal = message.text.startswith("/removecash")
        tx_id = int(time.time())

        if update_affiliate_earning(user_id, amount, subtract=is_removal, admin_id=message.from_user.id):
            new_data = getData(user_id)
            current = float(new_data.get("affiliate_earnings", 0.0))

            bot.reply_to(message,
f"{'💸 *Cᴀꜱʜ Dᴇᴅᴜᴄᴛɪᴏɴ*' if is_removal else '💵 *Cᴀꜱʜ Cʀᴇᴅɪᴛᴇᴅ*'}\n\n"
f"▸ *Uꜱᴇʀ ID:* `{user_id}`\n"
f"▸ *Aᴍᴏᴜɴᴛ:* {'-' if is_removal else '+'}UGX{amount:.2f}\n"
f"▸ *Nᴇᴡ Aꜰꜰɪʟɪᴀᴛᴇ Bᴀʟᴀɴᴄᴇ:* UGX{current:.2f}\n"
f"▸ *Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ID:* `{tx_id}`\n\n"
"📝 _Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ʟᴏɢɢᴇᴅ ɪɴ ᴄᴀꜱʜ ʜɪꜱᴛᴏʀʏ_",
            parse_mode="Markdown")

            try:
                bot.send_message(
                    user_id,
f"{'🔻 *Aꜰꜰɪʟɪᴀᴛᴇ Wɪᴛʜᴅʀᴀᴡᴀʟ Pʀᴏᴄᴇꜱꜱᴇᴅ*' if is_removal else '💰 *Aꜰꜰɪʟɪᴀᴛᴇ Eᴀʀɴɪɴɢ Cʀᴇᴅɪᴛᴇᴅ*'}\n\n"
f"{'🧾 Yᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ᴡɪᴛʜᴅʀᴀᴡᴀʟ ʜᴀꜱ ʙᴇᴇɴ ᴘʀᴏᴄᴇꜱꜱᴇᴅ.' if is_removal else '🎉 Yᴏᴜ’ᴠᴇ ʀᴇᴄᴇɪᴠᴇᴅ ᴀ ᴄᴀꜱʜ ʙᴏɴᴜꜱ ꜰʀᴏᴍ ᴀᴅᴍɪɴ!'}\n\n"
f"▸ *Aᴍᴏᴜɴᴛ:* {'-' if is_removal else '+'}UGX{amount:.2f}\n"
f"▸ *Nᴇᴡ Bᴀʟᴀɴᴄᴇ:* UGX{current:.2f}\n"
f"▸ *Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ID:* `{tx_id}`\n\n"
"📌 _Yᴏᴜʀ ᴇᴀʀɴɪɴɢꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜᴘᴅᴀᴛᴇᴅ_",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("📊 View Earnings", callback_data="affiliate_stats")
                    )
                )
            except Exception as e:
                print(f"Affiliate notification failed: {e}")

        else:
            bot.reply_to(message, "❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴜᴘᴅᴀᴛᴇ ᴀꜰꜰɪʟɪᴀᴛᴇ ʙᴀʟᴀɴᴄᴇ", parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ *Eʀʀᴏʀ:* `{str(e)}`", parse_mode="Markdown")



#=========================== End of Add and Remove Coins =================================#

#=========================== Batch Coin Commands =================================#
@bot.message_handler(func=lambda m: m.text == "📦 Batch Coins")
def show_batch_coins_help(message):
    if message.from_user.id not in admin_user_ids:
        return
    bot.reply_to(message,
        "🧮 *Bᴀᴛᴄʜ Cᴏɪɴꜱ Pᴀɴᴇʟ*\n\n"
        "Uꜱᴇ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅꜱ ᴛᴏ ᴀᴅᴅ ᴏʀ ʀᴇᴍᴏᴠᴇ ᴄᴏɪɴꜱ ꜰᴏʀ ᴀʟʟ ᴜꜱᴇʀꜱ:\n\n"
        "▸ `/alladdcoins <amount>`\n"
        "▸ `/allremovecoins <amount>`\n\n"
        "⚠️ *Nᴏᴛᴇ:* Aʟʟ ᴜꜱᴇʀꜱ ᴡɪʟʟ ʙᴇ ɴᴏᴛɪꜰɪᴇᴅ.",
        parse_mode="Markdown")

@bot.message_handler(commands=['alladdcoins', 'allremovecoins'])
def handle_batch_coins(message):
    if message.from_user.id not in admin_user_ids:
        bot.reply_to(message,
            "⛔ *Aᴅᴍɪɴ Aᴄᴄᴇꜱꜱ Dᴇɴɪᴇᴅ*\n\n"
            "Tʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ ᴛᴏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ꜱᴛᴀꜰꜰ ᴏɴʟʏ\n"
            "Uɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴀᴛᴛᴇᴍᴘᴛꜱ ᴀʀᴇ ʟᴏɢɢᴇᴅ",
            parse_mode="Markdown")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message,
"⚡ *Uꜱᴀɢᴇ Gᴜɪᴅᴇ*\n\n"
"▸ Aᴅᴅ ᴄᴏɪɴꜱ: `/alladdcoins <amount>`\n"
"▸ Rᴇᴍᴏᴠᴇ ᴄᴏɪɴꜱ: `/allremovecoins <amount>`\n\n"
"💡 Exᴀᴍᴘʟᴇ: `/alladdcoins 100`",
            parse_mode="Markdown")
        return

    try:
        amount = float(args[1]) if '.' in args[1] else int(args[1])
        if amount <= 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message,
"⚠️ *Iɴᴠᴀʟɪᴅ Aᴍᴏᴜɴᴛ*\n\n"
"Amount must be:\n"
"▸ A positive number\n"
"▸ Decimal values allowed\n"
"▸ Minimum: 0.01",
            parse_mode="Markdown")
        return

    users = get_all_users()
    success = 0
    failed = 0

    for uid in users:
        try:
            if args[0] == '/alladdcoins':
                if addBalance(uid, amount):
                    data = getData(uid)
                    bot.send_message(
                        uid,
f"🎉 *Aᴄᴄᴏᴜɴᴛ Cʀᴇᴅɪᴛᴇᴅ*\n\n"
f"Yᴏᴜʀ SMM Bᴏᴏꜱᴛᴇʀ ᴡᴀʟʟᴇᴛ ʜᴀꜱ ʙᴇᴇɴ ᴛᴏᴘᴘᴇᴅ ᴜᴘ!\n\n"
f"▸ Aᴍᴏᴜɴᴛ: +{amount:.2f} ᴄᴏɪɴꜱ\n"
f"▸ Nᴇᴡ Bᴀʟᴀɴᴄᴇ: {data['balance']:.2f}\n"
f"▸ Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ID: {int(time.time())}\n\n"
"💎 Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʙᴇɪɴɢ ᴀ ᴠᴀʟᴜᴇᴅ ᴄᴜꜱᴛᴏᴍᴇʀ!",
                        parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton("🛍️ Shop Now", callback_data="show_send_orders")
                        )
                    )
                    success += 1
                else:
                    failed += 1
            elif args[0] == '/allremovecoins':
                if cutBalance(uid, amount):
                    data = getData(uid)
                    bot.send_message(
                        uid,
                    f"🔔 *ACCOUNT DEBITED*\n\n"
                    f"Cᴏɪɴꜱ ʜᴀᴠᴇ ʙᴇᴇɴ Dᴇᴅᴜᴄᴛᴇᴅ ꜰʀᴏᴍ ʏᴏᴜʀ Sᴍᴍ Bᴏᴏꜱᴛᴇʀ Wᴀʟʟᴇᴛ\n\n"
                    f"▸ Aᴍᴏᴜɴᴛ: -{amount:.2f} coins\n"
                    f"▸ Nᴇᴡ Bᴀʟᴀɴᴄᴇ: {data['balance']:.2f}\n"
                    f"▸ Tʀᴀɴꜱᴀᴄᴛɪᴏɴ ID: {int(time.time())}\n\n"
                    "⚠️ Cᴏɴᴛᴀᴄᴛ Sᴜᴘᴘᴏʀᴛ ɪꜰ ᴛʜɪꜱ ᴡᴀꜱ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("📩 Contact Support", url="https://t.me/SocialHubBoosterTMbot")
                        )
                    )
                    success += 1
                else:
                    failed += 1
        except Exception as e:
            print(f"Batch update failed for {uid}: {e}")
            failed += 1

    bot.reply_to(message,
        f"📊 *Bᴀᴛᴄʜ Oᴘᴇʀᴀᴛɪᴏɴ Cᴏᴍᴘʟᴇᴛᴇᴅ*\n\n"
        f"✅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟ: {success}\n"
        f"❌ Fᴀɪʟᴇᴅ: {failed}",
        parse_mode="Markdown")

#=============================== Admin Stats Command =====================================#
@bot.message_handler(func=lambda m: m.text == "📊 Analytics" and m.from_user.id in admin_user_ids)
def show_analytics(message):
    """Show comprehensive bot analytics with multi-page dashboard"""
    try:
        # Store the original message ID if this is a new request
        if not hasattr(message, 'is_callback'):
            message.original_message_id = message.message_id + 1  # Next message will be +1
            
        show_users_stats(message)
        
    except Exception as e:
        print(f"Analytics error: {e}")
        bot.reply_to(message, 
"⚠️ <b>Aɴᴀʟʏᴛɪᴄꜱ Dᴀꜱʜʙᴏᴀʀᴅ Uɴᴀᴠᴀɪʟᴀʙʟᴇ</b>\n\n"
"Our ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴛʀɪᴄꜱ ꜱʏꜱᴛᴇᴍ ɪꜱ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴏꜰꜰʟɪɴᴇ\n"
"Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ",
            parse_mode='HTML')

def show_users_stats(message, is_refresh=False):
    """Show users statistics page"""
    try:
        # Get user stats
        total_users = get_user_count()
        active_users = get_active_users(7)
        new_users_24h = get_new_users(1)
        banned_users = len(get_banned_users())
        deleted_users = get_deleted_users_count()
        
        # Get referral stats
        top_referrer = get_top_referrer()
        total_referrals = get_total_referrals()
        
        # Format top referrer
        if top_referrer['user_id']:
            username = f"@{top_referrer['username']}" if top_referrer['username'] else f"User {top_referrer['user_id']}"
            referrer_display = f"🏆 {username} (Invited {top_referrer['count']} users)"
        else:
            referrer_display = "📭 No referrals yet"

        # Create users stats page
        msg = f"""
<blockquote>
📊 <b>Uꜱᴇʀꜱ Aɴᴀʟʏᴛɪᴄꜱ  Rᴇᴘᴏʀᴛ</b>
━━━━━━━━━━━━━━━━━━━━

👥 <b>Uꜱᴇʀ Sᴛᴀᴛɪꜱᴛɪᴄꜱ</b>
├ Tᴏᴛᴀʟ Uꜱᴇʀꜱ: <code>{total_users}</code>
├ Aᴄᴛɪᴠᴇ (7ᴅ): <code>{active_users}</code>
├ Nᴇᴡ (24ʜ): <code>{new_users_24h}</code>
├ Bᴀɴɴᴇᴅ Uꜱᴇʀꜱ: <code>{banned_users}</code>
└ Dᴇʟᴇᴛᴇᴅ ᴜꜱᴇʀꜱ: <code>{deleted_users}</code>

🔗 <b>Rᴇꜰᴇʀʀᴀʟ Pʀᴏɢʀᴀᴍ</b>
└ {referrer_display}
└ Tᴏᴛᴀʟ Rᴇꜰᴇʀʀᴀʟꜱ: <code>{total_referrals}</code>

📅 Gᴇɴᴇʀᴀᴛᴇᴅ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
</blockquote>
"""
        
        # Create navigation buttons
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🛒 Orders Stats", callback_data="orders_stats"),
            InlineKeyboardButton("💰 Finance Stats", callback_data="finance_stats")
        )
        markup.row(
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_users_stats"),
            InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")  
        )

        if hasattr(message, 'is_callback') or is_refresh:
            # Edit existing message
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=msg,
                parse_mode='HTML',
                reply_markup=markup
            )
        else:
            # Send new message
            sent_msg = bot.send_message(
                message.chat.id,
                msg,
                parse_mode='HTML',
                reply_markup=markup
            )
            message.original_message_id = sent_msg.message_id
        
    except Exception as e:
        print(f"Users stats error: {e}")

def show_orders_stats(message):
    """Show orders statistics page"""
    try:
        # Get order stats
        total_orders = get_total_orders()
        completed_orders = get_completed_orders()
        
        # Get free orders stats
        free_orders_daily = get_free_orders_count(1)   # Daily
        free_orders_weekly = get_free_orders_count(7)  # Weekly
        free_orders_monthly = get_free_orders_count(30) # Monthly
        
        # Get premium orders stats
        premium_orders_daily = get_premium_orders_count(1)   # Daily
        premium_orders_weekly = get_premium_orders_count(7)  # Weekly
        premium_orders_monthly = get_premium_orders_count(30) # Monthly
        
        # Calculate conversion rates
        conversion_rate = (completed_orders/total_orders)*100 if total_orders > 0 else 0

        # Create orders stats page
        msg = f"""
<blockquote>
📊 <b>Oʀᴅᴇʀꜱ Aɴᴀʟʏᴛɪᴄꜱ  Rᴇᴘᴏʀᴛ</b>
━━━━━━━━━━━━━━━━━━━━

🛒 <b>Oʀᴅᴇʀ Mᴇᴛʀɪᴄꜱ</b>
├ Tᴏᴛᴀʟ Oʀᴅᴇʀꜱ: <code>{total_orders}</code>
├ Cᴏᴍᴘʟᴇᴛᴇᴅ: <code>{completed_orders}</code>
└ Cᴏɴᴠᴇʀꜱɪᴏɴ Rᴀᴛᴇ: <code>{conversion_rate:.1f}%</code>

💎 <b>Pʀᴇᴍɪᴜᴍ Oʀᴅᴇʀꜱ</b>
▫️ Dᴀɪʟʏ: <code>{premium_orders_daily}</code>
▫️ Wᴇᴇᴋʟʏ: <code>{premium_orders_weekly}</code>
▫️ Mᴏɴᴛʜʟʏ: <code>{premium_orders_monthly}</code>

🆓 <b>Fʀᴇᴇ Oʀᴅᴇʀꜱ</b>
▫️ Dᴀɪʟʏ: <code>{free_orders_daily}</code>
▫️ Wᴇᴇᴋʟʏ: <code>{free_orders_weekly}</code>
▫️ Mᴏɴᴛʜʟʏ: <code>{free_orders_monthly}</code>

📅 Gᴇɴᴇʀᴀᴛᴇᴅ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
</blockquote>
"""
        
        # Create navigation buttons
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("👥 Users Stats", callback_data="users_stats"),
            InlineKeyboardButton("💰 Finance Stats", callback_data="finance_stats")
        )
        markup.row(
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_orders_stats"),
            InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")  
        )

        # Edit existing message
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=msg,
            parse_mode='HTML',
            reply_markup=markup
        )
        
    except Exception as e:
        print(f"Orders stats error: {e}")

def show_finance_stats(message):
    """Show financial statistics page"""
    try:
        # Get financial stats
        total_users = get_user_count()
        total_orders = get_total_orders()
        total_deposits = get_total_deposits()
        
        # Get order costs
        free_orders_cost = get_free_orders_cost()        # Total cost of all free orders
        premium_orders_cost = get_premium_orders_cost()  # Total cost of all premium orders
        total_orders_cost = free_orders_cost + premium_orders_cost
        
        # Calculate averages
        avg_order_value = total_deposits / total_orders if total_orders > 0 else 0
        avg_deposit_per_user = total_deposits / total_users if total_users > 0 else 0

        # Create finance stats page
        msg = f"""
<blockquote>
💰 <b>Fɪɴᴀɴᴄɪᴀʟꜱ Aɴᴀʟʏᴛɪᴄꜱ  Rᴇᴘᴏʀᴛ</b>
━━━━━━━━━━━━━━━━━━━━

▫️ Tᴏᴛᴀʟ Dᴇᴘᴏꜱɪᴛꜱ: <code>{total_deposits:.2f}</code> ᴄᴏɪɴꜱ
▫️ Aᴠɢ Oʀᴅᴇʀ Vᴀʟᴜᴇ: <code>{avg_order_value:.2f}</code> ᴄᴏɪɴꜱ
▫️ ꜰʀᴇᴇ ᴏʀᴅᴇʀꜱ ᴄᴏꜱᴛ: <code>{free_orders_cost:.2f}</code> ᴄᴏɪɴꜱ
▫️ ᴘʀᴇᴍɪᴜᴍ ᴏʀᴅᴇʀꜱ ᴄᴏꜱᴛ: <code>{premium_orders_cost:.2f}</code> ᴄᴏɪɴꜱ
▫️ ᴛᴏᴛᴀʟ ᴏʀᴅᴇʀꜱ ᴄᴏꜱᴛ: <code>{total_orders_cost:.2f}</code> ᴄᴏɪɴꜱ
▫️ Aᴠɢ Dᴇᴘᴏꜱɪᴛ/Uꜱᴇʀ: <code>{avg_deposit_per_user:.2f}</code> ᴄᴏɪɴꜱ

📅 Gᴇɴᴇʀᴀᴛᴇᴅ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
</blockquote>
"""
        
        # Create navigation buttons
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("👥 Users Stats", callback_data="users_stats"),
            InlineKeyboardButton("🛒 Orders Stats", callback_data="orders_stats")
        )
        markup.row(
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_finance_stats"),
            InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")  
        )

        # Edit existing message
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=msg,
            parse_mode='HTML',
            reply_markup=markup
        )
        
    except Exception as e:
        print(f"Finance stats error: {e}")

# Handle Refresh buttons
@bot.callback_query_handler(func=lambda call: call.data in ["refresh_users_stats", "refresh_orders_stats", "refresh_finance_stats"])
def handle_refresh_stats(call):
    try:
        call.message.is_callback = True
        
        if call.data == "refresh_users_stats":
            show_users_stats(call.message, is_refresh=True)
        elif call.data == "refresh_orders_stats":
            show_orders_stats(call.message)
        elif call.data == "refresh_finance_stats":
            show_finance_stats(call.message)
            
        bot.answer_callback_query(call.id, "🔄 Data refreshed")
    except Exception as e:
        print(f"Error refreshing stats: {e}")
        bot.answer_callback_query(call.id, "⚠️ Failed to refresh", show_alert=True)

# Handle Navigation buttons
@bot.callback_query_handler(func=lambda call: call.data in ["users_stats", "orders_stats", "finance_stats"])
def handle_stats_navigation(call):
    try:
        call.message.is_callback = True
        
        if call.data == "users_stats":
            show_users_stats(call.message)
        elif call.data == "orders_stats":
            show_orders_stats(call.message)
        elif call.data == "finance_stats":
            show_finance_stats(call.message)
            
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Error navigating stats: {e}")
        bot.answer_callback_query(call.id, "⚠️ Failed to navigate", show_alert=True)

# =========================== Enhanced Broadcast Command ================= #
@bot.message_handler(func=lambda m: m.text == "📤 Broadcast" and m.from_user.id in admin_user_ids)
def broadcast_start(message):
    """Start normal broadcast process (unpinned)"""
    # Create cancel button markup
    cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cancel_markup.add(KeyboardButton("✘ Cᴀɴᴄᴇʟ"))
    
    msg = bot.reply_to(message, 
                      "📢 ✨ <b>Cᴏᴍᴘᴏꜱᴇ Yᴏᴜʀ Bʀᴏᴀᴅᴄᴀꜱᴛ Mᴇꜱꜱᴀɢᴇ</b> ✨\n\n"
                      "Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ʏᴏᴜ'ᴅ ʟɪᴋᴇ ᴛᴏ ꜱᴇɴᴅ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ.\n"
                      "Tʜɪꜱ ᴡɪʟʟ ʙᴇ ꜱᴇɴᴛ ᴀꜱ ᴀ ʀᴇɢᴜʟᴀʀ (ᴜɴᴘɪɴɴᴇᴅ) ᴍᴇꜱꜱᴀɢᴇ.\n\n"
                      "🖋️ Yᴏᴜ ᴄᴀɴ ɪɴᴄʟᴜᴅᴇ ᴛᴇxᴛ, ᴘʜᴏᴛᴏꜱ, ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛꜱ.\n"
                      "❌ Cʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴀɴᴄᴇʟ:", 
                      parse_mode="HTML",
                      reply_markup=cancel_markup)
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    """Process the broadcast message and ask for confirmation"""
    if message.text and message.text.strip() == "✘ Cᴀɴᴄᴇʟ":
        bot.reply_to(message, "🛑 <b>Broadcast cancelled.</b>", 
                     parse_mode="HTML", reply_markup=admin_markup)
        return
    
    users = get_all_users()
    if not users:
        bot.reply_to(message, "❌ No users found to broadcast to", reply_markup=admin_markup)
        return
    
    # Generate broadcast ID
    from functions import generate_broadcast_id
    broadcast_id = generate_broadcast_id()
    
    # Store the message for confirmation
    broadcast_data = {
        'message_obj': message,
        'total_users': len(users),
        'broadcast_id': broadcast_id
    }
    
    # Create confirmation buttons
    confirm_markup = InlineKeyboardMarkup()
    confirm_markup.row(
        InlineKeyboardButton("✅ Sᴇɴᴅ Bʀᴏᴀᴅᴄᴀꜱᴛ", callback_data="confirm_broadcast"),
        InlineKeyboardButton("❌ Cᴀɴᴄᴇʟ", callback_data="cancel_broadcast")
    )
    
    # Show preview and confirmation
    try:
        # Forward the message to show preview
        preview_msg = bot.forward_message(message.chat.id, message.chat.id, message.message_id)
        
        confirmation_text = f"""📢 <b>Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏɴꜰɪʀᴍᴀᴛɪᴏɴ</b>

🆔 <b>Broadcast ID:</b> <code>{broadcast_id}</code>
👥 <b>Tᴏᴛᴀʟ Rᴇᴄɪᴘɪᴇɴᴛꜱ:</b> <code>{len(users)}</code>
📊 <b>Mᴇꜱꜱᴀɢᴇ Tʏᴘᴇ:</b> {'Text' if message.text else 'Media'}

🔍 <b>Pʀᴇᴠɪᴇᴡ ᴀʙᴏᴠᴇ</b> - ᴛʜɪꜱ ɪꜱ ʜᴏᴡ ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ᴀᴘᴘᴇᴀʀ

💡 <b>Note:</b> You can delete this broadcast later using the ID above
⚠️ <b>Aʀᴇ ʏᴏᴜ ꜱᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ꜱᴇɴᴅ ᴛʜɪꜱ ʙʀᴏᴀᴅᴄᴀꜱᴛ?</b>"""

        bot.send_message(
            message.chat.id,
            confirmation_text,
            parse_mode="HTML",
            reply_markup=confirm_markup,
            reply_to_message_id=preview_msg.message_id
        )
        
        # Store broadcast data for callback
        bot.current_broadcast_data = broadcast_data
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error processing message: {str(e)}", reply_markup=admin_markup)

@bot.callback_query_handler(func=lambda call: call.data in ["confirm_broadcast", "cancel_broadcast"])
def handle_broadcast_confirmation(call):
    """Handle broadcast confirmation or cancellation"""
    try:
        if call.data == "cancel_broadcast":
            bot.answer_callback_query(call.id, "❌ Bʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ")
            bot.edit_message_text(
                "🛑 <b>Broadcast Cancelled</b>\n\n"
                "Tʜᴇ ʙʀᴏᴀᴅᴄᴀꜱᴛ ʜᴀꜱ ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )
            return
        
        if call.data == "confirm_broadcast":
            bot.answer_callback_query(call.id, "📤 Sᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀꜱᴛ...")
            
            # Get the stored broadcast data
            if not hasattr(bot, 'current_broadcast_data'):
                bot.answer_callback_query(call.id, "❌ Bʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴀᴛᴀ ɴᴏᴛ ꜰᴏᴜɴᴅ", show_alert=True)
                return
            
            broadcast_data = bot.current_broadcast_data
            message = broadcast_data['message_obj']
            users = get_all_users()
            broadcast_id = broadcast_data['broadcast_id']
            
            # Update message to show processing
            bot.edit_message_text(
                f"⏳ <b>Starting Broadcast...</b>\n\n"
                f"🆔 <b>Broadcast ID:</b> <code>{broadcast_id}</code>\n"
                f"👥 <b>Total Users:</b> <code>{len(users)}</code>\n\n"
                f"🔄 Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴡʜɪʟᴇ ᴡᴇ ꜱᴇɴᴅ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ...",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )
            
            # Start the actual broadcast
            send_broadcast_message(bot, message, users, call.message, broadcast_id)
            
            # Clear the stored data
            delattr(bot, 'current_broadcast_data')
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Eʀʀᴏʀ: {str(e)}", show_alert=True)

def send_broadcast_message(bot, message, users, progress_message, broadcast_id):
    """Send the actual broadcast message to all users and track message IDs"""
    from functions import save_broadcast, save_user_message_id
    
    success = 0
    failed = 0
    blocked = 0
    deleted = 0
    not_found = 0
    bot_users = 0
    
    # Save broadcast to database first
    message_data = {
        'message_id': message.message_id,
        'chat_id': message.chat.id,
        'content_type': 'text' if message.text else 'media',
        'content': message.text if message.text else 'media_content'
    }
    
    save_broadcast(broadcast_id, message_data, len(users), 0, message.from_user.id)
    
    # Enhanced sending notification with progress bar concept
    progress_msg = progress_message
    
    # Calculate update interval (at least 1)
    update_interval = max(1, len(users) // 10)
    start_time = time.time()
    
    for index, user_id in enumerate(users):
        try:
            # Use copy_message to preserve all Telegram formatting exactly as sent
            sent_message = bot.copy_message(user_id, message.chat.id, message.message_id)
            
            # Save the message ID for this user
            save_user_message_id(broadcast_id, user_id, sent_message.message_id)
            success += 1
            
        except Exception as e:
            error_msg = str(e).lower()
            if "blocked" in error_msg or "user is blocked" in error_msg:
                blocked += 1
            elif "deleted" in error_msg or "peer id invalid" in error_msg:
                deleted += 1
            elif "chat not found" in error_msg or "bad request" in error_msg:
                not_found += 1
            elif "bots can't send messages to bots" in error_msg:
                bot_users += 1
            else:
                failed += 1
            logger.error(f"Failed to send to {user_id}: {e}")
        
        # Update progress periodically
        if (index+1) % update_interval == 0 or index+1 == len(users):
            progress = int((index+1)/len(users)*100)
            progress_bar = '█' * (progress//10) + '░' * (10 - progress//10)
            try:
                bot.edit_message_text(f"""📨 <b>Bʀᴏᴀᴅᴄᴀꜱᴛ Pʀᴏɢʀᴇꜱꜱ</b>
                
🆔 <b>Broadcast ID:</b> <code>{broadcast_id}</code>
📊 Tᴏᴛᴀʟ Rᴇᴄɪᴘɪᴇɴᴛꜱ: <code>{len(users)}</code>
✅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟ: <code>{success}</code>
🚫 Bʟᴏᴄᴋᴇᴅ: <code>{blocked}</code>
🗑️ Dᴇʟᴇᴛᴇᴅ: <code>{deleted}</code>
🔍 Nᴏᴛ Fᴏᴜɴᴅ: <code>{not_found}</code>
🤖 Bᴏᴛ Usᴇʀs: <code>{bot_users}</code>
❌ Fᴀɪʟᴇᴅ: <code>{failed}</code>
⏳ Sᴛᴀᴛᴜꜱ: <i>Sᴇɴᴅɪɴɢ...</i>

[{progress_bar}] {progress}%""", 
                    progress_message.chat.id, progress_message.message_id, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Failed to update progress: {e}")
        
        time.sleep(0.1)  # Rate limiting
    
    # Calculate time taken
    elapsed_time = int(time.time() - start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    if minutes > 0:
        time_taken = f"{minutes}m {seconds}s"
    else:
        time_taken = f"{seconds}s"
    
    # Enhanced completion message
    completion_text = f"""📣 <b>Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>

🆔 <b>Broadcast ID:</b> <code>{broadcast_id}</code>

📊 <b>Sᴛᴀᴛɪꜱᴛɪᴄꜱ:</b>
├ 📤 <i>Sᴇɴᴛ:</i> <code>{success}</code>
├ 🚫 <i>Bʟᴏᴄᴋᴇᴅ:</i> <code>{blocked}</code>
├ 🗑️ <i>Dᴇʟᴇᴛᴇᴅ:</i> <code>{deleted}</code>
├ 🔍 <i>Nᴏᴛ Fᴏᴜɴᴅ:</i> <code>{not_found}</code>
├ 🤖 <i>Bᴏᴛ Usᴇʀs:</i> <code>{bot_users}</code>
└ ❌ <i>Fᴀɪʟᴇᴅ:</i> <code>{failed}</code>

⏱️ <i>Tɪᴍᴇ ᴛᴀᴋᴇɴ:</i> <code>{time_taken}</code>
⏰ <i>Fɪɴɪꜱʜᴇᴅ ᴀᴛ:</i> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>

💡 <b>Note:</b> Use the Broadcast ID above to delete this message later if needed.

✨ <i>Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱʏꜱᴛᴇᴍ!</i>"""

    try:
        bot.edit_message_text(completion_text, 
                            progress_message.chat.id, progress_message.message_id, 
                            parse_mode="HTML")
    except:
        bot.send_message(progress_message.chat.id, completion_text, parse_mode="HTML", reply_markup=admin_markup)
# ============================= Enhanced Ban User Command ============================= #
@bot.message_handler(func=lambda m: m.text == "🔒 Ban User" and m.from_user.id in admin_user_ids)
def ban_user_start(message):
    """Start ban user process"""
    msg = bot.reply_to(message, 
        "⚡ *SMM Aᴅᴍɪɴ Pᴀɴᴇʟ - Bᴀɴ Uꜱᴇʀ*\n\n"
        "Eɴᴛᴇʀ Uꜱᴇʀ Iᴅ Tᴏ Bᴀɴ:\n"
        "▸ *Fᴏʀᴍᴀᴛ*: `123456789`\n"
        "▸ *Nᴏᴛᴇ*: Uꜱᴇʀ ᴡɪʟʟ ʟᴏꜱᴇ ᴀʟʟ ꜱᴇʀᴠɪᴄᴇ ᴀᴄᴄᴇꜱꜱ\n\n"
        "✘ Tʏᴘᴇ *'Cᴀɴᴄᴇʟ'* ᴛᴏ ᴀʙᴏʀᴛ",
        parse_mode="Markdown",
        reply_markup=ForceReply(selective=True))
    bot.register_next_step_handler(msg, process_ban_user)

def process_ban_user(message):
    """Ban a user with enhanced features"""
    if message.text == "Cancel":
        bot.reply_to(message, "❌ Ban cancelled.", reply_markup=admin_markup)
        return
    
    user_id = message.text.strip()
    
    if not user_id.isdigit():
        bot.reply_to(message, 
            "❌ *Iɴᴠᴀʟɪᴅ Iɴᴘᴜᴛ*\n"
            "Uꜱᴇʀ Iᴅ ᴍᴜꜱᴛ ᴄᴏɴᴛᴀɪɴ ᴏɴʟʏ ɴᴜᴍʙᴇʀꜱ\n"
            "Exᴀᴍᴘʟᴇ: `123456789`",
            parse_mode="Markdown",
            reply_markup=admin_markup)
        return
    
    if is_banned(user_id):
        bot.reply_to(message, 
            "⚠️ *User Already Banned*\n"
            f"User `{user_id}` is already in ban list",
            parse_mode="Markdown",
            reply_markup=admin_markup)
        return
    
    ban_user(user_id)
    
    # Enhanced ban notification to user
    try:
        appeal_markup = InlineKeyboardMarkup()
        appeal_markup.row(
            InlineKeyboardButton("📩 Appeal Ban", url="https://t.me/SocialHubBoosterTMbot"),
            InlineKeyboardButton("📋 View Terms", callback_data="ban_terms")
        )

        
        bot.send_message(
            user_id,
            f"⛔ *ACCOUNT SUSPENDED*\n\n"
f"⛔ *Aᴄᴄᴏᴜɴᴛ Sᴜꜱᴘᴇɴᴅᴇᴅ*\n\n"
f"Yᴏᴜʀ ᴀᴄᴄᴇꜱꜱ ᴛᴏ *SMM Bᴏᴏꜱᴛᴇʀ* ꜱᴇʀᴠɪᴄᴇꜱ ʜᴀꜱ ʙᴇᴇɴ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ.\n\n"
f"▸ *Rᴇᴀꜱᴏɴ*: Vɪᴏʟᴀᴛɪᴏɴ ᴏꜰ Tᴇʀᴍꜱ\n"
f"▸ *Aᴘᴘᴇᴀʟ*: Aᴠᴀɪʟᴀʙʟᴇ ᴠɪᴀ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ\n"
f"▸ *Sᴛᴀᴛᴜꜱ*: Pᴇʀᴍᴀɴᴇɴᴛ (ᴜɴᴛɪʟ ᴀᴘᴘᴇᴀʟ)\n\n"
f"⚠️ Aᴛᴛᴇᴍᴘᴛɪɴɢ ᴛᴏ ʙʏᴘᴀꜱꜱ ᴡɪʟʟ ʀᴇꜱᴜʟᴛ ɪɴ IP ʙʟᴀᴄᴋʟɪꜱᴛ",
parse_mode="Markdown",
reply_markup=appeal_markup
        )
        notified_success = True
    except Exception as e:
        print(f"Ban notification error: {e}")
        notified_success = False
    
    # Enhanced admin confirmation
    bot.reply_to(message,
    f"✅ *Uꜱᴇʀ Bᴀɴɴᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ*\n\n"
    f"▸ Uꜱᴇʀ Iᴅ: `{user_id}`\n"
    f"▸ Aᴄᴛɪᴏɴ: Fᴜʟʟ ꜱᴇʀᴠɪᴄᴇ ʀᴇꜱᴛʀɪᴄᴛɪᴏɴ\n"
    f"▸ Nᴏᴛɪꜰɪᴇᴅ: {'Yᴇꜱ' if notified_success else 'Fᴀɪʟᴇᴅ'}\n\n"
    f"📝 _Tʜɪꜱ ᴜꜱᴇʀ ʜᴀꜱ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ʙᴀɴ ᴅᴀᴛᴀʙᴀꜱᴇ_",
    parse_mode="Markdown",
    reply_markup=admin_markup)

# Add this callback handler for the terms button 
@bot.callback_query_handler(func=lambda call: call.data == "ban_terms")
def show_ban_terms(call):
    """Show the policy message when View Terms is clicked"""
    try:
        # Get the policy message from the policy_command function
        policy_text = """
<blockquote>
📜 <b>🤖 Bᴏᴛ Uꜱᴀɢᴇ Pᴏʟɪᴄʏ & Gᴜɪᴅᴇʟɪɴᴇꜱ</b> 📜
━━━━━━━━━━━━━━━━━━━━

🔹 <b>1. Aᴄᴄᴇᴘᴛᴀʙʟᴇ Uꜱᴇ</b>
   ├ ✅ Pᴇʀᴍɪᴛᴛᴇᴅ: Lᴇɢᴀʟ, ɴᴏɴ-ʜᴀʀᴍꜰᴜʟ ᴄᴏɴᴛᴇɴᴛ
   └ ❌ Pʀᴏʜɪʙɪᴛᴇᴅ: Sᴘᴀᴍ, ʜᴀʀᴀꜱꜱᴍᴇɴᴛ, ɪʟʟᴇɢᴀʟ ᴍᴀᴛᴇʀɪᴀʟ

🔹 <b>2. Fᴀɪʀ Uꜱᴀɢᴇ Pᴏʟɪᴄʏ</b>
   ├ ⚖️ Aʙᴜꜱᴇ ᴍᴀʏ ʟᴇᴀᴅ ᴛᴏ ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ
   └ 📊 Exᴄᴇꜱꜱɪᴠᴇ ᴜꜱᴀɢᴇ ᴍᴀʏ ʙᴇ ʀᴀᴛᴇ-ʟɪᴍɪᴛᴇᴅ

🔹 <b>3. Fɪɴᴀɴᴄɪᴀʟ Pᴏʟɪᴄʏ</b>
   ├ 💳 Aʟʟ ᴛʀᴀɴꜱᴀᴄᴛɪᴏɴꜱ ᴀʀᴇ ꜰɪɴᴀʟ
   └ 🔄 Nᴏ ʀᴇꜰᴜɴᴅꜱ ꜰᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ꜱᴇʀᴠɪᴄᴇꜱ

🔹 <b>4. Pʀɪᴠᴀᴄʏ Cᴏᴍᴍɪᴛᴍᴇɴᴛ</b>
   ├ 🔒 Yᴏᴜʀ ᴅᴀᴛᴀ ꜱᴛᴀʏꜱ ᴄᴏɴꜰɪᴅᴇɴᴛɪᴀʟ
   └ 🤝 Nᴇᴠᴇʀ ꜱʜᴀʀᴇᴅ ᴡɪᴛʜ ᴛʜɪʀᴅ ᴘᴀʀᴛɪᴇꜱ

🔹 <b>5. Pʟᴀᴛꜰᴏʀᴍ Cᴏᴍᴘʟɪᴀɴᴄᴇ</b>
   ├ ✋ Mᴜꜱᴛ ꜰᴏʟʟᴏᴡ Tᴇʟᴇɢʀᴀᴍ'ꜱ TᴏS
   └ 🌐 Aʟʟ ᴄᴏɴᴛᴇɴᴛ ᴍᴜꜱᴛ ʙᴇ ʟᴇɢᴀʟ ɪɴ ʏᴏᴜʀ ᴊᴜʀɪꜱᴅɪᴄᴛɪᴏɴ

⚠️ <b>CᴏɴꜱᴇQᴜᴇɴᴄᴇꜱ ᴏꜰ Vɪᴏʟᴀᴛɪᴏɴ</b>
   ├ ⚠️ Fɪʀꜱᴛ ᴏꜰꜰᴇɴꜱᴇ: Wᴀʀɴɪɴɢ
   ├ 🔇 Rᴇᴘᴇᴀᴛᴇᴅ ᴠɪᴏʟᴀᴛɪᴏɴꜱ: Tᴇᴍᴘᴏʀᴀʀʏ ꜱᴜꜱᴘᴇɴꜱɪᴏɴ
   └ 🚫 Sᴇᴠᴇʀᴇ ᴄᴀꜱᴇꜱ: Pᴇʀᴍᴀɴᴇɴᴛ ʙᴀɴ

📅 <i>Lᴀꜱᴛ ᴜᴘᴅᴀᴛᴇᴅ: {update_date}</i>
━━━━━━━━━━━━━━━━━━━━
💡 Nᴇᴇᴅ ʜᴇʟᴘ? Cᴏɴᴛᴀᴄᴛ @SocialHubBoosterTMbot
</blockquote>
""".format(update_date=datetime.now().strftime('%Y-%m-%d'))

        
        # Answer the callback first
        bot.answer_callback_query(call.id)
        
        # Send the policy message
        bot.send_message(
            call.message.chat.id,
            policy_text,
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Error showing ban terms: {e}")
        bot.answer_callback_query(call.id, "⚠️ Failed to load terms", show_alert=True)
    

# ============================= Premium Unban Command ============================= #
@bot.message_handler(func=lambda m: m.text == "✅ Unban User" and m.from_user.id in admin_user_ids)
def unban_user_start(message):
    """Start unban user process"""
    msg = bot.reply_to(message,
"⚡ *SMM Aᴅᴍɪɴ Pᴀɴᴇʟ - Uɴʙᴀɴ Uꜱᴇʀ*\n\n"
"Eɴᴛᴇʀ Uꜱᴇʀ Iᴅ Tᴏ Uɴʙᴀɴ:\n"
"▸ Wɪʟʟ ʀᴇꜱᴛᴏʀᴇ ᴀʟʟ ꜱᴇʀᴠɪᴄᴇꜱ\n"
"▸ Aᴜᴛᴏᴍᴀᴛɪᴄ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ ꜱᴇɴᴛ\n\n"
"✘ Tʏᴘᴇ *'Cancel'* ᴛᴏ ᴀʙᴏʀᴛ",
        parse_mode="Markdown",
        reply_markup=ForceReply(selective=True))
    bot.register_next_step_handler(msg, process_unban_user)

def process_unban_user(message):
    """Unban a user with premium features"""
    if message.text == "Cancel":
        bot.reply_to(message, "❌ Unban cancelled.", reply_markup=admin_markup)
        return
    
    user_id = message.text.strip()
    
    if not user_id.isdigit():
        bot.reply_to(message,
            "❌ *Iɴᴠᴀʟɪᴅ Iɴᴘᴜᴛ*\n"
            "Uꜱᴇʀ Iᴅ ᴍᴜꜱᴛ ᴄᴏɴᴛᴀɪɴ ᴏɴʟʏ Nᴜᴍʙᴇʀꜱ\n"
            "Exᴀᴍᴘʟᴇ: `987654321`",
            parse_mode="Markdown",
            reply_markup=admin_markup)
        return
    
    if not is_banned(user_id):
        bot.reply_to(message,
            f"ℹ️ *User Not Banned*\n"
            f"User `{user_id}` isn't in ban records",
            parse_mode="Markdown",
            reply_markup=admin_markup)
        return
    
    unban_user(user_id)
    
    # Premium unban notification
    try:
        markup = InlineKeyboardMarkup()
        # Changed callback_data to trigger the send_orders_menu directly
        markup.add(InlineKeyboardButton("🛒 Return to Services", callback_data="show_send_orders"))
        
        bot.send_message(
            user_id,
            f"✅ *Aᴄᴄᴏᴜɴᴛ Rᴇɪɴꜱᴛᴀᴛᴇᴅ*\n\n"
            f"Yᴏᴜʀ *SMM Bᴏᴏꜱᴛᴇʀ* ᴀᴄᴄᴇꜱꜱ ʜᴀꜱ ʙᴇᴇɴ ʀᴇꜱᴛᴏʀᴇᴅ!\n\n"
            f"▸ Aʟʟ ꜱᴇʀᴠɪᴄᴇꜱ: Rᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ\n"
            f"▸ Oʀᴅᴇʀ ʜɪꜱᴛᴏʀʏ: Pʀᴇꜱᴇʀᴠᴇᴅ\n"
            f"▸ Bᴀʟᴀɴᴄᴇ: Uɴᴀꜰꜰᴇᴄᴛᴇᴅ\n\n"
            f"⚠️ Pʟᴇᴀꜱᴇ ʀᴇᴠɪᴇᴡ ᴏᴜʀ ᴛᴇʀᴍꜱ ᴛᴏ ᴀᴠᴏɪᴅ ꜰᴜᴛᴜʀᴇ ɪꜱꜱᴜᴇꜱ",
            parse_mode="Markdown",
            reply_markup=markup
        )
        notified_success = True
    except Exception as e:
        print(f"Unban notification error: {e}")
        notified_success = False
    
    # Admin confirmation with flair
    bot.reply_to(message,
        f"✨ *Uꜱᴇʀ Uɴʙᴀɴɴᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ*\n\n"
        f"▸ Uꜱᴇʀ Iᴅ: `{user_id}`\n"
        f"▸ Sᴇʀᴠɪᴄᴇꜱ: Rᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ\n"
        f"▸ Nᴏᴛɪꜰɪᴇᴅ: {'Yᴇꜱ' if notified_success else 'Fᴀɪʟᴇᴅ'}\n\n"
        f"📝 _Rᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ʙᴀɴ ᴅᴀᴛᴀʙᴀꜱᴇ_",
        parse_mode="Markdown",
        reply_markup=admin_markup)

# Add this new handler for showing send orders menu
@bot.callback_query_handler(func=lambda call: call.data == "show_send_orders")
def show_send_orders_menu(call):
    """Show the send orders menu when 'Return to Services' is clicked"""
    try:
        # Delete the unban notification message
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
            
        # Show the send orders menu
        bot.send_message(
            call.message.chat.id,
            "📤 Sᴇʟᴇᴄᴛ Pʟᴀᴛꜰᴏʀᴍ Tᴏ Sᴇɴᴅ Oʀᴅᴇʀꜱ:",
            reply_markup=send_orders_markup
        )
        
        # Answer the callback
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Error showing send orders menu: {e}")
        bot.answer_callback_query(call.id, "⚠️ Failed to load services", show_alert=True)

# ============================= VIP Banned Users List ============================= #
@bot.message_handler(func=lambda m: m.text == "📋 List Banned" and m.from_user.id in admin_user_ids)
def list_banned(message):
    """Show paginated list of banned users"""
    banned_users = get_banned_users()
    
    if not banned_users:
        # Create close button for empty list
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_ban_list"))
        
        bot.send_message(message.chat.id,
            "🛡️ <b>Bᴀɴ Lɪꜱᴛ Sᴛᴀᴛᴜꜱ</b>\n\n"
            "Nᴏ ᴜꜱᴇʀꜱ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ\n\n"
            "▸ Dᴀᴛᴀʙᴀꜱᴇ: 0 Entries\n"
            "▸ Lᴀꜱᴛ ʙᴀɴ: None",
            parse_mode="HTML",
            reply_markup=markup)
        return
    
    show_banned_page(message, banned_users, page=0)

def show_banned_page(message, banned_users, page=0):
    """Show a page of banned users"""
    PAGE_SIZE = 5
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_users = banned_users[start_idx:end_idx]
    
    # Create quoted style content
    inner_list = ""
    for i, user_id in enumerate(page_users, start_idx + 1):
        try:
            user = bot.get_chat(user_id)
            name = user.first_name or f"User {user_id}"
            inner_list += f"{i}. {name} (`{user_id}`)\n"
        except:
            inner_list += f"{i}. User `{user_id}`\n"
    
    quoted_content = f"<blockquote><b>{inner_list}</b></blockquote>"
    
    msg = f"""<b>⛔ Bᴀɴɴᴇᴅ Usᴇʀꜱ Lɪꜱᴛ</b>

📊 Tᴏᴛᴀʟ Bᴀɴɴᴇᴅ: <code>{len(banned_users)}</code>
📄 Pᴀɢᴇ: <code>{page + 1}/{(len(banned_users) + PAGE_SIZE - 1) // PAGE_SIZE}</code>
⏰ Lᴀꜱᴛ Uᴘᴅᴀᴛᴇᴅ: <code>{datetime.now().strftime('%Y-%m-%d %H:%M')}</code>

{quoted_content}"""

    # Create pagination buttons
    markup = InlineKeyboardMarkup()
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⌫ ʙᴀᴄᴋ", callback_data=f"ban_page_{page-1}"))
    
    if end_idx < len(banned_users):
        nav_buttons.append(InlineKeyboardButton("ɴᴇxᴛ ⌦", callback_data=f"ban_page_{page+1}"))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    markup.row(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_ban_list"))
    
    bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ban_page_") or call.data == "close_ban_list")
def handle_ban_pagination(call):
    """Handle banned users pagination"""
    if call.data == "close_ban_list":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    try:
        page = int(call.data.split("_")[-1])
        banned_users = get_banned_users()
        
        if not banned_users:
            bot.answer_callback_query(call.id, "No banned users found", show_alert=True)
            return
        
        show_banned_page(call.message, banned_users, page)
        bot.answer_callback_query(call.id)
    except:
        bot.answer_callback_query(call.id, "Error loading page", show_alert=True)

# ============================= Premium Leaderboard ============================= #
@bot.message_handler(func=lambda m: m.text == "🏆 Leaderboard")
def show_leaderboard(message):
    """Show VIP leaderboard with pagination"""
    top_users = get_top_users(limit=50)
    
    if not top_users:
        # Create close button for empty leaderboard
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_leaderboard"))
        
        bot.send_message(message.chat.id,
            "🌟 <b>SMM Bᴏᴏꜱᴛᴇʀ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ</b>\n\n"
            "Nᴏ ᴏʀᴅᴇʀ ᴅᴀᴛᴀ ᴀᴠᴀɪʟᴀʙʟᴇ ʏᴇᴛ\n\n"
            "Bᴇ ᴛʜᴇ ꜰɪʀꜱᴛ ᴛᴏ ᴀᴘᴘᴇᴀʀ ʜᴇʀᴇ!",
            parse_mode="HTML",
            reply_markup=markup)
        return
    
    show_leaderboard_page(message, top_users, page=0)

def show_leaderboard_page(message, top_users, page=0):
    """Show a page of leaderboard"""
    PAGE_SIZE = 10
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_users = top_users[start_idx:end_idx]
    
    # Medal emojis for ranking
    medal_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    # Create quoted style content
    inner_list = ""
    for i, (user_id, count) in enumerate(page_users, start_idx + 1):
        try:
            user = bot.get_chat(user_id)
            name = user.first_name or f"User {user_id}"
            emoji = medal_emoji[i-1] if i <= len(medal_emoji) else "🔹"
            inner_list += f"{emoji} {name}: <b>{count}</b> orders\n"
        except:
            emoji = medal_emoji[i-1] if i <= len(medal_emoji) else "🔹"
            inner_list += f"{emoji} User {user_id}: <b>{count}</b> orders\n"
    
    quoted_content = f"<blockquote>{inner_list}</blockquote>"
    
    msg = f"""<b>🏆 SMM Bᴏᴏꜱᴛᴇʀ Tᴏᴘ Cʟɪᴇɴᴛꜱ</b>

📊 Rᴀɴᴋᴇᴅ ʙʏ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴏʀᴅᴇʀꜱ
📄 Pᴀɢᴇ: <code>{page + 1}/{(len(top_users) + PAGE_SIZE - 1) // PAGE_SIZE}</code>
👥 Tᴏᴛᴀʟ Tᴏᴘ Usᴇʀꜱ: <code>{len(top_users)}</code>

{quoted_content}

💎 <i>Vɪᴘ Bᴇɴᴇꜰɪᴛꜱ Aᴠᴀɪʟᴀʙʟᴇ - Tᴏᴘ 3 ɢᴇᴛ ᴍᴏɴᴛʜʟʏ ʙᴏɴᴜꜱᴇꜱ!</i>"""

    # Create pagination buttons
    markup = InlineKeyboardMarkup()
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⌫ ʙᴀᴄᴋ", callback_data=f"leader_page_{page-1}"))
    
    if end_idx < len(top_users):
        nav_buttons.append(InlineKeyboardButton("ɴᴇxᴛ ⌦", callback_data=f"leader_page_{page+1}"))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    markup.row(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_leaderboard"))
    
    # Check if we're editing an existing message or sending a new one
    if hasattr(message, 'message_id') and hasattr(message, 'from_user'):
        # This is a callback query - edit the existing message
        try:
            bot.edit_message_text(
                msg,
                chat_id=message.chat.id,
                message_id=message.message_id,
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception as e:
            logger.error(f"Failed to edit message, sending new one: {e}")
            bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=markup)
    else:
        # This is a new message - send it
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("leader_page_") or call.data == "close_leaderboard")
def handle_leaderboard_pagination(call):
    """Handle leaderboard pagination"""
    if call.data == "close_leaderboard":
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.answer_callback_query(call.id)
        return
    
    try:
        page = int(call.data.split("_")[-1])
        top_users = get_top_users(limit=50)
        
        if not top_users:
            bot.answer_callback_query(call.id, "No leaderboard data found", show_alert=True)
            return
        
        # Pass the callback message to edit the existing message
        show_leaderboard_page(call.message, top_users, page)
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Error in leaderboard pagination: {e}")
        bot.answer_callback_query(call.id, "Error loading page", show_alert=True)

#======================= Function to Pin Annoucement Messages ====================#
@bot.message_handler(func=lambda m: m.text == "📌 Pin Message" and m.from_user.id in admin_user_ids)
def pin_message_start(message):
    """Start pin message process"""
    # Create cancel button markup
    cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cancel_markup.add(KeyboardButton("✘ Cᴀɴᴄᴇʟ"))
    
    msg = bot.reply_to(message, 
                      "📌 ✨ <b>Sᴇɴᴅ Yᴏᴜʀ Pɪɴɴᴇᴅ Mᴇꜱꜱᴀɢᴇ</b> ✨\n\n"
                      "Pʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴘɪɴ ɪɴ ᴀʟʟ ᴜꜱᴇʀꜱ' ᴄʜᴀᴛꜱ.\n\n"
                      "🖋️ Yᴏᴜ ᴄᴀɴ ꜱᴇɴᴅ ᴛᴇxᴛ, ᴘʜᴏᴛᴏꜱ, ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛꜱ.\n"
                      "❌ Cʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴀɴᴄᴇʟ:",
                      parse_mode="HTML",
                      reply_markup=cancel_markup)
    bot.register_next_step_handler(msg, process_pin_message)

def process_pin_message(message):
    """Process and send the pinned message to all users"""
    if message.text and message.text.strip() == "✘ Cᴀɴᴄᴇʟ":
        bot.reply_to(message, "🛑 <b>Pin cancelled.</b>", 
                     parse_mode="HTML", reply_markup=admin_markup)
        return
    
    users = get_all_users()
    success, failed, blocked, deleted, not_found = 0, 0, 0, 0, 0
    
    # Progress message
    progress_msg = bot.reply_to(message, f"""📨 <b>Pɪɴɴɪɴɢ Mᴇꜱꜱᴀɢᴇꜱ</b>
    
📊 Tᴏᴛᴀʟ Usᴇʀs: <code>{len(users)}</code>
⏳ Sᴛᴀᴛᴜꜱ: <i>Processing...</i>

[░░░░░░░░░░] 0%""", parse_mode="HTML")
    
    update_interval = max(1, len(users) // 10)
    start_time = time.time()
    
    for index, user_id in enumerate(users):
        try:
            # Use copy_message to preserve all Telegram formatting
            sent = bot.copy_message(user_id, message.chat.id, message.message_id)
            
            # Pin the message
            bot.pin_chat_message(user_id, sent.message_id)
            save_pinned_message(user_id, sent.message_id)  # Save in MongoDB
            success += 1
            
        except Exception as e:
            error_msg = str(e).lower()
            if "blocked" in error_msg or "user is blocked" in error_msg:
                blocked += 1
            elif "deleted" in error_msg or "peer id invalid" in error_msg:
                deleted += 1
            elif "chat not found" in error_msg or "bad request" in error_msg:
                not_found += 1
            else:
                failed += 1
            logger.error(f"Error pinning for {user_id}: {e}")
        
        # Update progress
        if (index+1) % update_interval == 0 or index+1 == len(users):
            progress = int((index+1)/len(users)*100)
            progress_bar = '█' * (progress//10) + '░' * (10 - progress//10)
            try:
                bot.edit_message_text(f"""📨 <b>Pɪɴɴɪɴɢ Pʀᴏɢʀᴇꜱꜱ</b>
                
📊 Tᴏᴛᴀʟ Usᴇʀs: <code>{len(users)}</code>
✅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟ: <code>{success}</code>
🚫 Bʟᴏᴄᴋᴇᴅ: <code>{blocked}</code>
🗑️ Dᴇʟᴇᴛᴇᴅ: <code>{deleted}</code>
🔍 Nᴏᴛ Fᴏᴜɴᴅ: <code>{not_found}</code>
❌ Fᴀɪʟᴇᴅ: <code>{failed}</code>
⏳ Sᴛᴀᴛᴜꜱ: <i>Pɪɴɴɪɴɢ...</i>

[{progress_bar}] {progress}%""", 
                    message.chat.id, progress_msg.message_id, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Failed to update progress: {e}")
        
        time.sleep(0.1)

    # Calculate time taken
    elapsed_time = int(time.time() - start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    time_taken = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
    
    completion_text = f"""📌 <b>Pɪɴɴɪɴɢ Cᴏᴍᴘʟᴇᴛᴇᴅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>

📊 <b>Sᴛᴀᴛɪꜱᴛɪᴄꜱ:</b>
├ 📌 <i>Pɪɴɴᴇᴅ:</i> <code>{success}</code>
├ 🚫 <i>Bʟᴏᴄᴋᴇᴅ:</i> <code>{blocked}</code>
├ 🗑️ <i>Dᴇʟᴇᴛᴇᴅ:</i> <code>{deleted}</code>
├ 🔍 <i>Nᴏᴛ Fᴏᴜɴᴅ:</i> <code>{not_found}</code>
└ ❌ <i>Fᴀɪʟᴇᴅ:</i> <code>{failed}</code>

⏱️ <i>Tɪᴍᴇ ᴛᴀᴋᴇɴ:</i> <code>{time_taken}</code>
⏰ <i>Fɪɴɪꜱʜᴇᴅ ᴀᴛ:</i> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>

✨ <i>Mᴇꜱꜱᴀɢᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴘɪɴɴᴇᴅ!</i>"""

    try:
        bot.edit_message_text(completion_text, 
                            message.chat.id, progress_msg.message_id, 
                            parse_mode="HTML")
    except:
        bot.reply_to(message, completion_text, parse_mode="HTML", reply_markup=admin_markup)

# ========================= UNPIN Button Handler ================================================#
@bot.message_handler(func=lambda m: m.text == "📍 Unpin" and m.from_user.id in admin_user_ids)
def unpin_and_delete_all(message):
    """Unpin and delete pinned messages for all users"""
    
    # Create inline keyboard for confirmation
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ ᴄᴏɴꜰɪʀᴍ ᴜɴᴘɪɴ", callback_data="confirm_unpin_all"),
        InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_unpin")
    )
    
    bot.reply_to(
        message,
        "📍 <b>Uɴᴘɪɴ Aʟʟ Mᴇꜱꜱᴀɢᴇꜱ</b>\n\n"
        "⚠️ <b>Yᴏᴜ ᴀʀᴇ ᴀʙᴏᴜᴛ ᴛᴏ:</b>\n"
        "• Unpin messages from ALL users\n"
        "• Delete pinned messages\n"
        "• Clear from database\n\n"
        "🔴 <b>This action cannot be undone!</b>\n\n"
        "➤ Click the button below to confirm:",
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["confirm_unpin_all", "cancel_unpin"])
def handle_unpin_confirmation(call):
    """Handle unpin confirmation via inline buttons"""
    if call.data == "cancel_unpin":
        bot.answer_callback_query(call.id, "❌ Unpin cancelled")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    
    if call.data == "confirm_unpin_all":
        bot.answer_callback_query(call.id, "⏳ Starting unpin process...")
        
        # Update message to show processing
        bot.edit_message_text(
            "⏳ <b>Uɴᴘɪɴɴɪɴɢ Mᴇꜱꜱᴀɢᴇꜱ...</b>\n\n"
            "🔄 Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴡʜɪʟᴇ ᴡᴇ ᴜɴᴘɪɴ ᴀʟʟ ᴍᴇꜱꜱᴀɢᴇꜱ...",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        users_pins = get_all_pinned_messages()
        success, failed, blocked, deleted, not_found = 0, 0, 0, 0, 0
        
        total_users = len(users_pins)
        if total_users == 0:
            bot.edit_message_text(
                "ℹ️ <b>Nᴏ Pɪɴɴᴇᴅ Mᴇꜱꜱᴀɢᴇꜱ Fᴏᴜɴᴅ</b>\n\n"
                "There are no pinned messages to unpin.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML"
            )
            return
        
        start_time = time.time()
        
        for index, (user_id, message_id) in enumerate(users_pins.items()):
            try:
                bot.unpin_chat_message(user_id, message_id=message_id)
                bot.delete_message(user_id, message_id)
                success += 1
            except Exception as e:
                error_msg = str(e).lower()
                if "blocked" in error_msg or "user is blocked" in error_msg:
                    blocked += 1
                elif "deleted" in error_msg or "peer id invalid" in error_msg:
                    deleted += 1
                elif "chat not found" in error_msg or "bad request" in error_msg:
                    not_found += 1
                else:
                    failed += 1
                logger.error(f"Error unpinning for {user_id}: {e}")
            
            # Update progress every 10 users or at the end
            if (index+1) % 10 == 0 or index+1 == total_users:
                progress = int((index+1)/total_users*100)
                progress_bar = '█' * (progress//10) + '░' * (10 - progress//10)
                try:
                    bot.edit_message_text(f"""⏳ <b>Uɴᴘɪɴɴɪɴɢ Pʀᴏɢʀᴇꜱꜱ</b>
                    
📊 Tᴏᴛᴀʟ Pɪɴɴᴇᴅ: <code>{total_users}</code>
✅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟ: <code>{success}</code>
🚫 Bʟᴏᴄᴋᴇᴅ: <code>{blocked}</code>
🗑️ Dᴇʟᴇᴛᴇᴅ: <code>{deleted}</code>
🔍 Nᴏᴛ Fᴏᴜɴᴅ: <code>{not_found}</code>
❌ Fᴀɪʟᴇᴅ: <code>{failed}</code>
⏳ Sᴛᴀᴛᴜꜱ: <i>Uɴᴘɪɴɴɪɴɢ...</i>

[{progress_bar}] {progress}%""", 
                        call.message.chat.id, call.message.message_id, parse_mode="HTML")
                except:
                    pass
            
            time.sleep(0.1)
        
        clear_all_pinned_messages()  # Clear from MongoDB
        
        # Calculate time taken
        elapsed_time = int(time.time() - start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_taken = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
        
        completion_text = f"""📍 <b>Uɴᴘɪɴɴɪɴɢ Cᴏᴍᴘʟᴇᴛᴇᴅ!</b>

📊 <b>Sᴛᴀᴛɪꜱᴛɪᴄꜱ:</b>
├ 📌 <i>Uɴᴘɪɴɴᴇᴅ:</i> <code>{success}</code>
├ 🚫 <i>Bʟᴏᴄᴋᴇᴅ:</i> <code>{blocked}</code>
├ 🗑️ <i>Dᴇʟᴇᴛᴇᴅ:</i> <code>{deleted}</code>
├ 🔍 <i>Nᴏᴛ Fᴏᴜɴᴅ:</i> <code>{not_found}</code>
└ ❌ <i>Fᴀɪʟᴇᴅ:</i> <code>{failed}</code>

⏱️ <i>Tɪᴍᴇ ᴛᴀᴋᴇɴ:</i> <code>{time_taken}</code>
⏰ <i>Fɪɴɪꜱʜᴇᴅ ᴀᴛ:</i> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>

✨ <i>Aʟʟ ᴍᴇꜱꜱᴀɢᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴᴘɪɴɴᴇᴅ ᴀɴᴅ ᴅᴇʟᴇᴛᴇᴅ!</i>"""
        
        bot.edit_message_text(
            completion_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )

#================= Check User Info by ID ===================================#
@bot.message_handler(func=lambda m: m.text == "👤 User Info" and m.from_user.id in admin_user_ids)
def user_info_start(message):
    msg = bot.reply_to(message, "Enter user ID or username (@username):")
    bot.register_next_step_handler(msg, process_user_info)

def process_user_info(message):
    query = message.text.strip()
    try:
        if query.startswith('@'):
            user = bot.get_chat(query)
            user_id = user.id
        else:
            user_id = int(query)
            user = bot.get_chat(user_id)
        
        user_data = getData(user_id) or {}
        
        info = f"""
<blockquote>
┌──────────────────────
│ 🔍 <b>𝗨𝘀𝗲𝗿 𝗜𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝗼𝗻</b>:
│ ━━━━━━━━━━━━━━━━━━━━━━
│ 🆔 Iᴅ: <code>{user_id}</code>
│ 👤 Nᴀᴍᴇ: {user.first_name} {user.last_name or ''}
│ 📛 Uꜱᴇʀɴᴀᴍᴇ: @{user.username if user.username else 'N/A'}
│ 💰 Bᴀʟᴀɴᴄᴇ: {user_data.get('balance', 0)}
│ 📊 Oʀᴅᴇʀꜱ: {user_data.get('orders_count', 0)}
│ 👥 Rᴇꜰᴇʀʀᴀʟꜱ: {user_data.get('total_refs', 0)}
│ 🔨 Sᴛᴀᴛᴜꜱ: {"BANNED ⛔" if is_banned(user_id) else "ACTIVE ✅"}
└─────────────────────
</blockquote>
        """
        
        # Add close button
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button"))
        
        bot.reply_to(message, info, parse_mode="HTML", reply_markup=markup)
    except ValueError:
        bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ. ᴍᴜꜱᴛ ʙᴇ ɴᴜᴍᴇʀɪᴄ.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

#============================== Server Status Command ===============================#
@bot.message_handler(func=lambda m: m.text == "🖥 Server Status" and m.from_user.id in admin_user_ids)
def server_status(message):
    try:
        import psutil, platform
        from datetime import datetime
        from functions import db
        
        # System info
        uname = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        # Memory info
        mem = psutil.virtual_memory()
        
        # Disk info
        disk = psutil.disk_usage('/')
        
        # MongoDB stats
        mongo_stats = db.command("dbstats")
        
        status = f"""
<blockquote>
┌─────────────────────
│ 🖥 <b>𝙎𝙮𝙨𝙩𝙚𝙢 𝙎𝙩𝙖𝙩𝙪𝙨</b>
│ ━━━━━━━━━━━━━━━━━━━━━━
│ 💻 <b>Sʏꜱᴛᴇᴍ</b>: {uname.system} {uname.release}
│ ⏱ <b>Uᴘᴛɪᴍᴇ</b>: {datetime.now() - boot_time}
│ ━━━━━━━━━━━━━━━━━━━━━━
│ 🧠 <b>Cᴘᴜ</b>: {psutil.cpu_percent()}% usage
│ 💾 <b>Mᴇᴍᴏʀʏ</b>: {mem.used/1024/1024:.1f}MB / {mem.total/1024/1024:.1f}MB
│ 🗄 <b>Dɪꜱᴋ</b>: {disk.used/1024/1024:.1f}MB / {disk.total/1024/1024:.1f}MB
│ ━━━━━━━━━━━━━━━━━━━━━━
│ 📊 <b>𝙈𝙤𝙣𝙜𝙤𝘿𝘽 𝙎𝙩𝙖𝙩𝙨</b>
│ 📦 Dᴀᴛᴀ ꜱɪᴢᴇ: {mongo_stats['dataSize']/1024/1024:.1f}MB
│ 🗃 Sᴛᴏʀᴀɢᴇ: {mongo_stats['storageSize']/1024/1024:.1f}MB
│ 📂 Cᴏʟʟᴇᴄᴛɪᴏɴꜱ: {mongo_stats['collections']}
└─────────────────────
</blockquote>
        """
        # Add close button
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button"))

        bot.reply_to(message, status, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"❌ Error getting status: {str(e)}")

#========================== Export User Data (CSV) =================#
@bot.message_handler(func=lambda m: m.text == "📤 Export Data" and m.from_user.id in admin_user_ids)
def export_data(message):
    try:
        from functions import users_collection
        import csv
        from io import StringIO
        
        users = users_collection.find({})
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Username', 'Balance', 'Join Date', 'Referrals', 'Status'])
        
        # Write data
        for user in users:
            writer.writerow([
                user.get('user_id', ''),
                f"@{user.get('username', '')}" if user.get('username') else '',
                user.get('balance', 0),
                user.get('join_date', ''),
                user.get('total_refs', 0),
                'BANNED' if user.get('banned', False) else 'ACTIVE'
            ])
        
        # Send file
        output.seek(0)
        bot.send_document(
            message.chat.id,
            ('users_export.csv', output.getvalue()),
            caption="📊 Uꜱᴇʀ Dᴀᴛᴀ Exᴘᴏʀᴛ"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Export failed: {str(e)}")

#======================= Maintenance Mode command ==================================#
# Add this at the top with other global variables
maintenance_mode = False
maintenance_message = "🚧 Tʜᴇ Bᴏᴛ ɪꜱ Cᴜʀʀᴇɴᴛʟʏ Uɴᴅᴇʀ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ, Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ Lᴀᴛᴇʀ."

# Maintenance toggle command
@bot.message_handler(func=lambda m: m.text == "🔧 Maintenance" and m.from_user.id in admin_user_ids)
def toggle_maintenance(message):
    global maintenance_mode, maintenance_message
    
    if maintenance_mode:
        maintenance_mode = False
        bot.reply_to(message, "✅ 𝙈𝙖𝙞𝙣𝙩𝙚𝙣𝙖𝙣𝙘𝙚 𝙢𝙤𝙙𝙚 𝘿𝙄𝙎𝘼𝘽𝙇𝙀𝘿")
    else:
        # Create cancel button for message input
        cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        cancel_markup.add(KeyboardButton("❌ Cancel Maintenance"))
        
        msg = bot.reply_to(message, 
                          "✍️ <b>Eɴᴛᴇʀ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴇꜱꜱᴀɢᴇ</b>\n\n"
                          "Pʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ꜱᴇɴᴅ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ.\n\n"
                          "❌ Cʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴀɴᴄᴇʟ:",
                          parse_mode="HTML",
                          reply_markup=cancel_markup)
        bot.register_next_step_handler(msg, confirm_maintenance_message)

def confirm_maintenance_message(message):
    # Check if user cancelled
    if message.text and message.text.strip() == "❌ Cancel Maintenance":
        bot.reply_to(message, "❌ Maintenance setup cancelled.", reply_markup=admin_markup)
        return
        
    global maintenance_message
    maintenance_message = message.text
    
    # Calculate hours and minutes for display
    hours = MAINTENANCE_AUTO_DISABLE_TIME // 3600
    minutes = (MAINTENANCE_AUTO_DISABLE_TIME % 3600) // 60
    
    time_display = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    # Create confirmation buttons
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ ᴀᴄᴄᴇᴘᴛ &amp; ꜱᴇɴᴅ", callback_data="accept_maintenance"),
        InlineKeyboardButton("⌧ ᴄᴀɴᴄᴇʟ ⌧", callback_data="cancel_maintenance")
    )
    
    bot.reply_to(
        message,
        f"🔧 <b>Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴇꜱꜱᴀɢᴇ Cᴏɴꜰɪʀᴍᴀᴛɪᴏɴ</b>\n\n"
        f"<blockquote>{maintenance_message}</blockquote>\n\n"
        f"📊 <b>Tʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴡɪʟʟ ʙᴇ ꜱᴇɴᴛ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ ᴀɴᴅ ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ɢᴏ ɪɴᴛᴏ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ.</b>\n\n"
        f"👥 <b>Tᴏᴛᴀʟ Usᴇʀꜱ:</b> <code>{len(get_all_users())}</code>\n"
        f"⏰ <b>Aᴜᴛᴏ-ᴅɪꜱᴀʙʟᴇ:</b> <code>{time_display}</code>\n\n"
        f"<i>Cʟɪᴄᴋ 'Accept & Send' ᴛᴏ ᴄᴏɴꜰɪʀᴍ ᴏʀ 'Cancel' ᴛᴏ ᴀʙᴏʀᴛ:</i>",
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["accept_maintenance", "cancel_maintenance"])
def handle_maintenance_confirmation(call):
    global maintenance_mode, maintenance_message
    
    if call.data == "cancel_maintenance":
        bot.answer_callback_query(call.id, "❌ Maintenance cancelled")
        bot.edit_message_text(
            "🛑 <b>Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Cᴀɴᴄᴇʟʟᴇᴅ</b>\n\n"
            "Tʜᴇ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ʜᴀꜱ ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ. Tʜᴇ ʙᴏᴛ ʀᴇᴍᴀɪɴꜱ ᴀᴄᴛɪᴠᴇ.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        return
    
    if call.data == "accept_maintenance":
        bot.answer_callback_query(call.id, "⏳ ᴇɴᴀʙʟɪɴɢ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ...")
        maintenance_mode = True
        
        # Calculate hours and minutes for display
        hours = MAINTENANCE_AUTO_DISABLE_TIME // 3600
        minutes = (MAINTENANCE_AUTO_DISABLE_TIME % 3600) // 60
        time_display = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        # Update the confirmation message
        bot.edit_message_text(
            "⏳ <b>Eɴᴀʙʟɪɴɢ Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ...</b>\n\n"
            "🔄 Sᴇɴᴅɪɴɢ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ...",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        # Send to all users
        users = get_all_users()
        sent = 0
        failed = 0
        
        for user_id in users:
            try:
                bot.send_message(user_id, f"⚠️ 𝙈𝙖𝙞𝙣𝙩𝙚𝙣𝙖𝙣𝙘𝙚 𝙉𝙤𝙩𝙞𝙘𝙚:\n{maintenance_message}")
                sent += 1
                time.sleep(0.1)
            except:
                failed += 1
                continue
        
        # Final update with results
        bot.edit_message_text(
            f"✅ <b>Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Eɴᴀʙʟᴇᴅ</b>\n\n"
            f"📊 <b>Nᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ Rᴇꜱᴜʟᴛꜱ:</b>\n"
            f"├ ✅ Sᴜᴄᴄᴇꜱꜱꜰᴜʟ: <code>{sent}</code>\n"
            f"└ ❌ Fᴀɪʟᴇᴅ: <code>{failed}</code>\n\n"
            f"⏰ <b>Aᴜᴛᴏ-ᴅɪꜱᴀʙʟᴇ ɪɴ:</b> <code>{time_display}</code>\n\n"
            f"🔧 <b>Tʜᴇ ʙᴏᴛ ɪꜱ ɴᴏᴡ ɪɴ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ</b>",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        )
        
        # Start auto-disable thread with configurable time
        threading.Thread(target=auto_disable_maintenance).start()

def auto_disable_maintenance():
    global maintenance_mode
    
    # Wait for the configured time
    time.sleep(MAINTENANCE_AUTO_DISABLE_TIME)
    
    # Disable maintenance mode
    maintenance_mode = False
    
    # Notify all admins
    notify_admins_maintenance_disabled()
    
    # Notify all users
    notify_users_maintenance_disabled()
    
    logger.info("Maintenance mode auto-disabled after configured time")

def notify_admins_maintenance_disabled():
    """Notify all admins that maintenance mode has been disabled"""
    try:
        for admin_id in admin_user_ids:
            try:
                bot.send_message(
                    admin_id,
                    "✅ <b>Mᴀɪɴᴛᴇɴᴀɴᴄᴇ Mᴏᴅᴇ Aᴜᴛᴏ-Dɪꜱᴀʙʟᴇᴅ</b>\n\n"
                    "🔧 <b>Tʜᴇ ʙᴏᴛ ʜᴀꜱ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴇxɪᴛᴇᴅ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ ᴀɴᴅ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ.</b>\n\n"
                    "⏰ <b>Dᴜʀᴀᴛɪᴏɴ:</b> Cᴏᴍᴘʟᴇᴛᴇᴅ\n"
                    "👥 <b>Uꜱᴇʀꜱ ɴᴏᴛɪꜰɪᴇᴅ:</b> Yᴇꜱ",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Error in notify_admins_maintenance_disabled: {e}")

def notify_users_maintenance_disabled():
    """Notify all users that maintenance mode has been disabled and bot is active"""
    try:
        users = get_all_users()
        sent = 0
        failed = 0
        
        for user_id in users:
            try:
                bot.send_message(
                    user_id,
                    "🎉 <b>Bᴏᴛ Iꜱ Bᴀᴄᴋ Oɴʟɪɴᴇ!</b>\n\n"
                    "✅ <b>Mᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n"
                    "🔧 <b>Tʜᴇ ʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ꜰᴏʀ ᴜꜱᴇ.</b>\n\n"
                    "✨ <b>Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʏᴏᴜʀ ᴘᴀᴛɪᴇɴᴄᴇ!</b>\n\n"
                    "➤ Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜꜱᴇ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ ɴᴏʀᴍᴀʟʟʏ.",
                    parse_mode="HTML"
                )
                sent += 1
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                failed += 1
                continue
        
        logger.info(f"Maintenance disabled notifications: {sent} successful, {failed} failed")
        
    except Exception as e:
        logger.error(f"Error in notify_users_maintenance_disabled: {e}")

#============================ Order Management Commands =============================#
#============================ Order Management Commands =============================#
@bot.message_handler(func=lambda m: m.text == "📦 Order Manager" and m.from_user.id in admin_user_ids)
def check_order_start(message):
    msg = bot.reply_to(message, "Enter Order ID:")
    bot.register_next_step_handler(msg, process_check_order)


def process_check_order(message):
    order_id = message.text.strip()
    try:
        from functions import orders_collection
        order = orders_collection.find_one({"order_id": order_id})
        
        if order:
            user_id = order.get('user_id', 'N/A')
            status_time = datetime.fromtimestamp(order.get('timestamp', time.time())).strftime('%Y-%m-%d %H:%M')
            status = f"""
<blockquote>
┌─────────────────────
│ 📦 <b>Order #{order_id}</b>
│ ━━━━━━━━━━━━━━
│ 👤 Uꜱᴇʀ: {order.get('username', 'N/A')} (<code>{user_id}</code>)
│ 🛒 Sᴇʀᴠɪᴄᴇ: {order.get('service', 'N/A')}
│ 🔗 Lɪɴᴋ: {order.get('link', 'N/A')}
│ 📊 Qᴜᴀɴᴛɪᴛʏ: {order.get('quantity', 'N/A')}
│ 💰 Cᴏꜱᴛ: {order.get('cost', 'N/A')}
│ 🔄 Sᴛᴀᴛᴜꜱ: {order.get('status', 'N/A')}
│ ⏱ Dᴀᴛᴇ: {status_time}
└─────────────────────
</blockquote>
            """

            # Create inline buttons - Contact button and Close button
            markup = InlineKeyboardMarkup()
            
            # Add contact button if user_id is valid
            if user_id and user_id != 'N/A':
                markup.row(
                    InlineKeyboardButton("📞 ᴄᴏɴᴛᴀᴄᴛ ᴜꜱᴇʀ", url=f"tg://user?id={user_id}")
                )
            
            markup.row(
                InlineKeyboardButton("⌧ ᴄʟᴏꜱᴇ ⌧", callback_data="close_button")
            )

            bot.reply_to(
                message,
                status,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=markup
            )
        else:
            bot.reply_to(message, "❌ Order not found")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

#========================== Add this handler for the /policy command =================#

@bot.message_handler(commands=['policy'])
def policy_command(message):
    """Show the bot's usage policy"""
    policy_text = """
<blockquote>
📜 <b> Bᴏᴛ Uꜱᴀɢᴇ Pᴏʟɪᴄʏ & Gᴜɪᴅᴇʟɪɴᴇꜱ</b>
━━━━━━━━━━━━━━━━━━━━

🔹 <b>1. Aᴄᴄᴇᴘᴛᴀʙʟᴇ Uꜱᴇ</b>
  ├ ✅ Pᴇʀᴍɪᴛᴛᴇᴅ: Lᴇɢᴀʟ, ɴᴏɴ-ʜᴀʀᴍꜰᴜʟ ᴄᴏɴᴛᴇɴᴛ
  └ ❌ Pʀᴏʜɪʙɪᴛᴇᴅ: Sᴘᴀᴍ, ʜᴀʀᴀꜱꜱᴍᴇɴᴛ, ɪʟʟᴇɢᴀʟ ᴍᴀᴛᴇʀɪᴀʟ

🔹 <b>2. Fᴀɪʀ Uꜱᴀɢᴇ Pᴏʟɪᴄʏ</b>
   ├ ⚖️ Aʙᴜꜱᴇ ᴍᴀʏ ʟᴇᴀᴅ ᴛᴏ ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ
   └ 📊 Exᴄᴇꜱꜱɪᴠᴇ ᴜꜱᴀɢᴇ ᴍᴀʏ ʙᴇ ʀᴀᴛᴇ-ʟɪᴍɪᴛᴇᴅ

🔹 <b>3. Fɪɴᴀɴᴄɪᴀʟ Pᴏʟɪᴄʏ</b>
   ├ 💳 Aʟʟ ᴛʀᴀɴꜱᴀᴄᴛɪᴏɴꜱ ᴀʀᴇ ꜰɪɴᴀʟ
   └ 🔄 Nᴏ ʀᴇꜰᴜɴᴅꜱ ꜰᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ꜱᴇʀᴠɪᴄᴇꜱ

🔹 <b>4. Pʀɪᴠᴀᴄʏ Cᴏᴍᴍɪᴛᴍᴇɴᴛ</b>
   ├ 🔒 Yᴏᴜʀ ᴅᴀᴛᴀ ꜱᴛᴀʏꜱ ᴄᴏɴꜰɪᴅᴇɴᴛɪᴀʟ
   └ 🤝 Nᴇᴠᴇʀ ꜱʜᴀʀᴇᴅ ᴡɪᴛʜ ᴛʜɪʀᴅ ᴘᴀʀᴛɪᴇꜱ

🔹 <b>5. Pʟᴀᴛꜰᴏʀᴍ Cᴏᴍᴘʟɪᴀɴᴄᴇ</b>
   ├ ✋ Mᴜꜱᴛ ꜰᴏʟʟᴏᴡ Tᴇʟᴇɢʀᴀᴍ'ꜱ TᴏS
   └ 🌐 Aʟʟ ᴄᴏɴᴛᴇɴᴛ ᴍᴜꜱᴛ ʙᴇ ʟᴇɢᴀʟ ɪɴ ʏᴏᴜʀ ᴊᴜʀɪꜱᴅɪᴄᴛɪᴏɴ

⚠️ <b>CᴏɴꜱᴇQᴜᴇɴᴄᴇꜱ ᴏꜰ Vɪᴏʟᴀᴛɪᴏɴ</b>
   ├ ⚠️ Fɪʀꜱᴛ ᴏꜰꜰᴇɴꜱᴇ: Wᴀʀɴɪɴɢ
   ├ 🔇 Rᴇᴘᴇᴀᴛᴇᴅ ᴠɪᴏʟᴀᴛɪᴏɴꜱ: Tᴇᴍᴘᴏʀᴀʀʏ ꜱᴜꜱᴘᴇɴꜱɪᴏɴ
   └ 🚫 Sᴇᴠᴇʀᴇ ᴄᴀꜱᴇꜱ: Pᴇʀᴍᴀɴᴇɴᴛ ʙᴀɴ

📅 <i> Lᴀꜱᴛ ᴜᴘᴅᴀᴛᴇᴅ: {update_date}</i>
━━━━━━━━━━━━━━━━━━━━
💡 Nᴇᴇᴅ ʜᴇʟᴘ? Cᴏɴᴛᴀᴄᴛ @SocialHubBoosterTMbot
</blockquote>
""".format(update_date=datetime.now().strftime('%Y-%m-%d'))  # Fixed datetime reference
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="✅ ᴀᴄᴄᴇᴘᴛ ᴘᴏʟɪᴄʏ", callback_data="accept_policy"))
    
    bot.reply_to(message, policy_text, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "accept_policy")
def accept_policy_callback(call):
    bot.answer_callback_query(
        call.id,
        text="🙏 Tʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ʏᴏᴜʀ Cᴏᴏᴘᴇʀᴀᴛɪᴏɴ!",
        show_alert=True
    )

    try:
        # Remove the button
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )

        # Delete the message after a short delay (optional)
        bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    except Exception as e:
        print(f"Error deleting policy message: {e}")

#======================== Set Bot Commands =====================#
from notification_image import create_order_notification, cleanup_image

# ==================== FLASK INTEGRATION ==================== #
# Configure API helper settings
telebot.apihelper.READ_TIMEOUT = 30
telebot.apihelper.CONNECT_TIMEOUT = 10
telebot.apihelper.RETRY_ON_ERROR = True
telebot.apihelper.MAX_RETRIES = 3


log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File handler with rotation
file_handler = RotatingFileHandler('bot.log', maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(log_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Get logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[408, 429, 500, 502, 503, 504]
)

session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

from webserver import create_web_app
from config import ADMIN_USER_IDS
import threading

# Create Flask app
web_app = create_web_app(bot, ADMIN_USER_IDS)

# Run it in a background thread so it doesn’t block the bot
threading.Thread(target=lambda: web_app.run(host="0.0.0.0", port=8080)).start()

from keep_alive import start_keep_alive, keep_alive
from config import PORT, KEEP_ALIVE_ENABLED

# Start keep-alive system
if KEEP_ALIVE_ENABLED:
    start_keep_alive(PORT)
    logger.info("Keep-alive system started")
# ==================== BOT POLLING ==================== #
def run_bot():
    set_bot_commands()
    logger.info("Bot is starting...")
    
    # Initial delay to prevent immediate restart storms
    time.sleep(10)
    
    while True:
        try:
            logger.info("Starting bot polling...")
            # Use skip_pending=True to skip old updates after restart
            bot.polling(none_stop=True, timeout=30, skip_pending=True)
            
        except ConnectionError as e:
            error_msg = f"Connection error: {e}. Reconnecting in 30 seconds..."
            logger.warning(error_msg)
            web_app.notify_admins(error_msg)
            time.sleep(30)
            
        except telebot.apihelper.ApiException as e:
            error_msg = f"Telegram API error: {str(e)[:200]}"
            logger.warning(error_msg)
            time.sleep(30)
            
        except Exception as e:
            error_msg = f"Bot polling failed: {str(e)[:200]}"
            logger.error(error_msg)
            
            # Don't notify for common, expected errors
            if not isinstance(e, (ConnectionError, telebot.apihelper.ApiException)):
                web_app.notify_admins(error_msg)
                
            # Longer delay for more serious errors
            time.sleep(30)
            
        # Small delay before restarting to prevent tight loops
        time.sleep(5)

# ==================== MAIN EXECUTION ==================== #
if __name__ == '__main__':
    try:
        logger.info("Initializing bot...")
        
        # Start keep-alive thread
        keep_alive_thread = threading.Thread(target=keep_alive)
        keep_alive_thread.daemon = True
        keep_alive_thread.start()
        
        # Start bot in background thread
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Configure Flask server
        logger.info("Starting Flask server...")
        web_app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', '10000')),
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.critical(f"Fatal error in main execution: {e}")
        web_app.notify_admins(f"Bot crashed: {str(e)[:200]}")
        raise


