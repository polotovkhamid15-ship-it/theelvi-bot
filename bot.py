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
    CallbackQueryHandler,
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

ASK_PRODUCT, ASK_NAME, ASK_PHONE, ASK_LOCATION = range(4)


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
            "text/plain; charset=utf-8",
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
            HealthHandler,
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
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data.clear()

    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "Men *Madina*, TheElvi konsultantiman 👜✨\n"
        "Sizga mahsulot tanlash va zakaz qilishda yordam beraman.\n\n"
        "Quyidagilardan birini tanlang 👇",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================
# 👜 SUMKA KERAK EDI
# =========================

async def start_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data.clear()

    await update.message.reply_text(
        "Albatta 😊 Sizga yordam beraman! 👜\n\n"
        "Qanday sumka qidiryapsiz?\n\n"
        "Masalan:\n"
        "🖤 Qora sumka\n"
        "🎀 Kundalik sumka\n"
        "✨ Klassik sumka\n"
        "👜 Kichik sumka\n\n"
        "Mahsulot nomini yoki qanday sumka kerakligini yozing 👇"
    )

    return ASK_PRODUCT


# =========================
# MAHSULOT
# =========================

async def ask_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data["product"] = (
        update.message.text.strip()
    )

    await update.message.reply_text(
        "Zo‘r tanlov 😊👜\n\n"
        "Zakazingizni rasmiylashtirish uchun "
        "ismingizni yozib qoldiring 👇"
    )

    return ASK_NAME


# =========================
# ISM
# =========================

async def ask_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data["name"] = (
        update.message.text.strip()
    )

    phone_keyboard = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    "📱 Telefon raqamimni yuborish",
                    request_contact=True,
                )
            ],
            [
                KeyboardButton(
                    "✍️ Raqamni yozish"
                )
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await update.message.reply_text(
        "Rahmat! 😊\n\n"
        "📱 Endi bog‘lanishimiz uchun "
        "telefon raqamingizni yuboring.",
        reply_markup=phone_keyboard,
    )

    return ASK_PHONE


# =========================
# TELEFON
# =========================

async def ask_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message.contact:

        context.user_data["phone"] = (
            update.message.contact.phone_number
        )

    elif update.message.text == "✍️ Raqamni yozish":

        await update.message.reply_text(
            "📱 Telefon raqamingizni yozing:\n\n"
            "Masalan: +998901234567"
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
                    request_location=True,
                )
            ],
            [
                KeyboardButton(
                    "✍️ Manzilni yozish"
                )
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await update.message.reply_text(
        "Ajoyib! 👍\n\n"
        "📍 Endi yetkazib berish manzilingizni yuboring.\n\n"
        "Eng qulayi — *Lokatsiyani yuborish* tugmasini bosing.\n"
        "Shunda bizga xaritadagi aniq joylashuvingiz keladi.",
        parse_mode="Markdown",
        reply_markup=location_keyboard,
    )

    return ASK_LOCATION


# =========================
# LOKATSIYA / MANZIL
# =========================

async def ask_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.message.location:

        location = update.message.location

        context.user_data["latitude"] = (
            location.latitude
        )

        context.user_data["longitude"] = (
            location.longitude
        )

        context.user_data["address"] = (
            f"https://www.google.com/maps?q="
            f"{location.latitude},"
            f"{location.longitude}"
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

    # =====================
    # TASDIQLASH
    # =====================

    product = context.user_data.get(
        "product",
        "-",
    )

    name = context.user_data.get(
        "name",
        "-",
    )

    phone = context.user_data.get(
        "phone",
        "-",
    )

    address = context.user_data.get(
        "address",
        "-",
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Zakazni tasdiqlash",
                    callback_data="confirm_order",
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Zakazni bekor qilish",
                    callback_data="cancel_order",
                )
            ],
        ]
    )

    await update.message.reply_text(
        "🎀 *Zakazingiz tayyor!*\n\n"
        f"👤 Ism: {name}\n"
        f"📱 Telefon: {phone}\n"
        f"👜 Mahsulot: {product}\n"
        f"📍 Manzil: {address}\n\n"
        "Ma’lumotlar to‘g‘rimi?",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

    return ConversationHandler.END


# =========================
# ZAKAZNI TASDIQLASH
# =========================

async def confirm_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    user = query.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "username yo‘q"
    )

    product = context.user_data.get(
        "product",
        "-",
    )

    name = context.user_data.get(
        "name",
        "-",
    )

    phone = context.user_data.get(
        "phone",
        "-",
    )

    address = context.user_data.get(
        "address",
        "-",
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
            parse_mode="Markdown",
        )

        if (
            "latitude" in context.user_data
            and "longitude" in context.user_data
        ):

            await context.bot.send_location(
                chat_id=OWNER_CHAT_ID,
                latitude=context.user_data[
                    "latitude"
                ],
                longitude=context.user_data[
                    "longitude"
                ],
            )

        logger.info(
            "Yangi zakaz egasiga yuborildi."
        )

    except Exception as e:

        logger.error(
            f"Zakaz yuborishda xato: {e}"
        )

    await query.edit_message_text(
        "✅ *Zakazingiz qabul qilindi!*\n\n"
        "Rahmat! 👜✨\n"
        "Tez orada Madina siz bilan bog‘lanadi.",
        parse_mode="Markdown",
    )

    context.user_data.clear()


