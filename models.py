import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, List

class DatabaseManager:
    def __init__(self, db_file="database/users.json"):
        self.db_file = db_file
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Ensure database file exists"""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({"users": {}, "withdrawals": []}, f)
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except:
            return {"users": {}, "withdrawals": []}
    
    def save_data(self, data):
        """Save data to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)

class User:
    def __init__(self, telegram_id: str, username: str = "", first_name: str = "", last_name: str = ""):
        self.telegram_id = str(telegram_id)
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.referral_code = str(uuid.uuid4())[:8]
        self.referred_by = None
        self.referred_users = []
        self.wallet_balance = 0
        self.upi_id = ""
        self.joined_channel = False
        self.created_at = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "referral_code": self.referral_code,
            "referred_by": self.referred_by,
            "referred_users": self.referred_users,
            "wallet_balance": self.wallet_balance,
            "upi_id": self.upi_id,
            "joined_channel": self.joined_channel,
            "created_at": self.created_at,
            "last_active": self.last_active
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(
            telegram_id=data["telegram_id"],
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", "")
        )
        user.referral_code = data.get("referral_code", str(uuid.uuid4())[:8])
        user.referred_by = data.get("referred_by")
        user.referred_users = data.get("referred_users", [])
        user.wallet_balance = data.get("wallet_balance", 0)
        user.upi_id = data.get("upi_id", "")
        user.joined_channel = data.get("joined_channel", False)
        user.created_at = data.get("created_at", datetime.now().isoformat())
        user.last_active = data.get("last_active", datetime.now().isoformat())
        return user

class UserRepository:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_user(self, telegram_id: str, username: str = "", first_name: str = "", last_name: str = "", referred_by: str = None) -> User:
        """Create a new user"""
        data = self.db.load_data()
        
        if str(telegram_id) in data["users"]:
            return self.get_user(telegram_id)
        
        user = User(telegram_id, username, first_name, last_name)
        if referred_by:
            user.referred_by = referred_by
        
        data["users"][str(telegram_id)] = user.to_dict()
        self.db.save_data(data)
        return user
    
    def get_user(self, telegram_id: str) -> Optional[User]:
        """Get user by telegram ID"""
        data = self.db.load_data()
        user_data = data["users"].get(str(telegram_id))
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def update_user(self, user: User):
        """Update user data"""
        data = self.db.load_data()
        user.last_active = datetime.now().isoformat()
        data["users"][user.telegram_id] = user.to_dict()
        self.db.save_data(data)
    
    def get_user_by_referral_code(self, referral_code: str) -> Optional[User]:
        """Get user by referral code"""
        data = self.db.load_data()
        for user_data in data["users"].values():
            if user_data.get("referral_code") == referral_code:
                return User.from_dict(user_data)
        return None
    
    def add_referral(self, referrer_id: str, referred_id: str, reward: int = 5):
        """Add referral and reward"""
        data = self.db.load_data()
        
        # Update referrer
        if referrer_id in data["users"]:
            referrer = data["users"][referrer_id]
            if referred_id not in referrer["referred_users"]:
                referrer["referred_users"].append(referred_id)
                referrer["wallet_balance"] += reward
                data["users"][referrer_id] = referrer
        
        # Update referred user
        if referred_id in data["users"]:
            referred = data["users"][referred_id]
            referred["referred_by"] = referrer_id
            data["users"][referred_id] = referred
        
        self.db.save_data(data)
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        data = self.db.load_data()
        return [User.from_dict(user_data) for user_data in data["users"].values()]
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        data = self.db.load_data()
        total_users = len(data["users"])
        active_users = sum(1 for user in data["users"].values() if user.get("joined_channel", False))
        total_withdrawals = len(data.get("withdrawals", []))
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_withdrawals": total_withdrawals
        }

class WithdrawalRepository:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_withdrawal_request(self, telegram_id: str, amount: int, upi_id: str):
        """Create withdrawal request"""
        data = self.db.load_data()
        
        withdrawal = {
            "id": str(uuid.uuid4()),
            "telegram_id": telegram_id,
            "amount": amount,
            "upi_id": upi_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "processed_at": None
        }
        
        if "withdrawals" not in data:
            data["withdrawals"] = []
        
        data["withdrawals"].append(withdrawal)
        self.db.save_data(data)
        return withdrawal
    
    def get_user_withdrawals(self, telegram_id: str):
        """Get user withdrawal history"""
        data = self.db.load_data()
        return [w for w in data.get("withdrawals", []) if w["telegram_id"] == telegram_id]
    
    def get_all_withdrawals(self):
        """Get all withdrawal requests"""
        data = self.db.load_data()
        return data.get("withdrawals", [])
    
    def update_withdrawal_status(self, withdrawal_id: str, status: str):
        """Update withdrawal status"""
        data = self.db.load_data()
        for withdrawal in data.get("withdrawals", []):
            if withdrawal["id"] == withdrawal_id:
                withdrawal["status"] = status
                withdrawal["processed_at"] = datetime.now().isoformat()
                break
        self.db.save_data(data)

