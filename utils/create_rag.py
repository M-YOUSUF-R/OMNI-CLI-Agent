from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_core.tools import tool

import chromadb
from chromadb.config import Settings

from .open_pdf import readPdf

from rich.console import Console

from dotenv import load_dotenv
load_dotenv()

console = Console()

def embeddingFunc():
  return OllamaEmbeddings(model="nomic-embed-text")

def createKnowledgeBaseFromExternalResource():
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
  )
  
  doc_name , pdf = readPdf()
  if pdf is None:
    console.print('[red]x Nothing entered in knowledgebase...[/red]')
    return
  chunks = text_splitter.split_documents(pdf)
  print("creating vector database...")
  embeddings = embeddingFunc()
  vector_db = Chroma.from_documents(
    documents=chunks, 
    embedding=embeddings, 
    persist_directory="./chroma_db",
    collection_name=doc_name
  )
  console.print("[bold green]✓ Knowledge Base Updated.[/bold green]\n")

@tool
def createKnowledgeBaseByAI(collection_name:str,information:str):
  """Add infromation in the knowledgebase
  Args:
    collection_name:str -> the knowledge collection name to search the require information form knowlebase.
    information:str -> the information which will be saved in knowledgebase.
  """
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
  )
  raw_docuemnt = Document(page_content=information)

  docs = text_splitter.split_documents([raw_docuemnt])
  embedding = embeddingFunc()
  vector_db = Chroma.from_documents(
    documents=docs,
    embedding=embedding,
    persist_directory="./chroma_db",
    collection_name=collection_name
  )
  console.print("[bold green]✓ Knowledge Base Updated.[/bold green]\n")
  

@tool
def deleteKnowledgeByCollection(collection_name:str):
  """Can Delete a specific collection_name's datas from knowledgebase
  Args:
    collection_name:str-> name of the collection
  """
  chroma_client = chromadb.PersistentClient(path='./chroma_db')
  chroma_client.delete_collection(name=collection_name)

@tool
def deleteKnowledgeAllCollection():
  """Can Delete entrie knowledgebase
  """
  chroma_client = chromadb.PersistentClient(path='./chroma_db',settings=Settings(allow_reset=True))
  chroma_client.reset()
@tool
def listChromaCollectionName()->list[str]:
  """List all chroma collection name to search them in `searchKnowledgeBase` function
  return:
    collections:list[str] -> all the collection name
  """
  
  chroma_client = chromadb.PersistentClient(path='./chroma_db')

  collections = chroma_client.list_collections()
  collections = [collection.name for collection in collections]
  return collections

@tool
def searchKnowledgeBase(query:str,collection_name:str)->str:
  """Search the local knowledge base.
  Args: 
    query:str -> the query to search from the knowledgebase
    collection_name:str -> the collection of related content which was used to create the knowledgebase
  """
  embeddings = embeddingFunc()
  db = Chroma(
    embedding_function=embeddings, 
    persist_directory="./chroma_db",
    collection_name=collection_name
  )

  retriever = db.as_retriever(search_kwargs={'k':2})
  docs = retriever.invoke(query)
  return "\n\n".join(doc.page_content for doc in docs)

