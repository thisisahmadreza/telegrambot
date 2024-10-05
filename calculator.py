import telebot

# Your Telegram Bot Token
TOKEN = '8012221612:AAGvIO2S9UtdxtK38xi_HDVG3V75zpY_q-U'
bot = telebot.TeleBot(TOKEN)

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
    bot.send_message(message.chat.id, "Please enter trade type (short or long).")
    bot.register_next_step_handler(message, get_trade_type)

# Function to get trade type
def get_trade_type(message):
    trade_type = message.text.lower()
    if trade_type in ['short', 'long']:
        user_data['trade_type'] = trade_type
        bot.send_message(message.chat.id, "Please enter strategy (scalp or swing).")
        bot.register_next_step_handler(message, get_strategy)
    else:
        bot.send_message(message.chat.id, "Invalid input. Please enter 'short' or 'long'.")
        bot.register_next_step_handler(message, get_trade_type)

# Function to get strategy
def get_strategy(message):
    strategy = message.text.lower()
    if strategy in ['scalp', 'swing']:
        user_data['strategy'] = strategy
        bot.send_message(message.chat.id, "Please enter the entry point (EP).")
        bot.register_next_step_handler(message, get_entry_point)
    else:
        bot.send_message(message.chat.id, "Invalid input. Please enter 'scalp' or 'swing'.")
        bot.register_next_step_handler(message, get_strategy)

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
            f"💸Entry : {user_data['entry_point']}\n"
            "⚠️3% of Future Wallet\n"
            f"🏹TP:\n"
            + "\n".join([f"TP{i+1}: {tp:.2f}" for i, tp in enumerate(tps)]) + "\n"
            f"❌SL: {sl:.2f}\n"
            "@alpha_signalsss 🐺"
        )

        bot.send_message(message.chat.id, "Here is the signal, please confirm to post:\n\n" + confirm_message)
        bot.send_message(message.chat.id, "Type 'yes' to confirm or 'no' to cancel.")
        bot.register_next_step_handler(message, confirm_post)

    except ValueError:
        bot.send_message(message.chat.id, "Invalid input. Please enter a valid number for entry point.")
        bot.register_next_step_handler(message, get_entry_point)

# Function to handle confirmation
def confirm_post(message):
    if message.text.lower() == 'yes':
        bot.send_message('@your_channel_name', user_data['confirm_message'])
        bot.send_message(message.chat.id, "Signal posted successfully!")
    else:
        bot.send_message(message.chat.id, "Posting cancelled.")

# Start the bot and indicate it is running successfully
if __name__ == "__main__":
    print("Bot is running successfully!")  # This message will show in the VPS terminal
    bot.polling()
