regs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Registers $0 ~ $23
mems = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # memory 0x2000 to 0x2050
mems_location = [0x2000, 0x2004, 0x2008, 0x200c, 0x2010, 0x2014, 0x2018, 0x201c, 0x2020, 0x2024, 0x2028, 0x202c, 0x2030, 0x2034, 0x2038, 0x203c, 0x2040, 0x2044, 0x2048, 0x204c, 0x2050, 0x2054, 0x2058, 0x205c, 0x2060, 0x2064]

cycle = 0
pipeIntrs = 0
threecycle = 0
fourcycle = 0
fivecycle = 0
chSUM = 0
dhSUM = 0
chStall = 0
dhStall = 0
pc = -1
end = 0
n = 0
NOP = 0
stall = 0
num_of_instr = 0
counter = -1
allf = 0xFFFFFFFF
inst_file = "instr_list.txt"
outputFile = open(inst_file, "w")

from math import log, ceil

block_used_tag = 0           # for LRU mechanism

class Block:
    def __init__(self, word_num):
        self.data = [0 for i in range(word_num)]
        self.wd_num = word_num
        self.tag = None
        self.valid = 0
        self.used_tag = 0     # for LRU mechanism


class Blocks:
    #wrd   set
    def __init__(self, wd_num, way_num, blk_num):
        self.way_num = way_num
        self.blk_num = blk_num
        self.wd_num = wd_num
        self.data = []
        for i in range(blk_num):
            tmp_set = [Block(wd_num) for j in range(way_num)]
            self.data.append(tmp_set)

        self.block_bit: int = ceil(log(self.blk_num, 2))
        self.word_bit: int = ceil(log(self.wd_num, 2))   # in block offset bits
        self.read_num = 0
        self.hit_num = 0

    def __getitem__(self, n):
        return self.data[n]

    def get_blk_index(self, mems_index):
        if type(mems_index) == type(1):
            mems_index = format(mems_index, '032b')
        if mems_index[32 - self.block_bit - self.word_bit: 32 - self.word_bit]:
            return int(mems_index[32 - self.block_bit - self.word_bit: 32 - self.word_bit], 2)
        else:
            return 0

    def read(self, mems_index, ):
        self.read_num += 1
        global block_used_tag
        block_used_tag += 1
        if type(mems_index) == type(1):
            mems_index = format(mems_index, '032b')

        target_tag = int(mems_index[0: 32 - self.block_bit - self.word_bit], 2)

        if self.blk_num == 1:
            block_index = 0
        else:
            block_index = int(mems_index[32 - self.block_bit - self.word_bit: 32 - self.word_bit], 2)

        for i in range(self.way_num):
            # hit
            if target_tag == self[block_index][i].tag and self[block_index][i].valid == 1:
                self[block_index][i].used_tag = block_used_tag
                self.hit_num += 1
                return True
        # miss
        min_tag = 0
        min_index = 0
        for i in range(self.way_num):
            if self[block_index][i].valid == 0:
                min_index = i
                break
            if self[block_index][i].used_tag < min_tag:
                min_tag = self[block_index][i].used_tag
                min_index = i

        self[block_index][min_index].tag = target_tag
        # target mem address
        mems_index_address: int = (int(mems_index, 2) - int(mems_index[- self.word_bit:], 2) - 8192) // 4
        self[block_index][min_index].data = mems[mems_index_address: mems_index_address + self.wd_num]
        self[block_index][min_index].valid = 1
        self[block_index][min_index].used_tag = block_used_tag

        return False

    def get_the_block_need_to_write(self, mems_index):
        if isinstance(mems_index, int):
            mems_index = format(mems_index, '032b')

        target_tag = int(mems_index[0: 32 - self.block_bit - self.word_bit], 2)
        if self.blk_num == 1:
            block_index = 0
        else:
            block_index = int(mems_index[32 - self.block_bit - self.word_bit: 32 - self.word_bit], 2)

        for i in range(self.way_num):
            # hit
            if target_tag == self[block_index][i].tag and self[block_index][i].valid == 1:
                return self[block_index][i]
        # miss
        min_tag = 0
        min_index = 0
        for i in range(self.way_num):
            if self[block_index][i].valid == 0:
                min_index = i
                break
            if self[block_index][i].used_tag < min_tag:
                min_tag = self[block_index][i].used_tag
                min_index = i

        return self[block_index][min_index]

    def show(self):
        if self.way_num == 1:
            for i in range(self.blk_num):
                print("        block", i, ":")
                print("                  valid:", self[i][0].valid)
                print("                  tag  :", format(self[i][0].tag))
                for j in self[i][0].data:
                    if j < 0:
                        j = 2**32 + j
                    print("                  0x" + format(j, '08x'))
        else:
            for i in range(self.blk_num):
                print("         set", i, ":")

                # valid
                output = ''
                for j in range(self.way_num):
                    output += "                  valid:   " + str(self[i][j].valid)
                print(output)

                # tags
                output = ''
                for j in range(self.way_num):
                    output += "                  tag  :" + str(self[i][j].tag)
                print(output)

                # content
                output = ''
                for j in range(self.wd_num):
                    tmp_string = ''
                    for k in range(self.way_num):
                        ele = self[i][k].data

                        d = 0
                        for indx in ele:
                            if indx < 0:
                                indx = 2**32 + ele
                            output += "                  0x" + format(indx, '08x')
                            d += 1
                            if (d == ceil(log(self.blk_num, 2))):
                                output += "\n"
                                d = 0
                        print(output)


