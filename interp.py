import sys
import re
import os.path
from os import path


INTEGER = 'INTEGER'
PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
LPAREN = '('
RPAREN = ')'
EOF = 'EOF'

class Tokenization(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
    
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


class lexicalAnalyzer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        
    def check_next_char(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.check_next_char()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.check_next_char()
        return int(result)

    def get_next_token(self):

        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Tokenization(INTEGER, self.integer()) 

            if self.current_char == '+':
                self.check_next_char()
                return Tokenization(PLUS, '+')

            if self.current_char == '-':
                self.check_next_char()
                return Tokenization(MINUS, '-')

            if self.current_char == '*':
                self.check_next_char()
                return Tokenization(MUL, '*')

            if self.current_char == '(':
                self.check_next_char()
                return Tokenization(LPAREN, '(')

            if self.current_char == ')':
                self.check_next_char()
                return Tokenization(RPAREN, ')')

            print("Syntax Error at " , self.current_char)
            sys.exit(1)

        return Tokenization(EOF, None)



class Operator:
    def __init__(self, left, op, right):
        self.left = left #left child
        self.token = self.op = op # operator
        self.right = right # right child


class Num:
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

 
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            print("Error")
            sys.exit(0);

    def factor(self):
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    def term(self):
        node = self.factor()
        while self.current_token.type == MUL:
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            node = Operator(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = Operator(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()


class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def visit_Operator(self, node):
        # apply operation to the children of the operator
        if node.op.type == PLUS: 
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        
    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)
    def visit(self, node):
        if  type(node).__name__ == "Num":
            return self.visit_Num(node)
        elif  type(node).__name__ == "Operator":
            return self.visit_Operator(node)
        else:
            print("Error")
            sys.exit()

def read_file(file_name):
    if(path.exists(file_name) == False ):
        print('Error, file not found')
        sys.exit(0)
    # Open the file with read only permit
    f = open(file_name, "r")
    # use readlines to read all lines in the file
    # The variable "lines" is a list containing all lines in the file
    lines = f.readlines()
    # close the file after reading the lines.
    f.close()
    return lines


def check_semicolon(lines):
    for i in lines:
        if (i[-1:]) != ';':
            print('Error')
            sys.exit(0)
    return True

def split_lines(lines):
    for i in range (len(lines)):
        lines[i]= lines[i].replace("\n","")
        lines[i] = lines[i].split("=");
        
        if len(lines[i]) != 2:
            print('Error')
            sys.exit(0)
    return lines

def check_identifier(ident):
    if re.match('^[_a-z]\w*' , ident) is not None:
        return True
    return False

variables = {}

def split_exp(exp):
    global variables
    values = {}
    vars = re.findall('[_a-z]\w*' , exp)
  
    for i in  range(len(vars)):
    
        if vars[i] not in variables:
            print('Error')
            sys.exit(0)
        values[vars[i]] = variables[vars[i]]
    
    for i in vars:
        exp = exp.replace(i ,str( variables[i] ))
    
    if re.match('[a-z]|[A-Z]|_' , exp) is not None:
        sys.exit(0)
    return exp

def calculate_value(text):
    
    lexer = lexicalAnalyzer(text)

    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    return result
# ((\++)|(-+))+ 
def get_minus_plus(lis):
    ret = []
    for i in range(len(lis)):
        lis[i] = lis[i][0]
        if  '-' in lis[i]:
            ret.append( '-')
        else:
            ret.append ('+')
    return ret

def parse_line(line):
    global variables
    exp = split_exp(line)
    exp = exp.replace(';' , '')
    plus_minus = re.findall(r'(((\++)|(-+))+)' , exp)

    plus_minus_2 = get_minus_plus(plus_minus)
    for i in range (len(plus_minus)):
        exp = exp.replace(plus_minus[i] , plus_minus_2[i])
    
    mul = 1
    exp = exp.strip()
    if exp[0] == '+':
        exp = exp[1:]
        
    if exp[0] == '-':
        exp = exp[1:]
        mul = -1
    
    return calculate_value(exp) * mul

def remove_white_spaces(lines):
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    return lines

def run():
    global variables
    file_name = input("Please enter the file name that contains the code: ")
    lines = read_file(file_name)
    lines = remove_white_spaces(lines)
    check_semicolon(lines)
    lines = split_lines(lines)
    for i in lines:
        
        i[0] = i[0].replace(" " , "")
        check_identifier(i[0])
        variables[i[0]]  = parse_line(i[1])

        
    for i in sorted(variables):
        print("{}  = {}".format(i , variables[i]))

run()
