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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Initialize modbus and connect to client
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def init(
    port="COM3", 
    baudrate=9600, 
    bytesize=8,
    parity='N', 
    stopbits=1, 
    device_address=1):
    """
    Serve as a modbus server/master and open up a modbus serial connection 
    with a client/device at a specified port
    Modbus RTU configuration:
    port - Serial port (USB port on computer: Use device manager to locate)
    baudrate - bit rate or communication speed (9600 by default)
    bytesize - size of each register response 
    parity - none
    """

    client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=1 # communication timeout in seconds
            )

    try:
        return client
    except Exception as e:
        print("Failed to establish modbus connection.")
        return None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Read from Modbus float register
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def read_float(client, starting_register, num_registers, device_address=1):
    """
    Read from 32-bit floating registers: Convert to decimal
    client - Client object established during init function
    starting_register - First register read
    num_registers - Number of registers read after first register read
    device_address - Address of device you are connected to (1 by default)
    """
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
                return None
            else:
                data = response.registers
                voltage_binary = data[0:2]
                binary_data = BinaryPayloadDecoder.fromRegisters(data, byteorder=Endian.Big, wordorder=Endian.Big)
                result = binary_data.decode_32bit_float()
                return result
        finally:
            # Close the Modbus connection
            client.close()
    else:
        print("Failed to connect to the Shark 200 meter.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#             Read from all registers of interest on Shark 200
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_all(client, device_address=1):
    """
    Designed to read all registers of interest for Shark200 meter
    """
    V_AN = round(read_float(client, 999, 2, device_address), 1)
    V_BN = round(read_float(client, 1001, 2, device_address), 1)
    V_CN = round(read_float(client, 1003, 2, device_address), 1)
    
    return V_AN, V_BN, V_CN



if __name__ == "__main__":

    client = init()
    data = get_all(client)
    print(data)
    
