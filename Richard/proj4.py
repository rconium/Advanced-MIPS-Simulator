regs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; #Registers $0 ~ $23
mems = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; #memory 0x2000 to 0x2050

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
allf = 0xFFFFFFFF
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
    disassemble(instructions, diagnose, choice)

    if (diagnose == 1 or choice == 0):
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


    oldRD = -1

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
                if (n+2 <= len(instructions) - 1):
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
            elif (diagnose == 2 or choice == 0):
                print("cycle: " + str(cycle))
                if (n+1 <= len(instructions) - 1):
                    if (getRS(instructions[n + 1]) == t or getRT(instructions[n + 1]) == t):
                        print("Data hazard")
                        print("Number of NOPs: 2")
                        NOP += 2
                        dhSUM += 2
                if (n+2 <= len(instructions) - 1):
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
                if (n+2 <= len(instructions) - 1):
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
                    if (n+2 <= len(instructions) - 1):
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
                    if (n+2 <= len(instructions) - 1):
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
                    if (n+2 <= len(instructions) - 1):
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
                    if (n+2 <= len(instructions) - 1):
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
                        if (getRS(instructions[n + 1]) == d or getRT(instructions[n + 2]) == d):
                            print("Data hazard")
                            print("Number of NOPs: 2")
                            NOP += 2
                            dhSUM += 2
                    if (n+2 <= len(instructions) - 1):
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
                oldRD = d

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
                    if (n+2 <= len(instructions) - 1):
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
                oldRD = d

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
                    if (n+2 <= len(instructions) - 1):
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
                oldRD = d
        n = n + 1
        


# It's not really necessary to understand how it works for this class, but it allows us to use this code as a module or a standalone program.
if __name__ == "__main__":
    main()