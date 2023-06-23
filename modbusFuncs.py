#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Module/Program Name: modbusFuncs.py
# Module Description:
# The following program is to read in modbus RTU data via RS485 (RS485 to USB).
# Original Author: Russell Hedrick
# Original Date: 06/23/2023
# Last Edit: 06/23/2023 
# Edit Description:
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                   Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from pymodbus.client import ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder 

# Modbus RTU configuration
port = "COM3" # Serial port (USB port on computer)
baudrate = 9600
bytesize = 8 # data bits
parity = 'N'
stopbits = 1 

# Modbus address of the Shark 200 meter
device_address = 1

# Modbus register address to read
starting_register = 999 # Starting register address
num_registers = 10 # number of registers to read

# Establish Modbus RTU connection
client = ModbusSerialClient(
        port=port,
        baudrate=baudrate,
        bytesize=bytesize,
        parity=parity,
        stopbits=stopbits,
        timeout=1 # communication timeout in seconds
        )

# Connect to the Shark 200 meter
if client.connect():
    try:
        # Read holding registers
        response = client.read_holding_registers(
            address=starting_register,
            count=num_registers,
            slave=device_address
        )
        
        if response.isError():
            print(f"Modbus Error: {response}")
        else:
            data = response.registers
            voltage_binary = data[0:2]
            decoded = BinaryPayloadDecoder.fromRegisters(voltage_binary, byteorder=Endian.Big, wordorder=Endian.Big)
            voltage = decoded.decode_32bit_float()
            print(voltage_binary)
            # decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            # data = decoder.decode_32bit_float()
            # Extract the data from the response

            # Process the data as per your requirements
            print(f"Received data: {data}")
            print(voltage)
            
    finally:
        # Close the Modbus connection
        client.close()

else:
    print("Failed to connect to the Shark 200 meter.")