# =========================
# ZAKAZNI BEKOR QILISH
# =========================

async def cancel_order_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    context.user_data.clear()

    await query.edit_message_text(
        "❌ Zakaz bekor qilindi."
    )


# =========================
# 📞 BIZ BILAN BOG‘LANISH
# =========================

async def contact_us(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    phone_keyboard = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    "📱 Telefon raqamimni yuborish",
                    request_contact=True,
                )
            ],
            [
                KeyboardButton(
                    "✍️ Raqamni yozish"
                )
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    context.user_data["contact_request"] = True

    await update.message.reply_text(
        "Albatta 😊\n\n"
        "Siz bilan bog‘lanishimiz uchun "
        "telefon raqamingizni qoldiring 📱",
        reply_markup=phone_keyboard,
    )


# =========================
# 📞 ALOQA RAQAMINI QABUL QILISH
# =========================

async def receive_contact(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not context.user_data.get(
        "contact_request"
    ):
        return

    if update.message.contact:

        phone = (
            update.message.contact.phone_number
        )

    elif update.message.text == "✍️ Raqamni yozish":

        await update.message.reply_text(
            "📱 Telefon raqamingizni yozing:"
        )

        return

    else:

        phone = update.message.text.strip()

    user = update.message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "username yo‘q"
    )

    try:

        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=(
                "📞 *YANGI ALOQA SO‘ROVI!*\n\n"
                f"👤 Ism: {user.first_name}\n"
                f"📱 Telefon: {phone}\n"
                f"💬 Telegram: {username}\n"
                f"🆔 ID: {user.id}"
            ),
            parse_mode="Markdown",
        )

    except Exception as e:

        logger.error(
            f"Aloqa yuborishda xato: {e}"
        )

    context.user_data.clear()

    await update.message.reply_text(
        "✅ Rahmat! 😊\n\n"
        "Telefon raqamingizni oldik.\n"
        "Tez orada siz bilan bog‘lanamiz.",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================
# 💬 MADINA BILAN CHAT
# =========================

async def madina_chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "💬 *Madina bilan chat*\n\n"
        "Albatta 😊 Men shu yerdaman.\n\n"
        "Sizga qanday sumka kerak?\n"
        "Xohlasangiz mahsulot, rang yoki "
        "narxi haqida so‘rashingiz mumkin. 👜✨",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================
# 🚚 YETKAZIB BERISH
# =========================

async def delivery(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "🚚 *Ha, yetkazib berish mavjud!*\n\n"
        "📍 Toshkent bo‘ylab yetkazib beramiz.\n"
        "🇺🇿 O‘zbekiston bo‘ylab ham yuborish mumkin.\n\n"
        "Yetkazib berish narxi manzilga qarab "
        "aniqlanadi.\n\n"
        "Zakaz qilish uchun:\n"
        "👜 *Sumka kerak edi* tugmasini bosing.",
        parse_mode="Markdown",
        reply_markup=MAIN_KEYBOARD,
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

    # Health server
    thread = threading.Thread(
        target=run_health_server,
        daemon=True,
    )

    thread.start()

    logger.info(
        f"Health server {PORT}-portda ishga tushdi."
    )

    # Telegram bot
    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # =====================
    # ZAKAZ CONVERSATION
    # =====================

    order_conversation = ConversationHandler(

        entry_points=[
            MessageHandler(
                filters.Regex(
                    r"^👜 Sumka kerak edi$"
                ),
                start_order,
            )
        ],

        states={

            ASK_PRODUCT: [
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND,
                    ask_product,
                )
            ],

            ASK_NAME: [
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND,
                    ask_name,
                )
            ],

            ASK_PHONE: [
                MessageHandler(
                    (
                        filters.CONTACT
                        | filters.TEXT
                    )
                    & ~filters.COMMAND,
                    ask_phone,
                )
            ],

            ASK_LOCATION: [
                MessageHandler(
                    (
                        filters.LOCATION
                        | filters.TEXT
                    )
                    & ~filters.COMMAND,
                    ask_location,
                )
            ],
        },

        fallbacks=[],
    )

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        order_conversation
    )

    # =====================
    # ZAKAZ TUGMALARI
    # =====================

    app.add_handler(
        CallbackQueryHandler(
            confirm_order,
            pattern=r"^confirm_order$",
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            cancel_order_callback,
            pattern=r"^cancel_order$",
        )
    )

    # =====================
    # BOG‘LANISH
    # =====================

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^📞 Siz bilan bog‘lanmoqchiman$"
            ),
            contact_us,
        )
    )

    # =====================
    # MADINA CHAT
    # =====================

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^💬 Madina bilan chat qilish$"
            ),
            madina_chat,
        )
    )

    # =====================
    # YETKAZIB BERISH
    # =====================

    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^🚚 Yetkazib berish bormi\?$"
            ),
            delivery,
        )
    )

    # =====================
    # ALOQA TELEFONI
    # =====================

    app.add_handler(
        MessageHandler(
            (
                filters.CONTACT
                | filters.Regex(
                    r"^✍️ Raqamni yozish$"
                )
            ),
            receive_contact,
        )
    )

    # =====================
    # UNKNOWN
    # =====================

    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            unknown,
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
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "😊 Quyidagi bo‘limlardan birini tanlang:",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================
# START
# =========================

if __name__ == "__main__":
    main()
