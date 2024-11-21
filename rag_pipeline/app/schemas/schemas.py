from datetime import datetime
from pydantic import BaseModel

class ContractBase(BaseModel):
    file_name: str

class ContractCreate(ContractBase):
    """
    Schema for creating a new Contract.
    """
    pass

class Contract(ContractBase):
    id: int
    upload_date: datetime
    processed: bool

    class Config:
        orm_mode = True