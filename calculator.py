from telebot import types

# Function to confirm the post with Yes/No buttons
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

    # Create Yes/No buttons
    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Yes", callback_data="confirm_yes")
    no_button = types.InlineKeyboardButton("No", callback_data="confirm_no")
    markup.add(yes_button, no_button)

    # Ask for confirmation to post
    bot.send_message(message.chat.id, "Here is the signal, please confirm to post:\n\n" + confirm_message)
    bot.send_message(message.chat.id, "Please confirm:", reply_markup=markup)

# Callback query handler for Yes/No buttons
@bot.callback_query_handler(func=lambda call: call.data in ['confirm_yes', 'confirm_no'])
def handle_confirmation(call):
    if call.data == 'confirm_yes':
        # Send photo with caption to the channel
        bot.send_photo(chat_id='-1002261291977', photo=user_data['photo'], caption=user_data['confirm_message'])
        bot.send_message(call.message.chat.id, "Signal posted successfully!")
    elif call.data == 'confirm_no':
        bot.send_message(call.message.chat.id, "Posting cancelled.")
    # Remove inline buttons after decision
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# Start the bot and indicate it is running successfully
if __name__ == "__main__":
    print("Bot is running successfully!")
    bot.polling(none_stop=True)
