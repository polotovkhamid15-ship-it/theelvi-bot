import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler, CallbackQueryHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "6968841061"))

ASK_NAME, ASK_PHONE, ASK_ADDRESS, ASK_PRODUCT = range(4)

MAIN_KEYBOARD = ReplyKeyboardMarkup([
    [KeyboardButton("🛍️ Buyurtma berish")],
    [KeyboardButton("💰 Narxlar"), KeyboardButton("🚚 Yetkazib berish")],
    [KeyboardButton("📞 Bog'lanish"), KeyboardButton("❓ Savol")],
], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ *TheElvi* ga xush kelibsiz!\n\n"
        "👜 Sumkalar | 👟 Oyoq kiyim | 💎 Aksessuarlar\n"
        "📍 Toshkent | Yetkazib berish mavjud\n\n"
        "Quyidagilardan birini tanlang 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 *Narxlar haqida:*\n\n"
        "Narxlar Instagram sahifamizda har bir post ostida ko'rsatilgan.\n\n"
        "📱 Instagram: @theelvi.uz\n\n"
        "Aniq narx bilish uchun buyurtma bering yoki DM yozing! 😊",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚚 *Yetkazib berish:*\n\n"
        "📍 Toshkent shahri bo'ylab yetkazib beramiz\n"
        "⏰ Vaqt: 1-2 kun ichida\n"
        "💵 Narxi: buyurtma vaqtida aniqlanadi\n\n"
        "Buyurtma berish uchun tugmani bosing 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Bog'lanish:*\n\n"
        "📱 Instagram: @theelvi.uz\n"
        "💬 Telegram: ushbu bot orqali\n"
        "🕐 Ish vaqti: 09:00 - 21:00\n"
        "📍 Toshkent, O'zbekiston",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Maxsulotlar haqida", callback_data="q_product")],
        [InlineKeyboardButton("📦 Qaytarish haqida", callback_data="q_return")],
        [InlineKeyboardButton("💳 To'lov haqida", callback_data="q_payment")],
    ])
    await update.message.reply_text(
        "❓ *Qaysi savol?*",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "q_product":
        await query.edit_message_text(
            "🛍️ *Mahsulotlar haqida:*\n\n"
            "Barcha mahsulotlarni Instagram sahifamizda ko'rishingiz mumkin:\n"
            "📱 @theelvi.uz\n\n"
            "Buyurtma berish uchun /buyurtma yozing!",
            parse_mode="Markdown"
        )
    elif query.data == "q_return":
        await query.edit_message_text(
            "📦 *Qaytarish:*\n\n"
            "Mahsulot kelgandan so'ng 24 soat ichida muammo bo'lsa\n"
            "qaytarish mumkin. Batafsil: @theelvi.uz",
            parse_mode="Markdown"
        )
    elif query.data == "q_payment":
        await query.edit_message_text(
            "💳 *To'lov usullari:*\n\n"
            "✅ Naqd pul (yetkazib berganda)\n"
            "✅ Karta orqali (Click, Payme)\n\n"
            "Qulay usulni tanlashingiz mumkin!",
            parse_mode="Markdown"
        )


async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ *Buyurtma rasmiylashtirish*\n\n"
        "Bekor qilish uchun: /bekor\n\n"
        "1️⃣ Ismingizni kiriting:",
        parse_mode="Markdown"
    )
    return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("2️⃣ Telefon raqamingiz:\n(+998 XX XXX XX XX)")
    return ASK_PHONE


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("3️⃣ Manzilingiz (tuman, ko'cha):")
    return ASK_ADDRESS


async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text(
        "4️⃣ Qaysi mahsulotni xohlaysiz?\n\n"
        "Mahsulot nomi, rangi va miqdorini yozing.\n"
        "Masalan: *Qora sumka, 1 dona*",
        parse_mode="Markdown"
    )
    return ASK_PRODUCT


async def finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product"] = update.message.text
    user = update.message.from_user
    order_text = (
        f"🆕 *YANGI BUYURTMA!*\n\n"
        f"👤 Ism: {context.user_data['name']}\n"
        f"📱 Telefon: {context.user_data['phone']}\n"
        f"📍 Manzil: {context.user_data['address']}\n"
        f"🛍️ Mahsulot: {context.user_data['product']}\n\n"
        f"💬 Telegram: @{user.username or 'username yoq'}\n"
        f"🆔 ID: {user.id}"
    )
    try:
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=order_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Xato: {e}")
    await update.message.reply_text(
        "✅ *Buyurtmangiz qabul qilindi!*\n\n"
        "📞 Tez orada siz bilan bog'lanamiz!\n"
        "Rahmat xarid uchun 🙏",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )
    return ConversationHandler.END


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Buyurtma bekor qilindi.", reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tushunmadim 😊 Pastdagi tugmalardan birini tanlang:", reply_markup=MAIN_KEYBOARD)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    order_conv = ConversationHandler(
        entry_points=[
            CommandHandler("buyurtma", start_order),
            MessageHandler(filters.Regex("^🛍️ Buyurtma berish$"), start_order),
        ],
        states={
            ASK_NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_address)],
            ASK_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_order)],
        },
        fallbacks=[CommandHandler("bekor", cancel_order)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(order_conv)
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.Regex("^💰 Narxlar$"), prices))
    app.add_handler(MessageHandler(filters.Regex("^🚚 Yetkazib berish$"), delivery))
    app.add_handler(MessageHandler(filters.Regex("^📞 Bog'lanish$"), contact))
    app.add_handler(MessageHandler(filters.Regex("^❓ Savol$"), question))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    logger.info("TheElvi bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
