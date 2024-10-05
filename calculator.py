from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.ext import ConversationHandler

# Define states for the conversation
COIN, ENTRY_POINT, TRADE_TYPE, STRATEGY = range(4)

# Start command handler
def start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        "Welcome to the Alpha Signal Calculator! Please enter the Coin Name:"
    )
    return COIN

# Handle coin input
def coin(update: Update, _: CallbackContext) -> int:
    user_data = _.user_data
    user_data['coin'] = update.message.text
    update.message.reply_text(
        "Please enter the Entry Point (EP):"
    )
    return ENTRY_POINT

# Handle entry point input
def entry_point(update: Update, _: CallbackContext) -> int:
    user_data = _.user_data
    user_data['entry_point'] = float(update.message.text)
    update.message.reply_text(
        "Please choose the Trade Type:\n"
        "1. SHORT\n"
        "2. LONG"
    )
    return TRADE_TYPE

# Handle trade type input
def trade_type(update: Update, _: CallbackContext) -> int:
    user_data = _.user_data
    user_data['trade_type'] = update.message.text
    update.message.reply_text(
        "Please choose the Strategy:\n"
        "1. SCALP\n"
        "2. SWING"
    )
    return STRATEGY

# Handle strategy input and calculate results
def strategy(update: Update, _: CallbackContext) -> int:
    user_data = _.user_data
    user_data['strategy'] = update.message.text
    
    # Perform calculations
    result = calculate_signal(user_data)
    
    update.message.reply_text(result)
    return ConversationHandler.END

def calculate_signal(data):
    coin_name = data['coin']
    entry_point = data['entry_point']
    trade_type = data['trade_type']
    strategy = data['strategy']
    
    result = f"🪙{coin_name}\n{trade_type}\n{strategy}\nLv: 20✖️\n💸Entry: {entry_point:.2f}\n⚠️3% of Future Wallet\n🏹TP:\n"

    # Add calculations based on trade type and strategy
    if trade_type == "SHORT":
        if strategy == "SCALP":
            for i in range(6):
                result += f"{entry_point * (1 - (0.02 * (i + 1))):.2f}\n"
            result += f"❌SL: = {entry_point * 1.06:.2f}\n"
        elif strategy == "SWING":
            for i in range(4):
                result += f"{entry_point * (1 - (0.05 * (i + 1))):.2f}\n"
            result += f"❌SL: = {entry_point * 1.08:.2f}\n"

    elif trade_type == "LONG":
        if strategy == "SCALP":
            for i in range(6):
                result += f"{entry_point * (1 + (0.02 * (i + 1))):.2f}\n"
            result += f"❌SL: = {entry_point * 0.94:.2f}\n"
        elif strategy == "SWING":
            for i in range(4):
                result += f"{entry_point * (1 + (0.05 * (i + 1))):.2f}\n"
            result += f"❌SL: = {entry_point * 0.92:.2f}\n"
    
    result += "\n@alpha_signalsss 🐺"
    return result

# End the conversation
def cancel(update: Update, _: CallbackContext) -> int:
    update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

def main():
    # Replace 'YOUR_TOKEN_HERE' with your actual bot token
    updater = Updater("8012221612:AAHd58-95oNM5Tz05uJbEHNMyFgOPjWpyYM")

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            COIN: [MessageHandler(Filters.text & ~Filters.command, coin)],
            ENTRY_POINT: [MessageHandler(Filters.text & ~Filters.command, entry_point)],
            TRADE_TYPE: [MessageHandler(Filters.text & ~Filters.command, trade_type)],
            STRATEGY: [MessageHandler(Filters.text & ~Filters.command, strategy)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
