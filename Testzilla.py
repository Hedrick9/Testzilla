#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           IMPORTS/Libraries 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import core.UI as UI
import core.file_utils as fu
import core.niDAQFuncs as ni 
import core.modbusFuncs as mb
import pandas as pd
import numpy as np
import time
import threading
from datetime import date, datetime, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import QIcon
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Classes & Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Class for handling timing events
class TestTime:

    def __init__(self, timing_interval=1):
        self.initial_clock_time = time.time()
        self.clock_time = 0
        self.test_time = 0
        self.test_time_min = 0
        self.timing_interval = timing_interval # sample every n seconds
        self.current_index = 0
        self.testing = False
        self.time_to_write = False

    def update_time(self):
        self.clock_time = time.time() - self.initial_clock_time
        self.test_time += 1
        self.current_index += 1
        if self.clock_time - self.test_time > 1:
            self.test_time += 1
        if self.test_time % self.timing_interval == 0:
            self.time_to_write = True
            self.test_time_min = round(self.test_time/60, 2)
        else:
            self.time_to_write = False

    def reset(self):
        self.initial_clock_time = time.time()
        self.clock_time = 0
        self.test_time = 0
        self.test_time_min = 0
        self.current_index = 0

#~~~~~~~~~ Get Data and Handle Data Related Actions ~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Data:

    def __init__(self):
        self.ni_daq = ni.NI()
        self.tc_modules = self.ni_daq.tc_modules
        self.ni_data = [None]*22
        self.mb_data = [[0]*13]
        self.data_log = []
        self.data_to_write = None
        self.stream = False
        self.last_pulse_data = [0, 0, 0, 0]
        self.pcfs = [1,0.1, 1, 1] # pcfs = pulse conversion factors
        self.pulse_data = [0, 0, 0, 0]
        self.pulse_reset = [0, 0, 0, 0]

    def update_ni_data(self):
        self.ni_data = self.ni_daq.read_all()

    def read_ni_data(self):
        return self.ni_data

    def ni_stream(self):
        while self.stream == True:
            self.update_ni_data()

    def get_data(self, test_time):
        tod = datetime.now().strftime("%H:%M:%S")
        time_data = [tod, test_time.test_time_min]
        # Try to read in data from ni hardware; otherwise return list of 0's
        if self.tc_modules > 0:
            ni_data = list(np.around(np.array(self.ni_data),2))
            data = self.mb_data[0][:3] + \
            list(np.multiply(self.pcfs, np.array(ni_data[:4])-np.array(self.pulse_reset))) + \
            [None if x > 3500 else x for x in ni_data[4:]] # replace pulse_reset with last_pulse_data for interval pulses
            self.data_log.append(time_data.copy()+data)
            self.pulse_data = list(np.array(ni_data[:4])-np.array(self.last_pulse_data))
            self.last_pulse_data = ni_data[:4]
        else:
            status.append("error reading from ni-DAQ")
            data = list(np.zeros(25))
            self.data_log.append(time_data.copy()+data)
        if test_time.timing_interval == 1: self.data_to_write = time_data.copy() + data.copy()
        else:
            average_data = pd.DataFrame(self.data_log[-test_time.timing_interval:].copy()).drop(columns=[0,1,4,5,6,7,8]).mean()
            _write = [*average_data[0:2], *self.data_log[-1][4:9], *average_data[2:]]
            self.data_to_write = time_data.copy() + [None if np.isnan(item) else round(item,2) for item in _write]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            Startup Application
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    # system status record
    status = []
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            Initialize DAQ(s)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Initializes Data object and begin ni DAQ processes
    data = Data()
    # Initialize modbus client connection and start reading modbus data
    try:
        client = mb.init(port="COM4")
        mb.write_(client, 20000, 5555) # reset energy accumulators    
        thread = threading.Thread(target=mb.data_stream, args=(client, data.mb_data,), daemon=True)
        thread.start()
    except Exception as e:
        status.append("Unable to connect to modbus device.")
        print("Unable to connect to modbus device.")
        data.mb_data = [list(np.zeros(13))]

 #~~~~~~~ ONLY USE SECTION BELOW FOR 4 CHANNEL TC MODULE ~~~~~~~~~~~~~~~~~~~~~~~
    data.stream = True
    try:
        thread = threading.Thread(target=data.ni_stream, args=(), daemon=True)
        thread.start()
    except Exception as e:
        print("Unable to connect to ni DAQ.")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                Initialize Application and Start Event Loop
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    try:
        test_time = TestTime(1) # Initialize timing object with 1 second timing_interval
        # Create a QTimer for event loop
        timer = QTimer() 
        timer.setTimerType(Qt.PreciseTimer)
        # Create PySide application object
        app = QApplication()
        app.setWindowIcon(QIcon("photos/tz-icon.png")) 
        mw = UI.MainWindow(data, test_time, status, timer)
        # Show the application and start the PySide6 event loop
        mw.show()
        # Create Data directory if it does not exist
        fu.create_directory()
        # Create new CSV Test File
        fu.file_setup(test_time.testing, data.tc_modules)
        status.append("Adding new file: {}".format(fu.file_name))
    #~~~~~~ Timing Sequence ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        timer.start(1000)
        # timer event executions
        timer.timeout.connect(test_time.update_time)
        # timer.timeout.connect(data.update_ni_data)
        timer.timeout.connect(lambda: data.get_data(test_time))
        timer.timeout.connect(lambda: mw.update_plot(data.data_log))
        timer.timeout.connect(lambda: mw.data_window.update_data(data, test_time))
        timer.timeout.connect(lambda: mw.update_values(data, test_time))
        timer.timeout.connect(lambda: mw.update_system_status(status[-1]))
        timer.timeout.connect(lambda: fu.write_data(data.data_to_write, test_time.testing, test_time.time_to_write))
        timer.timeout.connect(mw.data_window.retrieve_model_data)

        app.exec()
    except KeyboardInterrupt:
        print("Programa Terminado.")
    except Exception as e:
        print(e)

    finally:
        data.ni_daq.close_daq()

