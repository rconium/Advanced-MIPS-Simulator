regs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; #Registers $0 ~ $23
mems = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; #memory 0x2000 to 0x2050

cycle = 0#fix from0
threecycle = 0
fourcycle = 0
fivecycle = 0
chSUM = 0
dhSUM = 0
pc = -1
end = 0
n = 0
num_of_instr = 0
counter = -1
allf = 0xFFFFFFFF
pipeCycles = 1

inst_file = "instr_list.txt"
outputFile = open(inst_file, "w")



def main():
    fileName = input("Please enter MIPS instruction file name: ")
    inst_file = "instr_list.txt"
    print("Note: This program assumes that the instructions are in hex.")
    inputFile = open(fileName, "r")
    outputFile = open(inst_file, "w")
    global instructions
    global diagnose
    instructions = []  # Declares instructions to be an array
    num_of_instr = 0
    diagnose = 0

    choice = True if int(input("press 1 for diagnose mode else 0 for normal operation\n")) == 1 else False

    if choice:
        while (diagnose < 1 or diagnose > 3):
            diagnose = int(input("1)multi-cycle\t\t2)slow pipeline\t\t3)fast pipeline\n"))
            if (diagnose < 1 or diagnose > 3):
                print("enter values from 1-3 ONLY puta")


    for line in inputFile:
        if (line == "\n" or line[0] == '#'):  # empty lines and comments ignored
            continue
        line = line.replace('\n', '')  # Removes new line characters
        line = format(int(line, 16),
                      "032b")  # The int function converts the hex instruction into some numerical value, then format converts it into a binary string
        num_of_instr = num_of_instr + 1
        instructions.append(line)
    inputFile.close()
    disassemble(instructions, diagnose)

    if (diagnose == 1 or choice == 0):
        print("------------------ Multi-cycle cpu ------------------")
        print("Total # of cycles = " + str(cycle))
        print("# of 3 cycles = " + str(threecycle))
        print("% of instructions are 3 cycles = " + str(threecycle/pc) + " %")
        print("# of 4 cycles = " + str(fourcycle))
        print("% of instructions are 3 cycles = " + str(fourcycle/pc) + " %")
        print("# of 5 cycles = " + str(fivecycle))
        print("% of instructions are 3 cycles = " + str(fivecycle/pc) + " %")
    elif (diagnose == 2 or choice == 0):
        print("------------------ Slow pipeline cpu ------------------")
        print("# Instructions entering pipeline: " + str(pipeCycles - 1))
        print("finishing up the last instruction: 4")
        print("Number of control hazards " + str(chSUM))
        print("Number of data hazards " + str(dhSUM))
        print("Total number of cycles in slow pipeline: " + str(pipeCycles - 1 + chSUM + dhSUM + 4))
def getCycle(argument):
    switcher = {
        1: "F",
        2: "D",
        3: "E",
        4: "M",
        0: "W",
    }
    return switcher.get((argument, "nothing"))

def decoderRs1(i):
    s = int(i[6:11], 2)
    return s
def decoderRt1(i):
        t = int(i[11:16], 2)
        return t
def decoderRs2(i):
        s = int(i[6:11], 2)
        return s
def decoderRt2(i):
        t = int(i[11:16], 2)
        return t

