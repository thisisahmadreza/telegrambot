import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

# Your Telegram Bot Token
TOKEN = '8012221612:AAGvIO2S9UtdxtK38xi_HDVG3V75zpY_q-U'
bot = telebot.TeleBot(TOKEN)

# List of channel IDs where the bot should post (add your channel IDs here)
channel_ids = ['-1002261291977']  # Replace with your channel ID

# Variables to store user input
user_data = {}

# Command to start interaction with bot
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello! Please provide the coin name.")
    bot.register_next_step_handler(message, get_coin_name)

# Function to get coin name
def get_coin_name(message):
    user_data['coin_name'] = message.text
    show_trade_type_buttons(message)

# Function to show inline buttons for trade type (short/long)
def show_trade_type_buttons(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Short", callback_data="short"),
        InlineKeyboardButton("Long", callback_data="long")
    )
    bot.send_message(message.chat.id, "Please select trade type:", reply_markup=markup)

# Function to show inline buttons for strategy (scalp/swing)
def show_strategy_buttons(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Scalp", callback_data="scalp"),
        InlineKeyboardButton("Swing", callback_data="swing")
    )
    bot.send_message(message.chat.id, "Please select strategy:", reply_markup=markup)

# Callback handler for buttons
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data in ['short', 'long']:
        user_data['trade_type'] = call.data
        show_strategy_buttons(call.message)
    elif call.data in ['scalp', 'swing']:
        user_data['strategy'] = call.data
        bot.send_message(call.message.chat.id, "Please enter the entry point (EP).")
        bot.register_next_step_handler(call.message, get_entry_point)

# Function to format numbers with up to 10 decimal places, trimming trailing zeros
def format_number(number):
    return f"{number:.10g}"

# Function to get entry point and calculate TP and SL
def get_entry_point(message):
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

        # Confirmation before posting
        confirm_message = (
            f"🪙 {user_data['coin_name']}\n"
            f"{user_data['trade_type'].capitalize()}\n"
            f"{user_data['strategy'].capitalize()}\n"
            f"Lv: 20✖️\n"
            f"💸Entry : {format_number(user_data['entry_point'])}\n"
            "⚠️3% of Future Wallet\n"
            f"🏹TP:\n"
            + "\n".join([f"TP{i+1}: {format_number(tp)}" for i, tp in enumerate(tps)]) + "\n"
            f"❌SL: {format_number(sl)}\n"
            "@alpha_signalsss 🐺"
        )

        user_data['confirm_message'] = confirm_message

        bot.send_message(message.chat.id, "Here is the signal, please confirm to post:\n\n" + confirm_message)
        bot.send_message(message.chat.id, "Type 'yes' to confirm or 'no' to cancel.")
        bot.register_next_step_handler(message, confirm_post)

    except ValueError:
        bot.send_message(message.chat.id, "Invalid input. Please enter a valid number for entry point.")
        bot.register_next_step_handler(message, get_entry_point)

# Function to handle confirmation and ask for the image
def confirm_post(message):
    if message.text.lower() == 'yes':
        bot.send_message(message.chat.id, "Please send the image to be posted with the signal.")
        bot.register_next_step_handler(message, get_image)
    else:
        bot.send_message(message.chat.id, "Posting cancelled.")

# Function to handle image reception and post with caption to the channel
@bot.message_handler(content_types=['photo'])
def get_image(message):
    if message.photo:
        # Get the file ID of the largest image version (highest resolution)
        file_id = message.photo[-1].file_id
        user_data['photo'] = file_id

        # Post the photo with caption to the channel
        for channel_id in channel_ids:
            try:
                bot.send_photo(
                    channel_id, 
                    user_data['photo'], 
                    caption=user_data['confirm_message']
                )
            except Exception as e:
                bot.send_message(message.chat.id, f"Error occurred posting to {channel_id}: {str(e)}")
        
        bot.send_message(message.chat.id, "Signal posted successfully with image to the channel!")
    else:
        bot.send_message(message.chat.id, "Please send a valid image.")
        bot.register_next_step_handler(message, get_image)

# Start the bot and indicate it is running successfully
if __name__ == "__main__":
    print("Bot is running successfully!")  # This message will show in the VPS terminal

    # Polling with retries and error handling
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"Bot encountered an error: {str(e)}")
            time.sleep(5)  # Wait for 5 seconds before restarting polling
