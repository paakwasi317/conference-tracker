from fastapi import APIRouter, Depends, HTTPException, status

tracker_api = APIRouter(prefix="/v1/tracker")