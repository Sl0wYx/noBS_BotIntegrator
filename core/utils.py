import os
import subprocess

from dotenv import load_dotenv

API_URL = "https://api.noboobs.world/receive_message"

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
NEXTCLOUD_URL = "https://cloud.noboobs.world/remote.php/dav/files/{username}/"
load_dotenv(ENV_PATH)

def upload_file(file_path: str, remote_path: str):
    username = os.getenv("NEXTCLOUD_USER")
    password = os.getenv("NEXTCLOUD_PASS")

    url = NEXTCLOUD_URL.format(username=username) + remote_path.lstrip("/")

    subprocess.run(
        [
            "curl",
            "-u", f"{username}:{password}",
            "-T", file_path,
            url,
        ],
        check=True,
    )

STYLES = {"bold_start":"**", "italic_start":"_", "underline_start":"<u>",
              "bold_end":"**", "italic_end":"_", "url_start":"[url](", "url_end":")", "underline_end":"</u>"}
# Telegram json to markdown convertion
def markdown_convert(needed_entities, entries, message_text, channel_message):
    if needed_entities:
        # Generates a list of start/end points of formating
        for entity in needed_entities:
            entry_start = [entity.offset, entity.type + "_start"]
            entry_end = [entity.length + entity.offset, entity.type + "_end"]

            entries.append(entry_start)
            entries.append(entry_end)
    else:
        channel_message = message_text

    last_index = 0
    # Adds formating in given start/end points
    for entry in range(len(entries)):

        index = entries[entry][0]
        style = entries[entry][1]

        if style in STYLES:
            channel_message += message_text[last_index:index] + STYLES[style]
        else:
            channel_message += message_text[last_index:index]

        last_index = index

    channel_message += message_text[last_index:len(message_text)]

    return channel_message


