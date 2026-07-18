from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    message: str
    data: Optional[T] = None
    error: Optional[str] = None
