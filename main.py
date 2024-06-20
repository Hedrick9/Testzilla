#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                  IMPORTS/Libraries used for program and UI 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import file_utils as fu
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta
import threading
import niDAQFuncs as ni
import modbusFuncs as mb
from PySide6.QtCore import QTime, QTimer, Qt 
from PySide6.QtGui import (QIcon, QAction, QStandardItemModel, QStandardItem, 
        QFont, QPixmap)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
        QHBoxLayout, QPushButton, QListWidget, QLabel, QLineEdit, QComboBox,
        QStatusBar, QFrame, QTableView, QDialog, QMenu, QSpacerItem, QSizePolicy)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            START OF PROGRAM
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Status Updates from System
status = []
testing = False # Test Status
current_index = 0
# Color Palette
PRIMARY_COLOR = "#000000" 
SECONDARY_COLOR = "#0f0f0f"
TRI_COLOR = "#121212"  
BUTTON_COLOR = "#1f1f1f" 
FONT_COLOR1 = "#ffffff"
# FONT_STYLE = "Helvetica" "Courier New" "Bahnschrift"
FONT_STYLE = "Bahnschrift"
start_time = QTime.currentTime()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            Initialize DAQ(s)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Initializes ni DAQ and returns number of tc modules available
ni_daq = ni.NI()
tc_modules = ni_daq.tc_modules
# Initialize modbus client connection and start reading modbus data
try:
    client = mb.init(port="COM3")
    mb.write_(client, 20000, 5555) # reset energy accumulators    
    mb_data = []
    thread = threading.Thread(target=mb.data_stream, args=(client, mb_data,), daemon=True)
    thread.start()
except Exception as e:
    status.append("Unable to connect to modbus device.")
    print("Unable to connect to modbus device.")
    mb_data = [list(np.zeros(13))]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define relevant functions prior to their call
class TestTime:

    def __init__(self, timing_interval=1):
        self.initial_clock_time = time.time()
        self.clock_time = 0
        self.test_time = 0
        self.test_time_min = 0
        self.timing_interval = timing_interval # sample every n seconds
        self.time_to_write = False

    def update_time(self):
        self.clock_time = time.time() - self.initial_clock_time
        self.test_time += 1
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

ni_data = None
data_log = []
data_to_write = None
last_pulse_data = [0, 0, 0, 0]
pulse_data = [0, 0, 0, 0]
pulse_reset = [0, 0, 0, 0]
def get_data(pcfs=[1, .05, 1, 1]): # pcfs = pulse conversion factors
    global data_to_write
    global last_pulse_data
    global pulse_data
    global pulse_reset
    global ni_data
    global mb_data
    tod = datetime.now().strftime("%H:%M:%S")
    time_data = [tod, test_time.test_time_min]
    # Try to read in data from ni hardware; otherwise return list of 0's
    if tc_modules > 0:
        # ni_data = list(np.around(np.array(ni.read_daq()),1))
        ni_data = list(np.around(np.array(ni_daq.read_all()),2))
        data = mb_data[0][:3] + \
        list(np.multiply(pcfs, np.array(ni_data[:4])-np.array(pulse_reset))) + \
        [None if x > 3500 else x for x in ni_data[4:]] # replace pulse_reset with last_pulse_data for interval pulses
        data_log.append(time_data.copy()+data)
        pulse_data = list(np.array(ni_data[:4])-np.array(last_pulse_data))
        last_pulse_data = ni_data[:4]
    else:
        status.append("error reading from ni-DAQ")
        data = list(np.zeros(25))
        data_log.append(time_data.copy()+data)
    if test_time.timing_interval == 1: data_to_write = time_data.copy() + data.copy()
    else:
        average_data = pd.DataFrame(data_log[-test_time.timing_interval:].copy()).drop(columns=[0,1,4,5,6,7,8]).mean()
        _write = [*average_data[0:2], *data_log[-1][4:9], *average_data[2:]]
        data_to_write = time_data.copy() + [None if np.isnan(item) else round(item,2) for item in _write]

