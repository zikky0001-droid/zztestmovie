from pathlib import Path
import sys
import traceback

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from moviebox_api_v3.v3.constants import SubjectType
from moviebox_api_v3.v3.core import Search
from moviebox_api_v3.v3.http_client import MovieBoxHttpClient


app = FastAPI(title="MovieBox API v3 Test")

BASE_DIR = Path(__file__).parent


@app.get("/")
async def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/api/test")
async def test():
    return {
        "status": "ok",
        "python": sys.version,
        "package": "moviebox-api-v3",
        "version": "3.0.2"
    }


@app.get("/api/search")
async def search(q: str, page: int = 1, per_page: int = 10):

    if not q.strip():
        return JSONResponse(
            {
                "success": False,
                "error": "Missing query"
            },
            status_code=400
        )

    if page < 1:
        page = 1

    if per_page < 1:
        per_page = 10

    if per_page > 50:
        per_page = 50

    query = q.strip()

    print("=" * 60, flush=True)
    print(f"[MovieBox v3] Searching: {query}", flush=True)
    print(f"[MovieBox v3] Page: {page}", flush=True)
    print(f"[MovieBox v3] Per page: {per_page}", flush=True)
    print("=" * 60, flush=True)

    try:

        async with MovieBoxHttpClient(timeout=8) as client:

            print(
                "[MovieBox v3] HTTP client created",
                flush=True
            )

            api = Search(
                client_session=client,
                query=query,
                subject_type=SubjectType.ALL,
                page=page,
                per_page=per_page,
            )

            print(
                "[MovieBox v3] Search object created",
                flush=True
            )

            data = await api.get_content()

            print(
                "[MovieBox v3] Search request completed",
                flush=True
            )

            return {
                "success": True,
                "query": query,
                "page": page,
                "per_page": per_page,
                "result": serialize(data)
            }

    except Exception as e:

        print("=" * 60, flush=True)
        print("[MovieBox v3] ERROR", flush=True)
        print("=" * 60, flush=True)

        print(
            f"Error type: {type(e).__name__}",
            flush=True
        )

        print(
            f"Error: {str(e)}",
            flush=True
        )

        print("[MovieBox v3] Traceback:", flush=True)

        traceback.print_exc()

        print("=" * 60, flush=True)

        return JSONResponse(
            {
                "success": False,
                "query": query,
                "error": str(e),
                "error_type": type(e).__name__
            },
            status_code=500
        )


def serialize(value):

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (list, tuple)):
        return [
            serialize(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): serialize(item)
            for key, item in value.items()
        }

    if hasattr(value, "model_dump"):
        return serialize(value.model_dump())

    if hasattr(value, "dict"):
        return serialize(value.dict())

    if hasattr(value, "__dict__"):
        return serialize(vars(value))

    return str(value)
