<h1 align="center">
  VKExportTG 📄

  [RUS](#-что-это) // [ENG](#-what-is-it)
</h1>

<h1 align="center">
  <a href="#rus"><b>RUS</b></a>
</h1>

# 📄 Что это?

VKExportTG позволяет экспортировать данные в файл JSON с личной страницы ВК или другого человека через Telegram бота
![image](https://user-images.githubusercontent.com/54765502/133928495-f5f8f111-2cb4-4b7b-96b6-f9f2bde090b2.png)


## ✅ Экспорт доступен для
* Данных профиля <kbd>[users.get](https://vk.com/dev/users.get)</kbd>
* Документов <kbd>[docs.get](https://vk.com/dev/docs.get)</kbd>
* Друзей <kbd>[friends.get](https://vk.com/dev/friends.get)</kbd>
* Подарков <kbd>[gifts.get](https://vk.com/dev/gifts.get)</kbd>
* Заметок <kbd>[notes.get](https://vk.com/dev/notes.get)</kbd>
* Фотографий <kbd>[photos.get](https://vk.com/dev/photos.get)</kbd>
* Историй <kbd>[stories.get](https://vk.com/dev/stories.get)</kbd>
* Видео <kbd>[video.get](https://vk.com/dev/video.get)</kbd>
* Подписчиков <kbd>[users.getFollowers](https://vk.com/dev/users.getFollowers)</kbd>
* Групп и публичных страниц <kbd>[groups.get](https://vk.com/dev/groups.get)</kbd>
* Маркета <kbd>[market.get](https://vk.com/dev/market.get)</kbd>
* Постов на стене <kbd>[wall.get](https://vk.com/dev/wall.get)</kbd>

## ⚙️ Использование
1) Скачайте скрипт
2) Установите пакеты, используя команду `pip install -r requirements.txt`
3) Установите `TELEGRAM_TOKEN` и `VK_TOKEN` в файле <kbd>settings.py</kbd>
4) Запустите бота, используя команду `python bot.py`

Команда `python bot.py -h` показана ниже

```
usage: bot.py [-h] [-v]

Usage: python bot.py

options:
  -h, --help     show this help message and exit
  -v, --verbose  Increase output verbosity
```


### 📍 Аргументы
`-v, --verbose` — показать подробности


## 🔌 Получение API токена
### VK токен
1) Откройте [vkhost.github.io](https://vkhost.github.io/)
2) Выберите приложение. Лучше всего использовать приложения Kate Mobile или VFeed 
3) Нажмите на выбранное приложение
4) Нажмите на  "Продолжить как" или "Разрешить"
5) Скопируйте часть URL начиная с `access_token= ` и заканчивая `&expires_in`
6) Вставьте токен в скрипт

Также можно использовать другие приложения или службы для получения VK токена
### Telegram токен
1) Откройте Telegram бота [@BotFarther](https://telegram.me/BotFather), он поможет в создании и будущем управлении ботом.
2) Чтобы создать нового бота, введите `/newbot`. Следуйте инструкции.
3) После создания бота в сообщении будет распологаться API токен, сгенерированный для бота

### ***Вы можете разместить собственного бота на [Heroku](https://heroku.com/). Это [руководство](https://devcenter.heroku.com/articles/getting-started-with-python) поможет развернуть приложение Python за считанные минуты.***
<h1 align="center">
  <a href="#eng"><b>ENG</b></a>
</h1>

## 📄 What is it?
VKExportTG allows you to export data to a JSON file from a personal VK page or another page via a Telegram bot
![image](https://user-images.githubusercontent.com/54765502/133928495-f5f8f111-2cb4-4b7b-96b6-f9f2bde090b2.png)

## Export available for
* Profile data <kbd>[users.get](https://vk.com/dev/users.get)</kbd>
* Documents <kbd>[docs.get](https://vk.com/dev/docs.get)</kbd>
* Friends <kbd>[friends.get](https://vk.com/dev/friends.get)</kbd>
* Gifts <kbd>[gifts.get](https://vk.com/dev/gifts.get)</kbd>
* Notes <kbd>[notes.get](https://vk.com/dev/notes.get)</kbd>
* Photos <kbd>[photos.get](https://vk.com/dev/photos.get)</kbd>
* Stories <kbd>[stories.get](https://vk.com/dev/stories.get)</kbd>
* Videos <kbd>[video.get](https://vk.com/dev/video.get)</kbd>
* Followers <kbd>[users.getFollowers](https://vk.com/dev/users.getFollowers)</kbd>
* Groups, public pages <kbd>[groups.get](https://vk.com/dev/groups.get)</kbd>
* Market items <kbd>[market.get](https://vk.com/dev/market.get)</kbd>
* Wall posts <kbd>[wall.get](https://vk.com/dev/wall.get)</kbd>

## ⚙️ Usage
1) Download script
2) Install packages using `pip install -r requirements.txt`
3) Set Telegram token in `TELEGRAM_TOKEN`, VK token in `VK_TOKEN` and VK API version in `V`.
3) Run script using `python bot.py`

The command `python collector.py -h` is shown below
```
usage: bot.py [-h] [-v]

Usage: python bot.py

options:
  -h, --help     show this help message and exit
  -v, --verbose  Increase output verbosity
```


### 📍 Arguments
`-v, --verbose` - Increase output verbosity


## 🔌 Getting VK API token
1) Visit [vkhost.github.io](https://vkhost.github.io/)
2) Choose app. It's better to use token from Kate Mobile or VFeed apps 
3) Click on app 
4) Click on "Continue as" or "Allow"
5) Copy part of URL from `access_token= `to `&expires_in`
6) Paste token to CLI

You can use other apps or services to get VK token.
### Telegram token
1) In Telegram, go to bot named [@BotFarther](https://telegram.me/BotFather) to create and manage your bot.
2) To create a new bot type `/newbot` or click on it from menu.
3) After creating Telegram bot. You will see in message a new API token generated for bot.


### ***You can host own bot on [Heroku](https://heroku.com/). This [tutorial](https://devcenter.heroku.com/articles/getting-started-with-python) will have you deploying a Python app in minutes.***


