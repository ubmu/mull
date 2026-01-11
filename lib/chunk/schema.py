import math
from dataclasses import dataclass

from .base import Chunk
from .common import PVOC_KAISER_DEFAULT_BETA, PVOC_WINDOW_TYPE

@dataclass
class FormatChunk(Chunk):
    """The baseline `fmt ` chunk defined by the WAVEFORMAT structure."""

    format_tag: int
    """The compression code identifying the WAVE data format."""
    #: For example, 1 (0x0001) is uncompressed PCM (Pulse-Code Modulation).
    channel_count: int
    """The number of audio channels."""
    #: For example, 1 is mono, 2 is stereo.
    sample_rate: int
    """The number of samples per second in Hz."""
    byte_rate: int
    """The average number of bytes required per second for playback."""
    #: (sample_rate * channel_count * bits_per_sample) / 8
    block_align: int
    """The number of bytes needed for each frame. A frame is one sample for each channel."""
    #: (channel_count * bits_per_sample) / 8

    @property
    def format_name(self) -> str:
        """The string representation of the compression format code."""
        return ...

    @property
    def valid(self) -> bool:
        """Whether this is a valid WAVEFORMAT chunk."""
        #: TODO: Validate each value.
        return self.payload_size == 14

#: NOTE: We validate payload_size as we write chunks using the same schemas.

@dataclass
class PCMFormatChunk(FormatChunk):
    """An extension to WAVEFORMAT defined as PCMWAVEFORMAT."""

    bits_per_sample: int
    """The precision of each sample in bits."""

    @property
    def valid(self, recommended: bool = False) -> bool:
        """Whether this is a valid PCMWAVEFORMAT chunk."""
        if self.format_tag != 0x0001: #: TODO: Replace with constant.
            return False

        if self.payload_size != 16:
            return False

        if self.bits_per_sample not in (8, 16):
            return False

        if recommended:
            expected_byte_rate = self.sample_rate * self.block_align
            if self.byte_rate != expected_byte_rate:
                return False

        expected_block_align = self.channel_count * math.ceil(self.bits_per_sample / 8)
        if self.block_align != expected_block_align:
            return False

        return True

@dataclass
class ADPCMFormatChunk(PCMFormatChunk):
    #: TODO: Use WAVEFORMATEX?
    """The Microsoft ADPCM format variant."""
    extension_size: int
    """The size of the extended information block."""
    samples_per_block: int
    """The number of samples per block."""
    #: (((block_align - (7 * channels)) * 8) / (bits_per_sample * channels)) + 2
    coefficient_count: int
    """The number of coefficient sets defined in coefficients."""
    coefficients: list[tuple[int, int]]
    """..."""
    #:(i16, i16) * coefficient_count

@dataclass
class IMAADPCMFormatChunk(PCMFormatChunk):
    """The IMA ADPCM or DVI ADPCM format variant."""
    ...


#@dataclass
#class ExtendedFMTChunk(PCMFMTChunk):
#    """An extension to PCMWAVEFORMAT defined as WAVEFORMATEX."""
#
#    extension_size: int
#    """The size of the extended field."""
#    #: extension_size will be 0 or 22. If it is not 0, then it is extensible.
#
#    @property
#    def valid(self) -> bool:
#        """Whether this is a valid WAVEFORMATEX chunk."""
#        return self.payload_size == 18 and self.format_tag != 0xFFFE

#@dataclass
#class ExtensibleFMTChunk(ExtendedFMTChunk):
#    """An extension to WAVEFORMATEX defined as WAVEFORMATEXTENSIBLE."""
#
#    valid_bits_per_sample: int
#    """The actual precision of each sample in bits. Must be less than or equal to `bits_per_sample`."""
#    #samples_per_block
#    #reserved
#    #: TODO: Figure out the Extensible chunk
#    channel_mask: int
#    """The assignment of channels to speaker positions."""
#    subformat: str

