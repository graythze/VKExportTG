import logging
import time
from typing import Dict, Any
import requests
import settings

token = settings.VK_TOKEN
version = settings.V

TIME_WAIT = 1 / 3
VK_API_URL = "https://api.vk.ru/method/"

logger = logging.getLogger(__name__)


def make_request(method, data, offset_step, verbose) -> list:
    """Fetch all pages returned by a VK method."""
    request_data: Dict[str, Any] = {
        **data,
        "access_token": token,
        "v": version,
    }

    offset = 0
    all_items = []

    while True:
        request = requests.post(
            f"{VK_API_URL}{method}", data=request_data
        ).json()
        if verbose:
            logger.debug("VK response: %s", request)
        else:
            logger.info("Got %s response for offset %s", method, offset)

        items = request.get("response", {}).get("items", [])

        if not items:
            logger.info("Finished parsing %s", method)
            break

        all_items.extend(items)
        if offset_step <= 0:
            break

        offset += offset_step
        request_data["offset"] = offset
        time.sleep(TIME_WAIT)

    time.sleep(TIME_WAIT)
    return all_items


def get_numeric_id(user_id: int) -> int:
    if user_id.isnumeric():
        return user_id

    request = requests.post(f"{VK_API_URL}users.get", data={
        "user_ids": user_id,
        "access_token": token,
        "v": version,
    }).json()
    try:
        return request["response"][0]["id"]
    except (KeyError, IndexError, TypeError):
        error = request.get("error", {})
        message = error.get("error_msg", "Unable to resolve VK user")
        code = error.get("error_code", "unknown")
        raise ValueError(f"CODE {code}: {message}") from None


def docs_get(id: int, verbose: bool) -> list:
    data = {"count": 2000, "offset": 0, "owner_id": id, "return_tags": 1}
    return make_request("docs.get", data,0, verbose)


def friends_get(id: int, verbose: bool) -> list:
    data = {"user_id": id,
            "order": "name",
            "count": 5000,
            "offset": 0,
            "fields": "uid,first_name,last_name,deactivated,verified,sex,bdate,city,country,home_town,photo_max,"
                      "photo_max_orig,online,lists,can_see_all_posts,can_see_audio,can_write_private_message,timezone,"
                      "domain,has_mobile,contacts,site,education,universities,schools,status,last_seen,screen_name,"
                      "followers_count,counters,occupation,nickname,relatives,relation,personal,connections,exports,"
                      "wall_comments,activities,interests,music,movies,tv,books,games,about,quotes,can_post"}
    return make_request("friends.get", data, 5000, verbose)


def gifts_get(id: int, verbose: bool) -> list:
    data = {"user_id": id,
            "count": 1000,
            "offset": 0}
    return make_request("gifts.get", data, 1000, verbose)


def notes_get(id: int, verbose: bool) -> list:
    data = {"user_id": id,
            "offset": 0,
            "count": 100,
            "sort": 1}
    return make_request("notes.get", data, 100, verbose)


def photos_get_all(id: int, verbose: bool) -> list:
    data = {"owner_id": id,
            "extended": 1,
            "offset": 0,
            "count": 200,
            "photo_sizes": 1,
            "no_service_albums": 0}
    return make_request("photos.getAll", data, 200, verbose)


def stories_get(id: int, verbose: bool) -> list:
    data = {"owner_id": id,
            "extended": 1,}
    return make_request("stories.get", data, 0, verbose)


def users_get(id: int, verbose: bool) -> Any | None:
    request = requests.post(f"{VK_API_URL}users.get", data={
        "user_ids": id,
        "fields": "uid,first_name,last_name,deactivated,verified,sex,bdate,city,country,home_town,photo_max,"
                  "photo_max_orig,online,lists,domain,has_mobile,can_write_private_message,timezone,screen_name,"
                  "contacts,site,education,universities,schools,status,last_seen,followers_count,counters,occupation,"
                  "nickname,relatives,relation,personal,connections,exports,wall_comments,activities,interests,music,"
                  "movies,tv,books,games,about,quotes,can_post,can_see_all_posts,can_see_audio",
        "access_token": token,
        "v": version}).json()
    logger.debug("VK users.get response: %s", request)

    if "response" in request:
        time.sleep(TIME_WAIT)
        return request["response"]


def videos_get(id: int, verbose: bool) -> list:
    data = {"owner_id": id,
            "count": 200,
            "offset": 0,
            "extended": 1}
    return make_request("video.get", data, 200, verbose)


def followers_get(id: int, verbose: bool) -> list:
    data = {"user_id": id,
            "offset": 0,
            "count": 1000,
            "fields": "uid,first_name,last_name,deactivated,verified,sex,bdate,city,country,home_town,last_seen,status,"
                      "photo_max,photo_max_orig,online,lists,domain,has_mobile,counters,occupation,nickname,relatives,"
                      "contacts,site,education,universities,schools,status,relation,personal,connections,exports,"
                      "followers_count,can_see_all_posts,can_see_audio,can_write_private_message,timezone,screen_name,"
                      "wall_comments,activities,interests,music,movies,tv,books,games,about,quotes,can_post"}
    return make_request("users.getFollowers", data, 1000, verbose)


def groups_get(id: int, verbose: bool) -> list:
    data = {"user_id": id,
            "extended": 1,
            "fields": "id,name,screen_name,is_closed,deactivated,is_admin,admin_level,is_member,invited_by,type,"
                      "has_photo,photo_50,photo_100,photo_200,activity,age_limits,can_create_topic,can_message,"
                      "can_post,can_see_all_posts,can_upload_doc,can_upload_video,city,contacts,counters,country,"
                      "cover,description,fixed_post,main_album_id,main_section,market,members_count,place,"
                      "public_date_label,site,status,trending,verified,wiki_page",
        "offset": 0,
        "count": 1000}
    return make_request("groups.get", data, 1000, verbose)


def wall_get(id: int, verbose: bool) -> list:
    data = {"owner_id": id,
            "offset": 0,
            "count": 100,
            "filter": "all",
            "extended": 1}
    return make_request("wall.get", data, 100, verbose)



def market_get(id: int, verbose: bool) -> list:
    data = {"owner_id": id,
            "count": 200,
            "offset": 0,
            "extended": 1}
    return make_request("market.get", data, 200, verbose)
