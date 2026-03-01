import httpx
from typing import Any,Optional,Dict
import asyncio
from fastapi import HTTPException


async def _request_with_retries(
    method: str,
    url: str,
    request_id: str,
    json: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str,Any]] = None
) -> httpx.Response:
    timeout:float = 2.4
    http_retries = 3
    timeout = httpx.Timeout(timeout)
    headers={"User": "Reza"}

    last_exc: Exception | None = None
    for attempt in range(http_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.request(
                    method,
                    url,
                    headers=headers,
                    json=json,
                )
                return resp
        except (httpx.TimeoutException, httpx.TransportError) as e:
            last_exc = e
            if attempt < http_retries:
                await asyncio.sleep(0.1 * (attempt + 1))
                continue
            break

    raise HTTPException(status_code=502, detail=f"Document service unavailable: {last_exc}")