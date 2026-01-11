from enum import IntEnum

PVOC_KAISER_DEFAULT_BETA = 6.8

class PVOC_WINDOW_TYPE(IntEnum):
    HAMMING = 1
    HANNING = 2
    KAISER = 3
    RECT = 4
    CUSTOM = 5

#: class PVOC_ANALYSIS_FORMAT(IntEnum):
    #: AMP_FREQ = 0
    #: AMP_PHASE = 1
