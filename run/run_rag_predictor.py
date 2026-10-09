from agent.ltrag.rag_predictor import RetrievalPredictor
from run.util import run

if __name__ == "__main__":
    run(predictor=RetrievalPredictor, data_num=204)
