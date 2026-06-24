"""
Telegram channel forwarder (userbot / Telethon version).

This runs as YOUR Telegram account rather than a bot, because Bot API bots
can only read a channel's posts if they've been added as an admin by the
channel's owner. A regular account can forward from any channel/group it can
already view -- no admin rights needed.

Polls the source chat for messages newer than the last one we've seen, and
forwards each to the destination chat. Designed to be run repeatedly by a
scheduler (e.g. a GitHub Actions cron job) rather than as a long-running
process -- state (the last forwarded message id) is persisted to state.json
between runs so nothing is missed or duplicated.

Required environment variables:
    TG_API_ID       - numeric api_id from my.telegram.org/apps
    TG_API_HASH     - api_hash from my.telegram.org/apps
    TG_SESSION      - Telethon StringSession (see generate_session.py)
    SOURCE_CHAT_ID  - username (e.g. "Magazine_bank") or numeric chat id
    DEST_CHAT_ID    - username or numeric chat id (e.g. "-4801992377")

Optional:
    STATE_FILE      - path to the state file (default: state.json)
    FETCH_LIMIT     - max messages to scan per run (default: 100)
"""

import asyncio
import json
import os
import sys

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION = os.environ["TG_SESSION"]
SOURCE_CHAT_ID = os.environ["SOURCE_CHAT_ID"]
DEST_CHAT_ID = os.environ["DEST_CHAT_ID"]
STATE_FILE = os.environ.get("STATE_FILE", "state.json")
FETCH_LIMIT = int(os.environ.get("FETCH_LIMIT", "100"))


def _normalize(value: str):
    """Numeric chat ids should be ints for Telethon; usernames stay strings."""
    try:
        return int(value)
    except ValueError:
        return value.lstrip("@")


SOURCE_CHAT_ID = _normalize(SOURCE_CHAT_ID)
DEST_CHAT_ID = _normalize(DEST_CHAT_ID)


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_id": 0}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


async def main() -> None:
    state = load_state()
    last_id = state.get("last_id", 0)

    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    await client.start()

    try:
        source_entity = await client.get_entity(SOURCE_CHAT_ID)
        dest_entity = await client.get_entity(DEST_CHAT_ID)

        new_messages = []
        async for msg in client.iter_messages(
            source_entity, min_id=last_id, reverse=True, limit=FETCH_LIMIT
        ):
            new_messages.append(msg)

        forwarded = 0
        for msg in new_messages:
            try:
                await client.forward_messages(dest_entity, msg.id, source_entity)
                forwarded += 1
                last_id = max(last_id, msg.id)
                await asyncio.sleep(1)  # gentle on rate limits
            except Exception as exc:  # noqa: BLE001
                print(f"Failed to forward message {msg.id}: {exc}", file=sys.stderr)

        state["last_id"] = last_id
        save_state(state)
        print(f"Checked {len(new_messages)} new message(s), forwarded {forwarded}.")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
