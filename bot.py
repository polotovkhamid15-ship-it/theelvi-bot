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
    ConversationHandler,
    ContextTypes,
    filters,
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

PRODUCT, NAME, LOCATION, CONFIRM = range(4)


# =========================
# ASOSIY MENU
# =========================

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["👜 Sumka kerak edi"],
        ["📞 Siz bilan bog‘lanmoqchiman"],
        ["💬 Madina bilan chat qilish"],
        ["🚚 Yetkazib berish bormi?"],
    ],
    resize_keyboard=True
)


# =========================
# RAILWAY HEALTH
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"TheElvi Bot is running!")

    def log_message(self, format, *args):
        pass


def run_health_server():

    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )

    logger.info(
        f"Health server {PORT}-portda ishga tushdi."
    )

    server.serve_forever()


# =========================
# START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "Men *Madina*, TheElvi konsultantiman 👜✨\n\n"
        "Sizga mahsulot tanlash va zakaz qilishda yordam beraman.\n\n"
        "Quyidagilardan birini tanlang 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )


# =========================
# SUMKA KERAK
# =========================

async def start_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = ReplyKeyboardMarkup(
        [
            ["🖤 Qora sumka", "🎀 Kundalik sumka"],
            ["✨ Klassik sumka", "👜 Kichik sumka"],
        ],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Albatta 😊 Sizga yordam beraman! 👜\n\n"
        "Qanday sumka qidiryapsiz?\n\n"
        "Quyidagilardan birini tanlang 👇",
        reply_markup=keyboard
    )

    return PRODUCT


# =========================
# MAHSULOT
# =========================

async def product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["product"] = update.message.text

    await update.message.reply_text(
        f"Zo‘r tanlov! {update.message.text} 👜✨\n\n"
        "Endi ismingizni yozing 👇"
    )

    return NAME


# =========================
# ISM
# =========================

async def name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "Rahmat 😊\n\n"
        "Endi yetkazib berish uchun lokatsiyangizni yuboring 👇",
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton(
                        "📍 Lokatsiyani yuborish",
                        request_location=True
                    )
                ]
            ],
            resize_keyboard=True
        )
    )

    return LOCATION


# =========================
# LOKATSIYA
# =========================

async def location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message.location:

        latitude = update.message.location.latitude
        longitude = update.message.location.longitude

        context.user_data["latitude"] = latitude
        context.user_data["longitude"] = longitude

        context.user_data["location"] = (
            f"https://maps.google.com/?q="
            f"{latitude},{longitude}"
        )

    else:

        context.user_data["location"] = (
            update.message.text
        )

    data = context.user_data

    keyboard = ReplyKeyboardMarkup(
        [
            ["✅ Zakazni tasdiqlash"],
            ["🏠 Asosiy menyu"],
        ],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🛍️ *Zakazingiz:*\n\n"
        f"👤 Ism: {data.get('name')}\n"
        f"👜 Mahsulot: {data.get('product')}\n"
        f"📍 Manzil: {data.get('location')}\n\n"
        "Ma’lumotlar to‘g‘rimi?",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    return CONFIRM


# =========================
# ZAKAZNI TASDIQLASH
# =========================

async def confirm(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message.text != "✅ Zakazni tasdiqlash":
        return CONFIRM

    data = context.user_data
    user = update.message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "username yo‘q"
    )

    order_text = (
        "🆕 *YANGI ZAKAZ!*\n\n"
        f"👤 Ism: {data.get('name')}\n"
        f"👜 Mahsulot: {data.get('product')}\n"
        f"📍 Manzil: {data.get('location')}\n\n"
        f"💬 Telegram: {username}\n"
        f"🆔 ID: {user.id}"
    )

    try:

        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=order_text,
            parse_mode="Markdown"
        )

        if "latitude" in data:

            await context.bot.send_location(
                chat_id=OWNER_CHAT_ID,
                latitude=data["latitude"],
                longitude=data["longitude"]
            )

        logger.info("Zakaz egasiga yuborildi.")

    except Exception as e:

        logger.error(
            f"Zakaz yuborishda xato: {e}"
        )

    await update.message.reply_text(
        "✅ *Zakazingiz qabul qilindi!*\n\n"
        "Rahmat 🙏\n"
        "Tez orada Madina siz bilan bog‘lanadi. 👜✨",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )

    context.user_data.clear()

    return ConversationHandler.END


# =========================
# BIZ BILAN BOG‘LANISH
# =========================

async def contact(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📞 +998 90 708 00 23",
                    url="tel:+998907080023"
                )
            ]
        ]
    )

    await update.message.reply_text(
        "📞 Biz bilan bog‘lanish uchun "
        "quyidagi raqamni bosing 👇",
        reply_markup=keyboard
    )


# =========================
# MADINA BILAN CHAT
# =========================

async def madina(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "💬 *Madina bilan chat*\n\n"
        "Albatta 😊 Men shu yerdaman!\n\n"
        "Qanday sumka qidiryapsiz?\n"
        "Savolingizni bemalol yozing 👜✨",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )


# =========================
# YETKAZIB BERISH
# =========================

async def delivery(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🚚 *Yetkazib berish mavjud!*\n\n"
        "📍 Toshkent bo‘ylab yetkazib beramiz.\n"
        "🇺🇿 O‘zbekiston bo‘ylab ham yuboramiz.\n\n"
        "Yetkazib berish narxi manzilga qarab aniqlanadi.",
        parse_mode="Markdown",
        reply_markup=MAIN_MENU
    )


# =========================
# MAIN
# =========================

def main():

    if not BOT_TOKEN:

        logger.error("BOT_TOKEN topilmadi!")
        return

    thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    thread.start()

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    order_conversation = ConversationHandler(

        entry_points=[
            MessageHandler(
                filters.Regex(
                    r"^👜 Sumka kerak edi$"
                ),
                start_order
            )
        ],

        states={

            PRODUCT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    product
                )
            ],

            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    name
                )
            ],

            LOCATION: [
                MessageHandler(
                    filters.LOCATION | filters.TEXT,
                    location
                )
            ],

            CONFIRM: [
                MessageHandler(
                    filters.TEXT,
                    confirm
                )
            ],
        },

        fallbacks=[]
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        order_conversation
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^📞 Siz bilan bog‘lanmoqchiman$"
            ),
            contact
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^💬 Madina bilan chat qilish$"
            ),
            madina
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^🚚 Yetkazib berish bormi\?$"
            ),
            delivery
        )
    )

    logger.info("TheElvi bot ishga tushdi!")

    app.run_polling()


# =========================
# ISHGA TUSHIRISH
# =========================

if __name__ == "__main__":
    main()
