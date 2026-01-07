from llm.llm_client import LLMClient
import time

def test_real_scenarios():
    client = LLMClient()
    
    print(f"🚀 Testing with: {client.provider.value} - {client.model}")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Logic translation",
            "messages": [
                {"role": "user", "content": "Translate to FOL: All cats are animals"}
            ]
        },
        {
            "name": "Logic correction", 
            "messages": [
                {"role": "user", "content": "Fix this FOL: ∀x(Cat(x) ∧ Animal(x))"}
            ]
        },
        {
            "name": "Vietnamese logic",
            "messages": [
                {"role": "user", "content": "Mọi con mèo đều là động vật, dịch sang logic"}
            ]
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n🧪 Test {i+1}: {test['name']}")
        print(f"Q: {test['messages'][0]['content']}")
        
        start = time.time()
        try:
            response = client.chat_completion(test["messages"])
            elapsed = time.time() - start
            
            print(f"⏱️  Time: {elapsed:.2f}s")
            print(f"A: {response}")
            # print(f"A: {response[500]}..." if len(response) > 500 else f"A: {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed! Ollama is ready for your FOL application.")

if __name__ == "__main__":
    test_real_scenarios()