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

# Command to start interaction with the bot
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    # Clear previous user data and active session
    if chat_id in active_sessions:
        bot.clear_step_handler_by_chat_id(chat_id)
        active_sessions.pop(chat_id, None)

    # Initialize a new session
    user_data[chat_id] = {}
    bot.send_message(chat_id, "Please provide the coin name.")
    active_sessions[chat_id] = time.time()  # Track session start time
    bot.register_next_step_handler(message, get_coin_name)

# Function to get coin name
def get_coin_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['coin_name'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('short', 'long')
    bot.send_message(chat_id, "Please choose trade type:", reply_markup=markup)
    bot.register_next_step_handler(message, get_trade_type)

# Function to get trade type using buttons
def get_trade_type(message):
    chat_id = message.chat.id
    trade_type = message.text.lower()
    if trade_type in ['short', 'long']:
        user_data[chat_id]['trade_type'] = trade_type
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('scalp', 'swing')
        bot.send_message(chat_id, "Please choose strategy:", reply_markup=markup)
        bot.register_next_step_handler(message, get_strategy)
    else:
        bot.send_message(chat_id, "Invalid input. Please choose 'short' or 'long'.")
        bot.register_next_step_handler(message, get_trade_type)

# Function to get strategy using buttons
def get_strategy(message):
    chat_id = message.chat.id
    strategy = message.text.lower()
    if strategy in ['scalp', 'swing']:
        user_data[chat_id]['strategy'] = strategy
        bot.send_message(chat_id, "Please enter the entry point (EP).")
        bot.register_next_step_handler(message, get_entry_point)
    else:
        bot.send_message(chat_id, "Invalid input. Please choose 'scalp' or 'swing'.")
        bot.register_next_step_handler(message, get_strategy)

# Function to get entry point and calculate TP and SL
def get_entry_point(message):
    chat_id = message.chat.id
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
        "⚠️3% of Future Wallet\n"
        f"🏹TP:\n"
        + "\n".join([f"{tp:.10g}".rstrip('0').rstrip('.') for tp in user_data[chat_id]['tps']]) + "\n"  # TPs formatted appropriately
        f"❌SL: {user_data[chat_id]['sl']:.10g}\n"  # Display SL with maximum 10 significant figures
        " \n"
        "@alpha_signalsss 🐺"
    )

    user_data[chat_id]['confirm_message'] = confirm_message

    # Create inline keyboard for confirmation
    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Yes", callback_data="confirm_yes")
    no_button = types.InlineKeyboardButton("No", callback_data="confirm_no")
    markup.add(yes_button, no_button)

    bot.send_message(chat_id, "Here is the signal, please confirm to post:\n\n" + confirm_message, reply_markup=markup)

# Handling confirmation button presses
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def handle_confirmation(call):
    chat_id = call.message.chat.id
    if call.data == "confirm_yes":
        post_to_channel(chat_id)  # Post to channel if confirmed
    else:
        bot.send_message(chat_id, "Signal posting canceled.")
        user_data.pop(chat_id, None)  # Clear user data after cancellation

# Function to post to channel
def post_to_channel(chat_id):
    bot.send_photo(chat_id='-1002261291977', photo=user_data[chat_id]['photo'], caption=user_data[chat_id]['confirm_message'])
    bot.send_message(chat_id, "Signal posted to channel successfully!")
    user_data.pop(chat_id, None)  # Clear user data after posting

# Start the bot and indicate it is running successfully
if __name__ == "__main__":
    print("Bot is running successfully!")
    bot.polling(none_stop=True)
