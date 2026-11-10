from contextlib import asynccontextmanager

from fastapi import FastAPI
from faststream.rabbit import RabbitBroker, RabbitQueue

from pydantic import BaseModel


class OrderCreated(BaseModel):
    order_id: int
    user_id: int
    total: float


broker = RabbitBroker(
    "amqp://guest:guest@localhost:5672/"
)

queue = RabbitQueue("orders", durable=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with broker:
        await broker.start()
        await broker.declare_queue(queue)
        yield


app = FastAPI(lifespan=lifespan)


@app.post("/orders", status_code=202)
async def create_order(order: OrderCreated):
    await broker.publish(
        order,
        queue=queue,
        persist=True,
    )

    return {"status": "queued"}