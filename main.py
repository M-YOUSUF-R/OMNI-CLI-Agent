import asyncio
from langchain_core.messages import AIMessageChunk

# Rich UI Imports
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.prompt import Prompt

from agent import createOpenRouteModel, createOllamaMode, current_time, word_count, build_agent
from utils.general_search import generalSearch
from utils.open_links import extractTextFromPage
from utils.write_file import writeMDFile,convertToPDF
from utils.read_file import getFileContent
from utils.create_rag import (
    searchKnowledgeBase, listChromaCollectionName,
    createKnowledgeBaseFromExternalResource, createKnowledgeBaseByAI, 
    deleteKnowledgeByCollection, deleteKnowledgeAllCollection,
)

# Initialize Rich Console
console = Console() 

TOOLS = [
    current_time, word_count,generalSearch,
    extractTextFromPage,
    listChromaCollectionName,searchKnowledgeBase, 
    createKnowledgeBaseByAI, 
    deleteKnowledgeByCollection,deleteKnowledgeAllCollection,
    getFileContent,writeMDFile,convertToPDF,
]

def changeModel():
    """Prompts the user to select a model and returns (llm_instance, display_name)."""
    console.print("\n[bold yellow]🤖 Model Selection[/bold yellow]")
    console.print("[1] OpenRoute (Cloud/Free Router)")
    console.print("[2] Ollama (Local - llama3.1:latest)")
    
    choice = Prompt.ask(
        "Select model provider", 
        choices=["1", "2"], 
        default="1"
    )
    
    if choice == "1":
        model_name = "openrouter/free"
        console.print(f"[green]✓ Switched to {model_name}[/green]\n")
        return createOpenRouteModel(), model_name
    else:
        model_name = "llama3.1:latest"
        console.print(f"[green]✓ Switched to Ollama Model ({model_name}).[/green]\n")
        return createOllamaMode(), model_name

SYSTEM_PROMPT = """You are an elite, highly autonomous AI Research Assistant. Your goal is to provide complete, rigorous, and deeply analytical answers with minimal user guidance.

Follow this strict Tool Execution Protocol for every query:
1. TOOL-FIRST THINKING: Never guess or rely solely on static training data for factual queries. Always look at your available tools first.
2. SEARCH PRIORITY (Strict Order):
   - Step A: Always call `searchKnowledgeBase` first to see if the information exists in your local documents.
   - Step B: If (and only if) the knowledge base lacks sufficient details, immediately call `generalSearch` to search the web.
   - Step C: If a search result contains a highly relevant URL, use `extractTextFromPage` to read the target webpage directly for deeper analysis.
3. CONCISE & AGGRESSIVE REASONING: Do not ask the user for permission or clarification to run tools. Proactively run the necessary tools to assemble a comprehensive, fact-checked answer.
4. ERROR HANDLING: If a tool returns an error, explain the error plainly and try an alternative tool or search query.
5. FORMATTING: Present information beautifully using Markdown (bold headers, clean bullet points, tables). 
   - Never truncate links.
"""

def display_welcome_banner():
    """Displays a stylized banner and available commands."""
    banner_text = Text("⚡ AI RESEARCH AGENT CLI ⚡\n", style="bold cyan center")
    banner_text.append("Ready to review papers, search the web, and analyze documents.\n\n", style="italic white")
    banner_text.append("Commands:\n", style="bold yellow")
    banner_text.append("  /upload  • Load documents into the knowledge base\n", style="green")
    banner_text.append("  /model   • Change LLM Model provider\n", style="blue")
    banner_text.append("  /clear   • Clear the Console\n", style="yellow")
    banner_text.append("  /exit    • Close the session\n", style="red")
    console.print(Panel(banner_text, border_style="cyan", expand=False))

# Default model configuration
llm_model = createOpenRouteModel()
current_model_name = "openrouter/free"

async def main():
    global llm_model, current_model_name
    
    agent = build_agent(llm_model, TOOLS, SYSTEM_PROMPT)
    config = {"configurable": {"thread_id": "free-agent-session"}}
    
    console.clear()
    display_welcome_banner()
    console.print(f"[italic dim]Model connection initialized successfully (Active: {current_model_name})...[/italic dim]\n")
    
    while True:
        try:
            prompt_str = f"[bold magenta]⚡ You[/bold magenta] [dim]({current_model_name})[/dim] [bold white]›[/bold white] "
            question = console.input(prompt_str).strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Exiting... Goodbye![/bold red]")
            break
            
        if not question or question.lower() == "/exit":
            console.print("[bold red]Exiting... Goodbye![/bold red]")
            break
        elif question.lower() == "/upload":
            console.print("\n[bold yellow]🔄 Launching Knowledge Base Creator...[/bold yellow]")
            createKnowledgeBaseFromExternalResource()
            continue
        elif question.lower() == "/clear":
            console.clear()            
            display_welcome_banner()  
            continue
        elif question.lower() == '/model':
            llm_model, current_model_name = changeModel()
            agent = build_agent(llm_model, TOOLS, SYSTEM_PROMPT)
            continue

        console.print(f"\n[bold cyan]🤖 Agent[/bold cyan]")
        
        full_response = ""
        resolved_model = None
        initial_spinner = Spinner("dots", text=" Thinking...", style="cyan")
        
        with Live(initial_spinner, console=console, refresh_per_second=20) as live:
            try:
                response = agent.astream(
                    {"messages": [{"role": "user", "content": question}]},
                    config=config,
                    stream_mode="messages",
                )

                async for chunk, node in response:
                    # Capture the specific model resolved by OpenRouter's router backend
                    if isinstance(chunk, AIMessageChunk):
                        # Safely try to pull metadata names from LangChain chunk details
                        meta = chunk.response_metadata
                        if meta and "model_name" in meta and not resolved_model:
                            resolved_model = meta["model_name"]
                            # Print a sub-header panel as soon as the exact model registers
                            console.print(f"[dim italic grey]↳ Selected Route: {resolved_model}[/dim italic grey]")

                    if isinstance(chunk, AIMessageChunk) and chunk.tool_calls:
                        live.update(Spinner("dots", text=" Activating tools...", style="yellow"))
                    elif chunk.__class__.__name__ == "ToolMessage":
                        live.update(Spinner("dots", text=" Processing tool data...", style="magenta"))
                    elif isinstance(chunk, AIMessageChunk) and chunk.content:
                        full_response += chunk.content
                        live.update(Markdown(full_response))
                        
            except Exception as e:
                live.update(Panel(f"[bold red]Error encountered:[/bold red]\n{e}", border_style="red"))
        print("\n")

if __name__ == '__main__':
    asyncio.run(main())
