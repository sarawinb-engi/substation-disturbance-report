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
        self.ul1 = None 
        self.ul2 = None 
        self.ul3 = None 
        self.il1 = None
        self.il2 = None 
        self.il3 = None 
        self.per_unit = None 
        self.voltage_sag = 
    