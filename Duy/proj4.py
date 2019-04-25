regs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; #Registers $0 ~ $23
mem_range = 1024
mems = [0 for i in range(mem_range)]
mems_location = [0x2000, 0x2004, 0x2008, 0x200c, 0x2010, 0x2014, 0x2018, 0x201c, 0x2020, 0x2024, 0x2028, 0x202c, 0x2030, 0x2034, 0x2038, 0x203c, 0x2040, 0x2044, 0x2048, 0x204c, 0x2050]

cycle = 0
pipeIntrs = 0
threecycle = 0
fourcycle = 0
fivecycle = 0
chSUM = 0
dhSUM = 0
pc = -1
end = 0
n = 0
NOP = 0
num_of_instr = 0
counter = -1
k = 0
allf = 0xFFFFFFFF
inst_file = "instr_list.txt"
outputFile = open(inst_file, "w")

from math import log, ceil

block_used_tag = 0           # for LRU mechanism

class Block:
    def __init__(self, word_num):
        self.info = [0 for i in range(word_num)]
        self.wd_num = word_num
        self.tag = None
        self.vali = 0
        self.used_tag = 0     # for LRU mechanism


class Blocks:
    def __init__(self, way_num, blk_num, wd_num):
        self.way_num = way_num
        self.blk_num = blk_num
        self.wd_num = wd_num
        self.info = []
        for i in range(blk_num):
            tmp_set = [Block(wd_num) for j in range(way_num)]
            self.info.append(tmp_set)

        self.block_bit: int = ceil(log(self.blk_num, 2))
        self.word_bit: int = ceil(log(self.wd_num, 2)) + 2   # in block offset bits
        self.read_num = 0
        self.hit_num = 0

    def __getitem__(self, n):
        return self.info[n]

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
            target_block_index = 0
        else:
            target_block_index = int(mems_index[32 - self.block_bit - self.word_bit: 32 - self.word_bit], 2)

        for i in range(self.way_num):
            # hit
            if target_tag == self[target_block_index][i].tag and self[target_block_index][i].vali == 1:
                self[target_block_index][i].used_tag = block_used_tag
                self.hit_num += 1
                return True
        # miss
        min_tag = 0
        min_index = 0
        for i in range(self.way_num):
            if self[target_block_index][i].vali == 0:
                min_index = i
                break
            if self[target_block_index][i].used_tag < min_tag:
                min_tag = self[target_block_index][i].used_tag
                min_index = i

        self[target_block_index][min_index].tag = target_tag
        # target mem address
        mems_index_address: int = (int(mems_index, 2) - int(mems_index[- self.word_bit:], 2) - 8192) // 4
        self[target_block_index][min_index].info = mems[mems_index_address: mems_index_address + self.wd_num]
        self[target_block_index][min_index].vali = 1
        self[target_block_index][min_index].used_tag = block_used_tag

        return False

    def get_the_block_need_to_write(self, mems_index):
        if isinstance(mems_index, int):
            mems_index = format(mems_index, '032b')

        target_tag = int(mems_index[0: 32 - self.block_bit - self.word_bit], 2)
        if self.blk_num == 1:
            target_block_index = 0
        else:
            target_block_index = int(mems_index[32 - self.block_bit - self.word_bit: 32 - self.word_bit], 2)

        for i in range(self.way_num):
            # hit
            if target_tag == self[target_block_index][i].tag and self[target_block_index][i].vali == 1:
                return self[target_block_index][i]
        # miss
        min_tag = 0
        min_index = 0
        for i in range(self.way_num):
            if self[target_block_index][i].vali == 0:
                min_index = i
                break
            if self[target_block_index][i].used_tag < min_tag:
                min_tag = self[target_block_index][i].used_tag
                min_index = i

        return self[target_block_index][min_index]

    def show(self):
        if self.way_num == 1:
            for i in range(self.blk_num):
                print("        block", i, ":")
                print("                  valid:", self[i][0].vali)
                print("                  tag  :", format(self[i][0].tag))
                for j in self[i][0].info:
                    if j < 0:
                        j = 2**32 + j
                    print("                  0x" + format(j, '08x'))
        else:
            for i in range(self.blk_num):
                print("         set", i, ":")

                # valid bits
                tmp_string = ''
                for j in range(self.way_num):
                    tmp_string += "                  valid:   " + str(self[i][j].vali)
                print(tmp_string)

                # tags
                tmp_string = ''
                for j in range(self.way_num):
                    tmp_string += "                  tag  :" + str(self[i][j].tag)
                print(tmp_string)



