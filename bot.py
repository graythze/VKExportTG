# TODO Attractive messages
# TODO Remove folder after fail

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
    shutil.rmtree(folder)


def find_at(msg):
    for text in msg:
        if text in text:
            return text


def get_country_str(country):
    time.sleep(0.35)
    country_str = requests.post("https://api.vk.com/method/database.getCountriesById",
                                data={"country_ids": str(country),
                                      "access_token": settings.VK_TOKEN,
                                      "v": settings.V}).json()['response'][0]
    return country_str


def get_city_str(city):
    time.sleep(0.35)
    city_str = requests.get("https://api.vk.com/method/database.getCitiesById",
                            data={"city_ids": str(city),
                                  "access_token": settings.VK_TOKEN,
                                  "v": settings.V}).json()['response'][0]
    return city_str


def creating_files(filename, data):
    with open(filename, mode="w", encoding="utf-8") as file:
        file.write(str(data))
    doc = open(filename, 'rb')
    doc.close()


@bot.message_handler(commands=['start'])
def regular_message(message):
    bot.send_message(message.chat.id, "<b>Welcome to bot! 🤖</b>\n"
                                      "\nPlease send the page user ID 🔎"
                                      '\n(eg. "<b>durov</b>" or "<b>id1</b>")', parse_mode="HTML")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "This bot allows you to export public data any page from settings.VK.\n"
                                      "To start, send a text message with ID\n"
                                      '\n(eg. "<b>durov</b>" or "<b>id1</b>")', parse_mode="HTML")


