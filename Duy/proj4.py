regs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; #Registers $0 ~ $23
mems = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; #memory 0x2000 to 0x2050

last_Instruction_stored = 0 #Detect for last instruction written into (2 NOPS)
second_last_stored = 0 #Moves last instruction written here for 1 NOP
pipeCycle = 4  #instruction should finish at "5th cycle"
branchNOP = 0
branchStall = 0
cycle = 0
threecycle = 0
fourcycle = 0
fivecycle = 0
pc = -1
end = 0
n = 0
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

    diagnose = True if int(input("press 1 for diagnose mode else 0 for normal operation\n")) == 1 else False

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

    #print("\n------------------ MIPS Instructions file compile successfully ------------------\n")
    #print("Here is the number of instruction in the MIPS instructions file: " + str(num_of_instr))
    #print("Here is the total number of the instructions of the program: " + str(counter) + "\n")

    #print("------------------ Register Content ------------------")
    #print("Register" + "           " + "Value")
    #for x in range(23):
    #    if (regs[x] > 2147483647):
    #        regs[x] = 4294967295 - regs[x] + 1
    #        regs[x] = -regs[x]
    #    print("$" + str('{:>2}'.format(x)) + str('{:>20}'.format(regs[x])))

    #print("PC " + str('{:>20}'.format(pc * 4)))
    #print("\n")
    #print("------------------ Memory Content ------------------")
    #print("Memory Address" + "              " + "Value")

    #memory_initial = 0x1FFC
    #for x in range(21):
    #    memory_initial = memory_initial + 4
    #    print("M[" + str(hex(memory_initial)) + "]" + str('{:>25}'.format(mems[x])))

    print("------------------ Multi-cycle cpu ------------------")
    print("Total # of cycles = " + str(cycle))
    print("# of 3 cycles = " + str(threecycle))
    print("% of instructions are 3 cycles = " + str(threecycle/pc) + " %")
    print("# of 4 cycles = " + str(fourcycle))
    print("% of instructions are 3 cycles = " + str(fourcycle/pc) + " %")
    print("# of 5 cycles = " + str(fivecycle))
    print("% of instructions are 3 cycles = " + str(fivecycle/pc) + " %" + "\n")
    print("------------------- Slow-Pipe cpu -------------------")
    print("Total # of cycles = " + str(cycle + branchNOP))
    print("delays: " + str(branchStall))


