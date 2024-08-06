#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Module/Program Name: file_utils.py
# Module Description:
# The following program is designed to handle all file related tasks such as, 
# creating files, copying files, writing data, etc.
# Original Author: Russell Hedrick
# Original Date: 05/20/2023
# Last Edit: 
# Edit Description:
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                   Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import os
import csv
import shutil
import pandas as pd
from datetime import date
#~~~~~~~~~~~~~~~~~~~~~~~~~~~ Creat File Directory  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
current_directory = None
def create_directory():
    global current_directory
    current_directory = os.getcwd()
    if not os.path.exists(current_directory + "/Data"):
        os.mkdir(current_directory + "/Data")
        print("New Data directory added...\n")

#~~~~~~~~~~~~~~~~~~~~~~~~~~ CSV File Setup Function ~~~~~~~~~~~~~~~~~~~~~~~~~~~
file_name = None
def file_setup(testing, tc_modules):
    global file_name
    global current_directory
        
    if testing:
        pass
    else:
        # Create unique data file
        os.chdir(current_directory + "/Data")
        file_date = date.today().strftime("%m-%d-%y")
        headers = ["Time of Day", "Test Time", "Voltage", "W", "Wh.208", "Wh.120","Gas","Water","Extra"] + \
                  ["AI 1", "AI 2", "Ambient"]
        if tc_modules == 1:
            for i in range(1, 16):
                headers.append("Temp {}".format(i))
        else: 
            for i in range(1, 32):
                headers.append("Temp {}".format(i))

            
        for i in range(50):
            if not os.path.isfile(os.getcwd() +'/'+ file_date +'_'+ str(i) + ".csv"):
                file_name = file_date + '_' + str(i) + ".csv"
                print("Adding new file: {}\n".format(file_name))
                break
            elif i==49:
                print("Maximum files achieved for the day. Please remove some and try again.")
        with open(file_name, 'a') as file_data:
            csvWriter = csv.writer(file_data, delimiter=',')
            csvWriter.writerow([file_date])
            csvWriter.writerow(headers)
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create File Copy ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def copy_file():
    global file_name
    global current_directory
    global file_name

    source_file = current_directory + "/Data/" + file_name
    destination_file = current_directory + "/Data/" + "copy.csv"

    shutil.copy2(source_file, destination_file)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Data Write Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def write_data(data, testing, time_to_write):
    global file_name
    if testing and time_to_write:
        with open(file_name, 'a', newline='') as file_data:
            csvWriter = csv.writer(file_data, delimiter=',')
            csvWriter.writerow(data)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Data Dump  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def data_dump(data, testing):
    # cols = list(range(len(data[0]))) 
    datar = pd.DataFrame(data)
    destination_file = current_directory + "/Data/" + "data_dump.csv"
    if not testing:
        datar.to_csv(destination_file)
       
def write_headers(headers):
    global file_name
    # Read the CSV file into a list of lists
    with open(file_name, mode='r', newline='') as file:
        reader = csv.reader(file)
        data = list(reader)
    # Overwrite the first row (header)
    data[2] = headers
    # Write the updated data back to the CSV file
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def read_config(config_file="default_config.csv"):
    file_path = current_directory + "/config/" + config_file
    configs = pd.read_csv(file_path)
    return configs
    
    
