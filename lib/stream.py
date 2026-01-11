import io
import struct
import uuid

from pathlib import Path
from typing import BinaryIO

from .common import Endianness, Source


#: STRUCT FORMAT CHARACTERS:
#: '<' - little-endian
#: '>' - big-endian
#:
#: 'b' - signed char
#: 'B' - unsigned char
#: 'h' - signed 16-bit integer
#: 'H' - unsigned 16-bit integer
#: 'i' - signed 32-bit integer
#: 'I' - unsigned 32-bit integer
#: 'q' - signed 64-bit integer
#: 'Q' - unsigned 64-bit integer
#: 'f' - float
#: 'd' - double

class Stream:
    """Unified interface for reading and seeking binary sources."""

    def __init__(self, source: Source):
        self._stream = self._transform_source(source)
        self._size = self._get_size()
        self._position = 0 #: tell()


    def _transform_source(self, source: Source) -> BinaryIO:
        """Normalize the input source into a seekable stream."""
        #: TODO: Complete this at a later date.
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists() and not path.is_file():
                raise FileNotFoundError(f'File not found: {source}')

            stream = open(path, 'rb')

        else:
            raise TypeError(f"Unsupported source type: {type(source)}")

        return stream

    def _get_size(self) -> int:
        """The total size of the stream in bytes."""
        self._stream.seek(0, io.SEEK_END)
        size = self._stream.tell()
        #: Reset stream.
        self._stream.seek(0)
        return size

    def tell(self) -> int:
        """The current absolute position of the stream cursor."""
        return self._position

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> None:
        """Move the stream cursor to a specified offset relative to whence."""
        self._position = self._stream.seek(offset, whence)

    def read(self, size: int = -1) -> bytes:
        """Read a specified number of bytes from the stream."""
        _data = self._stream.read(size)
        self._position += len(_data)
        return _data

    #: def find_next_chunk...
    #: def find_pattern...

    #: ... [read_i8 to read_f64_le] ...

    def read_integer(self, size: int, endian: Endianness, signed: bool = False) -> int:
        """Read a variable-width integer using the specified endianness and sign."""
        #: Using int.from_bytes when size is unknown for now.
        #: Also will be used for sizes unsupported by struct.unpack such as 24-bit.
        _data = self.read(size)
        return int.from_bytes(_data, byteorder=endian, signed=signed)

    def read_i8(self) -> int:
        """Read a signed 8-bit integer."""
        return struct.unpack("b", self.read(1))[0]

    def read_u8(self) -> int:
        """Read an unsigned 8-bit integer."""
        return struct.unpack("B", self.read(1))[0]

    def read_i16_be(self) -> int:
        """Read a signed 16-bit big-endian integer."""
        return struct.unpack(">h", self.read(2))[0]

    def read_i16_le(self) -> int:
        """Read a signed 16-bit little-endian integer."""
        return struct.unpack("<h", self.read(2))[0]

    def read_u16_be(self) -> int:
        """Read an unsigned 16-bit big-endian integer."""
        return struct.unpack(">H", self.read(2))[0]

    def read_u16_le(self) -> int:
        """Read an unsigned 16-bit little-endian integer."""
        return struct.unpack("<H", self.read(2))[0]

    def read_i32_be(self) -> int:
        """Read a signed 32-bit big-endian integer."""
        return struct.unpack(">i", self.read(4))[0]

    def read_i32_le(self) -> int:
        """Read a signed 32-bit little-endian integer."""
        return struct.unpack("<i", self.read(4))[0]

    def read_u32_be(self) -> int:
        """Read an unsigned 32-bit big-endian integer."""
        return struct.unpack(">I", self.read(4))[0]

    def read_u32_le(self) -> int:
        """Read an unsigned 32-bit little-endian integer."""
        return struct.unpack("<I", self.read(4))[0]

    def read_i64_be(self) -> int:
        """Read a signed 64-bit big-endian integer."""
        return struct.unpack(">q", self.read(8))[0]

    def read_i64_le(self) -> int:
        """Read a signed 64-bit little-endian integer."""
        return struct.unpack("<q", self.read(8))[0]

    def read_u64_be(self) -> int:
        """Read an unsigned 64-bit big-endian integer."""
        return struct.unpack(">Q", self.read(8))[0]

    def read_u64_le(self) -> int:
        """Read an unsigned 64-bit little-endian integer."""
        return struct.unpack("<Q", self.read(8))[0]

    def read_f32_be(self) -> float:
        """Read a 32-bit big-endian float."""
        return struct.unpack(">f", self.read(4))[0]

    def read_f32_le(self) -> float:
        """Read a 32-bit little-endian float."""
        return struct.unpack("<f", self.read(4))[0]

    def read_f64_be(self) -> float:
        """Read a 64-bit big-endian float."""
        return struct.unpack(">d", self.read(8))[0]

    def read_f64_le(self) -> float:
        """Read a 64-bit little-endian float."""
        return struct.unpack("<d", self.read(8))[0]

    def read_guid_le(self) -> uuid.UUID:
        """Read a 16-byte GUID. Always little-endian."""
        raw_bytes = self.read(16)
        return uuid.UUID(bytes_le=raw_bytes)

    def read_string(
        self, size: int, encoding: str = "ascii", strip: bool = False
    ) -> str:
        """Decode sequence of characters into a string using specified encoding."""
        raw_bytes = self.read(size)
        s = raw_bytes.decode(encoding)
        return s.rstrip("\x00") if strip else s

    def __len__(self) -> int:
        """The total size of the stream stream in bytes."""
        return self._size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stream.close()
