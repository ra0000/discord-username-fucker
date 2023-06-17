import requests
import time
import signal
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import string
import itertools
from words import WORDS
import sys
import os.path
import shutil

if not os.path.exists("credentials.py"):
    if os.path.exists("sample_credentials.py"):
        shutil.copy("sample_credentials.py", "credentials.py")

    print("ERR: Set credentials.py")
    sys.exit(1)

from credentials import ACCOUNTS
from telegram import broadcast



# digit 2: 00 ~ 99
# digit 3: 000 ~ 999
# ...
def generate_number_username(digit=2):
    for i in range(10**digit - 1):
        yield str(i).zfill(digit)


# combination of lowercase alphabet, numbers 0 ~ 9, dot and underscore
# digit 2: aa ~ __
# digit 3: aaa ~ ___
# ...
def generate_lowercase_and_number_and_dot_and_underscore_username(digit=2):
    allowed_username = string.ascii_lowercase + string.digits + "._"

    for i in itertools.product(allowed_username, repeat=digit):
        username = "".join(i)

        if ".." in username:
            continue
        yield username


available_usernames = []
lock = Lock()


def fetch(value):
    index = value[0]
    username = value[1]
    account = ACCOUNTS[index % len(ACCOUNTS)]

    print(f"[{index}]: try {username}")

    while True:
        r = requests.patch(
            url="https://discord.com/api/v9/users/@me",
            json={"username": username, "password": account["password"]},
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Authorization": account["token"],
            },
        )
        print(r.json())

        if "rate limited" in r.text:
            time.sleep(0.5)
            continue

        if "captcha" in r.text or "Unknown Session" in r.text:
            print(f"{username} ok")
            broadcast(str(username))

            global available_usernames
            with lock:
                available_usernames.append(username)

        time.sleep(2.12)
        break


executor = ThreadPoolExecutor(max_workers=len(ACCOUNTS))


def fetch_thread(fetch_iterator, offset=0):
    for _ in range(offset):
        next(fetch_iterator)

    with executor:
        executor.map(fetch, fetch_iterator)


if __name__ == "__main__":
    def exit_print_available_usernames():
        executor.shutdown(wait=False, cancel_futures=True)
        print(f"Shutting down...\navailable_usernames: {available_usernames}")
        broadcast(str(available_usernames))
        sys.exit(0)

    signal.signal(signal.SIGINT, lambda *_: exit_print_available_usernames())

    # fetch_thread(enumerate(WORDS)) # fetch words dictionary
    #fetch_thread(enumerate(generate_number_username(4)))
    fetch_thread(
        enumerate(generate_lowercase_and_number_and_dot_and_underscore_username(3)) 
    )

    exit_print_available_usernames()