import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Correct imports for modern LangGraph state machine agents
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
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
def create_model():
    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv('OPEN_ROUTE_API_KEY'),
        model="openrouter/free"
    )

def build_agent(model,tools:list,system_prompt:str):
  # Fix 3: Avoided variable shadowing error by referencing global llm_model
  check_pointer = InMemorySaver()

  # Using the standard modern LangGraph react engine
  return create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt, # Replaces system_prompt in newer langgraph versions
    checkpointer=check_pointer
  )
