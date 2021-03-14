import java.io.*; // Import FileOutputStream class
import java.util.*; 

public class CompilationEngine {

    PrintWriter p;
    JackTokenizer tokenizer;
    String op = "+-*/|=&<>";

    String unaryOp = "-~";
    List<String> keywordConstant = new ArrayList<>();
    public CompilationEngine(JackTokenizer tokenizer, PrintWriter p){
        this.p = p;
        this.tokenizer = tokenizer;
        keywordConstant.add("true");
        keywordConstant.add("false");
        keywordConstant.add("null");
        keywordConstant.add("this");
    }


    public static void main(JackTokenizer tokenizer, PrintWriter p){
        CompilationEngine engine = new CompilationEngine( tokenizer, p);

        engine.compileClass();
    }

    public void compileClass(){
        // current token is class
        // class: 'class' className '{' classVarDec* subroutineDec* '}'
        p.println("<class>");

        // add opening bracket
        addNextToken();
        // add className
        p.println(addIdentifier());
        tokenizer.advance();
        // add opening bracket
        p.println(addSymbol());
        tokenizer.advance();

        // add 0 or more classVarDec
        while(isClassVarDec()){
            addClassVarDec();
        }

        // add 0 or ore subroutine dec
        while(isSubroutineDec()){
            addSubrotineDec();
        }

        // add closing bracket
        addNextToken();

        p.println("</class>");

    }

    private String addIdentifier(){
        String l = "<identifier>";
        l = l.concat(tokenizer.identifier());
        l = l.concat("</identifier>");
        return l;
    }

    private String addSymbol(){
        String l = "<symbol>";
        l = l.concat(tokenizer.symbol());
        l = l.concat("</symbol>");
        return l;
    }

    private void addClassVarDec(){
        // current token is static or field
        p.println("<classVarDec>");
        // while ";" hasnt been encountered add tokens
        while(!tokenizer.symbol().equals(";")){
            addNextToken();
        }
        // add  ";"
        addNextToken();
        p.println("</classVarDec>");
    }

    private void addSubrotineDec(){
        //subroutineDec: ('constructor'|'function'|'method')
        // ('void' | type) subroutineName '(' parameterList ')'
        // subroutineBody

        p.println("<subroutineDec>");
        // add  ('constructor'|'function'|'method')
        addNextToken();
        // add ('void' | type)
        addNextToken();
        // add subroutineName
        addNextToken();
        // add '('
        addNextToken();
        // add paramerterList
        addParameterList();
        // add ')'
        addNextToken();

        // add subroutineBody
        p.println("<subroutineBody>");
        

        // add body opening bracket
        addNextToken();

        // add 0 or more varDec
        while(isVarDec()){
            addVarDec();
        }

        // add statements
        p.println("<statements>");
        while(isStatement()){
             addStatement();
        }
        p.println("</statements>");
        p.println("</subroutineBody>");

        // add  ";"
        addNextToken();
        p.println("</subroutineDec>");
    }

    private boolean isStatement(){
        return tokenizer.tokenType().equals("KEYWORD") && (tokenizer.keyWord().equals("let") || tokenizer.keyWord().equals("if") || tokenizer.keyWord().equals("while") || tokenizer.keyWord().equals("do") || tokenizer.keyWord().equals("return"));
    }

