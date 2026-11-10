
import asyncio
import json
from datetime import datetime

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from reports import ReportRequest, build_report

from main import QUEUE_NAME


def log(text: str) -> None:
    print(f"{datetime.now():%H:%M:%S} {text}", flush=True)


async def handle(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=True, reject_on_redelivered=True):
        payload = json.loads(message.body)
        report_id = payload["report_id"]
        log(f"взяв {report_id}" + (" (повторна доставка)" if message.redelivered else ""))
        await build_report(report_id, ReportRequest(**payload["data"]))
        log(f"готово {report_id}")


async def main() -> None:
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        log(f"чекаю на повідомлення в черзі {QUEUE_NAME}, Ctrl+C щоб зупинити")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    await handle(message)
                except Exception as e:  # noqa: BLE001  один зламаний звіт не має вбивати воркер
                    log(f"помилка: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("воркер зупинено")
