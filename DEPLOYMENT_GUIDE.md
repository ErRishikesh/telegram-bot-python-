# ROYAL EARNING Bot - cPanel Deployment Guide

## Quick Setup for cPanel Hosting

### Step 1: Upload Files
1. Extract the `royal_earning_bot.zip` file
2. Upload all files to your cPanel File Manager in the `public_html` directory
3. Ensure all files maintain their directory structure

### Step 2: Configure Python App (cPanel)
1. Go to **Python App** in cPanel
2. Click **Create Application**
3. Set the following:
   - **Python Version**: 3.7+ (latest available)
   - **Application Root**: `/public_html/royal_earning_bot` (or your upload path)
   - **Application URL**: Your domain or subdomain
   - **Application Startup File**: `start.py`
   - **Application Entry Point**: `start_system`

### Step 3: Install Dependencies
1. In the Python App interface, click **Open Terminal**
2. Run the following commands:
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Configure Environment
1. Edit the `.env` file with your actual values:
   ```
   BOT_TOKEN=your_actual_bot_token
   CHANNEL_ID=@your_channel_username
   CHANNEL_URL=https://t.me/your_channel
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_secure_password
   ```

### Step 5: Start the Application
1. In cPanel Python App, click **Restart**
2. Your bot system will be available at your domain
3. Admin panel: `https://yourdomain.com`

## Alternative Setup (Shared Hosting)

If Python App is not available in your cPanel:

### Option 1: Manual Setup
1. Upload files to `public_html`
2. Use SSH (if available) to install dependencies:
   ```bash
   cd public_html/royal_earning_bot
   pip3 install --user -r requirements.txt
   python3 start.py
   ```

### Option 2: Contact Hosting Provider
- Ask your hosting provider to enable Python support
- Request installation of required Python packages

## Configuration Details

### Bot Token Setup
1. Go to [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot or use existing token
3. Copy the token to `.env` file

### Channel Setup
1. Create a Telegram channel
2. Add your bot as an administrator
3. Get the channel username (e.g., @your_channel)
4. Update `.env` with channel details

### Admin Credentials
- Change default admin username and password in `.env`
- Use strong passwords for security

## File Permissions
Ensure the following permissions:
- `start.py`: 755
- `app.py`: 755
- `database/` folder: 755
- All `.py` files: 644

## Troubleshooting

### Common Issues:

1. **Bot not responding**:
   - Check bot token in `.env`
   - Verify bot is started with `/start` command
   - Check server logs for errors

2. **Admin panel not loading**:
   - Verify Python app is running
   - Check file permissions
   - Ensure all dependencies are installed

3. **Database errors**:
   - Check if `database/` folder is writable
   - Verify JSON file permissions

4. **Channel verification failing**:
   - Ensure bot is admin in the channel
   - Check channel ID format (@channel_username)
   - Verify channel is public or bot has access

### Support Files:
- `app.py` - Main Flask application
- `start.py` - System startup script
- `bot/telegram_bot.py` - Telegram bot logic
- `database/models.py` - Database operations
- `templates/admin.html` - Admin panel interface

## Security Notes
- Change default admin credentials immediately
- Use HTTPS for production deployment
- Regularly backup the `database/users.json` file
- Monitor server logs for suspicious activity

## Performance Tips
- For high traffic, consider upgrading to VPS
- Use process managers like PM2 for production
- Implement rate limiting for API endpoints
- Regular database cleanup and optimization

---

**Need Help?**
Contact your hosting provider for Python app setup assistance or server configuration issues.