def disassemble(instructions, diagnose):
    global n
    global outputFile
    instr = []
    global pc
    global cycle
    global threecycle
    global fourcycle
    global fivecycle
    global pipeCycle
    global branchNOP
    global branchStall
    global last_Instruction_stored
    global second_last_stored
    global end
    global num_of_instr
    global counter
    while end != 1:
        # print(n)

        instr = instructions[n]

        n += 1
        pc += 1
        pipeCycle += 1
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
            if diagnose:
                print("cycle: " + str(cycle))
                print("Running 4 cycles")
                print("ori $" + str(t) + ", $" + str(s) + ", 0d" + str(imm))
                print("pc = " + str(pc*4) + "\n")
            cycle += 4
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
            if diagnose:
                print("cycle: " + str(cycle))
                print("Running 5 cycles")
                print("lw $" + str(t) + "," + str(imm) + "($" + str(s) + ")")
                print("pc = " + str(pc*4) + "\n")
            cycle += 5
            fivecycle += 1

        # ------------------ addi ------------------

        if (instr[0:6] == "001000"):
            outputFile.write("addi $" + str(t) + ", $" + str(s) + ", " + str(imm) + "\n")
            regs[t] = regs[s] + imm
            outputFile.write("r" + str(t) + " = " + str(regs[t]) + "\n")
            if diagnose:
                print("cycle: " + str(cycle))
                print("Running 4 cycles")
                print("addi $" + str(t) + ", $" + str(s) + ", " + str(imm))
                print("pc = " + str(pc*4) + "\n")
            cycle += 4
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
            if diagnose:
                print("cycle: " + str(cycle))
                print("Running 4 cycles")
                print("sw $" + str(t) + ", " + str(imm) + "($" + str(s) + ")")
                print("pc = " + str(pc*4) + "\n")
            cycle += 4
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
            if diagnose:
                print("cycle: " + str(cycle))
                print("Running 3 cycles")
                print("beq $" + str(t) + ", $" + str(s) + ", " + str(imm))
                print("pc = " + str(pc*4) + "\n")
            cycle += 3
            threecycle += 1
            branchNOP = 3
            branchStall += 1

        # ------------------ bne ------------------

        if (instr[0:6] == "000101"):  # bne
            outputFile.write("bne $" + str(t) + ", $" + str(s) + ", " + str(imm) + "\n")
            outputFile.write("bne " + str(regs[t]) + " , " + str(regs[s]) + " , " + str(imm) + "\n")
            if (regs[t] != regs[s]):
                pc = pc + imm
                n = n + imm
            if diagnose:
                print("cycle: " + str(cycle))
                print("Running 3 cycles")
                print("bne $" + str(t) + ", $" + str(s) + ", " + str(imm))
                print("pc = " + str(pc*4) + "\n")
            cycle += 3
            threecycle += 1
            branchNOP = 3
            branchStall += 1

        # -------------------------------------------- R TYPE --------------------------------------------

        if (instr[0:6] == "000000"):
            d = int(instr[16:21], 2)
            sh = int(instr[21:26], 2)

            # ------------------ add ------------------

            if (instr[26:32] == "100000"):
                outputFile.write("add $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = regs[s] + regs[t]
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if diagnose:
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print("add $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                fourcycle += 1

            # ------------------ sub ------------------

            if (instr[26:32] == "100010"):
                outputFile.write("sub $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = regs[s] - regs[t]
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if diagnose:
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print("sub $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                fourcycle += 1

            # ------------------ slt ------------------

            if (instr[26:32] == "101010"):
                outputFile.write("slt $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                if (regs[s] < regs[t]):
                    regs[d] = 1
                else:
                    regs[d] = 0
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if diagnose:
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print("slt $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                fourcycle += 1

            # ------------------ sltu ------------------
            if(instr[26:32] == "101011"):
                outputFile.write("sltu $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                S = regs[s] & allf
                T = regs[t] & allf
                if(S < T):
                    regs[d] = 1
                else:
                    regs[d] = 0
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if diagnose:
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print("sltu $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                fourcycle += 1

            # ------------------ addu ------------------

            if (instr[26:32] == "100001"):  # ADDU
                outputFile.write("addu $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = regs[s] + regs[t]
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if diagnose:
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print("addu $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                fourcycle += 1

            # ------------------ sll ------------------

            if (instr[26:32] == "000000"):
                outputFile.write("sll $" + str(d) + ", $" + str(t) + ", " + str(sh) + "\n")
                regs[d] = (regs[t] << sh) & (0xFFFFFFFF)
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if diagnose:
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print("sll $" + str(d) + ", $" + str(t) + ", " + str(sh))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                fourcycle += 1

            # ------------------ xor ------------------

            if (instr[26:32] == "100110"):
                outputFile.write("xor $" + str(d) + ", $" + str(s) + ", $" + str(t) + "\n")
                regs[d] = regs[s] ^ regs[t]
                outputFile.write("r" + str(d) + " = " + str(regs[d]) + "\n")
                if diagnose:
                    print("cycle: " + str(cycle))
                    print("Running 4 cycles")
                    print("xor $" + str(d) + ", $" + str(s) + ", $" + str(t))
                    print("pc = " + str(pc * 4) + "\n")
                cycle += 4
                fourcycle += 1


# It's not really necessary to understand how it works for this class, but it allows us to use this code as a module or a standalone program.
if __name__ == "__main__":
    main()
