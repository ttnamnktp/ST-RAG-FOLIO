from agent.ltrag.translate_story_predictor import TranslateStoryPredictor
from run.util import run

if __name__ == "__main__":
    run(predictor=TranslateStoryPredictor, data_num=204)
