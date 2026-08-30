import logging
import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Load environment variables
load_dotenv()

# ===== CONFIGURATION =====
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: BOT_TOKEN not set!")
    exit(1)

print("✅ BOT_TOKEN loaded!")

# ===== DATABASE =====
users_data = {}

def get_user(user_id):
    if user_id not in users_data:
        users_data[user_id] = {
            "points": 0,
            "streak": 0,
            "name": "",
            "last_bonus": None,
            "bonuses": 0,
        }
    return users_data[user_id]

# ===== KEYBOARDS =====

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎁 Claim Bonus", callback_data="bonus")],
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("💡 Tips", callback_data="tips")],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_menu():
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu")]]
    return InlineKeyboardMarkup(keyboard)

# ===== COMMANDS =====

async def start(update, context):
    user = update.effective_user
    user_id = user.id
    name = user.first_name or "Player"
    
    data = get_user(user_id)
    data["name"] = name
    
    text = f"🎮 Welcome {name}!\n\nClaim daily bonuses and track your progress!\n\n📊 Points: {data['points']}\n🔥 Streak: {data['streak']} days"
    
    await update.message.reply_text(text, reply_markup=main_menu())
    print(f"✅ /start from {name}")

async def bonus(update, context):
    user_id = update.effective_user.id
    data = get_user(user_id)
    
    today = datetime.now().date()
    
    if data["last_bonus"] == today:
        await update.message.reply_text(
            "⏰ Already claimed today! Come back tomorrow.",
            reply_markup=back_menu()
        )
        return
    
    amount = random.randint(5, 30)
    
    if data["streak"] >= 7:
        amount = int(amount * 1.5)
        msg = "🔥 7-Day Streak! +50% bonus!"
    elif data["streak"] >= 3:
        amount = int(amount * 1.2)
        msg = "⭐ 3-Day Streak! +20% bonus!"
    else:
        msg = "🎁 Daily bonus!"
    
    data["points"] += amount
    data["bonuses"] += 1
    
    if data["last_bonus"] == today - timedelta(days=1):
        data["streak"] += 1
    else:
        data["streak"] = 1
    
    data["last_bonus"] = today
    
    text = f"🎉 {msg}\n\n✨ +{amount} points\n📊 Points: {data['points']}\n🔥 Streak: {data['streak']} days"
    
    await update.message.reply_text(text, reply_markup=back_menu())

async def stats(update, context):
    user_id = update.effective_user.id
    data = get_user(user_id)
    
    sorted_users = sorted(users_data.items(), key=lambda x: x[1]["points"], reverse=True)
    rank = 1
    for i, (uid, _) in enumerate(sorted_users, 1):
        if uid == user_id:
            rank = i
            break
    
    text = f"📊 My Stats\n\n👤 {data['name']}\n⭐ Points: {data['points']}\n🔥 Streak: {data['streak']} days\n🎁 Bonuses: {data['bonuses']}\n🏆 Rank: #{rank}"
    
    await update.message.reply_text(text, reply_markup=back_menu())

async def leaderboard(update, context):
    if not users_data:
        await update.message.reply_text("🏆 No players yet! Be the first!", reply_markup=back_menu())
        return
    
    sorted_users = sorted(users_data.items(), key=lambda x: x[1]["points"], reverse=True)
    
    text = "🏆 Leaderboard\n\n"
    for i, (uid, data) in enumerate(sorted_users[:10], 1):
        name = data.get("name", f"Player_{str(uid)[:4]}")
        points = data["points"]
        streak = data["streak"]
        
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}."
        
        text += f"{medal} {name} - {points} pts ({streak}d)\n"
    
    await update.message.reply_text(text, reply_markup=back_menu())

async def tips(update, context):
    tips_list = [
        "🎯 Practice tracking targets daily.",
        "🧠 Take breaks to reset focus.",
        "⚙️ Lower sensitivity for better aim.",
        "📊 Watch your replays.",
        "🎮 Warm up before matches.",
        "🔥 Focus on one skill at a time.",
        "📝 Track your progress.",
        "💪 Stay positive and keep learning.",
    ]
    
    tip = random.choice(tips_list)
    text = f"💡 Gaming Tip\n\n{tip}"
    
    await update.message.reply_text(text, reply_markup=back_menu())

