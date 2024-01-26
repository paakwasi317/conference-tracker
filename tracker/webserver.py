from fastapi import APIRouter, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import io
from typing import Annotated

from utils.scheduler import Scheduler

tracker_api = APIRouter(prefix="/tracker")

templates = Jinja2Templates(directory="templates")

@tracker_api.post("/uploadfile")
async def create_upload_file(file: Annotated[bytes, File()]):
    file_byte = io.BytesIO(file)
    scheduler= Scheduler()
    scheduler.clean_data(file_byte)
    multiple_schedules = scheduler.create_multiple_schedules()
    return {"schedules": multiple_schedules}

@tracker_api.get("", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="item.html", context={}
    )