#~~~~~~~~~~~~~~~~~~~~~~ Update Plot Function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def update_plot():
    # Update the plot with new data
    df = pd.DataFrame(data_log)
    # Create list of tc channels to graph    
    if graph_menu is not None:
        tc_list_ = [tc.text() for tc in graph_menu.actions() if tc.isCheckable() and tc.isChecked()]
        tc_list = [int(name.split()[1]) for name in tc_list_]
        while len(tc_list) > 11:
            tc_list.remove(tc_list[-1])
    
    # Graph tc channels in list
    if len(data_log) < 3600 and len(tc_list)>0:
        ax.clear()
        for item in tc_list:
            ax.plot(df[item+11], label=str(item), lw=0.5)
    elif len(data_log) >= 3600 and len(tc_list)>0:
        ax.clear()
        for item in tc_list:
            ax.plot(df[item+11][-3600:-1], label=str(item), lw=0.5)
    # Graph tc channel 0 if none selected
    else:
        if len(df) < 3600:
            ax.clear()
            ax.plot(df[11], label="ambient", lw=0.5)
        else:
            ax.clear()
            ax.plot(df[11][-3600:-1], label="ambient", lw=0.5)
    
    # Format Plot   
    if graph_window is not None:
        try:
            ax.set_ylim([graph_range[-1][1], graph_range[-1][0]])
        except Exception as e:
            pass
    else: 
        ax.set_ylim([None, None])
    ax.legend(loc='lower right', frameon=False, ncol=3, labelcolor=FONT_COLOR1)
    ax.set_facecolor(TRI_COLOR)
    ax.tick_params(labelbottom=False, labelcolor=FONT_COLOR1, color="#ffffff", labelsize=8)
    ax.minorticks_on()
    #ax.spines[:].set_visible(False)#set_color("#ffffff")
    ax.spines[:].set_color("#2b2b2a")
    ax.spines[:].set_linewidth(0.25)
    ax.grid(which='major', linewidth=0.3, color="#03fcd3") #22ffff
    ax.grid(which='minor', linewidth=0.1, color="#03fcd3") 
    canvas.draw() # update plot

#~~~~~~~~~ Slot function for handling status update in status bar ~~~~~~~~~~~~~
def update_system_status(status):
     
    system_status_label.setText(status)

#~~~~~~~~~ Slot function for handling start button click event ~~~~~~~~~~~~~~~~
def start_test():
    global testing
    global start_time
    global data_log
    global pulse_data
    global pulse_reset
    global status_indicator
    global current_index
    testing = True
    data_log = []
    current_index=0
    pulse_reset = pulse_data
    status.append("testing in progress...")
    status_indicator.setStyleSheet("background-color: #225c40; font: 12px; \
        color: #ffffff; font-weight: bold;")
    status_indicator.setText("Recording")
    test_file_label.setText(f"File Name: {fu.file_name}")
    start_time = QTime.currentTime()
    test_time.reset()
    data_to_write[1] = 0.0 # resets the clock and writes a t0 timestamp 
    fu.write_data(data_to_write, testing, True)
    timer.start(1000)  # Start the timer to update the plot every 1000 milliseconds (1 second)

#~~~~~~~~~ Slot function for handling stop button click event ~~~~~~~~~~~~~~~~~
def stop_test():
    global testing
    global status_indicator
    testing = False
    timer.stop()  # Stop the timer to stop updating the plot
    status.append("testing concluded.")
    update_system_status(status[-1])
    status_indicator.setStyleSheet("background-color: #b8494d; font: 12px; \
        color: #ffffff; font-weight: bold;")
    status_indicator.setText("Not Recording")

#~~~~~~~~~ Slot function for handling reset button click event ~~~~~~~~~~~~~~~~
def reset_():
    global start_time
    global pulse_data
    global pulse_reset
    pulse_reset = pulse_data
    start_time = QTime.currentTime()
    test_time.reset()
    data_to_write[1] = 0.0 # resets the clock and writes a t0 timestamp 
    fu.write_data(data_to_write, testing, True)
    timer.start(1000)

#~~~~~~~~~~~~~~~~~ Function for Initial Data Window Display ~~~~~~~~~~~~~~~~~~~
data_window,tc_model,pulse_model,modbus_model,index_label,\
temp_avg_value_1a,temp_avg_value_1b,temp_avg_value_1c,\
temp_avg_value_2a,temp_avg_value_2b,temp_avg_value_2c,\
er_time_label,energy_rate_label,start_index_input,end_index_input,\
gcf_input,hhv_input,meter_selection = [None for item in range(18)]
def show_data_window():
    global data_window, tc_model, pulse_model, modbus_model, index_label, \
           temp_avg_value_1a, temp_avg_value_1b, temp_avg_value_1c, \
           temp_avg_value_2a, temp_avg_value_2b, temp_avg_value_2c, \
           er_time_label,energy_rate_label,start_index_input,end_index_input,\
           gcf_input,hhv_input,meter_selection
    # spacer item function to prevent program crash bug
    def spacer_():
        return QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed)

   # Create a window for data view
    data_window = QWidget()
    data_window.setWindowTitle("Data")
    data_window.setGeometry(1000, 100, 425, 800)
    data_window.setStyleSheet(f"background-color: {SECONDARY_COLOR};")
    
    layout = QVBoxLayout()
    layout.setSpacing(0)
    # Add a labels to the window
    label1 = QLabel("Temperatures (F):", data_window)
    label1.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
            font-family:{}; text-decoration: underline;".format(FONT_STYLE))
    
    label2 = QLabel("Pulse Data:", data_window)
    label2.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
            font-family:{}; text-decoration: underline;".format(FONT_STYLE))

    label3 = QLabel("Modbus Data:", data_window)
    label3.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
            font-family:{}; text-decoration: underline;".format(FONT_STYLE))


    label4 = QLabel("Analysis:", data_window)
    label4.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
            font-family:{}; text-decoration: underline;".format(FONT_STYLE))

    
