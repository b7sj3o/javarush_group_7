import asyncio
import json
import os
from pathlib import Path
import random
from datetime import datetime

from pydantic import BaseModel, Field

reports_dir = Path("reports")

class ReportRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    rows: int = Field(default=100_000, ge=1, le=100_000_000)
    fail: bool = False


async def build_report(report_id: str, data: ReportRequest) -> dict:
    await asyncio.sleep(5)
    if data.fail:
        raise ValueError(f"Звіт {report_id}: не вдалося зібрати дані")

    numbers = [random.randint(1, 1000) for _ in range(data.rows)]
    report = {
        "report_id": report_id,
        "title": data.title,
        "rows": data.rows,
        "total": sum(numbers),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "worker_pid": os.getpid(),
    }
    reports_dir.mkdir(exist_ok=True)
    path = reports_dir / f"{report_id}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