async def about(update, context):
    text = "ℹ️ Day2Day Bonus Bot\n\nDaily bonuses and gaming tips!\n❌ No gambling.\n✅ Free to use."
    await update.message.reply_text(text, reply_markup=back_menu())

# ===== BUTTON HANDLER =====

async def button(update, context):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    
    if data == "menu":
        text = f"🎮 Welcome back, {user_data['name']}!\n\n📊 Points: {user_data['points']}\n🔥 Streak: {user_data['streak']} days"
        await query.edit_message_text(text, reply_markup=main_menu())
    
    elif data == "bonus":
        today = datetime.now().date()
        
        if user_data["last_bonus"] == today:
            await query.edit_message_text("⏰ Already claimed today!", reply_markup=back_menu())
            return
        
        amount = random.randint(5, 30)
        
        if user_data["streak"] >= 7:
            amount = int(amount * 1.5)
            msg = "🔥 7-Day Streak! +50%!"
        elif user_data["streak"] >= 3:
            amount = int(amount * 1.2)
            msg = "⭐ 3-Day Streak! +20%!"
        else:
            msg = "🎁 Daily bonus!"
        
        user_data["points"] += amount
        user_data["bonuses"] += 1
        
        if user_data["last_bonus"] == today - timedelta(days=1):
            user_data["streak"] += 1
        else:
            user_data["streak"] = 1
        
        user_data["last_bonus"] = today
        
        text = f"🎉 {msg}\n\n✨ +{amount} points\n📊 Points: {user_data['points']}\n🔥 Streak: {user_data['streak']} days"
        await query.edit_message_text(text, reply_markup=back_menu())
    
    elif data == "stats":
        sorted_users = sorted(users_data.items(), key=lambda x: x[1]["points"], reverse=True)
        rank = 1
        for i, (uid, _) in enumerate(sorted_users, 1):
            if uid == user_id:
                rank = i
                break
        
        text = f"📊 My Stats\n\n👤 {user_data['name']}\n⭐ Points: {user_data['points']}\n🔥 Streak: {user_data['streak']} days\n🎁 Bonuses: {user_data['bonuses']}\n🏆 Rank: #{rank}"
        await query.edit_message_text(text, reply_markup=back_menu())
    
    elif data == "leaderboard":
        if not users_data:
            await query.edit_message_text("🏆 No players yet!", reply_markup=back_menu())
            return
        
        sorted_users = sorted(users_data.items(), key=lambda x: x[1]["points"], reverse=True)
        
        text = "🏆 Leaderboard\n\n"
        for i, (uid, d) in enumerate(sorted_users[:10], 1):
            name = d.get("name", f"Player_{str(uid)[:4]}")
            points = d["points"]
            streak = d["streak"]
            
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            text += f"{medal} {name} - {points} pts ({streak}d)\n"
        
        await query.edit_message_text(text, reply_markup=back_menu())
    
    elif data == "tips":
        tips_list = [
            "🎯 Practice tracking targets daily.",
            "🧠 Take breaks to reset focus.",
            "⚙️ Lower sensitivity for better aim.",
            "📊 Watch your replays.",
            "🎮 Warm up before matches.",
            "🔥 Focus on one skill at a time.",
            "📝 Track your progress.",
            "💪 Stay positive and keep learning.",
        ]
        tip = random.choice(tips_list)
        await query.edit_message_text(f"💡 Gaming Tip\n\n{tip}", reply_markup=back_menu())

# ===== MAIN =====

def main():
    print("🚀 Starting Day2Day Bonus Bot...")
    print("🤖 @day2day_bonusbot")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bonus", bonus))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("tips", tips))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CallbackQueryHandler(button))
    
    print("✅ Bot is running!")
    print("⚠️ Press Ctrl+C to stop")
    
    app.run_polling()

if __name__ == "__main__":
    main()
