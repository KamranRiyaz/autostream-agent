from graph import app
import uuid

thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print("🤖 AutoStream Agent is running. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ['quit', 'exit']:
        break
        
    # Invoke the graph with the user's message
    inputs = {"messages": [("user", user_input)]}
    result = app.invoke(inputs, config=config)
    
    # Print the agent's latest response
    print(f"\nAgent: {result['messages'][-1].content}\n")