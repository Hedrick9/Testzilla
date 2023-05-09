#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                  IMPORTS/Libraries used for program and UI 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime
import threading
import NiDAQFuncs as ni
from PySide6.QtCore import QTime, QTimer, QSize, Qt
from PySide6.QtGui import QIcon, QAction, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
        QHBoxLayout, QPushButton, QListWidget, QGridLayout, QLabel, QLineEdit, 
        QStatusBar, QFrame, QTableView, QDialog)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            START OF PROGRAM
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Status Updates from System
status = []
# Test Status
testing = False
# Simulated Data File 
file_name = "scratch_data_0.csv"
# Color Palette
primary_color = "#0f0f0f"
secondary_color = "#2b2b2a"
font_color1 = "#ffffff"
start_time = QTime.currentTime()
print(start_time)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                            Initialize DAQ(s)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#daq_thread = threading.Thread(target=ni.init_daq, args=(1, True,))
#daq_thread.start()
import time
status.append("Initializing DAQ...")
ni.init_daq()
status.append("Done")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Setup Test File
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define relevant functions prior to their call
# Define the update_plot function to update the Matplotlib plot
d = []
def update_plot():
    # Get x and y data from CSV or DAQ
    # Update the plot with new data
    data = pd.read_csv(file_name)
    more_data = ni.read_daq()
    d.append(more_data)
    df = pd.DataFrame(d)
    
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

    if len(d) < 50:
        y1 = df[0]
        y2 = df[1]
        y3 = df[2]
    else:
        y1 = df[0][-50:-1]
        y2 = df[1][-50:-1]
        y3 = df[2][-50:-1]
    
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
def start_graph():
    timer.start(1000)  # Start the timer to update the plot every 1000 milliseconds (1 second)

# Slot function for handling stop button click event
def stop_graph():
    timer.stop()  # Stop the timer to stop updating the plot

# Slot function for handling reset button click event
def reset_():
    global start_time
    start_time = QTime.currentTime()

data_window = None
def show_data_window():
    global data_window
    # Create a window for data view
    data_window = QWidget()
    data_window.setWindowTitle("Data")
    data_window.setGeometry(600, 50, 400, 600)
    data_window.setStyleSheet("background-color: #0f0f0f;")
    
    # Add a label to the window
    label = QLabel("View Data Below:", data_window)
    layout = QVBoxLayout()
    layout.addWidget(label)
    data_window.setLayout(layout)

    # Show the Data View window
    data_window.show()

def write_data(file_name, data):
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
model = QStandardItemModel(4, 2)
for row in range(4):
    for column in range(2):
        item = QStandardItem("Row {}, Column {}".format(row, column))
        model.setItem(row, column, item)
table_view1 = QTableView(frame1)
table_view1.horizontalHeader().setVisible(False)
table_view1.verticalHeader().setVisible(False)
table_view1.setModel(model)
table_view1.setStyleSheet("background-color: #0f0f0f; color: #ffffff; font: 10px;"\
                      "border-style: solid; border-width: 0 1px 1px 1px;")
table_view2 = QTableView(frame1)
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
                      "border-style: solid; border-width: 0 1px 1px 1px;")

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
graph_menu = menubar.addMenu("Graph")

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
   #  
   # hours = elapsed_time.hour()
   # minutes = elapsed_time.minute() 
   # seconds = elapsed_time.second() % 60
   # Update the label text with the elapsed time
    status_bar_label.setText("Elapsed Time: {}".format(elapsed_time))

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
start_button.clicked.connect(start_graph)

# Create a "Stop" push button
stop_button = QPushButton("Stop")
stop_button.setStyleSheet(button_style)
stop_button.clicked.connect(stop_graph)

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
timer.timeout.connect(update_plot)
timer.timeout.connect(update_elapsed_time)
timer.timeout.connect(update_system_status(status[-1]))


if __name__ == "__main__":

    try:
        # Show the application and start the PySide6 event loop
        main_window.show()

        # Create Data directory if it does not exist
        current_directory = os.getcwd()
        if not os.path.exists(current_directory + "/Data"):
            os.mkdir(current_directory + "/Data")
            print("New Data directory added...\n")
            status.append("New Data directory added...")
        
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

