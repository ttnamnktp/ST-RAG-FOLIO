from agent.ltrag.translate_rag_predictor import TranslateRagPredictor
from run.util import run

if __name__ == "__main__":
    run(predictor=TranslateRagPredictor, data_num=204)
