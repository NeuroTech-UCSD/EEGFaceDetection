# COGS 189 Final Project: EEG Face Detection
Final Project for COGS 189, Winter 2020. 
<br>Trains a classifier to detect whether a person wearing a neurosky is looking at a face or not. 


## Project Structure 
- Data_Analysis: Contains the data and code to visualize / process the data. 
- PsychoPy_code: Files regarding experimental set up, including images. 
- mindwave_code: Raw eeg collection code. 


## Recording Data
- Install Lab Recorder from LSL https://github.com/sccn/lsl_archived/wiki/LabRecorder.wiki 
- Install Python Packages (you'll need to go through the code to see which packages are imported and that you don't have) 
- Run the PsychoPy Experiment: 
   - Start Lab Recorder 
   - change directory into the PsychoPy_code folder
   - python PsychoRun.py
- Run the NeuroSky Raw EEG collector: 
   - change directory into the mindwave_code folder
   - python LSLCollectRawData.py
- Select the LSL streams (your EEG stream + PsychoPy markers stream) in Lab Recorder to start recording 
- Rename the filename to participant_%p_block_%s.xdf and put the participant# in the Participant field, and session# in the Session field. 
- Press "Start" in Lab Recorder
- Put participant# and session# in the popup box from PsychoPy and Run! 

## Viewing Data 
- Move the data you just recorded into Data_Analysis/data/
- Run Jupyter Notebook and go to the Data_Analysis folder. 
- Open .ipynb files and you can use any of the functions in helperFunctions.py or constants.py
