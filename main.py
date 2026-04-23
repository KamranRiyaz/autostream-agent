from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from graph import app as agent_app

app = FastAPI()

@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    # Run the graph
    # Note: In a real app, you'd use 'From' as a thread_id for memory
    inputs = {"messages": [("user", Body)]}
    result = agent_app.invoke(inputs)
    
    # Extract the last message from the result state
    agent_reply = result["messages"][-1].content
    
    twiml_response = MessagingResponse()
    twiml_response.message(agent_reply)
    
    return PlainTextResponse(str(twiml_response), media_type="application/xml")