def main():
    fileName = input("Please enter MIPS instruction file name: ")
    inst_file = "instr_list.txt"
    print("Note: This program assumes that the instructions are in hex.\n")
    inputFile = open(fileName, "r")
    outputFile = open(inst_file, "w")
    global instructions
    global diagnose
    global cache_DM
    global cache_FA
    global cache_SA
    instructions = []  # Declares instructions to be an array
    num_of_instr = 0
    diagnose = 0
    cacheChoice = -1
    way = -1
    sets = -1

    choice = True if int(input("Press 1 for diagnose mode else 0 for normal operation: ")) == 1 else False

    if (choice == True):
        while (diagnose < 1 or diagnose > 3):
            diagnose = int(input("1)Multi-cycle\t\t2)Slow pipeline\t\t3)Fast pipeline\n> "))
            if (diagnose < 1 or diagnose > 3):
                print("ERROR: Enter values from 1-3 ONLY")

    while((cacheChoice < 1 or cacheChoice > 3) and choice == True):
        cacheChoice = int(input("\nChoose which cache to run with the CPU\n1)Direct-mapping\t\t2)2-way Set-associative\t\t3)Fully-associated\n> "))
        if (cacheChoice < 1 or cacheChoice > 3):
            print("ERROR: Enter values from 1-3")

        # DM (b=8, N=1, S=8)
        #cache_DM = Blocks(8, 1, 8)
        # FA, 4 blocks, 2 words each block
        #cache_FA = Blocks(16, 4, 1)
        # 2way-SA, total 8 blocks, 2 words each block
        #cache_SA = Blocks(8, 2, 4)
        # User Customized cache configuration
    if choice:
        print("Enter Cache Configuration:")
        if (cacheChoice == 1 and choice):
            block = int(input("block size:"))
            while (way != 1):
                way = int(input("way:"))
                if (way != 1):
                    print("Direct-mapping can only have 1 way. ONLY ENTER 1 for WAY")
            sets = int(input("set:"))
            cache_DM = Blocks(block, way, sets)
        elif (cacheChoice == 2 and choice):
            block = int(input("block size:"))
            while (way != 2 and way != 3):
                way = int(input("way:"))
                if (way != 2 and way != 3):
                    print("2-way Set-associative can only have 2 way. ONLY ENTER 2 for WAY")
            sets = int(input("set:"))
            cache_SA = Blocks(block, way, sets)
        elif choice:
            block = int(input("block size:"))
            way = int(input("way:"))
            while (sets != 1):
                sets = int(input("set:"))
                if (sets != 1):
                    print("Fully-associated can only have 1 set. ONLY ENTER 1 for SETS")
            cache_FA = Blocks(block, way, sets)


        #cache_user = Blocks(block, way, sets)
        #cache_DM = cache_SA = cache_FA = cache_user

    for line in inputFile:
        if (line == "\n" or line[0] == '#'):  # empty lines and comments ignored
            continue
        line = line.replace('\n', '')  # Removes new line characters
        line = format(int(line, 16),
                      "032b")  # The int function converts the hex instruction into some numerical value, then format converts it into a binary string
        num_of_instr = num_of_instr + 1
        instructions.append(line)
    inputFile.close()
    disassemble(instructions, diagnose, choice, cacheChoice)

    if(cacheChoice == 1):
        print("For cache DM:")
        print("    Hit rate: %.2f" % (cache_DM.hit_num / cache_DM.read_num))
    if(cacheChoice == 3):
        print("For cache FA:")
        print("    Hit rate: %.2f" % (cache_FA.hit_num / cache_FA.read_num))
    if(cacheChoice == 2):
        print("For cache SA:")
        print("    Hit rate: %.2f" % (cache_SA.hit_num / cache_SA.read_num))


    if (diagnose == 1 or choice == 0):
        print("------------------ Multi-cycle cpu ------------------")
        print("Total # of cycles = " + str(cycle))
        print("# of 3 cycles = " + str(threecycle))
        print("% of instructions are 3 cycles = " + str(threecycle / pc) + " %")
        print("# of 4 cycles = " + str(fourcycle))
        print("% of instructions are 3 cycles = " + str(fourcycle / pc) + " %")
        print("# of 5 cycles = " + str(fivecycle))
        print("% of instructions are 3 cycles = " + str(fivecycle / pc) + " %\n")
    if (diagnose == 2 or choice == 0):
        print("------------------ Slow pipeline cpu ------------------")
        print("Total # of cycles = " + str(pipeIntrs + NOP + 4 - 3))
        print("# instr entering pipeline: " + str(pipeIntrs))
        print("finishing up the last instruction: 4")
        print("control hazard delay = " + str(chSUM - 3))
        print("data hazards dealy = " + str(dhSUM) + "\n")
    if (diagnose == 3 or choice == 0):
        print("------------------ Fast pipeline cpu ------------------")
        print("Total # of cycles = " + str(pipeIntrs + stall + 4 - 1))
        print("# instr entering pipeline: " + str(pipeIntrs))
        print("finishing up the last instruction: 4")
        print("control hazard delay= " + str(chStall - 1))
        print("data hazard delay = " + str(dhStall))


