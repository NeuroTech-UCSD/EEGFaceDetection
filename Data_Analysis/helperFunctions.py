from imports import *
from constants import StreamType

# Load in xdf info a useable format
def loadxdf(fname, synthetic = False):
    # Load dataset from xdf and export eeg_raw, eeg_time, mrk_raw, mrk_time, channels
    streams, fileheader = pyxdf.load_xdf(fname, dejitter_timestamps=False) #ollie 9/11/2019
    
    # Create empty dict to be returned
    stream_data = {}
    
    # Seperate streams
    for stream in streams:
        stream_type = stream['info']['type'][0].lower()
        if stream_type in StreamType.getValues():
            stream_data[stream_type] = {}
            if stream_type == StreamType.EEG.value: 
                # Baseline EEG
                stream_data[stream_type][StreamType.DATA.value] = np.array(stream['time_series'])
                for channel in range(np.array(stream['time_series']).shape[1]): 
                    values = stream_data[stream_type][StreamType.DATA.value][:,channel]
                    mean = np.mean(values)
                    stream_data[stream_type][StreamType.DATA.value][:,channel] = values - mean
            else :
                stream_data[stream_type][StreamType.DATA.value] = np.array(stream['time_series'])
            stream_data[stream_type][StreamType.TIME.value] = np.array(stream['time_stamps'])
            if stream_type == StreamType.EEG.value: 
                stream_data[stream_type][StreamType.FS.value] = stream['info']['nominal_srate'][0]
        
    return stream_data
    

def getEEGfs(original_data):
    if StreamType.EEG.value in original_data : 
        return int(original_data[StreamType.EEG.value][StreamType.FS.value])
    else : 
        return -1


def ensureDirExists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def writeToPickle(data, output_path):
    mode = 'a' if os.path.exists(output_path) else 'w'
    # Create file if does not exist
    with open(output_path, mode) as f:
        f = f # Do nothing
    
    # Write data to output
    with open(output_path, 'wb') as f: 
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

def loadPickle(path):
    with open(path, 'rb+') as f:
        data = pickle.load(f)
    return data

# Returns a new data structure that starts at start_timestamp and ends at end_timestamp (inclusive)
def epochByTime(start_timestamp, end_timestamp, data): 
    new_data = {}
    for stream_type in data: 
        time_series = data[stream_type][StreamType.TIME.value]
        data_series = data[stream_type][StreamType.DATA.value]
        
        indexes = np.intersect1d(np.where(time_series >= start_timestamp), np.where(time_series <= end_timestamp)) 
        new_data[stream_type] = {}
        new_data[stream_type][StreamType.TIME.value] = time_series[indexes]
        new_data[stream_type][StreamType.DATA.value] = data_series[indexes]
        if StreamType.FS.value in data[stream_type].keys():
            fs = data[stream_type][StreamType.FS.value]
            new_data[stream_type][StreamType.FS.value] = fs
    
    return new_data

# Get the corresponding timestamp for a marker index
def getTimestampForMarkIndex(mrk_index, data):
    return data[StreamType.MARKER.value][StreamType.TIME.value][mrk_index]

# Return a new data structure that starts at the marker from index up to the marker to index (inclusive)
def epochByMarkIndex(mrk_from_index, mrk_to_index, data):
    
    start_timestamp = getTimestampForMarkIndex(mrk_from_index, data)
    end_timestamp = getTimestampForMarkIndex(mrk_to_index, data)
    
    return epochByTime(start_timestamp, end_timestamp, data)

# Returns the filtered EEG data by IIR Butterworth order = 2 
def filterEEG(eeg_data, fs, f_range=(0.5,50)):
    sig_filt = filt.filter_signal(eeg_data, fs, 'bandpass', f_range, filter_type='iir', butterworth_order=2)
    test_sig_filt = filt.filter_signal(sig_filt, fs, 'bandstop', (58, 62), n_seconds=1)
    num_nans = sum(np.isnan(test_sig_filt))
    sig_filt = np.concatenate(([0]*(num_nans // 2), sig_filt, [0]*(num_nans // 2)))
    sig_filt = filt.filter_signal(sig_filt, fs, 'bandstop', (58, 62), n_seconds=1)
    sig_filt = sig_filt[~np.isnan(sig_filt)]
    return sig_filt


# Get all the marker indexes in dictionary form
def getMarkerIndexes(original_data):
    markers = np.array(original_data[StreamType.MARKER.value][StreamType.DATA.value][:,0])
    marker_indexes = {}
    for index, marker in enumerate(markers): 
        if marker not in marker_indexes:
            marker_indexes[marker] = list()
        marker_indexes[marker].append(index)
    return marker_indexes


# Get index of the previous and next label 
def getPreviousLabelIndex(label_to_find, max_index, original_data): 
    index = max_index
    while(index >= 0):
        if original_data[StreamType.MARKER.value][StreamType.DATA.value][index] == label_to_find:
            return index
        index -= 1
    return -1

def getNextLabelIndex(label_to_find, min_index, original_data): 
    index = min_index
    while(index < len(original_data[StreamType.MARKER.value][StreamType.DATA.value])):
        if original_data[StreamType.MARKER.value][StreamType.DATA.value][index] == label_to_find:
            return index
        index += 1
    return -1

## Get data sections

# marker_primary is the primary marker to look for. marker_secondary is the secondary label to help bound the primary marker in the front or the back. 
def getMarkerBoundSingleMarkerData(marker_primary, marker_secondary, original_data, go_backward=True):
    marker_indexes = getMarkerIndexes(original_data)
    sub_markers_indexes = marker_indexes[marker_primary]
    sub_markers_secondary_indexes = list()
    data = list()
    for sub_markers_index in sub_markers_indexes:
        if go_backward:
            secondary_index = getPreviousLabelIndex(marker_secondary, sub_markers_index, original_data)
            data.append(epochByMarkIndex(secondary_index, sub_markers_index, original_data))
        else :
            secondary_index = getNextLabelIndex(marker_secondary, sub_markers_index, original_data)
            data.append(epochByMarkIndex(sub_markers_index, secondary_index, original_data))
        
        sub_markers_secondary_indexes.append(secondary_index)
    return data, sub_markers_indexes, sub_markers_secondary_indexes
        
