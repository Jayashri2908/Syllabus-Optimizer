import os
import sys
import json
import logging
import time

# Setup path to include src
sys.path.append(os.getcwd())

from src.ai.openrouter_model import OpenRouterModel

def test_all_free_models():
    # Read model list from file
    if not os.path.exists("free_models.json"):
        print("Error: free_models.json not found. Run get_openrouter_list.py first.")
        return
        
    with open("free_models.json", "r") as f:
        models_to_test = json.load(f)
    
    print(f"--- Testing {len(models_to_test)} OpenRouter Free Models ---")
    
    results = []
    
    for i, model_name in enumerate(models_to_test):
        print(f"[{i+1}/{len(models_to_test)}] Testing: {model_name}...", end=" ", flush=True)
        try:
            model = OpenRouterModel(config={"model": model_name})
            # Simple ping
            response = model.generate(prompt="hi", max_tokens=5)
            print(f"SUCCESS")
            results.append({"model": model_name, "status": "SUCCESS", "response": response.strip()})
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"FAILED (429 Rate Limit)")
                results.append({"model": model_name, "status": "FAILED", "reason": "Rate Limit (429)"})
            elif "404" in error_msg:
                print(f"FAILED (404 Not Found)")
                results.append({"model": model_name, "status": "FAILED", "reason": "Not Found (404)"})
            else:
                print(f"FAILED ({error_msg[:50]}...)")
                results.append({"model": model_name, "status": "FAILED", "reason": error_msg[:100]})
        
        # Tiny delay to be slightly nicer to the API, though we're already rate limited
        time.sleep(0.5)

    # Save summary
    with open("detailed_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    successes = [r for r in results if r['status'] == 'SUCCESS']
    print(f"\n--- Summary ---")
    print(f"Total Tested: {len(models_to_test)}")
    print(f"Successes: {len(successes)}")
    if successes:
        print("Working Models:")
        for s in successes:
            print(f" - {s['model']}")

if __name__ == "__main__":
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        # Try to load from .env if available
        try:
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("OPENROUTER_API_KEY="):
                        api_key = line.split("=")[1].strip()
                        os.environ["OPENROUTER_API_KEY"] = api_key
                        break
        except:
            pass
            
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable not set.")
    else:
        test_all_free_models()
