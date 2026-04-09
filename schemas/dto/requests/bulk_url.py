"""
Request DTO for bulk URL shortening endpoint.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.dto.requests.url import CreateUrlRequest


class BulkCreateUrlRequest(BaseModel):
    """Request body for bulk URL shortening.

    Accepts a list of URL creation requests (max 50 per batch).
    Each item follows the same schema as the single shorten endpoint.
    """

    urls: list[CreateUrlRequest] = Field(
        min_length=1,
        max_length=50,
        description="List of URLs to shorten. Maximum 50 per request.",
    )
