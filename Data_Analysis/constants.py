from enum import Enum


# Data stream types
class StreamType(Enum):
    MARKER = 'markers'
    EEG = 'eeg'
    DATA = 'data'
    TIME = 'time'
    FS = 'fs'
    
    def getValues() :
        return [st.value for st in StreamType]

