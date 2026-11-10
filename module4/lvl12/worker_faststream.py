import asyncio

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from pydantic import BaseModel


class OrderCreated(BaseModel):
    order_id: int
    user_id: int
    total: float


broker = RabbitBroker(
    "amqp://guest:guest@localhost:5672/"
)

app = FastStream(broker)


@broker.subscriber(
    RabbitQueue("orders", durable=True)
)
async def process_order(order: OrderCreated):
    print(f"Processing order #{order.order_id}")

    await asyncio.sleep(5)

    print(f"Order #{order.order_id} completed!")