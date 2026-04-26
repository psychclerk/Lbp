from . import ast_nodes as ast
import os

class CodeGeneratorC:
    def __init__(self):
        self.indent_level = 0
        self.output = []
        self.current_function = None
        self.global_vars = set()
        self.forward_decls = []
        self.dimmed_vars = set()
        self.array_vars = set()
        self.pending_controls = {} # parent_handle_name -> [Node]
        self.pending_commands = {} # parent_handle_name -> [(handle_name, content)]
        self.opened_windows = set()

    def pre_scan(self, node):
        if isinstance(node, ast.AssignNode):
            if isinstance(node.target, ast.ArrayAccessNode):
                name = self.normalize_id(node.target.name)
                self.global_vars.add(name)
                self.array_vars.add(name)
            else:
                self.global_vars.add(self.normalize_id(node.target))
        elif isinstance(node, ast.LbDimNode):
            name = self.normalize_id(node.name)
            self.dimmed_vars.add(name)
            self.global_vars.add(name)
            self.array_vars.add(name)
        elif isinstance(node, ast.ForNode):
            self.global_vars.add(self.normalize_id(node.var))
        elif isinstance(node, ast.LbLineInputNode):
            self.global_vars.add(self.normalize_id(node.var))
        elif isinstance(node, ast.LbConfirmNode):
            self.global_vars.add(self.normalize_id(node.var))
        elif isinstance(node, ast.LbPromptNode):
            self.global_vars.add(self.normalize_id(node.var))
        elif isinstance(node, ast.VarNode):
            if not node.name.startswith('#'):
                self.global_vars.add(self.normalize_id(node.name))
        elif isinstance(node, ast.ArrayAccessNode):
             name = self.normalize_id(node.name)
             self.global_vars.add(name)
             self.array_vars.add(name)
        elif isinstance(node, ast.CallNode):
             # Some array accesses might look like calls if they are in an expression
             # but the parser should have distinguished them. 
             # However, in Liberty BASIC, they look the same.
             # Let's check if it's potentially an array.
             pass
        elif isinstance(node, ast.LbMenuNode):
            win_handle = "lbh_" + node.handle[1:].lower() if node.handle.startswith('#') else node.handle.lower()
            self.global_vars.add(f"m_{win_handle}")
        elif isinstance(node, (ast.SubNode, ast.FunctionNode)):
            # Don't recurse into parameters for global vars, but do recurse into body
            for stmt in node.body:
                self.pre_scan(stmt)
            return

        # Recurse for all other nodes
        for attr_name in dir(node):
            if attr_name.startswith('_'): continue
            attr = getattr(node, attr_name)
            if isinstance(attr, ast.Node):
                self.pre_scan(attr)
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, ast.Node):
                        self.pre_scan(item)

    def indent(self):
        return "    " * self.indent_level

    def emit(self, line):
        self.output.append(self.indent() + line)

    def normalize_id(self, name):
        if not name: return name
        res = ""
        if name.startswith('#'):
            # For handles like #win.btn, we want lbh_win_btn
            res = "lbh_" + name[1:].replace('.', '_').lower()
            self.global_vars.add(res)
            return res
        
        lower_name = name.lower()
        if lower_name in ('windowwidth', 'windowheight', 'upperleftx', 'upperlefty', 'displaywidth', 'displayheight', 'mousex', 'mousey'):
             return lower_name.replace('windowwidth', 'WindowWidth').replace('windowheight', 'WindowHeight').replace('upperleftx', 'UpperLeftX').replace('upperlefty', 'UpperLeftY').replace('displaywidth', 'DisplayWidth').replace('displayheight', 'DisplayHeight').replace('mousex', 'MouseX').replace('mousey', 'MouseY')

        # BASIC variable suffixes
        name = lower_name
        if name.endswith('$'): name = name[:-1] + "_str"
        elif name.endswith('%'): name = name[:-1] + "_int"
        elif name.endswith('&'): name = name[:-1] + "_long"
        elif name.endswith('!'): name = name[:-1] + "_float"
        elif name.endswith('#'): name = name[:-1] + "_double"
        
        res = name.replace('.', '_')
        return res

    def is_string(self, node):
        if isinstance(node, ast.LiteralNode):
            return isinstance(node.value, str)
        if isinstance(node, ast.VarNode):
            return node.name.endswith('$')
        if isinstance(node, ast.CallNode):
            return node.name.endswith('$')
        if isinstance(node, ast.BinOpNode) and node.op == '+':
            return self.is_string(node.left) or self.is_string(node.right)
        return False

    def generate(self, node):
        self.pre_scan(node)
        self.visit(node)
        
        # Combine forward declarations and final output
        final_output = ["#include \"lb_runtime_win32.h\"", ""]
        final_output.extend(self.forward_decls)
        final_output.append("")
        
        # Global variables
        for var in sorted(list(self.global_vars)):
            if var in ('WindowWidth', 'WindowHeight', 'UpperLeftX', 'UpperLeftY', 'DisplayWidth', 'DisplayHeight', 'MouseX', 'MouseY'):
                continue
            if var in self.array_vars:
                if "_str" in var:
                    final_output.append(f"char (*{var})[1024] = NULL;")
                else:
                    final_output.append(f"double *{var} = NULL;")
                continue
            if var.startswith("lbh_"):
                # Use void* for all handles to be generic (HWND, FILE*, etc)
                final_output.append(f"void* {var} = NULL;")
            elif var.startswith("m_"):
                final_output.append(f"HMENU {var} = NULL;")
            elif "_str" in var:
                final_output.append(f"char {var}[65536] = \"\";")
            else:
                final_output.append(f"double {var} = 0;")
        final_output.append("")
        
        final_output.extend(self.output)
        
        return "\n".join(final_output) + "\n"

    def visit(self, node):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{node.__class__.__name__} method')

    def visit_ProgramNode(self, node):
        functions = [s for s in node.statements if isinstance(s, (ast.SubNode, ast.FunctionNode))]
        others = [s for s in node.statements if not isinstance(s, (ast.SubNode, ast.FunctionNode))]
        
        # First pass for forward declarations
        for func in functions:
            name = self.normalize_id(func.name)
            params = []
            for p in func.params:
                if p.endswith("$"): params.append(f"const char* {self.normalize_id(p)}")
                else: params.append(f"double {self.normalize_id(p)}")
            if isinstance(func, ast.FunctionNode):
                ret_type = "const char*" if func.name.endswith("$") else "double"
            else:
                ret_type = "void"
            p_list = ", ".join(params) if params else "void"
            self.forward_decls.append(f"{ret_type} {name}({p_list});")

        for func in functions:
            self.visit(func)
            
        self.emit("int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {")
        self.indent_level += 1
        self.emit("(void)hInstance; (void)hPrevInstance; (void)lpCmdLine; (void)nCmdShow;")
        self.emit("lb_init(hInstance, nCmdShow);")
        for stmt in others:
            self.visit(stmt)
        self.emit("return 0;")
        self.indent_level -= 1
        self.emit("}")

    def visit_SubNode(self, node):
        name = self.normalize_id(node.name)
        params = []
        for p in node.params:
            if p.endswith('$'):
                params.append(f"const char* {self.normalize_id(p)}")
            else:
                params.append(f"double {self.normalize_id(p)}")
        self.emit(f"void {name}({', '.join(params)}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")
        self.emit("")

    def visit_FunctionNode(self, node):
        name = self.normalize_id(node.name)
        params = []
        for p in node.params:
            if p.endswith('$'):
                params.append(f"const char* {self.normalize_id(p)}")
            else:
                params.append(f"double {self.normalize_id(p)}")
        ret_type = "const char*" if node.name.endswith('$') else "double"
        self.emit(f"{ret_type} {name}({', '.join(params)}) {{")
        self.indent_level += 1
        if ret_type == "double":
            self.emit(f"double {name}_ret = 0;")
        else:
            self.emit(f"static char {name}_ret[65536] = \"\";")
        for stmt in node.body:
            self.visit(stmt)
        self.emit(f"return {name}_ret;")
        self.indent_level -= 1
        self.emit("}")
        self.emit("")

    def visit_AssignNode(self, node):
        if isinstance(node.target, ast.ArrayAccessNode):
            target = self.visit(node.target)
            value = self.visit(node.value)
            if "_str" in target:
                self.emit(f"strcpy({target}, {value});")
            else:
                self.emit(f"{target} = {value};")
        else:
            target = self.normalize_id(node.target)
            self.global_vars.add(target)
            value = self.visit(node.value)
            if "_str" in target:
                self.emit(f"strcpy({target}, {value});")
            else:
                self.emit(f"{target} = {value};")

    def visit_LbDimNode(self, node):
        name = self.normalize_id(node.name)
        size = self.visit(node.size)
        if "_str" in name:
            self.emit(f"{name} = malloc(((int)({size}) + 1) * 1024);")
        else:
            self.emit(f"{name} = malloc(((int)({size}) + 1) * sizeof(double));")

    def visit_ArrayAccessNode(self, node):
        name = self.normalize_id(node.name)
        index = self.visit(node.index)
        return f"{name}[(int){index}]"

    def visit_IfNode(self, node):
        condition = self.visit(node.condition)
        self.emit(f"if ({condition}) {{")
        self.indent_level += 1
        for stmt in node.then_branch:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")
        if node.else_branch:
            self.emit("else {")
            self.indent_level += 1
            for stmt in node.else_branch:
                self.visit(stmt)
            self.indent_level -= 1
            self.emit("}")

    def visit_ForNode(self, node):
        var = self.normalize_id(node.var)
        self.global_vars.add(var)
        start = self.visit(node.start)
        end = self.visit(node.end)
        step = self.visit(node.step)
        self.emit(f"for ({var} = {start}; {var} <= {end}; {var} += {step}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")

    def visit_WhileNode(self, node):
        condition = self.visit(node.condition)
        self.emit(f"while ({condition}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")

    def visit_CallStmtNode(self, node):
        val = self.visit(node.call_node)
        self.emit(f"{val};")

    def visit_CallNode(self, node):
        name = self.normalize_id(node.name)
        
        # Special handling for eof() to avoid lb_get_text on the handle
        if name == 'eof':
            args_list = []
            for arg in node.args:
                if isinstance(arg, ast.VarNode) and arg.name.startswith('#'):
                    args_list.append(self.normalize_id(arg.name))
                else:
                    args_list.append(str(self.visit(arg)))
            args = ", ".join(args_list)
            return f"(feof((FILE*){args}) == 0 ? 0 : 1)"

        args_list = [str(self.visit(arg)) for arg in node.args]
        args = ", ".join(args_list)
        
        # Builtin mapping
        if name == 'str_str': return f"lb_str({args})"
        if name == 'val': return f"atof({args})"
        if name == 'len_str' or name == 'len': return f"strlen({args})"
        if name == 'left_str': return f"lb_left({args_list[0]}, (int)({args_list[1]}))"
        if name == 'mid_str':
            if len(node.args) == 2:
                return f"lb_mid({args_list[0]}, (int)({args_list[1]}), -1)"
            return f"lb_mid({args_list[0]}, (int)({args_list[1]}), (int)({args_list[2]}))"
        if name == 'right_str': return f"lb_right({args_list[0]}, (int)({args_list[1]}))"
        if name == 'upper_str': return f"lb_upper({args})"
        if name == 'lower_str': return f"lb_lower({args})"
        if name == 'instr': return f"lb_instr({args})"
        if name == 'chr_str': return f"lb_chr((int)({args}))"
        if name == 'asc': return f"(double)(*({args}))"
        
        if name in self.array_vars and len(args_list) == 1:
            return f"{name}[(int){args_list[0]}]"
            
        return f"{name}({args})"

    def visit_PrintNode(self, node):
        content = self.visit(node.content)
        if node.handle:
            handle_name = node.handle.lower()
            if handle_name.startswith('#'):
                win_handle_name = handle_name.split('.')[0][1:]
                if win_handle_name not in self.opened_windows:
                    self.pending_commands.setdefault(win_handle_name, []).append((node.handle, content))
                    return

            handle = self.normalize_id(node.handle)
            self.emit(f"lb_command({handle}, {content});")
        else:
            if self.is_string(node.content):
                self.emit(f"printf(\"%s\\n\", {content});")
            else:
                self.emit(f"printf(\"%g\\n\", {content});")

    def visit_LbWaitNode(self, node):
        self.emit("lb_wait();")

    def visit_LbNoticeNode(self, node):
        msg = self.visit(node.message)
        self.emit(f"lb_notice({msg});")

    def visit_LbConfirmNode(self, node):
        msg = self.visit(node.message)
        var = self.normalize_id(node.var)
        self.global_vars.add(var)
        self.emit(f"{var} = lb_confirm({msg});")

    def visit_LbPromptNode(self, node):
        msg = self.visit(node.message)
        var = self.normalize_id(node.var)
        self.global_vars.add(var)
        self.emit(f"lb_prompt({msg}, {var});")

    def visit_OpenWindowNode(self, node):
        handle = self.normalize_id(node.handle)
        title = self.visit(node.title)
        window_id = node.handle[1:].lower() if node.handle.startswith('#') else node.handle.lower()
        self.opened_windows.add(window_id)
        
        if node.type == 'WINDOW':
            self.emit(f"{handle} = lb_open_window({title});")
            self.emit(f"lb_register_handle(\"{node.handle}\", {handle});")
            # Create pending controls for this window
            if window_id in self.pending_controls:
                for ctrl_node in self.pending_controls[window_id]:
                    self.emit_control_creation(ctrl_node)
                del self.pending_controls[window_id]
        elif node.type == 'SQLITE':
            self.emit(f"{handle} = lb_open_sqlite({title});")
            self.emit(f"lb_register_handle(\"{node.handle}\", {handle});")
        elif node.type in ('INPUT', 'OUTPUT', 'APPEND'):
            self.emit(f"{handle} = lb_open_file({title}, \"{node.type.lower()}\");")
            self.emit(f"lb_register_handle(\"{node.handle}\", {handle});")

        # Emit pending commands for this window/file
        if window_id in self.pending_commands:
            for h_name, content in self.pending_commands[window_id]:
                h_id = self.normalize_id(h_name)
                self.emit(f"lb_command({h_id}, {content});")
            del self.pending_commands[window_id]

    def visit_CloseNode(self, node):
        handle = self.normalize_id(node.handle)
        self.emit(f"lb_close({handle});")

    def emit_control_creation(self, node):
        if isinstance(node, ast.GuiControlNode):
            handle = self.normalize_id(node.handle)
            parent_handle = "lbh_" + node.handle.split('.')[0][1:].lower()
            caption = self.visit(node.caption)
            handler = self.normalize_id(node.handler) if node.handler else "NULL"
            x = self.visit(node.x)
            y = self.visit(node.y)
            w = self.visit(node.w)
            h = self.visit(node.h)
            self.emit(f"{handle} = lb_create_control(\"{node.type}\", {parent_handle}, {caption}, {x}, {y}, {w}, {h}, {handler});")
            self.emit(f"lb_register_handle(\"{node.handle}\", {handle});")
        elif isinstance(node, ast.LbTabControlNode):
            handle = self.normalize_id(node.handle)
            parent_handle = "lbh_" + node.handle.split('.')[0][1:].lower()
            x = self.visit(node.x)
            y = self.visit(node.y)
            w = self.visit(node.w)
            h = self.visit(node.h)
            self.emit(f"{handle} = lb_create_tabcontrol({parent_handle}, {x}, {y}, {w}, {h});")
            self.emit(f"lb_register_handle(\"{node.handle}\", {handle});")
        elif isinstance(node, ast.LbMenuNode):
            handle = self.normalize_id(node.handle)
            # Menus are attached to window, which starts with lbh_
            win_handle = "lbh_" + node.handle[1:].lower() if node.handle.startswith('#') else node.handle.lower()
            title = self.visit(node.title)
            menu_var = f"m_{win_handle}"
            self.global_vars.add(menu_var)
            self.emit(f"{menu_var} = lb_create_menu({handle}, {title});")
            for cap, handler in node.items:
                h = self.normalize_id(handler) if handler else "NULL"
                self.emit(f"lb_add_menu_item({menu_var}, {self.visit(cap)}, {h});")

    def visit_GuiControlNode(self, node):
        parent_handle_name = node.handle.split('.')[0][1:].lower()
        if parent_handle_name in self.opened_windows:
            self.emit_control_creation(node)
        else:
            self.pending_controls.setdefault(parent_handle_name, []).append(node)

    def visit_LiteralNode(self, node):
        if isinstance(node.value, str):
            escaped = node.value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
            return f'"{escaped}"'
        return str(node.value)

    def visit_VarNode(self, node):
        name = self.normalize_id(node.name)
        if name.startswith('lbh_'):
            return f"lb_get_text((HWND){name})"
        return name

    def visit_BinOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if op == '+':
            left_is_str = self.is_string(node.left)
            right_is_str = self.is_string(node.right)
            if left_is_str or right_is_str:
                if not left_is_str: left = f"lb_str({left})"
                if not right_is_str: right = f"lb_str({right})"
                return f"lb_add_strings({left}, {right})"
            return f"({left} + {right})"
        
        if op == '=':
            if self.is_string(node.left) or self.is_string(node.right):
                return f"(strcmp({left}, {right}) == 0)"
            op = '=='
        elif op == '<>':
            if self.is_string(node.left) or self.is_string(node.right):
                return f"(strcmp({left}, {right}) != 0)"
            op = '!='
        elif op.upper() == 'AND': op = '&&'
        elif op.upper() == 'OR': op = '||'
        elif op.upper() == 'MOD': op = '%'
        return f"({left} {op} {right})"

    def visit_UnaryOpNode(self, node):
        expr = self.visit(node.expr)
        op = node.op
        if op.upper() == 'NOT': op = '!'
        return f"({op}{expr})"

    def visit_LbTabControlNode(self, node):
        parent_handle_name = node.handle.split('.')[0][1:].lower()
        if parent_handle_name in self.opened_windows:
            self.emit_control_creation(node)
        else:
            self.pending_controls.setdefault(parent_handle_name, []).append(node)

    def visit_LbMenuNode(self, node):
        parent_handle_name = node.handle[1:].lower() if node.handle.startswith('#') else node.handle.lower()
        if parent_handle_name in self.opened_windows:
            self.emit_control_creation(node)
        else:
            self.pending_controls.setdefault(parent_handle_name, []).append(node)

    def visit_LbFillNode(self, node):
        handle = self.normalize_id(node.handle)
        db_handle = self.normalize_id(node.db_handle)
        sql = self.visit(node.sql)
        self.emit(f"lb_fill_from_db({handle}, {db_handle}, {sql});")

    def visit_LbLineInputNode(self, node):
        handle = self.normalize_id(node.handle)
        var = self.normalize_id(node.var)
        self.emit(f"lb_line_input({handle}, {var});")

    def visit_LbLocateNode(self, node):
        x = self.visit(node.x)
        y = self.visit(node.y)
        self.emit(f"lb_locate({x}, {y});")

    def visit_ExitStmtNode(self, node):
        if node.type in ('FOR', 'WHILE'):
            self.emit("break;")
        else:
            self.emit("return;")
