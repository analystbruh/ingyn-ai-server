import datetime
import json
from typing import Dict, Optional
from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2
import asyncio
import os
import uuid
from src.funcs.workout_plan import workouts

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


async def create_http_tasks(start_date, number):
    date_format = "%m/%d/%Y"
    start_date_obj = datetime.datetime.strptime(start_date, date_format)
    start_datetime = start_date_obj + datetime.timedelta(hours=13)
    json_payload = { "number": number }
    job_marker = uuid.uuid4()
    right_now = datetime.datetime.now()
    for i in range(6):
        jp = {
            "exercises": workouts[f"day_{i}"],
            **json_payload
        }
        print("JSON PAYLOAD:", jp)
        if i == 0:
            seconds_from_now_start = 10
        else:
            seconds_from_now_start = int(
                (start_datetime - right_now).total_seconds()
            ) + (i - 1) * 24 * 60 * 60
        await create_http_task(
            project=PROJECT_ID,
            location=LOCATION_ID,
            queue=QUEUE,
            url=TARGET,
            json_payload=jp,
            scheduled_seconds_from_now=seconds_from_now_start,
            task_id=f"workout-{job_marker}-{i}",
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
