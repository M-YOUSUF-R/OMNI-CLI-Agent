from agent import create_model,current_time,word_count,build_agent

TOOLS = [current_time, word_count]

llm_model = create_model()
print('Model connection initialized...')

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to tools for getting the current time and counting words in text. "
    "Use tools when the user's request needs one. "
    "If the question doesn't need a tool, answer directly. "
    "If a tool returns an error, explain the error plainly."
)

def main():
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

    # Track the final AI message chunk to read its metadata at the end
    final_ai_msg = None

    # stream_mode="messages" gives us (message_chunk, metadata)
    for msg, metadata in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
        stream_mode="messages"
    ):
        
      # Print standard text tokens as they generate
      if msg.content:
        print(msg.content, end="", flush=True)

      # Catch and print tool calls before they execute
      tool_calls = getattr(msg, "tool_calls", None)
      if tool_calls:
          for call in tool_calls:
              print(f"\n[tool call] {call['name']}({call['args']})")

    print("\n") # Newline after response text completes

if __name__ == '__main__':
    main()
