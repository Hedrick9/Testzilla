#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                  IMPORTS/Libraries used for program and UI 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, datetime
import threading
import niDAQFuncs as ni
from PySide6.QtCore import QTime, QTimer, QSize, Qt
from PySide6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem, QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
        QHBoxLayout, QPushButton, QListWidget, QGridLayout, QLabel, QLineEdit, 
        QStatusBar, QFrame, QTableView, QDialog, QMenu)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            START OF PROGRAM
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Status Updates from System
status = []
testing = False # Test Status
# Simulated Data File 
file_name = "scratch_data_0.csv"
# Color Palette
primary_color = "#0f0f0f"
secondary_color = "#2b2b2a"
font_color1 = "#ffffff"
font_style = "Courier New"
start_time = QTime.currentTime()
print(start_time)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            Initialize DAQ(s)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#daq_thread = threading.Thread(target=ni.init_daq, args=(1, True,))
#daq_thread.start()
status.append("Initializing DAQ...")
ni.init_daq()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Setup Test File
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define relevant functions prior to their call
# Define the update_plot function to update the Matplotlib plot
d = []
last_data = [0, 0, 0, 0]
pulse_d = [0, 0, 0, 0]
pulse_reset = [0, 0, 0, 0]
def get_data():
    global last_data
    global pulse_d
    global pulse_reset
    tod = datetime.now().strftime("%H:%M:%S")
    # Try to read in data from ni hardware; otherwise return list of 0's
    try:
        data_ = list(np.around(np.array(ni.read_daq()),1))
        data = list(np.array(data_[:4])-np.array(last_data)) + ["open" if x > 4000 else x for x in data_[4:]]
        data.insert(0, tod)
        data.insert(1, 0)
        d.append(data)
        pulse_d = list(np.array(data_[:4])-np.array(pulse_reset))
        last_data = data_[:4]
    except Exception as e:
        print(e)
        status.append("error reading from ni-DAQ")
        data = list(np.zeros(20))
        data.insert(0, tod)
        d.append(data)

def update_plot():
    # Update the plot with new data
    #data = pd.read_csv(file_name)
    df = pd.DataFrame(d)

# Use for simulated data stream    
#    if len(data) < 50:
#        x = data['Time']
#        y1 = data['y1']
#        y2 = data['y2']
#        y3 = data['y3']
#    else:
#        x = data['Time'][-50:-1]
#        y1 = data['y1'][-50:-1]
#        y2 = data['y2'][-50:-1]
#        y3 = data['y3'][-50:-1]

    if len(d) < 3600:
        y1 = df[4]
        y2 = df[5]
        y3 = df[6]
    else:
        y1 = df[4][-3600:-1]
        y2 = df[5][-3600:-1]
        y3 = df[6][-3600:-1]
    
    ax.clear()    
    ax.plot(y1, label="1", lw=0.5)
    ax.plot(y2, label="2", lw=0.5)
    ax.plot(y3, label="3", lw=0.5)
    
   
    ax.legend(loc='lower right', frameon=False, ncol=3, labelcolor="#ffffff")
    ax.set_facecolor("#121212")
    ax.tick_params(labelbottom=False, labelcolor="#ffffff", color="#ffffff", labelsize=8)
    #ax.spines[:].set_visible(False)#set_color("#ffffff")
    ax.spines[:].set_color(secondary_color)
    ax.spines[:].set_linewidth(0.25)
    plt.grid(axis='y', linewidth=0.25) #color="white"
    # Call canvas.draw() to update the plot on the canvas
    canvas.draw()


def update_system_status(status):
     
    system_status_label.setText(status)

# Slot function for handling start button click event
def start_test():
    global testing
    global start_time
    global d
    global pulse_d
    global pulse_reset
    start_time = QTime.currentTime()
    testing = True
    d = []
    timer.start(1000)  # Start the timer to update the plot every 1000 milliseconds (1 second)
    pulse_reset = pulse_d
    status.append("testing in progress...")

# Slot function for handling stop button click event
def stop_test():
    global testing
    testing = False
    timer.stop()  # Stop the timer to stop updating the plot
    status.append("testing concluded.")
    update_system_status(status[-1])

# Slot function for handling reset button click event
def reset_():
    global start_time
    global pulse_d
    global pulse_reset
    start_time = QTime.currentTime()
    pulse_reset = pulse_d

