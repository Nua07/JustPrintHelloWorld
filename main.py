import json
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
    elif cmd == "PUSH":
        ast.append({"cmd":"PUSH", "vals":[val]})
    elif cmd == "PRINT":
        ast.append({"cmd":"PRINT", "vals":[val]})

@pg.production("a : INDENTIFIER SPACE INDENTIFIER COMMA SPACE INDENTIFIER")
@pg.production("a : INDENTIFIER SPACE INDENTIFIER COMMA SPACE NUMBER")
def b(p):
    cmd = p[0].getstr()
    lval = p[2].getstr()
    rval = {}
    
    if p[5].gettokentype() == "INDENTIFIER":
        rval = {"type":"var", "val":p[5].getstr()}
    elif p[5].gettokentype() == "NUMBER":
        rval = {"type":"const", "val":int(p[5].getstr())}

    if cmd == "SET":
        ast.append({"cmd":"SET", "vals":[lval, rval]})

def getVal(env, val):
    if val["type"] == "const":
        return val["val"]
    elif val["type"] == "var":
        return env[val["val"]]
        
def exec():
    cursor = 0
    env = {}
    stack = []
    while cursor < len(ast):
        current_cmd = ast[cursor]["cmd"]
        current_vals = ast[cursor]["vals"]
        
        if current_cmd == "SET":
            env[current_vals[0]] = getVal(env, current_vals[1])
            
        if current_cmd == "JMP":
            cursor = int(getVal(env, current_vals[0]))
            continue
            
        if current_cmd == "PUSH":
            stack.append(getVal(env, current_vals[0]))
        
        if current_cmd == "PRINT":
            c = int(getVal(env, current_vals[0]))
            for i in range(c):
                print(chr(int(stack.pop())), end="")
        cursor += 1
        
lexer = lg.build()
parser = pg.build()

f=open("a.phw", "r")
code = f.read()
f.close()

for i in code.split("\n"):
    if i:
        #print(i)
        parser.parse(lexer.lex(i))

#print(json.dumps(ast, indent=4, sort_keys=True))
exec()
