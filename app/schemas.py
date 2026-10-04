from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=250)
    nice_classes: list[int] = Field(default_factory=list)
    include_similar: bool = True
    limit: int = Field(default=20, ge=1, le=100)

class CompareSide(BaseModel):
    name: str
    nice_classes: list[int] = Field(default_factory=list)
    specification: str | None = None

class CompareRequest(BaseModel):
    left: CompareSide
    right: CompareSide

class IngestResponse(BaseModel):
    rpi_number: int | None
    rpi_date: str | None
    process_count: int
    event_count: int
    source_sha256: str
    parser_version: str
