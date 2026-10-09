# run_folio_validation.py
from data.data_loader import JsonlDatasetLoader
from agent.naive_predictor.naive_predictor import NaivePredictor
from llm.llm_client import LLMClient
from run.util import run

if __name__ == "__main__":
    run()
