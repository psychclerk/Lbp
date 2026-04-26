import math

# Math functions
def abs(x): return math.fabs(x)
def acos(x): return math.acos(x)
def asin(x): return math.asin(x)
def atan(x): return math.atan(x)
def cos(x): return math.cos(x)
def exp(x): return math.exp(x)
def floor(x): return math.floor(x)
def int_val(x): return int(math.floor(x)) # LB uses INT(x) for floor
def log(x): return math.log(x)
def sin(x): return math.sin(x)
def sqrt(x): return math.sqrt(x)
def tan(x): return math.tan(x)
pi = math.pi

# String functions (1-based indexing)
def left_str(s, n):
    s = str(s)
    return s[:int(n)]

def mid_str(s, start, length=None):
    s = str(s)
    start = int(start) - 1
    if length is None:
        return s[start:]
    return s[start:start+int(length)]

def right_str(s, n):
    s = str(s)
    n = int(n)
    if n <= 0: return ""
    return s[-n:]

def upper_str(s): return str(s).upper()
def lower_str(s): return str(s).lower()
def len_str(s): return len(str(s))

def instr(s, target, start=1):
    s = str(s)
    target = str(target)
    start = int(start) - 1
    try:
        return s.find(target, start) + 1
    except:
        return 0

def val(s):
    try:
        return float(str(s))
    except:
        return 0

def str_str(n): return str(n)
def space_str(n): return " " * int(n)
def string_str(n, char): return str(char) * int(n)
def ltrim_str(s): return str(s).lstrip()
def rtrim_str(s): return str(s).rstrip()
def trim_str(s): return str(s).strip()

def chr_str(n): return chr(int(n))
def asc(s): return ord(s[0]) if s else 0

class PFile:
    def __init__(self, path, mode):
        self.path = path
        self.mode = 'r' if mode == 'input' else 'w' if mode == 'output' else 'a'
        self.file = open(path, self.mode)

    def command(self, content):
        self.file.write(str(content) + '\n')

    def readline(self):
        return self.file.readline().rstrip('\n\r')

    def close(self):
        self.file.close()

    def eof(self):
        pos = self.file.tell()
        char = self.file.read(1)
        self.file.seek(pos)
        return 1 if not char else 0

def eof(handle):
    if hasattr(handle, 'eof'):
        return handle.eof()
    return 1

# Global state for window management
WindowWidth = 800
WindowHeight = 600
UpperLeftX = 100
UpperLeftY = 100
DisplayWidth = 1024
DisplayHeight = 768
MouseX = 0
MouseY = 0

def DB_POPULATE_STRINGGRID(grid, data, headers=None):
    grid.set_grid_data(data, headers)

