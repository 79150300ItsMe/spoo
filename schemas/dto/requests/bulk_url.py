"""
Request DTO for bulk URL shortening endpoint.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class BulkUrlItem(BaseModel):
    """A single URL entry in a bulk shorten request."""

    url: str = Field(
        max_length=8192,
        description="The destination URL to shorten.",
    )


class BulkCreateUrlRequest(BaseModel):
    """Request body for bulk URL shortening.

    Accepts a list of URLs and shared settings that apply to all URLs.
    Max 50 URLs per batch. Settings like password, block_bots, max_clicks,
    expire_after, and private_stats are applied uniformly to every URL.
    """

    urls: list[BulkUrlItem] = Field(
        min_length=1,
        max_length=50,
        description="List of URLs to shorten. Maximum 50 per request.",
    )

    # Shared settings applied to all URLs
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        description="Password to protect all URLs. Min 8 chars.",
    )
    block_bots: bool | None = Field(
        default=None,
        description="Block known bot user agents from accessing the URLs.",
    )
    max_clicks: int | None = Field(
        default=None,
        gt=0,
        description="Maximum clicks before each URL expires.",
    )
    expire_after: str | int | None = Field(
        default=None,
        description="Expiration time for all URLs. ISO 8601 or Unix epoch.",
    )
    private_stats: bool | None = Field(
        default=None,
        description="Make statistics private for all URLs.",
    )
