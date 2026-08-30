
---

### `main.py`

```python
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load environment variables
load_dotenv()

# ===== LOGGING =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# ===== DATABASE (In-memory for demo - use PostgreSQL in production) =====
users_data: Dict[int, Dict] = {}

def get_user_data(user_id: int) -> Dict:
    """Get or create user data."""
    if user_id not in users_data:
        users_data[user_id] = {
            "points": 0,
            "streak": 0,
            "first_name": "",
            "last_bonus_date": None,
            "bonuses_claimed": 0,
            "tips_received": [],
        }
    return users_data[user_id]

# ===== GAMING TIPS =====
GAMING_TIPS = [
    "🎯 Practice tracking moving targets in aim trainers for 15 minutes daily.",
    "🧠 Take a 5-minute break between matches to reset your focus.",
    "⚙️ Lower your sensitivity gradually for better micro-adjustments.",
    "📊 Watch your replays to identify positioning mistakes.",
    "🎮 Warm up with 10 minutes of practice mode before competitive matches.",
    "🔥 Focus on one skill to improve each week.",
    "📝 Take notes after each match to track your progress.",
    "🎯 Keep crosshair at head level at all times.",
    "🧘 Practice mindfulness during gameplay for better focus.",
    "⚡ Optimize your settings for higher FPS.",
    "🎮 Play with a consistent team to build chemistry.",
    "📈 Track your win rate over time to measure improvement.",
]

# ===== BONUS REWARDS =====
BONUS_REWARDS = [
    "🎁 +10 points",
    "🎁 +15 points",
    "🎁 +20 points",
    "🎁 +25 points",
    "🎁 +30 points",
    "🎁 +50 points (🌟 BONUS!)",
    "🎁 +5 points + a gaming tip",
    "🎁 +10 points + a special tip",
]

# ===== KEYBOARDS =====

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create the main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("🎁 Claim Daily Bonus", callback_data="bonus")],
        [InlineKeyboardButton("💡 Gaming Tips", callback_data="tips")],
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_menu_keyboard() -> InlineKeyboardMarkup:
    """Create a keyboard with back to menu button."""
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    return InlineKeyboardMarkup(keyboard)

def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for stats page."""
    keyboard = [
        [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== COMMAND HANDLERS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "Player"
    
    # Initialize user data
    user_data = get_user_data(user_id)
    user_data["first_name"] = first_name
    
    welcome_text = f"""🎮 *Welcome to Day2Day Bonus, {first_name}!*

Get daily gaming bonuses, rewards, and tips — completely free!

*Here's what I can do for you:*
🎁 *Daily Bonus* - Claim your reward every day
💡 *Gaming Tips* - Improve your skills
📊 *Track Stats* - Monitor your progress
🏆 *Leaderboard* - Compete with others

*No gambling. Just rewards for playing smart.* 🎯

Tap a button below to get started!"""

    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when /help is issued."""
    help_text = """📖 *Day2Day Bonus - Help*

*Commands:*
/start - Main menu
/help - This message
/bonus - Claim your daily bonus
/stats - Your stats
/leaderboard - Top players
/tips - Get gaming tips

*How it works:*
1️⃣ Claim your daily bonus
2️⃣ Earn points and build streaks
3️⃣ Get gaming tips
4️⃣ Compete on the leaderboard

*Everything is free - no gambling!* 🎮"""

    await update.message.reply_text(
        help_text,
        reply_markup=get_back_menu_keyboard(),
        parse_mode="Markdown",
    )


async def bonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Claim daily bonus."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    first_name = user_data.get("first_name", update.effective_user.first_name or "Player")
    
    today = datetime.now().date()
    
    # Check if already claimed today
    if user_data.get("last_bonus_date") == today:
        await update.message.reply_text(
            f"⏰ *You've already claimed your bonus today, {first_name}!*\n\n"
            f"Come back tomorrow for another reward. 🌟\n\n"
            f"📊 Points: {user_data['points']} | Streak: {user_data['streak']} days",
            reply_markup=get_stats_keyboard(),
            parse_mode="Markdown",
        )
        return
    
    # Calculate bonus
    bonus_amount = random.randint(5, 30)
    
    # Bonus multipliers for streaks
    if user_data["streak"] >= 7:
        bonus_amount = int(bonus_amount * 1.5)
        bonus_message = "🔥 *7-Day Streak Bonus!* +50% extra!"
    elif user_data["streak"] >= 3:
        bonus_amount = int(bonus_amount * 1.2)
        bonus_message = "⭐ *3-Day Streak Bonus!* +20% extra!"
    else:
        bonus_message = "🎁 *Daily Bonus claimed!*"
    
    # Update user data
    user_data["points"] += bonus_amount
    user_data["bonuses_claimed"] += 1
    
    # Update streak
    if user_data.get("last_bonus_date") == today - timedelta(days=1):
        user_data["streak"] += 1
    else:
        user_data["streak"] = 1
    
    user_data["last_bonus_date"] = today
    
    # Random tip to include sometimes
    tip = random.choice(GAMING_TIPS) if random.random() < 0.3 else None
    
    bonus_text = f"""🎉 *Bonus Claimed, {first_name}!*

{bonus_message}

✨ *+{bonus_amount} points earned!*
📊 Points: {user_data['points']}
🔥 Streak: {user_data['streak']} days
📅 Total Bonuses: {user_data['bonuses_claimed']}

{f"💡 *Tip of the day:* {tip}" if tip else "Keep playing smart! 🎮"}"""

    keyboard = [
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("💡 More Tips", callback_data="tips")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        bonus_text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user stats."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    first_name = user_data.get("first_name", update.effective_user.first_name or "Player")
    
    # Calculate rank
    sorted_users = sorted(
        users_data.items(),
        key=lambda x: x[1]["points"],
        reverse=True
    )
    rank = next(
        (i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id),
        len(users_data),
    )
    
    stats_text = f"""📊 *My Stats*

👤 Player: {first_name}
⭐ Points: {user_data['points']}
🔥 Streak: {user_data['streak']} days
🎁 Bonuses Claimed: {user_data['bonuses_claimed']}
🏆 Rank: #{rank} on leaderboard

Keep claiming your daily bonus! 🎮"""

    await update.message.reply_text(
        stats_text,
        reply_markup=get_stats_keyboard(),
        parse_mode="Markdown",
    )


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show leaderboard."""
    if not users_data:
        leaderboard_text = "🏆 *Leaderboard*\n\nNo players yet! Be the first to claim a bonus! 🎮"
    else:
        sorted_users = sorted(
            users_data.items(),
            key=lambda x: x[1]["points"],
            reverse=True
        )
        
        leaderboard_text = "🏆 *Leaderboard*\n\n"
        for i, (user_id, data) in enumerate(sorted_users[:10], 1):
            first_name = data.get("first_name", f"Player_{str(user_id)[:6]}")
            points = data["points"]
            streak = data["streak"]
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            leaderboard_text += f"{medal} {first_name} - {points} pts ({streak}d)\n"
    
    keyboard = [
        [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        leaderboard_text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show gaming tips."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    # Get tips user hasn't seen
    seen_indices = set(user_data.get("tips_received", []))
    available_tips = [i for i in range(len(GAMING_TIPS)) if i not in seen_indices]
    
    if available_tips:
        tip_index = random.choice(available_tips[:5])  # Pick from first 5 available
        tip = GAMING_TIPS[tip_index]
        user_data["tips_received"] = user_data.get("tips_received", []) + [tip_index]
    else:
        # Reset and give random tip
        tip = random.choice(GAMING_TIPS)
        user_data["tips_received"] = []
    
    tips_text = f"""💡 *Gaming Tip*

{tip}

💪 *Pro tip:* Apply this in your next gaming session!

📊 Points: {user_data['points']} | Streak: {user_data['streak']} days
📚 Tips received: {len(user_data.get('tips_received', []))}"""

    keyboard = [
        [InlineKeyboardButton("💡 Another Tip", callback_data="tips")],
        [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        tips_text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


# ===== CALLBACK QUERY HANDLERS =====

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    first_name = user_data.get("first_name", update.effective_user.first_name or "Player")
    
    if data == "menu":
        welcome_text = f"""🎮 *Welcome back, {first_name}!*

What would you like to do?"""
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown",
        )
    
    elif data == "bonus":
        today = datetime.now().date()
        
        if user_data.get("last_bonus_date") == today:
            await query.edit_message_text(
                f"⏰ *You've already claimed your bonus today, {first_name}!*\n\n"
                f"Come back tomorrow for another reward. 🌟\n\n"
                f"📊 Points: {user_data['points']} | Streak: {user_data['streak']} days",
                reply_markup=get_stats_keyboard(),
                parse_mode="Markdown",
            )
            return
        
        # Calculate bonus
        bonus_amount = random.randint(5, 30)
        
        if user_data["streak"] >= 7:
            bonus_amount = int(bonus_amount * 1.5)
            bonus_message = "🔥 *7-Day Streak Bonus!* +50% extra!"
        elif user_data["streak"] >= 3:
            bonus_amount = int(bonus_amount * 1.2)
            bonus_message = "⭐ *3-Day Streak Bonus!* +20% extra!"
        else:
            bonus_message = "🎁 *Daily Bonus claimed!*"
        
        user_data["points"] += bonus_amount
        user_data["bonuses_claimed"] += 1
        
        if user_data.get("last_bonus_date") == today - timedelta(days=1):
            user_data["streak"] += 1
        else:
            user_data["streak"] = 1
        
        user_data["last_bonus_date"] = today
        
        tip = random.choice(GAMING_TIPS) if random.random() < 0.3 else None
        
        bonus_text = f"""🎉 *Bonus Claimed, {first_name}!*

{bonus_message}

✨ *+{bonus_amount} points earned!*
📊 Points: {user_data['points']}
🔥 Streak: {user_data['streak']} days
📅 Total Bonuses: {user_data['bonuses_claimed']}

{f"💡 *Tip of the day:* {tip}" if tip else "Keep playing smart! 🎮"}"""
        
        keyboard = [
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("💡 More Tips", callback_data="tips")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            bonus_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    
    elif data == "stats":
        sorted_users = sorted(
            users_data.items(),
            key=lambda x: x[1]["points"],
            reverse=True
        )
        rank = next(
            (i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == user_id),
            len(users_data),
        )
        
        stats_text = f"""📊 *My Stats*

👤 Player: {first_name}
⭐ Points: {user_data['points']}
🔥 Streak: {user_data['streak']} days
🎁 Bonuses Claimed: {user_data['bonuses_claimed']}
🏆 Rank: #{rank} on leaderboard

Keep claiming your daily bonus! 🎮"""
        
        await query.edit_message_text(
            stats_text,
            reply_markup=get_stats_keyboard(),
            parse_mode="Markdown",
        )
    
    elif data == "leaderboard":
        if not users_data:
            leaderboard_text = "🏆 *Leaderboard*\n\nNo players yet! Be the first to claim a bonus! 🎮"
        else:
            sorted_users = sorted(
                users_data.items(),
                key=lambda x: x[1]["points"],
                reverse=True
            )
            
            leaderboard_text = "🏆 *Leaderboard*\n\n"
            for i, (uid, data_dict) in enumerate(sorted_users[:10], 1):
                name = data_dict.get("first_name", f"Player_{str(uid)[:6]}")
                points = data_dict["points"]
                streak = data_dict["streak"]
                
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                leaderboard_text += f"{medal} {name} - {points} pts ({streak}d)\n"
        
        keyboard = [
            [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            leaderboard_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    
    elif data == "tips":
        seen_indices = set(user_data.get("tips_received", []))
        available_tips = [i for i in range(len(GAMING_TIPS)) if i not in seen_indices]
        
        if available_tips:
            tip_index = random.choice(available_tips[:5])
            tip = GAMING_TIPS[tip_index]
            user_data["tips_received"] = user_data.get("tips_received", []) + [tip_index]
        else:
            tip = random.choice(GAMING_TIPS)
            user_data["tips_received"] = []
        
        tips_text = f"""💡 *Gaming Tip*

{tip}

💪 *Pro tip:* Apply this in your next gaming session!

📊 Points: {user_data['points']} | Streak: {user_data['streak']} days
📚 Tips received: {len(user_data.get('tips_received', []))}"""
        
        keyboard = [
            [InlineKeyboardButton("💡 Another Tip", callback_data="tips")],
            [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            tips_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )


# ===== ERROR HANDLER =====

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


# ===== MAIN FUNCTION =====

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("bonus", bonus_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("tips", tips_command))
    
    # Register callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Register error handler
    application.add_error_handler(error_handler)

    # Run the bot
    print("🚀 Day2Day Bonus Bot is running...")
    print("🤖 Bot username: @day2day_bonusbot")
    print("📋 Available commands: /start, /help, /bonus, /stats, /leaderboard, /tips")
    print("⚠️  Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
