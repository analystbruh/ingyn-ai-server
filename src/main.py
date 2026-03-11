import os
from fastapi import FastAPI, Request
import httpx
from src.funcs.gcloud_task import create_http_tasks
from src.funcs.questions import questions, q1, q5, q6
import json
from datetime import datetime
import asyncio
from src.google_auth import get_access_token
from time import time


PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID")
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID")
MODEL_ID = os.environ.get("GOOGLE_MODEL_ID")
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

app = FastAPI()

async def record_to_sb(from_num, to_num, message, wamid):
    async with httpx.AsyncClient() as client:
        url = 'https://vfykuelpurgsboklpubf.supabase.co/rest/v1/message_history'
        timeout_config = httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=None)
        db_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": 'return=minimal'
        }
        db_payload = {
            "wamid": wamid,
            "from_phone_id": from_num,
            "to_phone_id": to_num,
            "message": message,
            "timestamp": int(time())
        }
        db_response = await client.post(
            url=url,
            headers=db_headers,
            json=db_payload,
            timeout=timeout_config
        )
        print("DB STATUS:", db_response.status_code, db_response.text)
        return "done"

async def record_ans_to_sb(qid, message, wamid, setid, qwamid):
    async with httpx.AsyncClient() as client:
        url = 'https://vfykuelpurgsboklpubf.supabase.co/rest/v1/qanda'
        timeout_config = httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=None)
        db_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": 'return=minimal'
        }
        db_payload = {
            "qid": qid,
            "answer": message,
            "answer_wamid": wamid,
            'setid': setid,
            'qwamid': qwamid
        }
        db_response = await client.post(
            url=url,
            headers=db_headers,
            json=db_payload,
            timeout=timeout_config
        )
        print("DB STATUS:", db_response.status_code, db_response.text)
        return "done"

async def retrieve_from_sb(number):
    async with httpx.AsyncClient() as client:
        url = f'https://vfykuelpurgsboklpubf.supabase.co/rest/v1/message_history?select=*&to_phone_id=eq.{number}&timestamp=lte.{int(time())}&order=timestamp.desc'
        timeout_config = httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=None)
        db_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f"Bearer {SUPABASE_KEY}",
            "Range": '0-0'
        }
        db_response = await client.get(
            url=url,
            headers=db_headers,
            timeout=timeout_config
        )
        print("DB STATUS:", db_response.status_code, db_response.text)
        return db_response.json()

async def retrieve_ans_from_sb(setid):
    async with httpx.AsyncClient() as client:
        url = f'https://vfykuelpurgsboklpubf.supabase.co/rest/v1/qanda?select=*&setid=eq.{setid}&order=qid'
        timeout_config = httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=None)
        db_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f"Bearer {SUPABASE_KEY}",
            "Range": '0-9'
        }
        db_response = await client.get(
            url=url,
            headers=db_headers,
            timeout=timeout_config
        )
        print("DB STATUS:", db_response.status_code, db_response.text)
        return db_response.json()

async def retrieve_setid_from_sb(qwamid):
    async with httpx.AsyncClient() as client:
        url = f'https://vfykuelpurgsboklpubf.supabase.co/rest/v1/qanda?select=*&qwamid=eq.{qwamid}&order=qid'
        timeout_config = httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=None)
        db_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f"Bearer {SUPABASE_KEY}",
            "Range": '0-0'
        }
        db_response = await client.get(
            url=url,
            headers=db_headers,
            timeout=timeout_config
        )
        print("DB STATUS:", db_response.status_code, db_response.text)
        return db_response.json()

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
        print("RESPOND:", response.status_code, response.text)
        # take response and write sent message to db
        res_data = response.json()
        wamid = res_data['messages'][0]['id']
        to_number = res_data['contacts'][0]['input']
        from_number = '14704222503'
        res = await record_to_sb(from_number, to_number, message, wamid)
        print(res)
        return wamid

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

