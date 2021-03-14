import sys


class VMTranslator:

    def __init__(self, input_file, output_file=''):
        # destination path
        dest = filepath.split('/')
        dest[-1] = dest[-1].split('.')[0]+".asm"
        dest = '/'.join(dest)
        self.input_file = input_file
        self.output_file = dest
        self.parsed_lines = []
        self.temp_base = 5
        self.static_base = 16
        self.stack_base = 256
        self.screen_base = 16384
        self.kbd = 24576
        self.arithmetic_commands = [
            'add', 'sub', 'eq', 'lt', 'gt', 'and', 'or', 'not', 'neg']
        self.branching_commands = ['goto', 'if-goto', 'label']
        self.line_count = -1

    def do_arithmetic(self, operation):
        t = ""
        t += self.pop()
        if operation == 'not':
            t += 'D=!D' + '\n'
        elif operation == 'neg':
            t += 'D=-D' + '\n'
        else:
            t += '@R13' + '\n'
            t += 'M=D' + '\n'
            t += self.pop()
            t += '@R13' + '\n'
            # values in D and M
            #  pop twice, do ooperation and add back to stack
            if operation == 'add':
                t += 'D=D+M' + '\n'
            elif operation == 'sub':
                t += 'D=D-M' + '\n'
            # true == -1 , false == 0
            elif operation == 'eq':
                t += 'D=D-M' + '\n'
                # set eq to true
                t += '@eq' + '\n'
                t += 'M=-1' + '\n'
                lines_so_far = self.line_count + len(t.split('\n'))-1
                # t += '@pushEq' + '\n'
                t += '@'+str(lines_so_far+5) + '\n'
                t += 'D;JEQ' + '\n'
                t += '@eq' + '\n'
                t += 'M=0' + '\n'
                # jump to here if equal
                t += '@eq' + '\n'
                t += 'D=M' + '\n'
            elif operation == 'gt':
                t += 'D=D-M' + '\n'
                # set eq to true
                t += '@gt' + '\n'
                t += 'M=-1' + '\n'
                lines_so_far = self.line_count + len(t.split('\n'))-1
                t += '@'+str(lines_so_far+5) + '\n'
                t += 'D;JGT' + '\n'
                t += '@gt' + '\n'
                t += 'M=0' + '\n'
                t += '@gt' + '\n'
                t += 'D=M' + '\n'
            elif operation == 'lt':
                t += 'D=D-M' + '\n'
                # set eq to true
                t += '@lt' + '\n'
                t += 'M=-1' + '\n'
                lines_so_far = self.line_count + len(t.split('\n'))-1
                t += '@'+str(lines_so_far+5) + '\n'
                t += 'D;JLT' + '\n'
                t += '@lt' + '\n'
                t += 'M=0' + '\n'
                t += '@lt' + '\n'
                t += 'D=M' + '\n'
            elif operation == 'and':
                t += 'D=D&M' + '\n'
            elif operation == 'or':
                t += 'D=D|M' + '\n'

        t += self.push()
        return t

        # after these instructions address is pointing to the segment value

    def translate_a_instruction(self, segment, value):
        # pointer 0 == this
        # pointer 1 == that
        #  temp 5-12, also called R5-R12
        # R13-R15 == RAM[13]-RAM[15]
        translated = []
        if segment == 'constant':
            translated.append('@' + value)
            translated.append('D=A')
            translated.append('@R13')
            translated.append('M=D')
        elif segment == 'temp':
            addr = self.temp_base + int(value)
            translated.append('@'+str(addr))
        elif segment == 'pointer':
            if(value == "0"):
                translated.append('@THIS')
            else:
                translated.append('@THAT')
        elif segment == 'static':
            addr = self.static_base + int(value)
            translated.append('@' + str(addr))
        else:
            if segment == 'local':
                translated.append("@LCL")
            elif segment == 'argument':
                translated.append('@ARG')
            elif segment == 'this':
                translated.append('@THIS')
            elif segment == 'that':
                translated.append('@THAT')
            translated.append("D=M")
            translated.append('@' + value)
            translated.append('A=D+A')
        return "\n".join(translated) + '\n'

    def parse(self):
        with open(self.input_file) as file:
            self.parsed_lines = [line.rstrip().split(' ') for line in file.readlines() if len(
                line) > 1 and line[0] != "/"]

    def translate(self):
        with open(self.output_file, 'w') as output:
            self.parse()
            for line in self.parsed_lines:
                command = line[0]
                if command == 'push' or command == 'pop':
                    translated = self.push_or_pop(line)
                    self.line_count += len(translated.split('\n'))-1
                    output.write(translated)
                elif command in self.arithmetic_commands:
                    translated = self.do_arithmetic(command)
                    # print(len(translated.split('\n')))
                    self.line_count += len(translated.split('\n'))-1
                    output.write(translated)
                elif command in self.branching_commands:
                    translated = self.do_branching(line)
                    self.line_count += len(translated.split('\n'))-1
                    output.write(translated)
            print(self.line_count)

    # saves pop in D
    def pop(self):
        t = []
        t.append("@SP")
        t.append('M=M-1')
        t.append("A=M")
        t.append('D=M')
        return "\n".join(t) + '\n'

    # pushes D to stack
    def push(self):
        t = []
        t.append('@SP')
        t.append('A=M')
        t.append('M=D')
        t.append('@SP')
        t.append('M=M+1')
        return "\n".join(t) + '\n'

    def push_or_pop(self, line):
        op, register, value = line
        # a_res end with pointing to correct ram address
        a_res = self.translate_a_instruction(register, value)
        if(op == 'pop'):
            #  save A to R13
            add_pop = []

            add_pop.append('D=A')
            add_pop.append('@R13')
            add_pop.append('M=D')
            # decrease SP, get the value and save it to where A is pointing to (add_pop.append())
            # pop
            add_pop.append(self.pop())
            add_pop.append('@R13')
            add_pop.append('A=M')
            add_pop.append('M=D')
            a_res += "\n".join(add_pop) + '\n'
        elif op == 'push':
            # save value, then push it on stack, then increase SP
            # save value to D
            a_res += 'D=M' + '\n'
            a_res += self.push()
        return a_res

    def do_branching(self, line):
        command, label = line
        translated = []
        if command is 'label':
            translated.append(add_label(argument))
        elif command is 'goto':
            # unconditional jump to label
            translated.append('@'+label)
            translated.append('0;JMP')
        elif command is 'if-goto':
            # jump to label only if stack top greater than 0
            translated.append('@SP')
            translated.append('A=M')
            translated.append('M;JGT')
        return '\n'.join(translated)+'\n'

    def add_label(self, label):
        tr = "("+label+")" + '\n'
        return tr


if __name__ == "__main__":
    filepath = sys.argv[1]
    translation = VMTranslator(filepath)
    translation.translate()
