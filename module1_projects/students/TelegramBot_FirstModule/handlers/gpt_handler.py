from keyboards.gpt_keyboard import gpt_keyboard

async def gpt(update, context):
    await send_image(update, context, "gpt")
    message = load_message("gpt")
    await update.message.reply_text(
        message,
        reply_markup=gpt_keyboard()
    )

    return GPT_DIALOG