    private void addStatement(){
        // let statement
        if(tokenizer.keyWord().equals("let")){
            p.println("<letStatement>");
            // while(!tokenizer.symbol().equals(";")){
            //     addNextToken();
            // }
            // add  "let"
            addNextToken();

            // add varName
            addNextToken();

            if(tokenizer.tokenType().equals("SYMBOL") && tokenizer.symbol().equals("[")){
                // add "["
                addNextToken();

                // add expression
                addExpression();

                // add "]"

                addNextToken();
            }

            // add "="
            addNextToken();

            // add expression

            addExpression();

            // add end ";"

            addNextToken();

            p.println("</letStatement>");

        }
        // if-else statement
        if(tokenizer.keyWord().equals("if")){
            p.println("<ifStatement>");
            // add  "if"
            addNextToken();

            // // add "("
            addNextToken();

                // add expression
            addExpression();

                // add ")"
            addNextToken();

            // // add "{"
            addNextToken();

            // // add statements
            p.println("<statements>");
            while(isStatement()){
                 addStatement();
            }
            p.println("</statements>");
            // // add "}"
            addNextToken();

            // add else 
            if(tokenizer.tokenType().equals("KEYWORD") && (tokenizer.keyWord().equals("else"))){
                // add else
                addNextToken();
                // add "{"
                addNextToken(); 

                // add statements
                p.println("<statements>");
                while(isStatement()){
                     addStatement();
                }
                p.println("</statements>");

                // add "}"
                addNextToken();
            }
            p.println("</ifStatement>");

        }

        // while statement
        if(tokenizer.keyWord().equals("while")){
            p.println("<whileStatement>");

            // add while
            addNextToken();

            // add "("
            addNextToken();

            // add expression
            addExpression();

            // add ")"
            addNextToken();

            // add "{"
            addNextToken();

            // add statements
            p.println("<statements>");
            while(isStatement()){
                 addStatement();
            }
            p.println("</statements>");
            // add "}"
            addNextToken();

            p.println("</whileStatement>");

        }
        // do statement
//         doStatement: 'do' subroutineCall ';'
        if(tokenizer.keyWord().equals("do")){
            p.println("<doStatement>");

            // not correct
            // while(!tokenizer.symbol().equals(";")){
            //     addNextToken();
            // }

            // add "do"
            addNextToken();
            // add subroutineCall

            // add className | subroutineName | varName
            addNextToken();
            if(tokenizer.symbol().equals(".")){
                // add dot
                addNextToken();
                // add subroutineName
                addNextToken();
            }

            // add opening bracket
            addNextToken();
            addExpressionList();
            
            // add closing bracket
            addNextToken();
            // add ";"
            addNextToken();
            p.println("</doStatement>");

        }
        // return statement
        // ReturnStatement 'return' expression? ';'
        if(tokenizer.keyWord().equals("return")){
            p.println("<returnStatement>");

            // not correct
            // while(!tokenizer.symbol().equals(";")){
            //     addNextToken();
            // }
            // add "return"
            addNextToken();

            if(isExpression()){
                addExpression();
            }
            // add ";"
            addNextToken();
            p.println("</returnStatement>");

        }
        
    }


    private void addExpression(){
        p.println("<expression>");
        // current will be a term
        //         term: integerConstant | stringConstant | keywordConstant |
                // varName | varName '[' expression ']' | subroutineCall |
                // '(' expression ')' | unaryOp term

        // add term
        addTerm();

        // check for operator
        while(op.contains(tokenizer.keyWord())){

            // add operator
            addNextToken();
            addTerm();
        }
        p.println("</expression>");

    }


    private void addTerm(){
        // add term
        p.println("<term>");
        //integerConstant | stringConstant | keywordConstant
        if(tokenizer.tokenType().equals("STRING_CONST")){
            addNextToken();
            
        }else if(tokenizer.tokenType().equals("INT_CONST")){
            addNextToken();

        }else if(keywordConstant.contains(tokenizer.identifier())){
            addNextToken();
        }else if(tokenizer.tokenType().equals("SYMBOL") && (tokenizer.symbol().equals("-") || tokenizer.symbol().equals("~"))){
        //  check for unary op
        // unaryOp term
            addNextToken();
            addTerm();
        }else if(tokenizer.tokenType().equals("SYMBOL") && tokenizer.symbol().equals("(")){
            // '(' expression ')' 

            // add opening bracket 
            addNextToken();
            // add expression
            addExpression();

            // add closing bracket
            addNextToken();
        }else{
            addNextToken();

            // subroutineCall:
            //subroutineName '(' expressionList ')'
            // if opening bracket then subroutineCall
            if(tokenizer.tokenType().equals("SYMBOL") && tokenizer.symbol().equals("(")){
                // add opening bracket
                addNextToken();

                // add expression list
                addExpressionList();

                // add  closing bracket
                addNextToken();
            }

            // (className | varName) '.' subroutineName '(' expressionList ')'
            if(tokenizer.tokenType().equals("SYMBOL") && tokenizer.symbol().equals(".")){
                // add dot
                addNextToken();

                // add subroutineName
                addNextToken();

                // add openingBracket
                addNextToken();

                // add expression list
                addExpressionList();

                // add closing bracket

                addNextToken();
            }
            //  varName '[' expression ']' 
            if(tokenizer.tokenType().equals("SYMBOL") && tokenizer.symbol().equals("[")){
                // add opening bracket
                addNextToken();
                addExpression();
                //add closing bracket
                addNextToken();
            }
        }


        p.println("</term>");
    }

