import telebot
import os
import re
from dotenv import load_dotenv
from telebot import types
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import UserRepository, WithdrawalRepository

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_URL = os.getenv('CHANNEL_URL')
BOT_URL = os.getenv('BOT_URL')
REFERRAL_REWARD = int(os.getenv('REFERRAL_REWARD', 5))
MIN_WITHDRAWAL = int(os.getenv('MIN_WITHDRAWAL', 100))

bot = telebot.TeleBot(BOT_TOKEN)
user_repo = UserRepository()
withdrawal_repo = WithdrawalRepository()

# User states for conversation flow
user_states = {}

def is_user_in_channel(user_id):
    """Check if user is member of the required channel"""
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def create_main_keyboard():
    """Create main menu keyboard"""
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("🔗 Get Referral Link"),
        types.KeyboardButton("💰 Wallet")
    )
    keyboard.add(
        types.KeyboardButton("💳 Set UPI ID"),
        types.KeyboardButton("❓ How to Use Bot")
    )
    return keyboard

def create_channel_keyboard():
    """Create keyboard for channel subscription"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL),
        types.InlineKeyboardButton("✅ Verify", callback_data="verify_channel")
    )
    return keyboard

def create_wallet_keyboard():
    """Create wallet keyboard"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"))
    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    
    # Check for referral code in start command
    referral_code = None
    if len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
    
    # Check if user exists
    user = user_repo.get_user(user_id)
    
    if not user:
        # Create new user
        referred_by = None
        if referral_code:
            referrer = user_repo.get_user_by_referral_code(referral_code)
            if referrer and referrer.telegram_id != user_id:
                referred_by = referrer.telegram_id
        
        user = user_repo.create_user(user_id, username, first_name, last_name, referred_by)
        
        # If referred by someone, add referral after channel verification
        if referred_by:
            user_states[user_id] = {'pending_referral': referred_by}
    
    # Check channel membership
    if not is_user_in_channel(user_id):
        welcome_text = f"""
🎉 Welcome to ROYAL EARNING Bot! 🎉

Hello {first_name}! To start earning, you need to:

1️⃣ Join our official channel
2️⃣ Verify your membership
3️⃣ Start earning through referrals!

💰 Earn ₹{REFERRAL_REWARD} for each successful referral!
💸 Minimum withdrawal: ₹{MIN_WITHDRAWAL}

Please join our channel first:
        """
        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=create_channel_keyboard()
        )
    else:
        user.joined_channel = True
        user_repo.update_user(user)
        
        # Process pending referral if any
        if user_id in user_states and 'pending_referral' in user_states[user_id]:
            referrer_id = user_states[user_id]['pending_referral']
            user_repo.add_referral(referrer_id, user_id, REFERRAL_REWARD)
            del user_states[user_id]
            
            # Notify referrer
            try:
                referrer = user_repo.get_user(referrer_id)
                bot.send_message(
                    referrer_id,
                    f"🎉 Congratulations! You earned ₹{REFERRAL_REWARD} from a new referral!\n💰 New Balance: ₹{referrer.wallet_balance + REFERRAL_REWARD}"
                )
            except:
                pass
        
        show_main_menu(message)

def show_main_menu(message):
    """Show main menu to verified users"""
    user_id = str(message.from_user.id)
    user = user_repo.get_user(user_id)
    
    welcome_text = f"""
🎉 Welcome to ROYAL EARNING! 🎉

Hello {message.from_user.first_name}!

💰 Current Balance: ₹{user.wallet_balance if user else 0}
👥 Total Referrals: {len(user.referred_users) if user else 0}

Choose an option below:
    """
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=create_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "verify_channel")
def verify_channel(call):
    user_id = str(call.from_user.id)
    
    if is_user_in_channel(user_id):
        user = user_repo.get_user(user_id)
        if user:
            user.joined_channel = True
            user_repo.update_user(user)
        
        # Process pending referral if any
        if user_id in user_states and 'pending_referral' in user_states[user_id]:
            referrer_id = user_states[user_id]['pending_referral']
            user_repo.add_referral(referrer_id, user_id, REFERRAL_REWARD)
            del user_states[user_id]
            
            # Notify referrer
            try:
                referrer = user_repo.get_user(referrer_id)
                bot.send_message(
                    referrer_id,
                    f"🎉 Congratulations! You earned ₹{REFERRAL_REWARD} from a new referral!\n💰 New Balance: ₹{referrer.wallet_balance + REFERRAL_REWARD}"
                )
            except:
                pass
        
        bot.edit_message_text(
            "✅ Channel membership verified successfully!",
            call.message.chat.id,
            call.message.message_id
        )
        
        show_main_menu(call.message)
    else:
        bot.answer_callback_query(
            call.id,
            "❌ Please join the channel first!",
            show_alert=True
        )

@bot.message_handler(func=lambda message: message.text == "🔗 Get Referral Link")
def get_referral_link(message):
    user_id = str(message.from_user.id)
    
    if not is_user_in_channel(user_id):
        bot.send_message(
            message.chat.id,
            "❌ Please join our channel first!",
            reply_markup=create_channel_keyboard()
        )
        return
    
    user = user_repo.get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "❌ User not found. Please use /start")
        return
    
    referral_link = f"{BOT_URL}?start={user.referral_code}"
    
    referral_text = f"""
🔗 Your Referral Link:

{referral_link}

📋 How it works:
• Share this link with friends
• When they join through your link and subscribe to our channel
• You earn ₹{REFERRAL_REWARD} instantly!

💰 Current Stats:
• Total Referrals: {len(user.referred_users)}
• Wallet Balance: ₹{user.wallet_balance}

Share and start earning! 🚀
    """
    
    bot.send_message(message.chat.id, referral_text)

