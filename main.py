import sys
import os
from compiler.lexer import tokenize
from compiler.parser import Parser
from compiler.codegen import CodeGenerator
from compiler.codegen_c import CodeGeneratorC

def transpile(source_code, use_wx=False, to_c=False):
    tokens = tokenize(source_code)
    parser = Parser(tokens)
    ast = parser.parse()
    if to_c:
        codegen = CodeGeneratorC()
    else:
        codegen = CodeGenerator(use_wx=use_wx)
    return codegen.generate(ast)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [--wx] [--c] <filename.bas>")
        sys.exit(1)
    
    use_wx = "--wx" in sys.argv
    to_c = "--c" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--wx", "--c")]
    
    if not args:
        print("Usage: python main.py [--wx] [--c] <filename.bas>")
        sys.exit(1)

    filename = args[0]
    with open(filename, 'r') as f:
        code = f.read()
    
    output_code = transpile(code, use_wx=use_wx, to_c=to_c)
    
    if to_c:
        output_filename = filename.replace('.bas', '.c')
    else:
        output_filename = filename.replace('.bas', '.py')
        
    with open(output_filename, 'w') as f:
        f.write(output_code)
    print(f"Transpiled {filename} to {output_filename}")
