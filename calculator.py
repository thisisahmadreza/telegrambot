import telebot
from telebot import types
import time

# Your Telegram Bot Token
TOKEN = '8012221612:AAGvIO2S9UtdxtK38xi_HDVG3V75zpY_q-U'
bot = telebot.TeleBot(TOKEN)

# Variables to store user input
user_data = {}
TIMEOUT_DURATION = 60  # Timeout duration in seconds

# Command to start interaction with bot
@bot.message_handler(commands=['start'])
def start(message):
    user_data.clear()  # Clear previous data to start fresh
    bot.send_message(message.chat.id, "Hello! Please provide the coin name.")
    bot.register_next_step_handler(message, get_coin_name, time.time())

# Function to get coin name
def get_coin_name(message, start_time):
    if time.time() - start_time > TIMEOUT_DURATION:
        bot.send_message(message.chat.id, "Session timed out. Please start again using /start.")
        return
    user_data['coin_name'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('short', 'long')
    bot.send_message(message.chat.id, "Please choose trade type:", reply_markup=markup)
    bot.register_next_step_handler(message, get_trade_type, time.time())

# Function to get trade type using buttons
def get_trade_type(message, start_time):
    if time.time() - start_time > TIMEOUT_DURATION:
        bot.send_message(message.chat.id, "Session timed out. Please start again using /start.")
        return
    trade_type = message.text.lower()
    if trade_type in ['short', 'long']:
        user_data['trade_type'] = trade_type
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('scalp', 'swing')
        bot.send_message(message.chat.id, "Please choose strategy:", reply_markup=markup)
        bot.register_next_step_handler(message, get_strategy, time.time())
    else:
        bot.send_message(message.chat.id, "Invalid input. Please choose 'short' or 'long'.")
        bot.register_next_step_handler(message, get_trade_type, time.time())

# Function to get strategy using buttons
def get_strategy(message, start_time):
    if time.time() - start_time > TIMEOUT_DURATION:
        bot.send_message(message.chat.id, "Session timed out. Please start again using /start.")
        return
    strategy = message.text.lower()
    if strategy in ['scalp', 'swing']:
        user_data['strategy'] = strategy
        bot.send_message(message.chat.id, "Please enter the entry point (EP).")
        bot.register_next_step_handler(message, get_entry_point, time.time())
    else:
        bot.send_message(message.chat.id, "Invalid input. Please choose 'scalp' or 'swing'.")
        bot.register_next_step_handler(message, get_strategy, time.time())

# Function to get entry point and calculate TP and SL
def get_entry_point(message, start_time):
    if time.time() - start_time > TIMEOUT_DURATION:
        bot.send_message(message.chat.id, "Session timed out. Please start again using /start.")
        return
    try:
        ep = float(message.text)
        user_data['entry_point'] = ep

        # Calculation logic based on trade type and strategy
        if user_data['trade_type'] == 'short' and user_data['strategy'] == 'scalp':
            tps = [ep * 0.98, ep * 0.96, ep * 0.94, ep * 0.92, ep * 0.90, ep * 0.88]
            sl = ep * 1.06
        elif user_data['trade_type'] == 'short' and user_data['strategy'] == 'swing':
            tps = [ep * 0.95, ep * 0.90, ep * 0.85, ep * 0.80]
            sl = ep * 1.08
        elif user_data['trade_type'] == 'long' and user_data['strategy'] == 'scalp':
            tps = [ep * 1.02, ep * 1.04, ep * 1.06, ep * 1.08, ep * 1.10, ep * 1.12]
            sl = ep * 0.94
        elif user_data['trade_type'] == 'long' and user_data['strategy'] == 'swing':
            tps = [ep * 1.05, ep * 1.10, ep * 1.15, ep * 1.20]
            sl = ep * 0.92

        user_data['tps'] = tps
        user_data['sl'] = sl

        # Ask for photo from user
        bot.send_message(message.chat.id, "Please send the image you want to use for the signal.")
        bot.register_next_step_handler(message, get_photo, time.time())

    except ValueError:
        bot.send_message(message.chat.id, "Invalid input. Please enter a valid number for entry point.")
        bot.register_next_step_handler(message, get_entry_point, time.time())

# Function to receive photo and confirm before posting
def get_photo(message, start_time):
    if time.time() - start_time > TIMEOUT_DURATION:
        bot.send_message(message.chat.id, "Session timed out. Please start again using /start.")
        return
    if message.content_type == 'photo':
        user_data['photo'] = message.photo[-1].file_id  # Get highest resolution photo
        confirm_signal(message)
    else:
        bot.send_message(message.chat.id, "Please send a valid photo.")
        bot.register_next_step_handler(message, get_photo, time.time())

# Function to confirm the post
def confirm_signal(message):
    # Confirmation message with TP and SL
    confirm_message = (
        f"🪙 {user_data['coin_name']}\n"
        f"{user_data['trade_type'].capitalize()}\n"
        f"{user_data['strategy'].capitalize()}\n"
        f"Lv: 20✖️\n"
        f"💸Entry : ```{user_data['entry_point']:.10g}```\n"  # Display EP with monospace formatting
        "⚠️3% of Future Wallet\n"
        f"🏹TP:\n"
        + "\n".join([f"```{tp:.10g}```".rstrip('0').rstrip('.') for tp in user_data['tps']]) + "\n"  # TPs formatted with monospace
        f"❌SL: ```{user_data['sl']:.10g}```\n"  # Display SL with monospace formatting
        "@alpha_signalsss 🐺"
    )

    user_data['confirm_message'] = confirm_message

    # Ask for confirmation to post
    bot.send_message(message.chat.id, "Here is the signal, please confirm to post:\n\n" + confirm_message)
    bot.send_message(message.chat.id, "Type 'y' to confirm or 'n' to cancel.")
    bot.register_next_step_handler(message, confirm_post, time.time())

# Function to handle confirmation
def confirm_post(message, start_time):
    if time.time() - start_time > TIMEOUT_DURATION:
        bot.send_message(message.chat.id, "Session timed out. Please start again using /start.")
        return
    if message.text.lower() == 'y':
        # Send photo with caption to the channel
        bot.send_photo(chat_id='-1002261291977', photo=user_data['photo'], caption=user_data['confirm_message'])
        bot.send_message(message.chat.id, "Signal posted successfully!")
    else:
        bot.send_message(message.chat.id, "Posting cancelled.")

# Start the bot and indicate it is running successfully
if __name__ == "__main__":
    print("Bot is running successfully!")
    bot.polling(none_stop=True)
