import os
import re
import time
import shutil
import telebot
import methods
import requests
import settings
import traceback
from telebot import util
from datetime import datetime

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, parse_mode=None)


def clean_folder(folder):
    # Remove files or folders inside of data\
    for content in os.listdir(folder):
        content_path = os.path.join(settings.default_path, content)
        if os.path.isfile(content_path):
            os.remove(content_path)
        else:
            shutil.rmtree(content_path)


def find_at(msg):
    for text in msg:
        if text in text:
            return text


def get_country_str(country):
    time.sleep(settings.API_TIMER)
    return requests.post("https://api.vk.com/method/database.getCountriesById",
                                data={"country_ids": str(country),
                                      "access_token": settings.VK_TOKEN,
                                      "v": settings.V}).json()['response'][0]


def get_city_str(city):
    time.sleep(settings.API_TIMER)
    return requests.get("https://api.vk.com/method/database.getCitiesById",
                            data={"city_ids": str(city),
                                  "access_token": settings.VK_TOKEN,
                                  "v": settings.V}).json()['response'][0]


def creating_files(filename, data):
    with open(filename, mode="w", encoding="utf-8") as file:
        file.write(str(data))
    doc = open(filename, 'rb')
    doc.close()


@bot.message_handler(commands=['start'])
def regular_message(message):
    bot.send_message(message.chat.id, "<b>🤖 Welcome to bot!</b>\n"
                                      "\nBot allows export public data from any VK user page\n"
                                      "\n🔎 To start, send user ID or nickname to start.\n"
                                      '\nAllowed types:'
                                      '\n   Nickname: <b>durov</b>'
                                      '\n   Origin ID: <b>id1</b>'
                                      '\n   Numeric ID: <b>1</b>', parse_mode="HTML")


@bot.message_handler(func=lambda msg: msg.text is not None)
def get_info(message):
    global path

    def create_file(filename):
        with open(filename, mode="w", encoding="utf-8") as file:
            file.write(str(data))
        with open(filename, 'rb') as doc:
            bot.send_document(message.from_user.id, doc)

    try:
        got_text = message.text.split()
        at_text = find_at(got_text).lower()
        if len(re.findall(r'com/(.*)', at_text)) > 0:
            at_text = re.findall(r'com/(.*)', at_text)[0]
        userid = methods.get_numeric_id(at_text, settings.VK_TOKEN, settings.V)
        start_time = int(time.time())
        request = methods.users_get(userid, settings.VK_TOKEN, settings.V)[0]

        data = {}

        if 'id' in request:
            data["ID"] = request['id']

        if 'first_name' and 'last_name' in request:
            data["Name"] = f"{request['first_name']} {request['last_name']}"
        else:
            if 'first_name' in request and len(request['first_name']) > 0:
                data["First name"] = request['first_name']

            if 'last_name' in request and len(request['last_name']) > 0:
                data["Last name"] = request['last_name']

        if 'nickname' in request and len(request['nickname']) > 0:
            data["Middle name"] = request['nickname']

        if 'maiden_name' in request and len(request['maiden_name']) > 0:
            data["Maiden name"] = request['maiden_name']

        if 'sex' in request and len(request['last_name']) > 0:
            if request['sex'] == 1:
                data["Sex"] = 'Female'
            elif request['sex'] == 2:
                data["Sex"] = 'Male'

        if 'bdate' in request:
            data["Birthday"] = request['bdate']

        if 'site' in request and len(request['site']) > 0:
            data["Site"] = request["site"]

        platform_map = {
            1: "m.vk.com",
            2: "iPhone",
            3: "iPad",
            4: "Android",
            5: "Windows Phone",
            6: "Windows 8",
            7: "vk.com"}

        if 'last_seen' in request and "deactivated" not in request:
            last_seen = request["last_seen"]
            data["Last seen"] = datetime.utcfromtimestamp(last_seen.get("time")).strftime('%Y-%m-%d %H:%M:%S')
            platform_id = last_seen.get("platform")
            if platform_id in platform_map:
                data["Platform"] = platform_map[platform_id]
        elif "deactivated" in request:
            pass
        else:
            data["Last seen"] = "Hidden by vk.me/app"

        if 'status' in request and len(request["status"]) > 0:
            data["Status"] = request["status"]

        if 'mobile_phone' in request and len(request["mobile_phone"]) > 0:
            data["Mobile"] = request["mobile_phone"]

        if 'home_phone' in request and len(request["home_phone"]) > 0:
            data["Home phone"] = request["home_phone"]

        socials = [("skype", "@"),
                   ("instagram", "instagram.com/"),
                   ("twitter", "twitter.com/"),
                   ("livejournal", "@"),
                   ("facebook", "facebook.com/")]

        for social in socials:
            if social[0] in request:
                data[f"{social[0].capitalize()}"] = f"{social[1]}{request[social[0]]}"

        if 'crop_photo' not in request:
            data["Avatar"] = request["photo_max_orig"]
        else:
            if 'photo' in request["crop_photo"]:
                full_size = max(request["crop_photo"]["photo"]['sizes'], key=lambda line: int(line['width']))
                data["Avatar"] = full_size['url']
            if 'date' in request["crop_photo"]["photo"]:
                data["Avatar date"] = datetime.utcfromtimestamp(
                    request["crop_photo"]["photo"]["date"]).strftime('%Y-%m-%d %H:%M:%S')

        def serialize(data):
            rslt = []
            for key, value in data.items():
                rslt += f"<b>— {key}</b>: {value}" + "\n"
            return ''.join(rslt)

        result = serialize(data)

        for i in settings.TO_REMOVE:
            result = result.replace(i, '')

        for text in util.split_string(result, 4096):
            start_parse_msg = f"<b>[{start_time}] Started parsing for vk.com/id{userid}</b>\n{text}"
            bot.send_message(message.from_user.id, start_parse_msg, parse_mode="HTML")
        path = f"{settings.default_path}/export{userid}_{int(time.time())}"
        print(path)
        os.mkdir(path)

        # Define the methods and their corresponding filenames
        methods_array = (
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
            ("market_get", "market")
        )

        for method, filename_prefix in methods_array:
            try:
                data = {"id": at_text, "parsing_started": int(time.time()),
                        method: getattr(methods, method)(userid, settings.VK_TOKEN, settings.V),
                        "parsing_finished": int(time.time())}
                filename = f"{path}/{filename_prefix}{userid}{settings.FILE_TYPE}"
                create_file(filename)
            except Exception as e:
                error_message = f"error while parsing {method} section: {e}"
                bot.send_message(message.from_user.id, error_message, parse_mode="HTML")

        end_time = int(time.time())
        eng_parse_msg = f"<b>[{end_time}] End parsing of vk.com/id{userid}. Elapsed {end_time - start_time} seconds</b>"
        bot.send_message(message.from_user.id, eng_parse_msg, parse_mode="HTML")
    except Exception as e:
        exception_msg = "<b>Looks like you entered negative or zero id. Enter the right ID or nickname.</b>"
        bot.send_message(message.from_user.id, f"<b> {exception_msg} \n {e}</b>", parse_mode="HTML")
        traceback.print_exc()
    finally:
        print(path)
        shutil.rmtree(path)


if os.path.exists(settings.default_path) and os.path.isdir(settings.default_path):
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
