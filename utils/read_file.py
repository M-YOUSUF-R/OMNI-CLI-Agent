import os
from langchain_core.tools import tool
@tool
def getFileContent(abs_file_path:str)->str:
  """read the file based on absolute file_path parameter
  Args:
    abs_file_path:str -> absolute path of the file
  return:
    content of the file
  """

  abs_path = abs_file_path;

  if not os.path.exists(abs_path):
    return f'Error: Cannot find "{file_path}" inside the permitted working direcotry'

  if not os.path.isfile(abs_path):

    return f'Error: File not found or is not a regular file: "{file_path}"'

  try:
    with open(abs_path,'r') as rf:
      file_content =  rf.read()
    return file_content

  except Exception as e:
    return f"error reading file at: {abs_path} exception: {e}"

