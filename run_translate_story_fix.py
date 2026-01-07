from agent.ltrag.translate_story_fix_predictor import TranslateStoryFixPredictor
from run.util import run

if __name__ == "__main__":
    run(predictor=TranslateStoryFixPredictor, data_num=204)
