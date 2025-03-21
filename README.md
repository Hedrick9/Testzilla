# Testzilla
An application that provides an intuitive user interface for laboratory testing. A back-end designed to interface with multiple DAQ systems.

## Testzilla Current Version: 2.05

## Testzilla TODO List:
- [x] Fix format of test time
- [x] Fix graph config: slect list of items
- [x] Add custom graph scale feature for y-axis
- [x] Fix graphing for null/open channels
- [x] Add new file creation feature
- [x] Work on config page: 
    - [x] Time sampling
    - [x] TC offsets: look into file upload
    - [x] Logging extra channel specified by user 
- [x] Incorporate modbus read capabilites
    - [x] Read in modbus data from Shark meter/General device
    - [x] Determine registers necessary 
- [x] Incorporate modbus write function for accumulator reset
- [x] Incorporate ni AI module (ni-9215)
- [x] Add 2 tc module capability - detect how many modules available and scale appropriately?
- [x] Fix timing and time data
- [x] Averaging for temperature readings 
- [x] Energy Rate calculator
- [x] Add ambient channel to Main window
- [x] Rename channel ability
- [x] Correct reset timing
- [x] Add t0 timestamp for start test and resets
- [x] Rename default temp channel 0
- [x] Copy data feature
- [x] Fix Spacing for widgets
- [x] Fix Window close issue
- [x] Averaging for intervals greater than 1 second
- [x] Logging data for intervals greater than 1 second
- [x] Swap upper and lower bound for graph range
- [x] Create table for modbus data in data window
- [x] Test Analog input reading w/ RH meter (avg various readings?)
- [x] Update ni script for greater configuration flexibility 
- [x] Create Data class for all data related processes
- [x] Create UI script to isolate UI processes from main script 
- [x] Change button layout (horizontal versus vertical)
- [x] Add emergency data dump feature 
- [x] Add analog section on data window
- [ ] Add fry test capability
- [ ] Add burger test capability
- [ ] Update modbus script 
    - [ ] Investigate Alternative Libraries
    - [ ] Allow for manual reboot

## Software Requirements:
### NI MAX and related drivers: 
***NI MAX & NI DAQ-mx:***
```markdown
https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#521556
```
### Python 3.12 or later: 
```markdown
https://www.python.org/
```
***Python Dependencies***
- pandas
- matplotlib
- nidaqmx
- PySide6
- pymodbus==3.5.4
- minimalmodbus
- pyserial
```Powershell
pip install pandas matplotlib nidaqmx PySide6 pymodbus==3.5.4 minimalmodbus pyserial
```

```python
test = "This is a test"
```

