import asyncio
from contextlib import asynccontextmanager
import json
from uuid import uuid4

import aio_pika
from fastapi import FastAPI, BackgroundTasks, HTTPException

from reports import ReportRequest


QUEUE_NAME = "reports"

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()

    await channel.declare_queue(QUEUE_NAME, durable=True)
    app.state.channel = channel
    yield
    await connection.close()
    
    
app = FastAPI(title="Звіти через RabbitMQ", lifespan=lifespan)


# async def generate_pdf():
#     await asyncio.sleep(20)
#     print("PDF generated!")


# @app.get("/report")
# async def generate_report(
#     background_tasks: BackgroundTasks
# ):
#     background_tasks.add_task(generate_pdf)
    
#     return {"ok": True}


@app.post("/reports", status_code=202) # 202 Accepted
async def create_report(data: ReportRequest):
    payload = {
        "report_id": uuid4().hex,
        "data": {**data.model_dump()}
    }

    message = aio_pika.Message(
        body=json.dumps(payload).encode(),
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )

    try:
        await app.state.channel.default_exchange.publish(
            message,
            routing_key=QUEUE_NAME,
            mandatory=True,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Cannot enqueue report",
        ) from exc

    return {
        "status": "queued",
    }