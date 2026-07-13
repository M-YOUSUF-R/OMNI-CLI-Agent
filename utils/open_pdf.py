from tkinter import filedialog
from langchain_community.document_loaders import PyPDFLoader

def readPdf():
  try:
    pdf_file = filedialog.askopenfilename(
      title='select file',
      filetypes=[('pdf files','*.pdf')]
    )
    loader = PyPDFLoader(pdf_file)
    doc = loader.load()
    return pdf_file.replace("\\","/").split("/" )[-1],doc
  except:
    print('no file selected...')
    return None,None

