#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Module/Program Name: NiDAQFuncs.py
# Module Description:
# The following program is to read data from the ni-cDAQ-9178 using the nidaqmx lib.
# Original Author: Russell Hedrick
# Original Date: 04/28/2023
# Last Edit: 06/20/2024
# Edit Description:
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                   Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import nidaqmx
import nidaqmx.system
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Create Task for each Device/Module
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NI:

    def __init__(self):
        self.task_list = [] # list for all tasks that will be used for reading
        self.ci_slot = None # Flag for whether counter module is connected
        self.ai_slot = None # Flag for whether anaolog input module is connected
        self.tc_modules = 0 # number of tc modules connected
        self.four_chan = False
    #~~~~~~ Identify whether modules are conencted ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        system = nidaqmx.system.System.local()
        for count, device in enumerate(system.devices):
            if device.product_type == "NI 9211":
                self.tc_modules += 1
                self.four_chan = True
            elif device.product_type == "NI 9214":
                self.tc_modules += 1
            elif device.product_type == "NI 9411":
                self.ci_slot = count # Check which slot ci module is in 
            elif device.product_type == "NI 9215":
                self.ai_slot = count # Check which slot ai module is in 
    #~~~~~~ Create Tasks for Counter/DI Module ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        try:
        #   tc_task = nidaqmx.Task() # Thermocouple task
            ci_task1 = nidaqmx.Task() # Counter task 1 (Energy)
            ci_task2 = nidaqmx.Task() # Counter task 2 (Gas)
            ci_task3 = nidaqmx.Task() # Counter task 3 (Water)
            ci_task4 = nidaqmx.Task() # Counter task 4 (Extra)
            self.task_list.append(ci_task1)
            self.task_list.append(ci_task2)
            self.task_list.append(ci_task3)
            self.task_list.append(ci_task4)

        except Exception as e:
            print("Unable to connect to NI-DAQ")

    #~~~~~ Load tasks created in MAX (Measurement & Automation Explorer)
        p_tasks = system.tasks.task_names # list of all persisted tasks in memory
        # To Load Persisted Tasks by index instead of name:
        # ptask1 = nidaqmx.system.storage.persisted_task.PersistedTask(system.tasks.task_names[0])
        try:
            # Create a persisted task - Loads the existing task from memory
            if "ai_task" in p_tasks:
                ptask1 = nidaqmx.system.storage.persisted_task.PersistedTask("ai_task")
                ai_task = ptask1.load() # this task can now be used as others shown above
                self.task_list.append(ai_task)
        except Exception as e:
            print(f"Unable to load task from NI-MAX: ai_task") # system.tasks.task_names[0]
            ai_task = None
            self.task_list.append(ai_task)
        try:
            # Create a persisted task - Loads the existing task from memory
            if "tc_task1" in p_tasks:
                ptask2 = nidaqmx.system.storage.persisted_task.PersistedTask("tc_task1")
                tc_task1 = ptask2.load() # this task can now be used as others shown above
                self.task_list.append(tc_task1)
        except Exception as e:
            print(f"Unable to load task from NI-MAX: tc_task1") # system.tasks.task_names[1]
            tc_task1 = None
            self.task_list.append(tc_task1)
        try:
            # Create a persisted task - Loads the existing task from memory
            if "tc_task2" in p_tasks:
                ptask3 = nidaqmx.system.storage.persisted_task.PersistedTask("tc_task2")
                tc_task2 = ptask3.load() # this task can now be used as others shown above
                self.task_list.append(tc_task2)
        except Exception as e:
            print(f"Unable to load task from NI-MAX: tc_task2") # system.tasks.task_names[2]
            tc_task2 = None
            self.task_list.append(tc_task2)

        #~~~~~ Configure NI-DAQ Modules ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """
        Configure specific tasks such as counters. This method is done for all 
        tasks not created through ni MAX. Configure each counter task for edge
        counting.
        task_list[0] = ci_task1
        task_list[1] = ci_task2
        task_list[2] = ci_task3
        task_list[3] = ci_task4
        """ 

        system = nidaqmx.system.System.local() 
        ## Configure NI-9214 thermocouple module (EXAMPLE)
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
        if self.ci_slot is not None:
            # Channel Names 
            ci_chan1 = system.devices[self.ci_slot].ci_physical_chans[0].name # Pin1 = ctr0
            ci_chan2 = system.devices[self.ci_slot].ci_physical_chans[2].name # Pin3 = ctr2
            ci_chan3 = system.devices[self.ci_slot].ci_physical_chans[1].name # Pin6 = ctr1
            ci_chan4 = system.devices[self.ci_slot].ci_physical_chans[3].name # Pin8 = ctr3
            
            # configure ci_task1
            self.task_list[0].ci_channels.add_ci_count_edges_chan(
                    counter=ci_chan1,
                    name_to_assign_to_channel="",
                    edge=nidaqmx.constants.Edge.RISING,
                    initial_count=0)
           
            # configure ci_task2
            self.task_list[1].ci_channels.add_ci_count_edges_chan(
                    counter=ci_chan2,
                    name_to_assign_to_channel="",
                    edge=nidaqmx.constants.Edge.RISING,
                    initial_count=0)
            
            # configure ci_task3
            self.task_list[2].ci_channels.add_ci_count_edges_chan(
                    counter=ci_chan3,
                    name_to_assign_to_channel="",
                    edge=nidaqmx.constants.Edge.RISING,
                    initial_count=0)
            
            # configure ci_task4
            self.task_list[3].ci_channels.add_ci_count_edges_chan(
                    counter=ci_chan4,
                    name_to_assign_to_channel="",
                    edge=nidaqmx.constants.Edge.RISING,
                    initial_count=0)

            # Initialize counter tasks
            for i in range(0, 4):
                self.task_list[i].start()
        else:
            print("Unable to connect to digital input module NI-9411")

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #               Class Methods for Reading Data from Modules
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~ Class method for reading data from ni 9411 module ~~~~~~~~~~~~~~~~~~~
    def read_ci_data(self):
        data = []
        if self.ci_slot is not None:
            data.insert(0, self.task_list[0].ci_channels[0].ci_count) # ci_task1
            data.insert(1, self.task_list[1].ci_channels[0].ci_count) # ci_task2
            data.insert(2, self.task_list[2].ci_channels[0].ci_count) # ci_task3
            data.insert(3, self.task_list[3].ci_channels[0].ci_count) # ci_task4
        else:
            data.extend([0,0,0,0])
        return data
    #~~~~ Class method for reading data from ni 9214 module ~~~~~~~~~~~~~~~~~~~
    def read_tc_data(self):
        data = []
        if self.four_chan == True: 
            for i in range(5, len(self.task_list)):
                if self.task_list[i] is not None: 
                    data.extend(self.task_list[i].read())
                    data = data + [0]*(16-len(data))
        else:
            for i in range(5, len(self.task_list)):
                if self.task_list[i] is not None: data.extend(self.task_list[i].read())

        return data
    #~~~~ Class method for reading data from ni 9215 module ~~~~~~~~~~~~~~~~~~~
    def read_ai_data(self):
        data = []
        if self.ai_slot is not None:
            data.extend(self.task_list[4].read())
        else:
            data.extend([0,0])

        return data
    #~~~~ Class method for reading from all tasks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def read_all(self):
        data = []
        data.extend(self.read_ci_data()) # read counter data
        data.extend(self.read_ai_data()) # read analog input data
        data.extend(self.read_tc_data()) # read thermocouple data
        return data
    #~~~~ Class method for closing ni Tasks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def close_daq(self):
        # Close all running tasks in task_list
        try:
            for task in self.task_list:
                if task is not None: task.close()
        
        except Exception as e:
            print(e)
            return "No tasks to close." 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":
    
    import time
    # Print Devices in DAQ
    #task = nidaqmx.Task()
    # system = nidaqmx.system.System.local()
    #for device in system.devices:
    #    print(device.name)
    #print(len(system.devices))
    
    ni = NI()

    for task in ni.task_list:
        if task is not None: task.close()


