import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()



@tool
def current_time() -> str:
    """Return the current local date and time.
    Use this when the user asks what time or date it is.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def word_count(text: str) -> int:
    """Count the number of words in a piece of text.
    Use this when the user asks how long a piece of writing is,
    or asks you to count the words in something they've shared.
    Returns the word count as an integer.
    """
    return len(text.split())
def createOpenRouteModel():
    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv('OPEN_ROUTE_API_KEY'),
        model="openrouter/free",
        max_retries=3,
        timeout=10.0 
    )
def createOllamaMode():
    return ChatOllama(
        model='llama3.1:latest',
    )

def build_agent(model,tools:list,system_prompt:str):

  check_pointer = InMemorySaver()

  # Using the standard modern LangGraph react engine
  return create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=check_pointer
  )
