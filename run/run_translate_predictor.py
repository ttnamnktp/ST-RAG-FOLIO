from agent.ltrag.translate_predictor import TranslatePredictor
from run.util import run

if __name__ == "__main__":
    run(predictor=TranslatePredictor, data_num=204)
