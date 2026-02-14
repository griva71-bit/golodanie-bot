import telebot
from telebot import types
import os
from threading import Thread
from http.server import HTTPServer, SimpleHTTPRequestHandler

BOT_TOKEN = os.environ['BOT_TOKEN']
ADMIN_ID = 75271120

bot = telebot.TeleBot(BOT_TOKEN)

pending_payments = {}

# Веб-сервер чтобы бот не засыпал
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), MyHandler)
    server.serve_forever()

Thread(target=run_server, daemon=True).start()

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton("🎬 Купить видеокурс"),
        types.KeyboardButton("📦 Купить коробку"),
        types.KeyboardButton("✉️ Написать автору")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🍃 *Добро пожаловать в Голодание с улыбкой!*\n\n"
        "Я — бот доктора Александрова, врача с 30-летним стажем.\n\n"
        "🎬 *Видеокурс* — полная методика лечебного голодания.\n"
        "Пошаговая инструкция: подготовка, вход, голодание, выход.\n\n"
        "📦 *Коробка для голодания* — всё необходимое для курса "
        "собрано в одной коробке. Доставка по всей России.\n\n"
        "Выберите что вас интересует — кнопки внизу 👇",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "🎬 Купить видеокурс")
def buy_course(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_paid = types.InlineKeyboardButton("✅ Я оплатил(а)", callback_data="paid_course")
    markup.add(btn_paid)
    bot.send_message(
        message.chat.id,
        "🎬 *Видеокурс Голодание с улыбкой*\n\n"
        "Стоимость: *2 900 руб*\n\n"
        "Переведите на карту Сбербанка:\n\n"
        "💳 `2202 2081 3882 1575`\n"
        "Получатель: *Вячеслав Юрьевич А.*\n\n"
        "В комментарии напишите ваш ник в Telegram\n\n"
        "После перевода нажмите кнопку ниже 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "📦 Купить коробку")
def buy_box(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_paid = types.InlineKeyboardButton("✅ Я оплатил(а)", callback_data="paid_box")
    markup.add(btn_paid)
    bot.send_message(
        message.chat.id,
        "📦 *Коробка для голодания*\n\n"
        "Всё необходимое для курса голодания в одной коробке.\n"
        "Доставка по всей России.\n\n"
        "Стоимость: *2 000 руб* + доставка\n\n"
        "Переведите на карту Сбербанка:\n\n"
        "💳 `2202 2081 3882 1575`\n"
        "Получатель: *Вячеслав Юрьевич А.*\n\n"
        "В комментарии напишите ваш ник в Telegram\n\n"
        "После перевода нажмите кнопку ниже 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "✉️ Написать автору")
def contact(message):
    pending_payments[message.from_user.id] = "waiting_message"
    bot.send_message(
        message.chat.id,
        "✉️ *Напишите ваше сообщение:*\n\n"
        "Просто отправьте текст — доктор Александров получит его и ответит!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "paid_course")
def paid_course(call):
    user = call.from_user
    username = f"@{user.username}" if user.username else f"{user.first_name}"
    markup_admin = types.InlineKeyboardMarkup(row_width=2)
    btn_confirm = types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_course_{user.id}")
    btn_reject = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}")
    markup_admin.add(btn_confirm, btn_reject)
    bot.send_message(
        ADMIN_ID,
        f"💰 *НОВАЯ ОПЛАТА КУРСА!*\n\n"
        f"👤 Клиент: {username}\n"
        f"🆔 ID: `{user.id}`\n"
        f"💵 Сумма: 2 900 руб\n"
        f"📦 Товар: Видеокурс\n\n"
        f"Проверьте поступление на карте и нажмите кнопку:",
        parse_mode="Markdown",
        reply_markup=markup_admin
    )
    bot.answer_callback_query(call.id, "Заявка отправлена!")
    bot.send_message(
        call.message.chat.id,
        "⏳ *Спасибо!*\n\n"
        "Ваша оплата проверяется. Обычно это занимает несколько минут.\n"
        "После подтверждения вы получите видеокурс прямо сюда! 🎬",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "paid_box")
def paid_box(call):
    user = call.from_user
    username = f"@{user.username}" if user.username else f"{user.first_name}"
    markup_admin = types.InlineKeyboardMarkup(row_width=2)
    btn_confirm = types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_box_{user.id}")
    btn_reject = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}")
    markup_admin.add(btn_confirm, btn_reject)
    bot.send_message(
        ADMIN_ID,
        f"💰 *НОВАЯ ОПЛАТА КОРОБКИ!*\n\n"
        f"👤 Клиент: {username}\n"
        f"🆔 ID: `{user.id}`\n"
        f"💵 Сумма: 2 000 руб\n"
        f"📦 Товар: Коробка для голодания\n\n"
        f"Проверьте поступление на карте и нажмите кнопку:",
        parse_mode="Markdown",
        reply_markup=markup_admin
    )
    bot.answer_callback_query(call.id, "Заявка отправлена!")
    bot.send_message(
        call.message.chat.id,
        "⏳ *Спасибо!*\n\n"
        "Ваша оплата проверяется.\n"
        "После подтверждения мы попросим адрес доставки 📬",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_course_"))
def confirm_course(call):
    user_id = int(call.data.split("_")[2])
    bot.send_message(
        user_id,
        "✅ *Оплата подтверждена!*\n\n"
        "🎬 Вот ваш видеокурс! Приятного просмотра!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    # Отправляем видео
    try:
        with open("course_video.mp4", "rb") as video:
            bot.send_video(user_id, video, caption="🎬 Видеокурс: Голодание с улыбкой\n\nДоктор Александров")
    except:
        bot.send_message(user_id, "📹 Видео скоро будет отправлено! Ожидайте.")
        bot.send_message(ADMIN_ID, f"⚠️ Не удалось отправить видео клиенту {user_id}. Файл course_video.mp4 не найден!")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Курс подтвержден и видео отправлено клиенту {user_id}"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_box_"))
def confirm_box(call):
    user_id = int(call.data.split("_")[2])
    pending_payments[user_id] = "waiting_address"
    bot.send_message(
        user_id,
        "✅ *Оплата подтверждена!*\n\n"
        "📬 Напишите ваш адрес доставки и ФИО получателя:\n\n"
        "Просто отправьте текстом в этот чат 👇",
        parse_mode="Markdown"
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Коробка подтверждена для {user_id}. Ждём адрес."
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_payment(call):
    user_id = int(call.data.split("_")[1])
    bot.send_message(
        user_id,
        "❌ *Оплата не найдена*\n\n"
        "Проверьте реквизиты и попробуйте снова.\n"
        "Или нажмите «Написать автору» для помощи 👇",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"❌ Отклонено для {user_id}"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user = message.from_user
    username = f"@{user.username}" if user.username else f"{user.first_name}"
    user_id = user.id

    if pending_payments.get(user_id) == "waiting_address":
        bot.send_message(
            ADMIN_ID,
            f"📬 *Адрес доставки коробки:*\n\n"
            f"👤 Клиент: {username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"📍 Адрес: {message.text}",
            parse_mode="Markdown"
        )
        bot.reply_to(message, "✅ Адрес записан! Свяжемся с вами по доставке! 📦")
        pending_payments.pop(user_id, None)
        return

    if pending_payments.get(user_id) == "waiting_message":
        markup_admin = types.InlineKeyboardMarkup()
        btn_reply = types.InlineKeyboardButton("💬 Ответить", url=f"tg://user?id={user_id}")
        markup_admin.add(btn_reply)
        bot.send_message(
            ADMIN_ID,
            f"✉️ *Сообщение от клиента:*\n\n"
            f"👤 От: {username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"💬 Текст: {message.text}",
            parse_mode="Markdown",
            reply_markup=markup_admin
        )
        bot.reply_to(
            message,
            "✅ Сообщение отправлено! Доктор ответит в ближайшее время.",
            reply_markup=get_main_keyboard()
        )
        pending_payments.pop(user_id, None)
        return

    if user_id == ADMIN_ID and message.reply_to_message:
        try:
            text = message.reply_to_message.text
            if "ID: `" in text:
                client_id = int(text.split("ID: `")[1].split("`")[0])
                bot.send_message(
                    client_id,
                    f"💬 *Ответ от доктора Александрова:*\n\n{message.text}",
                    parse_mode="Markdown",
                    reply_markup=get_main_keyboard()
                )
                bot.reply_to(message, "✅ Ответ отправлен клиенту!")
                return
        except:
            pass

    bot.send_message(
        message.chat.id,
        "Выберите действие кнопками внизу 👇",
        reply_markup=get_main_keyboard()
    )

print("Bot started!")
bot.infinity_polling()