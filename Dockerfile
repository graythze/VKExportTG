FROM python:3.12-slim

WORKDIR /VKExportTGBot

COPY . .

RUN python -m pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
