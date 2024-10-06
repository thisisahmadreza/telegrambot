import telebot
from telebot import types
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Your Telegram Bot Token
TOKEN = '8012221612:AAGvIO2S9UtdxtK38xi_HDVG3V75zpY_q-U'
bot = telebot.TeleBot(TOKEN)

# Variables to store user input
user_data = {}
TIMEOUT_DURATION = 60  # Timeout duration in seconds
active_sessions = {}  # Track active sessions by user ID
PASSWORD = "your_password_here"  # Set your desired password

# Command to start interaction with bot
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    # Clear previous user data and active session
    if chat_id in active_sessions:
        bot.clear_step_handler_by_chat_id(chat_id)
        active_sessions.pop(chat_id, None)

    user_data[chat_id] = {}  # Initialize a new session
    bot.send_message(chat_id, "Please enter the password to access the bot:")
    bot.register_next_step_handler(message, check_password)

# Function to check password
def check_password(message):
    chat_id = message.chat.id
    if message.text == PASSWORD:
        bot.send_message(chat_id, "Access granted! Please provide the coin name.")
        active_sessions[chat_id] = time.time()  # Track session start time
        user_data[chat_id]['authenticated'] = True  # Set user as authenticated
        bot.register_next_step_handler(message, get_coin_name, active_sessions[chat_id])
    else:
        bot.send_message(chat_id, "Incorrect password. Please restart with /start.")
        user_data.pop(chat_id, None)  # Clear user data if password is incorrect
        active_sessions.pop(chat_id, None)  # Clear active session

# Function to get coin name
def get_coin_name(message, start_time):
    chat_id = message.chat.id
    if time.time() - start_time > TIMEOUT_DURATION:
        bot.send_message(chat_id, "Session timed out. Please start again using /start.")
        user_data.pop(chat_id, None)  # Clear user data on timeout
        active_sessions.pop(chat_id, None)  # Clear active session
        return

    user_data[chat_id]['coin_name'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('short', 'long')
    bot.send_message(chat_id, "Please choose trade type:", reply_markup=markup)
    bot.register_next_step_handler(message, get_trade_type, start_time)

# The rest of your existing functions remain unchanged...

# Start the bot and indicate it is running successfully
if __name__ == "__main__":
    print("Bot is running successfully!")
    bot.polling(none_stop=True)
