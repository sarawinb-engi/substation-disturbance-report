from fitz import open as fitz_open
import re 
from datetime import datetime 
import matplotlib.pyplot as plt 
from collections import Counter 
import numpy as np 
import cmath 
import json 
import pandas as pd 
from tabulate import tabulate 

class DisturbanceAnalyzer: 
    def __init__(self, file_path, nominal_voltage=115000 / np.sqrt(3),
                 system_frequency=50):
        self.file_path = file_path 
        self.nominal_voltage = nominal_voltage 
        self.system_frequency = system_frequency 
        self.text = self.extract_text_from_pdf() 
        self.ul1 = None 
        self.ul2 = None 
        self.ul3 = None 
        self.il1 = None
        self.il2 = None 
        self.il3 = None 
        self.per_unit = None 
        self.voltage_sag_pct = None
        self.duration_ms = None 
        self.duration_cycles = None 
        self.event_datetime = None 
        self.current_componets = {} 
        self.voltage_componets = {} 
        self.note = "" 
        self.severity = "🟢 Normal"

    # Seperate text from PDF Report 
    def extract_text_from_pdf(self): 
        doc = fitz_open(self.file_path) 
        text = "" 
        for page in doc:
            text += page.get_text() 
        return text 
    
    # Seperate time from PDF Report  
    def extract_event_time(self):
        match = re.search(r'Trig date and time\s+(\d+/\d+/\d+\s+\d+:\d+:\d\.\d+)',self.text) 
        if match:
            time_format = '%m/%d/%Y %I:%M:%S.%f'
            self.event_datetime = datetime.strptime(match.group(1), time_format) 
            
    # Seperate value from PDF Report (Voltage)
    def extract_voltage_values(self): 
        match_ul1 = re.search(r'UL1\s+([\d.]+)\(V\)\s+([\d.]+)°', self.text) 
        match_ul2 = re.search(r'UL2\s+([\d.]+)\(V\)\s+([\d.]+)°', self.text)
        match_ul3 = re.search(r'UL3\s+([\d.]+)\(V\)\s+([\d.]+)°', self.text)
        
        if match_ul1 and match_ul2 and match_ul3: 
            self.ul1 = (float(match_ul1.group(1), float(match_ul1.group(2))))
            self.ul2 = (float(match_ul2.group(1), float(match_ul2.group(2))))
            self.ul3 = (float(match_ul3.group(1), float(match_ul3.group(2))))
            
            # Caculations voltage percentage and per-unit 
            voltages = [self.ul1[0], self.ul2[0], self.ul3[3]] 
            min_voltage = min(voltages) 
            self.min_phase = min_voltage
            # Voltage Per-Unit 
            self.per_unit = min_voltage / self.nominal_voltage 
            # Voltage Sag (%) 
            self.voltage_sag_pct = ((self.nominal_voltage - min_voltage)/ self.nominal_voltage) * 100 
            
    # Seperate values from PDF Report (Current)
    def extract_current_values(self):
        match_il1 = re.search(r'IL1\s+([\d.]+)\(A\)\s+([\d.])+°', self.text)
        match_il2 = re.search(r'IL2\s+([\d.]+)\(A\)\s+([\d.])+°', self.text)
        match_il3 = re.search(r'IL3\s+([\d.]+)\(A\)\s+([\d.])+°', self.text) 
        
        if match_il1 and match_il2 and match_il3 : 
            self.il1 = (float(match_il1.group(1)), float(match_il1.group(2)))
            self.il2 = (float(match_il1.group(1)), float(match_il1.group(2)))
            self.il3 = (float(match_il1.group(1)), float(match_il1.group(2)))
            
    # Seperate Events on Report  
    def extrect_event_duration(self): 
        match_on = re.search(r"UV/OV START\s+On\s+(\d+/\d+/\d+\s+\d+:\d+:\d+\.\d+)", self.text)
        match_off = re.search(r"UV/OV START\s+Off\s+(\d+/\d+/\d+\s+\d+:\d+:\d+\.\d+)", self.text) 
        
        if match_on and match_off :
            time_format = '%m/%d/%Y %I:%M:%S.%f' 
            time_on = datetime.strptime(match_on.group(1), time_format) 
            time_off = datetime.strptime(match_off.group(1), time_format) 
            self.duration_ms = (time_off - time_on).total_seconds() * 1000 
            self.duration_cycles = round((self.duration_ms/1000) * self.system_frequency, 2) 
            