#~~~~~ Section 1: Temperature Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    tc_model = QStandardItemModel(8, 4)
    for row in range(8):
        for column in range(4):
            index = (row)+(column*8)
            item = QStandardItem("Temp {}: NA".format(index))
            tc_model.setItem(row, column, item)
    table_view1 = QTableView()
    table_view1.horizontalHeader().setVisible(False)
    # table_view1.verticalHeader().setDefaultSectionSize(300)
    table_view1.verticalHeader().setVisible(False)
    table_view1.setFixedHeight(260)
    table_view1.setModel(tc_model)
    table_view1.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: #ffffff; font: 12px; font-family:{FONT_STYLE};"\
                          "border-style: solid; border-width: 0 1px 1px")
    
    # Temp Average
    temp_avg_layout1 = QHBoxLayout()
    label_1a = QLabel(" Average of Temps  ")
    label_1a.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
    temp_avg_layout1.addWidget(label_1a)
    temp_avg_value_1a = QLineEdit()
    temp_avg_value_1a.setStyleSheet("color: #ffffff; font: 14px; border:none;border-bottom:1px solid white;")
    temp_avg_layout1.addWidget(temp_avg_value_1a)
    label_1b = QLabel(" to ")
    label_1b.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
    temp_avg_layout1.addWidget(label_1b)
    temp_avg_value_1b = QLineEdit()
    temp_avg_value_1b.setStyleSheet("color: #ffffff; font: 14px; border: none; border-bottom:1px solid white;")
    temp_avg_layout1.addWidget(temp_avg_value_1b)
    temp_avg_value_1c = QLabel(" = NA")
    temp_avg_value_1c.setStyleSheet("color: #ffffff; font: 14px; font-weight:bold;")
    temp_avg_layout1.addWidget(temp_avg_value_1c)
    

    temp_avg_layout2 = QHBoxLayout()
    label_2a = QLabel(" Average of Temps  ")
    label_2a.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
    temp_avg_layout2.addWidget(label_2a)
    temp_avg_value_2a = QLineEdit()
    temp_avg_value_2a.setStyleSheet("color: #ffffff; font: 14px; border:none;border-bottom:1px solid white;")
    temp_avg_layout2.addWidget(temp_avg_value_2a)
    label_2b = QLabel(" to ")
    label_2b.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
    temp_avg_layout2.addWidget(label_2b)
    temp_avg_value_2b = QLineEdit()
    temp_avg_value_2b.setStyleSheet("color: #ffffff; font: 14px; border:none;border-bottom:1px solid white;")
    temp_avg_layout2.addWidget(temp_avg_value_2b)
    temp_avg_value_2c = QLabel(" = NA")
    temp_avg_value_2c.setStyleSheet("color: #ffffff; font: 14px; font-weight:bold;")
    temp_avg_layout2.addWidget(temp_avg_value_2c)

#~~~~~~ Section 2: Pulse and Other Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    pulse_model = QStandardItemModel(3, 4)
    item1 = QStandardItem("Electric Energy:")
    item2 = QStandardItem("Interval: NA")
    item3 = QStandardItem("Total: NA")
    item4 = QStandardItem("Gas Energy:")
    item5 = QStandardItem("Interval: NA")
    item6 = QStandardItem("Total: NA")
    item7 = QStandardItem("Water:")
    item8 = QStandardItem("Interval: NA")
    item9 = QStandardItem("Total: NA")
    item10 = QStandardItem("Extra:")
    item11 = QStandardItem("Interval: NA")
    item12 = QStandardItem("Total: NA")

    pulse_model.setItem(0, 0, item1)
    pulse_model.setItem(1, 0, item2)
    pulse_model.setItem(2, 0, item3) # electric total
    pulse_model.setItem(0, 1, item4)
    pulse_model.setItem(1, 1, item5)
    pulse_model.setItem(2, 1, item6) # gas total
    pulse_model.setItem(0, 2, item7)
    pulse_model.setItem(1, 2, item8) 
    pulse_model.setItem(2, 2, item9) # water total
    pulse_model.setItem(0, 3, item10)
    pulse_model.setItem(1, 3, item11)
    pulse_model.setItem(2, 3, item12) # extra total
    
    table_view2 = QTableView()
    table_view2.horizontalHeader().setVisible(False)
    table_view2.verticalHeader().setVisible(False)
    table_view2.setModel(pulse_model)
    table_view2.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: #ffffff; font: 12px;"\
            f"font-family:{FONT_STYLE}; border-style: solid; border-width: 0 1px 1px 1px;")

