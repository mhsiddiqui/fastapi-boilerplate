"""Django-style page-number pagination.

Usage::

    from src.core.pagination import Page, PaginationParams, paginate

    @router.get("/users", response_model=Page[UserRead])
    async def list_users(
        request: Request,
        db: AsyncSession = Depends(get_async_db),
        params: PaginationParams = Depends(),
    ) -> Page[UserRead]:
        stmt = select(User).order_by(User.created.desc())
        return await paginate(request, db, stmt, UserRead, params)

The wrapper is generic — any ``Select`` + any Pydantic ``BaseModel`` works.
"""

from math import ceil
from typing import Generic, TypeVar

from fastapi import Query, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=BaseModel)

PAGE_QUERY = "page"
PAGE_SIZE_QUERY = "page_size"


class PaginationParams:
    """FastAPI dependency parsing ``?page=&page_size=`` query params.

    ``page`` is 1-indexed. ``page_size`` is clamped to [1, 200] so a single
    request can't drag the whole table.
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="1-indexed page number"),
        page_size: int = Query(default=50, ge=1, le=200, description="Items per page"),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PageLink(BaseModel):
    page: int
    url: str


class Page(BaseModel, Generic[T]):
    """Paginated response envelope. Generic over any Pydantic schema."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[T]
    total: int
    limit: int
    offset: int
    pages: int
    current: PageLink
    next: PageLink | None = None
    previous: PageLink | None = None


def _page_url(request: Request, page: int, page_size: int) -> str:
    """Rewrite the current request URL with new pagination query params."""
    return str(request.url.include_query_params(**{PAGE_QUERY: page, PAGE_SIZE_QUERY: page_size}))


async def paginate(
    request: Request,
    db: AsyncSession,
    stmt: Select,
    schema: type[T],
    params: PaginationParams,
) -> Page[T]:
    """Execute ``stmt`` paginated, serialize via ``schema``, return a :class:`Page`.

    Performs one ``COUNT(*) OVER (subquery)`` and one paginated SELECT — two
    round trips per call. The COUNT respects any WHERE/JOIN on ``stmt``.
    """
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    rows = (await db.execute(stmt.limit(params.limit).offset(params.offset))).scalars().all()

    pages = max(ceil(total / params.page_size) if total else 0, 1)

    current = PageLink(page=params.page, url=_page_url(request, params.page, params.page_size))
    next_link = (
        PageLink(page=params.page + 1, url=_page_url(request, params.page + 1, params.page_size))
        if params.page < pages
        else None
    )
    previous_link = (
        PageLink(page=params.page - 1, url=_page_url(request, params.page - 1, params.page_size))
        if params.page > 1
        else None
    )

    return Page[schema](
        items=[schema.model_validate(row) for row in rows],
        total=total,
        limit=params.limit,
        offset=params.offset,
        pages=pages,
        current=current,
        next=next_link,
        previous=previous_link,
    )
