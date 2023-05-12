#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Module/Program Name: NiDAQFuncs.py
# Module Description:
# The following program is to read data from the ni-cDAQ-9178 using the nidaqmx lib.
# Original Author: Russell Hedrick
# Original Date: 04/28/2023
# Last Edit: 
# Edit Description:
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                   Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import nidaqmx
import nidaqmx.system
import queue
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Create Task for each Device/Module
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
q = queue.Queue()
# Create a task for each nidaqmx event
try:
#    tc_task = nidaqmx.Task() # Thermocouple task
    ci_task1 = nidaqmx.Task() # Counter task 1 (Energy)
    ci_task2 = nidaqmx.Task() # Counter task 2 (Gas)
    ci_task3 = nidaqmx.Task() # Counter task 3 (Water)
    ci_task4 = nidaqmx.Task() # Counter task 4 (Extra)

except Exception as e:
    print("Unable to connect to NI-DAQ")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#          Load tasks created in MAX (Measurement & Automation Explroer)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
try:
    system = nidaqmx.system.System.local()
    # Determine the name of the created dask by indexing through tasks
    #print(system.tasks.task_names[0])
    # Create a persisted task - Loads the existing task from memory
    ptask1 = nidaqmx.system.storage.persisted_task.PersistedTask(system.tasks.task_names[0])
    # load the persisted task into a python task object
    tc_task1 = ptask1.load() # this task can now be used as others shown above
except Exception as e:
    print("Unable to load task from NI-MAX")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                          Configure NI-DAQ Modules
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def config_daq(tc_slot1=1, tc_slot2=2, ci_slot=2, fs=5):
     
    global tc_task1
    global ci_task1
    global ci_task2
    global ci_task3
    global ci_task4
    
    system = nidaqmx.system.System.local() 
    ## Configure NI-9214 thermocouple module
    #try:
    #    for channel in system.devices[tc_slot1].ai_physical_chans:
    #        tc_task.ai_channels.add_ai_thrmcpl_chan(channel.name,
    #                units=nidaqmx.constants.TemperatureUnits.DEG_F,
    #                thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
    #                cjc_source=nidaqmx.constants.CJCSource.BUILT_IN)
    #        tc_task.timing.cfg_samp_clk_timing(fs,
    #                source="",
    #                sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
    #except Exception as e:
    #    return "Unable to connect to thermocouple module NI-9214"
    
    # Configure NI-9411 digital input channel for pulse counting

    try:
        # Channel Names 
        ci_chan1 = system.devices[ci_slot].ci_physical_chans[0].name # Pin1 = ctr0
        ci_chan2 = system.devices[ci_slot].ci_physical_chans[2].name # Pin3 = ctr2
        ci_chan3 = system.devices[ci_slot].ci_physical_chans[1].name # Pin6 = ctr1
        ci_chan4 = system.devices[ci_slot].ci_physical_chans[3].name # Pin8 = ctr3
        
        # Define a task for each counter and configure each task for edge counting
        ci_task1.ci_channels.add_ci_count_edges_chan(
                counter=ci_chan1,
                name_to_assign_to_channel="",
                edge=nidaqmx.constants.Edge.RISING,
                initial_count=0)
       
        ci_task2.ci_channels.add_ci_count_edges_chan(
                counter=ci_chan2,
                name_to_assign_to_channel="",
                edge=nidaqmx.constants.Edge.RISING,
                initial_count=0)
        
        ci_task3.ci_channels.add_ci_count_edges_chan(
                counter=ci_chan3,
                name_to_assign_to_channel="",
                edge=nidaqmx.constants.Edge.RISING,
                initial_count=0)
        
        ci_task4.ci_channels.add_ci_count_edges_chan(
                counter=ci_chan4,
                name_to_assign_to_channel="",
                edge=nidaqmx.constants.Edge.RISING,
                initial_count=0)

    except Exception as e:
        return "Unable to connect to digital input module NI-9411"


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Main function called by main.py script
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def init_daq(sample_rate=0.2):

    global tc_task1
    global ci_task1
    global ci_task2
    global ci_task3
    global ci_task4
    
    try:
        config_daq(ci_slot=2)
        ci_task1.start()
        ci_task2.start()
        ci_task3.start()
        ci_task4.start()
    
    except Exception as e:
        print(e)
        return "Unable to Initialize NI-DAQ"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Read Data from tasks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def read_daq():
    
    global tc_task1
    global ci_task1
    global ci_task2
    global ci_task3
    global ci_task4
    # Read in thermocouple data from NI-9214 Module
    # Read in pulse data from NI-9411 Module
    try:
        data = tc_task1.read()
        data.insert(0, ci_task1.ci_channels[0].ci_count)
        data.insert(1, ci_task2.ci_channels[0].ci_count)
        data.insert(2, ci_task3.ci_channels[0].ci_count)
        data.insert(3, ci_task4.ci_channels[0].ci_count)
        #q.put(data)
        return data
    except Exception as e:
        print(e)
        print("Unable to read from NI-DAQ")
 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Close all running tasks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Update this section with all relevant tasks
def close_daq():

    global tc_task1
    global ci_task1
    global ci_task2
    global ci_task3
    global ci_task4

    try:
        tc_task1.close()
        ci_task1.stop()
        ci_task1.close()
        ci_task2.stop()
        ci_task2.close()
        ci_task3.stop()
        ci_task3.close()
        ci_task4.stop()
        ci_task4.close()
    except Exception as e:
        print(e)
        return "No tasks to close."
    
   
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":

# Print Devices in DAQ
    #task = nidaqmx.Task()
    system = nidaqmx.system.System.local()
    for device in system.devices:
        print(device)
    import threading
    import time

    init_daq()
    i=0
    while i<50:
        datar = read_daq()
        i+=1
        print(datar)

    close_daq()


