# fol_lexer.py
import re

TOKEN_SPEC = [
    ('FORALL', r'∀'),
    ('EXISTS', r'∃'),
    ('IMPLIES', r'→'),
    ('BIMPLIES', r'↔'),
    ('AND', r'∧'),
    ('OR', r'∨'),
    ('XOR', r'⊕'),
    ('NOT', r'¬'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('COMMA', r','),
    # ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('ID', r'[^\W\d_][\w\d_\.’]*'),
    ('SKIP', r'\s+'),
]

token_regex = '|'.join(f'(?P<{n}>{r})' for n, r in TOKEN_SPEC)

# def tokenize(text):
#     for m in re.finditer(token_regex, text):
#         kind = m.lastgroup
#         value = m.group()
#         if kind != 'SKIP':
#             yield (kind, value)

def tokenize(text):
    line = 1
    line_start = 0  # index bắt đầu dòng hiện tại

    for m in re.finditer(token_regex, text):
        kind = m.lastgroup
        value = m.group()
        start = m.start()

        if kind == 'SKIP':
            # cập nhật line nếu skip có newline
            newlines = value.count('\n')
            if newlines > 0:
                line += newlines
                line_start = start + value.rfind('\n') + 1
            continue

        col = start - line_start + 1
        yield (kind, value, line, col)
