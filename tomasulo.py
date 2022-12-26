'''
@File    :   tomasulo.py
@Time    :   2022/12/25 14:42:45
@Author  :   Zhang Maysion 
@Version :   1.0
@Contact :   zhangmx67@mail2.sysu.edu.cn
'''

# use tomasulo algorithm to simulate the execution of a program

# define the parameters
INPUT_FILE = "input1.txt"

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
        self.issueTime = -1 # cycle number when the instruction is issued
        # the execute complished time is writeback time - 1
        self.writeTime = -1 # cycle number when the instruction is written back
    
    def issue(self, cycle):
        self.issueTime = cycle
    
    # 加减乘除和store的writetime在源寄存器值可知时才确定（写回或者发布时）
    # load的writetime在issue时就能确定
    def setWriteTime(self, cycle):
        self.writeTime = cycle

# define the register class
class Register:
    def __init__(self, name):
        self.name = name # name of the register
        self.value = name # value of the register
        self.busy = False # whether the register is being occupied 
        self.fu = "" # function unit that is writing the register

    def occupy(self, fu):
        self.busy = True
        self.fu = fu

    def write(self, value):
        self.value = value

    def free(self):
        self.busy = False
        self.fu = ""


class Reservation:
    def __init__(self, name):
        self.name = name
        self.op = "" 
        self.time = 9999 # remaining time to complete the operation
        self.busy = False
        self.fn1 = "" # name of the instruction that is writing to the source register 1
        self.fn2 = "" # name of the instruction that is writing to the source register 2
        self.src1 = "" # value of the source register 1
        self.src2 = "" # value of the source register 2
        self.instruction = -1 # index of the instruction, so that we can set the time for it

    def isAvaible(self):
        return self.busy == False

    def occupy(self, op, fn1, fn2, src1, src2, instruction):
        self.op = op
        self.busy = True
        self.fn1 = fn1
        self.fn2 = fn2
        self.src1 = src1
        self.src2 = src2
        self.instruction = instruction

    # only update the value of the source register
    def write(self, fn, value):
        if self.fn1 == fn:
            self.src1 = value
            self.fn1 = ""
        if self.fn2 == fn:
            self.src2 = value
            self.fn2 = ""
 

    def free(self):
        self.op = ""
        self.time = 9999
        self.busy = False
        self.src1 = ""
        self.src2 = ""
        self.fn1 = ""
        self.fn2 = ""
        self.instruction = -1

    def execute(self):
        if self.busy == True:
            self.time -= 1

    def isEnd(self):
        if self.time == 0:
            return True
        else:
            return False



# define the reservation station class for ADD
class ReservationADD(Reservation):
    def __init__(self, name):
        super().__init__(name)
        self.type = "ADD"

    def occupy(self, op, fn1, fn2, src1, src2, instruction):
        super().occupy(op, fn1, fn2, src1, src2, instruction)
        if(fn1 == "" and fn2 == ""):
            self.time = cycle_add

    def write(self, fn, value):
        super().write(fn, value)
        if self.fn1 == "" and self.fn2 == "":
            self.busy = False
            self.op = ""
            self.time = cycle_add
            self.instruction = -1

    def free(self):
        super().free()

    def execute(self):
        super().execute()

    def isEnd(self):
        super().isEnd()

    def getResult(self):
        if(self.op == "ADDD"):
            return self.src1 + "+" + self.src2
        else:
            return self.src1 + "-" + self.src2

class ReservationMUL(Reservation):
    def __init__(self, name):
        super().__init__(name)
        self.type = "MUL"

    def occupy(self, op, fn1, fn2, src1, src2, instruction):
        super().occupy(op, fn1, fn2, src1, src2, instruction)
        if(fn1 == "" and fn2 == ""):
            self.time = cycle_mul

    def write(self, fn, value):
        super().write(fn, value)
        if self.fn1 == "" and self.fn2 == "":
            self.busy = False
            self.op = ""
            self.time = cycle_mul
            self.instruction = -1

    def free(self):
        super().free()

    def execute(self):
        super().execute()

    def isEnd(self):
        super().isEnd()

    def getResult(self):
        if(self.op == "MULTD"):
            return self.src1 + "*" + self.src2
        else:
            return self.src1 + "/" + self.src2

# define the load buffer class
# fn1 and fn2 are not used
# src1 is the memory address
# src2 is not used
# 每次load更新寄存器值，和reservation都是直接覆盖寄存器fn；
# 不同在于load直接计时，不用等待源寄存器
class LoadBuffer(Reservation):
# load buffer to a register    
    def __init__(self, name):
        super().__init__(name)
        self.type = "LOAD"

    def occupy(self, src1, instruction):
        super().occupy("LOAD", "", "", src1, "", instruction)
        self.time = cycle_load

    def getResult(self, index):
        return "M" + str(index)


    def execute(self):
        return super().execute()
    
    def isEnd(self):
        return super().isEnd()

    def free(self):
        return super().free()


# define the store buffer class
# fn1 is used
# fn2 is not used
# src1 is the value of register
# src2 is not used
# add dest to store the memory address
# 每次store获取源寄存器值时，和reservation都是从寄存器fn中获取（或者直接读取）；
# 不同在于store没有目标寄存器，直接写入内存（在寄存器fn不会出现store）
class StoreBuffer(Reservation):
    def __init__(self, name):
        super().__init__(name)
        self.type = "STORE"
        self.dest = ""

    def occupy(self, src, fn, dest, instruction):
        self.dest = dest
        super().occupy("STORE", fn, "", src, "", instruction)
        if fn == "":
            self.time = cycle_store

    def execute(self):
        return super().execute()
    
    def isEnd(self):
        return super().isEnd()

    def free(self):
        return super().free()

    def write(self, fn, value):
        if self.fn1 == fn:
            self.src1 = value
            self.fn1 = ""
            self.time = cycle_store


