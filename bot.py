import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
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

ASK_PRODUCT = 1
ASK_NAME = 2
ASK_PHONE = 3
ASK_LOCATION = 4


# =========================
# ASOSIY MENYU
# =========================

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["👜 Sumka kerak edi"],
        ["📞 Siz bilan bog‘lanmoqchiman"],
        ["💬 Madina bilan chat qilish"],
        ["🚚 Yetkazib berish bormi?"],
    ],
    resize_keyboard=True,
)


# =========================
# HEALTH SERVER
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )
        self.end_headers()

        self.wfile.write(
            b"TheElvi Bot is running!"
        )

    def log_message(self, format, *args):
        pass


def run_health_server():

    try:
        server = HTTPServer(
            ("0.0.0.0", PORT),
            HealthHandler
        )

        logger.info(
            f"Health server {PORT}-portda ishga tushdi."
        )

        server.serve_forever()

    except Exception as e:

        logger.error(
            f"Health server xatosi: {e}"
        )


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
        "Men *Madina*, TheElvi konsultantiman 👜✨\n"
        "Sizga mahsulot tanlash va zakaz qilishda yordam beraman.\n\n"
        "Quyidagilardan birini tanlang 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


# =========================
# SUMKA BOSHLASH
# =========================

async def start_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()

    bag_keyboard = ReplyKeyboardMarkup(
        [
            [
                "🖤 Qora sumka",
                "🎀 Kundalik sumka"
            ],
            [
                "✨ Klassik sumka",
                "👜 Kichik sumka"
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Albatta 😊 Sizga yordam beraman! 👜\n\n"
        "Qanday sumka qidiryapsiz?\n\n"
        "Quyidagilardan birini tanlang 👇",
        reply_markup=bag_keyboard
    )

    return ASK_PRODUCT


# =========================
# MAHSULOT
# =========================

async def ask_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    product = update.message.text.strip()

    context.user_data["product"] = product

    await update.message.reply_text(
        f"Zo‘r tanlov! {product} 👜✨\n\n"
        "Zakazingizni rasmiylashtirish uchun "
        "ismingizni yozib qoldiring 👇"
    )

    return ASK_NAME


# =========================
# ISM
# =========================

async def ask_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["name"] = (
        update.message.text.strip()
    )

    phone_keyboard = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    "📱 Telefon raqamimni yuborish",
                    request_contact=True
                )
            ],
            [
                "✍️ Raqamni yozish"
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Rahmat! 😊\n\n"
        "📱 Endi telefon raqamingizni yuboring.",
        reply_markup=phone_keyboard
    )

    return ASK_PHONE


# =========================
# TELEFON
# =========================

async def ask_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message.contact:

        context.user_data["phone"] = (
            update.message.contact.phone_number
        )

    elif update.message.text == "✍️ Raqamni yozish":

        await update.message.reply_text(
            "📱 Telefon raqamingizni yozing:\n\n"
            "Masalan:\n"
            "+998901234567"
        )

        return ASK_PHONE

    else:

        context.user_data["phone"] = (
            update.message.text.strip()
        )

    location_keyboard = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    "📍 Lokatsiyani yuborish",
                    request_location=True
                )
            ],
            [
                "✍️ Manzilni yozish"
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Ajoyib! 👍\n\n"
        "📍 Endi yetkazib berish manzilingizni yuboring.\n\n"
        "Eng qulayi — *Lokatsiyani yuborish* tugmasini bosing.",
        parse_mode="Markdown",
        reply_markup=location_keyboard
    )

    return ASK_LOCATION


# =========================
# LOKATSIYA
# =========================

