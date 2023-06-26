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
from PySide6.QtCore import QTime, QTimer, QSize, Qt
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
# Simulated Data File 
file_name = "scratch_data_0.csv"
# Color Palette
primary_color = "#000000" 
secondary_color = "#2b2b2a"
tri_color = "#121212"  
font_color1 = "#ffffff"
font_style = "Helvetica"
start_time = QTime.currentTime()
print(start_time)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            Initialize DAQ(s)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ni.init_daq()
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


data_ = None
d = []
last_data = [0, 0, 0, 0]
pulse_d = [0, 0, 0, 0]
pulse_reset = [0, 0, 0, 0]
def get_data(pcfs=[1, .05, 1, 1]):
    # global test_time
    global last_data
    global pulse_d
    global pulse_reset
    global data_
    tod = datetime.now().strftime("%H:%M:%S")
    # Try to read in data from ni hardware; otherwise return list of 0's
    data_ = ni.read_daq()
    if data_ is not None:
        data_ = list(np.around(np.array(ni.read_daq()),1))
        data = list(np.multiply(pcfs, np.array(data_[:4])-np.array(last_data))) + \
        ["open" if x > 4000 else x for x in data_[4:]]
        data.insert(0, tod)
        data.insert(1, test_time.test_time_min)
        d.append(data)
        pulse_d = list(np.array(data_[:4])-np.array(pulse_reset))
        last_data = data_[:4]
    else:
        status.append("error reading from ni-DAQ")
        data_ = list(np.zeros(20))
        data_.insert(0, tod)
        data_.insert(1, test_time.test_time_min)
        d.append(data_)
#~~~~~~~~~~~~~~~~~~~~~~ Update Plot Function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def update_plot():
    # Update the plot with new data
    #data = pd.read_csv(file_name)
    df = pd.DataFrame(d)
    # Create list of tc channels to graph    
    if graph_menu is not None:
        tc_list_ = [tc.text() for tc in graph_menu.actions() if tc.isCheckable() and tc.isChecked()]
        tc_list = [int(name.split()[1]) for name in tc_list_]
    
    # Graph tc channels in list
    if len(d) < 3600 and len(tc_list)>0:
        ax.clear()
        for item in tc_list:
            ax.plot(df[item+8], label=str(item), lw=0.5)
    elif len(d) >= 3600 and len(tc_list)>0:
        ax.clear()
        for item in tc_list:
            ax.plot(df[item+8][-3600:-1], label=str(item), lw=0.5)
    # Graph tc channel 0 if none selected
    else:
        if len(df) < 3600:
            ax.clear()
            ax.plot(df[8], label="ambient", lw=0.5)
        else:
            ax.clear()
            ax.plot(df[8][-3600:-1], label="ambient", lw=0.5)
    
    # Format Plot   
    if graph_window is not None:
        ax.set_ylim([0, 200])
    else: 
        ax.set_ylim([None, None])
    ax.legend(loc='lower right', frameon=False, ncol=3, labelcolor=font_color1)
    ax.set_facecolor(tri_color)
    ax.tick_params(labelbottom=False, labelcolor=font_color1, color="#ffffff", labelsize=8)
    ax.minorticks_on()
    #ax.spines[:].set_visible(False)#set_color("#ffffff")
    ax.spines[:].set_color(secondary_color)
    ax.spines[:].set_linewidth(0.25)
    # ax.grid(which='both', linewidth=0.25, color="#ffffff") 
    # ax.grid(which='major', linewidth=0.3, color="#22ffff") 
    # ax.grid(which='minor', linewidth=0.1, color="#22ffff") 
    ax.grid(which='major', linewidth=0.3, color="#03fcd3") 
    ax.grid(which='minor', linewidth=0.1, color="#03fcd3") 
    # Call canvas.draw() to update the plot on the canvas
    canvas.draw()

#~~~~~~~~~ Slot function for handling status update in status bar ~~~~~~~~~~~~~
def update_system_status(status):
     
    system_status_label.setText(status)

#~~~~~~~~~ Slot function for handling start button click event ~~~~~~~~~~~~~~~~
def start_test():
    global testing
    global start_time
    global d
    global pulse_d
    global pulse_reset
    global status_indicator
    testing = True
    d = []
    pulse_reset = pulse_d
    status.append("testing in progress...")
    status_indicator.setStyleSheet("background-color: #225c40; font: 12px; \
        color: #ffffff; font-weight: bold;")
    status_indicator.setText("Recording")
    start_time = QTime.currentTime()
    test_time.reset()
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
    global pulse_d
    global pulse_reset
    pulse_reset = pulse_d
    start_time = QTime.currentTime()
    test_time.reset()
    timer.start(1000)

