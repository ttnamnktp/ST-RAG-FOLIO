from z3_solver import Z3Solver

def run_test(name, logic_code):
    print(f"\n🧪 {name}")
    print("-" * 40)

    solver = Z3Solver()
    ok, error, solutions = solver.solve(logic_code)

    print(f"Executable : {ok}")
    print(f"Error      : {error}")
    print(f"Solutions  : {solutions}")

if __name__ == "__main__":

    # 1️⃣ SAT case
    run_test(
        "SAT example",
        """
x = z3.Int('x')
solver.add(x > 0)
solver.add(x < 5)
"""
    )

    # 2️⃣ UNSAT case
    run_test(
        "UNSAT example",
        """
x = z3.Int('x')
solver.add(x > 0)
solver.add(x < 0)
"""
    )

    # 3️⃣ Syntax / runtime error
    run_test(
        "Invalid logic",
        """
x = z3.Int('x'
solver.add(x > 0)
"""
    )

    # 4️⃣ Empty logic
    run_test(
        "Empty logic",
        ""
    )
