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
posted_messages = {}  # To track posted messages and message_ids
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
        user_data.clear()  # Clear user data on timeout
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
        user_data.clear()  # Clear user data on timeout
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
        user_data.clear()  # Clear user data on timeout
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
        user_data.clear()  # Clear user data on timeout
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
        user_data.clear()  # Clear user data on timeout
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
        f"💸Entry : {user_data['entry_point']:.10g}\n"  # Display EP with maximum 10 significant figures
        "⚠️3% of Future Wallet\n"
        f"🏹TP:\n"
        + "\n".join([f"{tp:.10g}".rstrip('0').rstrip('.') for tp in user_data['tps']]) + "\n"  # TPs formatted appropriately
        f"❌SL: {user_data['sl']:.10g}\n"  # Display SL with maximum 10 significant figures
        "@alpha_signalsss 🐺"
    )

    user_data['confirm_message'] = confirm_message

    # Create inline keyboard for confirmation
    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Yes", callback_data="confirm_yes")
    no_button = types.InlineKeyboardButton("No", callback_data="confirm_no")
    markup.add(yes_button, no_button)

    # Ask for confirmation to post with buttons
    bot.send_message(message.chat.id, "Here is the signal, please confirm to post:\n\n" + confirm_message, reply_markup=markup)

# Callback query handler for Yes/No buttons
@bot.callback_query_handler(func=lambda call: call.data in ['confirm_yes', 'confirm_no'])
def handle_confirmation(call):
    if call.data == 'confirm_yes':
        # Send photo with caption to the channel
        message = bot.send_photo(chat_id='-1002261291977', photo=user_data['photo'], caption=user_data['confirm_message'])
        
        # Store the message ID for editing later
        posted_messages[message.message_id] = {
            'tps': user_data['tps'],
            'sl': user_data['sl'],
            'coin_name': user_data['coin_name'],
            'trade_type': user_data['trade_type'],
            'strategy': user_data['strategy'],
            'entry_point': user_data['entry_point'],
            'photo': user_data['photo']  # Store photo for editing
        }

        bot.send_message(call.message.chat.id, "Signal posted successfully!")
    else:
        bot.send_message(call.message.chat.id, "Posting cancelled.")

# Listen for replies from admins in the channel to update TP/SL
@bot.message_handler(func=lambda message: message.reply_to_message and message.chat.id == -1002261291977)
def handle_admin_update(message):
    original_message_id = message.reply_to_message.message_id
    content = message.text.lower()

    if original_message_id in posted_messages:
        original_post_data = posted_messages[original_message_id]
        updated = False

        # Check for TP and SL updates
        if "tp 1" in content:
            original_post_data['tps'][0] = "✅ " + str(original_post_data['tps'][0])
            updated = True
        elif "tp 2" in content:
            original_post_data['tps'][1] = "✅ " + str(original_post_data['tps'][1])
            updated = True
        elif "tp 3" in content:
            original_post_data['tps'][2] = "✅ " + str(original_post_data['tps'][2])
            updated = True
        elif "tp 4" in content:
            original_post_data['tps'][3] = "✅ " + str(original_post_data['tps'][3])
            updated = True
        elif "stop 🛑🙏🏻" in content:
            original_post_data['sl'] = "✅ " + str(original_post_data['sl'])
            updated = True

        # Rebuild and edit the original message if an update occurred
        if updated:
            updated_message = (
                f"🪙 {original_post_data['coin_name']}\n"
                f"{original_post_data['trade_type'].capitalize()}\n"
                f"{original_post_data['strategy'].capitalize()}\n"
                f"Lv: 20✖️\n"
                f"💸Entry : {original_post_data['entry_point']:.10g}\n"
                "⚠️3% of Future Wallet\n"
                f"🏹TP:\n"
                + "\n".join([f"{tp}" for tp in original_post_data['tps']]) + "\n"
                f"❌SL: {original_post_data['sl']}\n"
                "@alpha_signalsss 🐺"
            )
            
            # Edit the original message
            bot.edit_message_caption(chat_id=message.chat.id, message_id=original_message_id, caption=updated_message)
    else:
        bot.send_message(message.chat.id, "This reply doesn't match any bot-generated post.")

# Start polling for updates
if __name__ == '__main__':
    bot.polling(none_stop=True)
