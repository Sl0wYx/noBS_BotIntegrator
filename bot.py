import os
import threading

from collections import defaultdict
from datetime import datetime
from threading import Timer

from dotenv import load_dotenv

import telebot
import requests
import urllib.request
from core import utils

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')
TOKEN = os.environ.get('BOT_TOKEN')
MY_ID = os.environ.get('MY_ID')

API_URL = "https://api.noboobs.world/receive_message"

bot = telebot.TeleBot(TOKEN)

def is_me(message):
    return message.from_user.id == MY_ID

@bot.message_handler(func=is_me,commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Hello! Your id: {message.from_user.id}")

def return_multiple_photos():
    global media_group
    media_group["state"] = "PROCESSING"

    headers = {"authorization": f"{API_TOKEN}"}
    data = media_group["data"]
    message_date = media_group["message_date"]

    for i, file_url in enumerate(media_group["photos"]):
        date_str = str(message_date).replace(" ", "_").replace(":", "-") + f"_{i}"
        try:
            urllib.request.urlretrieve(file_url, f"src/{date_str}.png")
            utils.upload_file(f"src/{date_str}.png", f"/history/{date_str}.png")
        except NotADirectoryError:
            print("Not a directory!")

        # try:
        # requests.post(API_URL, json=data, headers=headers)
        # except requests.exceptions.RequestException as e:
        # print(e)

    print(data)
    media_group = {
        "state": "EMPTY", # WAITING = waiting for the photo to arrive;
                        # RECORDING = recording new photo;
                        # PROCESSING = processing recorded media
                        # EMPTY = no group has been received
        'message_date': "",
        "photos": [],
        "data": defaultdict(int)
    }

t_lock = threading.Lock()
media_group = {
    "state": "EMPTY",  # WAITING = waiting for the photo to arrive;
    # RECORDING = recording new photo;
    # PROCESSING = processing recorded media,
    # EMPTY = no group has been received
    'message_date': "",
    "photos": [],
    "data": defaultdict(int) | defaultdict(str)
}
t = threading.Timer(100, return_multiple_photos)
@bot.channel_post_handler(content_types=['text', 'photo'])
def get_messsage(message):
    global media_group, t
    entries = []
    channel_message = ""

    if message.content_type == 'text':
        message_text = message.text
        if message_text.lower().endswith('#оголошення'):
            markdown_message = utils.markdown_convert(message.entities, entries, message_text, channel_message)
            date = datetime.fromtimestamp(message.date)

            headers = {"authorization": f"{API_TOKEN}"}
            data = {"message": markdown_message, "date": f"{date}"}

            try:
                requests.post(API_URL, json=data, headers=headers)
            except requests.exceptions.RequestException as e:
                print(e)
    elif message.content_type == 'photo':
        message_text = message.caption

        if not message.media_group_id and message_text and message_text.lower().endswith('#оголошення'):
            message_date = datetime.fromtimestamp(message.date)
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

            date_str = str(message_date).replace(" ", "_").replace(":", "-")

            try:
                urllib.request.urlretrieve(file_url, f"src/{date_str}.png")
                utils.upload_file(f"src/{date_str}.png", f"/history/{date_str}.png")
            except NotADirectoryError:
                print("Not a directory!")

            markdown_message = utils.markdown_convert(message.caption_entities, entries, message_text, channel_message)

            headers = {"authorization": f"{API_TOKEN}"}
            data = {"message": markdown_message, "date": f"{message_date}", "images": 1}

            #try:
                # requests.post(API_URL, json=data, headers=headers)
            #except requests.exceptions.RequestException as e:
                #print(e)
        elif message.media_group_id:

            media_group["state"] = "RECORDING"
            if t.is_alive():
                t.cancel()

            message_date = datetime.fromtimestamp(message.date)
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

            if message_text:
                markdown_message = utils.markdown_convert(message.caption_entities, entries, message_text, channel_message)

                media_group["message_date"] = message_date
                media_group["data"] = {"message": markdown_message, "date": f"{message_date}"}

            media_group["photos"].append(file_url)
            media_group["data"]["images"] += 1

            with t_lock:
                if media_group["state"] == "RECORDING":
                    t = Timer(0.01, return_multiple_photos)
                    t.start()
                    media_group["state"] = "WAITING"



print("Bot is running...")
bot.infinity_polling()