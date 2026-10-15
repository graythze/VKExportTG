# VKExportTG

<h1 align="center">
  VKExportTG 📄

  [RUS](#о-проекте) // [ENG](#about)
![image](https://user-images.githubusercontent.com/54765502/133928495-f5f8f111-2cb4-4b7b-96b6-f9f2bde090b2.png)

</h1>

<h1 align="center">
  <a href="#rus"><b>RUS</b></a>
</h1>

---

### О проекте

**VKExportTG** — Telegram-бот для выгрузки доступных данных публичного профиля VK в JSON. Отправьте боту числовой ID, короткое имя или ссылку на профиль — бот поставит задачу в очередь, покажет сведения о профиле и пришлёт результаты отдельными файлами.

Доступность и состав данных определяются токеном VK и настройками приватности страницы. Используйте проект только для данных, на обработку которых у вас есть право.

### Что экспортируется

Каждый раздел отправляется отдельным JSON-файлом:

- профиль (`users.get`);
- записи на стене (`wall.get`);
- документы (`docs.get`);
- фотографии (`photos.getAll`);
- заметки (`notes.get`);
- видео (`video.get`);
- друзья (`friends.get`);
- подарки (`gifts.get`);
- истории (`stories.get`);
- группы и публичные страницы (`groups.get`);
- товары (`market.get`);
- подписчики (`users.getFollowers`).

Большие списки разбиваются на части по 5 000 записей. Ошибка в одном разделе не останавливает экспорт остальных.

### Требования

- Python 3.12+ или Docker;
- Telegram Bot API token;
- VK API access token.

### Установка и запуск

1. Клонируйте репозиторий и перейдите в его каталог.
2. Создайте виртуальное окружение (необязательно, но рекомендуется):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Установите зависимости:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Создайте файл `.env` на основе примера:

   ```bash
   cp .env.example .env
   ```

5. Заполните `.env`:

   ```dotenv
   TELEGRAM_TOKEN=токен_бота_из_BotFather
   VK_TOKEN=ваш_токен_VK
   ALLOWED_USER_IDS=0
   VK_API_VER=5.82
   ```

6. Запустите бота:

   ```bash
   python bot.py
   ```

Для подробных логов используйте `python bot.py --verbose`. Справка по аргументам: `python bot.py --help`.

### Настройки

| Переменная | Назначение | Значение по умолчанию |
| --- | --- | --- |
| `TELEGRAM_TOKEN` | Токен Telegram-бота | обязательна |
| `VK_TOKEN` | Токен доступа VK API | обязательна |
| `ALLOWED_USER_IDS` | Telegram ID пользователей через запятую; `0` разрешает доступ всем | `0` |
| `VK_API_VER` | Версия VK API | `5.82` |

Команда `/myid` показывает ваш Telegram ID. Команды `/start`, `/menu` и `/help` открывают меню. Бот также понимает `id1`, `1`, `durov` и ссылки формата `https://vk.ru/durov` или `https://vk.com/durov`.

### Запуск в Docker

Соберите образ:

```bash
docker build -t vk-export-tg .
```

Запустите контейнер, передав настройки из `.env`:

```bash
docker run --env-file .env --name vk-export-tg --restart unless-stopped vk-export-tg
```

В проекте также есть `docker-compose.yaml` для сборки и управления сервисом. Перед запуском через Compose убедитесь, что переменные `TELEGRAM_TOKEN` и `VK_TOKEN` передаются в контейнер через настройки окружения сервиса.

<h1 align="center">
  <a href="#eng"><b>ENG</b></a>
</h1>

---
### About

**VKExportTG** is a Telegram bot that exports available data from a public VK profile as JSON. Send the bot a numeric ID, screen name, or profile URL; it queues the task, displays a profile summary, and sends each export section as a separate file.

The available data depends on the VK token and the profile privacy settings. Use the project only for data you are authorized to process.

### Exported data

Each section is sent as a separate JSON file:

- profile (`users.get`);
- wall posts (`wall.get`);
- documents (`docs.get`);
- photos (`photos.getAll`);
- notes (`notes.get`);
- videos (`video.get`);
- friends (`friends.get`);
- gifts (`gifts.get`);
- stories (`stories.get`);
- groups and public pages (`groups.get`);
- market items (`market.get`);
- followers (`users.getFollowers`).

Large lists are split into files of 5,000 items. An error in one section does not stop the remaining export.

### Requirements

- Python 3.12+ or Docker;
- a Telegram Bot API token;
- a VK API access token.

### Install and run

1. Clone the repository and open its directory.

3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create `.env` from the example:

   ```bash
   cp .env.example .env
   ```

5. Fill in `.env`:

   ```dotenv
   TELEGRAM_TOKEN=your_BotFather_token
   VK_TOKEN=your_VK_token
   ALLOWED_USER_IDS=0
   VK_API_VER=5.82
   ```

6. Start the bot:

   ```bash
   python bot.py
   ```

Use `python bot.py --verbose` for detailed logs. Run `python bot.py --help` for command-line help.

### Configuration

| Variable | Description | Default |
| --- | --- | --- |
| `TELEGRAM_TOKEN` | Telegram bot token | required |
| `VK_TOKEN` | VK API access token | required |
| `ALLOWED_USER_IDS` | Comma-separated Telegram user IDs; `0` allows everyone | `0` |
| `VK_API_VER` | VK API version | `5.82` |

Use `/myid` to display your Telegram ID. `/start`, `/menu`, and `/help` open the menu. The bot accepts `id1`, `1`, `durov`, and profile URLs such as `https://vk.ru/durov` or `https://vk.com/durov`.

### Docker

Build the image:

```bash
docker build -t vk-export-tg .
```

Run the container with the variables from `.env`:

```bash
docker run --env-file .env --name vk-export-tg --restart unless-stopped vk-export-tg
```

The repository also includes `docker-compose.yaml` for building and managing the service. Before running it with Compose, make sure `TELEGRAM_TOKEN` and `VK_TOKEN` are passed into the service container through its environment configuration.

