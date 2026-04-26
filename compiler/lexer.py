import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.line}, {self.column})"

KEYWORDS = {
    'SUB', 'FUNCTION', 'END', 'IF', 'THEN', 'ELSE', 'FOR', 'NEXT', 'TO', 'STEP',
    'WHILE', 'WEND', 'PRINT', 'WAIT', 'NOTICE', 'CONFIRM', 'PROMPT', 'OPEN',
    'FOR', 'WINDOW', 'BUTTON', 'TEXTBOX', 'TEXTEDITOR', 'STATICTEXT', 'LISTBOX', 'COMBOBOX',
    'CHECKBOX', 'RADIOBUTTON', 'GROUPBOX', 'LISTVIEW', 'DATEPICKER', 'PSTRINGGRID',
    'CLOSE', 'AS', 'AND', 'OR', 'NOT', 'SQLITE', 'MYSQL', 'EXIT', 'FILL', 'MENU', 'TABCONTROL',
    'INPUT', 'OUTPUT', 'APPEND', 'LINE', 'GRAPHICBOX', 'LOCATE', 'MOD', 'DIM', 'CALL'
}

TOKEN_TYPES = [
    ('NUMBER', r'\d+(\.\d+)?'),
    ('STRING', r'"(""|[^"])*"'),
    ('COMMENT', r"'[^\n]*"),
    ('HANDLE', r'#[a-zA-Z0-9.]+'),
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_$!%&#]*'),
    ('OP', r'<>|<=|>=|[+\-*/=<>]'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('COMMA', r','),
    ('SEMICOLON', r';'),
    ('COLON', r':'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.'),
]

def tokenize(code):
    tokens = []
    line_num = 1
    line_start = 0
    
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_TYPES)
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'COMMENT':
            continue
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'ID':
            upper_val = value.upper()
            if upper_val in KEYWORDS:
                kind = upper_val
        elif kind == 'STRING':
            value = value[1:-1].replace('""', '"')
        elif kind == 'NEWLINE':
            tokens.append(Token(kind, value, line_num, column))
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        tokens.append(Token(kind, value, line_num, column))
    return tokens
