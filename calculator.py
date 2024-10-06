import os
import telebot
from telebot import types
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Fetch your Telegram Bot Token from an environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Ensure the token is available
if not TOKEN:
    raise ValueError("Error: No TELEGRAM_BOT_TOKEN found. Set it as an environment variable.")

bot = telebot.TeleBot(TOKEN)

# Variables to store user input
user_data = {}
TIMEOUT_DURATION = 60  # Timeout duration in seconds
active_sessions = {}  # Track active sessions by user ID
PASSWORD = "alpha1"  # Set your desired password

# Command to start interaction with the bot
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    # Clear previous user data and active session
    if chat_id in active_sessions:
        bot.clear_step_handler_by_chat_id(chat_id)
        active_sessions.pop(chat_id, None)

    # Check if user is already authenticated
    if user_data.get(chat_id, {}).get('authenticated', False):
        bot.send_message(chat_id, "Welcome back! Please provide the coin name.")
        active_sessions[chat_id] = time.time()  # Track session start time
        bot.register_next_step_handler(message, get_coin_name)
    else:
        user_data[chat_id] = {}  # Initialize a new session
        bot.send_message(chat_id, "Please enter the password to access the bot:")
        bot.register_next_step_handler(message, check_password)

# Function to check password
def check_password(message):
    chat_id = message.chat.id
    if message.text == PASSWORD:
        user_data[chat_id]['authenticated'] = True  # Set user as authenticated
        bot.send_message(chat_id, "Access granted! Please provide the coin name.")
        active_sessions[chat_id] = time.time()  # Track session start time
        bot.register_next_step_handler(message, get_coin_name)
    else:
        bot.send_message(chat_id, "Incorrect password. Please restart with /start.")
        user_data.pop(chat_id, None)  # Clear user data if password is incorrect
        active_sessions.pop(chat_id, None)  # Clear active session

# Function to get coin name
def get_coin_name(message):
    chat_id = message.chat.id
    if not user_data[chat_id].get('authenticated', False):
        bot.send_message(chat_id, "You need to be authenticated to use this bot. Please restart with /start.")
        return

    user_data[chat_id]['coin_name'] = message.text

    # Show inline buttons for trade type (short/long)
    markup = types.InlineKeyboardMarkup()
    short_button = types.InlineKeyboardButton("Short", callback_data="short")
    long_button = types.InlineKeyboardButton("Long", callback_data="long")
    markup.add(short_button)  # Short button on one line
    markup.add(long_button)   # Long button on the next line
    bot.send_message(chat_id, "Please choose trade type:", reply_markup=markup)

# Handling trade type selection
@bot.callback_query_handler(func=lambda call: call.data in ["short", "long"])
def handle_trade_type_selection(call):
    chat_id = call.message.chat.id
    trade_type = call.data
    user_data[chat_id]['trade_type'] = trade_type

    # Show inline buttons for strategy (scalp/swing)
    markup = types.InlineKeyboardMarkup()
    scalp_button = types.InlineKeyboardButton("Scalp", callback_data="scalp")
    swing_button = types.InlineKeyboardButton("Swing", callback_data="swing")
    markup.add(scalp_button)  # Scalp button on one line
    markup.add(swing_button)  # Swing button on the next line
    bot.send_message(chat_id, "Please choose strategy:", reply_markup=markup)

# Handling strategy selection
@bot.callback_query_handler(func=lambda call: call.data in ["scalp", "swing"])
def handle_strategy_selection(call):
    chat_id = call.message.chat.id
    strategy = call.data
    user_data[chat_id]['strategy'] = strategy
    bot.send_message(chat_id, "Please enter the entry point (EP).")
    bot.register_next_step_handler(call.message, get_entry_point)

