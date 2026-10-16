from unittest.mock import patch

import httpx
import pytest

from rates import fetch_rate, get_http_client

NBU_USD = [{"r030": 840, "txt": "Долар США", "rate": 41.5, "cc": "USD", "exchangedate": "17.10.2026"}]


# @pytest.mark.asyncio
# @patch("rates.httpx.AsyncClient.get")
# async def test_fetch_rate_slide(mock_get):
#     mock_get.return_value.status_code = 200
#     mock_get.return_value.json.return_value = NBU_USD
#     async with httpx.AsyncClient(timeout=10) as client:
#         assert await fetch_rate(client=client, code="USD") == 41.5