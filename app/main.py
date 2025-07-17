import openai
import config
import os
Settings = config.Settings()
Settings.openai_api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API Key set successfully.", Settings.openai_api_key)

client = openai.Client(
    api_key=Settings.openai_api_key
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a Trading Assistant, who converts natural language into the function calls. From these set of functions "},
        {"role": "user", "content": "What is the current price of Bitcoin?"}
    ]
)

print("Response from OpenAI:", response.choices[0].message['content'])