    private void addExpressionList(){
        p.println("<expressionList>");
        while(isExpression() || tokenizer.symbol().equals(",")){
            if(tokenizer.symbol().equals(",")){
                addNextToken();
            }
            addExpression();
        }
        p.println("</expressionList>");

    }

    private boolean isExpression(){
        if(keywordConstant.contains(tokenizer.symbol())){
            return true;
        }else if(tokenizer.tokenType().equals("KEYWORD")){
            return false;
        }else if(tokenizer.tokenType().equals("INT_CONST") || tokenizer.tokenType().equals("STRING_CONST")){
            return true;
        }else if(unaryOp.contains(tokenizer.keyWord())){
            return true;
        }
        
        if(tokenizer.symbol().equals("(")){
            return true;
        }
        if(tokenizer.tokenType().equals("SYMBOL")){
            return false;
        }



        return true;
    }

    private boolean isVarDec(){
        return tokenizer.tokenType().equals("KEYWORD") && (tokenizer.keyWord().equals("var"));
    }
    private void addVarDec(){
        p.println("<varDec>");
        //'var' type varName (',' varName)* ';
        while(!tokenizer.symbol().equals(";")){
            addNextToken();
        }
        // add  ";"
        addNextToken();
        p.println("</varDec>");
    }

    private boolean isClassVarDec(){
        return tokenizer.tokenType().equals("KEYWORD") && (tokenizer.keyWord().equals("static") ||  tokenizer.keyWord().equals("field"));
    }
    private boolean isSubroutineDec(){
        return tokenizer.tokenType().equals("KEYWORD") && (tokenizer.keyWord().equals("constructor") ||  tokenizer.keyWord().equals("function")||  tokenizer.keyWord().equals("method"));
    }

    private void addParameterList(){
        p.println("<parameterList>");
        while(!tokenizer.symbol().equals(")")){
            addNextToken();
        }
        p.println("</parameterList>");
    }

    private void skipToken(){
        tokenizer.advance();
    }

    private void addNextToken(){
        String tokenType = tokenizer.tokenType();
        String l="";
        if(tokenType.equals("KEYWORD")){
          l = "<keyword>";
          l = l.concat(tokenizer.keyWord());
          l = l.concat("</keyword>");
        }else if(tokenType.equals("SYMBOL")){
          l = "<symbol>";
          l = l.concat(tokenizer.symbol());
          l = l.concat("</symbol>");
        }else if(tokenType.equals("STRING_CONST")){
          l = "<stringConstant>";
          l = l.concat(tokenizer.stringVal());
          l = l.concat("</stringConstant>");
        }else if(tokenType.equals("INT_CONST")){
          l = "<integerConstant>";
          l = l.concat(String.valueOf(tokenizer.intVal()));
          l = l.concat("</integerConstant>");
        }else if(tokenType.equals("IDENTIFIER")){
          l = "<identifier>";
          l = l.concat(tokenizer.identifier());
          l = l.concat("</identifier>");
        }
        // Print to tokenStream
        p.println(l);
        tokenizer.advance();
      }
 
}