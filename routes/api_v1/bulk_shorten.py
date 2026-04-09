"""
POST /api/v1/bulk-shorten — create multiple shortened URLs in one request.

Returns 200 with per-URL results (each URL can succeed or fail independently).
Auth is optional; API key users require `shorten:create` or `admin:all` scope.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from dependencies import (
    SHORTEN_SCOPES,
    CurrentUser,
    get_url_service,
    optional_scopes_verified,
)
from middleware.openapi import AUTH_RESPONSES, OPTIONAL_AUTH_SECURITY
from middleware.rate_limiter import Limits, limiter
from schemas.dto.requests.bulk_url import BulkCreateUrlRequest
from schemas.dto.responses.bulk_url import BulkShortenResponse, BulkUrlResultItem
from services.url_service import UrlService
from shared.datetime_utils import to_unix_timestamp
from shared.ip_utils import get_client_ip
from shared.logging import get_logger

log = get_logger(__name__)

router = APIRouter(tags=["URL Shortening"])


@router.post(
    "/bulk-shorten",
    status_code=200,
    responses=AUTH_RESPONSES,
    openapi_extra=OPTIONAL_AUTH_SECURITY,
    operation_id="bulkShortenUrls",
    summary="Bulk Create Shortened URLs",
)
@limiter.limit("5/minute")
async def bulk_shorten(
    request: Request,
    body: BulkCreateUrlRequest,
    user: CurrentUser | None = Depends(optional_scopes_verified(SHORTEN_SCOPES)),  # noqa: B008
    url_service: UrlService = Depends(get_url_service),
) -> BulkShortenResponse:
    """Create multiple shortened URLs in a single request.

    Submit up to **50 URLs** at once. Each URL is processed independently —
    if one fails (e.g. invalid URL, alias conflict), the others still succeed.

    **Authentication**: Optional — higher rate limits when authenticated.

    **API Key Scope**: `shorten:create` or `admin:all`

    **Rate Limits**: 5/minute

    **Notes**:

    - Each URL item follows the same schema as `POST /api/v1/shorten`
    - Failed URLs include an `error` message in the response
    - Results are returned in the same order as the input
    """
    owner_id = user.user_id if user is not None else None
    client_ip = get_client_ip(request)
    settings = request.app.state.settings
    app_url = settings.app_url.rstrip("/")

    results: list[BulkUrlResultItem] = []
    success_count = 0
    error_count = 0

    for i, url_req in enumerate(body.urls):
        try:
            doc = await url_service.create(url_req, owner_id, client_ip)
            results.append(
                BulkUrlResultItem(
                    index=i,
                    success=True,
                    alias=doc.alias,
                    short_url=f"{app_url}/{doc.alias}",
                    long_url=doc.long_url,
                    status=doc.status,
                )
            )
            success_count += 1
        except Exception as exc:
            error_msg = str(exc)
            # Extract clean error message from known error types
            if hasattr(exc, "message"):
                error_msg = exc.message
            results.append(
                BulkUrlResultItem(
                    index=i,
                    success=False,
                    long_url=url_req.long_url,
                    error=error_msg,
                )
            )
            error_count += 1
            log.warning(
                "bulk_shorten_item_failed",
                index=i,
                long_url=url_req.long_url,
                error=error_msg,
            )

    log.info(
        "bulk_shorten_completed",
        total=len(body.urls),
        success=success_count,
        errors=error_count,
        owner_id=str(owner_id) if owner_id else None,
    )

    return BulkShortenResponse(
        total=len(body.urls),
        success_count=success_count,
        error_count=error_count,
        results=results,
    )
