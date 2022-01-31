
import storage_service as ss
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.middleware.cors import CORSMiddleware
from fastapi import APIRouter , HTTPException
from fastapi.staticfiles import StaticFiles
from schemas import ProcessFile
from processing import Process,GenerateReport
import asyncio
import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(".env")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process_data/",status_code=201)
async def process_data(file_in: ProcessFile):
    
    if not file_in:
        raise HTTPException(
            status_code=400,
            detail="Error finding file, check  file and bucket name",
        )
    else:
        Process(filename=file_in.filename,bucket=file_in.bucket)

    return "Data uploaded created"

@app.post("/generate_report/",status_code=201)
async def process_data(file_in: ProcessFile):
    
    if not file_in:
        raise HTTPException(
            status_code=400,
            detail="Error finding file, check  file and bucket name",
        )
    else:
        GenerateReport(filename=file_in.filename,bucket=file_in.bucket)
        app.mount("/report", StaticFiles(directory="report"), name="report")

    return "Expectations created"




@app.post("/process_dashboard/",status_code=201)
def process_dashboard(file_in: ProcessFile):
    if not file_in:
            raise HTTPException(
                status_code=400,
                detail="Error finding file, check  file name. This endpoint must be requested afters process data.",
            )
    from mount_app import mount_dash_app
    mount_dash_app(app)
    return "Dashboard ready, visit the dashboard at /app/app1"


if __name__ == "__main__":
    uvicorn.run(app, port=8002)