# ast_fol.py
from dataclasses import dataclass
from typing import List

class Formula:
    pass

@dataclass
class Predicate(Formula):
    name: str
    args: List[str]

@dataclass
class Not(Formula):
    sub: Formula

@dataclass
class And(Formula):
    left: Formula
    right: Formula

@dataclass
class Or(Formula):
    left: Formula
    right: Formula

@dataclass
class Xor(Formula):
    left: Formula
    right: Formula

@dataclass
class Implies(Formula):
    left: Formula
    right: Formula

@dataclass
class ForAll(Formula):
    var: str
    body: Formula

@dataclass
class Exists(Formula):
    var: str
    body: Formula
    
@dataclass
class BiImplies(Formula): 
    left: Formula
    right: Formula

