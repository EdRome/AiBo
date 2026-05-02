import os
import logging
import uuid
import json
from datetime import datetime, timedelta
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from typing import Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

project = 'gen-lang-client-0680947061'
queue = 'whatsapp-consumption-reminder'
location = 'us-central1'
base_url = os.environ.get('CLOUD_TASK_BASE_URL', '')
url = base_url + '/consume_message'
url_summary = base_url + '/sales_summary'
url_remainder = base_url + '/remainder'
service_account = "aibo-sql@gen-lang-client-0680947061.iam.gserviceaccount.com"

client = tasks_v2.CloudTasksClient()
parent = client.queue_path(project, location, queue)

def list_scheduled_tasks():
    client = tasks_v2.CloudTasksClient()
    
    # El 'parent' es la ruta de la cola (queue)
    parent = f"projects/{project}/locations/{location}/queues/{queue}"
    
    # Listar las tareas
    tasks = client.list_tasks(request={"parent": parent})
    
    return [(task.name.split("/")[-1].split("-")[-1], task.http_request.url) for task in tasks]

def delete_inactivity_task(task_id: Optional[str] = None, phone_number: Optional[str] = None, task_name: Optional[str] = None):
    if task_name is None:
        task_name = f"projects/{project}/locations/{location}/queues/{queue}/tasks/{task_id}-{phone_number}"
    else:
        task_name = f"projects/{project}/locations/{location}/queues/{queue}/tasks/{task_name}"

    try:
        client.delete_task(name=task_name)
    except Exception as e:
        logger.error(f"Error al eliminar la tarea de inactividad: {e}")

def schedule_remainder_task(phone_number: str, fecha_recordatorio: datetime, message: str):
    tz_cdmx = ZoneInfo("America/Mexico_City")
    current_date = datetime.now(tz_cdmx)

    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(fecha_recordatorio)
    
    payload = {'sender': phone_number, 'message': message}

    task_id = f"{uuid.uuid4()}-recordatorio-{phone_number}"
    task_name = f"projects/{project}/locations/{location}/queues/{queue}/tasks/{task_id}"
    task = {
        'name': task_name,
        'http_request': {
            'http_method': tasks_v2.HttpMethod.POST,
            'url': url_remainder,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(payload).encode(),
            'oidc_token': {
                'service_account_email': service_account,
                'audience': url_remainder
            }
        },
        'schedule_time': timestamp
    }

    response = client.create_task(request={'parent': parent, 'task': task})
    return task_id


def schedule_sales_summary_task(phone_number: str):
    tasks = list_scheduled_tasks()
    for task in tasks:
        if task[0] == phone_number and task[1] == url_summary:
            logger.error(f"Ya existe una tarea de resumen de ventas para el numero {phone_number}")
            return

    tz_cdmx = ZoneInfo("America/Mexico_City")
    current_date = datetime.now(tz_cdmx)
    scheduled_date = current_date.replace(hour=22, minute=5, second=0, microsecond=0)
    if current_date >= scheduled_date:
        scheduled_date += timedelta(days=1)

    payload = {'sender': phone_number}

    task_id = f"{uuid.uuid4()}-{phone_number}"
    task_name = f"projects/{project}/locations/{location}/queues/{queue}/tasks/{task_id}"
    task = {
        'name': task_name,
        'http_request': {
            'http_method': tasks_v2.HttpMethod.POST,
            'url': url_summary,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(payload).encode(),
            'oidc_token': {
                'service_account_email': service_account,
                'audience': url_summary
            }
        },
        'schedule_time': scheduled_date
    }

    try:
        delete_inactivity_task(task_id, phone_number)
    except Exception as e:
        logger.error(f"Error al crear la tarea de inactividad: {e}")

    response = client.create_task(request={'parent': parent, 'task': task})
    return task_id

def schedule_inactivity_task(phone_number: str):
    delay_seconds = os.environ.get("DELAY_SECONDS", 10)
    delay_seconds = int(delay_seconds)
    d = datetime.now() + timedelta(seconds=delay_seconds)
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(d)

    payload = {'sender': phone_number}

    task_id = f"{uuid.uuid4()}-{phone_number}"
    task_name = f"projects/{project}/locations/{location}/queues/{queue}/tasks/{task_id}"
    task = {
        'name': task_name,
        'http_request': {
            'http_method': tasks_v2.HttpMethod.POST,
            'url': url,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(payload).encode(),
            'oidc_token': {
                'service_account_email': service_account,
                'audience': url
            }
        },
        'schedule_time': timestamp
    }

    try:
        delete_inactivity_task(task_id, phone_number)
    except Exception as e:
        logger.error(f"Error al crear la tarea de inactividad: {e}")

    response = client.create_task(request={'parent': parent, 'task': task})
    return task_id