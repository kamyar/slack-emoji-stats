import json
import logging
import os
import sys
from pprint import pprint

import aiohttp
from fastapi import FastAPI, Request
from mangum import Mangum
from pythonjsonlogger import jsonlogger

from src.datadog import publish_emoji_metric

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
DATADOG_METRICS = "https://api.datadoghq.com/api/v2/series"
SLACK_BASE_URL = "https://slack.com/api"
SLACK_USER_INFO = f"{SLACK_BASE_URL}/users.profile.get"
SLACK_CHANNEL_INFO = f"{SLACK_BASE_URL}/conversations.info"

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)


app = FastAPI()


async def get_user_from_id(user_id: str):
    headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            SLACK_USER_INFO, headers=headers, params={"user": user_id}
        ) as resp:
            if resp.status == 200:
                resp_json = await resp.json()
                print(resp_json)
                return resp_json["profile"]["display_name"]
            else:
                return "user_fetch_error"


async def get_channel_from_id(channel_id: str):
    headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            SLACK_CHANNEL_INFO, headers=headers, params={"channel": channel_id}
        ) as resp:
            if resp.status == 200:
                resp_json = await resp.json()
                # pprint(resp_json)
                if "channel" in resp_json:
                    channel_name = resp_json["channel"]["name"]
                    is_private = resp_json["channel"]["is_private"]
                    is_instant_message = False
                else:
                    channel_name = None
                    is_private = None
                    is_instant_message = True
                return channel_name, is_private, is_instant_message
            else:
                return "channel_fetch_error"


@app.post("/")
async def handle(request: Request):
    body = await request.body()
    if not body:
        return {}
    body_parsed = json.loads(body)
    if body_parsed["type"] == "url_verification":
        return body_parsed["challenge"]
    else:
        if "event" in body_parsed:
            event = body_parsed["event"]
            if event["type"] == "reaction_added":
                user_id = event["user"]
                emoji = event["reaction"].split(":")[0]
                # TODO: do something with skins tones? ^
                channel_id = event["item"]["channel"]
                user_name = await get_user_from_id(user_id)
                channel_name, is_private, is_im = await get_channel_from_id(channel_id)
                if is_private:
                    channel_name = None
                logging.info(f"{user_name} reacted with {emoji} in #{channel_name}")
                logging.info(event)
                publish_emoji_metric(
                    user=user_name,
                    emoji=emoji,
                    channel=channel_name,
                    is_private=is_private,
                    is_im=is_im,
                    is_channel=(not is_im),
                )


@app.get("/")
async def root():
    return {"message": "Hello World"}


handler = Mangum(app, lifespan="off")
