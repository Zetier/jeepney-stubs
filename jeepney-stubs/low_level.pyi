from _typeshed import FileDescriptorLike, ReadableBuffer
from collections.abc import Iterator, Sequence
from enum import Enum, IntEnum, IntFlag
from typing import Any, Generic, type_check_only
from typing_extensions import NoReturn, Protocol, TypeVar

T = TypeVar("T")
TPy = TypeVar("TPy")
TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

_Signature = str
_DBusObject = tuple[str, T]

_ParseResult = tuple[T, int]

@type_check_only
class Serializable(Protocol[T]):
    def parse_data(
        self,
        buf: ReadableBuffer,
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptorLike],
    ) -> _ParseResult[T]: ...
    def serialise(
        self,
        data: T,
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptorLike],
    ) -> bytes: ...

class SizeLimitError(ValueError):
    """Raised when trying to (de-)serialise data exceeding D-Bus' size limit.

    This is currently only implemented for arrays, where the maximum size is
    64 MiB.
    """

    pass

class Endianness(Enum):
    little = 1
    big = 2

    def struct_code(self) -> str: ...
    def dbus_code(self) -> bytes: ...

class MessageType(Enum):
    method_call = 1
    method_return = 2
    error = 3
    signal = 4

class MessageFlag(IntFlag):
    no_reply_expected = 1
    no_auto_start = 2
    allow_interactive_authorization = 4

class HeaderFields(IntEnum):
    path = 1
    interface = 2
    member = 3
    error_name = 4
    reply_serial = 5
    destination = 6
    sender = 7
    signature = 8
    unix_fds = 9

def padding(pos: int, step: int) -> int: ...

class FixedType(Serializable[T]):
    def __init__(self, size: int, struct_code: str) -> None: ...

class Boolean(FixedType[bool]):
    def __init__(self) -> None: ...

class FileDescriptor(FixedType[FileDescriptorLike]):
    def __init__(self) -> None: ...

class StringType(FixedType[str]):
    def __init__(self, length_type: FixedType[object]) -> None: ...
    @property
    def alignment(self) -> int: ...

    # Can't _exclude_ types with overloads but this throws on non-str data
    def check_data(self, data: object) -> None | NoReturn: ...

class ObjectPathType(StringType):
    def __init__(self) -> None: ...

class Struct:
    def __init__(
        self,
        fields: list[Array[object] | StringType | FixedType[object] | Variant],
    ) -> None: ...
    def parse_data(
        self,
        buf: bytes,
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptorLike] = ...,
    ) -> _ParseResult[Any]: ...
    def serialise(
        self,
        data: tuple[object, ...],
        pos: int,
        endianness: Endianness,
        fds: None = ...,
    ) -> bytes: ...

class DictEntry(Struct, Generic[TKey, TValue]):
    def __init__(self, fields: tuple[TKey, TValue]) -> None: ...

_TArrayKey = TypeVar("_TArrayKey", default=object)

# Can't really do proper specialization here but
# array is either an array of a serializable type
# OR a dict of serializable types. the first type
# must be either of fixed size or a string though.
class Array(Generic[T, _TArrayKey]):
    def __init__(
        self, elt_type: Serializable[T] | DictEntry[_TArrayKey, T]
    ) -> None: ...
    def parse_data(
        self,
        buf: ReadableBuffer,
        pos: int,
        endianness: Endianness,
        fds: Sequence[FileDescriptor] = ...,
    ) -> _ParseResult[list[T] | dict[_TArrayKey, T]]: ...
    def serialise(
        self,
        data: bytes | dict[_TArrayKey, T] | list[T],
        pos: int,
        endianness: Endianness,
        fds: Sequence[object] = ...,
    ) -> bytes: ...

class Variant:
    def parse_data(
        self,
        buf: bytes,
        pos: int,
        endianness: Endianness,
        fds: tuple[FileDescriptorLike] = ...,
    ) -> _ParseResult[tuple[_Signature, object]]: ...
    def serialise(
        self,
        data: tuple[_Signature, object],
        pos: int,
        endianness: Endianness,
        fds: None = ...,
    ) -> bytes: ...

def calc_msg_size(buf: bytes) -> int: ...
def parse_header_fields(
    buf: bytes,
    endianness: Endianness,
) -> (
    tuple[dict[HeaderFields, str], int] | tuple[dict[HeaderFields, str | int], int]
): ...
def parse_signature(
    sig: list[str],
) -> Struct | Array[object] | StringType | ObjectPathType | FixedType[object]: ...
def serialise_header_fields(
    d: dict[HeaderFields, str],
    endianness: Endianness,
) -> bytes: ...

class BufferPipe:
    def __init__(self) -> None: ...
    def _peek_iter(self, nbytes: int) -> Iterator[bytes]: ...
    def _read_iter(self, nbytes: int) -> Iterator[bytes]: ...
    def peek(self, nbytes: int) -> bytes: ...
    def read(self, nbytes: int) -> bytes: ...
    def write(self, b: bytes) -> None: ...

class Header:
    def __init__(
        self,
        endianness: Endianness,
        message_type: int | MessageType,
        flags: int,
        protocol_version: int,
        body_length: int,
        serial: int,
        fields: dict[HeaderFields, str | int],
    ) -> None: ...
    @classmethod
    def from_buffer(cls, buf: bytes) -> tuple[Header, int]: ...
    def serialise(self, serial: int | None = ...) -> bytes: ...

class Message:
    def __init__(self, header: Header, body: tuple[object, ...]) -> None: ...
    @classmethod
    def from_buffer(
        cls, buf: bytes, fds: list[FileDescriptorLike] = ...
    ) -> Message: ...
    def serialise(self, serial: int | None = ..., fds: None = ...) -> bytes: ...

class Parser:
    def __init__(self) -> None: ...
    def add_data(self, data: bytes, fds: list[FileDescriptorLike] = ...) -> None: ...
    def get_next_message(self) -> Message | None: ...
