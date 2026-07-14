import os
import asyncio
import markdown
os.add_dll_directory(r"C:\MyProjects\Open-Agents\GTK3-Runtime Win64\bin")
from weasyprint import HTML
from tkinter import filedialog
from langchain_core.tools import tool

# Helper function to run the Tkinter dialog safely in a separate thread
def _ask_directory():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw() # Hide the main tiny Tkinter window
    root.attributes('-topmost', True) # Bring the dialog to the front
    directory = filedialog.askdirectory(title='Select a Folder')
    root.destroy()
    return directory

@tool
def writeMDFile(file_name: str, content: str):
    """Write content to a file inside a user-selected directory.
    Use this tool when you need to save files, code, or documents to the disk.
    
    Args:
        file_name:str -> The name of the file (including extension, e.g., 'script.py').
        content:str -> The complete, raw text content to write inside the file.
    return:
      absolute_path of the markdown file. 
    """
    try:
        loop = asyncio.get_running_loop()
        working_dir = loop.run_in_executor(None, _ask_directory)
        working_dir = asyncio.run_coroutine_threadsafe(
            asyncio.to_thread(_ask_directory), loop
        ).result()
    except RuntimeError:
        working_dir = _ask_directory()

    if not working_dir:
        return "Error: User cancelled folder selection. File was not written."

    abs_path = os.path.abspath(os.path.join(working_dir, file_name))

    if os.path.isdir(abs_path):
        return f'Error: Path is a folder, not a regular file: "{abs_path}"'

    if not os.path.exists(abs_path):
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        except Exception as e:
            return f"Error creating parent directories for path: {abs_path}. Exception: {e}"

    try:
        with open(abs_path, 'w', encoding='utf-8') as wf:
          wf.write(content)
        print(f'Successfully wrote to "{abs_path}" ({len(content)} characters written)')
        return abs_path
    except Exception as e:
        return f"Error writing file at: {abs_path}. Exception: {e}"
@tool
def convertToPDF(file_path:str):
  """Convert the md file to proper PDF file
  Args:
    file_path:str-> the absolute_path of the .md file
  return:
    absolute_path of the pdf file
  """
  with open(file_path,'r') as md:
    md_text = md.read()
  html_text = markdown.markdown(md_text)
  output_path = f"{file_path.replace('\\','/').split('/')[-1].split('.')[0]}.pdf"
  HTML(string=html_text).write_pdf(output_path)
  return os.path.abspath(output_path)