def getCycle(argument):
    switcher = {
        "0": "F",
        "1": "D",
        "2": "E",
        "3": "M",
        '4': "W",
    }
    return switcher.get(str(argument), "nothing")


def getRS(i):
    return int(i[6:11], 2)


def getRT(i):
    return int(i[11:16], 2)


def getOP(i):
    return i[0:6]


## Table for all instruction opcodes
def getInstr(argument):
    switcher = {
        "000100": "beq",
        "000101": "bne",
    }
    return switcher.get(str(argument), "nothing")


def disassemble(instructions, diagnose, choice, cacheChoice):
    global n
    global NOP
    global stall
    global outputFile
    instr = []
    global pc
    global cycle
    global pipeIntrs
    global dhSUM
    global chSUM
    global chStall
    global dhStall
    global threecycle
    global fourcycle
    global fivecycle
    global end
    global num_of_instr
    global counter

    skip = False

    while end != 1:
        # print(n)

        instr = instructions[n]

        pc = pc + 1
        currentPC = pc
        # print(regs[12])
        counter = counter + 1
        s = int(instr[6:11], 2)
        t = int(instr[11:16], 2)

        # -------------------------------------------- I TYPE --------------------------------------------

        if (instr[0:6] != "000000"):

            # ------------------  Negative immediate conversion ------------------
            if (instr[16] == '1'):
                imm = 65535 - int(instr[16:32], 2) + 1
                # ("it should be Negative")
                imm = -imm
            else:
                imm = int(instr[16:32], 2)

        # ------------------ ori ------------------

        if (instr[0:6] == "001101"):
            imm = int(instr[16:32], 2)
            outputFile.write("ori $" + str(t) + ", $" + str(s) + ", 0d" + str(imm) + "\n")
            regs[t] = regs[s] | imm
            outputFile.write("r" + str(t) + " = " + str(regs[t]) + "\n")
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 4 cycles")
            if (diagnose == 2 or choice == 0):
                if (n + 1 <= len(instructions) - 1):
                    if (getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t):
                        print("Data hazard")
                        print("Number of NOPs: 2")
                        NOP += 2
                        dhSUM += 2
                        skip = True
                if (n + 2 <= len(instructions) - 1 and not skip):
                    if (getRS(instructions[n + 2]) == t or getRT(instructions[n + 2]) == t):
                        print("Data hazard")
                        print("Number of NOPs: 1")
                        NOP += 1
                        dhSUM += 1
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
            if (diagnose == 3 or choice == 0):
                if (n + 1 <= len(instructions) - 1):
                    if ((getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t) and
                            (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                                getOP(instructions[n + 1])) == "bne")):
                        if (choice != 0):
                            print("Data hazard")
                            print("Stall")
                        stall += 1
                        dhStall += 1
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (choice != 0):
                print("ori $" + str(t) + ", $" + str(s) + ", 0d" + str(imm))
                print("pc = " + str(pc * 4) + "\n")
            cycle += 4
            pipeIntrs += 1
            fourcycle += 1

        # ------------------ lw ------------------

        if (instr[0:6] == "100011"):
            if (imm > 32767):
                imm = 65535 - imm + 1
                imm = - imm
            outputFile.write("lw $" + str(t) + "," + str(imm) + "($" + str(s) + ")" + "\n")
            mems_index = (regs[s] - 8192) // 4
            mems_index = mems_index + imm // 4
            regs[t] = mems[mems_index]
            outputFile.write("r" + str(t) + " = " + str(regs[t]) + "\n")
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 5 cycles")
            if (diagnose == 2 or choice == 0):
                if (n + 1 <= len(instructions) - 1):
                    if (getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t):
                        if (choice != 0):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                        NOP += 2
                        dhSUM += 2
                        skip = True
                if (n + 2 <= len(instructions) - 1 and not skip):
                    if (getRS(instructions[n + 2]) == t or getRT(instructions[n + 2]) == t):
                        if (choice != 0):
                            print("Data hazard")
                            print("Stall")
                        NOP += 1
                        dhSUM += 1
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (diagnose == 3 or choice == 0):
                if (n + 1 <= len(instructions) - 1):
                    if (getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t):
                        if (choice != 0):
                            print("Data hazard")
                            print("Stall")
                        stall += 1
                        dhStall += 1
                    elif ((getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t) and
                          (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                              getOP(instructions[n + 1])) == "bne")):
                        if (choice != 0):
                            print("Data hazard")
                            print("Stall")
                        stall += 2
                        dhStall += 2
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (choice != 0):
                print("lw $" + str(t) + "," + str(imm) + "($" + str(s) + ")")
                print("pc = " + str(pc * 4) + "\n")
            if (cacheChoice == 1 and choice != 0):
                print("------------------------- cache -------------------------")
                print("target" + hex(mems_location[mems_index]))
                # DM Cache
                print("DM cache")
                block_index = cache_DM.get_blk_index(mems_index)
                target_block = cache_DM.get_the_block_need_to_write(mems_index)
                print("   blk/set to access :", block_index)
                print("   valid bit         :", target_block.valid)
                print("   tag               :", target_block.tag)
                hit = cache_DM.read(mems_index)
                print("   hit or not        :", hit)
                if hit:
                    print("   cache update data : no update ")

                else:
                    print("   cache update data :")
                    cache_DM.show()
            elif (cacheChoice == 3 and choice != 0):
                # FA Cache
                print()
                print("FA cache")
                block_index = cache_FA.get_blk_index(mems_index)
                target_block = cache_FA.get_the_block_need_to_write(mems_index)
                print("   blk/set to access :", block_index)
                print("   valid bit         :", target_block.valid)
                print("   tag               :", target_block.tag)
                hit = cache_FA.read(mems_index)
                print("   hit or not        :", hit)
                if hit:
                    print("   cache update data : no update ")

                else:
                    print("   cache update data :")
                    cache_FA.show()
            elif (cacheChoice == 2 and choice != 0):
                # 2 way set-associative cache
                print()
                print("2 way SA cache")
                block_index = cache_SA.get_blk_index(mems_index)
                target_block = cache_SA.get_the_block_need_to_write(mems_index)
                print("   blk/set to access :", block_index)
                print("   valid bit         :", target_block.valid)
                print("   tag               :", target_block.tag)
                hit = cache_SA.read(mems_index)
                print("   hit or not        :", hit)
                if hit:
                    print("   cache update data : no update ")

                else:
                    print("   cache update data :")
                    cache_SA.show()
                print()
                #print("E. Customized cache configuration ")
                #block_index = cache_user.get_blk_index(mems_index)
                #target_block = cache_user.get_the_block_need_to_write(mems_index)
                #print("   blk/set to access :", block_index)
                #print("   valid bit         :", target_block.valid)
                #print("   tag               :", target_block.tag)
                #hit = cache_user.read(mems_index)
                #print("   hit or not        :", hit)
                #if hit:
                #    print("   cache update data : no update ")

                #else:
                #    print("   cache update data :")
                #    cache_user.show()

                print("------------------- end --------------------\n")
            cycle += 5
            pipeIntrs += 1
            fivecycle += 1

        # ------------------ addi ------------------

        if (instr[0:6] == "001000"):
            outputFile.write("addi $" + str(t) + ", $" + str(s) + ", " + str(imm) + "\n")
            regs[t] = regs[s] + imm
            outputFile.write("r" + str(t) + " = " + str(regs[t]) + "\n")
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 4 cycles")
            if (diagnose == 2 or choice == 0):
                if (n + 1 <= len(instructions) - 1):
                    if (getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t):
                        if (choice != 0):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                        NOP += 2
                        dhSUM += 2
                        skip = True
                if (n + 2 <= len(instructions) - 1 and not skip):
                    if (getRS(instructions[n + 2]) == t or getRT(instructions[n + 2]) == t):
                        if (choice != 0):
                            print("Data hazard")
                            print("Number of NOPs: 1")
                        NOP += 1
                        dhSUM += 1
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (diagnose == 3 or choice == 0):
                if (n + 1 <= len(instructions) - 1):
                    if ((getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t) and
                            (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                                getOP(instructions[n + 1])) == "bne")):
                        if (choice != 0):
                            print("Data hazard")
                            print("Stall")
                        stall += 1
                        dhStall += 1
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (choice != 0):
                print("addi $" + str(t) + ", $" + str(s) + ", " + str(imm))
                print("pc = " + str(pc * 4) + "\n")
            cycle += 4
            pipeIntrs += 1
            fourcycle += 1

        # ------------------ sw ------------------

        if (instr[0:6] == "101011"):
            if (imm > 32767):
                imm = 65535 - imm + 1
                imm = - imm
            outputFile.write("sw $" + str(t) + ", " + str(imm) + "($" + str(s) + ")" + "\n")
            mems_index = (regs[s] - 8192) // 4
            mems_index = mems_index + (imm // 4)
            mems[mems_index] = regs[t]
            outputFile.write("r" + str(t) + " = " + str(regs[t]) + "\n")
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 4 cycles")
            if (diagnose == 2 or choice == 0):
                if (choice != 0):
                    print("No hazard")
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (diagnose == 3 or choice == 0):
                if (choice != 0):
                    print("No hazard")
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (choice != 0):
                print("sw $" + str(t) + ", " + str(imm) + "($" + str(s) + ")")
                print("pc = " + str(pc * 4) + "\n")
            cycle += 4
            pipeIntrs += 1
            fourcycle += 1

        # ------------------ beq ------------------

        if (instr[0:6] == "000100"):  # beq
            outputFile.write("beq $" + str(t) + ", $" + str(s) + ", " + str(imm) + "\n")
            outputFile.write("beq " + str(regs[t]) + " , " + str(regs[s]) + " , " + str(imm) + "\n")
            if (t == 0 and s == 0 and imm == -1):
                end = 1
                outputFile.write("end")
                pc = pc + 1
            if (regs[t] == regs[s]):
                pc = pc + imm
                n = n + imm
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 3 cycles")
            if (diagnose == 2 or choice == 0):
                if (choice != 0):
                    print("Control hazard")
                    print("Number of NOPs: 3")
                NOP += 3
                chSUM += 3
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (diagnose == 3 or choice == 0):
                if (choice != 0):
                    print("Control hazard")
                if (regs[t] == regs[s]):
                    if (choice != 0):
                        print("Stall")
                    stall += 1
                    chStall += 1
                else:
                    if (choice != 0):
                        print("Flush")
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (choice != 0):
                print("beq $" + str(t) + ", $" + str(s) + ", " + str(imm))
                print("pc = " + str(pc * 4) + "\n")
            cycle += 3
            pipeIntrs += 1
            threecycle += 1

        # ------------------ bne ------------------

        if (instr[0:6] == "000101"):  # bne
            outputFile.write("bne $" + str(t) + ", $" + str(s) + ", " + str(imm) + "\n")
            outputFile.write("bne " + str(regs[t]) + " , " + str(regs[s]) + " , " + str(imm) + "\n")
            if (regs[t] != regs[s]):
                pc = pc + imm
                n = n + imm
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 3 cycles")
            if (diagnose == 2 or choice == 0):
                if (choice != 0):
                    print("Control hazard")
                    print("Number of NOPs: 3")
                NOP += 3
                chSUM += 3
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (diagnose == 3 or choice == 0):
                if (choice != 0):
                    print("Control hazard")
                if (regs[t] != regs[s]):
                    if (choice != 0):
                        print("Stall")
                    stall += 1
                    chStall += 1
                else:
                    if (choice != 0):
                        print("Flush")
                if (currentPC == 0):
                    if (choice != 0):
                        print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    if (choice != 0):
                        print("pipeline stage: " + str(getCycle(currentPC)))
            if (choice != 0):
                print("bne $" + str(t) + ", $" + str(s) + ", " + str(imm))
                print("pc = " + str(pc * 4) + "\n")
            cycle += 3
            pipeIntrs += 1
            threecycle += 1

        # -------------------------------------------- R TYPE --------------------------------------------

        if (instr[0:6] == "000000"):
            d = int(instr[16:21], 2)
            sh = int(instr[21:26], 2)

            # ------------------ add ------------------

            if (instr[26:32] == "100000"):
                outputFile.write("add $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = regs[s] + regs[t]
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                if (diagnose == 2 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n + 2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (diagnose == 3 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if ((getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d) and
                                (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                                    getOP(instructions[n + 1])) == "bne")):
                            if (choice != 0):
                                print("Data hazard")
                                print("Stall")
                            stall += 1
                            dhStall += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (choice != 0):
                    print("add $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                pipeIntrs += 1
                fourcycle += 1

            # ------------------ sub ------------------

            if (instr[26:32] == "100010"):
                outputFile.write("sub $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = regs[s] - regs[t]
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if (diagnose == 1):
                    if (choice != 0):
                        print("cycle: " + str(cycle))
                        print("Running 4 cycles")
                if (diagnose == 2 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n + 2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (diagnose == 3 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if ((getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d) and
                                (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                                    getOP(instructions[n + 1])) == "bne")):
                            if (choice != 0):
                                print("Data hazard")
                                print("Stall")
                            stall += 1
                            dhStall += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (choice != 0):
                    print("sub $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                pipeIntrs += 1
                fourcycle += 1

            # ------------------ slt ------------------

            if (instr[26:32] == "101010"):
                outputFile.write("slt $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                if (regs[s] < regs[t]):
                    regs[d] = 1
                else:
                    regs[d] = 0
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                if (diagnose == 2 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n + 2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (diagnose == 3 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if ((getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d) and
                                (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                                    getOP(instructions[n + 1])) == "bne")):
                            if (choice != 0):
                                print("Data hazard")
                                print("Stall")
                            stall += 1
                            dhStall += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (choice != 0):
                    print("slt $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                pipeIntrs += 1
                fourcycle += 1

            # ------------------ sltu ------------------
            if (instr[26:32] == "101011"):
                outputFile.write("sltu $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                # S = regs[s] & allf
                # T = regs[t] & allf
                S = abs(regs[s])
                T = abs(regs[t])
                if (S < T):
                    regs[d] = 1
                else:
                    regs[d] = 0
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                if (diagnose == 2 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n + 2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (diagnose == 3 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if ((getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d) and
                                (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                                    getOP(instructions[n + 1])) == "bne")):
                            if (choice != 0):
                                print("Data hazard")
                                print("Stall")
                            stall += 1
                            dhStall += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (choice != 0):
                    print("sltu $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                pipeIntrs += 1
                fourcycle += 1

            # ------------------ addu ------------------

            if (instr[26:32] == "100001"):  # ADDU
                outputFile.write("addu $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = abs(regs[s]) + abs(regs[t])
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                if (diagnose == 2 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n + 2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (diagnose == 3 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if ((getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d) and
                                (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                                    getOP(instructions[n + 1])) == "bne")):
                            if (choice != 0):
                                print("Data hazard")
                                print("Stall")
                            stall += 1
                            dhStall += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (choice != 0):
                    print("addu $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                pipeIntrs += 1
                fourcycle += 1

            # ------------------ sll ------------------

            if (instr[26:32] == "000000"):
                outputFile.write("sll $" + str(d) + ", $" + str(t) + ", " + str(sh) + "\n")
                regs[d] = (regs[t] << sh) & (0xFFFFFFFF)
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                if (diagnose == 2 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n + 2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (diagnose == 3 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if ((getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d) and
                                (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                                    getOP(instructions[n + 1])) == "bne")):
                            if (choice != 0):
                                print("Data hazard")
                                print("Stall")
                            stall += 1
                            dhStall += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (choice != 0):
                    if (choice != 0):
                        print("sll $" + str(d) + ", $" + str(t) + ", " + str(sh))
                        print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                pipeIntrs += 1
                fourcycle += 1

            # ------------------ xor ------------------

            if (instr[26:32] == "100110"):
                outputFile.write("xor $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = regs[s] ^ regs[t]
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                if (diagnose == 2 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n + 2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            if (choice != 0):
                                print("Data hazard")
                                print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (diagnose == 3 or choice == 0):
                    if (n + 1 <= len(instructions) - 1):
                        if ((getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d) and
                                (getInstr(getOP(instructions[n + 1])) == "beq" or getInstr(
                                    getOP(instructions[n + 1])) == "bne")):
                            if (choice != 0):
                                print("Data hazard")
                                print("Stall")
                            stall += 1
                            dhStall += 1
                    if (currentPC == 0):
                        if (choice != 0):
                            print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        if (choice != 0):
                            print("pipeline stage: " + str(getCycle(currentPC)))
                if (choice != 0):
                    print("xor $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                pipeIntrs += 1
                fourcycle += 1
        n = n + 1


# It's not really necessary to understand how it works for this class, but it allows us to use this code as a module or a standalone program.
if __name__ == "__main__":
    main()
