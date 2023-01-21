import json
import os
from pprint import pprint

import aiohttp
from fastapi import FastAPI, Request

from datadog import publish_emoji_metric

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
DATADOG_METRICS = "https://api.datadoghq.com/api/v2/series"
SLACK_BASE_URL = 'https://slack.com/api'
SLACK_USER_INFO = f'{SLACK_BASE_URL}/users.profile.get'
SLACK_CHANNEL_INFO = f'{SLACK_BASE_URL}/conversations.info'

app = FastAPI()

async def get_user_from_id(user_id: str):
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(SLACK_USER_INFO, headers=headers, params={"user": user_id}) as resp:
            if resp.status == 200:
                resp_json = await resp.json()
                print(resp_json)
                return resp_json["profile"]["display_name"]
            else:
                return "user_fetch_error"

async def get_channel_from_id(channel_id: str):
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(SLACK_CHANNEL_INFO, headers=headers, params={"channel": channel_id}) as resp:
            if resp.status == 200:
                resp_json = await resp.json()
                return resp_json["channel"]["name"]
            else:
                return "channel_fetch_error"

@app.post("/")
async def root(request: Request):
    body = await request.body()
    if not body:
        return {}
    body_parsed = json.loads(body)
    if body_parsed["type"] == "url_verification":
        return body_parsed["challenge"]
    else:
        if "event" in body_parsed:
            print(body_parsed)
            event = body_parsed["event"]
            if event["type"] == "reaction_added":
                user_id = event['item_user']
                emoji = event["reaction"].split(":")[0]
                # TODO: do something with skins tones? ^
                channel_id = event["item"]["channel"]
                user_name = await get_user_from_id(user_id)
                channel_name = await get_channel_from_id(channel_id)
                print(f"{user_name} reacted with {emoji} in #{channel_name}")
                publish_emoji_metric(user=user_name, emoji=emoji, channel=channel_name)