#~~~~~~ Section 3: Modbus Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    modbus_model = QStandardItemModel(4, 3)
    mb_item1 = QStandardItem("Avg. Voltage: NA")
    mb_item2 = QStandardItem("Watts: NA")
    mb_item3 = QStandardItem("Electric Energy: NA")
    mb_item4 = QStandardItem("V_AN: NA")
    mb_item5 = QStandardItem("V_BN: NA")
    mb_item6 = QStandardItem("V_CN: NA")
    mb_item7 = QStandardItem("V_AB: NA")
    mb_item8 = QStandardItem("V_BC: NA")
    mb_item9 = QStandardItem("V_AC: NA")
    mb_item10 = QStandardItem("I_A: NA")
    mb_item11 = QStandardItem("I_B: NA")
    mb_item12 = QStandardItem("I_C: NA")

    modbus_model.setItem(0, 0, mb_item1)
    modbus_model.setItem(0, 1, mb_item2)
    modbus_model.setItem(0, 2, mb_item3)
    modbus_model.setItem(1, 0, mb_item4)
    modbus_model.setItem(1, 1, mb_item5)
    modbus_model.setItem(1, 2, mb_item6)
    modbus_model.setItem(2, 0, mb_item7)
    modbus_model.setItem(2, 1, mb_item8)
    modbus_model.setItem(2, 2, mb_item9)
    modbus_model.setItem(3, 0, mb_item10)
    modbus_model.setItem(3, 1, mb_item11)
    modbus_model.setItem(3, 2, mb_item12)

    table_view3 = QTableView()
    table_view3.horizontalHeader().setVisible(False)
    table_view3.verticalHeader().setVisible(False)
    table_view3.setModel(modbus_model)
    table_view3.setStyleSheet(f"background-color: {SECONDARY_COLOR}; color: #ffffff; font: 12px;"\
            f"font-family:{FONT_STYLE}; border-style: solid; border-width: 0 1px 1px 1px;")
#~~~~~~ Section 4: Analysis ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    index_label = QLabel("Current Index = NA", data_window) 
    index_label.setStyleSheet("color: #ffffff; font: 14px; font-family:{};".format(FONT_STYLE))
    index_layout = QHBoxLayout()
    start_index_label = QLabel(" Start Index =  ")
    start_index_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
    index_layout.addWidget(start_index_label)
    start_index_input = QLineEdit()
    start_index_input.setStyleSheet("color: #ffffff; font: 14px; border:none;border-bottom: 1px solid white;")
    index_layout.addWidget(start_index_input)
    end_index_label = QLabel(" End Index = ")
    end_index_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
    index_layout.addWidget(end_index_label)
    end_index_input = QLineEdit()
    end_index_input.setStyleSheet("color: #ffffff; font: 14px; border:none;border-bottom: 1px solid white;")
    index_layout.addWidget(end_index_input)
     
    er_time_label = QLabel(" Start Time = NA     |     End Time = NA  ")
    er_time_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE};")
    
    meter_selection = QComboBox()
    meter_selection.setStyleSheet("color: #ffffff; font: 14px;")
    meter_selection.addItem("Gas Meter")
    meter_selection.addItem("120V Meter")
    meter_selection.addItem("208V Meter")
    # meter_selection.currentIndexChanged.connect(handle_meter_selection)

    energy_rate_layout = QHBoxLayout()
    hhv_label = QLabel(" HHV =            ")
    hhv_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
    energy_rate_layout.addWidget(hhv_label)
    hhv_input = QLineEdit("1")
    hhv_input.setStyleSheet("color: #ffffff; font: 14px; border:none;border-bottom: 1px solid white;")
    energy_rate_layout.addWidget(hhv_input)
    gcf_label = QLabel(" GCF =          ")
    gcf_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
    energy_rate_layout.addWidget(gcf_label)
    gcf_input = QLineEdit("1")
    gcf_input.setStyleSheet("color: #ffffff; font: 14px; border:none;border-bottom: 1px solid white;")
    energy_rate_layout.addWidget(gcf_input)
    
    energy_rate_label = QLabel(" Energy Rate = ")
    energy_rate_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE};")

#~~~~~~ Adjust Layout ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Organize structure of layout 
    layout.addWidget(label1)
    layout.addWidget(table_view1)
    layout.addLayout(temp_avg_layout1)
    layout.addLayout(temp_avg_layout2)
    layout.addWidget(label2)
    layout.addWidget(table_view2)
    layout.addWidget(label3)
    layout.addWidget(table_view3)
    layout.addWidget(label4)
    layout.addWidget(index_label)
    layout.addWidget(meter_selection)
    layout.addLayout(index_layout)
    layout.addItem(spacer_())
    layout.addWidget(er_time_label)
    layout.addLayout(energy_rate_layout)
    layout.addItem(spacer_())
    layout.addWidget(energy_rate_label)

    data_window.setLayout(layout)
    data_window.show()

#~~~~~~~~~~~~~~~~~~~~~~ Display Graph Window Function ~~~~~~~~~~~~~~~~~~~~~~~~~
def show_graph_window():
    # Create a window for graph configuration
    graph_menu.exec()