@dataclass
class PVOCFormatChunk(ExtendedFormatChunk):
    """The Phase Vocoder extension."""
    #: Subformat GUID for PVOC-EX: 8312B9C2-2E6E-11d4-A824-DE5B96C3AB21
    #: Source: https://rwdobson.com/pvocex/pvocex.html
    version: int
    """The version of the PVOC-EX header. Initial version is 1."""
    data_block_size: int
    """The size of the `PVOCDATA` block in bytes. Standard is 32."""
    word_format: int
    """The numerical format of the analysis data. `IEEE_FLOAT` or `IEEE_DOUBLE`."""
    analysis_format: int
    """The representation of analysis channels. `PVOC_AMP_FREQ` or `PVOC_AMP_PHASE`."""
    source_format: int
    """Used to disambiguate the source sample type."""
    window_type: PVOC_WINDOW_TYPE
    """
    The standard analysis window used.

    Defined types:
        - `PVOC_HAMMING`
        - `PVOC_HANNING`
        - `PVOC_KAISER`
        - `PVOC_RECT`
        - `PVOC_CUSTOM`
    """
    bin_count: int
    """
    The number of analysis channels.
    Derived from FFT size: `bin_count` = (`fft_size` / 2) + 1
    """
    window_length: int
    """The analysis window length in samples."""
    overlap: int
    """The window overlap length in sample, also known as decimation."""
    frame_align: int
    """
    The byte-alignment of a single analysis frame.
    Usually: `bin_count` * 2 * sizeof(`word_format`).
    """
    analysis_rate: float
    """
    The rate of analysis frames per second.
    Calculated as: `sample_rate` / `overlap`
    """
    window_parameter: float = 0.0
    """
    Additional parameter for specific window types.
    For the `PVOC_KAISER` window, this represents `beta`. (defaults to `6.8` if `0.0`)
    Defaults to `0.0` for other window types unless required.
    """

    @property
    def beta(self) -> float:
        """The beta value."""
        return PVOC_KAISER_DEFAULT_BETA if (self.window_type == PVOC_WINDOW_TYPE.KAISER and self.window_parameter == 0.0) else 0.0


    """The WAVE_FORMAT_EXTENSIBLE format should be used whenever:
        1) PCM data has more than 16 bits/sample.
        2) The number of channels is more than 2.
        3) The actual number of bits/sample is not equal to the container size.
        4) The mapping from channels to speakers needs to be specified."""

@dataclass
class DataChunk(Chunk):
    """The `data` chunk."""
    #: Nothing of note to add as of yet.
    #: Number of sample frames divides DataChunk.payload_size by
    #: FormatChunk.block_align
    #: FORMAT and DATA are REQUIRED.


@dataclass
class FactChunk(Chunk):
    """The `fact` chunk."""

    sample_length: int
    """The number of samples per channel."""