#~~~~~~~~~~~~~~~~~ Function for Initial Data Window Display ~~~~~~~~~~~~~~~~~~~
data_window = None
tc_model = None
pulse_model = None
temp_avg_value_1a = None
temp_avg_value_1b = None
temp_avg_value_1c = None
temp_avg_value_2a = None
temp_avg_value_2b = None
temp_avg_value_2c = None
index_label = None
def show_data_window():
    global data_window
    global tc_model
    global pulse_model
    global temp_avg_value_1a
    global temp_avg_value_1b
    global temp_avg_value_1c
    global temp_avg_value_2a
    global temp_avg_value_2b
    global temp_avg_value_2c
    global index_label
    # Create a window for data view
    data_window = QWidget()
    data_window.setWindowTitle("Data")
    data_window.setGeometry(1000, 100, 400, 700)
    data_window.setStyleSheet("background-color: #0f0f0f;")
    
    layout = QVBoxLayout()
    layout.setSpacing(0)
    # Add a labels to the window
    label1 = QLabel("Temperatures (F):", data_window)
    label1.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
            font-family:{}; text-decoration: underline;".format(font_style))
    
    label2 = QLabel("Energy & Water:", data_window)
    label2.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
            font-family:{}; text-decoration: underline;".format(font_style))

    label3 = QLabel("Analysis:", data_window)
    label3.setStyleSheet("color: #ffffff; font: 14px; font-weight: bold; \
            font-family:{}; text-decoration: underline;".format(font_style))

    
#~~~~~ Section 1: Temperature Data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    tc_model = QStandardItemModel(8, 2)
    for row in range(8):
        for column in range(2):
            index = (row)+(column*8)
            item = QStandardItem("Temp {}: NA".format(index))
            tc_model.setItem(row, column, item)
    table_view1 = QTableView()
    table_view1.horizontalHeader().setVisible(False)
    table_view1.verticalHeader().setVisible(False)
    table_view1.setModel(tc_model)
    table_view1.setStyleSheet("background-color: #0f0f0f; color: #ffffff; font: 12px;"\
                          "border-style: solid; border-width: 0 1px 1px 1px;")
    
    # Temp Average
    temp_avg_layout1 = QHBoxLayout()
    label_1a = QLabel(" Average of Temps  ")
    label_1a.setStyleSheet("color: #ffffff; font: 14px;")
    temp_avg_layout1.addWidget(label_1a)
    temp_avg_value_1a = QLineEdit()
    temp_avg_value_1a.setStyleSheet("color: #ffffff; font: 14px;")
    temp_avg_layout1.addWidget(temp_avg_value_1a)
    label_1b = QLabel(" to ")
    label_1b.setStyleSheet("color: #ffffff; font: 14px;")
    temp_avg_layout1.addWidget(label_1b)
    temp_avg_value_1b = QLineEdit()
    temp_avg_value_1b.setStyleSheet("color: #ffffff; font: 14px;")
    temp_avg_layout1.addWidget(temp_avg_value_1b)
    temp_avg_value_1c = QLabel(" = NA")
    temp_avg_value_1c.setStyleSheet("color: #ffffff; font: 14px; font-weight:bold;")
    temp_avg_layout1.addWidget(temp_avg_value_1c)
    

    temp_avg_layout2 = QHBoxLayout()
    label_2a = QLabel(" Average of Temps  ")
    label_2a.setStyleSheet("color: #ffffff; font: 14px;")
    temp_avg_layout2.addWidget(label_2a)
    temp_avg_value_2a = QLineEdit()
    temp_avg_value_2a.setStyleSheet("color: #ffffff; font: 14px;")
    temp_avg_layout2.addWidget(temp_avg_value_2a)
    label_2b = QLabel(" to ")
    label_2b.setStyleSheet("color: #ffffff; font: 14px;")
    temp_avg_layout2.addWidget(label_2b)
    temp_avg_value_2b = QLineEdit()
    temp_avg_value_2b.setStyleSheet("color: #ffffff; font: 14px;")
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
    table_view2.setStyleSheet("background-color: #0f0f0f; color: #ffffff; font: 12px;"\
                          "border-style: solid; border-width: 0 1px 1px 1px;")

#~~~~~ Section 3: Analysis ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    index_label = QLabel("Current Index = NA", data_window) 
    index_label.setStyleSheet("color: #ffffff; font: 14px; font-family:{};".format(font_style))

    # Add spacers for layout styling
    spacer_item = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed)
    # Organize structure of layout 
    layout.addWidget(label1)
    layout.addItem(spacer_item)
    layout.addWidget(table_view1)
    layout.addItem(spacer_item)
    layout.addLayout(temp_avg_layout1)
    layout.addLayout(temp_avg_layout2)
    layout.addItem(spacer_item)
    layout.addWidget(label2)
    layout.addItem(spacer_item)
    layout.addWidget(table_view2)
    layout.addWidget(label3)
    layout.addWidget(index_label)

    data_window.setLayout(layout)
    data_window.show()

