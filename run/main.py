# main.py
import sys
import os
import time

sys.path.append('.')

from translation.translator import TranslatorLLM
from fixer.fixer import FixerLLM
from solver.z3_solver import Z3Solver
from retrieval.retriever import Retriever
from config.config import TRANSLATION_KB_PATH, FIXER_KB_PATH

def print_header(msg):
    print("\n" + "="*10 + f" {msg} " + "="*10)

def main():
    print_header("LTRAG Free Version")
    
    start_total = time.time()
    
    print_header("Init Components")
    start = time.time()
    # 1. Khởi tạo components
    trans_retriever = Retriever(TRANSLATION_KB_PATH)
    fixer_retriever = Retriever(FIXER_KB_PATH)
    translator = TranslatorLLM()
    fixer = FixerLLM()
    solver = Z3Solver()
    end = time.time()
    print(f"✅ Components initialized in {end - start:.3f}s")
    
    # 2. Bài toán mẫu
    problem = """
All cats are animals.
Tom is a cat.
Therefore, Tom is an animal.
"""
    print_header("Problem")
    print(problem.strip())
    
    # 3. Retrieve translation examples
    print_header("Retrieve Translation Examples")
    start = time.time()
    trans_examples = trans_retriever.retrieve(problem, top_k=2)
    end = time.time()
    print(f"✅ Retrieved {len(trans_examples)} examples in {end - start:.3f}s")
    for i, ex in enumerate(trans_examples, 1):
        print(f"  Example {i}: {ex}")
    
    # 4. Translate
    print_header("Translate to Logic")
    start = time.time()
    logic = translator.formalize(problem, trans_examples)
    end = time.time()
    print(f"✅ Translation done in {end - start:.3f}s")
    print(f"Translated logic:\n{logic}")
    
    # 5. Solve
    print_header("Solve Logic")
    print("Logic:\n"+logic)
    start = time.time()
    is_valid, error, solutions = solver.solve(logic)
    end = time.time()
    
    if is_valid and not error:
        print(f"✅ Solution found in {end - start:.3f}s")
        if solutions:
            print("Solution(s):")
            for sol in solutions:
                print(" ", sol)
    else:
        print(f"❌ Error in solving ({end - start:.3f}s): {error}")
        # Try to fix
        print_header("Fix Logic")
        start = time.time()
        fix_examples = fixer_retriever.retrieve(error, top_k=1)
        fixed_logic = fixer.fix(problem, logic, error, fix_examples)
        end = time.time()
        print(f"✅ Fixed logic in {end - start:.3f}s")
        print(f"Fixed logic:\n{fixed_logic}")
    
    total_time = time.time() - start_total
    print_header(f"Total Execution Time: {total_time:.3f}s")

if __name__ == "__main__":
    main()
