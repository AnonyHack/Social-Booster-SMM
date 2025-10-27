import os
import time
import psutil
import threading
from datetime import datetime
from flask import Flask, jsonify


def create_web_app(bot, admin_user_ids, logger=None):
    """
    Create and configure a lightweight Flask web app for uptime & health monitoring.

    Args:
        bot: TeleBot instance
        admin_user_ids: list of admin Telegram user IDs
        logger: optional logger for error output
    Returns:
        Flask app instance
    """
    web_app = Flask(__name__)
    start_time = time.time()  # record startup time

    @web_app.route('/')
    def home():
        """Basic info endpoint"""
        try:
            bot_username = bot.get_me().username
        except Exception:
            bot_username = "unknown"
        return jsonify({
            "status": "running",
            "bot": bot_username,
            "uptime_seconds": time.time() - start_time,
            "admin_count": len(admin_user_ids),
            "version": "1.0"
        }), 200

    @web_app.route('/health')
    def health():
        """System health metrics"""
        process = psutil.Process(os.getpid())
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "memory_usage": f"{process.memory_info().rss / 1024 / 1024:.2f} MB",
            "active_threads": threading.active_count()
        }), 200

    @web_app.route('/ping')
    def ping():
        """Simple keep-alive endpoint"""
        return "pong", 200

    def notify_admins(message: str):
        """Send a one-time alert message to the first reachable admin"""
        for admin_id in admin_user_ids:
            try:
                bot.send_message(
                    admin_id,
                    f"⚠️ <b>Bot Notification</b> ⚠️\n\n{message}",
                    parse_mode='HTML'
                )
                break  # Notify just one to avoid rate limits
            except Exception as admin_error:
                if logger:
                    logger.error(f"Failed to notify admin {admin_id}: {admin_error}")
                continue

    # Expose helper to outer scope
    web_app.notify_admins = notify_admins
    return web_app
