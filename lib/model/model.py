from pydantic import BaseModel
from typing import Optional


class ResponseModel(BaseModel):
    success: bool
    status_code: int
    error: Optional[str] = None
    data: Optional[dict] = None
