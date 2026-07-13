from ddgs import DDGS

def searchImages(query:str,max_results:int=10)->dict:
  try:
    max_results = int(max_results)
  except (ValueError,TypeError) :
    max_results = 10

  with DDGS() as ddg:
    images = ddg.images(query,max_results)
  return images
