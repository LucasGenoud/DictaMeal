import requests
import json
import time

def test_structure_recipe(use_search=False):
    url = "http://localhost:8000/structure"
    # A dish name that definitely needs search to get ingredients
    payload = {"text": "Make me a traditional Carbonara", "use_search": use_search}
    
    print(f"\n--- Testing with use_search={use_search} ---")
    print(f"Sending request to {url} with payload: {payload}")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Response received in {time.time() - start_time:.2f}s")
        # print(json.dumps(data, indent=2))
        
        # Verification checks
        if data.get("ingredients") and len(data["ingredients"]) > 0:
             print(f"Ingredients found: {len(data['ingredients'])}")
             if use_search:
                 print("✅ PASS: Ingredients found with search.")
             else:
                 # Without search, it might halllucinate or return nothing, but we expect it to NOT look online.
                 # The key difference is we want to see it worked.
                 print("Ingredients found (Ollama hallucinated/knew it).")
        else:
            if not use_search:
                print("✅ PASS: No ingredients found (expected for empty context without search, or maybe basic knowledge).")
            else:
                print("❌ FAIL: No ingredients found even with search.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response:
             print(f"Response content: {e.response.text}")

if __name__ == "__main__":
    # 1. Test WITHOUT search (should be fast, might have hallucinated ingredients or be empty/generic)
    test_structure_recipe(use_search=False)
    
    # 2. Test WITH search (should take longer but have better data)
    test_structure_recipe(use_search=True)