data_window = None
tc_model = None
pulse_model = None
def show_data_window():
    global data_window
    global tc_model
    global pulse_model
    # Create a window for data view
    data_window = QWidget()
    data_window.setWindowTitle("Data")
    data_window.setGeometry(600, 100, 400, 700)
    data_window.setStyleSheet("background-color: #0f0f0f;")
    
    layout = QVBoxLayout()
    data_window.setLayout(layout)
    # Add a labels to the window
    label1 = QLabel("Temperatures (F):", data_window)
    label1.setStyleSheet("color: #ffffff; font: 12px; font-weight: bold; \
            font-family:{}; text-decoration: underline;".format(font_style))
    
    label2 = QLabel("Energy & Water:", data_window)
    label2.setStyleSheet("color: #ffffff; font: 12px; font-weight: bold; \
            font-family:{}; text-decoration: underline;".format(font_style))
    
    # Add Table for Thermocouple data
    tc_model = QStandardItemModel(8, 2)
    for row in range(8):
        for column in range(2):
            index = (row+1)+(column*8)
            item = QStandardItem("Temp {}: NA".format(index))
            tc_model.setItem(row, column, item)
    table_view1 = QTableView()
    table_view1.horizontalHeader().setVisible(False)
    table_view1.verticalHeader().setVisible(False)
    table_view1.setModel(tc_model)
    table_view1.setStyleSheet("background-color: {}; color: #ffffff; font: 10px;"\
                          "border-style: solid; border-width: 0 1px 1px 1px;".format(primary_color))
    
    # Add table for pulse data
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
    table_view2.setStyleSheet("background-color: #0f0f0f; color: #ffffff; font: 10px;"\
                          "border-style: solid; border-width: 0 1px 1px 1px;")
    # Organize structure of layout 
    layout.addWidget(label1)
    layout.addWidget(table_view1)
    layout.addWidget(label2)
    layout.addWidget(table_view2)

    data_window.show()

tc_graph_list = []
def show_graph_window():
    global tc_graph_list
    # Create a window for graph configuration
    graph_menu.exec()

def update_data_window():

    if tc_model is not None:
        # Update the values in the table 
        for row in range(8):
            for column in range(2):
                index = (row+1)+(column*8)
                tc_model.item(row, column).setText("Temp {}: {}".format(index, d[-1][index+5]))

    if pulse_model is not None:
        # Update the values in pulse table
        for i in range(4):
            pulse_model.item(1, i).setText("Interval: {}".format(d[-1][i+2]))
        for i in range(4):
            pulse_model.item(2, i).setText("Total: {}".format(pulse_d[i]))
           

def write_data(file_name, data):
    global testing
    if testing:
        with open(file_name, 'a', newline='') as file_data:
            csvWriter = csv.writer(file_data, delimiter=',')
            csvWriter.writerow(data)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                             Setup Main UI 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create the PySide6 application instance
app = QApplication(sys.argv)

# Set the window icon
app.setWindowIcon(QIcon("tz-icon.png")) 

# Create the main window for the application
main_window = QMainWindow()
main_window.setWindowTitle("Testzilla")
main_window.setGeometry(100, 50, 800, 650)
main_window.setStyleSheet("QMainWindow {background-color: #0f0f0f; border: 1px solid white;}")

# Create central widget for main window to hold other widgets
central_widget = QWidget()
main_window.setCentralWidget(central_widget)

# Create a vertical layout for the widget
main_layout = QVBoxLayout(central_widget)

# Set the layout for the widget
main_window.setLayout(main_layout)

# Create Horizontal layout for more data displays
second_layout = QHBoxLayout()
frame1 = QFrame()
frame1.setFrameShape(QFrame.Box)
frame2 = QFrame()
frame2.setFrameShape(QFrame.Box)
second_layout.addWidget(frame1)
second_layout.addWidget(frame2)
main_layout.addLayout(second_layout)

# Create a QStandardItemModel for data display
model = QStandardItemModel(2, 1)
#for row in range(4):
#    for column in range(2):
#        item = QStandardItem("Row {}, Column {}".format(row, column))
#        model.setItem(row, column, item)
time_item1 = QStandardItem("Test Time:")
time_item2 = QStandardItem("{}".format("0.0"))
model.setItem(0, 0, time_item1)
model.setItem(1, 0, time_item2)
table_view1 = QTableView(frame1)
table_view1.horizontalHeader().setVisible(False)
table_view1.verticalHeader().setVisible(False)
table_view1.setModel(model)
table_view1.setStyleSheet("background-color: #0f0f0f; color: #ffffff; font: 15px;"\
        "font-family:{}; font-weight: bold; border-style: solid;"\
        "border-width: 0 1px 1px 1px;".format(font_style))
table_view2 = QTableView(frame2)
table_view2.horizontalHeader().setVisible(False)
table_view2.verticalHeader().setVisible(False)
table_view2.setModel(model)
table_view2.setStyleSheet("background-color: #0f0f0f; color: #ffffff; font: 10px;"\
                      "border-style: solid; border-width: 0 1px 1px 1px;")

