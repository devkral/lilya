import asyncio
import functools
import hashlib
from typing import Any, Sequence, TypeVar, Union

from lilya.types import Lifespan, Receive, Scope, Send

T = TypeVar("T")

try:
    hashlib.md5(b"data", usedforsecurity=False)  # type: ignore[call-arg]

    def md5_hexdigest(data: bytes, *, usedforsecurity: bool = True) -> str:  # pragma: no cover
        return hashlib.md5(  # type: ignore[call-arg]
            data, usedforsecurity=usedforsecurity
        ).hexdigest()

except TypeError:  # pragma: no cover

    def md5_hexdigest(data: bytes, *, usedforsecurity: bool = True) -> str:
        return hashlib.md5(data).hexdigest()


def is_async_callable(obj: Any) -> Any:
    while isinstance(obj, functools.partial):
        obj = obj.func

    return asyncio.iscoroutinefunction(obj) or (
        callable(obj) and asyncio.iscoroutinefunction(obj.__call__)
    )


class AyncLifespanContextManager:  # pragma: no cover
    """
    Manages and handles the on_startup and on_shutdown events
    in an Lilya way.
    """

    def __init__(
        self,
        on_shutdown: Union[Sequence[Any], None] = None,
        on_startup: Union[Sequence[Any], None] = None,
    ) -> None:
        self.on_startup = [] if on_startup is None else list(on_startup)
        self.on_shutdown = [] if on_shutdown is None else list(on_shutdown)

    def __call__(self: T, app: object) -> T:
        return self

    async def __aenter__(self) -> None:
        """Runs the functions on startup"""
        for handler in self.on_startup:
            if is_async_callable(handler):
                await handler()
            else:
                handler()

    async def __aexit__(self, scope: Scope, receive: Receive, send: Send, **kwargs: "Any") -> None:
        """Runs the functions on shutdown"""
        for handler in self.on_shutdown:
            if is_async_callable(handler):
                await handler()
            else:
                handler()


def handle_lifespan_events(
    on_startup: Union[Sequence[Any], None] = None,
    on_shutdown: Union[Sequence[Any], None] = None,
    lifespan: Union[Lifespan[Any], None] = None,
) -> Any:  # pragma: no cover
    if on_startup or on_shutdown:
        return AyncLifespanContextManager(on_startup=on_startup, on_shutdown=on_shutdown)
    elif lifespan:
        return lifespan
    return None


def generate_lifespan_events(
    on_startup: Union[Sequence[Any], None] = None,
    on_shutdown: Union[Sequence[Any], None] = None,
    lifespan: Union[Lifespan[Any], None] = None,
) -> Any:  # pragma: no cover
    if lifespan:
        return lifespan
    return AyncLifespanContextManager(on_startup=on_startup, on_shutdown=on_shutdown)
