# Testzilla
An application that provides an intuitive user interface for laboratory testing. A backend designed to interface with multiple DAQ systems.

## Testzilla TODO List:
- [x] Fix format of test time
- [x] Fix graph config: slect list of items
- [x] Add custom graph scale feature for y-axis
- [x] Fix graphing for null/open channels
- [x] Allow for new file creation
- [x] Work on config page: Time sampling
- [ ] Work on config page: tc offsets, look into file upload
- [x] Incorporate modbus read capabilites
    - [x] Read in modbus data from Shark meter/General device
    - [x] Determine registers necessary 
- [x] Incorporate modbus write function for accumulator reset
- [x] Incorporate ni AI module (ni-9215)
- [x] Add 2 tc module capability - detect how many modules available and scale appropriately?
- [x] Fix timing and time data
- [x] Averaging for temperature readings 
- [ ] Averaging for pulse data
- [x] Add ambient channel to Main window
- [ ] Rename channel ability
- [x] Correct reset timing
- [x] Add t0 timestamp for start test and resets
- [x] Rename default temp channel 0
- [x] Copy data feature
- [x] Fix Spacing for widgets
- [x] Fix Window close issue
- [ ] Logging extra channel specified by user (config page)
- [x] Averaging for intervals greater than 1 second
- [x] Logging data for intervals greater than 1 second
- [x] Swap upper and lower bound for graph range
- [x] Create table for modbus data in data window
- [ ] Add fry test capability
- [ ] Add burger test capability
- [ ] Test Analog input reading w/ RH meter (avg various readings?)

## Software Requirements:
### NI MAX and related drivers: 
***NI MAX:***
```markdown
https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQwCAO&l=en-US
```
***NI DAQ-mx:***
```markdown
https://www.ni.com/en-us/support/downloads/drivers/download.ni-daq-mx.html#480879
```
### Python 3.11 or later: 
```markdown
https://www.python.org/
```
***Python Dependencies***
- pandas
- matplotlib
- nidaqmx
- PySide6
- pymodbus
- pyserial
```Powershell
pip install pandas matplotlib nidaqmx PySide6 pymodbus pyserial
```

```python
test = "This is a test"
```

