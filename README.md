# ROYAL EARNING - Telegram Referral Bot System

A complete Telegram referral bot system with admin panel for managing users and withdrawals.

## Features

- 🤖 **Telegram Bot**: Automated referral system with channel verification
- 💰 **Wallet System**: Track earnings and process withdrawals
- 👥 **Referral System**: Earn ₹5 per successful referral
- 💳 **UPI Integration**: Set UPI ID for easy withdrawals
- 📊 **Admin Panel**: Modern web interface for user and withdrawal management
- 🔒 **Secure**: JWT-based authentication for admin access

## Bot Features

### For Users:
- **Channel Verification**: Must join channel before accessing bot
- **Referral Links**: Generate unique referral links
- **Wallet Management**: View balance and referral count
- **UPI Setup**: Set UPI ID for withdrawals
- **Withdrawal Requests**: Request payouts (minimum ₹100)
- **Help System**: Built-in usage instructions

### For Admins:
- **Dashboard**: Overview of users, withdrawals, and statistics
- **User Management**: View all users, edit balances
- **Withdrawal Processing**: Approve/reject withdrawal requests
- **Real-time Updates**: Live data refresh
- **Responsive Design**: Works on desktop and mobile

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Quick Setup

1. **Extract the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (edit `.env` file):
   ```
   BOT_TOKEN=your_bot_token_here
   CHANNEL_ID=@your_channel_username
   CHANNEL_URL=https://t.me/your_channel
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_admin_password
   ```

4. **Start the system**:
   ```bash
   python start.py
   ```

## Configuration

### Environment Variables (.env)

```bash
# Telegram Bot Configuration
BOT_TOKEN=7616948328:AAE558BkB5uW00Uy2vAzchBATIK7BAKeVkM
BOT_URL=http://t.me/royal_earning_official_bot
CHANNEL_URL=https://t.me/royal_earning_official
CHANNEL_ID=@royal_earning_official

# Admin Panel Configuration
ADMIN_USERNAME=royal_earning
ADMIN_PASSWORD=Rishi@748

# App Configuration
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
FLASK_DEBUG=False

# Referral Configuration
REFERRAL_REWARD=5
MIN_WITHDRAWAL=100
```

## Deployment

### cPanel Hosting

1. **Upload files** to your cPanel file manager
2. **Install Python dependencies** via terminal:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up Python app** in cPanel:
   - Application root: `/path/to/royal_earning_bot`
   - Application startup file: `start.py`
   - Application entry point: `start_system`

4. **Configure domain** to point to the application

### VPS/Dedicated Server

1. **Clone or upload** the project files
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run with systemd** (recommended):
   ```bash
   sudo systemctl enable royal-earning-bot
   sudo systemctl start royal-earning-bot
   ```

## Usage

### Starting the System

```bash
python start.py
```

This will start both:
- Telegram bot (background)
- Admin panel web server (http://localhost:5000)

### Admin Panel Access

1. Open `http://your-domain.com` or `http://localhost:5000`
2. Login with admin credentials
3. Manage users and withdrawals

### Bot Commands

- `/start` - Start the bot and join system
- `/start REFERRAL_CODE` - Join via referral link

### Bot Menu Options

- 🔗 **Get Referral Link** - Generate your referral link
- 💰 **Wallet** - View balance and withdrawal options
- 💳 **Set UPI ID** - Configure UPI for withdrawals
- ❓ **How to Use Bot** - Usage instructions

## File Structure

```
royal_earning_bot/
├── app.py                 # Main Flask application
├── start.py              # System startup script
├── requirements.txt      # Python dependencies
├── .env                 # Environment configuration
├── README.md            # This file
├── bot/
│   └── telegram_bot.py  # Telegram bot implementation
├── database/
│   ├── models.py        # Database models and operations
│   └── users.json       # User data storage (auto-created)
└── templates/
    └── admin.html       # Admin panel frontend
```

## API Endpoints

### Admin Authentication
- `POST /api/admin/login` - Admin login
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/users` - Get all users
- `POST /api/admin/users/balance` - Update user balance
- `GET /api/admin/withdrawals` - Get withdrawal requests
- `POST /api/admin/withdrawals/approve` - Approve withdrawal
- `POST /api/admin/withdrawals/reject` - Reject withdrawal

### Health Check
- `GET /api/health` - System health status

## Database

The system uses JSON file storage for simplicity and cPanel compatibility:
- `database/users.json` - User data and referrals
- Automatic backup and data integrity
- Easy to migrate to MongoDB if needed

## Security Features

- JWT-based admin authentication
- Input validation and sanitization
- CORS protection
- Secure password handling
- Rate limiting (built into Telegram API)

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check bot token in `.env`
   - Verify bot is started with `/start` command
   - Check internet connection

2. **Admin panel not loading**:
   - Verify Flask is running on correct port
   - Check firewall settings
   - Ensure all dependencies are installed

3. **Channel verification failing**:
   - Verify channel ID format (@channel_username)
   - Ensure bot is admin in the channel
   - Check channel privacy settings

### Logs

Check console output for detailed error messages and system status.

## Support

For technical support or customization requests, contact the development team.

## License

This project is licensed under the MIT License.

---

**ROYAL EARNING Bot System v1.0**  
*Powered by ROYAL RISHI*

