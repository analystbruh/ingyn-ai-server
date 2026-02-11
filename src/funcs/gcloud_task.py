import datetime
import json
from typing import Dict, Optional
from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2
import asyncio
import os
import uuid

PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID")
LOCATION_ID = os.environ.get("GOOGLE_LOCATION_ID")
QUEUE = os.environ.get("GOOGLE_QUEUE")
TARGET = os.environ.get("TARGET_URL")


async def create_http_task(
    project: str,
    location: str,
    queue: str,
    url: str,
    json_payload: Dict,
    scheduled_seconds_from_now: Optional[int] = None,
    task_id: Optional[str] = None,
    deadline_in_seconds: Optional[int] = None,
) -> tasks_v2.Task:
    """Create an HTTP POST task with a JSON payload.
    Args:
        project: The project ID where the queue is located.
        location: The location where the queue is located.
        queue: The ID of the queue to add the task to.
        url: The target URL of the task.
        json_payload: The JSON payload to send.
        scheduled_seconds_from_now: Seconds from now to schedule the task for.
        task_id: ID to use for the newly created task.
        deadline_in_seconds: The deadline in seconds for task.
    Returns:
        The newly created task.
    """

    # Create a client.
    client = tasks_v2.CloudTasksAsyncClient()

    # Construct the task.
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=url,
            headers={"Content-type": "application/json"},
            body=json.dumps(json_payload).encode(),
        ),
        name=(
            client.task_path(project, location, queue, task_id)
            if task_id is not None
            else None
        ),
    )

    # Convert "seconds from now" to an absolute Protobuf Timestamp
    if scheduled_seconds_from_now is not None:
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(
            datetime.datetime.utcnow()
            + datetime.timedelta(seconds=scheduled_seconds_from_now)
        )
        task.schedule_time = timestamp

    # Convert "deadline in seconds" to a Protobuf Duration
    if deadline_in_seconds is not None:
        duration = duration_pb2.Duration()
        duration.FromSeconds(deadline_in_seconds)
        task.dispatch_deadline = duration

    # Use the client to send a CreateTaskRequest.
    res = await client.create_task(
        tasks_v2.CreateTaskRequest(
            # The queue to add the task to
            parent=client.queue_path(project, location, queue),
            # The task itself
            task=task,
        )
    )
    print("TASK CREATED: ", task_id)
    return res

