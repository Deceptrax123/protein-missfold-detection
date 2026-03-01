import os
import json
from mistralai import Mistral

client = Mistral(api_key="JatrHVB1dyMjeBy29pZZf8XEQzsGVzKG")

inputs = [
    {"role":"user","content":"Get me information on the following protein: MRTQLAVKDPGSIYFWNLEHCRGTQVAQMLKDYEPNTIRGHWLVSSKADQYFVKETLPRGIMNQW"}
]

response = client.beta.conversations.start(
    agent_id="ag_019ca82c89e17476ad204bb0b414dbb0",
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