#~~~~~~~~~~~~~~~~~~~~~~ Display Graph Window Function ~~~~~~~~~~~~~~~~~~~~~~~~~
def show_graph_window():
    # Create a window for graph configuration
    graph_menu.exec()

#~~~~~~~~~~~~~~~~~~~~~~~~ Display Graph Setup Window  ~~~~~~~~~~~~~~~~~~~~~~~~~
graph_window = None
def set_graph_window():
    global graph_window

    graph_window = QWidget()
    graph_window.setWindowTitle("Setup Graph")
    graph_window.setGeometry(120, 150, 200, 200)
    graph_window.setStyleSheet("background-color: #0f0f0f;")
    
    layout = QVBoxLayout()
    layout.setSpacing(0)

    label1 = QLabel("Set Y Lower Bound")
    label1.setStyleSheet("color: #ffffff; font: 14px;")
    entry1 = QLineEdit()
    entry1.setStyleSheet("color: #ffffff; font: 14px;")
    label2 = QLabel("Set Y Upper Bound")
    label2.setStyleSheet("color: #ffffff; font: 14px;")
    entry2 = QLineEdit()
    entry2.setStyleSheet("color: #ffffff; font: 14px;")
    button_style =  "QPushButton {background-color: #2b2b2b; color: #ffffff;}" \
                "QPushButton:hover {background-color: #555555;}" \
                "QPushButton:pressed {background-color: #777777;}"
    set_button = QPushButton("Set Range")
    set_button.setStyleSheet(button_style)
    auto_button = QPushButton("Autoscale")
    auto_button.setStyleSheet(button_style)

    layout.addWidget(label1)
    layout.addWidget(entry1)
    layout.addWidget(label2)
    layout.addWidget(entry2)
    layout.addWidget(set_button)
    layout.addWidget(auto_button)

    graph_window.setLayout(layout)
    graph_window.show()
#~~~~~~~~~~~~~~~~~~~~~~~~ Display Config Setup Window  ~~~~~~~~~~~~~~~~~~~~~~~~
def handle_time_selection(index):
    selected_option = index
    time_dict = {0: 1, 1: 5, 2: 30, 3: 60}
    test_time.timing_interval = time_dict[index]

config_window = None
def set_config_window():
    global config_window

    config_window = QWidget()
    config_window.setWindowTitle("Test Configuration Setup")
    config_window.setGeometry(200, 200, 300, 500)
    config_window.setStyleSheet("background-color: #0f0f0f;")
    
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
    global data_
    if tc_model is not None:
        # Update the values in the table 
        for row in range(8):
            for column in range(2):
                index = (row)+(column*8)
                tc_model.item(row, column).setText("Temp {}:    {}".format(index, d[-1][index+8]))
    
    if temp_avg_value_1a is not None:
        try:
            t1a = int(temp_avg_value_1a.text())
            t1b = int(temp_avg_value_1b.text())
            t1_l = data_[t1a+6:t1b+7]
            tavg1 = np.mean(np.array([value for value in t1_l if value < 4000]))
            temp_avg_value_1c.setText(" = {}".format(round(tavg1, 1)))
        except Exception as e:
            temp_avg_value_1c.setText(" = NA")

        try:
            t2a = int(temp_avg_value_2a.text())
            t2b = int(temp_avg_value_2b.text())
            t2_l = data_[t2a+6:t2b+7]
            tavg2 = np.mean(np.array([value for value in t2_l if value < 4000]))
            temp_avg_value_2c.setText(" = {}".format(round(tavg2, 1)))
        except Exception as e:
            temp_avg_value_2c.setText(" = NA")

    if pulse_model is not None:
        # Update the values in pulse table
        for i in range(4):
            pulse_model.item(1, i).setText("Interval: {}".format(d[-1][i+2]))
        for i in range(4):
            pulse_model.item(2, i).setText("Total: {}".format(pulse_d[i]))

    if index_label is not None:
        index_label.setText("Current Index = {}".format(current_index))
           
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                             Setup Main UI 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the PySide6 application instance
app = QApplication(sys.argv)

# Set the window icon
app.setWindowIcon(QIcon("photos/tz-icon.png")) 

# Create the main window for the application
main_window = QMainWindow()
main_window.setWindowTitle("Testzilla")
main_window.setGeometry(100, 100, 900, 800)
main_window.setStyleSheet("QMainWindow {background-color: #000000;border: 1px solid white;}")

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
            font-family:{};".format(font_style))
time_label.setPixmap(QPixmap("photos/test_time1.png"))
time_label.setAlignment(Qt.AlignCenter)
time_layout.addWidget(time_label)
time_label_value = QLabel("0.0")
time_label_value.setStyleSheet("color: #ffffff; font: 30px; font-weight:bold;\
            font-family:{};".format(font_style)) #  
