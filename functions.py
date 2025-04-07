from pymongo import MongoClient
from pymongo.errors import AutoReconnect
import time
import json
import re
import os
from dotenv import load_dotenv

# MongoDB connection setup
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))  # Load MongoDB connection string from .env file
db = client["Cluster0"]  # Replace with your database name
users_collection = db["users"]
bans_collection = db["bans"]

def isExists(user_id):
    """Check if the user exists in the database."""
    return users_collection.find_one({"user_id": user_id}) is not None

def insertUser(user_id, data):
    """Insert user data if the user does not exist."""
    if not isExists(user_id):
        data["user_id"] = user_id
        users_collection.insert_one(data)
        return True
    return False

def getData(user_id):
    """Retrieve all user data."""
    return users_collection.find_one({"user_id": user_id})

def updateUser(user_id, data):
    """Update user data in the database."""
    result = users_collection.update_one({"user_id": user_id}, {"$set": data})
    return result.modified_count > 0

def addBalance(user_id, amount):
    """Add balance to the user's account."""
    result = users_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": amount, "total_deposits": amount}, "$set": {"last_activity": time.time()}}
    )
    return result.modified_count > 0

def cutBalance(user_id, amount):
    """Deduct balance from the user's account."""
    user = getData(user_id)
    if user and user.get("balance", 0) >= amount:
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": -amount}}
        )
        return result.modified_count > 0
    return False

def ban_user(user_id):
    """Ban a user by adding a record to the bans collection."""
    bans_collection.insert_one({"user_id": user_id, "banned_at": time.time()})

def unban_user(user_id):
    """Unban a user by removing the record from the bans collection."""
    bans_collection.delete_one({"user_id": user_id})

def is_banned(user_id):
    """Check if a user is banned."""
    return bans_collection.find_one({"user_id": user_id}) is not None

def get_all_users():
    """Get a list of all user IDs."""
    return [user["user_id"] for user in users_collection.find({}, {"user_id": 1})]

def get_user_count():
    """Get the total number of users."""
    return users_collection.count_documents({})

def get_banned_users():
    """Get a list of all banned user IDs."""
    return [ban["user_id"] for ban in bans_collection.find({}, {"user_id": 1})]

def get_user_orders_stats(user_id):
    """Get order statistics for a specific user."""
    user = getData(user_id)
    if not user or "orders" not in user:
        return {"total": 0, "completed": 0, "pending": 0, "failed": 0}
    
    stats = {"total": len(user["orders"]), "completed": 0, "pending": 0, "failed": 0}
    for order in user["orders"]:
        if order["status"] == "completed":
            stats["completed"] += 1
        elif order["status"] == "pending":
            stats["pending"] += 1
        elif order["status"] == "failed":
            stats["failed"] += 1
    return stats

def add_order(user_id, order_data):
    """Add a new order to the user's history."""
    result = users_collection.update_one(
        {"user_id": user_id},
        {"$push": {"orders": order_data}}
    )
    return result.modified_count > 0

def get_top_users(limit=10):
    """Get top users by order count."""
    users = users_collection.find({"orders_count": {"$exists": True}}, {"user_id": 1, "orders_count": 1})
    sorted_users = sorted(users, key=lambda x: x["orders_count"], reverse=True)
    return sorted_users[:limit]

def get_active_users(days=7):
    """Get the count of users active in the last X days."""
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    return users_collection.count_documents({"last_activity": {"$gte": cutoff_time}})

def get_total_orders():
    """Get the total number of orders processed."""
    return sum(user.get("orders_count", 0) for user in users_collection.find({}, {"orders_count": 1}))

def get_total_deposits():
    """Get the total deposits made by all users."""
    return sum(user.get("total_deposits", 0) for user in users_collection.find({}, {"total_deposits": 1}))

def get_top_referrer():
    """Get the user with the most referrals."""
    top_referrer = users_collection.find_one(sort=[("total_refs", -1)], projection={"user_id": 1, "username": 1, "total_refs": 1})
    if top_referrer:
        return {"user_id": top_referrer["user_id"], "username": top_referrer.get("username"), "count": top_referrer["total_refs"]}
    return {"user_id": None, "username": None, "count": 0}

def is_valid_tiktok_username(username):
    """Check if the TikTok username is valid"""
    pattern = r'^[a-zA-Z0-9._]{2,24}$'  # Adjusted regex for TikTok usernames
    return re.match(pattern, username) is not None

def is_valid_tiktok_link(link):
    """Check if the TikTok link is in any valid format"""
    patterns = [
        r'^https?://(www\.|m\.)?tiktok\.com/@[\w\.-]+/video/\d+',  # Standard video links
        r'^https?://vm\.tiktok\.com/[\w]+/?',  # vm.tiktok.com short links
        r'^https?://(www\.)?tiktok\.com/t/[\w]+/?',  # t/ short links
        r'^https?://(www\.)?tiktok\.com/[\w]+/?',  # Other short links
        r'^https?://(www\.)?tiktok\.com/.+/photo/\d+'  # Photo posts
    ]
    link = link.strip().split('?')[0]  # Remove URL parameters
    return any(re.match(pattern, link) for pattern in patterns)

def getData(user_id):
    try:
        return users_collection.find_one({"user_id": user_id})
    except AutoReconnect:
        print("Reconnecting to MongoDB...")
        time.sleep(2)
        return getData(user_id)  # Retry
    
def addRefCount(user_id):
    """Increment the referral count for the user."""
    if isExists(user_id):
        file_path = os.path.join("Account", f'{user_id}.json')
        with open(file_path, 'r+') as file:
            data = json.load(file)
            # Increment the total_refs count
            data['total_refs'] = data.get('total_refs', 0) + 1  # Default to 0 if not found
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
        return True
    return False

def setWelcomeStaus(user_id):
    """Set the referral information for the user."""
    if isExists(user_id):

        file_path = os.path.join("Account", f'{user_id}.json')
        with open(file_path, 'r+') as file:
            data = json.load(file)
            data['welcome_bonus'] = 1
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
        return True
    return False

def setReferredStatus(user_id):
    """Set the referral information for the user."""
    if isExists(user_id):

        file_path = os.path.join("Account", f'{user_id}.json')
        with open(file_path, 'r+') as file:
            data = json.load(file)
            data['referred'] = 1
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
        return True
    return False

def track_exists(user_id):
    """Check if the referral user exists."""
    return isExists(user_id)

print("functions.py loaded with MongoDB integration.")

