# Day2Day Bonus Bot 🎁

A Telegram bot that provides daily gaming bonuses, rewards, and tips to help players improve their skills.

## Features

- 🎁 **Daily Bonus** - Claim your daily reward
- 📊 **Track Stats** - Monitor your points, streaks, and progress
- 🏆 **Leaderboard** - Compete with other players
- 💡 **Gaming Tips** - Get daily tips to improve
- 🎯 **Rewards System** - Earn points for consistency

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu with welcome message |
| `/help` | Help and available commands |
| `/bonus` | Claim your daily bonus |
| `/stats` | View your stats |
| `/leaderboard` | View top players |
| `/tips` | Get gaming tips |

## Bot Information

- **Username:** @day2day_bonusbot
- **Purpose:** Daily gaming bonuses and tips
- **Content:** Free - no gambling

## Installation

```bash
git clone https://github.com/yourusername/day2day-bonus-bot.git
cd day2day-bonus-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your bot token
python main.py