#~~~~~~~~~~~~~~~~~~~~~~~~ Display Graph Setup Window  ~~~~~~~~~~~~~~~~~~~~~~~~~
graph_window = None
graph_range = None
def set_graph_window():
    global graph_window
    global graph_range

    graph_window = QWidget()
    graph_window.setWindowTitle("Setup Graph")
    graph_window.setGeometry(400, 100, 350, 200)
    graph_window.setStyleSheet(f"background-color: {SECONDARY_COLOR};")

    graph_range = []
    
    layout = QVBoxLayout()
    layout.setSpacing(0)

    label1 = QLabel("Set Y Upper Bound")
    label1.setStyleSheet("color: #ffffff; font: 14px;")
    upper_bound_entry = QLineEdit()
    upper_bound_entry.setStyleSheet("color: #ffffff; font: 14px;")
    label2 = QLabel("Set Y Lower Bound")
    label2.setStyleSheet("color: #ffffff; font: 14px;")
    lower_bound_entry = QLineEdit()
    lower_bound_entry.setStyleSheet("color: #ffffff; font: 14px;")
    button_style =  "QPushButton {background-color: #2b2b2b; color: #ffffff;}" \
                "QPushButton:hover {background-color: #555555;}" \
                "QPushButton:pressed {background-color: #777777;}"
    set_button = QPushButton("Set Range")
    set_button.setStyleSheet(button_style)
    # set_button.clicked.connect(lambda: print(f"{upper_bound_entry.text()} and {lower_bound_entry.text()}"))
    set_button.clicked.connect(lambda: graph_range.append((int(upper_bound_entry.text()), int(lower_bound_entry.text()),)))

    layout.addWidget(label1)
    layout.addWidget(upper_bound_entry)
    layout.addWidget(label2)
    layout.addWidget(lower_bound_entry)
    layout.addWidget(set_button)

    graph_window.setLayout(layout)
    graph_window.show()
#~~~~~~~~~~~~~~~~~~~~~~~~ Display Config Setup Window  ~~~~~~~~~~~~~~~~~~~~~~~~
def handle_time_selection(index):
    time_dict = {0: 1, 1: 5, 2: 30, 3: 60}
    test_time.timing_interval = time_dict[index]

config_window = None
def set_config_window():
    global config_window

    config_window = QWidget()
    config_window.setWindowTitle("Test Configuration Setup")
    config_window.setGeometry(200, 200, 300, 200)
    config_window.setStyleSheet(f"background-color: {SECONDARY_COLOR};")
    
    layout = QVBoxLayout()
    layout.setSpacing(0)

    label1 = QLabel("Set Test Time Interval:")
    label1.setStyleSheet("color: #ffffff; font: 14px;")
    time_selection = QComboBox()
    time_selection.setStyleSheet("color: #ffffff; font: 14px;")
    time_selection.addItem("1 second")
    time_selection.addItem("5 seconds")
    time_selection.addItem("30 seconds")
    time_selection.addItem("1 minute")
    time_selection.currentIndexChanged.connect(handle_time_selection)
    layout.addWidget(label1)
    layout.addWidget(time_selection)

    config_window.setLayout(layout)
    config_window.show()


