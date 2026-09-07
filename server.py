from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from moviebox_api import MovieAuto

app = FastAPI(title="MovieBox Test")

BASE_DIR = Path(__file__).parent


@app.get("/")
async def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/api/test")
async def test():
    return {
        "status": "ok",
        "python": __import__("sys").version,
        "message": "MovieBox API is running"
    }


@app.get("/api/search")
async def search(q: str):
    if not q.strip():
        return JSONResponse(
            {"success": False, "error": "Missing query"},
            status_code=400
        )

    try:
        auto = MovieAuto()

        result = await auto.run(q.strip())

        return {
            "success": True,
            "query": q,
            "result": serialize(result)
        }

    except Exception as e:
        return JSONResponse(
            {
                "success": False,
                "query": q,
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
        return [serialize(x) for x in value]

    if isinstance(value, dict):
        return {
            str(k): serialize(v)
            for k, v in value.items()
        }

    if hasattr(value, "model_dump"):
        return serialize(value.model_dump())

    if hasattr(value, "dict"):
        return serialize(value.dict())

    if hasattr(value, "__dict__"):
        return serialize(vars(value))

    return str(value)
    
    