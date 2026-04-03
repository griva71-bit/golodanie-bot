import telebot
from telebot import types
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
from urllib.request import urlopen
import hashlib
import hmac
from urllib.parse import parse_qs

BOT_TOKEN = os.environ['BOT_TOKEN']
YOOMONEY_SECRET = os.environ['YOOMONEY_SECRET']
ADMIN_ID = 75271120

VIDEO_SHORT_FILE_ID = "BAACAgIAAxkBAAPbac2AEGt9Cq9W7kTFgBvtnGCK-eAAAtOPAAL3GHBKfKndY7V27MM6BA"
VIDEO_FULL_FILE_ID = "BAACAgIAAxkBAAPWac1w70dDBbzInRVOEstQwJZzTIUAAhu2AAL3GHhKVGZsJtSHGnY6BA"

bot = telebot.TeleBot(BOT_TOKEN)
pending_payments = {}
delivery_data = {}


def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("🎬 Купить видеокурс"),
               types.KeyboardButton("📦 Купить коробку"),
               types.KeyboardButton("📢 Новости"),
               types.KeyboardButton("✉️ Написать автору"))
    return markup


def send_course(user_id):
    try:
        bot.send_message(
            user_id,
            "✅ *Оплата подтверждена! Отправляем видеокурс...*",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard())
        bot.send_video(
            user_id,
            VIDEO_SHORT_FILE_ID,
            caption="🎬 *Вводное видео — краткий обзор курса*\nДоктор Александров",
            parse_mode="Markdown")
        bot.send_video(
            user_id,
            VIDEO_FULL_FILE_ID,
            caption="📚 *Полный курс с расшифровкой и пояснениями*\nДоктор Александров",
            parse_mode="Markdown")
        bot.send_message(
            user_id,
            "🎉 *Добро пожаловать в закрытый клуб!*\n\n"
            "💬 Присоединяйтесь к нашему сообществу:\n\n"
            "👉 https://t.me/+ROlmZP7pM2w4OWFi",
            parse_mode="Markdown")
        bot.send_message(
            ADMIN_ID,
            f"✅ *Курс автоматически отправлен!*\n🆔 ID: `{user_id}`",
            parse_mode="Markdown")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Ошибка отправки курса для {user_id}: {e}")


def check_yoomoney_hash(data: dict, secret: str) -> bool:
    keys = [
        "notification_type", "operation_id", "amount",
        "currency", "datetime", "sender",
        "codepro", "notification_secret", "label"
    ]
    values = []
    for k in keys:
        if k == "notification_secret":
            values.append(secret)
        else:
            v = data.get(k, [""])[0] if isinstance(data.get(k), list) else data.get(k, "")
            values.append(str(v))
    string = "&".join(values)
    expected = hashlib.sha1(string.encode("utf-8")).hexdigest()
    received = data.get("sha1_hash", [""])[0] if isinstance(data.get("sha1_hash"), list) else data.get("sha1_hash", "")
    return expected == received


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def do_POST(self):
        if self.path == "/payment":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode("utf-8")
            data = parse_qs(body)

            if check_yoomoney_hash(data, YOOMONEY_SECRET):
                label = data.get("label", [""])[0]
                amount = data.get("amount", ["0"])[0]

                if label.startswith("course_"):
                    user_id = int(label.split("_")[1])
                    Thread(target=send_course, args=(user_id,)).start()

                elif label.startswith("box_"):
                    user_id = int(label.split("_")[1])
                    username = data.get("sender", ["неизвестен"])[0]
                    markup_admin = types.InlineKeyboardMarkup(row_width=2)
                    markup_admin.add(
                        types.InlineKeyboardButton(
                            "✅ Подтвердить", callback_data=f"confirm_box_{user_id}"),
                        types.InlineKeyboardButton(
                            "❌ Отклонить", callback_data=f"reject_{user_id}"))
                    bot.send_message(
                        ADMIN_ID,
                        f"💰 *ОПЛАТА КОРОБКИ ПОЛУЧЕНА!*\n\n"
                        f"🆔 ID: `{user_id}`\n"
                        f"💵 Сумма: {amount} руб\n\n"
                        f"Нажмите подтвердить для оформления доставки:",
                        parse_mode="Markdown",
                        reply_markup=markup_admin)
                    bot.send_message(
                        user_id,
                        "✅ *Оплата получена!*\n\nОжидайте подтверждения от администратора 📬",
                        parse_mode="Markdown")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Получен webhook с неверной подписью!")

        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def run_server():
    server = HTTPServer(('0.0.0.0', 8080), MyHandler)
    server.serve_forever()


