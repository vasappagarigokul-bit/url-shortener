from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class URLRequest(BaseModel):
    long_url: HttpUrl = Field(...,
        max_length=8192
    )

class URLResponse(BaseModel):
    short_url: str

    model_config = ConfigDict(from_attributes=True)