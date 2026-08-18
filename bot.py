import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

# =========================
# SOZLAMALAR
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "6968841061"))
PORT = int(os.getenv("PORT", "8080"))

ASK_NAME, ASK_PHONE, async def ask_phone( ASK_PRODUCT = range(4)


# =========================
# ASOSIY MENYU
# =========================

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🛍️ Buyurtma berish")],
        [KeyboardButton("💰 Narxlar"), KeyboardButton("🚚 Yetkazib berish")],
        [KeyboardButton("📞 Bog'lanish"), KeyboardButton("❓ Savol")],
    ],
    resize_keyboard=True,
)


# =========================
# HEALTH SERVER
# =========================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"TheElvi Bot is running!")

    def log_message(self, format, *args):
        pass


def run_health_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server xatosi: {e}")


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ *TheElvi* ga xush kelibsiz!\n\n"
        "👜 Sumkalar\n"
        "👟 Oyoq kiyimlar\n"
        "💎 Aksessuarlar\n\n"
        "📍 Toshkent\n"
        "🚚 O'zbekiston bo'ylab yetkazib berish mavjud\n\n"
        "Quyidagi menyudan kerakli bo'limni tanlang 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================
# NARXLAR
# =========================

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 *Narxlar haqida*\n\n"
        "Mahsulotlarning narxi Instagram sahifamizdagi postlarda ko'rsatiladi.\n\n"
        "📱 Instagram: @theelvi.uz\n\n"
        "Aniq narxni bilish uchun bizga yozing 😊",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================
# YETKAZIB BERISH
# =========================

async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚚 *Yetkazib berish*\n\n"
        "📍 Toshkent shahri bo'ylab yetkazib beramiz.\n"
        "🇺🇿 O'zbekiston bo'ylab ham yuborish mumkin.\n\n"
        "⏰ Yetkazib berish vaqti: 1–2 kun.\n"
        "💵 Yetkazib berish narxi manzilga qarab aniqlanadi.\n\n"
        "Buyurtma berish uchun quyidagi tugmani bosing 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================
# BOG'LANISH
# =========================

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Biz bilan bog'lanish*\n\n"
        "📱 Instagram: @theelvi.uz\n"
        "💬 Telegram: ushbu bot orqali\n"
        "🕐 Ish vaqti: 09:00–21:00\n"
        "📍 Toshkent, O'zbekiston",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================
# SAVOLLAR
# =========================

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🛍️ Mahsulotlar",
                    callback_data="q_product",
                )
            ],
            [
                InlineKeyboardButton(
                    "📦 Qaytarish",
                    callback_data="q_return",
                )
            ],
            [
                InlineKeyboardButton(
                    "💳 To'lov",
                    callback_data="q_payment",
                )
            ],
        ]
    )

    await update.message.reply_text(
        "❓ *Savolingizni tanlang:*",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query
    await query.answer()

    if query.data == "q_product":

        await query.edit_message_text(
            "🛍️ *Mahsulotlar haqida*\n\n"
            "Barcha mahsulotlarni Instagram sahifamizda ko'rishingiz mumkin.\n\n"
            "📱 @theelvi.uz\n\n"
            "Buyurtma berish uchun /buyurtma yozing.",
            parse_mode="Markdown",
        )

    elif query.data == "q_return":

        await query.edit_message_text(
            "📦 *Mahsulotni qaytarish*\n\n"
            "Mahsulotni qabul qilganingizdan keyin muammo aniqlansa, "
            "biz bilan imkon qadar tezroq bog'laning.\n\n"
            "📱 @theelvi.uz",
            parse_mode="Markdown",
        )

    elif query.data == "q_payment":

        await query.edit_message_text(
            "💳 *To'lov usullari*\n\n"
            "✅ Naqd pul\n"
            "✅ Karta orqali\n"
            "✅ Click / Payme\n\n"
            "To'lov usuli buyurtma vaqtida kelishiladi.",
            parse_mode="Markdown",
        )


# =========================
# BUYURTMA BOSHLASH
# =========================

async def start_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "🛍️ *Buyurtma rasmiylashtirish*\n\n"
        "Buyurtmani bekor qilish uchun /bekor yozing.\n\n"
        "1️⃣ Ismingizni kiriting:",
        parse_mode="Markdown",
    )

    return ASK_NAME


