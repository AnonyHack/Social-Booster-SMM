import os
import json
import time
import re


def update_order_status(user_id, order_id, new_status):
    """Update status of a specific order"""
    try:
        filepath = os.path.join('Account', f'{user_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if 'orders' in data:
                for order in data['orders']:
                    if order.get('order_id') == order_id:
                        order['status'] = new_status
                        order['status_update_time'] = time.time()
                        break
            
            with open(filepath, 'w') as f:
                json.dump(data, f)
            return True
        return False
    except Exception as e:
        print(f"Error updating order status: {e}")
        return False
    

def get_user_orders_stats(user_id):
    """Get order statistics for a specific user"""
    stats = {
        'total': 0,
        'completed': 0,
        'pending': 0,
        'failed': 0
    }
    
    try:
        filepath = os.path.join('Account', f'{user_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if 'orders' in data:
                stats['total'] = len(data['orders'])
                for order in data['orders']:
                    if order.get('status') == 'completed':
                        stats['completed'] += 1
                    elif order.get('status') == 'pending':
                        stats['pending'] += 1
                    elif order.get('status') == 'failed':
                        stats['failed'] += 1
    except Exception as e:
        print(f"Error getting order stats: {e}")
    
    return stats

def isExists(user_id):
    """Check if the user file exists."""
    file_path = os.path.join('Account', f'{user_id}.json')
    return os.path.isfile(file_path)

def insertUser(user_id, data):
    """Insert user data if user file does not exist."""
    if not isExists(user_id):
        if not os.path.exists('Account'):
            os.makedirs('Account')
        file_path = os.path.join('Account', f'{user_id}.json')
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    return False

def getData(user_id):
    """Retrieve all user data in JSON format."""
    if isExists(user_id):
        file_path = os.path.join("Account", f'{user_id}.json')
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    else:
        # Return None or an empty dictionary if the user file does not exist
        return None

def addBalance(user_id, amount):
    """Add balance to user account and track deposits"""
    try:
        filepath = os.path.join('Account', f'{user_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Track deposits only when admin adds coins
            if 'total_deposits' not in data:
                data['total_deposits'] = 0
            data['total_deposits'] += amount
            
            data['balance'] = str(float(data['balance']) + amount)
            data['last_activity'] = time.time()
            
            with open(filepath, 'w') as f:
                json.dump(data, f)
            return True
        return False
    except:
        return False

def cutBalance(user_id, amount):
    """Deduct balance from the user account."""
    if isExists(user_id):
        file_path = os.path.join('Account', f'{user_id}.json')
        with open(file_path, 'r+') as file:
            data = json.load(file)
            current_balance = float(data['balance'])
            amount = float(amount)
            if current_balance >= amount:
                data['balance'] = str(current_balance - amount)
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
                return True
    return False

def track_exists(user_id):
    """Check if the referral user exists."""
    return isExists(user_id)

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

def updateUser(user_id, data):
    """Update user data in the database (JSON file-based storage)."""
    user_file = f"Account/{user_id}.json"
    
    try:
        # Ensure the directory exists
        if not os.path.exists("Account"):
            os.makedirs("Account")
        
        # Write the updated data to the user's file
        with open(user_file, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error updating user {user_id}: {e}")
        return False
    

#================= New Commands ===================#
# Add to functions.py
def get_all_users():
    """Get list of all user IDs"""
    if not os.path.exists('Account'):
        return []
    return [f.replace('.json', '') for f in os.listdir('Account') if f.endswith('.json')]

def get_user_count():
    """Get total number of users"""
    return len(get_all_users())

def ban_user(user_id):
    """Ban a user by creating a ban record"""
    if not os.path.exists('Bans'):
        os.makedirs('Bans')
    with open(f'Bans/{user_id}.ban', 'w') as f:
        f.write(str(int(time.time())))

def unban_user(user_id):
    """Unban a user by removing ban record"""
    ban_file = f'Bans/{user_id}.ban'
    if os.path.exists(ban_file):
        os.remove(ban_file)

def is_banned(user_id):
    """Check if user is banned"""
    return os.path.exists(f'Bans/{user_id}.ban')

def get_banned_users():
    """Get list of all banned user IDs"""
    if not os.path.exists('Bans'):
        return []
    return [f.replace('.ban', '') for f in os.listdir('Bans') if f.endswith('.ban')]

def get_top_users(limit=10):
    """Get top users by order count (you'll need to track orders)"""
    users = []
    for user_id in get_all_users():
        data = getData(user_id)
        if data and 'orders_count' in data:
            users.append((user_id, data['orders_count']))
    return sorted(users, key=lambda x: x[1], reverse=True)[:limit]

# New functions For Analytics on Admin Panel

def get_active_users(days=7):
    """Get count of users active in last X days"""
    active_users = 0
    account_folder = 'Account'
    if not os.path.exists(account_folder):
        return 0
    
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    
    for filename in os.listdir(account_folder):
        if filename.endswith('.json'):
            filepath = os.path.join(account_folder, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if 'last_activity' in data and data['last_activity'] > cutoff_time:
                        active_users += 1
            except:
                continue
    return active_users

def get_total_orders():
    """Get total orders processed"""
    total_orders = 0
    account_folder = 'Account'
    if not os.path.exists(account_folder):
        return 0
    
    for filename in os.listdir(account_folder):
        if filename.endswith('.json'):
            filepath = os.path.join(account_folder, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if 'orders_count' in data:
                        total_orders += data['orders_count']
            except:
                continue
    return total_orders

def get_total_deposits():
    """Get total deposits made by admin"""
    total_deposits = 0
    account_folder = 'Account'
    if not os.path.exists(account_folder):
        return 0
    
    for filename in os.listdir(account_folder):
        if filename.endswith('.json'):
            filepath = os.path.join(account_folder, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if 'total_deposits' in data:
                        total_deposits += data['total_deposits']
            except:
                continue
    return total_deposits

def get_top_referrer():
    """Get user with most referrals"""
    top_referrer = {'user_id': None, 'username': None, 'count': 0}
    account_folder = 'Account'
    if not os.path.exists(account_folder):
        return top_referrer
    
    for filename in os.listdir(account_folder):
        if filename.endswith('.json'):
            filepath = os.path.join(account_folder, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if 'total_refs' in data and data['total_refs'] > top_referrer['count']:
                        top_referrer = {
                            'user_id': data['user_id'],
                            'username': data.get('username', None),
                            'count': data['total_refs']
                        }
            except:
                continue
    return top_referrer

#============== Handle TikTok Links ==============#
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

print("functions.py loaded")