@bot.message_handler(func=lambda message: message.text == "💰 Wallet")
def show_wallet(message):
    user_id = str(message.from_user.id)
    
    if not is_user_in_channel(user_id):
        bot.send_message(
            message.chat.id,
            "❌ Please join our channel first!",
            reply_markup=create_channel_keyboard()
        )
        return
    
    user = user_repo.get_user(user_id)
    if not user:
        bot.send_message(message.chat.id, "❌ User not found. Please use /start")
        return
    
    withdrawals = withdrawal_repo.get_user_withdrawals(user_id)
    pending_withdrawals = [w for w in withdrawals if w['status'] == 'pending']
    total_withdrawn = sum(w['amount'] for w in withdrawals if w['status'] == 'approved')
    
    wallet_text = f"""
💰 Your Wallet

💵 Current Balance: ₹{user.wallet_balance}
👥 Total Referrals: {len(user.referred_users)}
💸 Total Withdrawn: ₹{total_withdrawn}
⏳ Pending Withdrawals: {len(pending_withdrawals)}

💳 UPI ID: {user.upi_id if user.upi_id else "Not Set"}

Minimum withdrawal: ₹{MIN_WITHDRAWAL}
    """
    
    keyboard = None
    if user.wallet_balance >= MIN_WITHDRAWAL and user.upi_id:
        keyboard = create_wallet_keyboard()
    
    bot.send_message(message.chat.id, wallet_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "withdraw")
def initiate_withdrawal(call):
    user_id = str(call.from_user.id)
    user = user_repo.get_user(user_id)
    
    if not user or user.wallet_balance < MIN_WITHDRAWAL:
        bot.answer_callback_query(
            call.id,
            f"❌ Minimum balance required: ₹{MIN_WITHDRAWAL}",
            show_alert=True
        )
        return
    
    if not user.upi_id:
        bot.answer_callback_query(
            call.id,
            "❌ Please set your UPI ID first!",
            show_alert=True
        )
        return
    
    # Create withdrawal request
    withdrawal = withdrawal_repo.create_withdrawal_request(
        user_id, user.wallet_balance, user.upi_id
    )
    
    # Deduct amount from wallet
    user.wallet_balance = 0
    user_repo.update_user(user)
    
    bot.edit_message_text(
        f"✅ Withdrawal request submitted!\n\n💸 Amount: ₹{withdrawal['amount']}\n💳 UPI ID: {withdrawal['upi_id']}\n\nYour request will be processed within 24-48 hours.",
        call.message.chat.id,
        call.message.message_id
    )

@bot.message_handler(func=lambda message: message.text == "💳 Set UPI ID")
def set_upi_id(message):
    user_id = str(message.from_user.id)
    
    if not is_user_in_channel(user_id):
        bot.send_message(
            message.chat.id,
            "❌ Please join our channel first!",
            reply_markup=create_channel_keyboard()
        )
        return
    
    user_states[user_id] = 'waiting_upi'
    
    bot.send_message(
        message.chat.id,
        "💳 Please enter your UPI ID:\n\nExample: yourname@paytm, yourname@phonepe, etc.\n\n⚠️ Make sure your UPI ID is correct as payments will be sent to this ID."
    )

@bot.message_handler(func=lambda message: message.text == "❓ How to Use Bot")
def how_to_use(message):
    help_text = f"""
❓ How to Use ROYAL EARNING Bot

🎯 Step-by-Step Guide:

1️⃣ Join our official channel
2️⃣ Get your unique referral link
3️⃣ Share with friends and family
4️⃣ Earn ₹{REFERRAL_REWARD} for each successful referral
5️⃣ Set your UPI ID for withdrawals
6️⃣ Withdraw when you reach ₹{MIN_WITHDRAWAL}

💰 Earning Rules:
• Each person who joins through your link = ₹{REFERRAL_REWARD}
• They must join the channel to complete referral
• No limit on referrals!

💸 Withdrawal Rules:
• Minimum withdrawal: ₹{MIN_WITHDRAWAL}
• Set UPI ID before withdrawal
• Processing time: 24-48 hours
• No withdrawal fees!

🚀 Start sharing and earning now!

Channel: {CHANNEL_URL}
    """
    
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = str(message.from_user.id)
    
    # Handle UPI ID input
    if user_id in user_states and user_states[user_id] == 'waiting_upi':
        upi_text = message.text.strip()
        
        # Basic UPI ID validation
        if '@' not in upi_text or len(upi_text) < 5:
            bot.send_message(
                message.chat.id,
                "❌ Invalid UPI ID format. Please enter a valid UPI ID like: yourname@paytm"
            )
            return
        
        user = user_repo.get_user(user_id)
        if user:
            user.upi_id = upi_text
            user_repo.update_user(user)
            
            del user_states[user_id]
            
            bot.send_message(
                message.chat.id,
                f"✅ UPI ID set successfully!\n\n💳 Your UPI ID: {upi_text}\n\nYou can now withdraw your earnings when you reach ₹{MIN_WITHDRAWAL}!"
            )
        return
    
    # Default response for unrecognized messages
    if not is_user_in_channel(user_id):
        bot.send_message(
            message.chat.id,
            "❌ Please join our channel first!",
            reply_markup=create_channel_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            "Please use the menu buttons below 👇",
            reply_markup=create_main_keyboard()
        )

def run_bot():
    """Run the Telegram bot"""
    print("🤖 ROYAL EARNING Bot is starting...")
    print(f"📢 Channel: {CHANNEL_URL}")
    print(f"🔗 Bot URL: {BOT_URL}")
    bot.infinity_polling()

if __name__ == "__main__":
    run_bot()

