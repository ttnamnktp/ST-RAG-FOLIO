from agent.ltrag.fixer.rag_fixer import RagFixer
# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    fixer = RagFixer("data/fixer-kb.json")
    
    entry = {
        "error_msg": "Syntax error at line 1, column 77\nExpected LPAREN, got ID (P2)",
        "error_line": "∀x ∀y (LaLigaTeam(x) ∧ LaLigaTeam(y) ∧ Points(x, P1) ∧ Points(y, P2) ∧ P1 > P2 → RankHigherThan(x, y))"
    }
    
    fixed_fol = fixer.fix(fol_error=entry["error_line"], error_msg=entry["error_msg"], premise="")
    print("Fixed FOL:", fixed_fol)