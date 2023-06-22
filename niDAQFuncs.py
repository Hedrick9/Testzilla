#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Module/Program Name: NiDAQFuncs.py
# Module Description:
# The following program is to read data from the ni-cDAQ-9178 using the nidaqmx lib.
# Original Author: Russell Hedrick
# Original Date: 04/28/2023
# Last Edit: 06/22/2023
# Edit Description:
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                   Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import nidaqmx
import nidaqmx.system
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Create Task for each Device/Module
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a task for each nidaqmx event
task_list = []
try:
    system = nidaqmx.system.System.local()
#    tc_task = nidaqmx.Task() # Thermocouple task
    ci_task1 = nidaqmx.Task() # Counter task 1 (Energy)
    ci_task2 = nidaqmx.Task() # Counter task 2 (Gas)
    ci_task3 = nidaqmx.Task() # Counter task 3 (Water)
    ci_task4 = nidaqmx.Task() # Counter task 4 (Extra)
    task_list.append(ci_task1)
    task_list.append(ci_task2)
    task_list.append(ci_task3)
    task_list.append(ci_task4)

except Exception as e:
    print("Unable to connect to NI-DAQ")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#          Load tasks created in MAX (Measurement & Automation Explroer)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~ Locate and Load Persisted Tasks ~~~~~~~~~~~~~~~~~~~~~~
try:
    # Determine the name of the created task by indexing through tasks
    #print(system.tasks.task_names[0])
    # Create a persisted task - Loads the existing task from memory
    ptask1 = nidaqmx.system.storage.persisted_task.PersistedTask(system.tasks.task_names[0])
    ai_task = ptask1.load() # this task can now be used as others shown above
    task_list.append(ai_task)
except Exception as e:
    print(f"Unable to load task from NI-MAX: {system.tasks.task_names[0]}")
    tc_task1 = None
    task_list.append(ai_task)
try:
    # Create a persisted task - Loads the existing task from memory
    ptask2 = nidaqmx.system.storage.persisted_task.PersistedTask(system.tasks.task_names[1])
    tc_task1 = ptask2.load() # this task can now be used as others shown above
    task_list.append(tc_task1)
except Exception as e:
    print(f"Unable to load task from NI-MAX: {system.tasks.task_names[1]}")
    tc_task1 = None
    task_list.append(tc_task1)
try:
    # Create a persisted task - Loads the existing task from memory
    ptask3 = nidaqmx.system.storage.persisted_task.PersistedTask(system.tasks.task_names[2])
    tc_task2 = ptask3.load() # this task can now be used as others shown above
    task_list.append(tc_task2)
except Exception as e:
    print(f"Unable to load task from NI-MAX: {system.tasks.task_names[2]}")
    tc_task2 = None
    task_list.append(tc_task2)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                          Configure NI-DAQ Modules
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def config_daq(fs=5):
    """
    Configure specific tasks such as counters. This method is done for all 
    tasks not created through ni MAX. Configure each counter task for edge
    counting.
    task_list[0] = ci_task1
    task_list[1] = ci_task2
    task_list[2] = ci_task3
    task_list[3] = ci_task4
    """ 
    global task_list
    
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
        if task_list[4] and task_list[5] is not None: # Check which slot ci module is in 
            ci_slot=3
        else:
            ci_slot=2
        # Channel Names 
        ci_chan1 = system.devices[ci_slot].ci_physical_chans[0].name # Pin1 = ctr0
        ci_chan2 = system.devices[ci_slot].ci_physical_chans[2].name # Pin3 = ctr2
        ci_chan3 = system.devices[ci_slot].ci_physical_chans[1].name # Pin6 = ctr1
        ci_chan4 = system.devices[ci_slot].ci_physical_chans[3].name # Pin8 = ctr3
        
        # configure ci_task1
        task_list[0].ci_channels.add_ci_count_edges_chan(
                counter=ci_chan1,
                name_to_assign_to_channel="",
                edge=nidaqmx.constants.Edge.RISING,
                initial_count=0)
       
        # configure ci_task2
        task_list[1].ci_channels.add_ci_count_edges_chan(
                counter=ci_chan2,
                name_to_assign_to_channel="",
                edge=nidaqmx.constants.Edge.RISING,
                initial_count=0)
        
        # configure ci_task3
        task_list[2].ci_channels.add_ci_count_edges_chan(
                counter=ci_chan3,
                name_to_assign_to_channel="",
                edge=nidaqmx.constants.Edge.RISING,
                initial_count=0)
        
        # configure ci_task4
        task_list[3].ci_channels.add_ci_count_edges_chan(
                counter=ci_chan4,
                name_to_assign_to_channel="",
                edge=nidaqmx.constants.Edge.RISING,
                initial_count=0)
        
    except Exception as e:
        return "Unable to connect to digital input module NI-9411"


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Main function called by main.py script
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def init_daq():
    """
    Initialize DAQ and start all counter input tasks
    """
    global task_list
    
    try:
        config_daq()
        for i in range(0, 4):
            if task_list[i] is not None: task_list[i].start()
   
    except Exception as e:
        print("Unable to Initialize NI-DAQ")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Read Data from tasks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def read_daq():
    """
    - Read in thermocouple data from NI-9214 Module
    - Read in pulse data from NI-9411 Module
    - Read in analog voltage data from NI-9215 Module
    """
    try:
        data = []
        for i in range(4, len(task_list)):
            if task_list[i] is not None: data.extend(task_list[i].read())
        
        data.insert(0, task_list[0].ci_channels[0].ci_count) # ci_task1
        data.insert(1, task_list[1].ci_channels[0].ci_count) # ci_task2
        data.insert(2, task_list[2].ci_channels[0].ci_count) # ci_task3
        data.insert(3, task_list[3].ci_channels[0].ci_count) # ci_task4
 
        return data

    except Exception as e:
        return None
 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Close all running tasks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def close_daq():
    """
    Close all running tasks in task_list
    """
    try:
        for task in task_list:
            if task is not None: task.close()
    
    except Exception as e:
        print(e)
        return "No tasks to close."
    
   
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":
    
    import time
# Print Devices in DAQ
    #task = nidaqmx.Task()
    # system = nidaqmx.system.System.local()
    for device in system.devices:
        print(device.name)
    print(len(system.devices))
    init_daq()
    d = read_daq()
    print(d)
    close_daq()
    
       


