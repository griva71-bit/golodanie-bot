from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

def run():
    HTTPServer(("0.0.0.0", 8080), H).serve_forever()

Thread(target=run, daemon=True).start()
import telebot
from telebot import types
import os
import time

BOT_TOKEN = os.environ['BOT_TOKEN']
ADMIN_ID = 75271120
VIDEO_FILE_ID = "BQACAgIAAxkBAAMXaZC5Xdtc0IFrpOwZy_CdVYxVVkAAAjKQAAIlYYlIM817HLFrmNE6BA"

bot = telebot.TeleBot(BOT_TOKEN)
pending_payments = {}

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton("🎬 Купить видеокурс"),
        types.KeyboardButton("📦 Купить коробку"),
        types.KeyboardButton("📢 Новости"),
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
        "📢 *Новости* — наш Telegram-канал с полезными материалами.\n\n"
        "Выберите что вас интересует — кнопки внизу 👇",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "📢 Новости")
def news_channel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Открыть канал", url="https://t.me/doconhunger"))
    bot.send_message(
        message.chat.id,
        "📢 *Канал «Врач на Голоде»*\n\n"
        "Новости, советы и истории от доктора Александрова.\n"
        "Подписывайтесь! 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "🎬 Купить видеокурс")
def buy_course(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("✅ Я оплатил(а)", callback_data="paid_course"))
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
    markup.add(types.InlineKeyboardButton("✅ Я оплатил(а)", callback_data="paid_box"))
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
    markup_admin.add(
        types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_course_{user.id}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}")
    )
    bot.send_message(
        ADMIN_ID,
        f"💰 *НОВАЯ ОПЛАТА КУРСА!*\n\n"
        f"👤 Клиент: {username}\n"
        f"🆔 ID: `{user.id}`\n"
        f"💵 Сумма: 2 900 руб\n"
        f"📦 Товар: Видеокурс\n\n"
        f"Проверьте поступление и нажмите кнопку:",
        parse_mode="Markdown",
        reply_markup=markup_admin
    )
    bot.answer_callback_query(call.id, "Заявка отправлена!")
    bot.send_message(
        call.message.chat.id,
        "⏳ *Спасибо!*\n\nОплата проверяется. После подтверждения получите видеокурс! 🎬",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "paid_box")
def paid_box(call):
    user = call.from_user
    username = f"@{user.username}" if user.username else f"{user.first_name}"
    markup_admin = types.InlineKeyboardMarkup(row_width=2)
    markup_admin.add(
        types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_box_{user.id}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}")
    )
    bot.send_message(
        ADMIN_ID,
        f"💰 *НОВАЯ ОПЛАТА КОРОБКИ!*\n\n"
        f"👤 Клиент: {username}\n"
        f"🆔 ID: `{user.id}`\n"
        f"💵 Сумма: 2 000 руб\n"
        f"📦 Товар: Коробка\n\n"
        f"Проверьте поступление и нажмите кнопку:",
        parse_mode="Markdown",
        reply_markup=markup_admin
    )
    bot.answer_callback_query(call.id, "Заявка отправлена!")
    bot.send_message(
        call.message.chat.id,
        "⏳ *Спасибо!*\n\nОплата проверяется. После подтверждения попросим адрес 📬",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_course_"))
def confirm_course(call):
    user_id = int(call.data.split("_")[2])
    bot.send_message(
        user_id,
        "✅ *Оплата подтверждена!*\n\n🎬 Вот ваш видеокурс! Приятного просмотра!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    try:
        bot.send_document(user_id, VIDEO_FILE_ID, caption="🎬 Видеокурс: Голодание с улыбкой\nДоктор Александров")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Ошибка отправки видео: {e}")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Курс подтвержден и отправлен клиенту {user_id}"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_box_"))
def confirm_box(call):
    user_id = int(call.data.split("_")[2])
    pending_payments[user_id] = "waiting_address"
    bot.send_message(
        user_id,
        "✅ *Оплата подтверждена!*\n\n📬 Напишите адрес доставки и ФИО получателя:",
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
        "❌ *Оплата не найдена*\n\nПроверьте реквизиты или напишите автору 👇",
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
            f"📬 *Адрес доставки:*\n\n👤 {username}\n🆔 ID: `{user_id}`\n📍 {message.text}",
            parse_mode="Markdown"
        )
        bot.reply_to(message, "✅ Адрес записан! Свяжемся по доставке! 📦",
                     reply_markup=get_main_keyboard())
        pending_payments.pop(user_id, None)
        return

    if pending_payments.get(user_id) == "waiting_message":
        markup_admin = types.InlineKeyboardMarkup()
        markup_admin.add(types.InlineKeyboardButton("💬 Ответить", url=f"tg://user?id={user_id}"))
        bot.send_message(
            ADMIN_ID,
            f"✉️ *Сообщение от клиента:*\n\n👤 {username}\n🆔 ID: `{user_id}`\n💬 {message.text}",
            parse_mode="Markdown",
            reply_markup=markup_admin
        )
        bot.reply_to(message, "✅ Сообщение отправлено! Доктор ответит в ближайшее время.",
                     reply_markup=get_main_keyboard())
        pending_payments.pop(user_id, None)
        return

    bot.send_message(message.chat.id, "Выберите действие 👇", reply_markup=get_main_keyboard())

print("Bot started!")
bot.infinity_polling()
