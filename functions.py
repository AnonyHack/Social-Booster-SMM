import os
import time
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta


# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MongoDB connection
try:
    client = MongoClient(MONGO_URI)
    db = client.get_database("smmhubboosterv2")  # Use your database name here
    # Define collections
    users_collection = db.users
    orders_collection = db.orders
    cash_logs_collection = db['affiliate_cash_logs']  # New collection for cash logs
    logger.info("Connected to MongoDB successfully")
except PyMongoError as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

def isExists(user_id):
    """Check if the user exists in database."""
    try:
        return users_collection.count_documents({"user_id": str(user_id)}) > 0
    except PyMongoError as e:
        logger.error(f"Error checking user existence {user_id}: {e}")
        return False

def insertUser(user_id, data):
    """Insert user data if user doesn't exist."""
    try:
        user_id = str(user_id)
        
        # Ensure balance is stored as float, not string
        if 'balance' in data:
            data['balance'] = float(data['balance'])
        
        # Add default fields for new users
        data['user_id'] = user_id
        data['join_date'] = data.get('join_date', datetime.now())  # Add join_date if not provided
        data['total_deposits'] = data.get('total_deposits', 0.0)  # Default total deposits
        data['orders_count'] = data.get('orders_count', 0)  # Default order count
        data['total_refs'] = data.get('total_refs', 0)  # Default referral count
        data['welcome_bonus'] = data.get('welcome_bonus', 0)  # Default welcome bonus status
        data['referred'] = data.get('referred', 0)  # Default referral status
        data['banned'] = data.get('banned', False)  # Default banned status
        # Add affiliate earnings field
        data['affiliate_earnings'] = data.get('affiliate_earnings', 0.0)
        
        # Insert the user into the database
        result = users_collection.insert_one(data)
        return result.inserted_id is not None
    except PyMongoError as e:
        logger.error(f"Error inserting user {user_id}: {e}")
        return False

def getData(user_id):
    """Retrieve all user data."""
    try:
        user_data = users_collection.find_one({"user_id": str(user_id)}, {'_id': 0})
        if user_data and 'balance' in user_data:
            # Ensure balance is returned as float
            user_data['balance'] = float(user_data['balance'])
        return user_data or None
    except PyMongoError as e:
        logger.error(f"Error getting user data {user_id}: {e}")
        return None

def updateUser(user_id, data):
    """Update user data in the database."""
    try:
        user_id = str(user_id)
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$set": data},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    except PyMongoError as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return False

def addBalance(user_id, amount):
    """Add balance to the user account and track deposits"""
    try:
        user_id = str(user_id)
        amount = float(amount)
        
        # Update both balance and total_deposits
        result = users_collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "balance": amount,
                    "total_deposits": amount  # Track deposits separately
                }
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    except (PyMongoError, ValueError) as e:
        logger.error(f"Error adding balance for {user_id}: {e}")
        return False

def cutBalance(user_id, amount):
    """Deduct balance from the user account (doesn't affect total_deposits)"""
    try:
        user_id = str(user_id)
        amount = float(amount)
        
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            return False
            
        if float(user.get('balance', 0)) >= amount:
            result = users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": -amount}}
            )
            return result.modified_count > 0
        return False
    except (PyMongoError, ValueError) as e:
        logger.error(f"Error cutting balance for {user_id}: {e}")
        return False

def track_exists(user_id):
    """Check if the referral user exists."""
    return isExists(user_id)

def setWelcomeStaus(user_id):
    """Set the welcome bonus status for the user."""
    try:
        user_id = str(user_id)
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"welcome_bonus": 1}}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error setting welcome status for {user_id}: {e}")
        return False

def setReferredStatus(user_id):
    """Set the referral status for the user."""
    try:
        user_id = str(user_id)
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"referred": 1}}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error setting referred status for {user_id}: {e}")
        return False

def addRefCount(user_id):
    """Increment the referral count for the user."""
    try:
        user_id = str(user_id)
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"total_refs": 1}}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error adding referral count for {user_id}: {e}")
        return False

