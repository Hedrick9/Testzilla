"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                 HEADER 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Title:       modbusFuncs.py 
Origin Date: 06/24/2024
Revised:     03/18/2025
Author(s):   Russell Hedrick
Contact:     rhedrick@frontierenergy.com
Description:

The following script focuses on the native UI.

"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import core.file_utils as fu
import core.modbusFuncs as mb 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                Constants
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
FONT_STYLE = "Bahnschrift"
PRIMARY_COLOR = "#000000"
SECONDARY_COLOR = "#0f0f0f"
TRI_COLOR = "#121212"  
DT_COLOR = "#050505"
BUTTON_COLOR = "#111111"
FONT_COLOR1 = "#ffffff"
# DATA_FONT = "#b5b5b5"
DATA_FONT = "#ffffff"
ERROR_FONT = "#b8494d"
GRID_COLOR = "#03fcd3"
BORDER_COLOR = "#ffffff"
IMAGE_FONT = "nasa"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                           Classes & Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Reusable spacer function
def spacer_():
    spacer_item = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed)
    return spacer_item

class MainWindow(QMainWindow):

    def __init__(self, data, ni_daq, test_time, status, timer):
        super().__init__()
        # Initialize parameters as instance variables
        self.data = data
        self.test_time = test_time
        self.status = status
        self.timer = timer
        self.tc_modules = ni_daq.tc_modules
        # Initialize other window classes and variables
        self.start_time = QTime.currentTime()
        self.data_window = DataWindow()
     #~~~~~~~ MAIN WINDOW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create the main window for the application
        self.setWindowTitle("Testzilla")
        self.setGeometry(100,50,900,800)
        self.setStyleSheet(f"QMainWindow {{background-color: {PRIMARY_COLOR};border:1px solid {BORDER_COLOR};}}")
        # Create central widget for main window to hold other main window widgets
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        # Create a vertical layout for the widget
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setSpacing(0)
        self.setLayout(self.central_layout)
     #~~~~~~~~~ HEADER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.header_widget = QWidget()
        self.header_widget.setMaximumHeight(135)
        self.header_layout = QHBoxLayout(self.header_widget)
        self.central_layout.addWidget(self.header_widget)
        # Header Subsection 1: Logo
        self.main_logo = QLabel("FSTC")
        self.main_logo.setStyleSheet(f"color: #ffffff; font: 40px; font-weight: bold;\
                font-family:{FONT_STYLE};")
        self.main_logo.setPixmap(QPixmap(f"photos/fstc_{IMAGE_FONT}.png"))
        self.header_layout.addWidget(self.main_logo)
        # Header Subsection 2: Test Time
        self.time_layout = QVBoxLayout()
        self.time_label = QLabel("TEST TIME:")
        self.time_label.setStyleSheet(f"color: #ffffff; font: 30px; font-weight: bold;\
                    font-family:{FONT_STYLE};")
        self.time_label.setPixmap(QPixmap(f"photos/test_time_{IMAGE_FONT}.png"))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_layout.addWidget(self.time_label)
        self.time_label_value = QLabel("0.0")
        self.time_label_value.setStyleSheet(f"color: #ffffff; font: 30px; font-weight:;\
                    font-family:{FONT_STYLE};") #  
        self.time_label_value.setAlignment(Qt.AlignCenter)
        self.time_layout.addWidget(self.time_label_value)
        spacer_item = QSpacerItem(10, 60, QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.time_layout.addItem(spacer_item)
        self.header_layout.addLayout(self.time_layout)
        # Header Subsection 3: Status and Ambient Temp
        self.status_layout = QVBoxLayout()
        self.status_label = QLabel("Status:")
        self.status_label.setStyleSheet(f"color: #ffffff; font: 25px; font-weight: bold;\
                    font-family:{FONT_STYLE};")
        self.status_label.setPixmap(QPixmap(f"photos/status_{IMAGE_FONT}.png"))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_layout.addWidget(self.status_label)
        self.status_indicator = QLabel("Not Recording")
        self.status_indicator.setFixedSize(250, 27)
        self.status_indicator.setStyleSheet(f"background-color: #b8494d; font: 12px;\
                color: {FONT_COLOR1}; font-weight: bold; border-style: solid;")
        self.status_indicator.setPixmap(QPixmap(f"photos/not_recording_{IMAGE_FONT}.png"))
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_layout.addWidget(self.status_indicator)
        self.ambient_label = QLabel("Ambient:")
        self.ambient_label.setStyleSheet(f"color: #ffffff; font: 25px; font-weight: bold;\
                    font-family:{FONT_STYLE};")
        self.ambient_label.setPixmap(QPixmap(f"photos/ambient_{IMAGE_FONT}.png"))
        self.ambient_label.setAlignment(Qt.AlignCenter)
        self.ambient_label_value = QLabel("NA")
        self.ambient_label_value.setStyleSheet(f"color: #ffffff; font: 25px; font-weight: ;\
                    font-family:{FONT_STYLE};")
        self.ambient_label_value.setAlignment(Qt.AlignCenter)
        self.status_layout.addWidget(self.ambient_label)
        self.status_layout.addWidget(self.ambient_label_value)
        self.header_layout.addLayout(self.status_layout)
     #~~~~~~ MATPLOTLIB GRAPH ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a Matplotlib figure and canvas
        fig = plt.Figure(facecolor=(PRIMARY_COLOR))
        self.canvas = FigureCanvas(fig)
        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor(PRIMARY_COLOR)
     #~~~~~~ GRAPH WINDOW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.graph_window = None
        self.graph_range = None
     #~~~~~~ CONFIG WINDOW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.config_window = None
        self.configs_window = None
        self.configs = None
     #~~~~~~~~ PUSH BUTTONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Set push button styles
        button_style1 = f"""QPushButton {{background-color: {BUTTON_COLOR}; 
                                          color: #ffffff; 
                                          font-family:{FONT_STYLE}; 
                                          font-size: {18}px;}}
                  QPushButton:hover {{background-color: #225c40;}}
                  QPushButton:pressed {{background-color: #777777;}}"""
        button_style2 = f"""QPushButton {{background-color: {BUTTON_COLOR}; 
                                          color: #ffffff; 
                                          font-family:{FONT_STYLE};
                                          font-size: {18}px;}}
                          QPushButton:hover {{background-color: #b8494d;}}
                          QPushButton:pressed {{background-color: #777777;}}"""
        button_style3 = f"""QPushButton {{background-color: {BUTTON_COLOR}; 
                                          color: #ffffff; 
                                          font-family:{FONT_STYLE};
                                          font-size: {18}px;}}
                          QPushButton:hover {{background-color: #555555;}}
                          QPushButton:pressed {{background-color: #777777;}}"""
        # Create a "Start" push button and its slot for handling button click event
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet(button_style1)
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.start_test)
        # Create a "Stop" push button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet(button_style2)
        self.stop_button.setFixedHeight(40)
        self.stop_button.clicked.connect(self.stop_test)
        # Create a "Reset" push button
        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet(button_style3)
        self.reset_button.setFixedHeight(40)
        self.reset_button.clicked.connect(self.reset_)

        self.button_widget = QWidget()
        self.button_widget.setMaximumHeight(50)
        self.button_layout = QHBoxLayout(self.button_widget)
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.stop_button)
        self.button_layout.addWidget(self.reset_button)

     #~~~~~~~~~ MENU BAR ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Create a menu bar object
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: #ffffff; font: 12px;"\
                f"font-family:{FONT_STYLE}; border-style: solid;"\
                 "border-width: 0 1px 1px 1px;")
        # Add a File menu
        file_menu = self.menubar.addMenu("File")
        # Add an action to the File menu
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # Add an action for new test file
        new_test_action = QAction("New Test", self)
        # new_test_action.triggered.connect(lambda: fu.file_setup(self.test_time.testing, self.tc_modules))
        new_test_action.triggered.connect(self.new_test)
        file_menu.addAction(new_test_action)
        # Add an action for copying test file
        copy_file_action = QAction("Create File Copy", self)
        copy_file_action.triggered.connect(fu.copy_file)
        file_menu.addAction(copy_file_action)
         # Add an action for emergency data dump
        data_dump_action = QAction("Data Dump", self)
        data_dump_action.triggered.connect(lambda: fu.data_dump(data.data_log, self.test_time.testing))
        file_menu.addAction(data_dump_action)
       # Add a Setup menu
        setup_menu = self.menubar.addMenu("Setup")
        # Add an action for Fry Test
        fry_test_action = QAction("Fryer Test", self)
        fry_test_action.triggered.connect(self.fry_test)
        setup_menu.addAction(fry_test_action)
        # Add an action for Burger Test
        burger_test_action = QAction("Burger Test", self)
        burger_test_action.triggered.connect(self.burger_test)
        setup_menu.addAction(burger_test_action)
        # Add an action for connecting to Shark 200 meter 
        shark200_action = QAction("Connect to Shark200", self)
        shark200_action.triggered.connect(lambda: data.modbus_thread(device="Shark200"))
        setup_menu.addAction(shark200_action)
        # Add a Data menu
        data_menu = self.menubar.addMenu("Data")
        # Add an action to the Data menu
        view_data_action = QAction("View Data", self)
        view_data_action.setShortcut("Ctrl+D")
        view_data_action.triggered.connect(self.data_window.display)
        data_menu.addAction(view_data_action)
        
        # Add Temperature Graph menu
        self.graph_menu = QMenu("Graph", self.menubar)
        self.tc_items = []
        for i in range(self.tc_modules*16):
            item = QAction(f"Temp {i}", self.graph_menu, checkable=True)
            self.tc_items.append(item)
        self.menubar.addMenu(self.graph_menu)
        
        g_font = QFont()
        g_font.setBold(True)
        g_font.setUnderline(True)
        graph_menu_action = QAction("Setup Graph Channels:", self)
        graph_menu_action.setFont(g_font)
        self.graph_menu.triggered.connect(self.show_graph_window)
        self.graph_menu.addAction(graph_menu_action)
        
        for i in range(self.tc_modules*16):
            self.graph_menu.addAction(self.tc_items[i])
        
        set_graph_action = QAction("Set Graph Range", self)
        set_graph_action.triggered.connect(self.set_graph_window)
        self.graph_menu.addAction(set_graph_action)
        # Add Graph menu for other channels
        # self.graph_menu2 = QMenu("Graph 2", self.menubar)
        # graph_action1 = QAction("mb.Watts", self.graph_menu2, checkable=True)
        # graph_action2 = QAction("mb.Voltage", self.graph_menu2, checkable=True)
        # self.graph_items = [graph_action1, graph_action2]
        # for item in self.graph_items: 
        #     self.graph_menu2.addAction(item)
        # self.menubar.addMenu(self.graph_menu2)
        # self.graph_menu2.triggered.connect(self.show_graph2_window)
        # Add a Configuration menu
        config_menu = self.menubar.addMenu("Config")
        setup_config_action = QAction("Setup Config", self)
        setup_config_action.triggered.connect(self.set_config_window)
        load_config_action = QAction("Load Config", self)
        load_config_action.triggered.connect(self.load_config_window)
        config_menu.addAction(setup_config_action)
        config_menu.addAction(load_config_action)
     #~~~~~~~~ STATUS BAR ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"QStatusBar {{background-color: {PRIMARY_COLOR};\
        color: #ffffff; font: 10px;border-style: solid; border-width: 1px 1px 1px 1px; border-color: white;}}")
        # Add the status bar to the main window
        self.setStatusBar(self.status_bar)
        # Add labels to the status bar for system status updates
        self.system_status_label = QLabel("")
        self.system_status_label.setStyleSheet("color: #ffffff;")
        self.status_bar.addPermanentWidget(self.system_status_label)
        self.test_file_label = QLabel("")
        self.test_file_label.setStyleSheet("color: #ffffff;")
        self.status_bar.addPermanentWidget(self.test_file_label)
        # Add a label to the status bar for elapsed time
        self.status_bar_label = QLabel("Elapsed Time: 00:00:00")
        self.status_bar_label.setStyleSheet("color: #ffffff;")
        self.status_bar.addPermanentWidget(self.status_bar_label)
     #~~~~~~~~~ STYLING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        border_line1 = QFrame()
        border_line1.setFrameShape(QFrame.HLine)
        border_line1.setFrameShadow(QFrame.Sunken)
        border_line1.setStyleSheet("color: {BORDER_COLOR}; background-color: {BORDER_COLOR}; border-width: 1px;")
        border_line2 = QFrame()
        border_line2.setFrameShape(QFrame.HLine)
        border_line2.setFrameShadow(QFrame.Sunken)
        border_line2.setStyleSheet("color: {BORDER_COLOR}; background-color: {BORDER_COLOR}; border-width: 1px;")
     #~~~~~~ LAYOUT ORGANIZATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.central_layout.addWidget(border_line1)
        self.central_layout.addWidget(self.canvas)
        self.central_layout.addWidget(border_line2)
        self.central_layout.addWidget(self.button_widget)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #       MAIN WINDOW CLASS FUNCTIONS
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def update_system_status(self, status):
        # Update status bar w/ system status
        self.system_status_label.setText(status)
        # Update elapsed program time
        time_difference = self.start_time.secsTo(QTime.currentTime())
        elapsed_time = QTime(0, 0, 0).addSecs(time_difference).toString("hh:mm:ss")
        self.status_bar_label.setText("Elapsed Time: {}".format(elapsed_time))
   
    #~~~~~~ UPDATE PLOT FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def update_plot(self, data_log):
        # Update the plot with new data
        df = pd.DataFrame(data_log)
        # Create list of tc channels to graph    
        if self.graph_menu is not None:
            tc_list_ = [tc.text() for tc in self.graph_menu.actions() if tc.isCheckable() and tc.isChecked()]
            tc_list = [int(name.split()[1]) for name in tc_list_]
            while len(tc_list) > 11:
                tc_list.remove(tc_list[-1])
        # Graph tc channels in list
        if len(data_log) < 3600 and len(tc_list)>0:
            self.ax.clear()
            for item in tc_list:
                self.ax.plot(df[1], df[item+11], label=str(item), lw=0.75)
        elif len(data_log) >= 3600 and len(tc_list)>0:
            self.ax.clear()
            for item in tc_list:
                self.ax.plot(df[1][-3600:-1], df[item+11][-3600:-1], label=str(item), lw=0.75)
        # Graph tc channel 0 if none selected
        else:
            if len(df) < 3600:
                self.ax.clear()
                self.ax.plot(df[1], df[11], label="ambient", lw=0.75)
            else:
                self.ax.clear()
                self.ax.plot(df[1][-3600:-1], df[11][-3600:-1], label="ambient", lw=0.75)
        # Format Plot   
        if self.graph_window is not None:
            try:
                self.ax.set_ylim([self.graph_range[-1][1], self.graph_range[-1][0]])
            except Exception as e:
                pass
        else: 
            self.ax.set_ylim([None, None])
        self.ax.legend(loc='lower right', frameon=False, ncol=3, labelcolor=FONT_COLOR1)
        self.ax.set_facecolor(TRI_COLOR)
        self.ax.tick_params(labelbottom=True, labelcolor=FONT_COLOR1, color="#ffffff", labelsize=11)
        self.ax.minorticks_on()
        #ax.spines[:].set_visible(False)#set_color("#ffffff")
        self.ax.spines[:].set_color("#2b2b2a")
        self.ax.spines[:].set_linewidth(0.25)
        self.ax.grid(which='major', linewidth=0.3, color=GRID_COLOR) 
        self.ax.grid(which='minor', linewidth=0.1, color=GRID_COLOR)
        self.canvas.draw() # update plot
    
    #~~~ DISPLAY GRAPH CHANNEL LIST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def show_graph_window(self):
        self.graph_menu.exec()
    # #~~~ DISPLAY GRAPH CHANNEL LIST ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    # def show_graph2_window(self):
    #     self.graph_menu2.exec()
    #
    #~~~ SET GRAPH RANGE FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_graph_window(self):
        self.graph_window = QWidget()
        self.graph_window.setWindowTitle("Setup Graph")
        self.graph_window.setGeometry(400, 100, 350, 200)
        self.graph_window.setStyleSheet(f"background-color: {SECONDARY_COLOR};")
        self.graph_range = []
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
        set_button.clicked.connect(lambda: self.graph_range.append((int(upper_bound_entry.text()), int(lower_bound_entry.text()),)))
    
        layout.addWidget(label1)
        layout.addWidget(upper_bound_entry)
        layout.addWidget(label2)
        layout.addWidget(lower_bound_entry)
        layout.addWidget(set_button)
        self.graph_window.setLayout(layout)
        self.graph_window.show()

    def handle_time_selection(self, index):
        time_dict = {0: 1, 1: 5, 2: 30, 3: 60}
        self.test_time.timing_interval = time_dict[index]

    def handle_port_selection(self, index):
        port_dict = {0: "COM3", 1: "COM4", 2: "COM5", 3: "COM6"}
        self.data.mb_port = port_dict[index]
        print(f"Changing Modbus Port to: {self.data.mb_port}")

    #~~~ CONFIGURATION SETTING FUNCTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_config_window(self):
        self.config_window = QWidget()
        self.config_window.setWindowTitle("Test Configuration Setup")
        self.config_window.setGeometry(200, 200, 300, 150)
        self.config_window.setStyleSheet(f"background-color: {PRIMARY_COLOR};")
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        # Test Time Update Rate 
        label1 = QLabel("Set Test Time Interval:")
        label1.setStyleSheet("color: #ffffff; font: 14px;")
        time_selection = QComboBox()
        time_selection.setStyleSheet("background-color:#222; color: #ffffff; font: 14px;")
        time_selection.addItem("1 second")
        time_selection.addItem("5 seconds")
        time_selection.addItem("30 seconds")
        time_selection.addItem("1 minute")
        time_selection.currentIndexChanged.connect(self.handle_time_selection)
        # Set Modbus COM port
        label2 = QLabel("Set Modbus COM Port:")
        label2.setStyleSheet("color: #ffffff; font: 14px;")
        port_selection = QComboBox()
        port_selection.setStyleSheet("background-color:#222; color: #ffffff; font: 14px;")
        port_selection.addItem("COM3")
        port_selection.addItem("COM4")
        port_selection.addItem("COM5")
        port_selection.addItem("COM6")
        port_selection.currentIndexChanged.connect(self.handle_port_selection)
        
        layout.addWidget(label1)
        layout.addWidget(time_selection)
        layout.addWidget(label2)
        layout.addWidget(port_selection)
        self.config_window.setLayout(layout)
        self.config_window.show()

    def load_config_window(self):
        self.configs_window = QWidget()
        self.configs_window.setWindowTitle("Load Configuration")
        self.configs_window.setGeometry(200, 200, 300, 200)
        self.configs_window.setStyleSheet(f"background-color: {PRIMARY_COLOR};")
        layout = QVBoxLayout()
        layout.setSpacing(0)

        # Label to display the selected file name
        self.config_path_label = QLabel("No file selected")
        self.config_path_label.setStyleSheet("color: #ffffff; font: 14px;")
        layout.addWidget(self.config_path_label)
        
        # Button to trigger the file dialog
        button_style = f"""QPushButton {{background-color: {BUTTON_COLOR}; 
                                          color: #ffffff; 
                                          font-family:{FONT_STYLE}; 
                                          font-size: {14}px;}}
                  QPushButton:hover {{background-color: {SECONDARY_COLOR};}}
                  QPushButton:pressed {{background-color: #777777;}}"""

        button = QPushButton("Select CSV File")
        button.setStyleSheet(button_style)
        button.clicked.connect(self.select_csv_file)
        layout.addWidget(button)
        
        self.configs_window.setLayout(layout)
        self.configs_window.show()

    def select_csv_file(self):
        config_path = fu.current_directory+"/config/"
        file_path, _ = QFileDialog.getOpenFileName(self, 
                                                   "Open CSV File",
                                                   config_path,
                                                   "CSV FIles (*.csv)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.config_path_label.setText(f"Selected File: {file_name}") 
            self.configs = fu.read_config(file_name) 
        else:
            self.config_path_label.setText(f"No file selected") 

    #~~~~ SLOT FUNCTION FOR HANDLING START BUTTON CLICK EVENT ~~~~~~~~~~~~~~~~
    def start_test(self):
        self.test_time.testing = True
        self.data.data_log = []
        self.data.pulse_reset = self.data.pulse_data
        self.status.append("testing in progress...")
        # Styling for status indicator ~~~
        self.status_indicator.setStyleSheet("background-color: #225c40; font: 12px; \
            color: #ffffff; font-weight: bold;")
        # self.status_indicator.setText("Recording")
        app_dir = fu.current_directory
        image_path = f"{app_dir}/photos/recording_{IMAGE_FONT}.png"
        pixmap = QPixmap(image_path)
        self.status_indicator.setPixmap(pixmap)
        # rewrite headers (if headers were renamed)
        fu.write_headers(self.data_window.retrieve_model_data())
        # update configs if changed 
        if self.configs is not None: 
            self.data.pcfs = [self.configs.elec_pcf[0], self.configs.gas_pcf[0], self.configs.water_pcf[0], self.configs.extra_pcf[0]]
        # reset clocks and begin test sequence
        self.test_file_label.setText(f"File Name: {fu.file_name}")
        self.start_time = QTime.currentTime()
        self.test_time.reset()
        self.data.data_to_write[1] = 0.0 # resets the clock and writes a t0 timestamp 
        fu.write_data(self.data.data_to_write, self.test_time.testing, True)
        self.timer.start(1000)  # Start the timer to update the plot every 1000 milliseconds (1 second)
    
    #~~~~ SLOT FUNCTION FOR HANDLING STOP BUTTON CLICK EVENT ~~~~~~~~~~~~~~~~~
    def stop_test(self):
        self.test_time.testing = False
        self.timer.stop()  # Stop the timer to stop updating the plot
        self.status.append("testing concluded.")
        self.update_system_status(self.status[-1])
        self.status_indicator.setStyleSheet("background-color: #b8494d; font: 12px; \
            color: #ffffff; font-weight: bold;")
        # self.status_indicator.setText("Not Recording")
        app_dir = fu.current_directory
        image_path = f"{app_dir}/photos/not_recording_{IMAGE_FONT}.png"
        pixmap = QPixmap(image_path)
        self.status_indicator.setPixmap(pixmap)
   
    #~~~~ SLOT FUNCTION FOR HANDLING RESET BUTTON CLICK EVENT ~~~~~~~~~~~~~~~~
    def reset_(self):
        self.data.data_log = []
        self.data.pulse_reset = self.data.pulse_data
        self.start_time = QTime.currentTime()
        self.test_time.reset()
        self.data.data_to_write[1] = 0.0 # resets the clock and writes a t0 timestamp 
        fu.write_data(self.data.data_to_write, self.test_time.testing, True)
        self.timer.start(1000)

    def update_values(self, data, test_time):
    #~~~~~ Update Elapsed Time ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Calculate the elapsed time since the program started
        time_difference = self.start_time.secsTo(QTime.currentTime())
        elapsed_time = QTime(0, 0, 0).addSecs(time_difference).toString("hh:mm:ss")
        self.status_bar_label.setText("Elapsed Time: {}".format(elapsed_time))
        
    #~~~~ Update Time Label ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.time_label_value.setText("{:.2f}".format(test_time.test_time_min))
    #~~~~ Update Ambient Temp Label ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
        if data.data_log[-1][11] == None:
            self.ambient_label_value.setText("Open")
            self.ambient_label_value.setStyleSheet("color: #b8494d; font: 25px; font-weight:;\
                font-family:{};".format(FONT_STYLE))
    
        elif 70 <= data.data_log[-1][11] < 80:
            self.ambient_label_value.setText("{}".format(data.data_log[-1][11]))
            self.ambient_label_value.setStyleSheet("color: #ffffff; font: 25px; font-weight:;\
                font-family:{};".format(FONT_STYLE))
        elif data.data_log[-1][11] >=80:
            self.ambient_label_value.setText("{}".format(data.data_log[-1][11]))
            self.ambient_label_value.setStyleSheet("color: #b8494d; font: 25px; font-weight:;\
                font-family:{};".format(FONT_STYLE))
        else:
            self.ambient_label_value.setText("{}".format(data.data_log[-1][11]))
            self.ambient_label_value.setStyleSheet("color: #4e94c7; font: 25px; font-weight:;\
                font-family:{};".format(FONT_STYLE))

    def new_test(self):
        fu.file_setup(self.test_time.testing, self.tc_modules)
        self.test_file_label.setText(f"File Name: {fu.file_name}")

    def fry_test(self):
        pass

    def burger_test(self):
        pass
 
class DataWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data")
        self.setGeometry(1050, 50, 425, 800)
        self.setStyleSheet(f"background-color: {PRIMARY_COLOR};")
        # Setup Data Window Layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        # Add a labels to the window
        label1 = QLabel("Temperatures (F):", self)
        label1.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
                font-family:{}; text-decoration: underline;".format(FONT_STYLE))
        label1.setPixmap(QPixmap(f"photos/temp_{IMAGE_FONT}.png"))

        label2 = QLabel("Pulse Data:", self)
        label2.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
                font-family:{}; text-decoration: underline;".format(FONT_STYLE))
        label2.setPixmap(QPixmap(f"photos/pulse_{IMAGE_FONT}.png"))

        label3 = QLabel("Modbus Data:", self)
        label3.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
                font-family:{}; text-decoration: underline;".format(FONT_STYLE))
        label3.setPixmap(QPixmap(f"photos/modbus_{IMAGE_FONT}.png"))

        label4 = QLabel("Analog Data:", self)
        label4.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
                font-family:{}; text-decoration: underline;".format(FONT_STYLE))
        label4.setPixmap(QPixmap(f"photos/analog_{IMAGE_FONT}.png"))

        label5 = QLabel("Analysis:", self)
        label5.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
                font-family:{}; text-decoration: underline;".format(FONT_STYLE))
        label5.setPixmap(QPixmap(f"photos/analysis_{IMAGE_FONT}.png"))
    #~~~~~ Section 1: Temperature Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.tc_model = QStandardItemModel(8, 8)
        for row in range(8):
            for column in range(8):
                if column % 2 == 0:
                    index = int((row)+((column/2)*8))
                    item = QStandardItem(f"Temp {index}:")
                    self.tc_model.setItem(row, column, item)
                else:
                    item = QStandardItem("NA".format(index))
                    self.tc_model.setItem(row, column, item)

        self.tc_model.item(0, 0).setText("Ambient:")
        table_view1 = QTableView()
        table_view1.horizontalHeader().setVisible(False)
        table_view1.verticalHeader().setVisible(False)
        table_view1.setFixedHeight(260)
        table_view1.setModel(self.tc_model)
        table_view1.setStyleSheet(f"background-color: {DT_COLOR}; color: {DATA_FONT}; font: 14px; font-family:{FONT_STYLE};"\
                "border-style: solid; border-width: 1px 1px 1px")
        # Temp Average
        temp_avg_layout1 = QHBoxLayout()
        label_1a = QLabel(" Average of Temps  ")
        label_1a.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
        label_1a.setPixmap(QPixmap(f"photos/avg_temp_{IMAGE_FONT}.png"))
        temp_avg_layout1.addWidget(label_1a)
        self.temp_avg_value_1a = QLineEdit()
        self.temp_avg_value_1a.setStyleSheet(f"color: {DATA_FONT}; font: 14px; border:none;border-bottom:1px solid white;")
        temp_avg_layout1.addWidget(self.temp_avg_value_1a)
        label_1b = QLabel(" to ")
        label_1b.setStyleSheet(f"color: {DATA_FONT}; font: 14px; font-family:{FONT_STYLE}")
        temp_avg_layout1.addWidget(label_1b)
        self.temp_avg_value_1b = QLineEdit()
        self.temp_avg_value_1b.setStyleSheet(f"color: {DATA_FONT}; font: 14px; border: none; border-bottom:1px solid white;")
        temp_avg_layout1.addWidget(self.temp_avg_value_1b)
        self.temp_avg_value_1c = QLabel(" = NA")
        self.temp_avg_value_1c.setStyleSheet(f"color: {DATA_FONT}; font: 14px; font-weight:bold;")
        temp_avg_layout1.addWidget(self.temp_avg_value_1c)
        
        temp_avg_layout2 = QHBoxLayout()
        label_2a = QLabel(" Average of Temps  ")
        label_2a.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
        label_2a.setPixmap(QPixmap(f"photos/avg_temp_{IMAGE_FONT}.png"))
        temp_avg_layout2.addWidget(label_2a)
        self.temp_avg_value_2a = QLineEdit()
        self.temp_avg_value_2a.setStyleSheet(f"color: {DATA_FONT}; font: 14px; border:none;border-bottom:1px solid white;")
        temp_avg_layout2.addWidget(self.temp_avg_value_2a)
        label_2b = QLabel(" to ")
        label_2b.setStyleSheet(f"color: {DATA_FONT}; font: 14px; font-family:{FONT_STYLE}")
        temp_avg_layout2.addWidget(label_2b)
        self.temp_avg_value_2b = QLineEdit()
        self.temp_avg_value_2b.setStyleSheet(f"color: {DATA_FONT}; font: 14px; border:none;border-bottom:1px solid white;")
        temp_avg_layout2.addWidget(self.temp_avg_value_2b)
        self.temp_avg_value_2c = QLabel(" = NA")
        self.temp_avg_value_2c.setStyleSheet(f"color: {DATA_FONT}; font: 14px; font-weight:bold;")
        temp_avg_layout2.addWidget(self.temp_avg_value_2c)
    #~~~~~~ Section 2: Pulse and Other Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.pulse_model = QStandardItemModel(3, 4)
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

        self.pulse_model.setItem(0, 0, item1)
        self.pulse_model.setItem(1, 0, item2)
        self.pulse_model.setItem(2, 0, item3) # electric total
        self.pulse_model.setItem(0, 1, item4)
        self.pulse_model.setItem(1, 1, item5)
        self.pulse_model.setItem(2, 1, item6) # gas total
        self.pulse_model.setItem(0, 2, item7)
        self.pulse_model.setItem(1, 2, item8) 
        self.pulse_model.setItem(2, 2, item9) # water total
        self.pulse_model.setItem(0, 3, item10)
        self.pulse_model.setItem(1, 3, item11)
        self.pulse_model.setItem(2, 3, item12) # extra total
        
        table_view2 = QTableView()
        table_view2.horizontalHeader().setVisible(False)
        table_view2.verticalHeader().setVisible(False)
        table_view2.setModel(self.pulse_model)
        table_view2.setStyleSheet(f"background-color: {DT_COLOR}; color: {DATA_FONT}; font: 14px;"\
                f"font-family:{FONT_STYLE}; border-style: solid; border-width: 0 1px 1px 1px;")

    #~~~~~~ Section 3: Modbus Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.modbus_model = QStandardItemModel(4, 3)
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

        self.modbus_model.setItem(0, 0, mb_item1)
        self.modbus_model.setItem(0, 1, mb_item2)
        self.modbus_model.setItem(0, 2, mb_item3)
        self.modbus_model.setItem(1, 0, mb_item4)
        self.modbus_model.setItem(1, 1, mb_item5)
        self.modbus_model.setItem(1, 2, mb_item6)
        self.modbus_model.setItem(2, 0, mb_item7)
        self.modbus_model.setItem(2, 1, mb_item8)
        self.modbus_model.setItem(2, 2, mb_item9)
        self.modbus_model.setItem(3, 0, mb_item10)
        self.modbus_model.setItem(3, 1, mb_item11)
        self.modbus_model.setItem(3, 2, mb_item12)

        self.table_view3 = QTableView()
        self.table_view3.horizontalHeader().setVisible(False)
        self.table_view3.verticalHeader().setVisible(False)
        self.table_view3.setModel(self.modbus_model)
    #~~~~~~ Section 4: Analog Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.analog_model = QStandardItemModel(1, 1)
        ai_item1 = QStandardItem("AI 1:  NA")
        ai_item2 = QStandardItem("AI 2:  NA")

        self.analog_model.setItem(0, 0, ai_item1)
        self.analog_model.setItem(0, 1, ai_item2)

        table_view4 = QTableView()
        table_view4.horizontalHeader().setVisible(False)
        table_view4.verticalHeader().setVisible(False)
        table_view4.setFixedHeight(40)
        table_view4.setModel(self.analog_model)
        table_view4.setStyleSheet(f"background-color: {DT_COLOR}; color: {DATA_FONT}; font: 14px;"\
                f"font-family:{FONT_STYLE}; border-style: solid; border-width: 0 1px 1px 1px;")
    #~~~~~~ Section 5: Analysis ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.index_label = QLabel("Current Index = NA", self) 
        self.index_label.setStyleSheet(f"color: {DATA_FONT}; font: 14px; font-family:{FONT_STYLE};")
        index_layout = QHBoxLayout()
        start_index_label = QLabel(" Start Index =  ")
        start_index_label.setStyleSheet(f"color: {DATA_FONT}; font: 14px; font-family:{FONT_STYLE}")
        start_index_label.setPixmap(QPixmap(f"photos/start_index_{IMAGE_FONT}.png"))
        index_layout.addWidget(start_index_label)
        self.start_index_input = QLineEdit()
        self.start_index_input.setStyleSheet(f"color: {DATA_FONT}; font: 14px; border:none;border-bottom: 1px solid white;")
        index_layout.addWidget(self.start_index_input)
        end_index_label = QLabel(" End Index = ")
        end_index_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
        end_index_label.setPixmap(QPixmap(f"photos/end_index_{IMAGE_FONT}.png"))
        index_layout.addWidget(end_index_label)
        self.end_index_input = QLineEdit()
        self.end_index_input.setStyleSheet(f"color: {DATA_FONT}; font: 14px; border:none;border-bottom: 1px solid white;")
        index_layout.addWidget(self.end_index_input)
         
        self.er_time_label = QLabel(" Start Time = NA     |     End Time = NA  ")
        self.er_time_label.setStyleSheet(f"color: {DATA_FONT}; font: 14px; font-family:{FONT_STYLE};")
        
        self.meter_selection = QComboBox()
        self.meter_selection.setStyleSheet(f"background-color: #111; color: {DATA_FONT}; font: 14px;")
        self.meter_selection.addItem("Gas Meter")
        self.meter_selection.addItem("120V Meter")
        self.meter_selection.addItem("208V Meter")
        self.meter_selection.addItem("Water Meter")
        # meter_selection.currentIndexChanged.connect(handle_meter_selection)
        energy_rate_layout = QHBoxLayout()
        hhv_label = QLabel(" HHV =            ")
        hhv_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
        hhv_label.setPixmap(QPixmap(f"photos/hhv_{IMAGE_FONT}.png"))
        energy_rate_layout.addWidget(hhv_label)
        self.hhv_input = QLineEdit("1")
        self.hhv_input.setStyleSheet("color: #ffffff; font: 14px; border:none;border-bottom: 1px solid white;")
        energy_rate_layout.addWidget(self.hhv_input)
        gcf_label = QLabel(" GCF =          ")
        gcf_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE}")
        gcf_label.setPixmap(QPixmap(f"photos/gcf_{IMAGE_FONT}.png"))
        energy_rate_layout.addWidget(gcf_label)
        self.gcf_input = QLineEdit("1")
        self.gcf_input.setStyleSheet("color: #ffffff; font: 14px; border:none;border-bottom: 1px solid white;")
        energy_rate_layout.addWidget(self.gcf_input)
        
        self.energy_rate_label = QLabel(" Energy Rate = ")
        self.energy_rate_label.setStyleSheet(f"color: #ffffff; font: 14px; font-family:{FONT_STYLE};")
    #~~~~~~ Adjust Layout ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Organize structure of layout 
        self.layout.addWidget(label1)
        self.layout.addWidget(table_view1)
        self.layout.addLayout(temp_avg_layout1)
        self.layout.addLayout(temp_avg_layout2)
        self.layout.addItem(spacer_())
        self.layout.addWidget(label2)
        self.layout.addWidget(table_view2)
        self.layout.addWidget(label3)
        self.layout.addWidget(self.table_view3)
        self.layout.addWidget(label4)
        self.layout.addWidget(table_view4)
        self.layout.addWidget(label5)
        self.layout.addItem(spacer_())
        self.layout.addWidget(self.index_label)
        self.layout.addWidget(self.meter_selection)
        self.layout.addLayout(index_layout)
        self.layout.addItem(spacer_())
        self.layout.addWidget(self.er_time_label)
        self.layout.addLayout(energy_rate_layout)
        self.layout.addItem(spacer_())
        self.layout.addWidget(self.energy_rate_label)
        self.setLayout(self.layout)
 
    def display(self):
        self.show()

    def update_data(self, data, test_time):
        # Update the values in the temperature table 
        for row in range(8):
            if len(data.data_log[0]) > 30: # if there are more than 16 tc's
                for column in range(1,8,2):
                    index = int((row)+(((column-1)/2)*8))
                    self.tc_model.item(row, column).setText(f"{data.data_log[-1][index+11]}")
            else:
                for column in range(1,4,2):
                    index = int((row)+(((column-1)/2)*8))
                    self.tc_model.item(row, column).setText(f"{data.data_log[-1][index+11]}")

        try:
            t1a = int(self.temp_avg_value_1a.text())
            t1b = int(self.temp_avg_value_1b.text())
            t1_l = data.ni_data[t1a+6:t1b+7]
            tavg1 = np.mean(np.array([value for value in t1_l if value < 4000]))
            self.temp_avg_value_1c.setText(f" = {round(tavg1, 1)}")
        except Exception as e:
            self.temp_avg_value_1c.setText(" = NA")

        try:
            t2a = int(self.temp_avg_value_2a.text())
            t2b = int(self.temp_avg_value_2b.text())
            t2_l = data.ni_data[t2a+6:t2b+7]
            tavg2 = np.mean(np.array([value for value in t2_l if value < 4000]))
            self.temp_avg_value_2c.setText(f" = {round(tavg2, 1)}")
        except Exception as e:
            self.temp_avg_value_2c.setText(" = NA")

        # Update the values in pulse table
        for i in range(4):
            self.pulse_model.item(1, i).setText(f"Interval: {data.pulse_data[i]:.2f}")
        for i in range(4):
            self.pulse_model.item(2, i).setText(f"Total: {data.data_log[-1][i+5]:.2f}")

        # Update the values in modbus table
        if data.mb_connected == True:
            self.table_view3.setStyleSheet(f"background-color: {DT_COLOR}; color: {DATA_FONT}; font: 14px;"\
                    f"font-family:{FONT_STYLE}; border-style: solid; border-width: 0 1px 1px 1px;")
        elif data.mb_connected == False:
            self.table_view3.setStyleSheet(f"background-color: {DT_COLOR}; color: {ERROR_FONT}; font: 14px;"\
                    f"font-family:{FONT_STYLE}; border-style: solid; border-width: 0 1px 1px 1px;")

        self.modbus_model.item(0, 0).setText(f"Avg. Voltage: {data.mb_data[0][0]}")
        self.modbus_model.item(0, 1).setText(f"Watts: {data.mb_data[0][1]}")
        self.modbus_model.item(0, 2).setText(f"Electrical Energy: {data.mb_data[0][2]}")
        self.modbus_model.item(1, 0).setText(f"V_AN: {data.mb_data[0][3]}")
        self.modbus_model.item(1, 1).setText(f"V_BN: {data.mb_data[0][4]}")
        self.modbus_model.item(1, 2).setText(f"V_CN: {data.mb_data[0][5]}")
        self.modbus_model.item(2, 0).setText(f"V_AB: {data.mb_data[0][6]}")
        self.modbus_model.item(2, 1).setText(f"V_BC: {data.mb_data[0][7]}")
        self.modbus_model.item(2, 2).setText(f"V_CA: {data.mb_data[0][8]}")
        self.modbus_model.item(3, 0).setText(f"I_A: {data.mb_data[0][9]}")
        self.modbus_model.item(3, 1).setText(f"I_B: {data.mb_data[0][10]}")
        self.modbus_model.item(3, 2).setText(f"I_C: {data.mb_data[0][11]}")

        # Update values in AI section
        self.analog_model.item(0, 0).setText(f"AI 1:  {data.data_log[-1][9]}")
        self.analog_model.item(0, 1).setText(f"AI 2:  {data.data_log[-1][10]}")
        # Update the values in analysis section 
        self.index_label.setText("Current Index = {}".format(data.current_index))
        try:
            st_i = int(self.start_index_input.text())
            et_i = int(self.end_index_input.text())
            hhv = int(self.hhv_input.text())
            gcf = float(self.gcf_input.text())
            ti = data.data_log[st_i][1]
            tf = data.data_log[et_i][1]
            self.er_time_label.setText(f" Start Time = {ti}     |     End Time = {tf}")
            meter_ix = {"Gas Meter": 6, "120V Meter": 5, "208V Meter":4, "Water Meter": 7}[self.meter_selection.currentText()]
            er_calc = (data.data_log[et_i][meter_ix] - data.data_log[st_i][meter_ix])*hhv*gcf/((tf-ti)/60)
            self.energy_rate_label.setText(f" Energy Rate = {round(er_calc,1)}")
        except ValueError as e:
            pass
        except IndexError as e:
            pass

    def retrieve_model_data(self):
        headers = ["Time of Day", "Test Time", "Voltage", "W", "Wh.208", "Wh.120","Gas","Water","Extra"] + \
                  ["AI 1", "AI 2", "Ambient"]
        for column in range(0,7,2):
            for row in range(8):
                item_data = self.tc_model.item(row, column).text()
                headers.append(item_data)
        headers.pop(12) # ambient header is unchanged 
        return headers


if __name__ == "__main__":
    
    app = QApplication()
    mw = MainWindow(testing, data)
    mw.show()

    app.exec()
