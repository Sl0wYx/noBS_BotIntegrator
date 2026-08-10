import os
import subprocess
from dotenv import load_dotenv

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