# Function to get entry point and calculate TP and SL
def get_entry_point(message):
    chat_id = message.chat.id
    if not user_data[chat_id].get('authenticated', False):
        bot.send_message(chat_id, "You need to be authenticated to use this bot. Please restart with /start.")
        return
    
    try:
        ep = float(message.text)
        user_data[chat_id]['entry_point'] = ep

        # Calculation logic based on trade type and strategy
        trade_type = user_data[chat_id]['trade_type']
        strategy = user_data[chat_id]['strategy']

        if trade_type == 'short' and strategy == 'scalp':
            tps = [ep * 0.98, ep * 0.96, ep * 0.94, ep * 0.92, ep * 0.90, ep * 0.88]
            sl = ep * 1.06
        elif trade_type == 'short' and strategy == 'swing':
            tps = [ep * 0.95, ep * 0.90, ep * 0.85, ep * 0.80]
            sl = ep * 1.08
        elif trade_type == 'long' and strategy == 'scalp':
            tps = [ep * 1.02, ep * 1.04, ep * 1.06, ep * 1.08, ep * 1.10, ep * 1.12]
            sl = ep * 0.94
        elif trade_type == 'long' and strategy == 'swing':
            tps = [ep * 1.05, ep * 1.10, ep * 1.15, ep * 1.20]
            sl = ep * 0.92

        user_data[chat_id]['tps'] = tps
        user_data[chat_id]['sl'] = sl

        # Ask for photo from user
        bot.send_message(chat_id, "Please send the image you want to use for the signal.")
        bot.register_next_step_handler(message, get_photo)

    except ValueError:
        bot.send_message(chat_id, "Invalid input. Please enter a valid number for entry point.")
        bot.register_next_step_handler(message, get_entry_point)

# Function to receive photo and confirm before posting
def get_photo(message):
    chat_id = message.chat.id
    if not user_data[chat_id].get('authenticated', False):
        bot.send_message(chat_id, "You need to be authenticated to use this bot. Please restart with /start.")
        return

    if message.content_type == 'photo':
        user_data[chat_id]['photo'] = message.photo[-1].file_id  # Get highest resolution photo
        confirm_signal(message)
    else:
        bot.send_message(chat_id, "Please send a valid photo.")
        bot.register_next_step_handler(message, get_photo)

# Function to confirm the post
def confirm_signal(message):
    chat_id = message.chat.id
    # Confirmation message with TP and SL
    confirm_message = (
        f"🪙 {user_data[chat_id]['coin_name']}\n"
        f"{user_data[chat_id]['trade_type'].capitalize()}\n"
        f"{user_data[chat_id]['strategy'].capitalize()}\n"
        f"Lv: 20✖️\n"
        f"💸Entry : {user_data[chat_id]['entry_point']:.10g}\n"  # Display EP with maximum 10 significant figures
        "🎯 Targets :\n" +
        "\n".join([f"{i+1} : {tp:.10g}" for i, tp in enumerate(user_data[chat_id]['tps'])]) + "\n"
        f"🛡Stop : {user_data[chat_id]['sl']:.10g}"
    )

    user_data[chat_id]['confirm_message'] = confirm_message

    # Confirm and proceed
    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Yes", callback_data="confirm_yes")
    no_button = types.InlineKeyboardButton("No", callback_data="confirm_no")
    markup.add(yes_button, no_button)  # Inline buttons horizontally

    bot.send_photo(chat_id, user_data[chat_id]['photo'], caption=confirm_message)
    bot.send_message(chat_id, "Confirm the signal:", reply_markup=markup)

# Handle confirmation callbacks
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_yes", "confirm_no"])
def handle_confirmation(call):
    chat_id = call.message.chat.id

    if call.data == "confirm_yes":
        bot.send_message(chat_id, "Signal confirmed. Posting...")
        # Here you would add code to post the signal
        bot.send_photo('@alpha_signalsss', photo=user_data[chat_id]['photo'], caption=user_data[chat_id]['confirm_message'])
        bot.send_message(chat_id, "Signal posted successfully!")
        user_data.pop(chat_id, None)  # Clear user data after posting
    else:
        bot.send_message(chat_id, "Signal cancelled. Restart with /start.")
        user_data.pop(chat_id, None)  # Clear user data after cancelling

# Polling
if __name__ == "__main__":
    bot.polling()
