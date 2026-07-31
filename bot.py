import argparse
import io
import json
import logging
import re
import time
import traceback
from datetime import datetime

import telebot
from telebot import types, util

import methods
import settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(description="Usage: python bot.py")
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
args = parser.parse_args()

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, parse_mode=None)
MAX_ITEMS_PER_FILE = 5000

waiting_for_identifier = set()

PLATFORM_NAMES = {
    1: "m.vk.ru",
    2: "iPhone",
    3: "iPad",
    4: "Android",
    5: "Windows Phone",
    6: "Windows 8",
    7: "vk.ru",
}

SOCIAL_PREFIXES = {
    "skype": "@",
    "instagram": "instagram.com/",
    "twitter": "twitter.com/",
    "livejournal": "@",
    "facebook": "facebook.com/",
}

EXPORT_SECTIONS = (
    ("users_get", "profile"),
    ("wall_get", "wall"),
    ("docs_get", "documents"),
    ("photos_get_all", "photos"),
    ("notes_get", "notes"),
    ("videos_get", "videos"),
    ("friends_get", "friends"),
    ("gifts_get", "gifts"),
    ("stories_get", "stories"),
    ("groups_get", "groups"),
    ("market_get", "market"),
    ("followers_get", "followers")
)


def main_keyboard() -> types.ReplyKeyboardMarkup:
    """Persistent keyboard for the most common actions."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        types.KeyboardButton("🔎 Новый экспорт"),
        types.KeyboardButton("💡 Примеры ввода"),
        types.KeyboardButton("📋 Возможности")
    )
    return keyboard


def menu_markup() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🔎 Новый экспорт", callback_data="menu:export"),
        types.InlineKeyboardButton("📋 Возможности", callback_data="menu:features"),
        types.InlineKeyboardButton("💡 Примеры ввода", callback_data="menu:examples"),
    )
    return keyboard


def send_menu(chat_id, text=None) -> None:
    text = text or (
        "<b>VK Export</b>\n\n"
        "Выберите действие ниже или отправьте ID, логин либо ссылку на профиль VK."
    )
    bot.send_message(
        chat_id, text, parse_mode="HTML", reply_markup=main_keyboard()
    )
    bot.send_message(chat_id, "Что будем делать?", reply_markup=menu_markup())


def features_text() -> str:
    return (
        "<b>📋 Что умеет бот</b>\n\n"
        "• Загружает публичный профиль VK\n"
        "• Экспортирует стену, фото, видео и документы\n"
        "• Выгружает друзей, группы, подарки, истории и товары\n"
        "• Отправляет каждый раздел отдельным JSON-файлом\n"
        "• Большие разделы автоматически разбиваются на части\n\n"
        "Доступность данных зависит от настроек приватности VK."
    )


def examples_text() -> str:
    return (
        "<b>💡 Примеры ввода</b>\n\n"
        "<code>durov</code>\n"
        "<code>id1</code>\n"
        "<code>1</code>\n"
        "<code>https://vk.ru/durov</code>\n"
        "<code>https://vk.com/durov</code>\n"
        "<code>https://vkontakte.com/durov</code>\n"
        "<code>https://vkontakte.ru/durov</code>\n"
    )


def get_user_input(message):
    """Extract a VK username or ID from the first word of a message."""
    value = (message.text or "").split()
    return value[0].lower() if value else ""


def send_export_file(filename, data, chat_id) -> None:
    """Serialize an export to an in-memory file and send it to Telegram."""
    document = io.BytesIO(
        json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    )
    document.name = filename
    document.seek(0)
    bot.send_document(chat_id, document)


def send_export_parts(filename, data, section_name, chat_id) -> None:
    """Save and send a section in files of at most 1000 items."""
    all_items = data.get(section_name)
    if not isinstance(all_items, list) or len(all_items) <= MAX_ITEMS_PER_FILE:
        send_export_file(filename, data, chat_id)
        return

    filename_root, filename_extension = filename.rsplit(".", 1)
    filename_extension = "." + filename_extension
    for part_number, start in enumerate(
        range(0, len(all_items), MAX_ITEMS_PER_FILE), start=1
    ):
        part_data = {
            section_name: all_items[start : start + MAX_ITEMS_PER_FILE],
        }
        part_filename = f"{filename_root}_part{part_number}{filename_extension}"
        send_export_file(part_filename, part_data, chat_id)


def format_profile(profile) -> dict:
    """Convert the useful profile fields into the human-readable summary."""
    result = {}

    if "id" in profile:
        result["ID"] = profile["id"]
    if profile.get("first_name") and profile.get("last_name"):
        result["Name"] = f"{profile['first_name']} {profile['last_name']}"
    else:
        if profile.get("first_name"):
            result["First name"] = profile["first_name"]
        if profile.get("last_name"):
            result["Last name"] = profile["last_name"]

    optional_fields = {
        "nickname": "Middle name",
        "maiden_name": "Maiden name",
        "bdate": "Birthday",
        "site": "Site",
        "status": "Status",
        "mobile_phone": "Mobile",
        "home_phone": "Home phone",
    }
    for field, label in optional_fields.items():
        if profile.get(field):
            result[label] = profile[field]

    if profile.get("sex") == 1:
        result["Sex"] = "Female"
    elif profile.get("sex") == 2:
        result["Sex"] = "Male"

    if "last_seen" in profile and "deactivated" not in profile:
        last_seen = profile["last_seen"]
        result["Last seen"] = datetime.fromtimestamp(last_seen["time"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        if last_seen.get("platform") in PLATFORM_NAMES:
            result["Platform"] = PLATFORM_NAMES[last_seen["platform"]]
    else:
        result["Last seen"] = "Hidden by vk.me/app"

    for name, prefix in SOCIAL_PREFIXES.items():
        if profile.get(name):
            result[name.capitalize()] = f"{prefix}{profile[name]}"

    crop_photo = profile.get("crop_photo", {}).get("photo", {})
    sizes = crop_photo.get("sizes", [])
    if sizes:
        result["Avatar"] = max(sizes, key=lambda size: int(size["width"]))["url"]
    elif profile.get("photo_max_orig"):
        result["Avatar"] = profile["photo_max_orig"]
    if crop_photo.get("date"):
        result["Avatar date"] = datetime.fromtimestamp(crop_photo["date"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return result


def profile_message(profile_data) -> str:
    message = "".join(
        f"<b>— {key}</b>: {value}\n" for key, value in profile_data.items()
    )
    for text_to_remove in settings.TO_REMOVE:
        message = message.replace(text_to_remove, "")
    return message


@bot.message_handler(commands=["start", "menu"])
def regular_message(message):
    waiting_for_identifier.discard(message.chat.id)
    send_menu(message.chat.id)


@bot.message_handler(commands=["help"])
def help_message(message):
    send_menu(message.chat.id, features_text())


@bot.callback_query_handler(func=lambda call: call.data.startswith("menu:"))
def menu_callback(call):
    action = call.data.split(":", 1)[1]
    bot.answer_callback_query(call.id)
    if action == "export":
        waiting_for_identifier.add(call.message.chat.id)
        bot.send_message(
            call.message.chat.id,
            "<b>🔎 Новый экспорт</b>\n\n"
            "Отправьте ID, короткое имя или ссылку на профиль VK.",
            parse_mode="HTML",
            reply_markup=main_keyboard(),
        )
        bot.send_message(call.message.chat.id, examples_text(), parse_mode="HTML", reply_markup=menu_markup())
    elif action == "features":
        bot.send_message(call.message.chat.id, features_text(), parse_mode="HTML", reply_markup=menu_markup())
    elif action == "examples":
        bot.send_message(call.message.chat.id, examples_text(), parse_mode="HTML", reply_markup=menu_markup())


@bot.message_handler(func=lambda message: message.text in {
    "🔎 Новый экспорт", "💡 Примеры ввода", "📋 Возможности"
})
def keyboard_action(message):
    if message.text == "🔎 Новый экспорт":
        waiting_for_identifier.add(message.chat.id)
        bot.send_message(message.chat.id, "Отправьте ID, короткое имя или ссылку VK.", reply_markup=main_keyboard())
    elif message.text == "📋 Возможности":
        send_menu(message.chat.id, features_text())
    else:
        send_menu(message.chat.id, examples_text())


@bot.message_handler(func=lambda message: message.text is not None)
def get_info(message):
    chat_id = message.from_user.id

    waiting_for_identifier.discard(chat_id)

    try:
        user_input = get_user_input(message)
        profile_match = re.search(r"^(?:https?://)?(?:www\.)?(?:vk\.(?:com|ru)|vkontakte\.(?:com|ru))/([^/?#]+)",
            user_input.strip(), re.IGNORECASE)
        username = profile_match.group(1) if profile_match else user_input
        user_id = methods.get_numeric_id(username)
        start_time = int(time.time())
        profile = methods.users_get(user_id, args.verbose)[0]

        for text in util.split_string(profile_message(format_profile(profile)), 4096):
            bot.send_message(
                chat_id,
                f"<b>Parsing vk.ru/id{user_id}</b>\n{text}",
                parse_mode="HTML",
            )

        export_prefix = f"export{user_id}_{int(time.time())}"

        for method_name, filename_prefix in EXPORT_SECTIONS:
            try:
                exported_data = {
                    method_name: getattr(methods, method_name)(
                        user_id, args.verbose
                    ),
                }
                filename = f"{export_prefix}/{filename_prefix}{user_id}{settings.FILE_TYPE}"
                send_export_parts(filename, exported_data, method_name, chat_id)
            except Exception as error:
                bot.send_message(
                    chat_id,
                    f"error while parsing {method_name} section: {error}",
                    parse_mode="HTML",
                )

        end_time = int(time.time())
        bot.send_message(
            chat_id,
            f"<b>[{end_time}] End parsing of vk.ru/id{user_id}. "
            f"Elapsed {end_time - start_time} seconds</b>",
            parse_mode="HTML",
        )
    except Exception as error:
        error_message = "Looks like you entered an invalid ID or nickname."
        bot.send_message(chat_id, f"<b>{error_message}\n{error}</b>", parse_mode="HTML")
        logger.exception("Failed to process VK export request")
while True:
    try:
        bot.polling()
    except Exception:
        logger.exception("Bot polling failed")
        time.sleep(1)
