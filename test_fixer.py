from agent.ltrag.fixer.fixer import FixerLLM
import json

folio_sample = {"premises": 
    ["Monkeypox is an infectious disease caused by the monkeypox virus.", 
     "Monkeypox virus can occur in certain animals, including humans.", 
     "Humans are mammals.", "Mammals are animals.", 
     "Symptons of Monkeypox include fever, headache, muscle pains, feeling tired, and so on.", 
     "People feel tired when they get a glu."], 
    
    "premises-FOL": ["\u2203x (OccurMonkeypoxVirus(x) \u2227 GetMonkeypox(x))", "\u2203x (Animal(x) \u2227 OccurMonkeypoxVirus(x))", "\u2200x (Human(x) \u2192 Mammal(x))", "\u2200x (Mammal(x) \u2192 Animal(x))", "\u2203x (GetMonkeypox(x) \u2227 (Fever(x) \u2228 Headache(x) \u2228 MusclePain(x) \u2228 Tired(x)))", "\u2200x (Human(x) \u2227 Flu(x) \u2192 Tired(x))"], "conclusion": "There is an animal.", "conclusion-FOL": "\u2203x (Animal(x))", "label": "True"}

broken_fol_sample = {
    'premises-FOL': 
        ['∀x (Monkeypox(x) → InfectiousDisease(x))', 
         '∃virus MonkeypoxVirus(virus)', 
         '∀animal (IsAnimal(animal) → (∃human Human(human) ∧ human = animal))', 
         '∀mammal (Mammal(mammal) → IsAnimal(mammal))', 
         '∀symptom (Symptoms(Monkeypox(x), symptom))', 
         '∀person (Glu(person) → Tired(person))'], 
        
    'conclusion-FOL': '∃animal IsAnimal(animal)'
    }

def test_fixer_llm():
    fixer = FixerLLM()

    # print("========== ORIGINAL FOL ==========")
    # print(json.dumps(broken_fol_sample, indent=2, ensure_ascii=False))

    fixed = fixer.fix(
        original_sample="Humans are mammals.",
        fol_sample="∀animal (IsAnimal(animal) → (∃human Human(human) ∧ human = animal))",
        error_msg="""
        Invalid character =
        ∀animal (IsAnimal(animal) → (∃human Human(human) ∧ human = animal))
        """
    )



if __name__ == "__main__":
    test_fixer_llm()
