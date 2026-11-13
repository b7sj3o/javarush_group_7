from celery.result import AsyncResult
from fastapi import FastAPI, BackgroundTasks, Query
from pydantic import BaseModel

from celery_app import celery_app
from mailer import send_email
from tasks import send_email_task


app = FastAPI()

class EmailData(BaseModel):
    to: str
    subject: str
    body: str


# ============ SYNC ============ 

@app.post("/emails/sync")
def send_sync(data: EmailData):
    send_email(data.to, data.subject, data.body)
    return {"status": "sent"}


# ============ BACKGROUND TASKS ============ 

@app.post("/emails/background", status_code=202)
def send_background(data: EmailData, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, data.to, data.subject, data.body)
    return {"status": "pending"}


# ============ CELERY ============ 

@app.post("/emails", status_code=202)
def send_celery(data: EmailData):
    result: AsyncResult = send_email_task.delay( data.to, data.subject, data.body)
    
    return {
        "task_id": result.id,
        "status": "pending"
    }
    
    
@app.post("/emails/bulk", status_code=202)
def send_bulk(count: int = Query(default=100, ge=1, le=1000)):
    task_ids = [send_email_task.delay(f"user{i}@example.com", "Розпродаж!", "Знижки до 50%").id for i in range(1, count + 1)]
    return {"queued": len(task_ids), "first_task_id": task_ids[0]}
    
    
@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }