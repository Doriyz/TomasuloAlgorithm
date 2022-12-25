'''
@File    :   tomasulo.py
@Time    :   2022/12/25 14:42:45
@Author  :   Zhang Maysion 
@Version :   1.0
@Contact :   zhangmx67@mail2.sysu.edu.cn
'''

# use tomasulo algorithm to simulate the execution of a program

# define the parameters
cycle_load = 2 
cycle_store = 2 

cycle_issue = 1
cycle_writeback = 1

# cycle_execution for each instruction
cycle_add = 2
cycle_sub = 2
cycle_mul = 10
cycle_div = 20

num_add = 3
num_mul = 2
num_load = 3
num_store = 3


# define the instruction class
class Instruction:
    def __init__(self, op, dest, src1, src2):
        self.op = op # operation
        self.dest = dest # destination register
        self.src1 = src1 # source register 1
        self.src2 = src2 # source register 2
        self.issue = -1 # cycle number when the instruction is issued
        # the execute complished time is writeback time - 1
        self.write = -1 # cycle number when the instruction is written back
    

# define the register class
class Register:
    def __init__(self, name):
        self.name = name # name of the register
        self.value = "" # value of the register
        self.busy = False # whether the register is being occupied 
        self.fu = "" # function unit that is writing the register


# define the reservation station class
class Reservation:
    def __init__(self, name):
        self.name = name
        self.op = "" 
        self.time = 9999 # remaining time to complete the operation
        self.busy = False
        self.qj = "" # name of the instruction that is writing to the source register 1
        self.qk = "" # name of the instruction that is writing to the source register 2
        self.vj = "" # value of the source register 1
        self.vk = "" # value of the source register 2
        self.dest = "" # destination register
        self.instruction = -1 # index of the instruction, so that we can set the time for it

    def free(self):
        self.op = ""
        self.time = 9999
        self.busy = False
        self.qj = ""
        self.qk = ""
        self.vj = ""
        self.vk = ""
        self.dest = ""
        self.instruction = -1

# define the load buffer class
class LoadBuffer:
    def __init__(self, name):
        self.name = name
        self.busy = False
        self.time = 9999 # remaining time to get the value from memory
        self.address = "" # address of the memory location to be loaded
        
        # the address suppose to be:
        # initially, address is the offset
        # after calculated, the address is the real address
        # However, in this program, we assume that the address is the real address
        self.dest = "" # destination register
        self.instruction = -1 # index of the instruction, so that we can set the time for it


# define the store buffer class
class StoreBuffer:
    def __init__(self, name):
        self.name = name
        self.busy = False
        self.time = 9999 # remaining time to store the value to memory
        self.address = "" # address of the memory location to be stored
        self.value = "" # value to be stored to memory


Instructions = []
Registers = []
Reservations = []
LoadBuffers = []
StoreBuffers = []
cycle = 0 # cycle number of the simulation
pc = 0 # program counter


def init():
    global Instructions, Registers, Reservations, LoadBuffers, StoreBuffers, cycle, pc

    Instructions.clear()
    Registers.clear()
    Reservations.clear()
    LoadBuffers.clear()
    StoreBuffers.clear()

    cycle = 0
    pc = 0

    file = open("input1.txt", "r")
    data = file.readlines()
    file.close()
    for i in data:
        op, dest, src1, src2 = i.split()
        Instructions.append(Instruction(op, dest, src1, src2))

    for i in range(32):
        Registers.append(Register("R" + str(i)))
    
    for i in range(num_add):
        Reservations.append(Reservation("Add" + str(i + 1)))
    
    for i in range(num_mul):
        Reservations.append(Reservation("Mult" + str(i + 1)))

    for i in range(num_load):
        LoadBuffers.append(LoadBuffer("Load" + str(i + 1)))
    
    for i in range(num_store):
        StoreBuffers.append(StoreBuffer("Store" + str(i + 1)))


def print_state():
    # print instruction status, reservation station status, load buffer status, register status
    state_str = "Cycle " + str(cycle) + "\n" + "\n"

    state_str += "Instruction Status\n"
    state_str += "Operation Destination Source1 Source2 Issue Execute Writeback\n"
    for i in Instructions:
        state_str += i.op + " " + i.dest + " " + i.src1 + " " + i.src2 + " " 
        if(i.issue == -1):
            state_str += "  "
        else:
            state_str += str(i.issue)
        state_str += " "
        if(i.write == -1):
            state_str += "  "
        else:
            state_str +=  str(i.write - 1) + " " + str(i.write)
            # the execute complished time is writeback time - 1
        state_str += "\n"

    state_str += "\n" + "Reservation Station Status\n"
    state_str += "Time Name Busy Operation Vj Qj Vk Qk\n"
    for r in Reservations:
        if(r. time == 9999):
            state_str += "  "
        else:
            state_str += str(r.time)
        if(r.busy):
            state_str += " " + r.name + " " + "Yes" + " " + r.op + " " + str(r.vj) + " " + r.qj + " " + str(r.vk) + " " + r.qk + "\n"
        else:
            state_str += " " + r.name + " " + "No" + "\n"

    state_str += "\n" + "Load Buffer Status\n"
    state_str += "Name Busy Address\n"
    for l in LoadBuffers:
        if(l.busy):
            state_str += l.name + " " + "Yes" + " " + l.address + "\n"
        else:
            state_str += l.name + " " + "No" + "\n"

    state_str += "\n" + "Register Status\n"
    state_str += "Name Value FunctionUnit\n"
    for r in Registers:
        state_str += r.name 
        if(r.busy):
            state_str += " " + r.value + " " + r.fu + "\n"
        else:
            state_str += " " + r.value + "\n"
    print(state_str)

def write_back():
    global Instructions, Registers, Reservations, LoadBuffers, StoreBuffers, cycle, pc

    for r in Reservations:
        if(r.busy and r.time == 0):
            # r.dest gets the result
            # write back to the destination register
            for reg in Registers:
                if(reg.name == r.dest):
                    if(Instructions[r.instruction].op == "ADDD"):
                        reg.value = r.vj + "+" + r.vk
                    elif(Instructions[r.instruction].op == "SUBD"):
                        reg.value = r.vj + "-" + r.vk
                    elif(Instructions[r.instruction].op == "MULTD"):
                        reg.value = r.vj + "*" + r.vk
                    elif(Instructions[r.instruction].op == "DIVD"):
                        reg.value = r.vj + "/" + r.vk
                    reg.fu = ""
                    break
            # write back the source register in reservation station
            for reg in Registers:
                if(reg.qj == r.name):
                    reg.qj = ""
                    reg.vj = r.dest
                if(reg.qk == r.name):
                    reg.qk = ""
                    reg.vk = r.dest
                # if both sourse registers ready
                if(reg.qj == "" and reg.qk == ""):
                    # judge the operation type and set the remain time
                    if(Instructions[r.instruction].op == "ADDD"):
                        r.time = cycle_add
                        Instructions[r.instruction].write = cycle + cycle_add + 1
                    elif(Instructions[r.instruction].op == "SUBD"):
                        r.time = cycle_sub
                        Instructions[r.instruction].write = cycle + cycle_sub + 1
                    elif(Instructions[r.instruction].op == "MULTD"):
                        r.time = cycle_mul
                        Instructions[r.instruction].write = cycle + cycle_mul + 1
                    elif(Instructions[r.instruction].op == "DIVD"):
                        r.time = cycle_div
                        Instructions[r.instruction].write = cycle + cycle_div + 1
            # we suppose that load and store will get the needed data immediately
            # so we do not write back to store and load buffer

            r.free()

