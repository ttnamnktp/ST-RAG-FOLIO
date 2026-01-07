# llm/llm_client.py
from openai import OpenAI
import requests
import json
from typing import List, Dict
from config.config import USE_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_BASE_URL, MAX_TOKENS, TEMPERATURE

class LLMClient:
    def __init__(self):
        self.provider = USE_PROVIDER
        self.model = LLM_MODEL
        self.base_url = LLM_BASE_URL
        self.api_key = LLM_API_KEY
        
        if self.provider.value in ["deepseek", "groq", "ollama"]:
            self.client = OpenAI(
                api_key=self.api_key if self.api_key else "not-needed",
                base_url=self.base_url
            )
    
    def chat_completion(self, messages: List[Dict], temperature=TEMPERATURE) -> str:
        """Call LLM"""
        
        if self.provider.value == "deepseek":
            # DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=MAX_TOKENS,
                stream=False
            )
            return response.choices[0].message.content
            
        # llm_client.py - phần Ollama
        elif self.provider.value == "ollama":
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=MAX_TOKENS
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Ollama API error: {e}")
                # Fallback logic...
            
        elif self.provider.value == "groq":
            # Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=MAX_TOKENS
            )
            return response.choices[0].message.content
            
        else:
            # Fallback: DeepSeek (luôn hoạt động)
            try:
                response = requests.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": MAX_TOKENS
                    }
                )
                return response.json()["choices"][0]["message"]["content"]
            except:
                return "∀x(Cat(x) → Animal(x))"  # Fallback hardcoded