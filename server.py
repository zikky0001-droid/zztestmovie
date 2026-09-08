from pathlib import Path
import sys
import traceback

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from moviebox_api import MovieAuto


app = FastAPI(title="MovieBox Test")

BASE_DIR = Path(__file__).parent


# =========================
# HOME
# =========================

@app.get("/")
async def home():
    return FileResponse(BASE_DIR / "index.html")


# =========================
# BASIC TEST
# =========================

@app.get("/api/test")
async def test():
    return {
        "status": "ok",
        "python": sys.version,
        "message": "MovieBox API is running"
    }


# =========================
# MOVIEBOX SEARCH
# =========================

@app.get("/api/search")
async def search(q: str):

    if not q.strip():
        return JSONResponse(
            {
                "success": False,
                "error": "Missing query"
            },
            status_code=400
        )

    try:
        query = q.strip()

        print("=" * 60, flush=True)
        print(f"[MovieBox] Searching: {query}", flush=True)
        print("=" * 60, flush=True)

        # Create MovieAuto client
        print("[MovieBox] Creating MovieAuto...", flush=True)

        auto = MovieAuto()

        print("[MovieBox] MovieAuto created successfully", flush=True)

        # Run search
        print("[MovieBox] Calling auto.run()...", flush=True)

        result = await auto.run(query)

        print("[MovieBox] Search completed successfully", flush=True)

        # Serialize result
        serialized = serialize(result)

        print("[MovieBox] Result serialized successfully", flush=True)

        return {
            "success": True,
            "query": query,
            "result": serialized
        }

    except Exception as e:

        print("=" * 60, flush=True)
        print("[MovieBox] SEARCH ERROR", flush=True)
        print("=" * 60, flush=True)

        print(
            f"[MovieBox] Error type: {type(e).__name__}",
            flush=True
        )

        print(
            f"[MovieBox] Error: {str(e)}",
            flush=True
        )

        print("[MovieBox] Full traceback:", flush=True)

        traceback.print_exc()

        print("=" * 60, flush=True)

        return JSONResponse(
            {
                "success": False,
                "query": q,
                "error": str(e),
                "error_type": type(e).__name__
            },
            status_code=500
        )


# =========================
# SERIALIZER
# =========================

def serialize(value):

    if value is None:
        return None

    # Primitive values
    if isinstance(value, (str, int, float, bool)):
        return value

    # Lists / tuples
    if isinstance(value, (list, tuple)):
        return [
            serialize(item)
            for item in value
        ]

    # Dictionaries
    if isinstance(value, dict):
        return {
            str(key): serialize(val)
            for key, val in value.items()
        }

    # Pydantic v2
    if hasattr(value, "model_dump"):
        return serialize(
            value.model_dump()
        )

    # Pydantic v1 compatibility
    if hasattr(value, "dict"):
        return serialize(
            value.dict()
        )

    # Objects with attributes
    if hasattr(value, "__dict__"):
        return serialize(
            vars(value)
        )

    # Final fallback
    return str(value)

After committing/pushing it, open:

"https://zztestmovie.onrender.com/api/search?q=Avatar"

If it still gives "500", send me the Render log starting from:

[MovieBox] Searching: Avatar

The traceback will tell us the actual package/runtime problem.
