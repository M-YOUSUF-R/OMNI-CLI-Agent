import asyncio
from langchain_core.messages import AIMessageChunk

# Rich UI Imports
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown
from rich.spinner import Spinner

from agent import create_model, current_time, word_count, build_agent
from utils.general_search import generalSearch
from utils.open_links import extractTextFromPage
from utils.create_rag import (
    searchKnowledgeBase, 
    createKnowledgeBaseFromExternalResource,createKnowledgeBaseByAI, 
    listChromaCollectionName,
    deleteKnowledgeByCollection,deleteKnowledgeAllCollection
)

# Initialize Rich Console
console = Console() 

TOOLS = [
    current_time, word_count, generalSearch, 
    extractTextFromPage, listChromaCollectionName,createKnowledgeBaseByAI, 
    searchKnowledgeBase, deleteKnowledgeByCollection,
    deleteKnowledgeAllCollection
]

llm_model = create_model()

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to tools for getting the current time and counting words in text. "
    "Use tools when the user's request needs one. "
    "If the question doesn't need a tool, answer directly. "
    "If a tool returns an error, explain the error plainly."
    "always check for the tools before you generate the response"
    "check if the answer are in your knowledgebase using `searchKnowledgeBase` else search it using `generalSearch` tool"
    "When providing URLs, sources, or website links, ALWAYS give the full url and in console it should be clickable",
    
)

def display_welcome_banner():
    """Displays a stylized banner and available commands."""
    banner_text = Text("⚡ AI RESEARCH AGENT CLI ⚡\n", style="bold cyan center")
    banner_text.append("Ready to review papers, search the web, and analyze documents.\n\n", style="italic white")
    banner_text.append("Commands:\n", style="bold yellow")
    banner_text.append("  /upload  • Load documents into the knowledge base\n", style="green")
    banner_text.append("  /clear   • Clear the Console\n", style="yellow")
    banner_text.append("  /exit    • Close the session\n", style="red")
    console.print(Panel(banner_text, border_style="cyan", expand=False))

async def main():
    agent = build_agent(llm_model, TOOLS, SYSTEM_PROMPT)
    config = {"configurable": {"thread_id": "free-agent-session"}}
    
    console.clear()
    display_welcome_banner()
    console.print("[italic dim]Model connection initialized successfully...[/italic dim]\n")
    
    while True:
        try:
            # Stylized interactive prompt
            question = console.input("[bold magenta]⚡ You[/bold magenta] [bold white]›[/bold white] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Exiting... Goodbye![/bold red]")
            break
            
        if not question or question.lower() == "/exit":
            console.print("[bold red]Exiting... Goodbye![/bold red]")
            break
        elif question.lower() == "/upload":
            console.print("\n[bold yellow]🔄 Launching Knowledge Base Creator...[/bold yellow]")
            createKnowledgeBaseFromExternalResource()
            #console.print("[bold green]✓ Knowledge Base Updated.[/bold green]\n")
            continue
        elif question.lower() == "/clear":
            console.clear()            
            display_welcome_banner()  
            continue

        console.print("\n[bold cyan]🤖 Agent[/bold cyan]")
        
        full_response = ""
        
        # Start with the initial Ollama-style dot spinner
        initial_spinner = Spinner("dots", text=" Thinking...", style="cyan")
        
        with Live(initial_spinner, console=console, refresh_per_second=20) as live:
            try:
                response = agent.astream(
                    {"messages": [{"role": "user", "content": question}]},
                    config=config,
                    stream_mode="messages",
                )
                
                async for chunk, node in response:
                    # 1. If the model decides it needs a tool, update spinner text
                    if isinstance(chunk, AIMessageChunk) and chunk.tool_calls:
                        live.update(Spinner("dots", text=" Activating tools...", style="yellow"))
                    
                    # 2. While the tool node is executing behind the scenes
                    elif chunk.__class__.__name__ == "ToolMessage":
                        live.update(Spinner("dots", text=" Processing tool data...", style="magenta"))
                    
                    # 3. As soon as the first actual text token arrives, swap out the spinner for the stream
                    elif isinstance(chunk, AIMessageChunk) and chunk.content:
                        full_response += chunk.content
                        live.update(Markdown(full_response))
                        
            except Exception as e:
                live.update(Panel(f"[bold red]Error encountered:[/bold red]\n{e}", border_style="red"))
                
        print("\n")  # Clear baseline after stream finishes

if __name__ == '__main__':
    asyncio.run(main())
