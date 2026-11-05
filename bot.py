import argparse
import html
import io
import json
import logging
import re
import threading
import time
import traceback
from pathlib import Path
from collections import deque
from datetime import datetime

import i18n
import telebot
from telebot import types, util

import methods
import config


i18n.set("file_format", "json")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("skip_locale_root_data", True)
i18n.set("available_locales", ["ru", "en"])
i18n.set("locale", config.LANG)
i18n.set("fallback", "ru")
i18n.load_path.append(str(Path(__file__).resolve().parent / "locales"))


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(description="Usage: python bot.py")
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
args = parser.parse_args()

bot = telebot.TeleBot(config.TELEGRAM_TOKEN, parse_mode=None)
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
        types.KeyboardButton(i18n.t("button_export")),
        types.KeyboardButton(i18n.t("button_examples")),
        types.KeyboardButton(i18n.t("button_features"))
    )
    return keyboard


def menu_markup() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(i18n.t("button_export"), callback_data="menu:export"),
        types.InlineKeyboardButton(i18n.t("button_features"), callback_data="menu:features"),
        types.InlineKeyboardButton(i18n.t("button_examples"), callback_data="menu:examples"),
    )
    return keyboard


def send_menu(chat_id, text=None) -> None:
    text = text or (
        i18n.t("welcome")
    )
    bot.send_message(
        chat_id, text, parse_mode="HTML", reply_markup=main_keyboard()
    )
    bot.send_message(
        chat_id,
        i18n.t("menu_prompt"),
        parse_mode="HTML",
        reply_markup=menu_markup(),
    )


def features_text() -> str:
    return i18n.t("features")


