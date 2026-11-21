"""python bench.py cpu | io | stuck | greedy | priority | ttl"""

import sys
import time

from celery.result import AsyncResult

from tasks import build_report, crunch, send_alert, send_promo, send_push


def wait(results: list[AsyncResult], timeout: float = 300) -> float:
    start = time.perf_counter()
    while not all(r.ready() for r in results):
        if time.perf_counter() - start > timeout:
            raise SystemExit("не дочекались: чи запущені воркери?")
        time.sleep(0.1)
    return time.perf_counter() - start


def show(results: list[AsyncResult]) -> None:
    for r in sorted(results, key=lambda r: r.result["done"]):
        print("  ", r.result)


def cpu() -> None:
    results = [crunch.delay() for _ in range(4)]
    print(f"4 × crunch: {wait(results):.1f} с")
    show(results)


def io() -> None:
    results = [build_report.delay(3) for _ in range(4)]
    print(f"4 × build_report(3): {wait(results):.1f} с")
    show(results)


def stuck() -> None:
    reports = [build_report.delay(10) for _ in range(6)]
    push = send_push.delay(1)
    print(f"push виконано через {wait([push]):.1f} с після відправки")
    wait(reports)


def greedy() -> None:
    results = [build_report.delay(12)] + [build_report.delay(1) for _ in range(7)]
    print(f"12 с + 7 × 1 с на двох воркерах: {wait(results):.1f} с")
    show(results)


def priority() -> None:
    pushes = [send_push.delay(i) for i in range(1, 11)]
    alert = send_alert.apply_async(args=["Сервер оплат не відповідає"], priority=9)
    print("У черзі 10 push і alert. Запусти воркер notifications і зачекай...")
    wait([*pushes, alert])
    order = sorted([*pushes, alert], key=lambda r: r.result["done"])
    place = order.index(alert) + 1
    print(f"alert виконано {place}-м з {len(order)}, хоча відправлено останнім")


def ttl() -> None:
    promo = send_promo.apply_async(args=["SALE50"], expires=10)
    print("Промокод у черзі, expires=10 с. Запусти воркер черги celery і чекай 30 с...")
    time.sleep(30)
    print("статус:", promo.status)

if __name__ == "__main__":
    {"cpu": cpu, "io": io, "stuck": stuck, "greedy": greedy, "priority": priority, "ttl": ttl}[sys.argv[1]]()
