from pydantic import AnyHttpUrl, BaseModel


class ShortenRequest(BaseModel):
    url: AnyHttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str
    target_url: str


class HealthResponse(BaseModel):
    status: str
    database: str
    cache: str
