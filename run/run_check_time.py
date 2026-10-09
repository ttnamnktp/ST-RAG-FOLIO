import time
from agent.ltrag.fixer_predictor import FixerPredictor
from agent.naive_predictor.naive_predictor import NaivePredictor
from agent.ltrag.translate_story_predictor import TranslateStoryPredictor
from agent.ltrag.translate_story_fix_predictor import TranslateStoryFixPredictor

from run.util import run

if __name__ == "__main__":
    data_num=5
    
    ## TRANSLATION
    print("="*80)
    print("CONFIC 2.5:3B")
    print("="*80)
    
    # naive 
    start = time.perf_counter()
    run(predictor=NaivePredictor, data_num=data_num)
    end = time.perf_counter()
    print(f"Naive Predictor: {(end - start)/data_num:.6f} seconds")
    
    # ST-RAG without Fixer
    start = time.perf_counter()
    run(predictor=TranslateStoryPredictor, data_num=data_num)
    end = time.perf_counter()
    print(f"RAG Predictor: {(end - start)/data_num:.6f} seconds")

    # ST-NoRAG
    start = time.perf_counter()
    run(predictor=FixerPredictor, data_num=data_num)
    end = time.perf_counter()
    print(f"Fixer Predictor: {(end - start)/data_num:.6f} seconds")
    
    # ST-RAG
    start = time.perf_counter()
    run(predictor=TranslateStoryFixPredictor, data_num=data_num)
    end = time.perf_counter()
    print(f"Fixer Predictor: {(end - start)/data_num:.6f} seconds")
    
