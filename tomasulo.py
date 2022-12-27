'''
@File    :   tomasulo.py
@Time    :   2022/12/25 14:42:45
@Author  :   Zhang Maysion 
@Version :   1.0
@Contact :   zhangmx67@mail2.sysu.edu.cn
'''

import time

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

def getExecuteTime(op):
    if op == "ADDD" or op == "SUBD":
        return cycle_add
    elif op == "MULTD":
        return cycle_mul
    elif op == "DIVD":
        return cycle_div
    elif op == "LD":
        return cycle_load
    elif op == "SD":
        return cycle_store
    else:
        return 0

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


class Register:
    def __init__(self, name):
        self.name = name # name of the register
        self.value = "R(" + name + ")"# value of the register
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

    def isBusy(self):
        return self.busy

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

    def isBusy(self):
        return self.busy

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
            # if(self.time == 0):
            #     self.free()

    def isEnd(self):
        if self.time == 0 and self.busy == True:
            return True
        else:
            return False

    def getExecuteTime(self):
        return None
        # global cycle_add, cycle_sub, cycle_mul, cycle_div, cycle_load, cycle_store
        # if self.op == "ADDD" or self.op == "SUBD":
        #     return cycle_add
        # elif self.op == "MULD":
        #     return cycle_mul
        # elif self.op == "DIVD":
        #     return cycle_div
        # elif self.op == "LD":
        #     return cycle_load
        # elif self.op == "SD":
        #     return cycle_store


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

    def free(self):
        super().free()

    def execute(self):
        super().execute()

    def isEnd(self):
        return super().isEnd()
    
    def isAvaible(self):
        return super().isAvaible()
    
    def isBusy(self):
        return super().isBusy()

    def write(self, fn, value):
        super().write(fn, value)

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
        return super().isEnd()

    def isAvaible(self):
        return super().isAvaible()

    def isBusy(self):
        return super().isBusy()
        
    def write(self, fn, value):
        super().write(fn, value)

    def getResult(self):
        if(self.op == "MULTD"):
            return self.src1 + "*" + self.src2
        else:
            return self.src1 + "/" + self.src2


class LoadBuffer(Reservation):
# fn1 and fn2 are not used
# src1 is the memory address
# src2 is not used
# 每次load更新寄存器值，和reservation都是直接覆盖寄存器fn；
# 不同在于load直接计时，不用等待源寄存器
# load buffer to a register    
    def __init__(self, name):
        super().__init__(name)
        self.type = "LOAD"

    def occupy(self, src1, instruction):
        super().occupy("LOAD", "", "", src1, "", instruction)
        self.time = cycle_load

    def getResult(self, index):
        return "M(A" + str(index + 1) + ")"


    def execute(self):
        super().execute()
    
    def isEnd(self):
        return super().isEnd()

    def free(self):
        super().free()

    def isAvaible(self):
        return super().isAvaible()

    def isBusy(self):
        return super().isBusy()
        
    def write(self, fn, value):
        super().write(fn, value)


class StoreBuffer(Reservation):
# fn1 is used
# fn2 is not used
# src1 is the value of register
# src2 is not used
# add dest to store the memory address
# 每次store获取源寄存器值时，和reservation都是从寄存器fn中获取（或者直接读取）；
# 不同在于store没有目标寄存器，直接写入内存（在寄存器fn不会出现store）
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
        super().execute()
        # store did not check in writeback statge, so we check here to free
        if(self.busy and self.time == 0):
            self.free()
    
    def isEnd(self):
        return super().isEnd()

    def free(self):
        super().free()

    def isBusy(self):
        return super().isBusy()

    def write(self, fn, value):
        if self.fn1 == fn:
            self.src1 = value
            self.fn1 = ""
            self.time = cycle_store

    def isAvaible(self):
        return super().isAvaible()
        
    def write(self, fn, value):
        super().write(fn, value)



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
            state_str += Registers[i].fu + "; "
        else:
            if(Registers[i].value == "R(" + Registers[i].name + ")"):
                state_str += " " + "; "
            else:
                state_str += str(Registers[i].value) + "; "

    state_str += "\n"
    print(state_str)


