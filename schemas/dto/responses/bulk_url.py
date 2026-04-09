"""
Response DTOs for bulk URL shortening endpoint.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.models.url import UrlStatus


class BulkUrlResultItem(BaseModel):
    """Result for a single URL in a bulk shorten response."""

    index: int = Field(description="Zero-based index of this URL in the request array.")
    success: bool = Field(description="Whether the URL was successfully shortened.")
    alias: str | None = Field(
        default=None,
        description="Short code (only present on success).",
    )
    short_url: str | None = Field(
        default=None,
        description="Full shortened URL (only present on success).",
    )
    long_url: str = Field(description="The original URL that was submitted.")
    error: str | None = Field(
        default=None,
        description="Error message (only present on failure).",
    )
    status: UrlStatus | None = Field(
        default=None,
        description="URL status (only present on success).",
    )


class BulkShortenResponse(BaseModel):
    """Response body for POST /api/v1/bulk-shorten."""

    total: int = Field(description="Total number of URLs submitted.")
    success_count: int = Field(description="Number of URLs successfully shortened.")
    error_count: int = Field(description="Number of URLs that failed.")
    results: list[BulkUrlResultItem] = Field(
        description="Per-URL results in the same order as the request."
    )