def add_order(user_id, order_data):
    """Add a new order to user's history."""
    try:
        order_data['user_id'] = str(user_id)
        if 'timestamp' not in order_data:
            order_data['timestamp'] = time.time()
        if 'status' not in order_data:
            order_data['status'] = 'pending'
        
        # Insert into orders collection
        result = orders_collection.insert_one(order_data)
        
        # Update user's order count (create field if doesn't exist)
        users_collection.update_one(
            {"user_id": str(user_id)},
            {"$inc": {"orders_count": 1}},
            upsert=True
        )
        
        return result.inserted_id is not None
    except PyMongoError as e:
        logger.error(f"Error adding order for {user_id}: {e}")
        return False


def get_user_orders_stats(user_id):
    """Get order statistics for a specific user."""
    stats = {
        'total': 0,
        'completed': 0,
        'pending': 0,
        'failed': 0
    }
    
    try:
        # Get counts for each status
        pipeline = [
            {"$match": {"user_id": str(user_id)}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        results = list(orders_collection.aggregate(pipeline))
        
        # Initialize all counts to 0 first
        stats = {
            'total': 0,
            'completed': 0,
            'pending': 0,
            'failed': 0
        }
        
        # Update counts based on aggregation results
        for result in results:
            status = result["_id"].lower()
            count = result["count"]
            
            if status == "processing":
                stats['pending'] += count  # Treat 'processing' as pending
            elif status in stats:
                stats[status] = count
        
        # Calculate total as sum of all known status counts
        stats['total'] = stats['completed'] + stats['pending'] + stats['failed']
    
    except Exception as e:
        logger.error(f"Error getting order stats for {user_id}: {e}")
        # Return default stats with all zeros if there's an error

    return stats

def update_order_status(user_id, order_id, new_status):
    """Update status of a specific order."""
    try:
        result = orders_collection.update_one(
            {"user_id": str(user_id), "order_id": order_id},
            {"$set": {
                "status": new_status,
                "status_update_time": time.time()
            }}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error updating order status {order_id}: {e}")
        return False
    
# ================= Affiliate Earnings Functions =================

def get_affiliate_earnings(user_id):
    """Get user's total affiliate earnings"""
    try:
        user = users_collection.find_one({"user_id": str(user_id)}, {"affiliate_earnings": 1})
        return float(user.get("affiliate_earnings", 0.0)) if user else 0.0
    except Exception as e:
        logger.error(f"Error getting affiliate earnings for {user_id}: {e}")
        return 0.0

def add_affiliate_earning(user_id, amount):
    """Add to user's affiliate earnings"""
    try:
        user_id = str(user_id)
        amount = float(amount)
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"affiliate_earnings": amount}},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error(f"Error adding affiliate earning for {user_id}: {e}")
        return False

def get_affiliate_users(user_id):
    """Get list of users referred by this affiliate"""
    try:
        user_id = str(user_id)
        users = users_collection.find({"ref_by": user_id}, {"user_id": 1, "_id": 0})
        return [u["user_id"] for u in users]
    except Exception as e:
        logger.error(f"Error getting affiliate users for {user_id}: {e}")
        return []
    
def update_affiliate_earning(user_id, amount, subtract=False, admin_id=None):
    """Add or subtract from affiliate earnings and log it separately."""
    user = users_collection.find_one({"user_id": str(user_id)})
    if not user:
        return False

    current = float(user.get("affiliate_earnings", 0.0))
    new_amount = current - float(amount) if subtract else current + float(amount)
    new_amount = round(max(new_amount, 0), 2)

    result = users_collection.update_one(
        {"user_id": str(user_id)},
        {"$set": {"affiliate_earnings": new_amount}}
    )

    # ✅ Log this transaction
    cash_logs_collection.insert_one({
        "user_id": str(user_id),
        "amount": float(amount),
        "type": "remove" if subtract else "add",
        "admin_id": str(admin_id) if admin_id else "unknown",
        "timestamp": datetime.utcnow()
    })

    return result.modified_count > 0


# Admin functions
def get_all_users():
    """Get list of all user IDs"""
    try:
        return [user['user_id'] for user in users_collection.find({}, {'user_id': 1, '_id': 0})]
    except PyMongoError as e:
        logger.error(f"Error getting all users: {e}")
        return []

def get_user_count():
    """Get total number of users"""
    try:
        return users_collection.count_documents({})
    except PyMongoError as e:
        logger.error(f"Error getting user count: {e}")
        return 0

def ban_user(user_id):
    """Ban a user by setting banned flag"""
    try:
        user_id = str(user_id)
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"banned": True}},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    except PyMongoError as e:
        logger.error(f"Error banning user {user_id}: {e}")
        return False