def issue():
    global Instructions, Registers, ReservationADDs, ReservationMULs, LoadBuffers, StoreBuffers, cycle, pc, memory_index

    if(pc < len(Instructions)):
        # judge the operation type and set the time
        op = Instructions[pc].op
        if(op == "ADDD" or op == "SUBD"):
            # find avaible reservation station
            set = -1
            for i in range(num_add):
                if(ReservationADDs[i].isAvaible()):
                    set = i
                    break
            if(set == -1):
                # wait for next cycle
                return False
            
            src1 = int(Instructions[pc].src1[1:])
            if(Registers[src1].isBusy()):
                # the source register is not ready
                fu1 = Registers[src1].fu
                src1 = ""
            else:
                fu1 = ""
                src1 = Registers[src1].value
            src2 = int(Instructions[pc].src2[1:])
            if(Registers[src2].isBusy()):
                # the source register is not ready
                fu2 = Registers[src2].fu
                src2 = ""
            else:
                fu2 = ""
                src2 = Registers[src2].value
            # issue in instrucction
            Instructions[pc].issue(cycle)
            if(fu1 == "" and fu2 == ""):
                if(op == "ADDD"):
                    Instructions[pc].setWriteTime(cycle + cycle_add + cycle_writeback)
                else:
                    Instructions[pc].setWriteTime(cycle + cycle_sub + cycle_writeback)
            # issue in reservation station
            ReservationADDs[set].occupy(op, fu1, fu2, src1, src2, pc)
            # issue in register
            dest = int(Instructions[pc].dest[1:])
            Registers[dest].occupy(ReservationADDs[set].name)

        elif(op == "MULTD" or op == "DIVD"):
            # find avaible reservation station
            set = -1
            for i in range(num_mul):
                if(ReservationMULs[i].isAvaible()):
                    set = i
                    break
            if(set == -1):
                # wait for next cycle
                return False
            
            src1 = int(Instructions[pc].src1[1:])
            if(Registers[src1].isBusy()):
                # the source register is not ready
                fu1 = Registers[src1].fu
                src1 = ""
            else:
                fu1 = ""
                src1 = Registers[src1].value
            src2 = int(Instructions[pc].src2[1:])
            if(Registers[src2].isBusy()):
                # the source register is not ready
                fu2 = Registers[src2].fu
                src2 = ""
            else:
                fu2 = ""
                src2 = Registers[src2].value
            # issue in instrucction
            Instructions[pc].issue(cycle)
            if(fu1 == "" and fu2 == ""):
                if(op == "MULTD"):
                    Instructions[pc].setWriteTime(cycle + cycle_mul + cycle_writeback)
                else:
                    Instructions[pc].setWriteTime(cycle + cycle_div + cycle_writeback)
            # issue in reservation station
            ReservationMULs[set].occupy(op, fu1, fu2, src1, src2, pc)
            # issue in register
            dest = int(Instructions[pc].dest[1:])
            Registers[dest].occupy(ReservationMULs[set].name)

        elif(op == "LD"):
            # find avaible load buffer
            set = -1
            for i in range(num_load):
                if(LoadBuffers[i].isAvaible()):
                    set = i
                    break
            if(set == -1):
                # wait for next cycle
                return False
            
            if(Instructions[pc].src1 == "0"):
                scr1 = Instructions[pc].src2
            else:
                scr1 = Instructions[pc].src1 + Instructions[pc].src2
            dest = int(Instructions[pc].dest[1:])
            # issue in instruction
            Instructions[pc].issue(cycle)
            Instructions[pc].setWriteTime(cycle + cycle_load + cycle_writeback)
            # issue in load buffer
            LoadBuffers[set].occupy(scr1, pc)
            # issue in register
            Registers[dest].occupy(LoadBuffers[set].name)

        elif(op == "SD"):
            # stor也需要像保留站一样考虑源寄存器是否空闲才设定写回时间
            # find avaible store buffer
            set = -1
            for i in range(num_store):
                if(StoreBuffers[i].isAvaible()):
                    set = i
                    break
            if(set == -1):
                # wait for next cycle
                return False
            
            if(Instructions[pc].src1 == "0"):
                dest = Instructions[pc].src2
            else:
                dest = Instructions[pc].src1 + Instructions[pc].src2
            src1 = int(Instructions[pc].dest[1:])
            if(Registers[src1].isBusy()):
                # the source register is not ready
                fu1 = Registers[src1].fu
                src1 = ""
            else:
                fu1 = ""
                src1 = Registers[src1].value
            
            # issue in instruction
            Instructions[pc].issue(cycle)
            if(fu1 == ""):
                Instructions[pc].setWriteTime(cycle + cycle_store + cycle_writeback)
            # issue in store buffer
            StoreBuffers[set].occupy(src1, fu1, dest, pc)
            # STORE does not need to occupy a register
        pc += 1

