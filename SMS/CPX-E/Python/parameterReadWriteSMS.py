from pyModbusTCP.client import ModbusClient
from time import sleep
import struct

# ----------- Helper Functions -----------

def float_to_modbus_registers_swap_endian(float_value):
    # Convert the float to its 32-bit IEEE 754 representation (packed as big-endian)
    packed = struct.pack('!f', float_value)  # '!f' means big-endian 4-byte float
    # Unpack the 4-byte float into a 32-bit unsigned integer
    unpacked = struct.unpack('!I', packed)[0]  # '!I' means big-endian unsigned int
    
    # Split the 32-bit integer into two 16-bit registers (big-endian)
    register_1 = (unpacked >> 16) & 0xFFFF  # Get the high 16 bits
    register_2 = unpacked & 0xFFFF         # Get the low 16 bits
    
    # Swap the endianness of each 16-bit register
    # This is done by reversing the byte order of each 16-bit value
    register_1_swapped = (register_1 >> 8) | ((register_1 & 0xFF) << 8)
    register_2_swapped = (register_2 >> 8) | ((register_2 & 0xFF) << 8)
    
    return register_1_swapped, register_2_swapped

# TCP auto connect on modbus request, close after it
# c = ModbusClient(host="192.168.1.199", auto_open=True, auto_close=True)

# TCP auto connect on first modbus request
# Specify the IP address of the CPX-E-EP module
c = ModbusClient(host="192.168.1.199", port=502, unit_id=1, auto_open=True)

# Use the index number specified in the SMS user manual
def Fun_Read(index):
    c.write_single_register(61,5)
    c.write_single_register(62,0)
    c.write_single_register(63,index)
    c.write_single_register(64,0)
    c.write_single_register(65,0)
    c.write_single_register(60,50)
    while(c.read_holding_registers(60,1) != [0]):
         regs = c.read_holding_registers(66,4)
    if regs:
         print(str(index) + "=" + str(regs))
    else:
         print("read error")

def Fun_Write_SpeedIn(value, module, channel):
     c.write_single_register(61,module)
     c.write_single_register(62,channel)
     c.write_single_register(63,256)
     c.write_single_register(64,0)
     c.write_single_register(65,1)
     c.write_single_register(66,value)
     c.write_single_register(60,51)

def Fun_Write_SpeedOut(value, module, channel):
     c.write_single_register(61,module)
     c.write_single_register(62,channel)
     c.write_single_register(63,257)
     c.write_single_register(64,0)
     c.write_single_register(65,1)
     c.write_single_register(66,value)
     c.write_single_register(60,51)

def Fun_Write_Force(value, module, channel):
     c.write_single_register(61,module)
     c.write_single_register(62,channel)
     c.write_single_register(63,258)
     c.write_single_register(64,0)
     c.write_single_register(65,1)
     c.write_single_register(66,value)
     c.write_single_register(60,51)

def Fun_Write_Intermediate_Position(value, module, channel):
    register_1, register_2 = float_to_modbus_registers_swap_endian(value)
    c.write_single_register(61,module)
    c.write_single_register(62,channel)
    c.write_single_register(63,264)
    c.write_single_register(64,0)
    c.write_single_register(65,4)
    c.write_single_register(66,register_1)
    c.write_single_register(67,register_2)
    c.write_single_register(60,51)

def Fun_Write_End_Position(value, module, channel):
    register_1, register_2 = float_to_modbus_registers_swap_endian(value)
    c.write_single_register(61,module)
    c.write_single_register(62,channel)
    c.write_single_register(63,262)
    c.write_single_register(64,0)
    c.write_single_register(65,4)
    c.write_single_register(66,register_1)
    c.write_single_register(67,register_2)
    c.write_single_register(60,51)

# ----------- Main Program -----------

# print("ISDU Status: " + str(c.read_holding_registers(60,1)))

# In CPX-E, module numbers start at 0. For example, CPX-E-EP module = 0
# In CPX-E-4IOL, IO-Link ports start at 0. For example, first port will be channel = 0

# Write/Read Speed IN
Fun_Write_SpeedIn(10, module=5, channel=0)
print("Speed In")
Fun_Read(256)

# Write/Read Speed OUT
Fun_Write_SpeedOut(5, module=5, channel=0)
print("Speed Out")
Fun_Read(257)

# Write/Read Force
Fun_Write_Force(5, module=5, channel=0)
print("Force")
Fun_Read(258)

# For position values, data type is float32 but decimal points are included in the integer part of the value. For example, 199.98 is entered as 19998
# Write/Read End Position
Fun_Write_End_Position(19998, module=5, channel=0)
print("Out Pos")
print(Fun_Read(262))

# Intermediate Position should always be less or equal than End Position. Otherwise, an error will be triggered
# Write/Read Intermediate Position
Fun_Write_Intermediate_Position(5000, module=5, channel=0)
print("Intermediate Pos")
Fun_Read(264)

# This section can be uncommented to command positions, be mindful of your own Modbus addressing since this will depend on your specific configuration.
# 256 = Move In
# 512 = Move Out
# 1024 = Quit Error
# 4096 = Move Intermediate
# while(True):
#     if c.write_single_register(40008,512):
#         print("write ok")
#     else:
#         print("write error")

c.close()