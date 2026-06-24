"""
Run this ONCE on your own computer (not in CI, not on a shared machine) to
generate a Telethon session string for the forwarder.

    pip install telethon
    python generate_session.py

It will ask for your api_id, api_hash, phone number, and the login code
Telegram sends you, then print a long session string.

Treat that string exactly like a password: anyone who has it can log into
your Telegram account without your phone. Never commit it to a file, never
paste it anywhere other than the GitHub secret field (TG_SESSION).
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(input("api_id: ").strip())
api_hash = input("api_hash: ").strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\nLogin successful. Your session string (copy everything between the lines):\n")
    print("-" * 60)
    print(client.session.save())
    print("-" * 60)
    print("\nStore this as the TG_SESSION secret in GitHub. Do not share it.")
