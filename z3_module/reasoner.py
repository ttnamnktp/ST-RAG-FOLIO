# reasoner.py
import z3
from z3_module.fol_parser import Parser
from z3_module.z3_encoder import Z3Encoder

def check_entailment(premises, conclusion):
    enc = Z3Encoder()

    prem_z3 = []
    for idx, p in enumerate(premises):
        ast = Parser(p, idx).parse()
        z3f = enc.encode(ast)
        assert isinstance(z3f, z3.BoolRef), type(z3f)
        prem_z3.append(z3f)

    concl_ast = Parser(conclusion,-1).parse()
    concl_z3 = enc.encode(concl_ast)
    assert isinstance(concl_z3, z3.BoolRef), type(concl_z3)

    s = z3.Solver()

    # Premises ⊨ Conclusion ?
    s.push()
    for f in prem_z3:
        s.add(f)
    s.add(z3.Not(concl_z3))
    sat_neg = (s.check() == z3.sat)
    s.pop()

    # Premises ⊨ ¬Conclusion ?
    s.push()
    for f in prem_z3:
        s.add(f)
    s.add(concl_z3)
    sat_pos = (s.check() == z3.sat)
    s.pop()

    if not sat_neg:
        return "True"
    if not sat_pos:
        return "False"
    return "Uncertain"
