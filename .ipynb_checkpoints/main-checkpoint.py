
import storage_service as ss
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi import APIRouter , HTTPException
from schemas import ProcessFile
from data_quality_service import Expectations
from processing import Process
import asyncio

app = FastAPI()

@app.post("/process_data/",status_code=201)
async def process_data(file_in: ProcessFile):

    process = Process(filename=file_in.filename,bucket=file_in.bucket)
    if not process.result:
            raise HTTPException(
                status_code=400,
                detail="Error finding file, check bucket name and file name",
            )
    await asyncio.sleep(1)
    if process.data_downloaded:                
        from mount_app import mount_dash_app
        mount_dash_app(app)
    return True


if __name__ == "__main__":
    uvicorn.run(app, port=8002)