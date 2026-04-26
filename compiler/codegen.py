from . import ast_nodes as ast
import os

class CodeGenerator:
    def __init__(self, use_wx=False):
        self.indent_level = 0
        self.output = []
        self.dimmed_vars = set()
        if use_wx:
            self.output.append("from lb_runtime import gui_wx as gui, builtins, database")
        else:
            self.output.append("from lb_runtime import gui, builtins, database")
        self.output.append("")
        self.output.append("class Handles:")
        self.output.append("    def __getattr__(self, name):")
        self.output.append("        if name.startswith('P'): return getattr(database, name)")
        self.output.append("        if name.startswith('F'): return getattr(builtins, 'PFile')")
        self.output.append("        # Auto-create LBWindow for unknown handles to allow deferred GUI")
        self.output.append("        win = gui.LBWindow()")
        self.output.append("        setattr(self, name, win)")
        self.output.append("        return win")
        self.output.append("")
        self.output.append("handles = Handles()")
        self.output.append("gui.set_handles(handles)")
        self.output.append("")
        self.current_function = None

    def indent(self):
        return "    " * self.indent_level

    def emit(self, line):
        self.output.append(self.indent() + line)

    def normalize_id(self, name):
        if not name: return name
        if name.startswith('#'):
            return "handles." + name[1:].replace('.', '_').lower()
        lower_name = name.lower()
        if lower_name in ('windowwidth', 'windowheight', 'upperleftx', 'upperlefty', 'displaywidth', 'displayheight', 'mousex', 'mousey'):
             # Map LB4 special variables to builtins module
             return "builtins." + lower_name.replace('windowwidth', 'WindowWidth').replace('windowheight', 'WindowHeight').replace('upperleftx', 'UpperLeftX').replace('upperlefty', 'UpperLeftY').replace('displaywidth', 'DisplayWidth').replace('displayheight', 'DisplayHeight').replace('mousex', 'MouseX').replace('mousey', 'MouseY')
        
        # BASIC variable suffixes: $ (string), % (integer), & (long), ! (single/float), # (double)
        name = lower_name
        if name.endswith('$'): name = name[:-1] + "_str"
        elif name.endswith('%'): name = name[:-1] + "_int"
        elif name.endswith('&'): name = name[:-1] + "_long"
        elif name.endswith('!'): name = name[:-1] + "_float"
        elif name.endswith('#'): name = name[:-1] + "_double"
        
        return name.replace('.', '_')

    def generate(self, node):
        self.visit(node)
        return "\n".join(self.output)

    def visit(self, node):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{node.__class__.__name__} method')

    def visit_ProgramNode(self, node):
        functions = [s for s in node.statements if isinstance(s, (ast.SubNode, ast.FunctionNode))]
        others = [s for s in node.statements if not isinstance(s, (ast.SubNode, ast.FunctionNode))]
        
        for func in functions:
            self.visit(func)
        
        for stmt in others:
            self.visit(stmt)

    def get_assigned_vars(self, statements):
        vars = set()
        for stmt in statements:
            if isinstance(stmt, ast.AssignNode):
                vars.add(self.normalize_id(stmt.target))
            elif isinstance(stmt, ast.LbConfirmNode):
                vars.add(self.normalize_id(stmt.var))
            elif isinstance(stmt, ast.LbPromptNode):
                vars.add(self.normalize_id(stmt.var))
            elif isinstance(stmt, ast.LbLineInputNode):
                vars.add(self.normalize_id(stmt.var))
            elif isinstance(stmt, ast.IfNode):
                vars.update(self.get_assigned_vars(stmt.then_branch))
                if stmt.else_branch:
                    vars.update(self.get_assigned_vars(stmt.else_branch))
            elif isinstance(stmt, (ast.ForNode, ast.WhileNode)):
                if isinstance(stmt, ast.ForNode):
                    vars.add(self.normalize_id(stmt.var))
                vars.update(self.get_assigned_vars(stmt.body))
        return vars

    def visit_SubNode(self, node):
        name = self.normalize_id(node.name)
        params = [self.normalize_id(p) for p in node.params]
        self.emit(f"def {name}({', '.join(params)}):")
        self.indent_level += 1
        
        assigned = self.get_assigned_vars(node.body)
        for var in sorted(list(assigned)):
            if var not in params and '.' not in var and not var.startswith('handles.'):
                self.emit(f"global {var}")

        if not node.body:
            self.emit("pass")
        else:
            for stmt in node.body:
                self.visit(stmt)
        self.indent_level -= 1
        self.emit("")

    def visit_FunctionNode(self, node):
        name = self.normalize_id(node.name)
        self.current_function = name
        params = [self.normalize_id(p) for p in node.params]
        self.emit(f"def {name}({', '.join(params)}):")
        self.indent_level += 1
        self.emit(f"{name} = None")
        
        assigned = self.get_assigned_vars(node.body)
        for var in sorted(list(assigned)):
            if var != name and var not in params and '.' not in var and not var.startswith('handles.'):
                self.emit(f"global {var}")

        if not node.body:
            self.emit("pass")
        else:
            for stmt in node.body:
                self.visit(stmt)
        self.emit(f"return {name}")
        self.indent_level -= 1
        self.emit("")
        self.current_function = None

    def visit_AssignNode(self, node):
        if isinstance(node.target, ast.ArrayAccessNode):
            target = self.visit(node.target)
        else:
            target = self.normalize_id(node.target)
        value = self.visit(node.value)
        self.emit(f"{target} = {value}")

    def visit_LbDimNode(self, node):
        name = self.normalize_id(node.name)
        self.dimmed_vars.add(name)
        size = self.visit(node.size)
        if name.endswith('_str'):
            self.emit(f"{name} = [''] * (int({size}) + 1)")
        else:
            self.emit(f"{name} = [0] * (int({size}) + 1)")

    def visit_ArrayAccessNode(self, node):
        name = self.normalize_id(node.name)
        index = self.visit(node.index)
        return f"{name}[int({index})]"

    def visit_IfNode(self, node):
        condition = self.visit(node.condition)
        self.emit(f"if {condition}:")
        self.indent_level += 1
        for stmt in node.then_branch:
            self.visit(stmt)
        self.indent_level -= 1
        if node.else_branch:
            self.emit("else:")
            self.indent_level += 1
            for stmt in node.else_branch:
                self.visit(stmt)
            self.indent_level -= 1

    def visit_ForNode(self, node):
        var = self.normalize_id(node.var)
        start = self.visit(node.start)
        end = self.visit(node.end)
        step = self.visit(node.step)
        self.emit(f"for {var} in range(int({start}), int({end}) + 1, int({step})):")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1

    def visit_WhileNode(self, node):
        condition = self.visit(node.condition)
        self.emit(f"while {condition}:")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1

    def visit_CallStmtNode(self, node):
        val = self.visit(node.call_node)
        self.emit(val)

    def visit_CallNode(self, node):
        name = self.normalize_id(node.name)
        args_list = [self.visit(arg) for arg in node.args]
        args = ", ".join([str(a) for a in args_list])
        if name in ('abs', 'acos', 'asin', 'atan', 'cos', 'exp', 'floor', 'log', 'sin', 'sqrt', 'tan', 'pi'):
            return f"builtins.{name}({args})"
        elif name in ('left_str', 'mid_str', 'right_str', 'upper_str', 'lower_str', 'len', 'instr', 'val', 'str_str', 'space_str', 'string_str', 'ltrim_str', 'rtrim_str', 'trim_str', 'int', 'chr_str', 'asc', 'eof'):
            py_name = name
            if py_name == 'len': py_name = 'len_str'
            elif py_name == 'int': py_name = 'int_val'
            return f"builtins.{py_name}({args})"
        if name in self.dimmed_vars and len(args_list) == 1:
            return f"{name}[int({args_list[0]})]"
        return f"{name}({args})"

    def visit_PrintNode(self, node):
        content = self.visit(node.content)
        if node.handle:
            handle = self.normalize_id(node.handle)
            self.emit(f"{handle}.command({content})")
        else:
            self.emit(f"print({content})")

    def visit_LbWaitNode(self, node):
        self.emit("gui.run_event_loop()")

    def visit_LbNoticeNode(self, node):
        msg = self.visit(node.message)
        self.emit(f"gui.notice({msg})")

    def visit_LbConfirmNode(self, node):
        msg = self.visit(node.message)
        var = self.normalize_id(node.var)
        self.emit(f"{var} = gui.confirm({msg})")

    def visit_LbPromptNode(self, node):
        msg = self.visit(node.message)
        var = self.normalize_id(node.var)
        self.emit(f"{var} = gui.prompt({msg})")

    def visit_OpenWindowNode(self, node):
        handle = self.normalize_id(node.handle)
        title = self.visit(node.title)
        if node.type == 'WINDOW':
            self.emit(f"{handle}.open({title}, builtins.WindowWidth, builtins.WindowHeight)")
        elif node.type == 'SQLITE':
            self.emit(f"{handle} = handles.PSQLite({title})")
        elif node.type == 'MYSQL':
            self.emit(f"{handle} = handles.PMySQL({title})")
        elif node.type in ('INPUT', 'OUTPUT', 'APPEND'):
            self.emit(f"{handle} = handles.FFile({title}, '{node.type.lower()}')")

    def visit_CloseNode(self, node):
        handle = self.normalize_id(node.handle)
        self.emit(f"{handle}.close()")

    def visit_LbFillNode(self, node):
        handle = self.normalize_id(node.handle)
        db_handle = self.normalize_id(node.db_handle)
        sql = self.visit(node.sql)
        self.emit(f"{handle}.fill_from_db({db_handle}, {sql})")

    def visit_LbLineInputNode(self, node):
        handle = self.normalize_id(node.handle)
        var = self.normalize_id(node.var)
        self.emit(f"{var} = {handle}.readline()")

    def visit_LbMenuNode(self, node):
        handle = self.normalize_id(node.handle)
        title = self.visit(node.title)
        items = []
        for cap, handler in node.items:
            h = self.normalize_id(handler) if handler else "None"
            items.append(f"({self.visit(cap)}, {h})")
        items_str = "[" + ", ".join(items) + "]"
        self.emit(f"{handle}.add_menu({title}, {items_str})")

    def visit_LbTabControlNode(self, node):
        handle = self.normalize_id(node.handle)
        parent_handle = "handles." + node.handle.split('.')[0][1:].lower()
        x = self.visit(node.x)
        y = self.visit(node.y)
        w = self.visit(node.w)
        h = self.visit(node.h)
        self.emit(f"{handle} = gui.LBTabControl({parent_handle}, x={x}, y={y}, w={w}, h={h})")

    def visit_LbLocateNode(self, node):
        x = self.visit(node.x)
        y = self.visit(node.y)
        # Usually for terminal/graphicbox, just print for now or stub
        self.emit(f"print(f'LOCATE at {x}, {y}')")

    def visit_ExitStmtNode(self, node):
        if node.type in ('FOR', 'WHILE'):
            self.emit("break")
        else:
            self.emit("return")

    def visit_GuiControlNode(self, node):
        handle = self.normalize_id(node.handle)
        parent_handle = "handles." + node.handle.split('.')[0][1:].lower()
        type_map = {
            'BUTTON': 'LBButton',
            'TEXTBOX': 'LBTextbox',
            'TEXTEDITOR': 'LBTexteditor',
            'STATICTEXT': 'LBStatictext',
            'LISTBOX': 'LBListbox',
            'COMBOBOX': 'LBCombobox',
            'CHECKBOX': 'LBCheckbox',
            'RADIOBUTTON': 'LBRadiobutton',
            'GROUPBOX': 'LBGroupbox',
            'LISTVIEW': 'LBListview',
            'DATEPICKER': 'LBDatepicker',
            'PSTRINGGRID': 'LBStringGrid',
            'GRAPHICBOX': 'LBGraphicbox'
        }
        cls = type_map.get(node.type, 'LBControl')
        caption = self.visit(node.caption)
        handler = self.normalize_id(node.handler) if node.handler else "None"
        x = self.visit(node.x)
        y = self.visit(node.y)
        w = self.visit(node.w)
        h = self.visit(node.h)
        self.emit(f"{handle} = gui.{cls}({parent_handle}, caption={caption}, handler={handler}, x={x}, y={y}, w={w}, h={h})")

    def visit_LiteralNode(self, node):
        if isinstance(node.value, str):
            escaped = node.value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
            return f'"{escaped}"'
        return str(node.value)

    def visit_VarNode(self, node):
        return self.normalize_id(node.name)

    def visit_BinOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if op == '+':
            return f"({left} + {right})"
        if op == '=': op = '=='
        elif op == '<>': op = '!='
        elif op.upper() == 'AND': op = 'and'
        elif op.upper() == 'OR': op = 'or'
        elif op.upper() == 'MOD': op = '%'
        return f"({left} {op} {right})"

    def visit_UnaryOpNode(self, node):
        expr = self.visit(node.expr)
        op = node.op
        if op.upper() == 'NOT': op = 'not '
        return f"({op}{expr})"
