import z3
from typing import Tuple, Optional, List

class Z3Solver:
    def __init__(self):
        self.solver = z3.Solver()
    
    def solve(self, logic_code: str) -> Tuple[bool, Optional[str], Optional[List[str]]]:
        """
        Returns: (is_executable, error_message, solutions)
        """
        try:
            # This is a simplified version — in reality, you'd parse the logic string
            # and convert to Z3 expressions. Here we assume logic_code is Python-executable.
            exec_globals = {}
            exec(logic_code, {"z3": z3}, exec_globals)
            
            # Check if solver is satisfiable
            if self.solver.check() == z3.sat:
                model = self.solver.model()
                solutions = [str(model)]
                return True, None, solutions
            else:
                return True, "Unsatisfiable", []
        
        except Exception as e:
            return False, str(e), None
    
    def reset(self):
        self.solver = z3.Solver()
        
        