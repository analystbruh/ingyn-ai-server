import os
from fastapi import FastAPI, Request
import httpx
from src.funcs.gcloud_task import create_http_tasks


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


async def send_workout(number, message=None):
    if not message:
        message = "ok then so DO 60,000,000 BILLION PUSH UPS RIGHT NOW OR SYBAU YOU FAT MFR!!!"
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


@app.get("/", status_code=200)
def home():
    return "HOME"


@app.post("/send-scheduled-workout")
async def send_scheduled_workout(data: Request):
    message = await data.json()
    # hard code links to five day workout in json
    res = await send_text(message.get("number"), "do some situps, like 10.")
    return res


@app.get("/webhook")
def webhook_get(hub: Request):
    print("trying...")
    data = hub.query_params
    print("challenge!:", data.get("hub.challenge"))
    return int(data.get("hub.challenge"))


@app.post("/webhook")
async def webhook_post(data: Request):
    payload = await data.json()
    data = payload.get("entry", {})
    if data:
        changes = data[0].get("changes", [])
        messages = []
        body = ""
        number = ""
        if changes:
            messages = changes[0].get("value", {}).get("messages", [])
        if messages:
            body = messages[0].get("text", {}).get("body")
        if body:
            number = messages[0].get("from")
        if number:
            if "WORKOUT" in body.upper():
                message = "Great! What day do you want start? (reply with date in '4/18/2024' format)"
                res = await send_text(number, message)
                return res
            try:
                start_date = await create_http_tasks(body, number)
                message = (
                    f"Your workouts have been scheduled! See ya on {start_date}!!!"
                )
                res = await send_text(number, message)
            except ValueError:
                message = "Please send starting date in format like '4/18/2024' format"
                res = await send_text(number, message)
        return "processed"
