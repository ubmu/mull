from dataclasses import dataclass

@dataclass
class Chunk:
    """A generic parsed chunk."""

    identifier: str
    """The FourCC chunk identifier."""
    payload_size: int
    """The reported size of the payload in bytes."""
    offset: int
    """The absolute byte offset where the chunk payload begins."""

@dataclass
class RawChunk:
    """
    An unparsed chunk without payload storage.
    """

    identifier: str
    """The FourCC chunk identifier."""
    reported_payload_size: int
    """The reported size of the payload in bytes."""
    actual_payload_size: int
    """
    The actual size of the payload in bytes.

    If CRF.VERIFY_REPORTED_SIZE is set, this is determined by:

        Checking if `size_field_exclusion_amount` is adhered to.

        Checking boundaries for the next valid chunk header.

    Otherwise, matches reported_size.
    """
    start_offset: int
    """The absolute byte offset where the chunk header begins."""
    payload_offset: int
    """The absolute byte offset where the chunk payload begins."""
    padding_size: int
    """The number of bytes added after the payload to align the chunk to boundary."""
    is_aligned: bool
    """Whether the current chunk is aligned."""
    breakpoint: bool
    """Whether a break/error occurred when reading the next chunk."""

    #: TODO: ENSURE THESE PROPERTIES WORK FOR ALL CONTAINERS.
    @property
    def end_offset(self) -> int:
        """Offset where the current chunk ends and the next is expected to begin."""
        return self.payload_offset + self.actual_payload_size + self.padding_size

    @property
    def size_mismatch(self) -> bool:
        """Whether the reported size matches the actual size."""
        return self.reported_payload_size == self.actual_payload_size

    @property
    def hidden_data(self) -> bool:
        """Hidden data may exist if actual payload size is greater than reported."""
        return self.actual_payload_size > self.reported_payload_size

#: NOTE: CHECKS FOR WHETHER ALIGNMENT MATCHES EXPECTED CONTAINER BOUNDARY
#: HAS TO BE DONE OUTSIDE OF RAWCHUNK.

@dataclass
class Master:
    """The container master chunk."""

    identifier: str
    """The FourCC container identifier."""
    size: int
    """Size of remaining data."""
    filesize: int
    """
    Size of the file.

    In general, this is calculated by using `size + size_bytes + identifier_bytes`.
    May differ based on container variant.
    """
    form_type: str
    """Formtype, or the specific file format."""
    size_field_exclusion_amount: int
    """
    The number of bytes the container excludes from chunk size.
    This value is the same as `overhead` stored within the container classes.
    """
