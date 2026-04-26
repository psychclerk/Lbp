from .lexer import Token
from . import ast_nodes as ast

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        if self.pos + offset >= len(self.tokens):
            return Token('EOF', '', -1, -1)
        return self.tokens[self.pos + offset]

    def consume(self, expected_type=None):
        token = self.peek()
        if expected_type and token.type != expected_type:
            raise RuntimeError(f"Expected {expected_type}, got {token.type} at line {token.line}")
        self.pos += 1
        return token

    def match(self, *types):
        token = self.peek()
        if token.type in types:
            return self.consume()
        return None

    def parse(self):
        statements = []
        while self.peek().type != 'EOF':
            while self.match('NEWLINE', 'COLON'): continue
            if self.peek().type == 'EOF': break
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            while self.match('NEWLINE', 'COLON'): continue
        return ast.ProgramNode(statements)

    def parse_statement(self):
        token = self.peek()
        if token.type == 'SUB':
            return self.parse_sub()
        elif token.type == 'FUNCTION':
            return self.parse_function()
        elif token.type == 'IF':
            return self.parse_if()
        elif token.type == 'FOR':
            return self.parse_for()
        elif token.type == 'WHILE':
            return self.parse_while()
        elif token.type == 'PRINT':
            return self.parse_print()
        elif token.type == 'WAIT':
            self.consume('WAIT')
            return ast.LbWaitNode()
        elif token.type == 'NOTICE':
            return self.parse_notice()
        elif token.type == 'CONFIRM':
            return self.parse_confirm()
        elif token.type == 'PROMPT':
            return self.parse_prompt()
        elif token.type == 'OPEN':
            return self.parse_open()
        elif token.type == 'CLOSE':
            return self.parse_close()
        elif token.type == 'FILL':
            return self.parse_fill()
        elif token.type == 'LINE':
            return self.parse_line_input()
        elif token.type == 'DIM':
            return self.parse_dim()
        elif token.type == 'MENU':
            return self.parse_menu()
        elif token.type == 'TABCONTROL':
            return self.parse_tabcontrol()
        elif token.type == 'LOCATE':
            self.consume('LOCATE')
            x = self.parse_expression()
            self.match('COMMA')
            y = self.parse_expression()
            return ast.LbLocateNode(x, y)
        elif token.type == 'CALL':
            self.consume('CALL')
            return ast.CallStmtNode(self.parse_call())
        elif token.type == 'HANDLE':
            handle = self.consume().value
            content = self.parse_expression()
            return ast.PrintNode(handle, content)
        elif token.type == 'EXIT':
            self.consume('EXIT')
            type = self.consume().type # SUB, FUNCTION, FOR, WHILE
            return ast.ExitStmtNode(type)
        elif token.type in ('BUTTON', 'TEXTBOX', 'TEXTEDITOR', 'STATICTEXT', 'LISTBOX', 'COMBOBOX', 'CHECKBOX', 'RADIOBUTTON', 'GROUPBOX', 'LISTVIEW', 'DATEPICKER', 'PSTRINGGRID', 'GRAPHICBOX'):
            return self.parse_gui_control()
        elif token.type == 'ID':
            # Check for assignment
            is_assign = False
            if self.peek(1).type == 'OP' and self.peek(1).value == '=':
                is_assign = True
            elif self.peek(1).type == 'LPAREN':
                # Look ahead for RPAREN followed by =
                p = 2
                depth = 1
                while self.pos + p < len(self.tokens):
                    t = self.peek(p)
                    if t.type == 'LPAREN': depth += 1
                    elif t.type == 'RPAREN':
                        depth -= 1
                        if depth == 0:
                            if self.peek(p+1).type == 'OP' and self.peek(p+1).value == '=':
                                is_assign = True
                            break
                    elif t.type == 'NEWLINE': break
                    p += 1
            
            if is_assign:
                return self.parse_assignment()
            else:
                return ast.CallStmtNode(self.parse_call())
        else:
            # Skip unknown for now or raise error
            self.consume()
            return None

    def parse_sub(self):
        self.consume('SUB')
        name = self.consume('ID').value
        params = []
        if self.match('LPAREN'):
            while self.peek().type != 'RPAREN':
                params.append(self.consume('ID').value)
                if not self.match('COMMA'): break
            self.consume('RPAREN')
        else:
            while self.peek().type == 'ID':
                params.append(self.consume('ID').value)
                if not self.match('COMMA'): break
        body = []
        while self.peek().type != 'END' and self.peek().type != 'EOF':
            while self.match('NEWLINE'): continue
            if self.peek().type == 'END': break
            stmt = self.parse_statement()
            if stmt: body.append(stmt)
            while self.match('NEWLINE'): continue
        self.consume('END')
        self.match('SUB')
        return ast.SubNode(name, params, body)

    def parse_function(self):
        self.consume('FUNCTION')
        name = self.consume('ID').value
        params = []
        if self.match('LPAREN'):
            while self.peek().type != 'RPAREN':
                params.append(self.consume('ID').value)
                if not self.match('COMMA'): break
            self.consume('RPAREN')
        else:
            while self.peek().type == 'ID':
                params.append(self.consume('ID').value)
                if not self.match('COMMA'): break
        body = []
        while self.peek().type != 'END' and self.peek().type != 'EOF':
            while self.match('NEWLINE'): continue
            if self.peek().type == 'END': break
            stmt = self.parse_statement()
            if stmt: body.append(stmt)
            while self.match('NEWLINE'): continue
        self.consume('END')
        self.match('FUNCTION')
        return ast.FunctionNode(name, params, body)

    def parse_if(self):
        self.consume('IF')
        condition = self.parse_expression()
        self.consume('THEN')
        then_branch = []
        else_branch = []
        
        # Handle single line IF vs block IF
        if self.peek().type != 'NEWLINE':
            then_branch.append(self.parse_statement())
            while self.match('COLON'):
                then_branch.append(self.parse_statement())
            if self.match('ELSE'):
                else_branch.append(self.parse_statement())
                while self.match('COLON'):
                    else_branch.append(self.parse_statement())
        else:
            while self.peek().type not in ('ELSE', 'END') and self.peek().type != 'EOF':
                while self.match('NEWLINE'): continue
                if self.peek().type in ('ELSE', 'END'): break
                stmt = self.parse_statement()
                if stmt: then_branch.append(stmt)
            if self.match('ELSE'):
                while self.peek().type != 'END' and self.peek().type != 'EOF':
                    while self.match('NEWLINE'): continue
                    if self.peek().type == 'END': break
                    stmt = self.parse_statement()
                    if stmt: else_branch.append(stmt)
            self.consume('END')
            self.match('IF')
        return ast.IfNode(condition, then_branch, else_branch)

    def parse_for(self):
        self.consume('FOR')
        var = self.consume('ID').value
        self.consume('OP') # =
        start = self.parse_expression()
        self.consume('TO')
        end = self.parse_expression()
        step = ast.LiteralNode(1)
        if self.match('STEP'):
            step = self.parse_expression()
        body = []
        while self.peek().type != 'NEXT' and self.peek().type != 'EOF':
            while self.match('NEWLINE'): continue
            if self.peek().type == 'NEXT': break
            stmt = self.parse_statement()
            if stmt: body.append(stmt)
        self.consume('NEXT')
        self.match('ID') # Optional var name after NEXT
        return ast.ForNode(var, start, end, step, body)

    def parse_while(self):
        self.consume('WHILE')
        condition = self.parse_expression()
        body = []
        while self.peek().type != 'WEND' and self.peek().type != 'EOF':
            while self.match('NEWLINE'): continue
            if self.peek().type == 'WEND': break
            stmt = self.parse_statement()
            if stmt: body.append(stmt)
        self.consume('WEND')
        return ast.WhileNode(condition, body)

    def parse_print(self):
        self.consume('PRINT')
        handle = None
        if self.peek().type == 'HANDLE':
            handle = self.consume().value
            self.match('COMMA')
        content = self.parse_expression()
        return ast.PrintNode(handle, content)

    def parse_notice(self):
        self.consume('NOTICE')
        msg = self.parse_expression()
        return ast.LbNoticeNode(msg)

    def parse_confirm(self):
        self.consume('CONFIRM')
        msg = self.parse_expression()
        self.match('SEMICOLON')
        var = self.consume('ID').value
        return ast.LbConfirmNode(msg, var)

    def parse_prompt(self):
        self.consume('PROMPT')
        msg = self.parse_expression()
        self.match('SEMICOLON')
        var = self.consume('ID').value
        return ast.LbPromptNode(msg, var)

    def parse_open(self):
        self.consume('OPEN')
        title = self.parse_expression()
        self.consume('FOR')
        type_token = self.peek()
        if type_token.type in ('ID', 'WINDOW', 'SQLITE', 'MYSQL', 'INPUT', 'OUTPUT', 'APPEND'):
            type = self.consume().type
        else:
            raise RuntimeError(f"Expected window or file type, got {type_token.type} at line {type_token.line}")
        self.consume('AS')
        handle = self.consume('HANDLE').value
        return ast.OpenWindowNode(handle, title, type)

    def parse_close(self):
        self.consume('CLOSE')
        handle = self.consume('HANDLE').value
        return ast.CloseNode(handle)

    def parse_fill(self):
        self.consume('FILL')
        handle = self.consume('HANDLE').value
        db_handle = self.consume('HANDLE').value
        sql = self.parse_expression()
        return ast.LbFillNode(handle, db_handle, sql)

    def parse_line_input(self):
        self.consume('LINE')
        self.consume('INPUT')
        handle = self.consume('HANDLE').value
        self.match('COMMA')
        var = self.consume('ID').value
        return ast.LbLineInputNode(handle, var)

    def parse_menu(self):
        self.consume('MENU')
        handle = self.consume('HANDLE').value
        self.consume('COMMA')
        title = self.parse_expression()
        items = []
        while self.peek().type == 'COMMA':
            self.consume('COMMA')
            caption = self.parse_expression()
            handler = ""
            # Look ahead to see if the next token is a handler
            if self.peek().type == 'COMMA':
                next_tok = self.peek(1)
                if next_tok.type in ('LBRACKET', 'ID'):
                    self.consume('COMMA')
                    if self.match('LBRACKET'):
                        handler = self.consume('ID').value
                        self.consume('RBRACKET')
                    else:
                        handler = self.consume('ID').value
            items.append((caption, handler))
        return ast.LbMenuNode(handle, title, items)

    def parse_tabcontrol(self):
        self.consume('TABCONTROL')
        handle = self.consume('HANDLE').value
        self.consume('COMMA')
        x = self.parse_expression()
        self.consume('COMMA')
        y = self.parse_expression()
        self.consume('COMMA')
        w = self.parse_expression()
        self.consume('COMMA')
        h = self.parse_expression()
        return ast.LbTabControlNode(handle, x, y, w, h)

    def parse_gui_control(self):
        type = self.consume().type
        handle = self.consume('HANDLE').value
        self.consume('COMMA')
        
        caption = ast.LiteralNode("")
        handler = ""
        
        if self.peek().type == 'STRING':
            caption = self.parse_expression()
            self.match('COMMA')
        
        if self.match('LBRACKET'):
            handler = self.consume('ID').value
            self.consume('RBRACKET')
            self.match('COMMA')
        elif self.peek().type == 'ID' and self.peek().value not in ('UL', 'UR', 'LL', 'LR'):
            handler = self.consume('ID').value
            self.match('COMMA')
        
        if self.peek().type == 'ID' and self.peek().value in ('UL', 'UR', 'LL', 'LR'):
            self.consume()
            self.match('COMMA')
            
        x = self.parse_expression()
        self.consume('COMMA')
        y = self.parse_expression()
        self.consume('COMMA')
        w = self.parse_expression()
        self.consume('COMMA')
        h = self.parse_expression()
        return ast.GuiControlNode(type, handle, caption, handler, x, y, w, h)

    def parse_assignment(self):
        target = self.consume('ID').value
        if self.match('LPAREN'):
            index = self.parse_expression()
            self.consume('RPAREN')
            self.consume('OP') # =
            value = self.parse_expression()
            return ast.AssignNode(ast.ArrayAccessNode(target, index), value)
        
        self.consume('OP') # =
        value = self.parse_expression()
        return ast.AssignNode(target, value)

    def parse_dim(self):
        self.consume('DIM')
        name = self.consume('ID').value
        self.consume('LPAREN')
        size = self.parse_expression()
        self.consume('RPAREN')
        return ast.LbDimNode(name, size)

    def parse_call(self):
        name = self.consume('ID').value
        args = []
        if self.match('LPAREN'):
            while self.peek().type != 'RPAREN':
                args.append(self.parse_expression())
                if not self.match('COMMA'): break
            self.consume('RPAREN')
        elif self.peek().type not in ('NEWLINE', 'EOF', 'ELSE', 'END'):
            while self.peek().type not in ('NEWLINE', 'EOF', 'ELSE', 'END'):
                args.append(self.parse_expression())
                if not self.match('COMMA'): break
        return ast.CallNode(name, args)

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        node = self.parse_logical_and()
        while True:
            op_tok = self.peek()
            if op_tok.type == 'OR':
                self.consume()
                node = ast.BinOpNode(node, 'OR', self.parse_logical_and())
            else:
                break
        return node

    def parse_logical_and(self):
        node = self.parse_comparison()
        while True:
            op_tok = self.peek()
            if op_tok.type == 'AND':
                self.consume()
                node = ast.BinOpNode(node, 'AND', self.parse_comparison())
            else:
                break
        return node

    def parse_comparison(self):
        node = self.parse_arithmetic()
        while True:
            op_tok = self.peek()
            if op_tok.type == 'OP' and op_tok.value in ('=', '<>', '<', '>', '<=', '>='):
                self.consume()
                node = ast.BinOpNode(node, op_tok.value, self.parse_arithmetic())
            else:
                break
        return node

    def parse_arithmetic(self):
        node = self.parse_term()
        while True:
            op_tok = self.peek()
            if op_tok.type == 'OP' and op_tok.value in ('+', '-'):
                self.consume()
                node = ast.BinOpNode(node, op_tok.value, self.parse_term())
            else:
                break
        return node

    def parse_term(self):
        node = self.parse_factor()
        while True:
            op_tok = self.peek()
            if op_tok.type == 'OP' and op_tok.value in ('*', '/'):
                self.consume()
                node = ast.BinOpNode(node, op_tok.value, self.parse_factor())
            elif op_tok.type == 'MOD':
                self.consume()
                node = ast.BinOpNode(node, 'MOD', self.parse_factor())
            else:
                break
        return node

    def parse_factor(self):
        if self.match('LPAREN'):
            node = self.parse_expression()
            self.consume('RPAREN')
            return node
        elif self.peek().type == 'NUMBER':
            return ast.LiteralNode(self.consume().value)
        elif self.peek().type == 'STRING':
            return ast.LiteralNode(self.consume().value)
        elif self.peek().type == 'ID':
            if self.peek(1).type == 'LPAREN':
                name = self.consume().value
                self.consume('LPAREN')
                args = []
                while self.peek().type != 'RPAREN':
                    args.append(self.parse_expression())
                    if not self.match('COMMA'): break
                self.consume('RPAREN')
                return ast.CallNode(name, args)
            return ast.VarNode(self.consume().value)
        elif self.peek().type == 'HANDLE':
             return ast.VarNode(self.consume().value)
        elif self.match('NOT'):
            return ast.UnaryOpNode('NOT', self.parse_factor())
        elif self.peek().type == 'OP' and self.peek().value == '-':
            self.consume()
            return ast.UnaryOpNode('-', self.parse_factor())
        else:
            raise RuntimeError(f"Unexpected token {self.peek().type} in expression at line {self.peek().line}")
