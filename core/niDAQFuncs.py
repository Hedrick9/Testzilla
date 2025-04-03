"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                 HEADER 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Title:       niDAQFuncs.py 
Origin Date: 04/28/2023
Revised:     04/02/2025
Author(s):   Russell Hedrick
Contact:     rhedrick@frontierenergy.com
Description:

The following script is designed to interface with the relevant ni modules 
using the nidaqmx library. When an NI class object is instantiated, it will 
detect the modules connected, and create tasks associated with each module.
Most setup and read tasks created are designed specifically for FSTC and CKV 
lab use.

"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                   Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np

import nidaqmx
import nidaqmx.system
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Create Task for each Device/Module
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NI:

    def __init__(self):
        self.task_dict = {} # list for all tasks that will be used for reading
        self.connected = False
        self.ci_slot = None # Flag for whether counter module is connected
        self.ai_volt_slot = None # Flag for whether anaolog voltage input module is connected
        self.ai_current_slot = None # Flag for whether anaolog current input module is connected
        self.ao_volt_slot = None # Flag for whether analog output voltage module is connected
        self.tc_modules = 0 # number of tc modules connected
        self.rtd_modules = 0 # number of rtd modules connected 
        self.four_chan = False
        self.system = nidaqmx.system.System.local()
    #~~~~~~ Identify whether modules are conencted ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for count, device in enumerate(self.system.devices):
            if device.product_type == "NI 9211":
                self.tc_modules += 1
                self.four_chan = True
                self.connected = True
            elif device.product_type == "NI 9214":
                self.tc_modules += 1
                self.connected = True
            elif device.product_type == "NI 9411":
                self.ci_slot = count # Check which slot ci module is in 
                self.connected = True
            elif device.product_type == "NI 9203":
                self.ai_current_slot = count # Check which slot ai current module is in 
                self.connected = True
            elif device.product_type == "NI 9215":
                self.ai_volt_slot = count # Check which slot ai voltage module is in 
                self.connected = True
            elif device.product_type == "NI 9264":
                self.ao_volt_slot = count # Check which slot ao voltage module is in 
                self.connected = True
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #               Class Methods for Reading Persisted Tasks from MAX
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    Read in persisted tasks that were created within ni MAX (Measurement &
    Automation Explorer).
    """ 
    def load_ptask(self, task_name):
        p_tasks = self.system.tasks.task_names
        try:    
            if task_name in p_tasks:
                p_task = nidaqmx.system.storage.persisted_task.PersistedTask(task_name)
                task = p_task.load()
                task.start()
                task.read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
                self.task_dict[task_name] = task
            else:
                print(f"Unable to load persisted task from ni MAX: {task_name}")
                task = None
                self.task_dict[task_name] = task
        except Exception as e:
            print(f"Unable to load persisted task from ni MAX: {task_name}")
            task = None
            self.task_dict[task_name] = task
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #               Class Methods for Setting Up Tasks for NI Modules
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    Configure specific tasks such as counters. These methods are done for 
    all tasks not created through ni MAX. 
    """ 
    #~~~~ Class method for setting up NI-9203 Analog Input Current Module ~~~~~
    def setup_ai_current(self):
        # Configure NI-9203 analog input current module if connected 
        if self.ai_current_slot is not None:
            # Channel Names
            aic_chan0 = self.system.devices[self.ai_current_slot].ai_physical_chans[0].name # AI0
            aic_chan1 = self.system.devices[self.ai_current_slot].ai_physical_chans[1].name # AI1
            aic_chan2 = self.system.devices[self.ai_current_slot].ai_physical_chans[2].name # AI2
            aic_chan3 = self.system.devices[self.ai_current_slot].ai_physical_chans[3].name # AI3
            aic_chan4 = self.system.devices[self.ai_current_slot].ai_physical_chans[4].name # AI4
            aic_chan5 = self.system.devices[self.ai_current_slot].ai_physical_chans[5].name # AI5
            aic_chan6 = self.system.devices[self.ai_current_slot].ai_physical_chans[6].name # AI6
            aic_chan7 = self.system.devices[self.ai_current_slot].ai_physical_chans[7].name # AI7

            aic_task1 = nidaqmx.Task() # Analog Input Current task 1 (Other) 
            # aic_task2 = nidaqmx.Task() # Analog Input Current task 2 (Other) - Uncomment to add task
            # configure analog output tasks
            aic_task1.ai_channels.add_ai_current_chan(aic_chan0, min_val=0.0, max_val=0.02)
            aic_task1.ai_channels.add_ai_current_chan(aic_chan1, min_val=0.0, max_val=0.02)
            aic_task1.ai_channels.add_ai_current_chan(aic_chan2, min_val=0.0, max_val=0.02)
            aic_task1.ai_channels.add_ai_current_chan(aic_chan3, min_val=0.0, max_val=0.02)
            aic_task1.ai_channels.add_ai_current_chan(aic_chan4, min_val=0.0, max_val=0.02)
            aic_task1.ai_channels.add_ai_current_chan(aic_chan5, min_val=0.0, max_val=0.02)
            aic_task1.ai_channels.add_ai_current_chan(aic_chan6, min_val=0.0, max_val=0.02)
            aic_task1.ai_channels.add_ai_current_chan(aic_chan7, min_val=0.0, max_val=0.02)
            # add configured tasks to task_dict for future calls
            self.task_dict["aic_task1"] = aic_task1
            # self.task_dict["aic_task2"] = aic_task2
        else:
            print("Unable to connect to analog current input module NI-9203")
    #~~~~ Class method for setting up NI-9215 Analog Input Voltage Module ~~~~~
    def setup_ai_volt(self):
        # Configure NI-9215 analog voltage input module if connected 
        if self.ai_volt_slot is not None:
            # Channel Names
            aiv_chan0 = self.system.devices[self.ai_volt_slot].ai_physical_chans[0].name # AI0
            aiv_chan1 = self.system.devices[self.ai_volt_slot].ai_physical_chans[1].name # AI1
            aiv_chan2 = self.system.devices[self.ai_volt_slot].ai_physical_chans[2].name # AI2
            aiv_chan3 = self.system.devices[self.ai_volt_slot].ai_physical_chans[3].name # AI3

            aiv_task1 = nidaqmx.Task() # Analog Input Voltage task 1 (Other)
            # aiv_task2 = nidaqmx.Task() # Analog Input Voltage task 2 (Other) - Uncomment to add task
            # configure analog output tasks
            aiv_task1.ai_channels.add_ai_voltage_chan(
                    aiv_chan0, 
                    terminal_config=nidaqmx.constants.TerminalConfiguration(10106), 
                    min_val=0.0, 
                    max_val=10.0) # Differential Reading = 10106
            aiv_task1.ai_channels.add_ai_voltage_chan(
                    aiv_chan1, 
                    terminal_config=nidaqmx.constants.TerminalConfiguration(10106), 
                    min_val=0.0, 
                    max_val=10.0) # Differential Reading = 10106
            aiv_task1.ai_channels.add_ai_voltage_chan(
                    aiv_chan2, 
                    terminal_config=nidaqmx.constants.TerminalConfiguration(10106), 
                    min_val=0.0, 
                    max_val=10.0)  # Differential Reading = 10106
            aiv_task1.ai_channels.add_ai_voltage_chan(
                    aiv_chan3, 
                    terminal_config=nidaqmx.constants.TerminalConfiguration(10106), 
                    min_val=0.0, 
                    max_val=10.0)  # Differential Reading = 10106
            # add configured tasks to task_dict for future calls
            self.task_dict["aiv_task1"] = aiv_task1
            # self.task_dict["aiv_task2"] = aiv_task2
        else:
            print("Unable to connect to analog voltage input module NI-9215")
    #~~~~ Class method for setting up NI-9264 Analog Voltage Output Module ~~~~
    def setup_ao_volt(self):
        # Configure NI-9264 analog output voltage module if connected 
        if self.ao_volt_slot is not None:
            # Channel Names
            ao_chan0 = self.system.devices[self.ao_volt_slot].ao_physical_chans[0].name # AO0
            ao_chan1 = self.system.devices[self.ao_volt_slot].ao_physical_chans[1].name # AO1
            ao_chan2 = self.system.devices[self.ao_volt_slot].ao_physical_chans[2].name # AO2
            ao_chan3 = self.system.devices[self.ao_volt_slot].ao_physical_chans[3].name # AO3
            ao_chan4 = self.system.devices[self.ao_volt_slot].ao_physical_chans[4].name # AO4

            ao_task1 = nidaqmx.Task() # Analog Output task 1 (Exhaust 1)
            ao_task2 = nidaqmx.Task() # Analog Output task 2 (Exhaust 2)
            ao_task3 = nidaqmx.Task() # Analog Output task 3 (Main Supply)
            ao_task4 = nidaqmx.Task() # Analog Output task 4 (LMUA-damper)
            ao_task5 = nidaqmx.Task() # Analog Output task 5 (Other)
            # configure analog output tasks
            ao_task1.ao_channels.add_ao_voltage_chan(ao_chan0, min_val=0.0, max_val=10.0)
            ao_task2.ao_channels.add_ao_voltage_chan(ao_chan1, min_val=0.0, max_val=10.0)
            ao_task3.ao_channels.add_ao_voltage_chan(ao_chan2, min_val=0.0, max_val=10.0)
            ao_task4.ao_channels.add_ao_voltage_chan(ao_chan3, min_val=0.0, max_val=10.0)
            ao_task5.ao_channels.add_ao_voltage_chan(ao_chan4, min_val=0.0, max_val=10.0)
            # add configured tasks to task_dict for future calls
            self.task_dict["ao_task1"] = ao_task1
            self.task_dict["ao_task2"] = ao_task2
            self.task_dict["ao_task3"] = ao_task3
            self.task_dict["ao_task4"] = ao_task4
            self.task_dict["ao_task5"] = ao_task5
        else:
            print("Unable to connect to analog voltage output module NI-9264")

    #~~~~ Class method for setting up NI-9411 Digital Counter Input Module ~~~~
    def setup_ci(self):
        # Configure NI-9411 digital input channel for pulse counting
        """
        The NI-9411 Digital Input Module must have a unique task created for each 
        counter. Therefore 4 tasks are created for each channel read unlike other 
        input models where multiple channel reads can be done on one task.
        """
        if self.ci_slot is not None:
            # Channel Names 
            ci_chan1 = self.system.devices[self.ci_slot].ci_physical_chans[0].name # Pin1 = ctr0
            ci_chan2 = self.system.devices[self.ci_slot].ci_physical_chans[2].name # Pin3 = ctr2
            ci_chan3 = self.system.devices[self.ci_slot].ci_physical_chans[1].name # Pin6 = ctr1
            ci_chan4 = self.system.devices[self.ci_slot].ci_physical_chans[3].name # Pin8 = ctr3

            ci_task1 = nidaqmx.Task() # Counter task 1 (Energy)
            ci_task2 = nidaqmx.Task() # Counter task 2 (Gas)
            ci_task3 = nidaqmx.Task() # Counter task 3 (Water)
            ci_task4 = nidaqmx.Task() # Counter task 4 (Extra)
            # configure ci_task1
            ci_task1.ci_channels.add_ci_count_edges_chan(
                    counter=ci_chan1,
                    name_to_assign_to_channel="",
                    edge=nidaqmx.constants.Edge.FALLING,
                    initial_count=0)
            # configure ci_task2
            ci_task2.ci_channels.add_ci_count_edges_chan(
                    counter=ci_chan2,
                    name_to_assign_to_channel="",
                    edge=nidaqmx.constants.Edge.FALLING,
                    initial_count=0)
            # configure ci_task3
            ci_task3.ci_channels.add_ci_count_edges_chan(
                    counter=ci_chan3,
                    name_to_assign_to_channel="",
                    edge=nidaqmx.constants.Edge.FALLING,
                    initial_count=0)
            # configure ci_task4
            ci_task4.ci_channels.add_ci_count_edges_chan(
                    counter=ci_chan4,
                    name_to_assign_to_channel="",
                    edge=nidaqmx.constants.Edge.FALLING,
                    initial_count=0)
            # add configured tasks to task_dict for future calls
            self.task_dict["ci_task1"] = ci_task1
            self.task_dict["ci_task2"] = ci_task2
            self.task_dict["ci_task3"] = ci_task3
            self.task_dict["ci_task4"] = ci_task4
            # Initialize counter tasks
            for i in range(1, 5):
                self.task_dict[f"ci_task{i}"].start()
        else:
            print("Unable to connect to digital input module NI-9411")

    #~~ Class method for setting up NI-9214/NI-9211 Thermocouple Input Module ~
    def setup_tc(self):
        if self.tc_modules > 0 and self.four_chan == True:
            tc_task1 = nidaqmx.Task() 
            for channel in self.system.devices[self.tc_modules].ai_physical_chans:
                tc_task1.ai_channels.add_ai_thrmcpl_chan(channel.name,
                       units=nidaqmx.constants.TemperatureUnits.DEG_F,
                       thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                       cjc_source=nidaqmx.constants.CJCSource.BUILT_IN)
            tc_task1.timing.cfg_samp_clk_timing(
                    rate=1000,
                    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                    samps_per_chan=1)
            tc_task1.start()
            tc_task1.read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
            self.task_dict["tc_task1"] = tc_task1
        elif self.tc_modules == 1 and self.four_chan == False:
            tc_task1 = nidaqmx.Task() 
            for channel in self.system.devices[1].ai_physical_chans:
                tc_task1.ai_channels.add_ai_thrmcpl_chan(channel.name,
                       units=nidaqmx.constants.TemperatureUnits.DEG_F,
                       thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                       cjc_source=nidaqmx.constants.CJCSource.BUILT_IN)
            tc_task1.timing.cfg_samp_clk_timing(
                    rate=1000,
                    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                    samps_per_chan=1)
            tc_task1.start()
            tc_task1.read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
            self.task_dict["tc_task1"] = tc_task1
        elif self.tc_modules == 2 and self.four_chan == False:
            tc_task1 = nidaqmx.Task()
            for channel in self.system.devices[1].ai_physical_chans:
                if channel.name.split('/')[1] == "ai0":
                    tc_task1.ai_channels.add_ai_thrmcpl_chan(channel.name,
                       units=nidaqmx.constants.TemperatureUnits.DEG_F,
                       thermocouple_type=nidaqmx.constants.ThermocoupleType.T,
                       cjc_source=nidaqmx.constants.CJCSource.BUILT_IN)
                else:
                    tc_task1.ai_channels.add_ai_thrmcpl_chan(channel.name,
                       units=nidaqmx.constants.TemperatureUnits.DEG_F,
                       thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                       cjc_source=nidaqmx.constants.CJCSource.BUILT_IN)
            tc_task2 = nidaqmx.Task()
            for channel in self.system.devices[2].ai_physical_chans:
                tc_task2.ai_channels.add_ai_thrmcpl_chan(channel.name,
                    units=nidaqmx.constants.TemperatureUnits.DEG_F,
                    thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                    cjc_source=nidaqmx.constants.CJCSource.BUILT_IN)
            tc_task1.timing.cfg_samp_clk_timing(
                    rate=1000,
                    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                    samps_per_chan=1)
            tc_task1.start()
            tc_task1.read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
            tc_task2.timing.cfg_samp_clk_timing(
                    rate=1000,
                    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                    samps_per_chan=1)
            tc_task2.start()
            tc_task2.read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
            self.task_dict["tc_task1"] = tc_task1
            self.task_dict["tc_task2"] = tc_task2
        else:
           print("Unable to connect to thermocouple module NI-9214")
    #~~ Setup all modules relevant to Testzilla program 
    def setup_testzilla(self):
        print("Initializing Testzilla setup...")
        # Uncomment below for loading Persisted Tasks
        # self.load_ptask("tc_task1")
        # self.load_ptask("tc_task2")
        self.setup_tc()
        self.setup_ci()
        if self.ai_volt_slot is not None:
            self.setup_ai_volt()
        elif self.ai_current_slot is not None:
            self.setup_ai_current()
        else: print("Unable to connect to analog voltage input module NI-9215")
        # self.setup_tc()
    #~~ Setup all modules relevant to CKV program 
    def setup_ckv(self):
        self.setup_tc()
        self.setup_ci()
        self.setup_ai_volt()
        self.setup_ai_current()
        self.setup_ao_volt()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #               Class Methods for Reading Data from Modules
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~ Class method for reading data from ni 9411 module ~~~~~~~~~~~~~~~~~~~
    def read_ci_data(self):
        data = []
        if self.ci_slot is not None:
            data.insert(0, self.task_dict["ci_task1"].ci_channels[0].ci_count) # ci_task1
            data.insert(1, self.task_dict["ci_task2"].ci_channels[0].ci_count) # ci_task2
            data.insert(2, self.task_dict["ci_task3"].ci_channels[0].ci_count) # ci_task3
            data.insert(3, self.task_dict["ci_task4"].ci_channels[0].ci_count) # ci_task4
        else:
            data.extend([0,0,0,0])
        return data
    #~~~~ Class method for reading on-demand data from ni 9214 module ~~~~~~~~~
    def read_tc_data(self):
        data = []
        if self.four_chan == True: 
            data.extend(self.task_dict["tc_task1"].read())
            data = data + [0]*(16-len(data))
        elif self.tc_modules == 1 and self.four_chan == False:
            data.extend(self.task_dict["tc_task1"].read())
        elif self.tc_modules == 2:
            data.extend(self.task_dict["tc_task1"].read())
            data.extend(self.task_dict["tc_task2"].read())
        else:
            data.extend([0]*16)
        return data
    #~~~~ Class method for reading continuous data from ni 9214 module ~~~~~~~~
    def read_tc_data_continuous(self):
        data = []
        if self.four_chan == True: 
            raw = self.task_dict["tc_task1"].read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
            data = np.array(raw, dtype=float).mean(axis=1).tolist()
            data = data + [0]*(16-len(data))
        elif self.tc_modules == 1 and self.four_chan == False:
            raw = self.task_dict["tc_task1"].read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
            data = np.array(raw, dtype=float).mean(axis=1).tolist()
        elif self.tc_modules == 2:
            raw1 = self.task_dict["tc_task1"].read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
            raw2 = self.task_dict["tc_task2"].read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
            data = np.array(raw1, dtype=float).mean(axis=1).tolist()
            data2 = np.array(raw2, dtype=float).mean(axis=1).tolist()
            data.extend(data2)
        else:
            data.extend([0]*16)
        return data

    #~~~~ Class method for reading data from NI-9226 module ~~~~~~~~~~~~~~~~~~~
    def read_rtd_data(self):
        data = []
        if self.rtd_modules > 0:
            pass 
        else:
            data.extend([0]*24)
        return data 
    #~~~~ Class method for reading data from NI-9215 module ~~~~~~~~~~~~~~~~~~~
    def read_ai_volt_data(self):
        data = []
        if self.ai_volt_slot is not None: 
            data.extend(self.task_dict["aiv_task1"].read())
        else:
            data.extend([0,0,0,0])

        return data
    #~~~~ Class method for reading data from NI-9203 module ~~~~~~~~~~~~~~~~~~~
    def read_ai_current_data(self):
        data = []
        if self.ai_current_slot is not None:
            data.extend(self.task_dict["aic_task1"].read())
        else:
            data.extend([0,0,0,0,0,0,0,0])
        return data
    #~~~~ Class method for reading from all tasks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def read_all_ckv(self):
        data = []
        data.extend(self.read_ci_data()) # read counter data
        data.extend(self.read_ai_volt_data()) # read analog input data
        data.extend(self.read_ai_current_data()) # read analog input data
        # data.extend(self.read_rtd_data()) # read rtd data 
        data.extend(self.read_tc_data()) # read thermocouple data
        return data
    #~~~~ Class method for reading from all tasks relevant to Testzilla ~~~~~~~
    def read_all_tz(self):
        data = []
        data.extend(self.read_ci_data()) # read counter data
        if self.ai_volt_slot is not None: 
            data.extend(self.read_ai_volt_data()[:2]) # read analog input data
        elif self.ai_current_slot is not None:
            data.extend(self.read_ai_current_data()[:2])
        else: data.extend([0,0])
        data.extend(self.read_tc_data_continuous()) # read thermocouple data
        return data
    #~~~~ Class method for writing to NI-9264 tasks ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def write_ao_volt(self, channel, voltage):
        if self.ao_volt_slot is not None:
            self.task_dict[f"ao_task{channel+1}"].write(voltage)
        else: print("Could not write to NI-9264 Analog Voltage Output Module")
    #~~~~ Class method for closing ni Tasks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def close_daq(self):
        # Close all running tasks in task_list
        try:
            for task in self.task_dict:
                if self.task_dict[task] is not None: self.task_dict[task].close()
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
    ni.setup_testzilla()
    # ni.write_ao_volt(0, 0)
#    raw_data = ni.task_dict["tc_task1"].read(number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE)
    print(ni.connected)
    ni.close_daq()



