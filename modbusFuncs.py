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
import time

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Initialize modbus and connect to client
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def init(
    port="COM3", 
    baudrate=19200,  # 19200 9600
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
#                       Write to Modbus register
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def write_(client, register_address, command, device_address=1):
    """
    Write to specified modbus register: Pymodbus should handle encoding.
    Example for resetting energy accumulators:
    write_(client, register_address=20000, command=5555, device_address=1)
    """
    client.connect()
    
    try:
        # Send the command
        response = client.write_register(register_address, command, slave=device_address)
        if response.isError():
            print(f"Command sending failed: {response}")
        else:
            print("Command sent successfully")

    finally:
        client.close()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                       Read from Modbus registers
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def read_registers(client, starting_register, num_registers, device_address=1, *args):
    """
    Read from specified registers: Output will be binary in decimal format. 
    Will likely need to be passed through a conversion function depending on 
    format type.
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
            if len(args) > 0:

                response2 = client.read_holding_registers(
                    address=args[0],
                    count=args[1],
                    slave=device_address)
            else: response2 = None
            
            if response.isError():
                print(f"Modbus Error: {response}")
                return None
            else:
                result = response.registers
                if response2 is not None:
                    result2 = response2.registers
                else: result2 = None
                result.extend(result2)
                return result
        finally:
            # Close the Modbus connection
            client.close()
    else:
        time.sleep(1) # wait 1 second before retesting signal
        print("Failed to read from Shark 200 meter.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Conversions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def convert_float(data):

    binary_data = BinaryPayloadDecoder.fromRegisters(data, byteorder=Endian.Big, wordorder=Endian.Big)
    result = binary_data.decode_32bit_float()
    return result

def convert_32bit_int(data):

    binary_data = BinaryPayloadDecoder.fromRegisters(data, byteorder=Endian.Big, wordorder=Endian.Big)
    result = binary_data.decode_32bit_int()
    return result

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#             Read from all registers of interest on Shark 200
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_all(client, device_address=1):
    """
    Designed to read all registers of interest for Shark200 meter
    """
    try:
        register_group = read_registers(client, 999, 26, device_address, 1499, 2)
        V_AN = round(convert_float(register_group[0:2]), 1) # Register 999 - 1000
        V_BN = round(convert_float(register_group[2:4]), 1) # Register 1001 - 1002
        V_CN = round(convert_float(register_group[4:6]), 1) # Register 1003 - 1004
        V_AB = round(convert_float(register_group[6:8]), 1) # Register 1005 - 1006
        V_BC = round(convert_float(register_group[8:10]), 1) # Register 1007 - 1008
        V_CA = round(convert_float(register_group[10:12]), 1) # Register 1009 - 1010
        I_A = round(convert_float(register_group[12:14]), 1) # Register 1011 - 1012
        I_B = round(convert_float(register_group[14:16]), 1) # Register 1013 - 1014
        I_C = round(convert_float(register_group[16:18]), 1) # Register 1015 - 1016
        watts = round(convert_float(register_group[18:20]), 1) # Register 1017 - 1018
        pf = round(convert_float(register_group[24:26]), 2) # Register 1023 - 1024
        wh = convert_32bit_int(register_group[26:28]) # Register 1499 - 1500

        if I_A == 0: V_avg = V_BC
        elif I_B == 0: V_avg = V_CA
        elif I_C == 0: V_avg = V_AB
        else: V_avg = round(sum([V_AB, V_BC, V_CA])/3, 1) 
        return V_avg, watts, wh, V_AN, V_BN, V_CN, V_AB, V_BC, V_CA, I_A, I_B, I_C, pf

    except TypeError:
        return None
    

def data_stream(client, stack):
    """
    Read modbus data continuously. Function designed for threading.
    """
    if client.connect():
        while True:
            try:
                mb_data = list(get_all(client))
                if len(stack) > 0:
                    stack.pop(0)
                stack.append(mb_data)
            except TypeError:
                pass
            except Exception as e:
                print(e)


if __name__ == "__main__":
    client = init()
    write_(client, 20000, 5555, device_address=1)
    while True:
        start = time.time()
        data = get_all(client)
        print(data)
        process_time = time.time() - start
        print(f"Process Time: {process_time}")

    # a = read_registers(client, 999, 2, 1, 1499, 2)
