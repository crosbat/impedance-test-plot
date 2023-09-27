# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 13:03:29 2023

@author: Nicolai André Weinreich
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta

def load_metadata(filepath):

    meta_data = pd.DataFrame()    

    with open(filepath, 'r') as file:
        csvreader = csv.reader(file, delimiter=';')
        for i, row in enumerate(csvreader):
            if i < 4:
                continue
            elif i > 9:
                break
            else:
                meta_data[row[0]] = row[1:3]
    
    meta_data["Channel ID"] = meta_data["Channel ID"].apply(int)
    meta_data["Revision"] = meta_data["Revision"].apply(float)
    meta_data["Sampling Rate"] = meta_data["Sampling Rate"].apply(int)
    meta_data["Trigger Count"] = meta_data["Trigger Count"].apply(int)
    meta_data["Sample Count"] = meta_data["Sample Count"].apply(int)
    
    return meta_data

def load_data(filepath, meta_data):
    
    data = pd.read_csv(filepath, delimiter=";", decimal=",", header=9, low_memory=False) # Read data from the csv file
    data = data.drop(["Trigger Start Time.1", "Unnamed: 4"], axis=1) # Remove unnecessary columns

    # Extend time column
    start_time = data["Trigger Start Time"].iloc[0]
    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H.%M.%S.%f")

    sample_rate = meta_data["Sampling Rate"].iloc[0]

    d_time = pd.Series(np.arange(len(data)))
    d_time = d_time.apply(lambda x: timedelta(seconds=x*(1/sample_rate)))

    data["Trigger Start Time"] = start_dt + d_time

    # Convert from current shunt voltage to current
    data["102 (Vdc)"] = data["102 (Vdc)"]/0.001 # Assuming 1 mOhm shunt resistance
    
    # Rename columns to more descriptive names
    data = data.rename({"Trigger Start Time" : "Time",
                        "101 (Vdc)" : "Voltage(V)",
                        "102 (Vdc)" : "Current(A)"}, axis=1)
    
    return data

def plot_data(data):
    
    plt.style.use('seaborn-darkgrid')
    fig, ax = plt.subplots(nrows=2, sharex=True)

    ax[0].plot(data["Time"], data["Current(A)"])
    ax[0].set_ylabel("Current (A)")
    
    ax[1].plot(data["Time"], data["Voltage(V)"])
    ax[1].set_ylabel("Voltage (V)")
    ax[1].set_xlabel("Sample Index")

    plt.savefig("impedance_data.png")

if __name__ == "__main__":
    
    filepath = "Data/1C PCC 10Hz 2023-09-22 13-04-28 0.csv" # Path to the csv file you want to load
    
    meta_data = load_metadata(filepath)
    data = load_data(filepath, meta_data)
    plot_data(data)