@bot.message_handler(func=lambda msg: msg.text is not None)
def get_info(message):
    global path

    def filemessage(filename):
        with open(filename, mode="w", encoding="utf-8") as file:
            file.write(str(data))
        doc = open(filename, 'rb')
        bot.send_document(message.from_user.id, doc)
        doc.close()

    try:
        got_text = message.text.split()
        at_text = find_at(got_text).lower()
        if len(re.findall(r'com/(.*)', at_text)) > 0:
            at_text = re.findall(r'com/(.*)', at_text)[0]
        userid = methods.get_numeric_id(at_text, settings.VK_TOKEN, settings.V)

        if int(userid) == 0:
            bot.send_message(message.from_user.id, "<b> Looks like you entered ZERO id. Enter the right ID or nickname. </b>",
                             parse_mode="HTML")
        else:
            start_time = int(time.time())
            request = methods.users_get(userid, settings.VK_TOKEN, settings.V)[0]

            data = {}

            if 'id' in request:
                data["<b>— ID</b>"] = request['id']

            if 'first_name' in request and 'last_name' in request:
                data["<b>— Name</b>"] = request['first_name'] + ' ' + request['last_name']
            else:
                if 'first_name' in request:
                    if len(request['first_name']) > 0:
                        data["<b>— First name</b>"] = request['first_name']

                if 'last_name' in request:
                    if len(request['last_name']) > 0:
                        data["<b>— Last name</b>"] = request['last_name']

            if 'nickname' in request:
                if len(request['nickname']) > 0:
                    data["<b>— Middle name</b>"] = request['nickname']

            if 'maiden_name' in request:
                if len(request['maiden_name']) > 0:
                    data["<b>— Maiden name</b>"] = request['maiden_name']

            if 'sex' in request:
                if len(request['last_name']) > 0:
                    if request['sex'] == 1:
                        data["<b>— Sex</b>"] = 'Female'
                    elif request['sex'] == 2:
                        data["<b>— Sex</b>"] = 'Male'

            if 'bdate' in request:
                data["<b>— Birthday</b>"] = request['bdate']

            if 'site' in request:
                if len(request['site']) > 0:
                    data["<b>— Site</b>"] = request["site"]

            if 'last_seen' in request:
                if 'time' in request["last_seen"]:
                    data["<b>— Last seen</b>"] = datetime.utcfromtimestamp(request["last_seen"]["time"]).strftime(
                        '%Y-%m-%d %H:%M:%S')
                if 'platform' in request["last_seen"]:
                    if request["last_seen"]["platform"] == 1:
                        data["<b>— Platform</b>"] = "m.vk.com"
                    if request["last_seen"]["platform"] == 2:
                        data["<b>— Platform</b>"] = "iPhone"
                    if request["last_seen"]["platform"] == 3:
                        data["<b>— Platform</b>"] = "iPad"
                    if request["last_seen"]["platform"] == 4:
                        data["<b>— Platform</b>"] = "Android"
                    if request["last_seen"]["platform"] == 5:
                        data["<b>— Platform</b>"] = "Windows Phone"
                    if request["last_seen"]["platform"] == 6:
                        data["<b>— Platform</b>"] = "Windows 8"
                    if request["last_seen"]["platform"] == 7:
                        data["<b>— Platform</b>"] = "vk.com"
            else:
                if "deactivated" in request:
                    pass
                else:
                    data["<b>— Last seen</b>"] = "Hidden by vk.me/app"

            if 'status' in request:
                if len(request["status"]) > 0:
                    data["<b>— Status</b>"] = request["status"]

            if 'mobile_phone' in request:
                if len(request["mobile_phone"]) > 0:
                    data["<b>— Mobile</b>"] = request["mobile_phone"]

            if 'home_phone' in request:
                if len(request["home_phone"]) > 0:
                    data["<b>— Home phone</b>"] = request["home_phone"]

            if 'skype' in request:
                data["<b>— Skype</b>"] = request["skype"]

            if 'instagram' in request:
                data["<b>— Instagram</b>"] = "@" + request["instagram"]

            if 'twitter' in request:
                data["<b>— Twitter</b>"] = "@" + request["twitter"]

            if 'livejournal' in request:
                data["<b>— LiveJournal</b>"] = "@" + request["livejournal"]

            if 'facebook' in request:
                data["<b>— Facebook</b>"] = "fb.com/" + request["facebook"]

            if 'crop_photo' not in request:
                data["<b>— Avatar</b>"] = request["photo_max_orig"]
            else:
                if 'crop_photo' in request:
                    if 'photo' in request["crop_photo"]:
                        full_size_ava = max(request["crop_photo"]["photo"]['sizes'],
                                            key=lambda line: int(line['width']))
                        data["<b>— Avatar</b>"] = full_size_ava['url']
                    if 'date' in request["crop_photo"]["photo"]:
                        data["<b>— Avatar date</b>"] = datetime.utcfromtimestamp(
                            request["crop_photo"]["photo"]["date"]).strftime('%Y-%m-%d %H:%M:%S')

            def serialize(dct, tabs=0):
                rslt = []
                pref = ' ' * tabs
                for k, v in dct.items():
                    if isinstance(v, dict):
                        rslt += [pref + str(k) + ':']
                        rslt += [serialize(v, tabs + 2)]
                    elif isinstance(v, list):
                        rslt += [pref + str(k) + ': ']
                        for x in range(len(v)):
                            rslt += [' ' * 2 + v[x]]
                    else:
                        rslt += [pref + str(k) + ': ' + str(v)]
                return '\n'.join(rslt)

            result = serialize(data)

            for i in settings.TO_REMOVE:
                result = result.replace(i, '')

            print(request)

            for text in util.split_string(result, 4096):
                bot.send_message(message.from_user.id, "<b>[" + str(start_time) + "] " +
                                 "Started parsing for vk.com/id" + str(userid) + "</b>\n" + text, parse_mode="HTML")

            path = "export" + str(at_text) + "_" + str(time.time())
            os.mkdir(path)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "main_profile": methods.users_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/profile" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "wall": methods.wall_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/wall" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "documents": methods.docs_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/documents" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "photos": methods.photos_get_all(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/photos" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "notes": methods.notes_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/notes" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "videos": methods.videos_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/videos" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "friends": methods.friends_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/friends" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "gifts": methods.gifts_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/gifts" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "stories": methods.stories_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/stories" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "groups": methods.groups_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/groups" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            data = {"id": at_text, "parsing_started": int(time.time()),
                    "market": methods.market_get(userid, settings.VK_TOKEN, settings.V),
                    "parsing_finished": int(time.time())}
            filename = path + "/market" + str(userid) + "_" + str(time.time()) + settings.FILE_TYPE
            filemessage(filename)

            end_time = int(time.time())
            bot.send_message(message.from_user.id, "<b>[" + str(time.time()) + "] " +
                             "Ended parsing for vk.com/id" + str(userid) + "</b>" + "\n<b>It took " +
                             str(end_time - start_time) + " seconds</b>", parse_mode="HTML")

            clean_folder(path)
    except:
        bot.send_message(message.from_user.id, "<b> Something gone wrong :-(</b>", parse_mode="HTML")
        traceback.print_exc()
        clean_folder(path)


while True:
    try:
        bot.polling()
    except:
        traceback.print_exc()
        time.sleep(5)