def examples_text() -> str:
    return i18n.t("examples")


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
        result[i18n.t("field_id")] = profile["id"]
    if profile.get("first_name") and profile.get("last_name"):
        result[i18n.t("field_name")] = f"{profile['first_name']} {profile['last_name']}"
    else:
        if profile.get("first_name"):
            result[i18n.t("field_first_name")] = profile["first_name"]
        if profile.get("last_name"):
            result[i18n.t("field_last_name")] = profile["last_name"]

    optional_fields = {
        "nickname": i18n.t("field_middle_name"),
        "maiden_name": i18n.t("field_maiden_name"),
        "bdate": i18n.t("field_birthday"),
        "site": i18n.t("field_site"),
        "status": i18n.t("field_status"),
        "mobile_phone": i18n.t("field_mobile"),
        "home_phone": i18n.t("field_home_phone"),
    }
    for field, label in optional_fields.items():
        if profile.get(field):
            result[label] = profile[field]

    if profile.get("sex") == 1:
        result[i18n.t("field_sex")] = i18n.t("female")
    elif profile.get("sex") == 2:
        result[i18n.t("field_sex")] = i18n.t("male")

    if "last_seen" in profile and "deactivated" not in profile:
        last_seen = profile["last_seen"]
        result[i18n.t("field_last_seen")] = datetime.fromtimestamp(last_seen["time"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        if last_seen.get("platform") in PLATFORM_NAMES:
            result[i18n.t("field_platform")] = PLATFORM_NAMES[last_seen["platform"]]
    else:
        result[i18n.t("field_last_seen")] = i18n.t("hidden_last_seen")

    for name, prefix in SOCIAL_PREFIXES.items():
        if profile.get(name):
            result[name.capitalize()] = f"{prefix}{profile[name]}"

    crop_photo = profile.get("crop_photo", {}).get("photo", {})
    sizes = crop_photo.get("sizes", [])
    if sizes:
        result[i18n.t("field_avatar")] = max(sizes, key=lambda size: int(size["width"]))["url"]
    elif profile.get("photo_max_orig"):
        result[i18n.t("field_avatar")] = profile["photo_max_orig"]
    if crop_photo.get("date"):
        result[i18n.t("field_avatar_date")] = datetime.fromtimestamp(crop_photo["date"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return result


def profile_message(profile_data) -> str:
    rows = []
    for key, value in profile_data.items():
        value = str(value)
        for text_to_remove in config.TO_REMOVE:
            value = value.replace(text_to_remove, "")
        rows.append(f"<b>— {key}</b>: {html.escape(value)}")
    return "\n".join(rows)


def is_authorized(user_id) -> bool:
    """Zero (0) allows anyone to interact with bot."""
    if 0 in config.ALLOWED_USER_IDS:
        return True
    else:
        if user_id in config.ALLOWED_USER_IDS:
            return True
        else:
            return False


@bot.message_handler(commands=["myid"])
def my_id_message(message):
    bot.send_message(
        message.chat.id,
        i18n.t("telegram_id", user_id=message.from_user.id),
        parse_mode="HTML",
    )


@bot.message_handler(func=lambda message: not is_authorized(message.from_user.id))
def unauthorized_message(message):
    bot.send_message(
        message.chat.id,
        i18n.t("unauthorized"),
        parse_mode="HTML",
    )


@bot.callback_query_handler(func=lambda call: not is_authorized(call.from_user.id))
def unauthorized_callback(call):
    bot.answer_callback_query(
        call.id,
        i18n.t("unauthorized"),
        show_alert=True,
    )


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
            i18n.t("export_prompt"),
            parse_mode="HTML",
            reply_markup=main_keyboard(),
        )
        bot.send_message(call.message.chat.id, examples_text(), parse_mode="HTML", reply_markup=menu_markup())
    elif action == "features":
        bot.send_message(call.message.chat.id, features_text(), parse_mode="HTML", reply_markup=menu_markup())
    elif action == "examples":
        bot.send_message(call.message.chat.id, examples_text(), parse_mode="HTML", reply_markup=menu_markup())


@bot.message_handler(func=lambda message: message.text in {
    i18n.t("button_export"), i18n.t("button_examples"), i18n.t("button_features")
})
def keyboard_action(message):
    if message.text == i18n.t("button_export"):
        waiting_for_identifier.add(message.chat.id)
        bot.send_message(
            message.chat.id,
            i18n.t("export_prompt_short"),
            parse_mode="HTML",
            reply_markup=main_keyboard(),
        )
    elif message.text == i18n.t("button_features"):
        send_menu(message.chat.id, features_text())
    else:
        send_menu(message.chat.id, examples_text())


@bot.message_handler(func=lambda message: message.text is not None)
def get_info(message):
    chat_id = message.chat.id
    waiting_for_identifier.discard(chat_id)
    user_input = get_user_input(message)
    position = export_queue.enqueue(chat_id, user_input)
    bot.send_message(
        chat_id,
        i18n.t("queued", position=position),
        parse_mode="HTML",
    )


def process_export(chat_id, user_input) -> None:
    """Parse one VK page and send its export files to the requesting chat."""
    try:
        profile_match = re.search(r"^(?:https?://)?(?:www\.)?(?:vk\.(?:com|ru)|vkontakte\.(?:com|ru))/([^/?#]+)",
            user_input.strip(), re.IGNORECASE)
        username = profile_match.group(1) if profile_match else user_input
        user_id = methods.get_numeric_id(username)
        start_time = int(time.time())
        profile = methods.users_get(user_id, args.verbose)[0]

        for text in util.split_string(profile_message(format_profile(profile)), 4096):
            bot.send_message(
                chat_id,
            f"<b>{i18n.t('parsing')}</b> <code>vk.ru/id{user_id}</code>\n{text}",
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
                filename = f"{export_prefix}/{filename_prefix}{user_id}.json"
                send_export_parts(filename, exported_data, method_name, chat_id)
            except Exception as error:
                bot.send_message(
                    chat_id,
                    f"<b>{i18n.t('section_error', method=method_name)}</b> "
                    f"<code>{html.escape(str(error))}</code>",
                    parse_mode="HTML",
                )

        end_time = int(time.time())
        bot.send_message(
            chat_id,
            i18n.t("finished", user_id=user_id, seconds=end_time - start_time),
            parse_mode="HTML",
        )
    except Exception as error:
        bot.send_message(
            chat_id,
            f"<b>{i18n.t('invalid_input')}</b>\n<code>{html.escape(str(error))}</code>",
            parse_mode="HTML",
        )
        logger.exception("Failed to process VK export request")


class ExportQueue:
    """Queue for VK export"""

    def __init__(self, processor) -> None:
        self.processor = processor
        self.jobs = deque()
        self.condition = threading.Condition()
        self.is_processing = False
        self.worker = threading.Thread(target=self.run, name="vk-export-worker", daemon=True)
        self.worker.start()

    def enqueue(self, chat_id, user_input) -> int:
        """Add parse request and return position"""
        with self.condition:
            if self.is_processing:
                task_precessing = 1
            else:
                task_precessing = 0
            position = len(self.jobs) + task_precessing + 1
            self.jobs.append((chat_id, user_input))
            self.condition.notify()
            return position

    def run(self) -> None:
        while True:
            with self.condition:
                while not self.jobs:
                    self.condition.wait()
                chat_id, user_input = self.jobs.popleft()
                self.is_processing = True

            try:
                self.processor(chat_id, user_input)
            except Exception:
                logger.exception("Unexpected error in VK export queue worker")
            finally:
                with self.condition:
                    self.is_processing = False


export_queue = ExportQueue(process_export)

while True:
    try:
        bot.polling()
    except Exception:
        logger.exception("Bot polling failed")
        time.sleep(1)
