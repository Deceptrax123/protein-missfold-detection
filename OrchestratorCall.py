import os
import json
from mistralai import Mistral
from dotenv import load_dotenv
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

client = Mistral(api_key=MISTRAL_API_KEY)

inputs = [
    {"role":"user","content":"Get me information on the following protein: MRTQLAVKDPGSIYFWNLEHCRGTQVAQMLKDYEPNTIRGHWLVSSKADQYFVKETLPRGIMNQW"}
]

response = client.beta.conversations.start(
    agent_id="",
    inputs=inputs)

entries = response.outputs[0]
print(entries)

try:
    parsed = json.loads(entries.content)
    final_dict = parsed["output"]
    print(final_dict)
except:
    print("Using Tool")
    try:
        fname = entries.name
        parsed = json.loads(entries.arguments)
    except Exception as e:
        raise ValueError(f"Call was not made properly {e}")
    
print(parsed)