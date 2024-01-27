from fastapi import APIRouter, File, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import io
from typing import Annotated

from utils.logger import logger
from utils.scheduler import Scheduler, SchedulingError

tracker_api = APIRouter(prefix="/tracker")

templates = Jinja2Templates(directory="templates")

@tracker_api.post("/uploadfile")
async def upload_file(file: Annotated[bytes, File()]):
    file_byte = io.BytesIO(file)
    scheduler= Scheduler()
    try:
        scheduler.clean_data(file_byte)
        tracks = scheduler.create_tracks()
    except SchedulingError as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Server error. Please Contact support")
    return {"schedules": tracks}

@tracker_api.get("", response_class=HTMLResponse)
async def tracker_view(request: Request):
    return templates.TemplateResponse(
        request=request, name="tracker.html", context={}
    )