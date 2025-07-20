# import openai
import config
import os
import services.hyperliquid
Settings = config.Settings()
Settings.openai_api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API Key set successfully.", Settings.openai_api_key)

# client = openai.Client(
#     api_key=Settings.openai_api_key
# )

#Testing if the Commits are made by CodeMongerr or not

# response = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a Trading Assistant, who converts natural language into the function calls. From these set of functions "},
#         {"role": "user", "content": "What is the current price of Bitcoin?"}
#     ]
# )

# Example usage of HyperliquidClient
# client = services.hyperliquid.HyperliquidClient(
#     wallet_address="0x8b3846CcfeCE6D84CcD0f1d1c0Ce73421B300DdC",
#     private_key="0x76798a7330a5f2989c67783e385bb780f894f854537242ed96f7382c7497c3d8",
# )
# client.get_market_price(
#     symbol="BTC/USDC:USDC",
# )



# print("Response from OpenAI:", response.choices[0].message['content'])