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
            + ", ".join([format_number(tp) for tp in tps]) + "\n"  # Removed TP1, TP2 labels and joined them with commas
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
