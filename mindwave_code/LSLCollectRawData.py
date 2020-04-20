from __future__ import print_function

import mindwave, time
from pprint import pprint
from pylsl import StreamInfo, StreamOutlet

import socket,select

import time, datetime, sys

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

import sys


class MindwaveLSLRecorder: 
    def __init__(self): 
        # Create eeg outlet [raw eeg, attention, meditation, blink]
        self.__Fs = 128 # 128Hz 
        info_eeg = StreamInfo(name='Mindwave EEG', 
            type='EEG', channel_count=4, nominal_srate=self.__Fs, 
            channel_format='float32', source_id='eeg_thread')
        self.__eeg_outlet = StreamOutlet(info_eeg)
        self.currentTimestamp = None
        


    def run(self):
        print("Connecting")
        headset = mindwave.Headset('/dev/tty.MindWaveMobile-SerialPo')
        time.sleep(2)
        print("Connected!")

        try:
            while (headset.poor_signal > 5):
                print("Headset signal noisy %d. Adjust the headset and the earclip." % (headset.poor_signal))
                time.sleep(0.1)
                
            print("Writing output to LSL stream" )
            stime = time.time()
            prevTime = 0
            while True:
                cycle_start_time = time.time()
                if headset.poor_signal > 5 :
                    print("Headset signal noisy %d. Adjust the headset and the earclip." % (headset.poor_signal))
                    self.__eeg_outlet.push_sample(np.array([0, 0, 0, 0]))
                else :
                    self.__eeg_outlet.push_sample(np.array([headset.raw_value, headset.attention, headset.meditation, headset.blink]))

                timeDiff = int(time.time()-stime)
                if(timeDiff != prevTime) : 
                    print("seconds elapsed: " + str(timeDiff))
                    prevTime = timeDiff

                
                time.sleep((1/(self.__Fs)) - (time.time() - cycle_start_time + 0.0005))

        finally:
            print("Closing!")
            headset.stop()

if __name__=="__main__":
    mlslr = MindwaveLSLRecorder()
    mlslr.run()