Instructions = []
Registers = []
ReservationADDs = []
ReservationMULs = []
LoadBuffers = []
StoreBuffers = []
cycle = 0 # cycle number of the simulation
pc = 0 # program counter
memory_index = 0 # load result index,only use in loadBuffer.getResult

def init():
    global Instructions, Registers, ReservationADDs, ReservationMULs, LoadBuffers, StoreBuffers, cycle, pc, memory_index

    Instructions.clear()
    Registers.clear()
    ReservationADDs.clear()
    ReservationMULs.clear()
    LoadBuffers.clear()
    StoreBuffers.clear()

    cycle = 0
    pc = 0
    memory_index = 0

    file = open(INPUT_FILE, "r")
    data = file.readlines()
    file.close()
    for i in data:
        op, dest, src1, src2 = i.split()
        Instructions.append(Instruction(op, dest, src1, src2))

    for i in range(32):
        Registers.append(Register("F" + str(i)))
    
    for i in range(num_add):
        ReservationADDs.append(ReservationADD("Add" + str(i + 1)))
    
    for i in range(num_mul):
        ReservationMULs.append(ReservationMUL("Mult" + str(i + 1)))

    for i in range(num_load):
        LoadBuffers.append(LoadBuffer("Load" + str(i + 1)))
    
    for i in range(num_store):
        StoreBuffers.append(StoreBuffer("Store" + str(i + 1)))


def print_state():
    # print the state of the simulation
    state_str = "Cycle_" + str(cycle) + "\n"

    for i in range(len(LoadBuffers)):
        if(LoadBuffers[i].busy):
            state_str += "Load" + str(i + 1) + ": Yes, " + LoadBuffers[i].src1 + ";" + "\n"
        else:
            state_str += "Load" + str(i + 1) + ": No" + ";" + "\n"
        

    for i in range(len(StoreBuffers)):
        if(StoreBuffers[i].busy):
            state_str += "Store" + str(i + 1) + ": Yes, " + StoreBuffers[i].dest
            if(StoreBuffers[i].fn1):
                state_str +=  ", " + StoreBuffers[i].fn1 + ";" + "\n"
            else:
                state_str +=  ", " + "NULL" + ";" + "\n"
        else:
            state_str += "Store" + str(i + 1) + ": No"+ ";"+ "\n"

    for i in range(len(ReservationADDs)):
        if(ReservationADDs[i].busy):
            state_str += "Add" + str(i + 1) + ": Yes, " + ReservationADDs[i].op 
            if(ReservationADDs[i].fn1):
                state_str +=  ", " + ReservationADDs[i].fn1
            else:
                state_str +=  ", " + ReservationADDs[i].src1
            if(ReservationADDs[i].fn2):
                state_str +=  ", " + ReservationADDs[i].fn2
            else:
                state_str +=  ", " + ReservationADDs[i].src2
            state_str += ";" + "\n"

        else:
            state_str += "Add" + str(i + 1) + ": No" + ";\n"

    for i in range(len(ReservationMULs)):
        if(ReservationMULs[i].busy):
            state_str += "Mult" + str(i + 1) + ": Yes, " + ReservationMULs[i].op 
            if(ReservationMULs[i].fn1):
                state_str +=  ", " + ReservationMULs[i].fn1
            else:
                state_str +=  ", " + ReservationMULs[i].src1
            if(ReservationMULs[i].fn2):
                state_str +=  ", " + ReservationMULs[i].fn2
            else:
                state_str +=  ", " + ReservationMULs[i].src2
            state_str += ";\n"
        else:
            state_str += "Mult" + str(i + 1) + ": No" + ";\n"

    for i in range(len(Registers)):
        state_str += "F" + str(i) + ": "
        if(Registers[i].fu):
            state_str += Registers[i].fn + "; "
        else:
            state_str += str(Registers[i].value) + "; "

    state_str += "\n"
    print(state_str)


def issue():
    global Instructions, Registers, ReservationADDs, ReservationMULs, LoadBuffers, StoreBuffers, cycle, pc, memory_index

    if(pc < len(Instructions)):
        # judge the operation type and set the time
        op = Instructions[pc].op
        if(Instructions[pc].op == "ADDD" or Instructions[pc].op == "SUBD"):
            
            
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
            


def write_back():
    global Instructions, Registers, Reservations, LoadBuffers, StoreBuffers, cycle, pc, memory_index

    for r in range(len(Reservations)):
        if(Reservations[r].busy and Reservations[r].time == 0):
            f = 0
            # write back to the destination

    for r in Reservations:
        if(r.busy and r.time == 0):
            # r.dest gets the result
            # write back to the destination register
            for i in range(len(Instructions)):
                break  
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



             
def execute():
    pass

def isAllFree():
    for i in range(num_add):
        if(Reservations[i].busy == True):
            return False
    for i in range(num_mul):
        if(Reservations[i + num_add].busy == True):
            return False    
    for i in range(num_load):
        if(LoadBuffers[i].busy == True):
            return False
    for i in range(num_store):
        if(StoreBuffers[i].busy == True):
            return False
    return True


def tomasulo():
    global Instructions, Registers, Reservations, LoadBuffers, StoreBuffers, cycle, pc
    init()
    print_state()
    while(pc < len(Instructions)):
        cycle += 1
        write_back()
        issue()
        execute()
        print_state()
    
    while not(isAllFree()):
        write_back()
        execute()
        print_state()
        cycle += 1
    
    # print the result




    






    


if __name__ == "__main__":
    tomasulo()


# 按照属性对列表排序
# b.sort(key=lambda x: x[1])