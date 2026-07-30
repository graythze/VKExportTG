import argparse
import json
import os
import re
import shutil
import time
import traceback
from datetime import datetime

import telebot
from telebot import util

import methods
import settings


parser = argparse.ArgumentParser(description="Usage: python bot.py")
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
args = parser.parse_args()

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, parse_mode=None)
MAX_ITEMS_PER_FILE = 5000

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
)


def clean_folder(folder):
    """Remove previously generated exports from the working directory."""
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


def get_user_input(message):
    """Extract a VK username or ID from the first word of a message."""
    value = (message.text or "").split()
    return value[0].lower() if value else ""


def send_export_file(filename, data, chat_id):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    with open(filename, "rb") as document:
        bot.send_document(chat_id, document)


def send_export_parts(filename, data, section_name, chat_id):
    """Save and send a section in files of at most 1000 items."""
    all_items = data.get(section_name)
    if not isinstance(all_items, list) or len(all_items) <= MAX_ITEMS_PER_FILE:
        send_export_file(filename, data, chat_id)
        return

    filename_root, filename_extension = os.path.splitext(filename)
    for part_number, start in enumerate(
        range(0, len(all_items), MAX_ITEMS_PER_FILE), start=1
    ):
        part_data = {
            "id": data["id"],
            section_name: all_items[start : start + MAX_ITEMS_PER_FILE],
        }
        part_filename = f"{filename_root}_part{part_number}{filename_extension}"
        send_export_file(part_filename, part_data, chat_id)


def format_profile(profile):
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
        result["Last seen"] = datetime.utcfromtimestamp(last_seen["time"]).strftime(
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
        result["Avatar date"] = datetime.utcfromtimestamp(crop_photo["date"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return result


def profile_message(profile_data):
    message = "".join(
        f"<b>— {key}</b>: {value}\n" for key, value in profile_data.items()
    )
    for text_to_remove in settings.TO_REMOVE:
        message = message.replace(text_to_remove, "")
    return message


@bot.message_handler(commands=["start"])
def regular_message(message):
    bot.send_message(
        message.chat.id,
        "<b>🤖 Welcome to bot!</b>\n\n"
        "Bot allows export public data from any VK user page\n\n"
        "🔎 To start, send user ID or nickname to start.\n\n"
        "Allowed types:\n   Nickname: <b>durov</b>\n"
        "   Origin ID: <b>id1</b>\n   Numeric ID: <b>1</b>",
        parse_mode="HTML",
    )


@bot.message_handler(func=lambda message: message.text is not None)
def get_info(message):
    export_path = None
    chat_id = message.from_user.id

    try:
        user_input = get_user_input(message)
        profile_match = re.search(r"^(?:https?://)?(?:www\.)?(?:vk\.(?:com|ru)|vkontakte\.(?:com|ru))/([^/?#]+)",
            user_input.strip(), re.IGNORECASE)
        username = profile_match.group(1) if profile_match else user_input
        user_id = methods.get_numeric_id(username, settings.VK_TOKEN, settings.V)
        start_time = int(time.time())
        profile = methods.users_get(user_id, settings.VK_TOKEN, settings.V, args.verbose)[0]

        for text in util.split_string(profile_message(format_profile(profile)), 4096):
            bot.send_message(
                chat_id,
                f"<b>[{start_time}] Started parsing for vk.ru/id{user_id}</b>\n{text}",
                parse_mode="HTML",
            )

        export_path = os.path.join(settings.default_path, f"export{user_id}_{int(time.time())}")
        os.mkdir(export_path)

        for method_name, filename_prefix in EXPORT_SECTIONS:
            try:
                exported_data = {
                    "id": username,
                    method_name: getattr(methods, method_name)(
                        user_id, settings.VK_TOKEN, settings.V, args.verbose
                    ),
                }
                filename = os.path.join(
                    export_path, f"{filename_prefix}{user_id}{settings.FILE_TYPE}"
                )
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
        traceback.print_exc()
    finally:
        if export_path and os.path.isdir(export_path):
            shutil.rmtree(export_path)


if os.path.isdir(settings.default_path):
    print(f"Default folder exists. Cleaning {settings.default_path}\\")
    clean_folder(settings.default_path)
else:
    print(f"Default folder does not exist. Creating {settings.default_path}\\")
    os.mkdir(settings.default_path)


while True:
    try:
        bot.polling()
    except Exception:
        traceback.print_exc()
        time.sleep(1)
