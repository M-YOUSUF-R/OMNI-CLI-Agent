import trafilatura as tf
from langchain_core.tools import tool

@tool
def extractTextFromPage(url:str):
  """This extract Text from a webpage link
  Args:
    url:str -> the link of that page
  return:
    text:str -> extracted texts
  """

  fetch_url = tf.fetch_url(url)
  text = tf.extract(fetch_url)
  return text
