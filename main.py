import logging
import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
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
    print("❌ ERROR: BOT_TOKEN not found in .env file!")
    print("Please create a .env file with: BOT_TOKEN=your_token_here")
    exit(1)

print("✅ BOT_TOKEN loaded successfully!")

# ===== DATABASE (In-memory) =====
users_data = {}

def get_user_data(user_id):
    if user_id not in users_data:
        users_data[user_id] = {
            "points": 0,
            "streak": 0,
            "first_name": "",
            "last_bonus_date": None,
            "bonuses_claimed": 0,
            "tips_received": [],
            "level": 1,
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
]

# ===== KEYBOARDS =====

def get_main_menu_keyboard():
    """Create the main menu keyboard with buttons."""
    keyboard = [
        [
            InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus"),
            InlineKeyboardButton("📊 My Stats", callback_data="stats"),
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
            InlineKeyboardButton("💡 Tips", callback_data="tips"),
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_menu_keyboard():
    """Create a keyboard with back to menu button."""
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
    return InlineKeyboardMarkup(keyboard)

# ===== COMMAND HANDLERS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message."""
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "Player"
    
    user_data = get_user_data(user_id)
    user_data["first_name"] = first_name
    
    # Calculate level based on points
    level = (user_data["points"] // 50) + 1
    user_data["level"] = level
    
    welcome_text = (
        f"🎮 Welcome to Day2Day Bonus, {first_name}!\n\n"
        f"Get daily gaming bonuses, rewards, and tips — completely free!\n\n"
        f"📊 Your Stats:\n"
        f"⭐ Points: {user_data['points']}\n"
        f"🔥 Streak: {user_data['streak']} days\n"
        f"📈 Level: {level}\n\n"
        f"Tap a button below to get started! 🚀"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
    )
    print(f"✅ /start executed for {first_name}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help message."""
    help_text = (
        "📖 Day2Day Bonus - Help\n\n"
        "Commands:\n"
        "/start - Main menu\n"
        "/help - This message\n"
        "/bonus - Claim your daily bonus\n"
        "/stats - Your stats\n"
        "/leaderboard - Top players\n"
        "/tips - Get gaming tips\n\n"
        "Everything is free - no gambling! 🎮"
    )
    
    await update.message.reply_text(
        help_text,
        reply_markup=get_back_menu_keyboard(),
    )


async def bonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Claim daily bonus."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    first_name = user_data.get("first_name", "Player")
    
    today = datetime.now().date()
    
    if user_data.get("last_bonus_date") == today:
        await update.message.reply_text(
            f"⏰ You've already claimed your bonus today, {first_name}!\n\n"
            f"Come back tomorrow for another reward. 🌟\n\n"
            f"📊 Points: {user_data['points']}\n"
            f"🔥 Streak: {user_data['streak']} days\n"
            f"📈 Level: {user_data['level']}",
            reply_markup=get_back_menu_keyboard(),
        )
        return
    
    # Calculate bonus
    bonus_amount = random.randint(5, 30)
    
    # Streak bonuses
    if user_data["streak"] >= 7:
        bonus_amount = int(bonus_amount * 1.5)
        bonus_message = "🔥 7-Day Streak Bonus! +50% extra!"
    elif user_data["streak"] >= 3:
        bonus_amount = int(bonus_amount * 1.2)
        bonus_message = "⭐ 3-Day Streak Bonus! +20% extra!"
    else:
        bonus_message = "Daily Bonus claimed! 🎁"
    
    # Update user data
    user_data["points"] += bonus_amount
    user_data["bonuses_claimed"] += 1
    
    # Update streak
    if user_data.get("last_bonus_date") == today - timedelta(days=1):
        user_data["streak"] += 1
    else:
        user_data["streak"] = 1
    
    user_data["last_bonus_date"] = today
    
    # Update level
    user_data["level"] = (user_data["points"] // 50) + 1
    
    bonus_text = (
        f"🎉 Bonus Claimed, {first_name}!\n\n"
        f"{bonus_message}\n\n"
        f"✨ +{bonus_amount} points earned!\n"
        f"📊 Points: {user_data['points']}\n"
        f"🔥 Streak: {user_data['streak']} days\n"
        f"📈 Level: {user_data['level']}\n"
        f"📅 Total Bonuses: {user_data['bonuses_claimed']}\n\n"
        f"Keep going! 🎮"
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        bonus_text,
        reply_markup=reply_markup,
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user stats."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    first_name = user_data.get("first_name", "Player")
    
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
    
    stats_text = (
        f"📊 My Stats\n\n"
        f"👤 Player: {first_name}\n"
        f"⭐ Points: {user_data['points']}\n"
        f"🔥 Streak: {user_data['streak']} days\n"
        f"🎁 Bonuses: {user_data['bonuses_claimed']}\n"
        f"📈 Level: {user_data['level']}\n"
        f"🏆 Rank: #{rank} on leaderboard\n\n"
        f"Keep claiming your daily bonus! 🎮"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        stats_text,
        reply_markup=reply_markup,
    )


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show leaderboard."""
    if not users_data:
        leaderboard_text = "🏆 Leaderboard\n\nNo players yet! Be the first to claim a bonus! 🎮"
    else:
        sorted_users = sorted(
            users_data.items(),
            key=lambda x: x[1]["points"],
            reverse=True
        )
        
        leaderboard_text = "🏆 Leaderboard\n\n"
        for i, (user_id, data) in enumerate(sorted_users[:10], 1):
            first_name = data.get("first_name", f"Player_{str(user_id)[:6]}")
            points = data["points"]
            streak = data["streak"]
            level = data.get("level", 1)
            
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            leaderboard_text += f"{medal} {first_name} - {points} pts (Lv.{level}, {streak}d)\n"
    
    keyboard = [
        [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        leaderboard_text,
        reply_markup=reply_markup,
    )


async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show gaming tips."""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    # Get random tip
    tip = random.choice(GAMING_TIPS)
    
    tips_text = (
        f"💡 Gaming Tip\n\n"
        f"{tip}\n\n"
        f"💪 Apply this in your next gaming session!\n\n"
        f"📊 Points: {user_data['points']}\n"
        f"🔥 Streak: {user_data['streak']} days"
    )
    
    keyboard = [
        [InlineKeyboardButton("💡 Another Tip", callback_data="tips")],
        [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        tips_text,
        reply_markup=reply_markup,
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About the bot."""
    about_text = (
        "ℹ️ About Day2Day Bonus\n\n"
        "This bot helps you stay consistent with your gaming goals.\n\n"
        "🎯 Features:\n"
        "• Daily Bonus claims\n"
        "• Streak multipliers\n"
        "• Level up system\n"
        "• Leaderboard competition\n\n"
        "📌 Made for gamers who want to play smarter.\n"
        "❌ No gambling. Just rewards for consistency.\n\n"
        "Start earning now! 🚀"
    )
    
    await update.message.reply_text(
        about_text,
        reply_markup=get_back_menu_keyboard(),
    )


# ===== CALLBACK HANDLER =====

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    first_name = user_data.get("first_name", "Player")
    
    if data == "menu":
        welcome_text = (
            f"🎮 Welcome back, {first_name}!\n\n"
            f"📊 Points: {user_data['points']}\n"
            f"🔥 Streak: {user_data['streak']} days\n"
            f"📈 Level: {user_data['level']}\n\n"
            f"What would you like to do?"
        )
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
        )
    
    elif data == "about":
        about_text = (
            "ℹ️ About Day2Day Bonus\n\n"
            "🎯 Features:\n"
            "• Daily Bonus claims\n"
            "• Streak multipliers\n"
            "• Level up system\n"
            "• Leaderboard competition\n\n"
            "❌ No gambling. Just rewards for consistency."
        )
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            about_text,
            reply_markup=reply_markup,
        )
    
    elif data == "bonus":
        today = datetime.now().date()
        
        if user_data.get("last_bonus_date") == today:
            await query.edit_message_text(
                f"⏰ You've already claimed today, {first_name}!\n\n"
                f"Come back tomorrow. 🌟\n\n"
                f"📊 Points: {user_data['points']}\n"
                f"🔥 Streak: {user_data['streak']} days",
                reply_markup=get_back_menu_keyboard(),
            )
            return
        
        bonus_amount = random.randint(5, 30)
        
        if user_data["streak"] >= 7:
            bonus_amount = int(bonus_amount * 1.5)
            bonus_message = "🔥 7-Day Streak! +50%"
        elif user_data["streak"] >= 3:
            bonus_amount = int(bonus_amount * 1.2)
            bonus_message = "⭐ 3-Day Streak! +20%"
        else:
            bonus_message = "Daily Bonus! 🎁"
        
        user_data["points"] += bonus_amount
        user_data["bonuses_claimed"] += 1
        
        if user_data.get("last_bonus_date") == today - timedelta(days=1):
            user_data["streak"] += 1
        else:
            user_data["streak"] = 1
        
        user_data["last_bonus_date"] = today
        user_data["level"] = (user_data["points"] // 50) + 1
        
        bonus_text = (
            f"🎉 Bonus Claimed!\n\n"
            f"{bonus_message}\n"
            f"✨ +{bonus_amount} points\n"
            f"📊 Points: {user_data['points']}\n"
            f"🔥 Streak: {user_data['streak']} days\n"
            f"📈 Level: {user_data['level']}\n\n"
            f"Keep going! 🎮"
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            bonus_text,
            reply_markup=reply_markup,
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
        
        stats_text = (
            f"📊 My Stats\n\n"
            f"👤 Player: {first_name}\n"
            f"⭐ Points: {user_data['points']}\n"
            f"🔥 Streak: {user_data['streak']} days\n"
            f"🎁 Bonuses: {user_data['bonuses_claimed']}\n"
            f"📈 Level: {user_data['level']}\n"
            f"🏆 Rank: #{rank}"
        )
        
        keyboard = [
            [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stats_text,
            reply_markup=reply_markup,
        )
    
    elif data == "leaderboard":
        if not users_data:
            leaderboard_text = "🏆 Leaderboard\n\nNo players yet! Be the first! 🎮"
        else:
            sorted_users = sorted(
                users_data.items(),
                key=lambda x: x[1]["points"],
                reverse=True
            )
            
            leaderboard_text = "🏆 Leaderboard\n\n"
            for i, (uid, data_dict) in enumerate(sorted_users[:10], 1):
                name = data_dict.get("first_name", f"Player_{str(uid)[:6]}")
                points = data_dict["points"]
                streak = data_dict["streak"]
                level = data_dict.get("level", 1)
                
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"{i}."
                
                leaderboard_text += f"{medal} {name} - {points} pts (Lv.{level}, {streak}d)\n"
        
        keyboard = [
            [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            leaderboard_text,
            reply_markup=reply_markup,
        )
    
    elif data == "tips":
        tip = random.choice(GAMING_TIPS)
        tips_text = f"💡 Gaming Tip\n\n{tip}\n\n💪 Apply this in your next session!"
        
        keyboard = [
            [InlineKeyboardButton("💡 Another Tip", callback_data="tips")],
            [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            tips_text,
            reply_markup=reply_markup,
        )


# ===== ERROR HANDLER =====

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Update {update} caused error: {context.error}")


# ===== MAIN =====

def main():
    print("🚀 Starting Day2Day Bonus Bot...")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        print("✅ Application built!")
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("bonus", bonus_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("leaderboard", leaderboard_command))
        application.add_handler(CommandHandler("tips", tips_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_error_handler(error_handler)
        
        print("✅ Handlers registered!")
        print("🤖 Bot: @day2day_bonusbot")
        print("📋 Commands: /start, /help, /bonus, /stats, /leaderboard, /tips, /about")
        print("⚠️  Press Ctrl+C to stop")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check BOT_TOKEN in .env file")
        print("2. Run: pip install python-telegram-bot==20.7 python-dotenv")
        print("3. Make sure Python 3.8+ is installed")


if __name__ == "__main__":
    main()
