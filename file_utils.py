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
from datetime import date
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
def file_setup(testing):
    global file_name
    global current_directory
        
    if testing:
        pass
    else:
        # Create unique data file
        os.chdir(current_directory + "/Data")
        file_date = date.today().strftime("%m-%d-%y")
        headers = ["Time of Day", "Test Time", "Wh","Gas","Water","Extra",]
        for i in range(1, 17):
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Data Write Function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def write_data(data, testing):
    global file_name
    if testing:
        with open(file_name, 'a', newline='') as file_data:
            csvWriter = csv.writer(file_data, delimiter=',')
            csvWriter.writerow(data)

