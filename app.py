from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import threading
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import UserRepository, WithdrawalRepository
from bot.telegram_bot import run_bot

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'royal_earning_secret_key_2024')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'royal_earning')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Rishi@748')

# Initialize repositories
user_repo = UserRepository()
withdrawal_repo = WithdrawalRepository()

def verify_admin_token(token):
    """Verify admin JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload.get('username') == ADMIN_USERNAME
    except:
        return False

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        if not verify_admin_token(token):
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def admin_panel():
    """Serve the admin panel"""
    return render_template('admin.html')

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Generate JWT token
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'message': 'Login successful'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid credentials'
        }), 401

@app.route('/api/admin/stats', methods=['GET'])
@require_admin_auth
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = user_repo.get_user_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/users', methods=['GET'])
@require_admin_auth
def get_users():
    """Get all users"""
    try:
        users = user_repo.get_all_users()
        users_data = [user.to_dict() for user in users]
        
        return jsonify({
            'success': True,
            'users': users_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/users/balance', methods=['POST'])
@require_admin_auth
def update_user_balance():
    """Update user balance"""
    try:
        data = request.get_json()
        telegram_id = data.get('telegram_id')
        new_balance = data.get('new_balance')
        
        if not telegram_id or new_balance is None:
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        user = user_repo.get_user(telegram_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user.wallet_balance = int(new_balance)
        user_repo.update_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Balance updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/withdrawals', methods=['GET'])
@require_admin_auth
def get_withdrawals():
    """Get all withdrawal requests"""
    try:
        withdrawals = withdrawal_repo.get_all_withdrawals()
        
        return jsonify({
            'success': True,
            'withdrawals': withdrawals
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/withdrawals/approve', methods=['POST'])
@require_admin_auth
def approve_withdrawal():
    """Approve withdrawal request"""
    try:
        data = request.get_json()
        withdrawal_id = data.get('withdrawal_id')
        
        if not withdrawal_id:
            return jsonify({
                'success': False,
                'message': 'Withdrawal ID required'
            }), 400
        
        withdrawal_repo.update_withdrawal_status(withdrawal_id, 'approved')
        
        return jsonify({
            'success': True,
            'message': 'Withdrawal approved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/withdrawals/reject', methods=['POST'])
@require_admin_auth
def reject_withdrawal():
    """Reject withdrawal request"""
    try:
        data = request.get_json()
        withdrawal_id = data.get('withdrawal_id')
        
        if not withdrawal_id:
            return jsonify({
                'success': False,
                'message': 'Withdrawal ID required'
            }), 400
        
        # Find the withdrawal and restore user balance
        withdrawals = withdrawal_repo.get_all_withdrawals()
        withdrawal = next((w for w in withdrawals if w['id'] == withdrawal_id), None)
        
        if withdrawal and withdrawal['status'] == 'pending':
            # Restore balance to user
            user = user_repo.get_user(withdrawal['telegram_id'])
            if user:
                user.wallet_balance += withdrawal['amount']
                user_repo.update_user(user)
        
        withdrawal_repo.update_withdrawal_status(withdrawal_id, 'rejected')
        
        return jsonify({
            'success': True,
            'message': 'Withdrawal rejected and balance restored'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'ROYAL EARNING Bot'
    })

def start_bot_in_thread():
    """Start the Telegram bot in a separate thread"""
    try:
        print("🤖 Starting Telegram bot...")
        run_bot()
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == '__main__':
    # Start the Telegram bot in a separate thread
    bot_thread = threading.Thread(target=start_bot_in_thread, daemon=True)
    bot_thread.start()
    
    # Start the Flask app
    print("🚀 Starting ROYAL EARNING Bot System...")
    print("📊 Admin Panel: http://localhost:5000")
    print(f"👤 Admin Username: {ADMIN_USERNAME}")
    print(f"🔑 Admin Password: {ADMIN_PASSWORD}")
    
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )

