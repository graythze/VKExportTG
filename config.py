from dotenv import dotenv_values, load_dotenv
import os


def user_parser():
    users = os.getenv("ALLOWED_USER_IDS", 0).split(",")
    user_list = []

    for user in users:
        user_list.append(int(user))

    return user_list

load_dotenv()

# Prefer LANG explicitly declared in .env over the host operating system locale.
_dotenv_lang = dotenv_values().get("LANG")
LANG = (_dotenv_lang or os.getenv("LANG") or "ru").strip().lower()
if LANG not in {"ru", "en"}:
    LANG = "ru"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
VK_TOKEN = os.environ["VK_TOKEN"]


VK_API_VERSION = os.getenv("VK_API_VER", "5.82")
ALLOWED_USER_IDS = user_parser()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    if value not in {"true", "false"}:
        raise ValueError(f"{name} must be True or False, got {value!r}")
    return value == "true"


PARSE_METHODS = {
    "users_get": env_bool("PARSE_USERS_GET"),
    "wall_get": env_bool("PARSE_WALL_GET"),
    "docs_get": env_bool("PARSE_DOCS_GET"),
    "photos_get_all": env_bool("PARSE_PHOTOS_GET_ALL"),
    "notes_get": env_bool("PARSE_NOTES_GET"),
    "videos_get": env_bool("PARSE_VIDEOS_GET"),
    "friends_get": env_bool("PARSE_FRIENDS_GET"),
    "gifts_get": env_bool("PARSE_GIFTS_GET"),
    "stories_get": env_bool("PARSE_STORIES_GET"),
    "groups_get": env_bool("PARSE_GROUPS_GET"),
    "market_get": env_bool("PARSE_MARKET_GET"),
    "followers_get": env_bool("PARSE_FOLLOWERS_GET"),
}

TO_REMOVE = (
    "https://",
    "http://",
    "&ava=1",
    "www.",
    "?ava=1"
)

API_TIMER = 0.34
