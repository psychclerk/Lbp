
class Node:
    pass

class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements

class SubNode(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class FunctionNode(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class IfNode(Node):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class ForNode(Node):
    def __init__(self, var, start, end, step, body):
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body

class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class CallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class CallStmtNode(Node):
    def __init__(self, call_node):
        self.call_node = call_node

class AssignNode(Node):
    def __init__(self, target, value):
        self.target = target
        self.value = value

class PrintNode(Node):
    def __init__(self, handle, content):
        self.handle = handle
        self.content = content

class LbWaitNode(Node):
    pass

class LbNoticeNode(Node):
    def __init__(self, message):
        self.message = message

class LbConfirmNode(Node):
    def __init__(self, message, var):
        self.message = message
        self.var = var

class LbPromptNode(Node):
    def __init__(self, message, var):
        self.message = message
        self.var = var

class LbFillNode(Node):
    def __init__(self, handle, db_handle, sql):
        self.handle = handle
        self.db_handle = db_handle
        self.sql = sql

class LbLineInputNode(Node):
    def __init__(self, handle, var):
        self.handle = handle
        self.var = var

class LbDimNode(Node):
    def __init__(self, name, size):
        self.name = name
        self.size = size

class ArrayAccessNode(Node):
    def __init__(self, name, index):
        self.name = name
        self.index = index

class LbEofNode(Node):
    def __init__(self, handle):
        self.handle = handle

class OpenWindowNode(Node):
    def __init__(self, handle, title, type):
        self.handle = handle
        self.title = title
        self.type = type

class CloseNode(Node):
    def __init__(self, handle):
        self.handle = handle

class ExitStmtNode(Node):
    def __init__(self, type):
        self.type = type

class GuiControlNode(Node):
    def __init__(self, type, handle, caption, handler, x, y, w, h):
        self.type = type
        self.handle = handle
        self.caption = caption
        self.handler = handler
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class LbMenuNode(Node):
    def __init__(self, handle, title, items):
        self.handle = handle
        self.title = title
        self.items = items # list of (caption, handler)

class LbTabControlNode(Node):
    def __init__(self, handle, x, y, w, h):
        self.handle = handle
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class LbLocateNode(Node):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class LiteralNode(Node):
    def __init__(self, value):
        self.value = value

class VarNode(Node):
    def __init__(self, name):
        self.name = name

class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOpNode(Node):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
