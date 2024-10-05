from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

# Define states for the conversation
COIN, ENTRY_POINT, TRADE_TYPE, STRATEGY = range(4)

# Start command handler
async def start(update: Update, context) -> int:
    await update.message.reply_text(
        "Welcome to the Alpha Signal Calculator! Please enter the Coin Name:"
    )
    return COIN

# Handle coin input
async def coin(update: Update, context) -> int:
    user_data = context.user_data
    user_data['coin'] = update.message.text
    await update.message.reply_text(
        "Please enter the Entry Point (EP):"
    )
    return ENTRY_POINT

# Handle entry point input
async def entry_point(update: Update, context) -> int:
    user_data = context.user_data
    user_data['entry_point'] = float(update.message.text)
    await update.message.reply_text(
        "Please choose the Trade Type:\n"
        "1. SHORT\n"
        "2. LONG"
    )
    return TRADE_TYPE

# Handle trade type input
async def trade_type(update: Update, context) -> int:
    user_data = context.user_data
    user_data['trade_type'] = update.message.text
    await update.message.reply_text(
        "Please choose the Strategy:\n"
        "1. SCALP\n"
        "2. SWING"
    )
    return STRATEGY

# Handle strategy input and calculate results
async def strategy(update: Update, context) -> int:
    user_data = context.user_data
    user_data['strategy'] = update.message.text
    
    # Perform calculations
    result = calculate_signal(user_data)
    
    await update.message.reply_text(result)
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
async def cancel(update: Update, context) -> int:
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

def main():
    # Replace 'YOUR_TOKEN_HERE' with your actual bot token
    application = Application.builder().token("8012221612:AAHd58-95oNM5Tz05uJbEHNMyFgOPjWpyYM").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            COIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, coin)],
            ENTRY_POINT: [MessageHandler(filters.TEXT & ~filters.COMMAND, entry_point)],
            TRADE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, trade_type)],
            STRATEGY: [MessageHandler(filters.TEXT & ~filters.COMMAND, strategy)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