def main():
    fileName = input("Please enter MIPS instruction file name: ")
    inst_file = "instr_list.txt"
    print("Note: This program assumes that the instructions are in hex.")
    inputFile = open(fileName, "r")
    outputFile = open(inst_file, "w")
    global instructions
    global diagnose
    global cache_a
    global cache_c
    global cache_d
    global cache_e
    instructions = []  # Declares instructions to be an array
    num_of_instr = 0
    diagnose = 0

    choice = True if int(input("press 1 for diagnose mode else 0 for normal operation\n")) == 1 else False

    if choice:
        while (diagnose < 1 or diagnose > 3):
            diagnose = int(input("1)multi-cycle\t\t2)slow pipeline\t\t3)fast pipeline\n"))
            if (diagnose < 1 or diagnose > 3):
                print("enter values from 1-3 ONLY puta")
    # DM (b=8, N=1, S=8)
    cache_a = Blocks(1, 8, 8)
    # C. FA, 4 blocks, 2 words each block
    cache_c = Blocks(4, 1, 16)
    # D. 2way-SA, total 8 blocks, 2 words each block
    cache_d = Blocks(2, 4, 8)
    # E. Customized cache configuration
    print("You can customize your cache configuration:")
    word = int(input("block size(wd):"))
    way = int(input("num of way:"))
    sets = int(input("num of set:"))
    cache_e = Blocks(way, sets, word)


    for line in inputFile:
        if (line == "\n" or line[0] == '#'):  # empty lines and comments ignored
            continue
        line = line.replace('\n', '')  # Removes new line characters
        line = format(int(line, 16),
                      "032b")  # The int function converts the hex instruction into some numerical value, then format converts it into a binary string
        num_of_instr = num_of_instr + 1
        instructions.append(line)
    inputFile.close()
    disassemble(instructions, diagnose, choice)

    if (diagnose == 1 or choice == 0):
        print("For cache configuration A:")
        print("    Hit rate: %.2f" % (cache_a.hit_num / cache_a.read_num))
        print("For cache configuration C:")
        print("    Hit rate: %.2f" % (cache_c.hit_num / cache_c.read_num))
        print("For cache configuration D:")
        print("    Hit rate: %.2f" % (cache_d.hit_num / cache_d.read_num))
        print("For cache configuration E:")
        print("    Hit rate: %.2f" % (cache_e.hit_num / cache_e.read_num))
        print("------------------ Multi-cycle cpu ------------------")
        print("Total # of cycles = " + str(cycle))
        print("# of 3 cycles = " + str(threecycle))
        print("% of instructions are 3 cycles = " + str(threecycle/pc) + " %")
        print("# of 4 cycles = " + str(fourcycle))
        print("% of instructions are 3 cycles = " + str(fourcycle/pc) + " %")
        print("# of 5 cycles = " + str(fivecycle))
        print("% of instructions are 3 cycles = " + str(fivecycle/pc) + " %")
    if (diagnose == 2 or choice == 0):
        print("------------------ Slow pipeline cpu ------------------")
        print("Total # of cycles = " + str(pipeIntrs + NOP + 4))
        print("Number of control hazards = " + str(chSUM))
        print("Number of data hazards = " + str(dhSUM))

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

