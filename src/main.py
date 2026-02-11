import os
from fastapi import FastAPI, Request
import httpx
from src.funcs.gcloud_task import create_http_tasks
import json
from datetime import datetime
import asyncio


PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID")
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")

app = FastAPI()


async def send_text(number, message):
    async with httpx.AsyncClient() as client:
        url = f"https://graph.facebook.com/v24.0/{PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": "true",
                "body": message,
            },
        }
        timeout_config = httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=None)
        response = await client.post(
            url, headers=headers, json=data, timeout=timeout_config
        )
        print("RESPOND:", response.status_code)
        return "done"

async def send_media(number, media_type, media_url, caption):
    print('sending:', media_url)
    async with httpx.AsyncClient() as client:
        url = f"https://graph.facebook.com/v24.0/{PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": media_type,
            media_type: {
                "link": media_url,
                "caption": caption
            },
        }
        print(data)
        timeout_config = httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=None)
        response = await client.post(
            url, headers=headers, json=data, timeout=timeout_config
        )
        print("RESPOND:", response.status_code)
        return "done"


@app.get("/")
def home():
    return "HOME"


@app.post("/send-scheduled-workout")
async def send_scheduled_workout(data: Request):
    message = await data.json()
    print("MESSAGE:", message)
    exercises = message.get('exercises')
    number = message.get('number')
    for exercise in exercises:
        media_type = exercise.get('type')
        media_url = exercise.get('media_url')
        caption = exercise.get('caption', '')
        if media_type == "text":
            text = exercise.get('text')
            res = await send_text(number, text)
        else:
            res = await send_media(number, media_type, media_url, caption)
        print(res)
        await asyncio.sleep(3)
    return "done"


@app.get("/webhook")
def webhook_get(hub: Request):
    print("trying...")
    data = hub.query_params
    print("challenge!:", data.get("hub.challenge"))
    return int(data.get("hub.challenge"))


@app.post("/webhook")
async def webhook_post(data: Request):
    payload = await data.json()
    print(json.dumps(payload, indent=2))
    data = payload.get("entry", {})
    if data:
        changes = data[0].get("changes", [])
        messages = []
        body = ""
        number = ""
        timestamp = 0
        if changes:
            messages = changes[0].get("value", {}).get("messages", [])
        if messages:
            body = messages[0].get("text", {}).get("body")
            timestamp = messages[0].get("timestamp")
            if timestamp:
                timediff = datetime.now() - datetime.fromtimestamp(int(timestamp))
                print('MESSAGE AGE:', timediff.seconds, "SECONDS")
                if timediff.seconds > 2 * 60:
                    # 5 minutes
                    return "old message"
        if body:
            number = messages[0].get("from")
        if number:
            if "WORKOUT ROUTINE" in body.upper():
                message = "Great! What day do you want start? (reply with date in '4/18/2024' format)"
                res = await send_text(number, message)
                return res
            if "DONE" in body.upper():
                message = "Outstanding!"
                res = await send_text(number, message)
                return res
            try:
                start_date = await create_http_tasks(body, number)
                message = (
                    f"Your workouts have been scheduled! See ya on {start_date}!!!"
                )
                res = await send_text(number, message)
                return res
            except ValueError:
                message = "Please send starting date in format like '4/18/2024'"
                res = await send_text(number, message)
                return res
            except Exception as e:
                print("ERROR:", e)
                return "failed"
        print('DONE')
        return "processed"