def unban_user(user_id):
    """Unban a user by removing banned flag"""
    try:
        user_id = str(user_id)
        result = users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"banned": False}}
        )
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error unbanning user {user_id}: {e}")
        return False

def is_banned(user_id):
    """Check if user is banned"""
    try:
        user = users_collection.find_one(
            {"user_id": str(user_id)},
            {"banned": 1}
        )
        return user and user.get("banned", False)
    except PyMongoError as e:
        logger.error(f"Error checking ban status for {user_id}: {e}")
        return False

def get_banned_users():
    """Get list of all banned user IDs"""
    try:
        return [user['user_id'] for user in users_collection.find(
            {"banned": True},
            {'user_id': 1, '_id': 0}
        )]
    except PyMongoError as e:
        logger.error(f"Error getting banned users: {e}")
        return []

def get_top_users(limit=10):
    """Get top users by order count"""
    try:
        pipeline = [
            {"$group": {
                "_id": "$user_id",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        return [(str(item["_id"]), item["count"]) for item in orders_collection.aggregate(pipeline)]
    except PyMongoError as e:
        logger.error(f"Error getting top users: {e}")
        return []

def get_active_users(days=7):
    """Get count of users active in last X days"""
    try:
        cutoff = time.time() - (days * 24 * 60 * 60)
        return users_collection.count_documents({
            "last_activity": {"$gte": cutoff}
        })
    except PyMongoError as e:
        logger.error(f"Error getting active users: {e}")
        return 0

def get_total_orders():
    """Get total orders processed"""
    try:
        return orders_collection.count_documents({})
    except PyMongoError as e:
        logger.error(f"Error getting total orders: {e}")
        return 0

def get_total_deposits():
    """Get total coins added by admin (not affected by spending)"""
    try:
        # Track deposits separately in user document
        result = users_collection.aggregate([{
            "$group": {
                "_id": None,
                "total": {"$sum": "$total_deposits"}
            }
        }])
        return next(result, {"total": 0})["total"]
    except PyMongoError as e:
        logger.error(f"Error getting total deposits: {e}")
        return 0

def get_top_referrer():
    """Get user with most referrals"""
    try:
        result = users_collection.find_one(
            {"total_refs": {"$gt": 0}},
            {"user_id": 1, "username": 1, "total_refs": 1},
            sort=[("total_refs", -1)]
        )
        if result:
            return {
                'user_id': result.get('user_id'),
                'username': result.get('username', 'N/A'),
                'count': result.get('total_refs', 0)
            }
        return {'user_id': None, 'username': None, 'count': 0}
    except PyMongoError as e:
        logger.error(f"Error getting top referrer: {e}")
        return {'user_id': None, 'username': None, 'count': 0}

def get_completed_orders():
    """Get the total number of completed orders."""
    try:
        return orders_collection.count_documents({"status": "completed"})
    except PyMongoError as e:
        logger.error(f"Error getting completed orders: {e}")
        return 0


def get_new_users(days=1):
    """Get the number of new users who joined within the last `days`."""
    try:
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Query the database for users who joined after the cutoff date
        return users_collection.count_documents({"join_date": {"$gte": cutoff_date}})
    except PyMongoError as e:
        logger.error(f"Error getting new users: {e}")
        return 0

# -- Pinned messages MongoDB -- #

def save_pinned_message(user_id, message_id):
    """Save pinned message ID for a user"""
    try:
        users_collection.update_one(
            {"user_id": str(user_id)},
            {"$set": {"pinned_message_id": message_id}},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving pinned message for {user_id}: {e}")

def get_all_pinned_messages():
    """Get all users with pinned message IDs"""
    pinned = {}
    try:
        users = users_collection.find({"pinned_message_id": {"$exists": True}})
        for user in users:
            pinned[user['user_id']] = user['pinned_message_id']
    except Exception as e:
        print(f"Error loading pinned messages: {e}")
    return pinned

def clear_all_pinned_messages():
    """Clear pinned message IDs from all users"""
    try:
        users_collection.update_many(
            {"pinned_message_id": {"$exists": True}},
            {"$unset": {"pinned_message_id": ""}}
        )
    except Exception as e:
        print(f"Error clearing pinned messages: {e}")

#========= Show how much the user spent ==========#
def get_confirmed_spent(user_id):
    try:
        pipeline = [
            {"$match": {
                "user_id": str(user_id),
                "status": "completed"  # Only completed orders
            }},
            {"$group": {
                "_id": None, 
                "total": {"$sum": "$cost"}
            }}
        ]
        result = list(orders_collection.aggregate(pipeline))
        return float(result[0]["total"]) if result else 0.0
    except Exception as e:
        print(f"Error in get_confirmed_spent: {e}")
        return 0.0

def get_pending_spent(user_id):
    try:
        pipeline = [
            {"$match": {
                "user_id": str(user_id),
                "status": {"$in": ["pending", "processing"]}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$cost"}}}
        ]
        result = list(orders_collection.aggregate(pipeline))
        return result[0]["total"] if result else 0.0
    except Exception as e:
        print(f"Error in get_pending_spent: {e}")
        return 0.0

def get_user_deposits(user_id):
    """Get total deposits for a user (coins added through purchases or admin)"""
    # Example with MongoDB:
    user = db.users.find_one({'user_id': str(user_id)})
    return float(user.get('total_deposits', 0)) if user else 0.0

# In functions.py
def delete_user(user_id):
    """Delete a user from the database"""
    try:
        users_collection.delete_one({"user_id": str(user_id)})
        orders_collection.delete_many({"user_id": str(user_id)})
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def lock_service(service_id):
    """Lock a service so only admins can order it"""
    try:
        locked_services = db.locked_services
        locked_services.update_one(
            {"service_id": service_id},
            {"$set": {"service_id": service_id}},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error locking service: {e}")
        return False

def unlock_service(service_id):
    """Unlock a service for all users"""
    try:
        locked_services = db.locked_services
        result = locked_services.delete_one({"service_id": service_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error unlocking service: {e}")
        return False

def get_locked_services():
    """Get list of all locked service IDs"""
    try:
        locked_services = db.locked_services
        return [doc["service_id"] for doc in locked_services.find()]
    except Exception as e:
        print(f"Error getting locked services: {e}")
        return []

def addBonusBalance(user_id, amount):
    """Add bonus coins without affecting total_deposits"""
    try:
        user_id = str(user_id)
        amount = float(amount)

        result = users_collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {"balance": amount},
                "$set": {"bonus_coins": amount, "last_bonus_claim": time.time()}
            }
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error adding bonus balance for {user_id}: {e}")
        return False

def removeOldBonus(user_id):
    """Remove old unused bonus coins if any"""
    try:
        user_id = str(user_id)
        user = users_collection.find_one({"user_id": user_id})

        if not user:
            return False

        bonus = float(user.get("bonus_coins", 0))
        if bonus > 0:
            current_balance = float(user.get("balance", 0))
            new_balance = max(0, current_balance - bonus)

            users_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {"balance": new_balance, "bonus_coins": 0}
                }
            )
            return True
        return False
    except Exception as e:
        logger.error(f"Error removing old bonus for {user_id}: {e}")
        return False


def get_suspicious_users():
    try:
        suspicious = []

        # 1. Users with bonus coins but no spending
        bonus_abusers = users_collection.find({
            "bonus_coins": {"$gt": 0},
            "$or": [
                {"orders_count": {"$lte": 0}},
                {"total_spent": {"$exists": False}},
                {"total_spent": 0}
            ]
        })

        for user in bonus_abusers:
            suspicious.append({
                "type": "🎁 Bonus Abuse",
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "balance": user.get("balance", 0),
                "bonus": user.get("bonus_coins", 0)
            })

        # 2. Users with balance > 100 but no deposits
        high_balance_no_deposit = users_collection.find({
            "balance": {"$gte": 100},
            "$or": [
                {"total_deposits": 0},
                {"total_deposits": {"$exists": False}}
            ]
        })

        for user in high_balance_no_deposit:
            suspicious.append({
                "type": "💰 High Balance, No Deposit",
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "balance": user.get("balance", 0),
                "deposits": user.get("total_deposits", 0)
            })

        # 3. Users who referred themselves (user_id == ref_by)
        self_referrals = users_collection.find({
            "$expr": {"$eq": ["$user_id", "$ref_by"]}
        })

        for user in self_referrals:
            suspicious.append({
                "type": "🌀 Self Referral",
                "user_id": user.get("user_id"),
                "username": user.get("username")
            })

        return suspicious

    except Exception as e:
        print(f"Error finding suspicious users: {e}")
        return []

#================== Top Affiliate Earners ======================#
def get_top_affiliate_earners(limit=10):
    """Return top N users by affiliate_earnings."""
    try:
        pipeline = [
            {"$match": {"affiliate_earnings": {"$gt": 0}}},
            {"$sort": {"affiliate_earnings": -1}},
            {"$limit": limit},
            {"$project": {"user_id": 1, "username": 1, "affiliate_earnings": 1, "_id": 0}}
        ]
        return list(users_collection.aggregate(pipeline))
    except Exception as e:
        print(f"Error getting top affiliates: {e}")
        return []

# ======================= TOP BALANCES ======================= #
def get_top_balances(limit=10):
    """Return top N users with the highest balance."""
    try:
        pipeline = [
            {"$sort": {"balance": -1}},
            {"$limit": limit},
            {"$project": {"user_id": 1, "username": 1, "balance": 1, "_id": 0}}
        ]
        return list(users_collection.aggregate(pipeline))
    except Exception as e:
        print(f"Error getting top balances: {e}")
        return []

# ======================= BONUS CONFIG ======================= #
_bonus_amount = 30
_bonus_interval = 60  # 1 hour for testing
_bonus_enabled = True

def get_bonus_amount():
    return _bonus_amount

def get_bonus_interval():
    return _bonus_interval

def is_bonus_enabled():
    return _bonus_enabled

def set_bonus_amount(amount):
    global _bonus_amount
    _bonus_amount = amount

def set_bonus_interval(seconds):
    global _bonus_interval
    _bonus_interval = seconds

def toggle_bonus():
    global _bonus_enabled
    _bonus_enabled = not _bonus_enabled
    return _bonus_enabled

def get_combined_leaderboard(limit=50):
    """Return top users ranked by combined score of balance, affiliate_earnings (UGX), and orders"""
    try:
        users = users_collection.aggregate([
            {
                "$addFields": {
                    "performance_score": {
                        "$add": [
                            { "$toDouble": "$balance" },
                            { "$multiply": [ { "$toDouble": "$affiliate_earnings" }, 364.8 ] },
                            { "$multiply": [ { "$toDouble": "$orders_count" }, 10 ] }
                        ]
                    }
                }
            },
            {
                "$sort": { "performance_score": -1 }
            },
            {
                "$project": {
                    "user_id": 1,
                    "username": 1,
                    "first_name": 1,
                    "balance": 1,
                    "affiliate_earnings": 1,
                    "orders_count": 1,
                    "performance_score": 1
                }
            },
            {
                "$limit": limit
            }
        ])
        return list(users)
    except Exception as e:
        print(f"Leaderboard error: {e}")
        return []



print("functions.py loaded with MongoDB support")