# =========================
# ISM
# =========================

async def ask_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data["name"] = update.message.text.strip()

    await update.message.reply_text(
        "2️⃣ Telefon raqamingizni yuboring:\n\n"
        "Masalan: +998901234567"
    )

    return ASK_PHONE


# =========================
# TELEFON
# =========================

async def ask_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data["phone"] = update.message.text.strip()

    await update.message.reply_text(
        "3️⃣ Manzilingizni yozing:\n\n"
        "Masalan: Chilonzor, Bunyodkor ko'chasi"
    )

    return ASK_ADDRESS


# =========================
# MANZIL
# =========================

async def ask_address(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data["address"] = update.message.text.strip()

    await update.message.reply_text(
        "4️⃣ Qaysi mahsulotni xohlaysiz?\n\n"
        "Mahsulot nomi, rangi va miqdorini yozing.\n\n"
        "Masalan:\n"
        "Qora ayollar sumkasi, 1 dona"
    )

    return ASK_PRODUCT


# =========================
# BUYURTMA YAKUNLASH
# =========================

async def finish_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data["product"] = update.message.text.strip()

    user = update.message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "username yo'q"
    )

    order_text = (
        "🆕 *YANGI BUYURTMA!*\n\n"
        f"👤 Ism: {context.user_data.get('name', '-')}\n"
        f"📱 Telefon: {context.user_data.get('phone', '-')}\n"
        f"📍 Manzil: {context.user_data.get('address', '-')}\n"
        f"🛍️ Mahsulot: {context.user_data.get('product', '-')}\n\n"
        f"💬 Telegram: {username}\n"
        f"🆔 Telegram ID: {user.id}"
    )

    try:

        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=order_text,
            parse_mode="Markdown",
        )

        logger.info("Yangi buyurtma egasiga yuborildi.")

    except Exception as e:

        logger.error(
            f"Buyurtmani egasiga yuborishda xato: {e}"
        )

    await update.message.reply_text(
        "✅ *Buyurtmangiz qabul qilindi!*\n\n"
        "📞 Tez orada siz bilan bog'lanamiz.\n\n"
        "TheElvi'ni tanlaganingiz uchun rahmat! 👜✨",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )

    return ConversationHandler.END


# =========================
# BUYURTMA BEKOR
# =========================

async def cancel_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Buyurtma bekor qilindi.",
        reply_markup=MAIN_KEYBOARD,
    )

    return ConversationHandler.END


# =========================
# TUSHUNARSIZ XABAR
# =========================

async def unknown(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "Tushunmadim 😊\n\n"
        "Pastdagi menyudan kerakli bo'limni tanlang 👇",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================
# MAIN
# =========================

def main():

    if not BOT_TOKEN:
        logger.error(
            "BOT_TOKEN topilmadi! Environment variable sozlang."
        )
        return

    # Health server
    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )

    health_thread.start()

    logger.info(
        f"Health server {PORT}-portda ishga tushdi."
    )

    # Telegram application
    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Buyurtma Conversation
    order_conv = ConversationHandler(

        entry_points=[
            CommandHandler(
                "buyurtma",
                start_order,
            ),

            MessageHandler(
                filters.Regex(
                    r"^🛍️ Buyurtma berish$"
                ),
                start_order,
            ),
        ],

        states={

            ASK_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_name,
                )
            ],

            ASK_PHONE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_phone,
                )
            ],

            ASK_ADDRESS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_address,
                )
            ],

            ASK_PRODUCT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    finish_order,
                )
            ],
        },

        fallbacks=[
            CommandHandler(
                "bekor",
                cancel_order,
            )
        ],
    )

    # Handlerlar
    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(order_conv)

    app.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^💰 Narxlar$"),
            prices,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^🚚 Yetkazib berish$"),
            delivery,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^📞 Bog'lanish$"),
            contact,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(r"^❓ Savol$"),
            question,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            unknown,
        )
    )

    logger.info("TheElvi bot ishga tushmoqda...")

    app.run_polling()


# =========================
# START PROGRAM
# =========================

if __name__ == "__main__":
    main()