def disassemble(instructions, diagnose):
    global n
    global outputFile
    instr = []
    global pc
    global cycle
    global dhSUM
    global chSUM
    global threecycle
    global fourcycle
    global fivecycle
    global end
    global num_of_instr
    global counter
    global pipeCycles
    tempRs1 = -1
    tempRt1  = -1
    tempRs2 = -1
    tempRt2 = -1
    oldRD = -2

    while end != 1:
        # print(n)
        #a = n
        instr = instructions[n]
    #    if (n+1 <= len(instructions) - 1):
    #        tempRs1 = decoderRs1(instructions[n+1])
    #        tempRt1 = decoderRt1(instructions[n+1])
    #    else:
    #        tempRs1 = 0
    #        tempRt1 = 0

    #    if (n+2 <= len(instructions) - 1 ):
    #        tempRs2 = decoderRs2(instructions[n+2])
    #        tempRt2 = decoderRt2(instructions[n+2])
    #    else:
    #        tempRs2 = 0
    #        tempRt2 = 0


        #n = n + 1
        pc = pc + 1
        currentPC = pc * 4
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
            print("ori $" + str(t) + ", $" + str(s) + ", 0d" + str(imm))
            print("pc = " + str(pc*4))
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 4 cycles")
                cycle += 4
            elif (diagnose == 2):
                print("cycle: " + str(pipeCycles))
                pipeCycles += 1
                if (oldRD == tempRs1 or oldRD == tempRt1 ):
                    print("Data hazard")
                    print("Number of NOPs: 2")
                    dhSUM += 2
                elif (oldRD == tempRs2 or oldRD == tempRt2):
                    print("Data hazard")
                    print("Number of NOPs: 1")
                    dhSUM += 1
                else:
                    print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                    print()
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
                    print()
                if (n+1 <= len(instructions) - 1):
                    tempRs1 = decoderRs1(instructions[n+1])
                    tempRt1 = decoderRt1(instructions[n+1])
                else:
                    tempRs1 = 0
                    tempRt1 = 0

                if (n+2 <= len(instructions) - 1 ):
                    tempRs2 = decoderRs2(instructions[n+2])
                    tempRt2 = decoderRt2(instructions[n+2])
                else:
                    tempRs2 = 0
                    tempRt2 = 0
            #cycle += 4
            n = n + 1
            fourcycle += 1
            oldRD = t

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
            print("lw $" + str(t) + "," + str(imm) + "($" + str(s) + ")")
            print("pc = " + str(pc*4))
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 5 cycles")
                print()
                cycle += 5
            elif (diagnose == 2):
                print("cycle: " + str(pipeCycles))
                pipeCycles += 1
                if (oldRD == tempRs1 or oldRD == tempRt1 ):
                    print("Data hazard")
                    print("Number of NOPs: 2")
                    dhSUM += 2
                elif (oldRD == tempRs2 or oldRD == tempRt2):
                    print("Data hazard")
                    print("Number of NOPs: 1")
                    dhSUM += 1
                else:
                    print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
                    print()
                if (n+1 <= len(instructions) - 1):
                    tempRs1 = decoderRs1(instructions[n+1])
                    tempRt1 = decoderRt1(instructions[n+1])
                else:
                    tempRs1 = 0
                    tempRt1 = 0

                if (n+2 <= len(instructions) - 1 ):
                    tempRs2 = decoderRs2(instructions[n+2])
                    tempRt2 = decoderRt2(instructions[n+2])
                else:
                    tempRs2 = 0
                    tempRt2 = 0

            #cycle += 5
            n = n  + 1
            fivecycle += 1
            oldRD = t

        # ------------------ addi ------------------

        if (instr[0:6] == "001000"):
            outputFile.write("addi $" + str(t) + ", $" + str(s) + ", " + str(imm) + "\n")
            regs[t] = regs[s] + imm
            outputFile.write("r" + str(t) + " = " + str(regs[t]) + "\n")
            print("addi $" + str(t) + ", $" + str(s) + ", " + str(imm))
            print("pc = " + str(pc*4))
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 4 cycles")
                print()
                cycle += 4
            elif (diagnose == 2):
                print("cycle: " + str(pipeCycles))
                pipeCycles += 1
                if (oldRD == tempRs1 or oldRD == tempRt1 ):
                    print("Data hazard")
                    print("Number of NOPs: 2")
                    dhSUM += 2
                elif (oldRD == tempRs2 or oldRD == tempRt2):
                    print("Data hazard")
                    print("Number of NOPs: 1")
                    dhSUM += 1
                else:
                    print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                    print()
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
                    print()
                if (n+1 <= len(instructions) - 1):
                    tempRs1 = decoderRs1(instructions[n+1])
                    tempRt1 = decoderRt1(instructions[n+1])
                else:
                    tempRs1 = 0
                    tempRt1 = 0

                if (n+2 <= len(instructions) - 1 ):
                    tempRs2 = decoderRs2(instructions[n+2])
                    tempRt2 = decoderRt2(instructions[n+2])
                else:
                    tempRs2 = 0
                    tempRt2 = 0

            #cycle += 4
            n = n + 1
            fourcycle += 1
            oldRD = t

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
            print("sw $" + str(t) + ", " + str(imm) + "($" + str(s) + ")")
            print("pc = " + str(pc*4))
            if (diagnose == 1):
                print("cycle: " + str(cycle))
                print("Running 4 cycles")
                print()
                cycle += 4
            elif (diagnose == 2):
                print("cycle: " + str(pipeCycles))
                pipeCycles += 1
                if (oldRD == tempRs1 or oldRD == tempRt1 ):
                    print("Data hazard")
                    print("Number of NOPs: 2")
                    dhSUM += 2
                elif (oldRD == tempRs2 or oldRD == tempRt2):
                    print("Data hazard")
                    print("Number of NOPs: 1")
                    dhSUM += 1
                else:
                    print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
                    print()
                if (n+1 <= len(instructions) - 1):
                    tempRs1 = decoderRs1(instructions[n+1])
                    tempRt1 = decoderRt1(instructions[n+1])
                else:
                    tempRs1 = 0
                    tempRt1 = 0

                if (n+2 <= len(instructions) - 1 ):
                    tempRs2 = decoderRs2(instructions[n+2])
                    tempRt2 = decoderRt2(instructions[n+2])
                else:
                    tempRs2 = 0
                    tempRt2 = 0

            #cycle += 4
            n = n + 1
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
                cycle += 3
            elif (diagnose == 2):
                print("cycle: " + str(cycle))
                if (oldRD == s or oldRD == t):
                    print("Control hazard")
                    print("Number of NOPs: 2")
                    chSUM += 1
                else:
                    print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
            print("beq $" + str(t) + ", $" + str(s) + ", " + str(imm))
            print("pc = " + str(pc*4) + "\n")
            #cycle += 3
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
                cycle += 3
            elif (diagnose == 2):
                print("cycle: " + str(cycle))
                if (oldRD == s or oldRD == t):
                    print("Control hazard")
                    print("Number of NOPs: 2")
                    chSUM += 1
                else:
                    print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
            print("bne $" + str(t) + ", $" + str(s) + ", " + str(imm))
            print("pc = " + str(pc*4) + "\n")
            #cycle += 3
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
                    cycle += 4
                elif (diagnose == 2):
                    print("cycle: " + str(cycle))
                    if (oldRD == s or oldRD == t):
                        print("Data hazard")
                        print("Number of NOPs: 3")
                        dhSUM += 1
                    else:
                        print("No hazard")
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
                print("add $" + str(d) + ", $" + str(s) + ", $" + str(t))
                print("pc = " + str(pc * 4) + "\n")
                #cycle += 4
                fourcycle += 1
                oldRD = d

            # ------------------ sub ------------------

            if (instr[26:32] == "100010"):
                outputFile.write("sub $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = regs[s] - regs[t]
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                print("sub $" + str(d) + ", $" + str(s) + ", $" + str(t))
                print("pc = " + str(pc * 4))
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print()
                    cycle += 4
                elif (diagnose == 2):
                    print("cycle: " + str(pipeCycles))
                    pipeCycles += 1
                    if (oldRD == tempRs1 or oldRD == tempRt1 ):
                        print("Data hazard")
                        print("Number of NOPs: 2")
                        dhSUM += 2
                    elif (oldRD == tempRs2 or oldRD == tempRt2):
                        print("Data hazard")
                        print("Number of NOPs: 1")
                        dhSUM += 1
                    else:
                        print("No hazard")
                    if (currentPC == 0):
                        print("pipeline stage: F")
                        print()
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
                        print()
                    if (n+1 <= len(instructions) - 1):
                        tempRs1 = decoderRs1(instructions[n+1])
                        tempRt1 = decoderRt1(instructions[n+1])
                    else:
                        tempRs1 = 0
                        tempRt1 = 0

                    if (n+2 <= len(instructions) - 1 ):
                        tempRs2 = decoderRs2(instructions[n+2])
                        tempRt2 = decoderRt2(instructions[n+2])
                    else:
                        tempRs2 = 0
                        tempRt2 = 0
                #cycle += 4
                n = n + 1
                fourcycle += 1
                oldRD = d

            # ------------------ slt ------------------

            if (instr[26:32] == "101010"):
                outputFile.write("slt $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                if (regs[s] < regs[t]):
                    regs[d] = 1
                else:
                    regs[d] = 0
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                print("slt $" + str(d) + ", $" + str(s) + ", $" + str(t))
                print("pc = " + str(pc * 4))
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print()
                    cycle += 4
                elif (diagnose == 2):
                    print("cycle: " + str(pipeCycles))
                    pipeCycles += 1
                if (oldRD == tempRs1 or oldRD == tempRt1 ):
                    print("Data hazard")
                    print("Number of NOPs: 2")
                    dhSUM += 2
                elif (oldRD == tempRs2 or oldRD == tempRt2):
                    print("Data hazard")
                    print("Number of NOPs: 1")
                    dhSUM += 1
                else:
                    print("No hazard")
                if (currentPC == 0):

                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
                    print()
                if (n+1 <= len(instructions) - 1):
                    tempRs1 = decoderRs1(instructions[n+1])
                    tempRt1 = decoderRt1(instructions[n+1])
                else:
                    tempRs1 = 0
                    tempRt1 = 0

                if (n+2 <= len(instructions) - 1 ):
                    tempRs2 = decoderRs2(instructions[n+2])
                    tempRt2 = decoderRt2(instructions[n+2])
                else:
                    tempRs2 = 0
                    tempRt2 = 0
                #cycle += 4
                n = n + 1
                fourcycle += 1
                oldRD = d

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
                print("sltu $" + str(d) + ", $" + str(s) + ", $" + str(t))
                print("pc = " + str(pc * 4))
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print()
                    cycle += 4
                elif (diagnose == 2):
                    print("cycle: " + str(pipeCycles))
                    pipeCycles += 1
                if (oldRD == tempRs1 or oldRD == tempRt1 ):
                    print("Data hazard")
                    print("Number of NOPs: 2")
                    dhSUM += 2
                elif (oldRD == tempRs2 or oldRD == tempRt2):
                    print("Data hazard")
                    print("Number of NOPs: 1")
                    dhSUM += 1
                else:
                    print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
                    print()
                if (n+1 <= len(instructions) - 1):
                    tempRs1 = decoderRs1(instructions[n+1])
                    tempRt1 = decoderRt1(instructions[n+1])
                else:
                    tempRs1 = 0
                    tempRt1 = 0

                if (n+2 <= len(instructions) - 1 ):
                    tempRs2 = decoderRs2(instructions[n+2])
                    tempRt2 = decoderRt2(instructions[n+2])
                else:
                    tempRs2 = 0
                    tempRt2 = 0
                #cycle += 4
                n = n + 1
                fourcycle += 1
                oldRD = d

            # ------------------ addu ------------------

            if (instr[26:32] == "100001"):  # ADDU
                outputFile.write("addu $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = abs(regs[s]) + abs(regs[t])
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                print("addu $" + str(d) + ", $" + str(s) + ", $" + str(t))
                print("pc = " + str(pc * 4))
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    cycle += 4
                elif (diagnose == 2):
                    print("cycle: " + str(pipeCycles))
                    pipeCycles += 1
                if (oldRD == tempRs1 or oldRD == tempRt1 ):
                    print("Data hazard")
                    print("Number of NOPs: 2")
                    dhSUM += 2
                elif (oldRD == tempRs2 or oldRD == tempRt2):
                    print("Data hazard")
                    print("Number of NOPs: 1")
                    dhSUM += 1
                else:
                    print("No hazard")
                if (currentPC == 0):
                    print("pipeline stage: F")
                else:
                    currentPC = currentPC % 5
                    print("pipeline stage: " + str(getCycle(currentPC)))
                    print()
                if (n+1 <= len(instructions) - 1):
                    tempRs1 = decoderRs1(instructions[n+1])
                    tempRt1 = decoderRt1(instructions[n+1])
                else:
                    tempRs1 = 0
                    tempRt1 = 0

                if (n+2 <= len(instructions) - 1 ):
                    tempRs2 = decoderRs2(instructions[n+2])
                    tempRt2 = decoderRt2(instructions[n+2])
                else:
                    tempRs2 = 0
                    tempRt2 = 0
                #cycle += 4
                n = n + 1
                fourcycle += 1
                oldRD = d

            # ------------------ sll ------------------

            if (instr[26:32] == "000000"):
                outputFile.write("sll $" + str(d) + ", $" + str(t) + ", " + str(sh) + "\n")
                regs[d] = (regs[t] << sh) & (0xFFFFFFFF)
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    cycle += 4
                elif (diagnose == 2):
                    print("cycle: " + str(cycle))
                    if (oldRD == s or oldRD == t):
                        print("Data hazard")
                        print("Number of NOPs: 3")
                        dhSUM += 1
                    else:
                        print("No hazard")
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
                print("sll $" + str(d) + ", $" + str(t) + ", " + str(sh))
                print("pc = " + str(pc * 4) + "\n")
                #cycle += 4
                fourcycle += 1
                oldRD = d

            # ------------------ xor ------------------

            if (instr[26:32] == "100110"):
                outputFile.write("xor $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = regs[s] ^ regs[t]
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                print("xor $" + str(d) + ", $" + str(s) + ", $" + str(t))
                print("pc = " + str(pc * 4))
                if (diagnose == 1):
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print()
                    cycle += 4
                elif (diagnose == 2):
                    print("cycle: " + str(pipeCycles))
                    pipeCycles += 1
                    if (oldRD == tempRs1 or oldRD == tempRt1 ):
                        print("Data hazard")
                        print("Number of NOPs: 2")
                        dhSUM += 2
                    elif (oldRD == tempRs2 or oldRD == tempRt2):
                        print("Data hazard")
                        print("Number of NOPs: 1")
                        dhSUM += 1
                    else:
                        print("No hazard")
                    if (currentPC == 0):
                        print("pipeline stage: F")
                    else:
                        currentPC = currentPC % 5
                        print("pipeline stage: " + str(getCycle(currentPC)))
                        print()
                    if (n+1 <= len(instructions) - 1):
                        tempRs1 = decoderRs1(instructions[n+1])
                        tempRt1 = decoderRt1(instructions[n+1])
                    else:
                        tempRs1 = 0
                        tempRt1 = 0

                    if (n+2 <= len(instructions) - 1 ):
                        tempRs2 = decoderRs2(instructions[n+2])
                        tempRt2 = decoderRt2(instructions[n+2])
                    else:
                        tempRs2 = 0
                        tempRt2 = 0

                #cycle += 4
                n = n + 1
                fourcycle += 1
                oldRD = d



# It's not really necessary to understand how it works for this class, but it allows us to use this code as a module or a standalone program.
if __name__ == "__main__":
    main()