Thread(target=run_server, daemon=True).start()


def self_ping():
    while True:
        time.sleep(240)
        try:
            urlopen("http://localhost:8080")
        except:
            pass


Thread(target=self_ping, daemon=True).start()


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
        "⚠️ *Дисклеймер:* Все материалы носят исключительно "
        "информационный характер и не являются медицинской рекомендацией. "
        "Перед применением проконсультируйтесь с врачом.\n\n"
        "Выберите что вас интересует — кнопки внизу 👇",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard())


@bot.message_handler(func=lambda m: m.text == "📢 Новости")
def news_channel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Открыть канал", url="https://t.me/doconhunger"))
    bot.send_message(message.chat.id,
                     "📢 *Канал «Врач на Голоде»*\n\n"
                     "Новости, советы и истории от доктора Александрова.\n"
                     "Подписывайтесь! 👇",
                     parse_mode="Markdown",
                     reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "🎬 Купить видеокурс")
def buy_course(message):
    user_id = message.from_user.id
    url = f"https://yoomoney.ru/quickpay/confirm?receiver=4100118420031768&quickpay-form=donate&sum=3900&label=course_{user_id}"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💳 Оплатить 3 900 руб", url=url)
    )
    bot.send_message(
        message.chat.id,
        "🎬 *Видеокурс Голодание с улыбкой*\n\n"
        "Стоимость: *3 900 руб*\n\n"
        "⚠️ *Дисклеймер:* Материалы курса носят исключительно "
        "информационный характер и не являются медицинской рекомендацией. "
        "Перед применением проконсультируйтесь с врачом.\n\n"
        "1️⃣ Нажмите *«Оплатить»*\n"
        "2️⃣ Оплатите картой или из кошелька\n"
        "3️⃣ Видеокурс придёт *автоматически* сразу после оплаты! 🎬",
        parse_mode="Markdown",
        reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "📦 Купить коробку")
def buy_box(message):
    user_id = message.from_user.id
    url = f"https://yoomoney.ru/quickpay/confirm?receiver=4100118420031768&quickpay-form=donate&sum=2900&label=box_{user_id}"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💳 Оплатить 2 900 руб", url=url)
    )
    bot.send_message(
        message.chat.id,
        "📦 *Коробка для голодания*\n\n"
        "Всё необходимое для курса голодания в одной коробке.\n"
        "Доставка по всей России через СДЭК.\n\n"
        "Стоимость: *2 900 руб* + доставка\n\n"
        "1️⃣ Нажмите *«Оплатить»*\n"
        "2️⃣ Оплатите картой или из кошелька\n"
        "3️⃣ После оплаты попросим адрес доставки 📬",
        parse_mode="Markdown",
        reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "✉️ Написать автору")
