from ddgs import DDGS
from langchain_core.tools import tool  

@tool
def generalSearch(query:str,max_results=10)->dict:
  """Helps searching content on online.
  Args:
    query:str -> query to search
    max_results:int -> number of result of search to get (default=10)
  output:
    reutrn a dictorany of all those search in this format:
    id: {
      title: title of the search_result page
      url: the link of a page
      body: short discription on that page
    }
  """
  try:
    max_results = int(max_results)
  except (ValueError, TypeError):
    max_results = 10

  with DDGS() as ddg:
    results = ddg.text(query,max_results=max_results)
    
  return results

