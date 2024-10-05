import telebot
from telebot import types
import time

# Your Telegram Bot Token
TOKEN = '8012221612:AAGvIO2S9UtdxtK38xi_HDVG3V75zpY_q-U'
bot = telebot.TeleBot(TOKEN)

# Variables to store user input
user_data = {}
TIMEOUT_DURATION = 60  # Timeout duration in seconds

# (Other parts of your code remain unchanged...)

# Function to confirm the post
def confirm_signal(message):
    # Confirmation message with TP and SL
    confirm_message = (
        f"🪙 {user_data['coin_name']}\n"
        f"{user_data['trade_type'].capitalize()}\n"
        f"{user_data['strategy'].capitalize()}\n"
        f"Lv: 20✖️\n"
        f"💸Entry : {user_data['entry_point']:.10g}\n"  # Display EP with maximum 10 significant figures
        "⚠️3% of Future Wallet\n"
        f"🏹TP:\n"
        + "\n".join([f"{tp:.10g}".rstrip('0').rstrip('.') for tp in user_data['tps']]) + "\n"  # TPs formatted appropriately
        f"❌SL: {user_data['sl']:.10g}\n"  # Display
