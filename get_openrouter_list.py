import requests
import json
import os

def get_free_models():
    url = "https://openrouter.ai/api/v1/models"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch models: {response.status_code}")
            return []
        
        models = response.json().get('data', [])
        free_models = []
        for m in models:
            pricing = m.get('pricing', {})
            try:
                prompt_price = float(pricing.get('prompt', 0))
                completion_price = float(pricing.get('completion', 0))
                # Some models might have free price but aren't strictly "free" in terms of rate limits
                # but we'll include anything with 0 cost.
                if prompt_price == 0 and completion_price == 0:
                    free_models.append(m.get('id'))
            except (ValueError, TypeError):
                continue
        
        # Sort and remove duplicates
        free_models = sorted(list(set(free_models)))
        return free_models
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

if __name__ == "__main__":
    free_list = get_free_models()
    with open("free_models.json", "w") as f:
        json.dump(free_list, f, indent=2)
    print(f"Found {len(free_list)} free models. List saved to free_models.json")
