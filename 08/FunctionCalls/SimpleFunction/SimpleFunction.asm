@256
D=A
@SP
M=D
@Sys.init
0;JMP
(SimpleFunction.test)
@0
D=A
@te
M=D
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@te
M=D
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@te
M=D
@SP
M=M-1
A=M
D=M
@te
D=D+M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
D=!D
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@te
M=D
@SP
M=M-1
A=M
D=M
@te
D=D+M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@te
M=D
@SP
M=M-1
A=M
D=M
@te
D=D-M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@FRAME
M=D
@5
D=D-A
A=D
D=M
@RET
M=D
@ARG
D=M
@0
A=D+A
D=A
@te
M=D
@SP
M=M-1
A=M
D=M
@te
A=M
M=D
@ARG
D=M+1
@SP
M=D
@FRAME
D=M-1
A=D
D=M
@THAT
M=D
@FRAME
D=M
@2
D=D-A
A=D
D=M
@THIS
M=D
@FRAME
D=M
@3
D=D-A
A=D
D=M
@ARG
M=D
@FRAME
D=M
@4
D=D-A
A=D
D=M
@LCL
M=D
@RET
A=M
0;JMP
