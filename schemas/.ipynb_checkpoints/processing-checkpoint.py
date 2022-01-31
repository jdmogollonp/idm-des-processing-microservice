from pydantic import BaseModel


class ProcessFile(BaseModel):  
    bucket: str
    filename: str
