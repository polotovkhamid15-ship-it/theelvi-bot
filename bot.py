import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Telegram Bot Token
TOKEN = os.getenv("BOT_TOKEN")


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\n"
        "Bot muvaffaqiyatli ishga tushdi! 🤖"
    )


# Oddiy xabarlar
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xabaringiz qabul qilindi ✅"
    )


# Xatoliklarni ko‘rsatish
async def error(update: object, context: ContextTypes.DEFAULT_TYPE):
    print("XATOLIK:", context.error)


# Botni ishga tushirish
def main():
    if not TOKEN:
        print("XATOLIK: BOT_TOKEN topilmadi!")
        return

    app = Application.builder().token(TOKEN).build()

    # /start
    app.add_handler(
        CommandHandler("start", start)
    )

    # Oddiy xabarlar
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message
        )
    )

    # Xatolar
    app.add_error_handler(error)

    print("BOT ISHGA TUSHDI 🚀")

    app.run_polling()


if __name__ == "__main__":
    main()