time_label_value.setAlignment(Qt.AlignCenter)
time_layout.addWidget(time_label_value)
spacer_item = QSpacerItem(10, 60, QSizePolicy.Expanding, QSizePolicy.Fixed)
time_layout.addItem(spacer_item)
header_layout.addLayout(time_layout)

# Header Subsection 3: Status and Ambient Temp
status_layout = QVBoxLayout()
status_label = QLabel("Status:")
status_label.setStyleSheet("color: #ffffff; font: 25px; font-weight: bold; \
            font-family:{};".format(font_style))
status_label.setPixmap(QPixmap("photos/status1.png"))
status_label.setAlignment(Qt.AlignCenter)
status_layout.addWidget(status_label)
status_indicator = QLabel("Not Recording")
status_indicator.setFixedSize(250, 27)
status_indicator.setStyleSheet("background-color: #b8494d; font: 12px; \
        color: {}; font-weight: bold; border-style: solid;".format(font_color1))
status_indicator.setAlignment(Qt.AlignCenter)
status_layout.addWidget(status_indicator)
ambient_label = QLabel("Ambient:")
ambient_label.setPixmap(QPixmap("photos/ambient1.png"))
ambient_label.setStyleSheet("color: #ffffff; font: 25px; font-weight: bold; \
            font-family:{};".format(font_style))
ambient_label.setAlignment(Qt.AlignCenter)
ambient_label_value = QLabel("NA")
ambient_label_value.setStyleSheet("color: #ffffff; font: 25px; font-weight: bold; \
            font-family:{};".format(font_style))
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
menubar.setStyleSheet("background-color: #0f0f0f; color: #ffffff; font: 10px;"\
        "font-family:{}; border-style: solid;"\
        "border-width: 0 1px 1px 1px;".format(font_style)) #; font-weight: bold

# Add a File menu
file_menu = menubar.addMenu("File")
# Add an action to the File menu
exit_action = QAction("Exit", main_window)
exit_action.setShortcut("Ctrl+Q")
exit_action.triggered.connect(main_window.close)
file_menu.addAction(exit_action)
# Add an action for new test file
new_test_action = QAction("New Test", main_window)
new_test_action.triggered.connect(fu.file_setup)
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
for i in range(8):
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

for i in range(8):
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
status_bar.setStyleSheet("QStatusBar {background-color: #0f0f0f; color: #ffffff; font: 10px;"\
"border-style: solid; border-width: 1px 1px 1px 1px; border-color: white;}")

# Add the status bar to the main window
main_window.setStatusBar(status_bar)

# Add a label to the status bar for system status updates
system_status_label = QLabel("")
system_status_label.setStyleSheet("color: #ffffff;")
status_bar.addPermanentWidget(system_status_label)

# Add a label to the status bar
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
    time_label_value.setText("{}".format(test_time.test_time_min))
#~~~~ Update Ambient Temp Label ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if d[-1][8] >=70 and d[-1][8] <80:
        ambient_label_value.setText("{}".format(d[-1][8]))
        ambient_label_value.setStyleSheet("color: #ffffff; font: 25px; font-weight:bold;\
            font-family:{};".format(font_style))
    elif d[-1][8] >=80:
        ambient_label_value.setText("{}".format(d[-1][8]))
        ambient_label_value.setStyleSheet("color: #b8494d; font: 25px; font-weight:bold;\
            font-family:{};".format(font_style))
    else:
        ambient_label_value.setText("{}".format(d[-1][8]))
        ambient_label_value.setStyleSheet("color: #4e94c7; font: 25px; font-weight:bold;\
            font-family:{};".format(font_style))
    
    global current_index
    current_index += 1
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Push Buttons
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set push button styles
button_style1 =  "QPushButton {background-color: #2b2b2b; color: #ffffff;}" \
                "QPushButton:hover {background-color: #225c40;}" \
                "QPushButton:pressed {background-color: #777777;}"
button_style2 =  "QPushButton {background-color: #2b2b2b; color: #ffffff;}" \
                "QPushButton:hover {background-color: #b8494d;}" \
                "QPushButton:pressed {background-color: #777777;}"
button_style3 =  "QPushButton {background-color: #2b2b2b; color: #ffffff;}" \
                "QPushButton:hover {background-color: #555555;}" \
                "QPushButton:pressed {background-color: #777777;}"
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
fig = plt.Figure(facecolor=(primary_color))
canvas = FigureCanvas(fig)
ax = fig.add_subplot(111)
ax.set_facecolor(primary_color)

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
timer.timeout.connect(lambda: fu.write_data(d[-1], testing, test_time.time_to_write))
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
        fu.file_setup(testing)
        status.append("Adding new file: {}".format(fu.file_name))

        app.exec()
    except Exception as e:
        print(e)

    finally:
        ni.close_daq()

    sys.exit()