# gemini
async def ingyn(number, prompt):
    access_token = get_access_token()
    url = f'https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/publishers/google/models/{MODEL_ID}:generateContent'
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    json_prompt = {
        "max_char_limit": 4096,
        "max_tokens": 4096,
        "format": "consise",
        "truncate": "true",
        "if_too_long": "trucate at last period",
        "prompt": prompt.get('prompt')
    }
    data = {
        'contents': {
            "role": 'user',
            "parts": { "text": json.dumps(json_prompt, indent=2)}
        }
    }
    async with httpx.AsyncClient() as client:
        timeout_config = httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=None)
        response = await client.post(url, json=data, headers=headers, timeout=timeout_config)
        res = response.json()
        answer = res['candidates'][0]['content']['parts'][0]['text']
        await send_text(number, answer)

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
        await asyncio.sleep(5)
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
    data = payload.get("entry", {})
    if data:
        changes = data[0].get("changes", [])
        messages = []
        body = ""
        user_number = ""
        waid = ""
        timestamp = 0
        # recieved messages
        if changes:
            messages = changes[0].get("value", {}).get("messages", [])
        if messages:
            timestamp = messages[0].get("timestamp")
            if timestamp:
                timediff = datetime.now() - datetime.fromtimestamp(int(timestamp))
                print('MESSAGE AGE:', timediff.seconds, "SECONDS")
                if timediff.seconds > 20:
                    # 20 seconds
                    return "old message"
            body = messages[0].get("text", {}).get("body")
            waid = messages[0].get("id")
        if body:
            user_number = messages[0].get("from")
            ingyn_number = changes[0].get("value", {}).get('metadata',{}).get('display_phone_number')
        if user_number:
            res = await process_incoming_message(user_number, ingyn_number, body, waid)
            return res
        return "processed"

async def process_incoming_message(from_num, to_num, body, wamid):
    print('process_message')
    print('FROM:', from_num, '\nBODY:', body)
    # write recieved message to db
    res = await record_to_sb(from_num, to_num, body, wamid)
    # check if message link message
    if body.strip().lower() == "go":
        res = await send_text(from_num, q1)
        return res
    # get last message sent to user
    last_message = await retrieve_from_sb(from_num)
    last_message_text = last_message[0]['message']
    # compare to script
    try:
        if last_message_text.startswith('Here’s what I’m hearing'):
            next_response = questions[q5]
        elif last_message_text == "Reply DONE when complete!" and 'done' in body.lower():
            prompt = { "prompt": "The user has replied 'DONE' in response to completing with workout challenge. Respond with a short, nice, congratulatory message."}
            asyncio.create_task(ingyn(from_num, {'prompt': prompt}))
            return 'done'
        else:
            next_response = questions[last_message[0]['message']]
    except KeyError:
        asyncio.create_task(ingyn(from_num, {'prompt': body}))
        return 'done'
    # if last message sent was q1 establish question set
    qwamid = last_message[0]['wamid']
    if last_message_text == q1:
        setid = qwamid
    else:
        res = await retrieve_setid_from_sb(qwamid)
        print('retrieve_setid_from_sb:', res)
        setid = res[0]['setid']

    # send next response
    # if previous question is the answer recall
    if next_response['nextq'] == q5:
        answers = await retrieve_ans_from_sb(setid)
        ans_list = []
        for answer in answers:
            ans_list.append(answer['answer'])
        ans_dict = {
            'ans1': ans_list[1],
            'ans2': ans_list[2],
            'ans3': body
        }
        nextq = q5.format(**ans_dict)
        print('ANSWERS:', answers)
        # next_wamid = await send_text
    else:
        nextq= next_response['nextq']
    next_wamid = await send_text(from_num, nextq)
    record_ans_status = await record_ans_to_sb(next_response['qid'], body, wamid, setid, next_wamid)
    print('record_ans_stsus:', record_ans_status)

    # if previous question is final question
    if nextq == q6:
        # schedule workouts
        start = await create_http_tasks(body, from_num)
        print(start)
        print('creating tasks...')
        print('workout scheduled!')
        return 'scheduled'
    return 'Done'