@dataclass
class ListInfoChunk(Chunk):
    """The `INFO` chunk within `LIST`."""
    #: Source: https://wavref.til.cafe/chunk/info/
    archival_location: str | None   #: [IARL]
    """
    Indicates where the subject of the file is archived.
    For example, `Trey Research`.
    """
    artist: str | None              #: [IART]
    """
    Lists the artist of the original subject of the file.
    For example, `Michaelangelo`.
    """
    commissioned: str | None        #: [ICMS]
    """
    Lists the name of the person or organization that commissioned the subject of the file.
    For example, `Pope Julian II`.
    """
    comments: str | None            #: [ICMT]
    """
    Provides general comments about the file or the subject of the file.
    If the comment is several sentences long, end each sentence with a period.
    Do not include newline characters.
    """
    copyright: str | None           #: [ICOP]
    """
    Records the copyright information for the file.
    For example, `Copyright Encyclopedia International 1991.`
    If there are multiple copyrights, separate them by a semicolon followed by a space.
    """
    creation_date: str | None       #: [ICRD]
    """
    Specifies the date the subject of the file was created.
    List dates in year-month-day format, padding one-digit months and days with a zero on the left.
    For example, `1553-05-03` for May 3, 1553.
    """
    cropped: str | None             #: [ICRP]
    """
    Describes whether an image has been cropped and, if so, how it was cropped.
    For example, `lower right corner`.
    """
    dimensions: str | None          #: [IDIM]
    """
    IDIM Dimensions.
    Specifies the size of the original subject of the file.
    For example, `8.5 in h, 11 in w`.
    """
    dots_per_inch: str | None       #: [IDPI]
    """Stores dots per inch setting of the digitizer used to produce the file, such as "300"."""
    engineer: str | None            #: [IENG]
    """
    Stores the name of the engineer who worked on the file.
    If there are multiple engineers, separate the names by a semicolon and a blank.
    For example, `Smith, John; Adams, Joe`.
    """
    genre: str | None               #: [IGNR]
    """Describes the original work, such as `landscape`, `portrait`, `still life`, etc."""
    keywords: str | None            #: [IKEY]
    """
    Provides a list of keywords that refer to the file or subject of the file.
    Separate multiple keywords with a semicolon and a blank.
    For example, `Seattle; aerial view; scenery`.
    """
    lightness: str | None           #: [ILGT]
    """
    Describes the changes in lightness settings on the digitizer required to produce the file.
    Note that the format of this information depends on hardware used.
    """
    medium: str | None              #: [IMED]
    """
    Describes the original subject of the file.
    For example, `computer image`, `drawing`, `lithograph`, and so forth.
    """
    name: str | None                #: [INAM]
    """Stores the title of the subject of the file, such as `Seattle From Above`."""
    palette: str | None             #: [IPLT]
    """Specifies the number of colors requested when digitizing an image, such as `256`."""
    product: str | None             #: [IPRD]
    """
    Specifies the name of the title the file was originally intended for.
    For example, `Encyclopedia of Pacific Northwest Geography`.
    """
    subject: str | None             #: [ISBJ]
    """Describes the contents of the file, such as `Aerial view of Seattle`."""
    software: str | None            #: [ISFT]
    """
    Identifies the name of the software package used to create the file.
    For example, `Microsoft WaveEdit`.
    """
    source: str | None              #: [ISRC]
    """
    Identifies the name of the person or organization who supplied the original subject of the file.
    For example, `Trey Research`.
    """
    source_form: str | None         #: [ISRF]
    """
    Identifies the original form of the material that was digitized.
    For example, `slide`, `paper`, `map`, and so forth.
    This is not necessarily the same as `medium`.
    """
    technician: str | None          #: [ITCH]
    """
    Identifies the technician who digitized the subject file.
    For example, `Smith, John`.
    """

    @property
    def client(self) -> str | None:
        """Other name for the `commissioned` field."""
        return self.commissioned

    @property
    def title(self) -> str | None:
        """Other name for the `name` field."""
        return self.name

    @property
    def album(self) -> str | None:
        """Online taggers treat `product` as an album field."""
        return self.product

@dataclass
class InstrumentChunk(Chunk):
    """The `inst` chunk."""

    unshifted_note: int
    """
    The MIDI note number that corresponds to the unshifted pitch of the sample.
    Valid values range from 0 to 127.
    """
    fine_tune: int
    """
    The pitch shift adjustments, in cents, needed to hit the `unshifted_note` value exactly.
    This value can be used to compensate for tuning errors in the sampling process.
    Valid values range from -50 to 50.
    """
    gain: int
    """
    The volume setting for the sample in decibels.
    A value of zero decibels suggests no change in the volume.
    A value of -6 decibels suggests reducing the amplitude of the sample by two.
    """
    low_note: int
    """
    The lower bound MIDI note number range of the sample.
    Valid values range from 0 to 127.
    """
    high_note: int
    """
    The upper bound MIDI note number range of the sample.
    Valid values range from 0 to 127.
    """
    low_velocity: int
    """
    The lower bound MIDI velocity range of the sample.
    Valid values range from 0 to 127.
    """
    high_velocity: int
    """
    The upper bound MIDI velocity range of the sample.
    Valid values range from 0 to 127.
    """
