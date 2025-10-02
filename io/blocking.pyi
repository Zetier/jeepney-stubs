from collections import deque
from collections.abc import Iterable
from socket import socket
from typing import Any, Literal

from ..bus_messages import MatchRule

from ..low_level import Message
from .common import FilterHandle

__all__ = [
    "open_dbus_connection",
    "DBusConnection",
    "Proxy",
]

def open_dbus_connection(
    bus: str = "SESSION",
    enable_fds: bool = False,
    auth_timeout: float = 1,
) -> DBusConnection: ...

class DBusConnectionBase:
    def __init__(self, sock: socket, enable_fds: bool = False) -> None: ...
    def __enter__(self) -> DBusConnection: ...
    def __exit__(self) -> Literal[False]: ...
    def close(self) -> None: ...

class DBusConnection(DBusConnectionBase):
    def send(self, message: Message, serial: Iterable[int] | None = None) -> None: ...

    # for backwards compat reasons, note that the actual lib just assigns it to send
    def send_message(
        self, message: Message, serial: Iterable[int] | None = None
    ) -> None: ...
    def receive(self, *, timeout: int | None = None) -> Message: ...
    def recv_messages(self, *, timeout: int | None = None) -> None: ...
    def send_and_get_reply(
        self, message: Message, *, timeout: int | None = None
    ) -> Message: ...
    def filter(
        self, rule: MatchRule, queue: deque[Message] | None = None, bufsize: int = 1
    ) -> FilterHandle: ...

class Proxy:
    def __init__(
        self,
        msggen: Any,
        connection: DBusConnection,
        *,
        timeout: float | None = ...,
    ) -> None: ...