def contact(message):
    pending_payments[message.from_user.id] = "waiting_message"
    bot.send_message(
        message.chat.id,
        "✉️ *Напишите ваше сообщение:*\n\n"
        "Просто отправьте текст — доктор Александров получит его и ответит!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard())


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_box_"))
def confirm_box(call):
    user_id = int(call.data.split("_")[2])
    pending_payments[user_id] = "waiting_fio"
    bot.send_message(
        user_id,
        "📦 *Отлично! Оформляем доставку СДЭК.*\n\n"
        "Вам нужно будет написать:\n"
        "• ФИО\n"
        "• Телефон\n"
        "• Адрес или пункт СДЭК\n\n"
        "Начнём! Напишите ваше *ФИО:*",
        parse_mode="Markdown")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Коробка подтверждена для {user_id}. Ждём данные доставки.")


@bot.message_handler(func=lambda message: pending_payments.get(message.from_user.id) == "waiting_fio")
def get_fio(message):
    user_id = message.from_user.id
    delivery_data[user_id] = {"fio": message.text}
    pending_payments[user_id] = "waiting_phone"
    bot.send_message(user_id,
                     f"✅ *ФИО:* {message.text}\n\nТеперь напишите ваш *телефон:*",
                     parse_mode="Markdown")


@bot.message_handler(func=lambda message: pending_payments.get(message.from_user.id) == "waiting_phone")
def get_phone(message):
    user_id = message.from_user.id
    delivery_data[user_id]["phone"] = message.text
    pending_payments[user_id] = "waiting_address"
    bot.send_message(user_id,
                     f"✅ *Телефон:* {message.text}\n\nТеперь напишите *адрес или пункт СДЭК:*",
                     parse_mode="Markdown")


@bot.message_handler(func=lambda message: pending_payments.get(message.from_user.id) == "waiting_address")
def get_address(message):
    user_id = message.from_user.id
    delivery_data[user_id]["address"] = message.text
    fio = delivery_data[user_id]["fio"]
    phone = delivery_data[user_id]["phone"]
    address = message.text
    bot.send_message(
        user_id,
        f"✅ *Данные приняты! Ожидайте отправку.*\n\n"
        f"👤 ФИО: {fio}\n"
        f"📞 Телефон: {phone}\n"
        f"📍 Адрес СДЭК: {address}",
        parse_mode="Markdown")
    bot.send_message(
        ADMIN_ID,
        f"📬 *Новый заказ на доставку!*\n\n"
        f"👤 ФИО: {fio}\n"
        f"📞 Телефон: {phone}\n"
        f"📍 Адрес СДЭК: {address}\n"
        f"🆔 ID покупателя: {user_id}",
        parse_mode="Markdown")
    pending_payments.pop(user_id, None)
    delivery_data.pop(user_id, None)


@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_payment(call):
    user_id = int(call.data.split("_")[1])
    bot.send_message(
        user_id,
        "❌ *Оплата не найдена*\n\nПроверьте и попробуйте снова или напишите автору 👇",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard())
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"❌ Отклонено для {user_id}")


@bot.message_handler(content_types=['video', 'document'])
def get_file_id(message):
    if message.from_user.id == ADMIN_ID:
        fid = message.video.file_id if message.video else message.document.file_id
        bot.send_message(ADMIN_ID, f"`{fid}`", parse_mode="Markdown")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user = message.from_user
    username = f"@{user.username}" if user.username else f"{user.first_name}"
    user_id = user.id

    if pending_payments.get(user_id) == "waiting_message":
        markup_admin = types.InlineKeyboardMarkup()
        markup_admin.add(types.InlineKeyboardButton("💬 Ответить", url=f"tg://user?id={user_id}"))
        bot.send_message(
            ADMIN_ID,
            f"✉️ *Сообщение от клиента:*\n\n👤 {username}\n🆔 ID: `{user_id}`\n💬 {message.text}",
            parse_mode="Markdown",
            reply_markup=markup_admin)
        bot.reply_to(message,
                     "✅ Сообщение отправлено! Доктор ответит в ближайшее время.",
                     reply_markup=get_main_keyboard())
        pending_payments.pop(user_id, None)
        return

    bot.send_message(message.chat.id, "Выберите действие 👇", reply_markup=get_main_keyboard())


import threading

def run_bot():
    print("Bot started!")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    app.run(host='0.0.0.0', port=8080)