second_layout.addWidget(table_view1)
second_layout.addWidget(table_view2)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                Menu Bar
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a menu bar object
menubar = main_window.menuBar()
menubar.setStyleSheet("background-color: #0f0f0f; color: #ffffff; font: 10px;"\
        "font-family:{}; font-weight: bold; border-style: solid;"\
        "border-width: 0 1px 1px 1px;".format(font_style))

# Add a File menu
file_menu = menubar.addMenu("File")
# Add an action to the File menu
exit_action = QAction("Exit", main_window)
exit_action.setShortcut("Ctrl+Q")
exit_action.triggered.connect(main_window.close)
file_menu.addAction(exit_action)

# Add a Setup menu
setup_menu = menubar.addMenu("Setup")

# Add a Data menu
data_menu = menubar.addMenu("Data")
# Add anaction to the Data menu
view_data_action = QAction("View Data", main_window)
view_data_action.triggered.connect(show_data_window)
data_menu.addAction(view_data_action)

# Add a Graph menu
graph_menu = QMenu("Graph", menubar)
tc_items = []
for i in range(8):
    item = QAction("Temp {}".format(i+1), graph_menu, checkable=True)
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
for action in graph_menu.actions():
    if action.isCheckable() and action.isChecked():
        print(action.text())

# Add a Configuration menu
config_menu = menubar.addMenu("Config")


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

def update_elapsed_time():
# Calculate the elapsed time since the program started
    time_difference = start_time.secsTo(QTime.currentTime())
    elapsed_time = QTime(0, 0, 0).addSecs(time_difference).toString("hh:mm:ss")
    test_time = round(time_difference / 60, 2)
    status_bar_label.setText("Elapsed Time: {}".format(elapsed_time))
    
    model.item(1, 0).setText("{}".format(test_time))
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Push Buttons
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set push button styles
button_style =  "QPushButton {background-color: #333333; color: #ffffff;}" \
                "QPushButton:hover {background-color: #555555;}" \
                "QPushButton:pressed {background-color: #777777;}"
# Create a "Start" push button and its slot for handling button click event
start_button = QPushButton("Start")
start_button.setStyleSheet(button_style)
start_button.clicked.connect(start_test)

# Create a "Stop" push button
stop_button = QPushButton("Stop")
stop_button.setStyleSheet(button_style)
stop_button.clicked.connect(stop_test)

# Create a "Reset" push button
reset_button = QPushButton("Reset")
reset_button.setStyleSheet(button_style)
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
# Add the canvas to the layout
main_layout.addWidget(canvas)
# Add the push buttons to the layout
main_layout.addWidget(start_button)
main_layout.addWidget(stop_button)
main_layout.addWidget(reset_button)


# Create a QTimer to call the update_plot function at a fixed interval
timer = QTimer()
timer.start(1000)
timer.timeout.connect(get_data)
timer.timeout.connect(update_plot)
timer.timeout.connect(update_data_window)
timer.timeout.connect(update_elapsed_time)
timer.timeout.connect(lambda: update_system_status(status[-1]))
timer.timeout.connect(lambda: write_data(file_name, d[-1]))

if __name__ == "__main__":

    try:
        # Show the application and start the PySide6 event loop
        main_window.show()

        # Create Data directory if it does not exist
        current_directory = os.getcwd()
        if not os.path.exists(current_directory + "/Data"):
            os.mkdir(current_directory + "/Data")
            print("New Data directory added...\n")
        
        # Create unique data file
        os.chdir(current_directory + "/Data")
        file_date = date.today().strftime("%m-%d-%y")
        
        headers = ["Time of Day", "Test Time", "Counter 1","Counter 2","Counter 3","Counter 4",]
        for i in range(1, 17):
            headers.append("Temp {}".format(i))
            
        for i in range(50):
            if not os.path.isfile(os.getcwd() +'/'+ file_date +'_'+ str(i) + ".csv"):
                file_name = file_date + '_' + str(i) + ".csv"
                print("Adding new file: {}\n".format(file_name))
                status.append("Adding new file: {}".format(file_name))
                break
            elif i==49:
                print("Maximum files achieved for the day. Please remove some and try again.")
        
        with open(file_name, 'a') as file_data:
            csvWriter = csv.writer(file_data, delimiter=',')
            csvWriter.writerow([file_date])
            csvWriter.writerow(headers)

        sys.exit(app.exec())
    except Exception as e:
        print(e)

    finally:
        ni.close_daq()

