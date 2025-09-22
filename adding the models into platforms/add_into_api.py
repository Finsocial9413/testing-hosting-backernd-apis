import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

# Adjust if your actual route differs (check http://127.0.0.1:8000/docs)
ENDPOINT = "/add_platform_model/add_platform_model"   # instead of /add_platform_model/add_platform_model/

import pandas as pd
df = pd.read_json('models_list/openai_models.json')

for i in range(len(df)):
    model_name = df.iloc[i][0]
    payload = {
        "platform_name": "OpenAIChat",      # <-- set the target platform
        "model_name": str(model_name)              # <-- model identifier
    }
    try:
        r = requests.post(BASE_URL + ENDPOINT, json=payload, timeout=20)
        r.raise_for_status()
        print("Success:", r.json())
    except requests.HTTPError:
        print("HTTP error:", r.status_code, r.text)
        sys.exit(1)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