def issueInReservation(op):
    # op is "ADDD" or "SUBD"or "MULTD"or "DIVD"
    global Instructions, Registers, Reservations, LoadBuffers, StoreBuffers, cycle, pc
    # check if there is a free reservation station
    set = -1
    if(op == "ADDD" or op == "SUBD"):
        for i in range(num_add):
            if(Reservations[i].busy == False):
                set = i
                break
    elif(op == "MULTD" or op == "DIVD"):
        for i in range(num_add, num_add + num_mul):
            if(Reservations[i].busy == False):
                set = i
                break
    if(set == -1):
        # there is no free reservation station, wait for next cycle
        return False
    # add the instruction to the reservation station
    Reservations[set].busy = True
    Reservations[set].op = op
    Reservations[set].instruction = pc
    Reservations[set].dest = Instructions[pc].dest
    Instructions[pc].issue = cycle
    Registers[int(Instructions[pc].dest[1:])].fu = Reservations[set].name
    # check if the source registers are ready
    # to get the index quickly, we use the name of the register as the index
    index = int(Instructions[pc].src1[1:])
    if(Registers[index].qj == ""):
        Reservations[set].vj = Registers[index].value
    else:
        Reservations[set].qj = Registers[index].qj
    index = int(Instructions[pc].src2[1:])
    if(Registers[index].qj == ""):
        Reservations[set].vk = Registers[index].value
    else:
        Reservations[set].qk = Registers[index].qj
    # if both sourse registers ready
    if(Reservations[set].qj == "" and Reservations[set].qk == ""):
        Reservation[set].time = cycle_add
        # Instructions[pc].exec = cycle + cycle_add
        Instructions[pc].write = cycle + cycle_add + 1


def issue():
    global Instructions, Registers, Reservations, LoadBuffers, StoreBuffers, cycle, pc

    if(pc < len(Instructions)):
        # judge the operation type and set the time
        op = Instructions[pc].op
        if(Instructions[pc].op == "ADDD" or Instructions[pc].op == "SUBD"):
            issueInReservation(op)
        elif(Instructions[pc].op == "MULTD" or Instructions[pc].op == "DIVD"):
            issueInReservation(op)
        elif(Instructions[pc].op == "LD"):
            # check if there is a free load buffer
            set = -1
            for i in range(num_load):
                if(LoadBuffers[i].busy == False):
                    set = i
                    break
            if(set == -1):
                # there is no free load buffer, wait for next cycle
                return False
            # add the instruction to the load buffer
            # we suppose that load will get the needed data immediately
            LoadBuffers[set].busy = True
            LoadBuffers[set].instruction = pc
            LoadBuffers[set].dest = Instructions[pc].dest
            if(Instructions[pc].src1 == "0"):
                LoadBuffers[set].address = Instructions[pc].src2
            else:
                LoadBuffers[set].address = Instructions[pc].src1 + Instructions[pc].src2
            Instructions[pc].issue = cycle
            Instructions[pc].write = cycle + cycle_load + 1
            Registers[int(Instructions[pc].dest[1:])].fu = LoadBuffers[set].name
        elif(Instructions[pc].op == "SD"):
            # check if there is a free store buffer
            set = -1
            for i in range(num_store):
                if(StoreBuffers[i].busy == False):
                    set = i
                    break
            if(set == -1):
                # there is no free store buffer, wait for next cycle
                return False
            # add the instruction to the store buffer
            # we suppose that store will get the needed data immediately
            StoreBuffers[set].busy = True
            StoreBuffers[set].instruction = pc
            StoreBuffers[set].address = Instructions[pc].src1
            StoreBuffers[set].value = Instructions[pc].src2
            Instructions[pc].issue = cycle
            Instructions[pc].write = cycle + cycle_store + 1
            
             
                    


def tomasulo():
    global Instructions, Registers, Reservations, LoadBuffers, StoreBuffers, cycle, pc
    init()
    print_state()
    while(pc < len(Instructions)):
        # write back the ready operands finished in last cycle
        write_back()
        # issue the a instruction
        issue()






    


if __name__ == "__main__":
    tomasulo()


# 按照属性对列表排序
# b.sort(key=lambda x: x[1])