# z3_encoder.py
import z3
from z3_module.ast_fol import (
    Predicate, Not, And, Or, Xor, Implies, BiImplies, ForAll, Exists
)

class Z3Encoder:
    def __init__(self):
        self.U = z3.DeclareSort('U')
        self.consts = {}
        self.preds = {}

    def const(self, name):
        if name not in self.consts:
            self.consts[name] = z3.Const(name, self.U)
        return self.consts[name]

    def pred(self, name, arity):
        if name not in self.preds:
            self.preds[name] = z3.Function(
                name, *([self.U] * arity), z3.BoolSort()
            )
        return self.preds[name]

    def encode(self, f, env=None):
        env = env or {}

        if isinstance(f, Predicate):
            args = [env.get(a, self.const(a)) for a in f.args]
            return self.pred(f.name, len(args))(*args)

        if isinstance(f, Not):
            return z3.Not(self.encode(f.sub, env))

        if isinstance(f, And):
            return z3.And(
                self.encode(f.left, env),
                self.encode(f.right, env)
            )

        if isinstance(f, Or):
            return z3.Or(
                self.encode(f.left, env),
                self.encode(f.right, env)
            )

        if isinstance(f, Xor):
            a = self.encode(f.left, env)
            b = self.encode(f.right, env)
            return z3.And(z3.Or(a, b), z3.Not(z3.And(a, b)))
        
        if isinstance(f, BiImplies):
            return z3.Implies(self.encode(f.left, env), self.encode(f.right, env)) \
                & z3.Implies(self.encode(f.right, env), self.encode(f.left, env))


        if isinstance(f, Implies):
            return z3.Implies(
                self.encode(f.left, env),
                self.encode(f.right, env)
            )

        if isinstance(f, ForAll):
            x = z3.Const(f.var, self.U)
            new_env = dict(env)
            new_env[f.var] = x
            return z3.ForAll([x], self.encode(f.body, new_env))

        if isinstance(f, Exists):
            x = z3.Const(f.var, self.U)
            new_env = dict(env)
            new_env[f.var] = x
            return z3.Exists([x], self.encode(f.body, new_env))

        raise TypeError(f"Unknown AST node: {type(f)}")
