from agent import create_model,current_time,word_count,build_agent
import asyncio

TOOLS = [current_time, word_count]

llm_model = create_model()
print('Model connection initialized...')

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to tools for getting the current time and counting words in text. "
    "Use tools when the user's request needs one. "
    "If the question doesn't need a tool, answer directly. "
    "If a tool returns an error, explain the error plainly."
)

async def main():
  agent = build_agent(llm_model,TOOLS,SYSTEM_PROMPT)
  config = {"configurable": {"thread_id": "free-agent-session"}}
  print("Ready! Ask the agent something. Streaming outputs in real time...\n")
  
  while True:
    try:
        question = input("You: ").strip()
    except (KeyboardInterrupt, EOFError):
        break
        
    if not question or question.lower() == "exit":
        break

    print("\nAnswer: ", end="", flush=True)


    # stream_mode="messages" gives us (message_chunk, metadata)
    response = agent.astream(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
        stream_mode="messages"
    )
    async for chunk in response:
        print(chunk[0].content, end="", flush=True)

    print("\n") # Newline after response text completes

if __name__ == '__main__':
    # main()
    asyncio.run(main())