def disassemble(instructions, diagnose, choice):
    global n
    global NOP
    global outputFile
    instr = []
    global pc
    global cycle
    global pipeIntrs
    global dhSUM
    global chSUM
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
            elif (diagnose == 2 or choice == 0):
                print("cycle: " + str(cycle))
                if (n+1 <= len(instructions) - 1):
                    if (getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t):
                        print("Data hazard")
                        print("Number of NOPs: 2")
                        NOP += 2
                        dhSUM += 2
                        skip = True
                if (n+2 <= len(instructions) - 1 and not skip):
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
            print("ori $" + str(t) + ", $" + str(s) + ", 0d" + str(imm))
            print("pc = " + str(pc*4) + "\n")
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
            elif (diagnose == 2):
                print("cycle: " + str(cycle))
                if (n+1 <= len(instructions) - 1):
                    if (getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t):
                        print("Data hazard")
                        print("Number of NOPs: 2")
                        NOP += 2
                        dhSUM += 2
                        skip = True
                if (n+2 <= len(instructions) - 1 and not skip):
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
            print("lw $" + str(t) + "," + str(imm) + "($" + str(s) + ")")
            print("pc = " + str(pc*4) + "\n")
            print("------------------------- cache -------------------------")
            print("target" + hex(mems_location[mems_index]))
            # cache A
            print("A. DM, 4 blocks, 4 words each block")
            target_block_index = cache_a.get_blk_index(mems_index)
            target_block = cache_a.get_the_block_need_to_write(mems_index)
            print("   blk/set to access :", target_block_index)
            print("   valid bit         :", target_block.vali)
            print("   tag               :", target_block.tag)
            hit = cache_a.read(mems_index)
            print("   hit or not        :", hit)
            if hit:
                print("   cache update info : no update ")

            else:
                print("   cache update info :")
                cache_a.show()


            print()
            print("C. FA, 4 blocks, 2 words each block")
            target_block_index = cache_c.get_blk_index(mems_index)
            target_block = cache_c.get_the_block_need_to_write(mems_index)
            print("   blk/set to access :", target_block_index)
            print("   valid bit         :", target_block.vali)
            print("   tag               :", target_block.tag)
            hit = cache_c.read(mems_index)
            print("   hit or not        :", hit)
            if hit:
                print("   cache update info : no update ")

            else:
                print("   cache update info :")
                cache_c.show()

            print()
            print("D. 2way-SA, total 8 blocks, 2 words each block")
            target_block_index = cache_d.get_blk_index(mems_index)
            target_block = cache_d.get_the_block_need_to_write(mems_index)
            print("   blk/set to access :", target_block_index)
            print("   valid bit         :", target_block.vali)
            print("   tag               :", target_block.tag)
            hit = cache_d.read(mems_index)
            print("   hit or not        :", hit)
            if hit:
                print("   cache update info : no update ")

            else:
                print("   cache update info :")
                cache_d.show()
            print()
            print("E. Customized cache configuration ")
            target_block_index = cache_e.get_blk_index(mems_index)
            target_block = cache_e.get_the_block_need_to_write(mems_index)
            print("   blk/set to access :", target_block_index)
            print("   valid bit         :", target_block.vali)
            print("   tag               :", target_block.tag)
            hit = cache_e.read(mems_index)
            print("   hit or not        :", hit)
            if hit:
                print("   cache update info : no update ")

            else:
                print("   cache update info :")
                cache_e.show()

           
            print("=== Cache Log End ====\n")
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
            elif (diagnose == 2 or choice == 0):
                print("cycle: " + str(cycle))
                if (n+1 <= len(instructions) - 1):
                    if (getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t):
                        print("Data hazard")
                        print("Number of NOPs: 2")
                        NOP += 2
                        dhSUM += 2
                        skip = True
                if (n+2 <= len(instructions) - 1 and not skip):
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
            print("addi $" + str(t) + ", $" + str(s) + ", " + str(imm))
            print("pc = " + str(pc*4) + "\n")
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
            elif (diagnose == 2 or choice == 0):
                print("cycle: " + str(cycle))
                print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
            print("sw $" + str(t) + ", " + str(imm) + "($" + str(s) + ")")
            print("pc = " + str(pc*4) + "\n")
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
            elif (diagnose == 2 or choice == 0):
                print("cycle: " + str(cycle))
                print("Control hazard")
                print("Number of NOPs: 3")
                NOP += 3
                chSUM += 3
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
            print("beq $" + str(t) + ", $" + str(s) + ", " + str(imm))
            print("pc = " + str(pc*4) + "\n")
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
            elif (diagnose == 2 or choice == 0):
                print("cycle: " + str(cycle))
                #if (oldRD == s or oldRD == t):
                print("Control hazard")
                print("Number of NOPs: 3")
                NOP += 3
                chSUM += 3
                #else: 
                #    print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
            print("bne $" + str(t) + ", $" + str(s) + ", " + str(imm))
            print("pc = " + str(pc*4) + "\n")
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
                elif (diagnose == 2 or choice == 0):
                    print("cycle: " + str(cycle))
                    if (n+1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n+2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
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
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                elif (diagnose == 2 or choice == 0):
                    print("cycle: " + str(cycle))
                    if (n+1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n+2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
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
                elif (diagnose == 2 or choice == 0):
                    print("cycle: " + str(cycle))
                    if (n+1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n+2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
                print("slt $" + str(d) + ", $" + str(s) + ", $" + str(t))
                print("pc = " + str(pc * 4) + "\n")
                cycle += 4 
                pipeIntrs += 1
                fourcycle += 1

            # ------------------ sltu ------------------
            if(instr[26:32] == "101011"):
                outputFile.write("sltu $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                #S = regs[s] & allf
                #T = regs[t] & allf
                S = abs(regs[s])
                T = abs(regs[t])
                if(S < T):
                    regs[d] = 1
                else:
                    regs[d] = 0
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                elif (diagnose == 2 or choice == 0):
                    print("cycle: " + str(cycle))
                    if (n+1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n+2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
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
                elif (diagnose == 2 or choice == 0):
                    print("cycle: " + str(cycle))
                    if (n+1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n+2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
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
                elif (diagnose == 2 or choice == 0):
                    print("cycle: " + str(cycle))
                    if (n+1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n+2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
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
                elif (diagnose == 2 or choice == 0):
                    print("cycle: " + str(cycle))
                    if (n+1 <= len(instructions) - 1):
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 1]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                            skip = True
                    if (n+2 <= len(instructions) - 1 and not skip):
                        if (getRS(instructions[n + 2]) == d or getRT(instructions[n + 2]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 1")
                            NOP += 1
                            dhSUM += 1
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
                print("xor $" + str(d) + ", $" + str(s) + ", $" + str(t))
                print("pc = " + str(pc * 4) + "\n")
                cycle += 4 
                pipeIntrs += 1
                fourcycle += 1
        n = n + 1
        


# It's not really necessary to understand how it works for this class, but it allows us to use this code as a module or a standalone program.
if __name__ == "__main__":
    main()
