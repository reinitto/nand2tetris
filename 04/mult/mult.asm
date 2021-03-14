// do a while loop and add to R2 the value of R1 R0 times

@i
M=0
@R2
M=0
(LOOP)
@i
D=M
@R0
D=M-D
@END
D;JEQ
@i
M=M+1
@R1
D=M
@R2
M=M+D
@LOOP
0;JMP


(END)
@END
0;JMP