def write_back():
    global Instructions, Registers, ReservationADDs, ReservationMULs, LoadBuffers, StoreBuffers, cycle, pc, memory_index
    # pick the finished update(time = 0 and is busy) in reservation and laod
    # update the register
    # update the reservation and store(if they use the updated data as source)
    # add instruction with writeTime

    # pick the update info
    update = []
    for i in range(len(ReservationADDs)):
        if(ReservationADDs[i].isEnd()):
            res = []
            res.append(ReservationADDs[i].name)
            res.append(ReservationADDs[i].getResult())
            update.append(res)
            ReservationADDs[i].free()        
    for i in range(len(ReservationMULs)):
        if(ReservationMULs[i].isEnd()):
            res = []
            res.append(ReservationMULs[i].name)
            res.append(ReservationMULs[i].getResult())
            update.append(res)
            ReservationMULs[i].free()
    for i in range(len(LoadBuffers)):
        if(LoadBuffers[i].isEnd()):
            res = []
            res.append(LoadBuffers[i].name)
            res.append(LoadBuffers[i].getResult(memory_index))
            memory_index += 1
            update.append(res)
            LoadBuffers[i].free()
    
    # update the register
    for j in range(len(update)):
        for i in range(len(Registers)):
            if(Registers[i].fu == update[j][0]):
                Registers[i].value = update[j][1]
                Registers[i].free()

    # update the reservation
    for j in range(len(update)):
        for i in range(len(ReservationADDs)):    
            if (ReservationADDs[i].isBusy() and (ReservationADDs[i].fn1 != "" or ReservationADDs[i].fn2 != "")):
                ReservationADDs[i].write(update[j][0], update[j][1])
                if(ReservationADDs[i].fn1 == "" and ReservationADDs[i].fn2 == ""):
                    ReservationADDs[i].time = getExecuteTime(ReservationADDs[i].op) + cycle_writeback
                    # update the instruction
                    # Instructions[ReservationADDs[i].instruction].setWriteTime(cycle + ReservationADDs[i].getExecuteTime() +  cycle_writeback)
                    # 在类中引用全局变量行不通，因为类的实例化是在函数外部，而函数外部的变量在函数内部是不可见的
                    Instructions[ReservationADDs[i].instruction].setWriteTime(cycle + getExecuteTime(ReservationADDs[i].op) +  cycle_writeback)
    for i in range(len(ReservationMULs)):
        for j in range(len(update)):
            # if not(ReservationMULs[i].isAvailble()):
            if (ReservationMULs[i].isBusy() and (ReservationMULs[i].fn1 != "" or ReservationMULs[i].fn2 != "")):
                ReservationMULs[i].write(update[j][0], update[j][1])
                if(ReservationMULs[i].fn1 == "" and ReservationMULs[i].fn2 == ""):
                    ReservationMULs[i].time = getExecuteTime(ReservationMULs[i].op) + cycle_writeback
                    # update the instruction
                    Instructions[ReservationMULs[i].instruction].setWriteTime(cycle + getExecuteTime(ReservationMULs[i].op) +  cycle_writeback)

    # update the store
    for i in range(len(StoreBuffers)):
        for j in range(len(update)):
            # if not(StoreBuffers[i].isAvailble()):
            if(StoreBuffers[i].isBusy() and StoreBuffers[i].fn1 != ""):
                StoreBuffers[i].write(update[j][0], update[j][1])
                if(StoreBuffers[i].fn1 == ""):
                    StoreBuffers[i].time = getExecuteTime(StoreBuffers[i]) + cycle_writeback
                    # update the instruction
                    Instructions[StoreBuffers[i].instruction].setWriteTime(cycle + getExecuteTime(StoreBuffers[i]) +  cycle_writeback)


def execute():
    global Instructions, Registers, ReservationADDs, ReservationMULs, LoadBuffers, StoreBuffers, cycle, pc, memory_index
    # execute in reservationADDs
    for i in range(len(ReservationADDs)):
        ReservationADDs[i].execute()
    
    # execute in reservationMULs
    for i in range(len(ReservationMULs)):
        ReservationMULs[i].execute()

    # execute in load buffers
    for i in range(len(LoadBuffers)):
        LoadBuffers[i].execute()

    # execute in store buffers
    for i in range(len(StoreBuffers)):
        StoreBuffers[i].execute()
        

def isAllFree():
    for i in range(num_add):
        if(ReservationADDs[i].isBusy()):
            return False
    for i in range(num_mul):
        if(ReservationMULs[i].isBusy()):
            return False    
    for i in range(num_load):
        if(LoadBuffers[i].isBusy()):
            return False
    for i in range(num_store):
        if(StoreBuffers[i].isBusy()):
            return False
    return True


def tomasulo():
    global Instructions, Registers, ReservationADDs, ReservationMULs, LoadBuffers, StoreBuffers, cycle, pc, memory_index
    init()
    print_state()
    cycle += 1
    while(pc < len(Instructions)):
        write_back()
        execute()
        issue()
        print_state()
        cycle += 1    
        # time.sleep(1)

    while not(isAllFree()):
        write_back()
        execute()
        print_state()
        cycle += 1
        
    
    # print the result
    for i in range(len(Instructions)):
        print("Instruction", i, ":", Instructions[i].op, " ", Instructions[i].issueTime, " ", Instructions[i].writeTime)
    


if __name__ == "__main__":
    tomasulo()


# 按照属性对列表排序
# b.sort(key=lambda x: x[1])