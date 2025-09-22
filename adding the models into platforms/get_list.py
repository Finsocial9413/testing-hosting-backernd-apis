import openai
import requests
import json
from typing import List, Dict

def list_openai_models_with_openai_client(api_key: str) -> List[Dict]:
    """
    Get all available OpenAI models using the official OpenAI Python client.
    
    Args:
        api_key (str): Your OpenAI API key
        
    Returns:
        List[Dict]: List of available models with their details
    """
    try:
        # Initialize the OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # List all models
        models = client.models.list()
        
        # Convert to list of dictionaries for easier handling
        model_list = []
        for model in models.data:
            model_dict = {
                'id': model.id,
                'object': model.object,
                'created': model.created,
                'owned_by': model.owned_by
            }
            model_list.append(model_dict)
        
        return model_list
        
    except Exception as e:
        print(f"Error using OpenAI client: {e}")
        return []

def display_models(models: List[Dict], filter_gpt_only: bool = False):
    """
    Display the models in a formatted way.
    
    Args:
        models (List[Dict]): List of model dictionaries
        filter_gpt_only (bool): If True, only show GPT models
    """
    if not models:
        print("No models found or error occurred.")
        return
    
    # Filter for GPT models if requested
    if filter_gpt_only:
        models = [model for model in models if 'gpt' in model['id'].lower()]
    
    # Sort models by name
    models = sorted(models, key=lambda x: x['id'])
    
    print(f"\nFound {len(models)} models:")
    print("-" * 80)
    print(f"{'Model ID':<40} {'Owner':<20} {'Created':<15}")
    print("-" * 80)
    
    for model in models:
        created_date = ""
        if model.get('created'):
            import datetime
            created_date = datetime.datetime.fromtimestamp(model['created']).strftime('%Y-%m-%d')
        
        print(f"{model['id']:<40} {model.get('owned_by', 'N/A'):<20} {created_date:<15}")

def main():
    """
    Main function to run the script.
    """
    # Replace with your actual OpenAI API key
    API_KEY = "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"
    
    if API_KEY == "your-openai-api-key-here":
        print("Please replace 'your-openai-api-key-here' with your actual OpenAI API key.")
        return

    
    # Method 1: Using OpenAI Python client (recommended)
    print("\n=== Using OpenAI Python Client ===")
    models_client = list_openai_models_with_openai_client(API_KEY)
    display_models(models_client)

    
    
    # Save to JSON file
    if models_client:
        with open('models_list/openai_models.json', 'w') as f:
            json.dump(models_client, f, indent=2)
        print(f"\nModels saved to 'openai_models.json'")

if __name__ == "__main__":
    main()