#~~~~~~~~~~~~~~~~~~~~~ Update Function for Data Window ~~~~~~~~~~~~~~~~~~~~~~~~
def update_data_window():
    global ni_data
    if tc_model is not None:
        # Update the values in the table 
        for row in range(8):
            if len(data_log[0]) > 30:
                for column in range(4):
                    index = (row)+(column*8)
                    tc_model.item(row, column).setText("Temp {}:    {}".format(index, data_log[-1][index+11]))
            else:
                for column in range(2):
                    index = (row)+(column*8)
                    tc_model.item(row, column).setText("Temp {}:    {}".format(index, data_log[-1][index+11]))

    
    if temp_avg_value_1a is not None:
        try:
            t1a = int(temp_avg_value_1a.text())
            t1b = int(temp_avg_value_1b.text())
            t1_l = ni_data[t1a+6:t1b+7]
            tavg1 = np.mean(np.array([value for value in t1_l if value < 4000]))
            temp_avg_value_1c.setText(" = {}".format(round(tavg1, 1)))
        except Exception as e:
            temp_avg_value_1c.setText(" = NA")

        try:
            t2a = int(temp_avg_value_2a.text())
            t2b = int(temp_avg_value_2b.text())
            t2_l = ni_data[t2a+6:t2b+7]
            tavg2 = np.mean(np.array([value for value in t2_l if value < 4000]))
            temp_avg_value_2c.setText(" = {}".format(round(tavg2, 1)))
        except Exception as e:
            temp_avg_value_2c.setText(" = NA")

    if pulse_model is not None:
        # Update the values in pulse table
        for i in range(4):
            pulse_model.item(1, i).setText(f"Interval: {pulse_data[i]:.2f}")
        for i in range(4):
            pulse_model.item(2, i).setText(f"Total: {data_log[-1][i+5]:.2f}")

    if modbus_model is not None:
        # Update the values in modbus table
        modbus_model.item(0, 0).setText(f"Avg. Voltage: {mb_data[0][0]}")
        modbus_model.item(0, 1).setText(f"Watts: {mb_data[0][1]}")
        modbus_model.item(0, 2).setText(f"Electrical Energy: {mb_data[0][2]}")
        modbus_model.item(1, 0).setText(f"V_AN: {mb_data[0][3]}")
        modbus_model.item(1, 1).setText(f"V_BN: {mb_data[0][4]}")
        modbus_model.item(1, 2).setText(f"V_CN: {mb_data[0][5]}")
        modbus_model.item(2, 0).setText(f"V_AB: {mb_data[0][6]}")
        modbus_model.item(2, 1).setText(f"V_BC: {mb_data[0][7]}")
        modbus_model.item(2, 2).setText(f"V_CA: {mb_data[0][8]}")
        modbus_model.item(3, 0).setText(f"I_A: {mb_data[0][9]}")
        modbus_model.item(3, 1).setText(f"I_B: {mb_data[0][10]}")
        modbus_model.item(3, 2).setText(f"I_C: {mb_data[0][11]}")

    if index_label is not None:
        index_label.setText("Current Index = {}".format(current_index))
        try:
            st_i = int(start_index_input.text())
            et_i = int(end_index_input.text())
            hhv = int(hhv_input.text())
            gcf = float(gcf_input.text())
            ti = data_log[st_i][1]
            tf = data_log[et_i][1]
            er_time_label.setText(f" Start Time = {ti}     |     End Time = {tf}")
            meter_ix = {"Gas Meter": 6, "120V Meter": 5, "208V Meter":4}[meter_selection.currentText()]
            er_calc = (data_log[et_i][meter_ix] - data_log[st_i][meter_ix])*hhv*gcf/((tf-ti)/60)
            energy_rate_label.setText(f" Energy Rate = {round(er_calc,1)}")
        except ValueError as e:
            pass
        except IndexError as e:
            pass

           
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                             Setup Main UI 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the PySide6 application instance
app = QApplication()

# Set the window icon
app.setWindowIcon(QIcon("photos/tz-icon.png")) 

# Create the main window for the application
main_window = QMainWindow()
main_window.setWindowTitle("Testzilla")
main_window.setGeometry(100, 100, 900, 800)
main_window.setStyleSheet(f"QMainWindow {{background-color: {PRIMARY_COLOR};border: 1px solid white;}}")

# Create central widget for main window to hold other widgets
central_widget = QWidget()
main_window.setCentralWidget(central_widget)

# Create a vertical layout for the widget
main_layout = QVBoxLayout(central_widget)
main_layout.setSpacing(0)

# Set the layout for the widget
main_window.setLayout(main_layout)

# Header Section
header_widget = QWidget()
header_widget.setMaximumHeight(135)
header_layout = QHBoxLayout(header_widget)
main_layout.addWidget(header_widget)

# Header Subsection 1: Logo
main_logo = QLabel()
main_logo.setPixmap(QPixmap("photos/fstc_logo2.png"))
header_layout.addWidget(main_logo)

# Header Subsection 2: Test Time
time_layout = QVBoxLayout()
time_label = QLabel("TEST TIME:")
time_label.setStyleSheet("color: #ffffff; font: 30px; font-weight: bold; \
            font-family:{};".format(FONT_STYLE))
time_label.setPixmap(QPixmap("photos/test_time1.png"))
time_label.setAlignment(Qt.AlignCenter)
time_layout.addWidget(time_label)
time_label_value = QLabel("0.0")
time_label_value.setStyleSheet("color: #ffffff; font: 30px; font-weight:bold;\
            font-family:{};".format(FONT_STYLE)) #  
time_label_value.setAlignment(Qt.AlignCenter)
time_layout.addWidget(time_label_value)
spacer_item = QSpacerItem(10, 60, QSizePolicy.Expanding, QSizePolicy.Fixed)
time_layout.addItem(spacer_item)
header_layout.addLayout(time_layout)

# Header Subsection 3: Status and Ambient Temp
status_layout = QVBoxLayout()
status_label = QLabel("Status:")
status_label.setStyleSheet("color: #ffffff; font: 25px; font-weight: bold; \
            font-family:{};".format(FONT_STYLE))
status_label.setPixmap(QPixmap("photos/status1.png"))
status_label.setAlignment(Qt.AlignCenter)
status_layout.addWidget(status_label)
status_indicator = QLabel("Not Recording")
status_indicator.setFixedSize(250, 27)
status_indicator.setStyleSheet("background-color: #b8494d; font: 12px; \
        color: {}; font-weight: bold; border-style: solid;".format(FONT_COLOR1))
status_indicator.setAlignment(Qt.AlignCenter)
status_layout.addWidget(status_indicator)
ambient_label = QLabel("Ambient:")
ambient_label.setPixmap(QPixmap("photos/ambient1.png"))
ambient_label.setStyleSheet("color: #ffffff; font: 25px; font-weight: bold; \
            font-family:{};".format(FONT_STYLE))
