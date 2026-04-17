import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from utils import send_email

load_dotenv()

def setup_agent():
    api_key = os.getenv("GROQ_API_KEY")
    
    llm = ChatGroq(api_key=api_key, model_name="llama-3.3-70b-versatile", temperature=0)

    def email_tool_wrapper(input_data):
        try:
            # Email aur message ko alag karne ka behtar tareeqa
            if "," in input_data:
                email_part, content_part = input_data.split(",", 1)
            else:
                email_part = input_data
                content_part = "No content provided"

            # Regex for clean email
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email_part)
            if not email_match:
                return "Error: Invalid email format. Please provide a valid email address."
            
            target_email = email_match.group(0)

            # Drafting email body
            draft_prompt = f"Write a professional email for: {content_part}. Return only Subject and Body."
            email_draft = llm.invoke(draft_prompt).content

            status = send_email(target_email, "Project Update", email_draft)
            return f"Status: {status} to {target_email}"
        except Exception as e:
            return f"Tool Error: {str(e)}"

    tools = [
        Tool(
            name="Email_Sender",
            func=email_tool_wrapper,
            description="Use to send emails. Format: 'recipient@gmail.com, message context'"
        )
    ]

    prompt = hub.pull("hwchase17/react-chat")
    # chat_history key yahan memory_key ke naam se aayegi
    agent_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    agent = create_react_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=agent_memory,
        verbose=True,
        handle_parsing_errors=True
    )
