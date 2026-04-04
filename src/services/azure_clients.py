from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
endpoint = os.getenv('endpoint')
model_name = os.getenv('model_name')
deployment = os.getenv('deployment')
subscription_key = os.getenv('subscription_key')
api_version = os.getenv('api_version')


async def getResponseModelClient():

    try:
        llm = AzureChatOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=subscription_key,
            azure_deployment=deployment,
            temperature=0.7,
        )
        return llm
    except Exception as e:
        return None