async def ask_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message.location:

        latitude = update.message.location.latitude
        longitude = update.message.location.longitude

        context.user_data["latitude"] = latitude
        context.user_data["longitude"] = longitude

        context.user_data["address"] = (
            f"https://www.google.com/maps?q="
            f"{latitude},{longitude}"
        )

    elif update.message.text == "✍️ Manzilni yozish":

        await update.message.reply_text(
            "✍️ Manzilingizni yozing:\n\n"
            "Masalan:\n"
            "Chilonzor, Bunyodkor ko‘chasi, 15-uy"
        )

        return ASK_LOCATION

    else:

        context.user_data["address"] = (
            update.message.text.strip()
        )

    # Zakaz ma'lumotlari

    product = context.user_data.get(
        "product",
        "-"
    )

    name = context.user_data.get(
        "name",
        "-"
    )

    phone = context.user_data.get(
        "phone",
        "-"
    )

    address = context.user_data.get(
        "address",
        "-"
    )

    confirm_keyboard = ReplyKeyboardMarkup(
        [
            ["✅ Zakazni tasdiqlash"],
            ["🏠 Asosiy menyu"],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "🎀 *Zakazingiz tayyor!*\n\n"
        f"👤 Ism: {name}\n"
        f"📱 Telefon: {phone}\n"
        f"👜 Mahsulot: {product}\n"
        f"📍 Manzil: {address}\n\n"
        "Ma’lumotlar to‘g‘rimi?\n"
        "Zakazni tasdiqlash uchun quyidagi tugmani bosing 👇",
        parse_mode="Markdown",
        reply_markup=confirm_keyboard
    )

    return ConversationHandler.END


# =========================
# ZAKAZ TASDIQLASH
# =========================

async def confirm_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message.text != "✅ Zakazni tasdiqlash":
        return

    user = update.message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "username yo‘q"
    )

    product = context.user_data.get(
        "product",
        "-"
    )

    name = context.user_data.get(
        "name",
        "-"
    )

    phone = context.user_data.get(
        "phone",
        "-"
    )

    address = context.user_data.get(
        "address",
        "-"
    )

    order_text = (
        "🆕 *YANGI ZAKAZ!*\n\n"
        f"👤 Ism: {name}\n"
        f"📱 Telefon: {phone}\n"
        f"👜 Mahsulot: {product}\n"
        f"📍 Manzil: {address}\n\n"
        f"💬 Telegram: {username}\n"
        f"🆔 ID: {user.id}"
    )

    try:

        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=order_text,
            parse_mode="Markdown"
        )

        if (
            "latitude" in context.user_data
            and "longitude" in context.user_data
        ):

            await context.bot.send_location(
                chat_id=OWNER_CHAT_ID,
                latitude=context.user_data["latitude"],
                longitude=context.user_data["longitude"]
            )

        logger.info(
            "Yangi zakaz egasiga yuborildi."
        )

    except Exception as e:

        logger.error(
            f"Zakaz yuborishda xato: {e}"
        )

    await update.message.reply_text(
        "✅ *Zakazingiz qabul qilindi!*\n\n"
        "Rahmat! 👜✨\n"
        "Tez orada Madina siz bilan bog‘lanadi.",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )

    context.user_data.clear()


# =========================
# BOG‘LANISH
# =========================

async def contact_us(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "Albatta 😊\n\n"
        "Siz bilan bog‘lanishimiz uchun "
        "telefon raqamingizni qoldiring 📱",
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton(
                        "📱 Telefon raqamimni yuborish",
                        request_contact=True
                    )
                ],
                [
                    "✍️ Raqamni yozish"
                ],
            ],
            resize_keyboard=True
        )
    )


# =========================
# MADINA CHAT
# =========================

async def madina_chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "💬 *Madina bilan chat*\n\n"
        "Albatta 😊 Men shu yerdaman.\n\n"
        "Sizga qanday sumka kerak?\n"
        "Mahsulot, rang yoki narx haqida "
        "bemalol so‘rashingiz mumkin. 👜✨",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


# =========================
# YETKAZIB BERISH
# =========================

async def delivery(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🚚 *Ha, yetkazib berish mavjud!*\n\n"
        "📍 Toshkent bo‘ylab yetkazib beramiz.\n"
        "🇺🇿 O‘zbekiston bo‘ylab ham yuborish mumkin.\n\n"
        "Yetkazib berish narxi manzilga qarab "
        "aniqlanadi.",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD
    )


# =========================
# MAIN
# =========================

def main():

    if not BOT_TOKEN:

        logger.error(
            "BOT_TOKEN topilmadi!"
        )

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

    # Zakaz jarayoni

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

            ASK_PRODUCT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_product
                )
            ],

            ASK_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    ask_name
                )
            ],

            ASK_PHONE: [
                MessageHandler(
                    filters.CONTACT | filters.TEXT,
                    ask_phone
                )
            ],

            ASK_LOCATION: [
                MessageHandler(
                    filters.LOCATION | filters.TEXT,
                    ask_location
                )
            ],
        },

        fallbacks=[]
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        order_conversation
    )

    # Zakazni tasdiqlash
    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^✅ Zakazni tasdiqlash$"
            ),
            confirm_order
        )
    )

    # Asosiy tugmalar

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^📞 Siz bilan bog‘lanmoqchiman$"
            ),
            contact_us
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^💬 Madina bilan chat qilish$"
            ),
            madina_chat
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

    # Noma'lum xabarlar

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            unknown
        )
    )

    logger.info(
        "TheElvi bot ishga tushdi!"
    )

    app.run_polling()


# =========================
# UNKNOWN
# =========================

async def unknown(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "😊 Quyidagi bo‘limlardan birini tanlang:",
        reply_markup=MAIN_KEYBOARD
    )


# =========================
# ISHGA TUSHIRISH
# =========================

if __name__ == "__main__":
    main()
