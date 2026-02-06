import json
import os

from base64 import b64encode
from pathlib import Path
from loguru import logger as log
import time



extensions = ["mp3", "wav", "ogg", "flac"]  # we will look for all those file types.


def check_file_availability(url):
    exit_status = os.system(f"wget -o --spider {url}")
    return exit_status == 0

def local_audio(path, mime="audio/mp3"):
    data = b64encode(Path(path).read_bytes()).decode()
    return [{"type": mime, "src": f"data:{mime};base64,{data}"}]


def _standardize_name(name: str) -> str:
    return name.lower().replace("_", " ").strip()
def _get_files_to_not_delete():
    not_delete = []
    if os.environ.get("PREPARE_SAMPLES"):
        for filename in ["sample_songs.json", "separate_songs.json"]:
            try:
                with open(filename) as f:
                    not_delete += list(json.load(f).keys())
            except Exception as e:
                log.warning(e)
    return not_delete
def _remove_file_older_than(file_path: str, max_age_limit: float):
    # If the file is older than the age limit, delete it
    if os.path.getmtime(file_path) < max_age_limit:
        try:
            log.info(f"Deleting {file_path}")
            os.remove(file_path)
        except OSError as e:
            log.warning(f"Error: Could not delete {file_path}. Reason: {e.strerror}")
def delete_old_files(directory: str, age_limit_seconds: int):
    files_to_not_delete = _get_files_to_not_delete()
    age_limit = time.time() - age_limit_seconds

    # Walk through the directory
    for dirpath, dirnames, filenames in os.walk(directory):
        if dirpath.split("/")[-1] not in files_to_not_delete:
            for filename in filenames:
                if filename.split(".")[0] not in files_to_not_delete:
                    file_path = os.path.join(dirpath, filename)
                    _remove_file_older_than(file_path, age_limit)
