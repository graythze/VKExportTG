from dotenv import load_dotenv
import os


def user_parser():
    users = os.getenv("ALLOWED_USER_IDS", 0).split(",")
    user_list = []

    for user in users:
        user_list.append(int(user))

    return user_list

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
VK_TOKEN = os.environ["VK_TOKEN"]


VK_API_VERSION = os.getenv("VK_API_VER", "5.82")
ALLOWED_USER_IDS = user_parser()

TO_REMOVE = (
    "https://",
    "http://",
    "&ava=1",
    "www.",
    "?ava=1"
)

API_TIMER = 0.34