# fol_parser.py
from z3_module.ast_fol import *
from z3_module.fol_lexer import tokenize
import json

class Parser:
    def __init__(self, text, idx):
        self.text=text
        self.idx=idx # index in premises
        self.tokens = list(tokenize(text))
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    # def eat(self, kind):
    #     tok = self.peek()
    #     assert tok and tok[0] == kind, f"Expected {kind}, got {tok}"
    #     self.pos += 1
    #     return tok[1]
    def format_error_context(self, text, line, col, msg):
        lines = text.splitlines()
        if line - 1 >= len(lines):
            return msg

        error_line = lines[line - 1]
        pointer = " " * (col - 1) + "^"

        return {
            "index" : self.idx,
            "error_msg" : msg,
            "error_line" : error_line,
            "pointer" : pointer
            # f"{pointer}"
        }

    def eat(self, kind):
        tok = self.peek()

        if tok is None:
            # dùng token trước đó để suy ra vị trí
            if self.pos > 0:
                _, _, line, col = self.tokens[self.pos - 1]
            else:
                line, col = 1, 1

            msg = f"Unexpected end of input, expected {kind}"
            raise Exception(json.dumps(self.format_error_context(self.text, line, col, msg)))

        tok_type, tok_val, line, col = tok

        if tok_type != kind:
            msg = (
                f"Syntax error at line {line}, column {col}\n"
                f"Expected {kind}, got {tok_type} ({tok_val})"
            )
            raise Exception(json.dumps(self.format_error_context(self.text, line, col, msg)))

        self.pos += 1
        return tok_val

    def parse(self):
        return self.parse_biimpl()
    
    def parse_biimpl(self):
        left = self.parse_implication()
        while self.peek() and self.peek()[0] == 'BIMPLIES':
            self.eat('BIMPLIES')
            right = self.parse_implication()
            left = BiImplies(left, right)
        return left

    def parse_implication(self):
        left = self.parse_xor()
        if self.peek() and self.peek()[0] == 'IMPLIES':
            self.eat('IMPLIES')
            right = self.parse_implication()
            return Implies(left, right)
        return left

    def parse_xor(self):
        left = self.parse_or()
        if self.peek() and self.peek()[0] == 'XOR':
            self.eat('XOR')
            right = self.parse_xor()
            return Xor(left, right)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.peek() and self.peek()[0] == 'OR':
            self.eat('OR')
            right = self.parse_and()
            left = Or(left, right)
        return left

    def parse_and(self):
        left = self.parse_unary()
        while self.peek() and self.peek()[0] == 'AND':
            self.eat('AND')
            right = self.parse_unary()
            left = And(left, right)
        return left

    def parse_unary(self):
        tok = self.peek()
        if tok[0] == 'NOT':
            self.eat('NOT')
            return Not(self.parse_unary())
        
        if tok[0] == 'FORALL':
            self.eat('FORALL')
            var = self.eat('ID')
            return ForAll(var, self.parse_unary())

        if tok[0] == 'EXISTS':
            self.eat('EXISTS')
            var = self.eat('ID')
            return Exists(var, self.parse_unary())
            
        return self.parse_atom()

    def parse_atom(self):
        if self.peek()[0] == 'LPAREN':
            self.eat('LPAREN')
            f = self.parse()
            self.eat('RPAREN')
            return f
        name = self.eat('ID')
        self.eat('LPAREN')
        args = [self.eat('ID')]
        while self.peek()[0] == 'COMMA':
            self.eat('COMMA')
            args.append(self.eat('ID'))
        self.eat('RPAREN')
        return Predicate(name, args)
