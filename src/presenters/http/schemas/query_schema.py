from pydantic import BaseModel


class QueryResponseSchema(BaseModel):
    id: int
    value: str
