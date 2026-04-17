import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
# Direct sub-module imports (Standard for LangChain 0.1+)
from langchain.agents.agent import AgentExecutor
from langchain.agents.react.agent import create_react_agent
from langchain import hub
from langchain.agents.tools import Tool
from langchain.memory import ConversationBufferMemory
from utils import send_email

# Load environment variables
load_dotenv()

# Global memory
agent_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def setup_agent():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Error: GROQ_API_KEY missing!")

    # Model Setup
    llm = ChatGroq(api_key=api_key, model_name="llama-3.3-70b-versatile", temperature=0)

    # Email Tool Wrapper
    def email_tool_wrapper(input_data):
        try:
            if "," not in input_data:
                return "Error: Use 'email, message' format."
            
            parts = input_data.split(",", 1)
            raw_email = parts[0].strip()
            raw_content = parts[1].strip()

            clean_email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_email)
            recipient_email = clean_email_match.group(0) if clean_email_match else raw_email.strip()

            # Professional Email Logic
            prompt_text = f"Write a professional email for: {raw_content}. Return only subject and body."
            response = llm.invoke(prompt_text).content
            
            status = send_email(recipient_email, "AI Agent Notification", response)
            return f"Status: {status} to {recipient_email}"
        except Exception as e:
            return f"Error: {str(e)}"

    # Tool Definition
    tools = [
        Tool(
            name="Email_Sender_Tool",
            func=email_tool_wrapper,
            description="Use to send professional emails. Input format: 'recipient@email.com, message'"
        )
    ]

    # Pulling the prompt
    prompt = hub.pull("hwchase17/react-chat")

    # Creating the Agent
    agent = create_react_agent(llm, tools, prompt)

    # Final Executor
    return AgentExecutor(
        agent=agent, 
        tools=tools, 
        memory=agent_memory, 
        verbose=True, 
        handle_parsing_errors=True
    )
