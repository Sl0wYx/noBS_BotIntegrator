from datetime import datetime
import os
from dotenv import load_dotenv
import telebot
import requests

load_dotenv("src/private")

API_TOKEN = os.environ.get('API_TOKEN')
TOKEN = os.environ.get('BOT_TOKEN')
MY_ID = os.environ.get('MY_ID')

API_URL = "https://api.noboons.world/receive_message"

bot = telebot.TeleBot(TOKEN)

def is_me(message):
    return message.from_user.id == MY_ID

@bot.message_handler(func=is_me,commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Hello! Your id: {message.from_user.id}")

@bot.channel_post_handler(content_types=['text', 'photo'])
def get_messsage(message):
    entries = []
    channel_message = ""

    if message.content_type == 'text':
        message_text = message.text
        if message_text.lower().endswith('#оголошення'):
            markdown_message = styles(message.entities, entries, message_text, channel_message)
            date = datetime.fromtimestamp(message.date)

            headers = {"Authorization": f"{API_TOKEN}"}
            data = {"Message": markdown_message, "Date": f"{date}"}
            requests.post(API_URL, json=data, headers=headers)
    elif message.content_type == 'photo':
        message_text = message.caption
        if message_text.lower().endswith('#оголошення'):
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
            date = datetime.fromtimestamp(message.date)


            markdown_message = markdown_convert(message.caption_entities, entries, message_text, channel_message)

            headers = {"Authorization": f"{API_TOKEN}"}
            data = {"Message": markdown_message, "File Url": file_url, "Date": f"{date}"}
            requests.post(API_URL, json=data, headers=headers)

# Telegram json to Markdown convertion, please don't judge
def markdown_convert(needed_entities, entries, message_text, channel_message):
    if needed_entities:
        for entity in needed_entities:
            entry_start = [entity.offset, entity.type + "_start"]
            entry_end = [entity.length + entity.offset, entity.type + "_end"]

            entries.append(entry_start)
            entries.append(entry_end)
    else:
        channel_message = message_text

    last_index = 0
    for entry in range(len(entries)):

        index = entries[entry][0]
        style = entries[entry][1]

        if style == "bold_start":
            channel_message += message_text[last_index:index] + "**"
        elif style == "italic_start":
            channel_message += message_text[last_index:index] + "*"
        elif style == "underline_start":
            channel_message += message_text[last_index:index] + "<u>"
        elif style == "url_start":
            channel_message += message_text[last_index:index] + "[url]("
        elif style == "bold_end":
            channel_message += message_text[last_index:index] + "**"
        elif style == "italic_end":
            channel_message += message_text[last_index:index] + "*"
        elif style == "underline_end":
            channel_message += message_text[last_index:index] + "</u>"
        elif style == "url_end":
            channel_message += message_text[last_index:index] + ")"
        else:
            channel_message += message_text[last_index:index]

        last_index = index

    channel_message += message_text[last_index:len(message_text)]

    return channel_message


print("Bot is running...")
bot.infinity_polling()