ambient_label.setAlignment(Qt.AlignCenter)
ambient_label_value = QLabel("NA")
ambient_label_value.setStyleSheet("color: #ffffff; font: 25px; font-weight: bold; \
            font-family:{};".format(FONT_STYLE))
ambient_label_value.setAlignment(Qt.AlignCenter)
status_layout.addWidget(ambient_label)
status_layout.addWidget(ambient_label_value)
header_layout.addLayout(status_layout)

border_line1 = QFrame()
border_line1.setFrameShape(QFrame.HLine)
border_line1.setFrameShadow(QFrame.Sunken)
border_line1.setStyleSheet("color: #ffffff; background-color: #ffffff; border-width: 1px;")
border_line2 = QFrame()
border_line2.setFrameShape(QFrame.HLine)
border_line2.setFrameShadow(QFrame.Sunken)
border_line2.setStyleSheet("color: #ffffff; background-color: #ffffff; border-width: 1px;")
main_layout.addWidget(border_line1)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                Menu Bar
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a menu bar object
menubar = main_window.menuBar()
menubar.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: #ffffff; font: 12px;"\
        f"font-family:{FONT_STYLE}; border-style: solid;"\
        "border-width: 0 1px 1px 1px;")
# Add a File menu
file_menu = menubar.addMenu("File")
# Add an action to the File menu
exit_action = QAction("Exit", main_window)
exit_action.setShortcut("Ctrl+Q")
exit_action.triggered.connect(main_window.close)
file_menu.addAction(exit_action)
# Add an action for new test file
new_test_action = QAction("New Test", main_window)
new_test_action.triggered.connect(lambda: fu.file_setup(testing, tc_modules))
file_menu.addAction(new_test_action)
# Add an action for copying test file
copy_file_action = QAction("Create File Copy", main_window)
copy_file_action.triggered.connect(fu.copy_file)
file_menu.addAction(copy_file_action)

# Add a Setup menu
setup_menu = menubar.addMenu("Setup")
# Add an action for Fry Test
fry_test_action = QAction("Fryer Test")
#fry_test_action.triggered.connect()
setup_menu.addAction(fry_test_action)
# Add an action for Burger Test
# Add a Data menu
data_menu = menubar.addMenu("Data")
# Add an action to the Data menu
view_data_action = QAction("View Data", main_window)
view_data_action.setShortcut("Ctrl+D")
view_data_action.triggered.connect(show_data_window)
data_menu.addAction(view_data_action)

# Add a Graph menu
graph_menu = QMenu("Graph", menubar)
tc_items = []
for i in range(tc_modules*16):
    item = QAction("Temp {}".format(i), graph_menu, checkable=True)
    tc_items.append(item)
menubar.addMenu(graph_menu)

g_font = QFont()
g_font.setBold(True)
g_font.setUnderline(True)
graph_menu_action = QAction("Setup Graph Channels:", main_window)
graph_menu_action.setFont(g_font)
graph_menu.triggered.connect(show_graph_window)
graph_menu.addAction(graph_menu_action)

for i in range(tc_modules*16):
    graph_menu.addAction(tc_items[i])

set_graph_action = QAction("Set Graph Range")
set_graph_action.triggered.connect(set_graph_window)
graph_menu.addAction(set_graph_action)

# Add a Configuration menu
config_menu = menubar.addMenu("Config")
setup_config_action = QAction("Setup Config", main_window)
setup_config_action.triggered.connect(set_config_window)
load_config_action = QAction("Load Config", main_window)
#load_config_action.triggered.connect()
config_menu.addAction(setup_config_action)
config_menu.addAction(load_config_action)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Set Status Bar
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a status bar object
status_bar = QStatusBar()
status_bar.setStyleSheet(f"QStatusBar {{background-color: {PRIMARY_COLOR};\
color: #ffffff; font: 10px;border-style: solid; border-width: 1px 1px 1px 1px; border-color: white;}}")

# Add the status bar to the main window
main_window.setStatusBar(status_bar)

# Add a label to the status bar for system status updates
system_status_label = QLabel("")
system_status_label.setStyleSheet("color: #ffffff;")
status_bar.addPermanentWidget(system_status_label)

# Add a label to the status bar for system status updates
test_file_label = QLabel("")
test_file_label.setStyleSheet("color: #ffffff;")
status_bar.addPermanentWidget(test_file_label)

# Add a label to the status bar for elapsed time
status_bar_label = QLabel("Elapsed Time: 00:00:00")
status_bar_label.setStyleSheet("color: #ffffff;")
status_bar.addPermanentWidget(status_bar_label)

# Function for updating the elapsed time label

def update_values():
#~~~~~ Update Elapsed Time ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Calculate the elapsed time since the program started
    # global test_time
    time_difference = start_time.secsTo(QTime.currentTime())
    elapsed_time = QTime(0, 0, 0).addSecs(time_difference).toString("hh:mm:ss")
    status_bar_label.setText("Elapsed Time: {}".format(elapsed_time))
    
