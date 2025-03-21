"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                 HEADER 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Title:       modbusFuncs.py 
Origin Date: 06/23/2023
Revised:     03/18/2025
Author(s):   Russell Hedrick
Contact:     rhedrick@frontierenergy.com
Description:

The following script is designed to interface with devices via modbus RTU. 
The assumption is that the hardware setup is RS485 converted to USB.

"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                   Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import minimalmodbus
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder 
import serial
import time
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                   Initialize modbus and connect to client
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def init(
    port="COM3", 
    device_address=1,
    baudrate=19200,  # 19200 9600
    bytesize=8,
    parity='N', 
    stopbits=1):
    """
    Serve as a modbus server/master and open up a modbus serial connection 
    with a client/device at a specified port
    Modbus RTU configuration:
    port - Serial port (USB port on computer: Use device manager to locate)
    baudrate - bit rate or communication speed (19200 by default)
    bytesize - size of each register response 
    parity - none
    """

    client = minimalmodbus.Instrument(port, device_address)
    client.serial.baudrate = baudrate
    client.serial.bytesize = bytesize
    client.serial.parity = minimalmodbus.serial.PARITY_NONE
    client.serial.stopbits = 1 
    client.serial.mode = minimalmodbus.MODE_RTU

    client.clear_buffers_before_each_transaction = True
    client.close_port_after_each_call = True

    try:
        return client
    except Exception as e:
        print("Failed to establish modbus connection.")
        return None
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                       Write to Modbus register
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def write_(client, register_address, command):
    """
    Write to specified modbus register: 
    Example for resetting energy accumulators:
    write_(client, register_address=20000, command=5555, device_address=1)
    """
    
    try:
        # Send the command
        response = client.write_register(register_address, command)
        print("Command sent successfully")

    except Exception as e:
        print(e)
        print(f"Failure to send Modbus command: {response}")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Conversions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def convert_float(data):

    binary_data = BinaryPayloadDecoder.fromRegisters(data, byteorder=Endian.BIG, wordorder=Endian.BIG)
    result = binary_data.decode_32bit_float()
    return result

def convert_32bit_int(data):

    binary_data = BinaryPayloadDecoder.fromRegisters(data, byteorder=Endian.BIG, wordorder=Endian.BIG)
    result = binary_data.decode_32bit_int()
    return result

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#             Read from all registers of interest on Shark 200
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_all(client):
    """
    Designed to read all registers of interest for Shark200 meter
    """
    try:
        register_group1 = client.read_registers(999, 26, 3)
        register_group2 = client.read_registers(1505, 2, 3)
        V_AN = round(convert_float(register_group1[0:2]), 1) # Register 999 - 1000
        V_BN = round(convert_float(register_group1[2:4]), 1) # Register 1001 - 1002
        V_CN = round(convert_float(register_group1[4:6]), 1) # Register 1003 - 1004
        V_AB = round(convert_float(register_group1[6:8]), 1) # Register 1005 - 1006
        V_BC = round(convert_float(register_group1[8:10]), 1) # Register 1007 - 1008
        V_CA = round(convert_float(register_group1[10:12]), 1) # Register 1009 - 1010
        I_A = round(convert_float(register_group1[12:14]), 1) # Register 1011 - 1012
        I_B = round(convert_float(register_group1[14:16]), 1) # Register 1013 - 1014
        I_C = round(convert_float(register_group1[16:18]), 1) # Register 1015 - 1016
        watts = round(convert_float(register_group1[18:20]), 1) # Register 1017 - 1018
        pf = round(convert_float(register_group1[24:26]), 2) # Register 1023 - 1024
        wh = convert_32bit_int(register_group2) # Register 1499 - 1500

        if I_A == 0: V_avg = V_BC
        elif I_B == 0: V_avg = V_CA
        elif I_C == 0: V_avg = V_AB
        else: V_avg = round(sum([V_AB, V_BC, V_CA])/3, 1) 
        return V_avg, watts, wh, V_AN, V_BN, V_CN, V_AB, V_BC, V_CA, I_A, I_B, I_C, pf

    except TypeError:
        return None


def data_stream(client, data):
    """
    Read modbus data continuously. Function designed for threading.
    """
    while True:    
        try:
            mb_data = list(get_all(client))
            stack = data.mb_data
            if len(stack) > 0:
                stack.pop(0)
            stack.append(mb_data)
            time.sleep(0.1)
            data.mb_connected = True
        except TypeError:
            pass
        except serial.serialutil.SerialException: # Connection Lost
            data.mb_connected = False
            time.sleep(1)
        except minimalmodbus.InvalidResponseError: # Invalid Response
            pass # Ignore missed package 
        except Exception as e:
            print(e)


if __name__ == "__main__":
    client = init(port="COM3")

    # data = client.read_registers(999,4,3)
    pt,i = [], 0
    while i < 100:
        pts = time.time()
        data = get_all(client)
        ptf = time.time() - pts
        pt.append(ptf)
        i+=1
        
        print(data)
        time.sleep(.1)
        print(f"Process Time: {ptf}")

    print(f"Mean Process Time: {sum(pt)/len(pt)}")
    
    response = write_(client, 20000, 5555)
