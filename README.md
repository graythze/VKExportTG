# STANDALONE VERSION: [VKExport](https://github.com/graythze/VKExport)

# 📄 VKExport (as Telegram Bot) 

VKExportTG allows you to export data in JSON file from your or friend's VK page
![image](https://user-images.githubusercontent.com/54765502/133928495-f5f8f111-2cb4-4b7b-96b6-f9f2bde090b2.png)

## ✅ Export available for
* Main profile data
* Documents  data
* Friends data
* Gifts data
* Notes data
* Photos data
* Stories data
* Videos data
* Page followers data
* Groups data
* Market data
* Wall data


### 🔌 Making self-hosted bot

#### 🛠 Set variables in settings.py:
* `TELEGRAM_TOKEN` is token of Telegram bot. Create bot and get token: [@BotFather](https://t.me/BotFather).
* `VK_TOKEN` is VK API access token.
* `V` is VK API version (already set by default) 

#### 🤖 Host bot
Common steps:
* Leave default or set new API version in setting.py in `V` string
* To start bot running, use `python bot.py` to launch.

It depends on how and where you're going to host bot. Choose your host provider and find information how to host applications.

### ***You can host own bot on [Heroku](https://heroku.com/). This [tutorial](https://devcenter.heroku.com/articles/getting-started-with-python) will have you deploying a Python app in minutes.***
