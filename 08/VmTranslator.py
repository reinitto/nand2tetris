import sys
import os


class VMTranslator:

    def __init__(self, input_file, output_file='', initialize=False):

        self.input_file = input_file
        self.output_file = output_file
        self.initialize = initialize
        self.parsed_lines = []
        self.temp_base = 5
        self.static_base = 16
        self.stack_base = 256
        self.screen_base = 16384
        self.kbd = 24576
        self.arithmetic_commands = [
            'add', 'sub', 'eq', 'lt', 'gt', 'and', 'or', 'not', 'neg']
        self.branching_commands = ['goto', 'if-goto', 'label']
        self.line_count = 5
        self.function_stack = ['Sys.init']
        self.calls_within_function = {'Sys.init': 0}
        if not output_file:
            # destination path
            dest = input_file.split('/')
            dest[-1] = dest[-1].split('.')[0]+".asm"
            dest = '/'.join(dest)
            self.output_file = dest

    def bootstrap(self):
        lines = []

    def do_arithmetic(self, operation):
        t = ""
        t += self.pop()
        if operation == 'not':
            t += 'D=!D' + '\n'
        elif operation == 'neg':
            t += 'D=-D' + '\n'
        else:
            t += '@te' + '\n'
            t += 'M=D' + '\n'
            t += self.pop()
            t += '@te' + '\n'
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
                true_label = self.do_branching(['label', 'eq_true'])
                t += '@' + true_label[1:-2] + '\n'
                t += 'D;JEQ' + '\n'
                t += '@eq' + '\n'
                t += 'M=0' + '\n'
                # jump to here if equal
                t += true_label
                t += '@eq' + '\n'
                t += 'D=M' + '\n'
            elif operation == 'gt':
                t += 'D=D-M' + '\n'
                # set eq to true
                t += '@gt' + '\n'
                t += 'M=-1' + '\n'
                true_label = self.do_branching(['label', 'gt_true'])
                t += '@' + true_label[1:-2] + '\n'
                t += 'D;JGT' + '\n'
                t += '@gt' + '\n'
                t += 'M=0' + '\n'
                t += true_label
                t += '@gt' + '\n'
                t += 'D=M' + '\n'
            elif operation == 'lt':
                t += 'D=D-M' + '\n'
                # set eq to true
                t += '@lt' + '\n'
                t += 'M=-1' + '\n'
                true_label = self.do_branching(['label', 'lt_true'])
                t += '@' + true_label[1:-2] + '\n'
                t += 'D;JLT' + '\n'
                t += '@lt' + '\n'
                t += 'M=0' + '\n'
                # jump here if true
                t += true_label
                t += '@lt' + '\n'
                t += 'D=M' + '\n'
            elif operation == 'and':
                t += 'D=D&M' + '\n'
            elif operation == 'or':
                t += 'D=D|M' + '\n'

        t += self.push()
        return t

    def translate_a_instruction(self, segment, value):
        # after these instructions address is pointing to the segment value

        # pointer 0 == this
        # pointer 1 == that
        #  temp 5-12, also called R5-R12
        # R13-R15 == RAM[13]-RAM[15]
        translated = []
        if segment == 'constant':
            translated.append('@' + value)
            translated.append('D=A')
            translated.append('@te')
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
            curr_class = self.function_stack[-1].split('.')[0]
            addr = curr_class + '.' + (value)
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
            translated.append('@' + str(value))
            translated.append('A=D+A')
        return "\n".join(translated) + '\n'

    def parse(self):
        with open(self.input_file) as file:
            self.parsed_lines = [line.split('//')[0].rstrip().split(' ') for line in file.readlines() if len(
                line) > 1 and line[0] != "/"]

    def translate(self):
        with open(self.output_file, 'a') as output:
            self.parse()
            if self.initialize:
                initCode = ['@256', 'D=A', '@SP', 'M=D']
                output.write("\n".join(initCode)+'\n')
                output.write(self.call_function(['call', 'Sys.init', 0]))
            for line in self.parsed_lines:
                # print(line)
                command = line[0]
                translated = ''
                if command == 'push' or command == 'pop':
                    translated = self.push_or_pop(line)
                elif command in self.arithmetic_commands:
                    translated = self.do_arithmetic(command)
                    # print(len(translated.split('\n')))
                elif command in self.branching_commands:
                    translated = self.do_branching(line)
                    if command == 'label':
                        self.line_count -= 1
                elif command == 'function':
                    # function declaration
                    # create function with the provided name
                    translated = self.create_function(line)
                    self.line_count -= 1
                    # print(self.line_count)
                elif command == 'call':
                    translated = self.call_function(line)
                elif command == 'return':
                    translated = self.do_return()
                self.line_count += len(translated.split('\n'))-1
                output.write(translated)
            print(self.line_count)

    def pop(self):
        # saves pop in D
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
            add_pop.append('@te')
            add_pop.append('M=D')
            # decrease SP, get the value and save it to where A is pointing to (add_pop.append())
            # pop
            pop_res = self.pop().split('\n')
            for i in range(0, len(pop_res)-1):
                add_pop.append(pop_res[i])
            add_pop.append('@te')
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
        if command == 'label':
            if len(self.function_stack) > 0:
                # functionName$label
                translated.append("("+self.function_stack[-1]+"$"+label+")")
            else:
                translated.append("("+label+")")
        elif command == 'goto':
            # unconditional jump to label
            if len(self.function_stack) > 0:
                # functionName$label
                translated.append('@'+self.function_stack[-1]+"$"+label)
            else:
                translated.append('@'+label)
            translated.append('0;JMP')
        elif command == 'if-goto':
            # jump to label only if stack not equal to 0
            pop_res = self.pop().split('\n')
            for i in range(0, len(pop_res)-1):
                translated.append(pop_res[i])
            if len(self.function_stack) > 0:
                # functionName$label
                translated.append('@'+self.function_stack[-1]+"$"+label)
            else:
                translated.append('@'+label)

            translated.append('D;JNE')
        return '\n'.join(translated)+'\n'

    def create_function(self, line):
        # create the function label and initializes lcl variables
        command, function_name, lcl_count = line
        self.function_stack.append(function_name)
        self.calls_within_function[function_name] = 0
        t = []
        t.append("("+function_name+")")
        lcl_count = int(lcl_count)
        cnt = 0
        while cnt < lcl_count:
            # initializes lcl vars to 0
            push_or_pop_res = self.push_or_pop(
                ['push', 'constant', '0']).split('\n')
            for i in range(0, len(push_or_pop_res)-1):
                t.append(push_or_pop_res[i])
            cnt += 1
        return '\n'.join(t)+'\n'

    def call_function(self, line):
        # deal with call functionName argCount
        # call Main.fibonacci 1
        op, function_name, argCount = line
        t = []
        # push return-address // (Using the label declared below)
        # create return-label
        # current function
        ret_count = str(self.calls_within_function[self.function_stack[-1]])
        ret_label = self.function_stack[-1] + "$ret." + ret_count
        self.calls_within_function[self.function_stack[-1]] += 1
        t.append('@'+ret_label)
        t.append('D=A')
        push_res = self.push().split('\n')
        for i in range(0, len(push_res)-1):
            t.append(push_res[i])
        # push LCL // Save LCL of the calling function
        t.append('@LCL')
        t.append('D=M')
        push_res = self.push().split('\n')
        for i in range(0, len(push_res)-1):
            t.append(push_res[i])
        # push ARG // Save ARG of the calling function
        t.append('@ARG')
        t.append('D=M')
        push_res = self.push().split('\n')
        for i in range(0, len(push_res)-1):
            t.append(push_res[i])
        # push THIS // Save THIS of the calling function
        t.append('@THIS')
        t.append('D=M')
        push_res = self.push().split('\n')
        for i in range(0, len(push_res)-1):
            t.append(push_res[i])
        # push THAT // Save THAT of the calling function
        t.append('@THAT')
        t.append('D=M')
        push_res = self.push().split('\n')
        for i in range(0, len(push_res)-1):
            t.append(push_res[i])
        # ARG = SP-n-5 // Reposition ARG (n ¼ number of args.)
        t.append("@SP")
        t.append('D=M')
        t.append('@'+str(argCount))
        t.append('D=D-A')
        t.append('@5')
        t.append('D=D-A')
        t.append('@ARG')
        t.append('M=D')
        # LCL = SP // Reposition LCL
        t.append('@SP')
        t.append('D=M')
        t.append('@LCL')
        t.append('M=D')
        # goto f // Transfer control
        t.append('@'+function_name)
        t.append('0;JMP')
        # (return-address) // Declare a label for the return-address
        t.append('(' + ret_label + ")")
        return '\n'.join(t)+'\n'

    def do_return(self):
        # return from function
        # self.function_stack.pop()
        t = []
        # FRAME = LCL // FRAME is a temporary variable
        t.append('@LCL')
        t.append('D=M')
        t.append('@FRAME')
        t.append('M=D')
        # RET = *(FRAME-5) // Put the return-address in a temp. var.
        t.append('@5')
        t.append('D=D-A')
        t.append('A=D')
        t.append('D=M')
        t.append('@RET')
        t.append('M=D')
        # *ARG = pop() // Reposition the return value for the caller
        push_or_pop_res = self.push_or_pop(
            ['pop', 'argument', '0']).split('\n')
        for i in range(0, len(push_or_pop_res)-1):
            t.append(push_or_pop_res[i])
        # SP = ARG+1 // Restore SP of the caller
        t.append('@ARG')
        t.append('D=M+1')
        t.append('@SP')
        t.append('M=D')
        # THAT = *(FRAME-1) // Restore THAT of the caller
        t.append('@FRAME')
        t.append('D=M-1')
        t.append('A=D')
        t.append('D=M')
        t.append('@THAT')
        t.append('M=D')
        # THIS = *(FRAME-2) // Restore THIS of the caller
        t.append('@FRAME')
        t.append('D=M')
        t.append('@2')
        t.append('D=D-A')
        t.append('A=D')
        t.append('D=M')
        t.append('@THIS')
        t.append('M=D')
        # ARG = *(FRAME-3) // Restore ARG of the caller
        t.append('@FRAME')
        t.append('D=M')
        t.append('@3')
        t.append('D=D-A')
        t.append('A=D')
        t.append('D=M')
        t.append('@ARG')
        t.append('M=D')
        # LCL = *(FRAME-4) // Restore LCL of the caller
        t.append('@FRAME')
        t.append('D=M')
        t.append('@4')
        t.append('D=D-A')
        t.append('A=D')
        t.append('D=M')
        t.append('@LCL')
        t.append('M=D')
        # goto RET // Goto return-address (in the caller’s code)
        t.append('@RET')
        t.append('A=M')
        t.append('0;JMP')
        return '\n'.join(t)+'\n'


if __name__ == "__main__":
    filepath = sys.argv[1]
    initCode = ['@256', 'D=A', '@SP', 'M=D']
    #  translate single file
    if filepath.endswith(".vm"):
        translation = VMTranslator(filepath)
        translation.translate()
    else:
        # otherwise compile every file ending in .vm into one .asm file
        print(os.listdir(filepath))
        dir_name = filepath + "/" + \
            os.path.basename(os.path.dirname(filepath))+".asm"
        with open(dir_name, 'w') as output:
            output.write("")
        for filename in os.listdir(filepath):
            if filename.endswith('.vm'):
                translation = VMTranslator(
                    filepath + "/" + filename, dir_name, True)
                translation.translate()
