# Telegram Channel Forwarder (100% free, runs on GitHub Actions)

Forwards every new post from `t.me/Magazine_bank` to your private group
"My Selected Downloads". No server, no VPS, no paid bot platform — it runs
entirely on GitHub's free Actions runners on a cron schedule.

## Why a "userbot" instead of a bot

A normal Telegram bot (from @BotFather) can only see a channel's posts if
the channel's *owner* adds it as an admin. You're a subscriber of
`Magazine_bank`, not an admin, so that path is closed. This script instead
logs in as **your own Telegram account** (via the Telethon library) — the
same access you already have when you read the channel in the app — and
forwards new posts from there. No one else's permission is required.

## How it works

`forwarder.py` connects to Telegram using a saved login session, finds
messages newer than the last one it forwarded, and sends them to your
destination group. A GitHub Actions workflow runs this every 5 minutes and
commits the small `state.json` file back to the repo so nothing is missed or
sent twice between runs.

## 1. Get your API credentials

1. Go to https://my.telegram.org/apps and log in (phone number + the code
   Telegram sends you).
2. You already have an app there named **upsc_agent** — you can reuse it, or
   create a new one. Either way, note its `api_id` and `api_hash`.

## 2. Generate a session string (do this on your own computer)

This is the one step that has to happen on a machine you control, since it
requires you to enter the Telegram login code yourself:

```
pip install telethon
python generate_session.py
```

It will ask for your `api_id`, `api_hash`, phone number, and login code, then
print a long session string. **Treat it like a password** — copy it
somewhere safe; you'll paste it into a GitHub secret in step 4 and then
should delete your local copy.

## 3. Set up the repo

1. Create a new **public** GitHub repository (public = unlimited free
   Actions minutes; private repos only get a limited free quota/month).
2. Upload these files to the repo root:
   - `forwarder.py`
   - `requirements.txt`
   - `state.json`
   - `.github_workflows_forward.yml` → **rename/move this to
     `.github/workflows/forward.yml`** (GitHub Actions only reads workflows
     from that exact path).
   - `generate_session.py` is only needed locally — you can skip uploading
     it, or include it for reference (it contains no secrets itself).

## 4. Add repo secrets

Settings → Secrets and variables → Actions → New repository secret:

| Secret name | Value |
|---|---|
| `TG_API_ID` | your api_id, e.g. `31513851` |
| `TG_API_HASH` | your api_hash |
| `TG_SESSION` | the session string from step 2 |
| `SOURCE_CHAT_ID` | `Magazine_bank` |
| `DEST_CHAT_ID` | `-4801992377` (the "My Selected Downloads" group id) |

## 5. Run it

Go to the **Actions** tab, enable workflows if prompted, and click
**Run workflow** to trigger it immediately — or just wait, since it runs
every 5 minutes automatically from then on.

## Notes

- ~5 minute delay per run, not instant — this is a polling design since
  GitHub Actions can't run a permanently-listening process for free.
- Public repos get unlimited free standard-runner minutes; this workflow
  uses well under a minute per run, so cost is $0.
- GitHub auto-disables scheduled workflows after 60 days with no repository
  activity, but this workflow commits `state.json` on every run, so it keeps
  itself alive indefinitely as long as it runs at least once every 60 days.
- If `Magazine_bank` (or any source) has "restrict saving content" turned on
  by its owner, Telegram blocks forwarding for everyone, including this
  script — there's no way around that from outside the channel.
- The bot created earlier via @BotFather (`Srikanthbalagoni10bot`) isn't
  used by this design and can be ignored or deleted via @BotFather's
  `/deletebot` if you don't want it lying around.
