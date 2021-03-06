import json
import sys
from rply import LexerGenerator
from rply import ParserGenerator

lg = LexerGenerator()

lg.add("NUMBER", r"\d+")
lg.add("INDENTIFIER", r"[a-zA-Z]+")
lg.add("COMMA", r",")
lg.add("SPACE", r"\s")

ast=[]

pg = ParserGenerator(["INDENTIFIER", "SPACE", "NUMBER", "COMMA"], precedence=[])

@pg.production("a : INDENTIFIER SPACE INDENTIFIER")
@pg.production("a : INDENTIFIER SPACE NUMBER")
def a(p):
    cmd = p[0].getstr()
    if p[2].gettokentype() == "INDENTIFIER":
        val = {"type":"var", "val":p[2].getstr()}
    elif p[2].gettokentype() == "NUMBER":
        val = {"type":"const", "val":p[2].getstr()}

    if cmd == "JMP":
        ast.append({"cmd":"JMP", "vals":[val]})
    if cmd == "JMPTRUE":
        ast.append({"cmd":"JMPTRUE", "vals":[val]})
    if cmd == "JMPFALSE":
        ast.append({"cmd":"JMPFALSE", "vals":[val]})
    elif cmd == "PUSH":
        ast.append({"cmd":"PUSH", "vals":[val]})
    elif cmd == "PRINT":
        ast.append({"cmd":"PRINT", "vals":[val]})
    elif cmd == "PRINTRAW":
        ast.append({"cmd":"PRINTRAW", "vals":[val]})

@pg.production("a : INDENTIFIER SPACE INDENTIFIER COMMA SPACE INDENTIFIER")
@pg.production("a : INDENTIFIER SPACE INDENTIFIER COMMA SPACE NUMBER")
def b(p):
    cmd = p[0].getstr()
    
    if p[2].gettokentype() == "INDENTIFIER":
        lval = {"type":"var", "val":p[2].getstr()}

    if p[5].gettokentype() == "INDENTIFIER":
        rval = {"type":"var", "val":p[5].getstr()}
    elif p[5].gettokentype() == "NUMBER":
        rval = {"type":"const", "val":int(p[5].getstr())}

    if cmd == "SET":
        ast.append({"cmd":"SET", "vals":[lval, rval]})

    elif cmd == "EQU":
        ast.append({"cmd":"EQU", "vals":[lval, rval]})

    elif cmd == "PLUS":
        ast.append({"cmd":"PLUS", "vals":[lval, rval]})
    
    elif cmd == "MUT":
        ast.append({"cmd":"MUT", "vals":[lval, rval]})

def getVal(env, val):
    if val["type"] == "const":
        return val["val"]
    elif val["type"] == "var":
        return env[val["val"]]
        
def exec():
    cursor = 0
    env = {}
    stack = []
    flag = 0
    while cursor < len(ast):
        current_cmd = ast[cursor]["cmd"]
        current_vals = ast[cursor]["vals"]
        
        if current_cmd == "SET":
            env[current_vals[0]["val"]] = getVal(env, current_vals[1])

        if current_cmd == "PLUS":
            env[current_vals[0]["val"]] += getVal(env, current_vals[1])
            
        if current_cmd == "MUT":
            env[current_vals[0]["val"]] *= getVal(env, current_vals[1])

        if current_cmd == "JMP":
            cursor = int(getVal(env, current_vals[0]))
            continue

        if current_cmd == "JMPTRUE":
            if flag == 1:
                cursor = int(getVal(env, current_vals[0]))
                continue
            
        if current_cmd == "JMPFALSE":
            if flag == 0:
                cursor = int(getVal(env, current_vals[0]))
                continue

        if current_cmd == "PUSH":
            stack.append(getVal(env, current_vals[0]))
        
        if current_cmd == "PRINT":
            c = int(getVal(env, current_vals[0]))
            for _ in range(c):
                print(chr(int(stack.pop())), end="")

        if current_cmd == "PRINTRAW":
            c = int(getVal(env, current_vals[0]))
            for _ in range(c):
                print(int(stack.pop()), end="")

        if current_cmd == "EQU":
            #print(env[current_vals[0]["val"]], getVal(env, current_vals[1]))
            if getVal(env, current_vals[0]) == getVal(env, current_vals[1]):
                flag = 1
            else:
                flag = 0
        cursor += 1
        
lexer = lg.build()
parser = pg.build()

f=open(sys.argv[1], "r")
code = f.read()
f.close()

for i in code.split("\n"):
    if i:
        #print(i)
        parser.parse(lexer.lex(i))

#print(json.dumps(ast, indent=4, sort_keys=True))
exec()