workouts = {
    "day_1": [
        {
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/motivation/motivation720.mp4"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/Air%20Squats%20or%20Goblet%20Squats.mp4",
            "caption": "Squats - 4x10"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/Bench%20Press.mp4",
            "caption": "Bench Press - 4x10"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/Dumbbell%20Rows.mp4",
            "caption": "Dumbbell Rows - 3x12"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/45%20sec%20planks.mp4",
            "caption": "Plank - 3x45 sec"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/25%20toe%20touches.mp4",
            "caption": "Toe Touches 3x20"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/10%20min%20incline%20walk%20or%20bike.mp4",
            "caption": "This one is optional."
        },{
            "type": "image",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/meal_plans/mealplan.png"
        },{
            "type": "text",
            "text": "Reply DONE when complete!"
        },
    ],
    "day_2": [
        {
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_2/MOTIVATION/ff4f755d-18ab-4421-b599-a4fa9f6dc657.mp4"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_2/WORKOUTS/walking%20lunges.mp4",
            "caption": "Walking Lunges - 3x12/leg"
        },{
            "type": "image",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_2/MEAL%20PLAN/ChatGPT%20Image%20Dec%2031%2C%202025%20at%2003_07_39%20PM.png"
        },{
            "type": "text",
            "text": "Reply DONE when complete!"
        },
    ],
    "day_3": [
        {
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_3/MOTIVATION/e4d4686a-b488-4a73-b755-077e50a2a1a2.mp4"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_3/WORKOUTS/hf_20260206_011821_5355935d-2f37-4576-bc04-48050f51cee3.mp4",
            "caption": "Kettlebell Swings 3x20"
        },{
            "type": "image",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_3/MEAL%20PLAN/ChatGPT%20Image%20Jan%203%2C%202026%20at%2011_56_11%20AM.png"
        },{
            "type": "text",
            "text": "Reply DONE when complete!"
        },
    ],
    "day_4": [
        {
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_4/MOTIVATION/hf_20260206_211547_8f724274-a981-4b74-9b86-f91029978f0b.mp4"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_4/WORKOUTS/hf_20260206_205733_62e94173-09f3-48f3-9d9b-2822103e8f03.mp4",
            "caption": "Incline Dumbbell Press - 3x10"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_4/WORKOUTS/hf_20260206_210733_31828d8c-3c2d-4d86-ab0a-fcd15ddc47e6.mp4",
            "caption": "This one is optional."
        },{
            "type": "image",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_4/MEAL%20PLAN/ChatGPT%20Image%20Feb%206%2C%202026%20at%2004_05_19%20PM.png"
        },{
            "type": "text",
            "text": "Reply DONE when complete!"
        },
    ],
    "day_5": [
        {
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_5/MOTIVATION/hf_20260206_211017_e0c85db6-b93e-44cb-961a-d46e3ad9589a.mp4"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_5/WORKOUTS/hf_20260206_211300_c11cb602-1387-4ce0-ba2a-a009677305ac.mp4",
            "caption": "Barbell Squats - 4x8"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_5/WORKOUTS/hf_20260206_220304_ca37cbf1-97ab-424e-8f08-ca12a236221c.mp4",
            "caption": "HIIT Bike or Sprints - 10-15 min"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/Dumbbell%20Rows.mp4",
            "caption": "Dumbbell Rows - 3x12"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/45%20sec%20planks.mp4",
            "caption": "Plank - 3x45 sec"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/25%20toe%20touches.mp4",
            "caption": "Toe Touches 3x20"
        },{
            "type": "video",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_1/workouts/10%20min%20incline%20walk%20or%20bike.mp4",
            "caption": "This one is optional."
        },{
            "type": "image",
            "media_url": "https://storage.googleapis.com/ingyn-workouts/day_5/MEAL%20PLAN/ChatGPT%20Image%20Feb%206%2C%202026%20at%2004_15_09%20PM.png"
        },{
            "type": "text",
            "text": "Congratulations on reaching the final day!!!"
        },
    ],
}

async def create_http_tasks(start_date, number):
    date_format = "%m/%d/%Y"
    start_date_obj = datetime.datetime.strptime(start_date, date_format)
    start_datetime = start_date_obj + datetime.timedelta(hours=13)
    json_payload = { "number": number }
    job_marker = uuid.uuid4()
    for i in range(5):
        jp = {
            "exercises": workouts[f"day_{i+1}"],
            **json_payload
        }
        print("JSON PAYLOAD:", jp)
        # seconds_from_now_start = int(
        #     (start_datetime - datetime.datetime.now()).total_seconds()
        # )
        await create_http_task(
            project=PROJECT_ID,
            location=LOCATION_ID,
            queue=QUEUE,
            url=TARGET,
            json_payload=jp,
            scheduled_seconds_from_now=i*60*5,#seconds_from_now_start + i * 24 * 60 * 60,
            task_id=f"workout-{job_marker}-{20 * (i + 1)}",
        )
    return start_datetime.strftime(date_format)


if __name__ == "__main__":
    project_id = "hallowed-byte-429019-g1"
    location_id = "us-central1"
    queue = "workouts-queue"
    target_uri = (
        "https://reginia-aerographic-nonflakily.ngrok-free.dev/send-scheduled-workout"
    )
    json_payload = {"number": "14049428693"}
    scheduled_seconds_from_now = 60
    for i in range(5):
        t = asyncio.run(
            create_http_task(
                project=project_id,
                location=location_id,
                queue=queue,
                url=target_uri,
                json_payload=json_payload,
                scheduled_seconds_from_now=scheduled_seconds_from_now * (i + 1),
                task_id=f"workout-{i + 1}",
            )
        )
        print(t)
