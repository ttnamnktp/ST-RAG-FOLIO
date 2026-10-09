# run_folio_validation.py
from agent.naive_predictor.reasoning_predictor import ReasoningPredictor
from run.util import run

if __name__ == "__main__":
    run(predictor=ReasoningPredictor)