#~~~~ Update Time Label ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    time_label_value.setText("{:.2f}".format(test_time.test_time_min))
#~~~~ Update Ambient Temp Label ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if data_log[-1][11] == None:
        ambient_label_value.setText("Open")
        ambient_label_value.setStyleSheet("color: #b8494d; font: 25px; font-weight:bold;\
            font-family:{};".format(FONT_STYLE))

    elif 70 <= data_log[-1][11] < 80:
        ambient_label_value.setText("{}".format(data_log[-1][11]))
        ambient_label_value.setStyleSheet("color: #ffffff; font: 25px; font-weight:bold;\
            font-family:{};".format(FONT_STYLE))
    elif data_log[-1][11] >=80:
        ambient_label_value.setText("{}".format(data_log[-1][11]))
        ambient_label_value.setStyleSheet("color: #b8494d; font: 25px; font-weight:bold;\
            font-family:{};".format(FONT_STYLE))
    else:
        ambient_label_value.setText("{}".format(data_log[-1][11]))
        ambient_label_value.setStyleSheet("color: #4e94c7; font: 25px; font-weight:bold;\
            font-family:{};".format(FONT_STYLE))
    
    global current_index
    current_index += 1
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Push Buttons
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set push button styles
button_style1 = f"QPushButton {{background-color: {BUTTON_COLOR}; color: #ffffff; font-family:{FONT_STYLE}}}\
                  QPushButton:hover {{background-color: #225c40;}}\
                  QPushButton:pressed {{background-color: #777777;}}"
button_style2 = f"QPushButton {{background-color: {BUTTON_COLOR}; color: #ffffff; font-family:{FONT_STYLE}}}\
                  QPushButton:hover {{background-color: #b8494d;}}\
                  QPushButton:pressed {{background-color: #777777;}}"
button_style3 = f"QPushButton {{background-color: {BUTTON_COLOR}; color: #ffffff; font-family:{FONT_STYLE}}}\
                  QPushButton:hover {{background-color: #555555;}}\
                  QPushButton:pressed {{background-color: #777777;}}"
# Create a "Start" push button and its slot for handling button click event
start_button = QPushButton("Start")
start_button.setStyleSheet(button_style1)
start_button.clicked.connect(start_test)

# Create a "Stop" push button
stop_button = QPushButton("Stop")
stop_button.setStyleSheet(button_style2)
stop_button.clicked.connect(stop_test)

# Create a "Reset" push button
reset_button = QPushButton("Reset")
reset_button.setStyleSheet(button_style3)
reset_button.clicked.connect(reset_)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Setup Matplotlib Graph
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a Matplotlib figure and canvas
fig = plt.Figure(facecolor=(PRIMARY_COLOR))
canvas = FigureCanvas(fig)
ax = fig.add_subplot(111)
ax.set_facecolor(PRIMARY_COLOR)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            Layout Organization
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Add the plot canvas to the layout
main_layout.addWidget(canvas)
main_layout.addWidget(border_line2)
# Add the push buttons to the layout
main_layout.addWidget(start_button)
main_layout.addWidget(stop_button)
main_layout.addWidget(reset_button)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#               Process Time Tool (For application testing only)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pt_start = time.time()
def process_time_start():
    global pt_start
    pt_start = time.time()

def process_time():
    global pt_start
    process_time = time.time() - pt_start
    if process_time > 1.1:
        print("Error: Time delay")
        update_system_status(f"Time Delay Error: Delay =  {1-process_time}s")
    print(process_time)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                              Timing Sequence
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
test_time = TestTime(1) #initialize timing sequence
# Create a QTimer to call the update_plot function at a fixed interval
timer = QTimer()
timer.setTimerType(Qt.PreciseTimer)
timer.start(1000)
# timer.timeout.connect(process_time)
# timer.timeout.connect(process_time_start)
timer.timeout.connect(test_time.update_time)
timer.timeout.connect(get_data)
timer.timeout.connect(update_plot)
timer.timeout.connect(update_data_window)
timer.timeout.connect(update_values)
timer.timeout.connect(lambda: update_system_status(status[-1]))
timer.timeout.connect(lambda: fu.write_data(data_to_write, testing, test_time.time_to_write))
# timer.timeout.connect(lambda: fu.write_data(data_log[-test_time.timing_interval:], testing, test_time.time_to_write))
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                         Main Program Event Loop
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":

    try:
        # Show the application and start the PySide6 event loop
        main_window.show()

        # Create Data directory if it does not exist
        fu.create_directory()
       
        # Create new CSV Test File
        fu.file_setup(testing, tc_modules)
        status.append("Adding new file: {}".format(fu.file_name))

        app.exec()
    except KeyboardInterrupt:
        print("Programa Terminado.")
    except Exception as e:
        print(e)

    finally:
        ni_daq.close_daq()
        sys.exit()

