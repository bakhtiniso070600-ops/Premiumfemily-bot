import os
import json
import urllib.request
import urllib.parse

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

API = f"https://api.telegram.org/bot{TOKEN}"


def api(method, data=None):
    data = data or {}
    encoded = urllib.parse.urlencode(data).encode()
    request = urllib.request.Request(
        f"{API}/{method}",
        data=encoded
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode())


def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        data["reply_markup"] = json.dumps({
            "inline_keyboard": keyboard
        })

    return api("sendMessage", data)


def main_menu():
    return [
        [
            {"text": "🛍 Каталог", "callback_data": "catalog"},
            {"text": "🔥 Акции", "callback_data": "sale"}
        ],
        [
            {"text": "✨ Новинки", "callback_data": "new"},
            {"text": "📦 Как заказать", "callback_data": "order"}
        ],
        [
            {"text": "💬 Связаться с нами", "callback_data": "contact"}
        ]
    ]


def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        send_message(
            chat_id,
            "🌸 Добро пожаловать в PremiumFemily! 🌸\n\n"
            "Товары для детей и взрослых с любовью ❤️\n\n"
            "Выберите нужный раздел:",
            main_menu()
        )

    elif text == "/help":
        send_message(
            chat_id,
            "Выберите раздел в меню ниже:",
            main_menu()
        )

    else:
        send_message(
            chat_id,
            "Пожалуйста, выберите нужный раздел 👇",
            main_menu()
        )


def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    message_id = callback["message"]["message_id"]
    data = callback["data"]

    api("answerCallbackQuery", {
        "callback_query_id": callback["id"]
    })

    if data == "catalog":
        text = (
            "🛍 КАТАЛОГ PREMIUMFEMILY\n\n"
            "👧 Товары для девочек\n"
            "👦 Товары для мальчиков\n"
            "🏠 Органайзеры для дома\n"
            "✨ Товары для взрослых\n\n"
            "Если вам понравился товар — "
            "напишите его название, и мы сообщим цену."
        )

    elif data == "sale":
        text = (
            "🔥 АКЦИИ\n\n"
            "Здесь будут товары со скидкой.\n\n"
            "Следите за обновлениями ❤️"
        )

    elif data == "new":
        text = (
            "✨ НОВИНКИ\n\n"
            "Здесь будут появляться новые товары PremiumFemily.\n\n"
            "Чтобы узнать цену товара, отправьте его название."
        )

    elif data == "order":
        text = (
            "📦 КАК ЗАКАЗАТЬ\n\n"
            "1️⃣ Выберите понравившийся товар.\n"
            "2️⃣ Напишите нам название товара.\n"
            "3️⃣ Мы сообщим цену и наличие.\n"
            "4️⃣ После подтверждения оформим заказ. ❤️"
        )

    elif data == "contact":
        text = (
            "💬 СВЯЗАТЬСЯ С НАМИ\n\n"
            "По вопросам заказа напишите нам в личные сообщения.\n\n"
            "🌸 PremiumFemily — с любовью для вас и вашей семьи."
        )

    else:
        text = "Выберите нужный раздел 👇"

    api("editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "reply_markup": json.dumps({
            "inline_keyboard": [
                [{"text": "⬅️ Главное меню", "callback_data": "home"}]
            ]
        })
    })


def main():
    offset = 0

    while True:
        updates = api("getUpdates", {
            "offset": offset,
            "timeout": 30
        })

        for update in updates.get("result", []):
            offset = update["update_id"] + 1

            if "message" in update:
                handle_message(update["message"])

            elif "callback_query" in update:
                callback = update["callback_query"]

                if callback["data"] == "home":
                    chat_id = callback["message"]["chat"]["id"]
                    message_id = callback["message"]["message_id"]

                    api("editMessageText", {
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": (
                            "🌸 PremiumFemily 🌸\n\n"
                            "Выберите нужный раздел:"
                        ),
                        "reply_markup": json.dumps({
                            "inline_keyboard": main_menu()
                        })
                    })

                    api("answerCallbackQuery", {
                        "callback_query_id": callback["id"]
                    })
                else:
                    handle_callback(callback)


if __name__ == "__main__":
    main()
